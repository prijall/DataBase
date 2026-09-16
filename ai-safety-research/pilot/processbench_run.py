"""Local, single-attempt ProcessBench calibration/evaluation with durable journals.

The separate preflight helper must validate exact local rendering/tokenization and
resources. This runner never retries a subject ID or resolves interrupted calls.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import importlib
import json
import os
from pathlib import Path
import socket
import subprocess
import threading
import time

import pilot
import processbench_prepare as preparation
from verification_only import atomic_write, run_lock

ROOT = Path(__file__).resolve().parent
MODEL = 'llama3.2:3b'
MODEL_DIGEST = 'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
OPTIONS = {'temperature': 0, 'seed': 42, 'num_ctx': 8192, 'num_predict': 1024, 'num_thread': 2}
REQUEST_SECONDS = 90
RESERVE_SECONDS = 130
BUDGET_SECONDS = 5400
MAX_ATTEMPTS = 60


def digest_bytes(content):
    return hashlib.sha256(content).hexdigest()


def canonical_hash(value):
    return digest_bytes(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8'))


def append_event(path, value):
    """Persist a whole small journal line before proceeding to the external action."""
    previous = path.read_text() if path.exists() else ''
    if previous and not previous.endswith('\n'):
        raise ValueError('Unterminated journal; manual audit required')
    atomic_write(path, previous + json.dumps(value, ensure_ascii=False) + '\n')


def read_lines(path):
    if not path.exists():
        return []
    content = path.read_text()
    if content and not content.endswith('\n'):
        raise ValueError('Unterminated journal; manual audit required')
    return [json.loads(line) for line in content.splitlines()]


def load_jobs(data_path, prompt_path, provenance_path, selection_path):
    examples, template, provenance, hashes = preparation.load_inputs(data_path, prompt_path, provenance_path)
    selection = json.loads(selection_path.read_text())
    expected = preparation.make_manifest(examples, template, provenance, hashes)
    if selection != expected:
        raise ValueError('Selection differs from deterministic pinned-source reconstruction')
    indexed = {example['id']: example for example in examples}
    jobs = []
    for split in ('calibration', 'evaluation'):
        for entry in selection['splits'][split]['records']:
            example = indexed[entry['id']]
            messages = preparation.render_messages(example, template)
            message_hash = canonical_hash(messages)
            if message_hash != entry['messages_sha256']:
                raise ValueError('Rendered message hash differs from selection')
            jobs.append({'id': example['id'], 'split': split, 'gold_label': example['label'],
                         'step_count': len(example['steps']), 'messages': messages,
                         'messages_sha256': message_hash,
                         'problem_group_sha256': entry['problem_group_sha256']})
    return jobs, dict(hashes, selection=digest_bytes(selection_path.read_bytes()))


def public_job(job):
    return {key: value for key, value in job.items() if key != 'messages'}


def completed_score(content, job, final_response, request_error=None):
    result = preparation.score_output(content, job['gold_label'], job['step_count'])
    normal = (isinstance(final_response, dict) and final_response.get('done') is True
              and final_response.get('done_reason') == 'stop' and not final_response.get('error')
              and request_error is None)
    result.update(normal_completion=bool(normal), usable=bool(normal and result['strict_index_valid']),
                  local_match=bool(normal and result['strict_index_valid'] and result['official_match']))
    return result


def decode_stream(content):
    """Recover only generated message content, preserving a malformed final fragment as an error."""
    pieces, final_response, events, stream_error = [], None, 0, None
    for line in content.splitlines():
        if not line.strip():
            continue
        try:
            chunk = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            stream_error = 'malformed streamed JSON'
            break
        if not isinstance(chunk, dict):
            stream_error = 'stream event is not an object'
            break
        if chunk.get('model') is not None and chunk['model'] != MODEL:
            stream_error = 'unexpected model identity in streamed response'
            break
        if final_response is not None:
            stream_error = 'data after terminal stream event'
            break
        events += 1
        message = chunk.get('message')
        if message is not None:
            if not isinstance(message, dict) or not isinstance(message.get('content', ''), str):
                stream_error = 'invalid streamed message content'
                break
            pieces.append(message.get('content', ''))
        if chunk.get('done') is True or chunk.get('error'):
            final_response = chunk
    return {'content': ''.join(pieces), 'raw_final_response': final_response,
            'stream_events': events, 'stream_error': stream_error}


class RequestDeadlineExceeded(TimeoutError):
    pass


def stream_chat(payload, on_line, deadline_seconds=REQUEST_SECONDS):
    """Fixed loopback streaming request with an independent absolute socket watchdog."""
    started = time.monotonic()
    fired = threading.Event()
    connection = http.client.HTTPConnection('127.0.0.1', 11434, timeout=deadline_seconds)
    # A watchdog-closed socket must not trigger HTTPConnection's implicit reopen.
    connection.auto_open = 0
    live = {'socket': None}

    def cancel():
        fired.set()
        sock = live['socket']
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass
        connection.close()

    watchdog = threading.Timer(deadline_seconds, cancel)
    watchdog.daemon = True
    watchdog.start()
    try:
        remaining = deadline_seconds - (time.monotonic() - started)
        if fired.is_set() or remaining <= 0:
            raise RequestDeadlineExceeded('Absolute request deadline reached')
        connection.timeout = remaining
        connection.connect()
        live['socket'] = connection.sock
        if fired.is_set():
            raise RequestDeadlineExceeded('Absolute request deadline reached')
        remaining = deadline_seconds - (time.monotonic() - started)
        if remaining <= 0:
            raise RequestDeadlineExceeded('Absolute request deadline reached')
        connection.sock.settimeout(remaining)
        connection.request('POST', '/api/chat', body=json.dumps(payload).encode('utf-8'),
                           headers={'Content-Type': 'application/json', 'Connection': 'close'})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError(f'Local server returned HTTP {response.status}')
        terminal = False
        while not terminal:
            line = response.readline(1024 * 1024 + 1)
            if fired.is_set() or time.monotonic() - started >= deadline_seconds:
                raise RequestDeadlineExceeded('Absolute request deadline reached')
            if not line:
                raise ValueError('Stream ended without a terminal server event')
            if len(line) > 1024 * 1024:
                raise ValueError('Oversized stream event')
            terminal = on_line(line)
        if fired.is_set() or time.monotonic() - started >= deadline_seconds:
            raise RequestDeadlineExceeded('Absolute request deadline reached')
    except Exception as error:
        if fired.is_set():
            raise RequestDeadlineExceeded('Absolute request deadline reached; server cancellation unverified') from error
        raise
    finally:
        watchdog.cancel()
        connection.close()


def read_history(directory, jobs):
    expected = {job['id']: job for job in jobs}
    events = read_lines(directory / 'journal.jsonl')
    responses = read_lines(directory / 'responses.jsonl')
    starts, finishes = {}, {}
    for event in events:
        if event['kind'] == 'attempt_started':
            key = event['id']
            if key not in expected or key in starts:
                raise ValueError('Unknown or repeated subject attempt; manual audit required')
            job = expected[key]
            if event['split'] != job['split'] or event['messages_sha256'] != job['messages_sha256']:
                raise ValueError('Journal attempt does not match selected job')
            number = event['attempt_number']
            if number != len(starts) + 1 or number > MAX_ATTEMPTS:
                raise ValueError('Invalid attempt ordering or limit')
            if event['stream_path'] != f'streams/attempt-{number:03}.jsonl':
                raise ValueError('Unexpected stream path')
            starts[key] = event
        elif event['kind'] == 'attempt_finished':
            key = event['id']
            if key not in starts or key in finishes:
                raise ValueError('Unmatched or repeated terminal journal record')
            finishes[key] = event
    indexed = {}
    for row in responses:
        key = row['id']
        if key in indexed or key not in starts or key not in expected:
            raise ValueError('Response without one unique journaled attempt')
        job, start = expected[key], starts[key]
        if row['job'] != public_job(job) or row['stream_path'] != start['stream_path']:
            raise ValueError('Saved response provenance differs from selected job')
        raw = (directory / row['stream_path']).read_bytes()
        if digest_bytes(raw) != row['stream_sha256']:
            raise ValueError('Raw stream hash mismatch')
        decoded = decode_stream(raw)
        if any(row[field] != decoded[field] for field in decoded):
            raise ValueError('Saved content differs from raw stream')
        final = decoded['raw_final_response']
        if row['request_error'] is None and (decoded['stream_error'] or final is None
                                             or final.get('done') is not True or final.get('error')):
            raise ValueError('Raw execution failure lacks a persisted request error')
        if row['observed_prompt_tokens'] != (final or {}).get('prompt_eval_count'):
            raise ValueError('Stored prompt count differs from raw server response')
        if row['request_error'] is None and (type(row['observed_prompt_tokens']) is not int
                                             or row['observed_prompt_tokens'] != row['expected_prompt_tokens']):
            raise ValueError('Unexplained prompt-token mismatch in completed record')
        calculated = completed_score(decoded['content'], job, decoded['raw_final_response'], row['request_error'])
        if row['score'] != calculated:
            raise ValueError('Saved score differs from raw-derived score')
        if key in finishes and finishes[key]['response_sha256'] != canonical_hash(row):
            raise ValueError('Terminal journal response hash mismatch')
        indexed[key] = row
    pending = [key for key in starts if key not in finishes or key not in indexed]
    if pending:
        raise ValueError('Ambiguous interrupted attempt; no retry or resume: ' + ', '.join(pending))
    if any(row['request_error'] for row in indexed.values()):
        raise ValueError('Prior request error requires external cancellation/state review; automatic resume refused')
    return events, starts, indexed


def analyze_cohort(jobs, responses, split):
    planned = [job for job in jobs if job['split'] == split]
    classes = {}
    for label_class, is_valid in (('valid', True), ('error', False)):
        subset = [job for job in planned if (job['gold_label'] == -1) == is_valid]
        rows = [responses[job['id']] for job in subset if job['id'] in responses]
        usable = [row for row in rows if row['score']['usable']]
        classes[label_class] = {'planned': len(subset), 'recorded': len(rows),
                                'missing': len(subset) - len(rows), 'usable': len(usable),
                                'official_matches': sum(row['score']['official_match'] for row in rows),
                                'local_matches': sum(row['score']['local_match'] for row in rows),
                                'conditional_local_accuracy': (sum(row['score']['local_match'] for row in usable) / len(usable)) if usable else None}
    rows = [responses[job['id']] for job in planned if job['id'] in responses]
    complete = len(rows) == len(planned)
    usable = sum(row['score']['usable'] for row in rows)
    gate = (split == 'calibration' and len(planned) == 20 and complete and usable >= 18
            and classes['valid']['local_matches'] >= 8 and classes['error']['local_matches'] >= 8)
    observed_scores = [row['score'] for row in rows]
    return {'split': split, 'planned': len(planned), 'recorded': len(rows),
            'missing': len(planned) - len(rows), 'complete': complete,
            'usable': usable, 'classes': classes, 'calibration_gate_passed': gate,
            'official_observed': preparation.aggregate_scores(observed_scores),
            'official_exact_matches': sum(row['score']['official_match'] for row in rows),
            'local_exact_matches': sum(row['score']['local_match'] for row in rows),
            'malformed': sum(row['score']['prediction'] is None for row in rows),
            'out_of_range': sum(row['score']['prediction'] is not None and not row['score']['strict_index_valid'] for row in rows),
            'length_stops': sum((row['raw_final_response'] or {}).get('done_reason') == 'length' for row in rows),
            'request_errors': sum(row['request_error'] is not None for row in rows)}


def write_summary(directory, jobs, responses, reason=None):
    reports = {split: analyze_cohort(jobs, responses, split) for split in ('calibration', 'evaluation')}
    lines = ['# ProcessBench local adaptation', '',
             'Primary extraction follows the published last-boxed-integer rule. Completion-gated local '
             'success additionally requires a normal server stop and an in-range prediction. '
             'These scores describe this small resource-adapted subset, not a published-score replication.', '',
             f"Stop/status: {reason or 'Invocation ended normally'}.", '',
             '| Cohort | Recorded / planned | Usable | Official exact matches / recorded | Local exact matches / planned | Length stops | Request errors |',
             '| --- | --- | ---: | --- | --- | ---: | ---: |']
    for name, report in reports.items():
        lines.append(f"| {name} | {report['recorded']}/{report['planned']} | {report['usable']} | "
                     f"{report['official_exact_matches']}/{report['recorded']} | "
                     f"{report['local_exact_matches']}/{report['planned']} | {report['length_stops']} | {report['request_errors']} |")
    for name, report in reports.items():
        lines += ['', f"### {name.title()} class scores", '',
                  '| Class | Recorded / planned | Usable | Official matches / recorded | Local matches / planned | Conditional local accuracy |',
                  '| --- | --- | ---: | --- | --- | --- |']
        for label, cell in report['classes'].items():
            conditional = 'not estimable' if cell['conditional_local_accuracy'] is None else f"{100 * cell['conditional_local_accuracy']:.1f}%"
            lines.append(f"| {label} | {cell['recorded']}/{cell['planned']} | {cell['usable']} | "
                         f"{cell['official_matches']}/{cell['recorded']} | {cell['local_matches']}/{cell['planned']} | {conditional} |")
        harmonic = report['official_observed']['harmonic_mean_percent']
        harmonic_text = 'not estimable' if harmonic is None else f'{harmonic:.2f}%'
        lines += ['', f'Observed-output official-compatible harmonic mean: {harmonic_text}. '
                  + ('Cohort complete.' if report['complete'] else 'Partial/unused cohort; this is not a completed planned-cohort score.'),
                  f"Malformed extractions: {report['malformed']}; out-of-range indices: {report['out_of_range']}; missing calls: {report['missing']}.", '']
    lines += [f"Calibration gate: **{'PASS' if reports['calibration']['calibration_gate_passed'] else 'NOT PASSED'}**.", '',
              'The harmonic mean combines error-free and erroneous-solution exact accuracies, not precision '
              'and recall. Our documented zero/zero convention is zero; an absent class is unavailable. '
              'Missing and failed calls remain unsuccessful against planned denominators for local feasibility. '
              'Raw streams are preserved; source prompts are reconstructed from pinned downloads and message hashes.', '']
    atomic_write(directory / 'SUMMARY.md', '\n'.join(lines))
    atomic_write(directory / 'ANALYSIS.json', json.dumps(reports, indent=2, allow_nan=False) + '\n')
    return reports


def current_model():
    candidate = next((item for item in pilot.api('tags')['models'] if item['name'] == MODEL), None)
    if candidate is None or candidate.get('remote_host') or candidate.get('digest') != MODEL_DIGEST:
        raise ValueError('Required installed local model identity unavailable')
    shown = pilot.api('show', {'model': MODEL})
    if shown.get('remote_host') or shown.get('remote_model'):
        raise ValueError('Remote model refused')
    return {'model_digest': candidate['digest'], 'details': candidate['details'],
            'template_sha256': digest_bytes(shown['template'].encode('utf-8')),
            'server_version': pilot.api('version')['version']}


def git_revision():
    paths = ['processbench_run.py', 'processbench_prepare.py', 'processbench_preflight.py',
             'processbench_resources.py', 'pilot.py', 'verification_only.py',
             'PROCESSBENCH_PLAN.md', 'PROCESSBENCH_EXECUTION.md', 'processbench/selection.json',
             'processbench/provenance.json']
    subprocess.check_call(['git', 'ls-files', '--error-unmatch', *paths], cwd=ROOT,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(['git', 'diff', '--quiet', 'HEAD', '--', *paths], cwd=ROOT)
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def dependencies(preflight_module, resource_module):
    paths = {'runner': Path(__file__), 'adapter': Path(preparation.__file__), 'pilot': Path(pilot.__file__),
             'atomic_io': ROOT / 'verification_only.py', 'preflight': Path(preflight_module.__file__),
             'resources': Path(resource_module.__file__), 'plan': ROOT / 'PROCESSBENCH_PLAN.md',
             'execution_addendum': ROOT / 'PROCESSBENCH_EXECUTION.md'}
    return {name: digest_bytes(path.read_bytes()) for name, path in paths.items()}


def remaining_budget(deadline_unix, initial_remaining, monotonic_started):
    return min(deadline_unix - time.time(), initial_remaining - (time.monotonic() - monotonic_started))


def run(args):
    jobs, input_hashes = load_jobs(args.data, args.prompt, args.provenance, args.selection)
    args.out.mkdir(parents=True, exist_ok=True)
    preflight_module = importlib.import_module('processbench_preflight')
    resource_module = importlib.import_module('processbench_resources')
    with run_lock(args.out):
        _, attempts, responses = read_history(args.out, jobs)
        if args.phase == 'evaluation' and not analyze_cohort(jobs, responses, 'calibration')['calibration_gate_passed']:
            raise ValueError('Evaluation refused: recomputed calibration gate has not passed')
        revision = git_revision()
        try:
            report = preflight_module.verify_preflight(args.preflight, jobs, MODEL, OPTIONS)
        except Exception as error:
            reason = f'Preflight blocked: {type(error).__name__}: {error}'
            append_event(args.out / 'journal.jsonl', {'kind': 'preflight_blocked', 'phase': args.phase,
                                                     'unix': time.time(), 'reason': reason})
            write_summary(args.out, jobs, responses, reason)
            raise
        identity = current_model()
        for name in ('model_digest', 'server_version', 'template_sha256'):
            if report[name] != identity[name]:
                raise ValueError(f'Preflight {name} differs from current local runtime')
        for row in responses.values():
            if row['expected_prompt_tokens'] != report['tokens'][row['id']]['prompt_tokens']:
                raise ValueError('Saved prompt-token expectation differs from frozen preflight')
        budget_started = report['budget_started_unix']
        if not isinstance(budget_started, (int, float)) or isinstance(budget_started, bool) or budget_started > time.time():
            raise ValueError('Invalid preflight budget start')
        deadline_unix = budget_started + BUDGET_SECONDS
        initial_remaining, monotonic_started = deadline_unix - time.time(), time.monotonic()
        protocol = {'protocol_name': 'processbench-local-v1', 'model': MODEL, 'identity': identity,
                    'options': OPTIONS, 'request_deadline_seconds': REQUEST_SECONDS,
                    'request_behavior': {'stream': True, 'truncate': False, 'shift': False, 'keep_alive': '30s'},
                    'reserve_seconds': RESERVE_SECONDS, 'budget_seconds': BUDGET_SECONDS,
                    'max_attempts': MAX_ATTEMPTS, 'budget_started_unix': budget_started,
                    'deadline_unix': deadline_unix, 'input_hashes': input_hashes,
                    'code_hashes': dependencies(preflight_module, resource_module),
                    'preflight_sha256': digest_bytes(args.preflight.read_bytes()),
                    'jobs': [public_job(job) for job in jobs]}
        manifest_path = args.out / 'manifest.json'
        if manifest_path.exists():
            if json.loads(manifest_path.read_text())['protocol'] != protocol:
                raise ValueError('Resume refused: frozen provenance, runtime, or budget changed')
        else:
            if attempts:
                raise ValueError('Journal exists without a run manifest')
            atomic_write(manifest_path, json.dumps({'git_commit': revision, 'protocol': protocol}, indent=2) + '\n')
        journal = args.out / 'journal.jsonl'
        append_event(journal, {'kind': 'session_started', 'phase': args.phase, 'unix': time.time(),
                               'remaining_seconds': initial_remaining})
        reason = None
        try:
            for job in [job for job in jobs if job['split'] == args.phase]:
                if job['id'] in attempts:
                    continue
                if len(attempts) >= MAX_ATTEMPTS:
                    reason = 'Fixed subject-attempt limit reached'
                    break
                if remaining_budget(deadline_unix, initial_remaining, monotonic_started) < RESERVE_SECONDS:
                    reason = 'Budget reserve reached; no new subject request started'
                    break
                snapshot = resource_module.snapshot()
                violations = resource_module.violations(snapshot, report['resource_baseline'])
                append_event(journal, {'kind': 'resource_check', 'stage': 'before', 'id': job['id'],
                                       'unix': time.time(), 'snapshot': snapshot, 'violations': violations})
                if violations:
                    reason = 'Resource stop: ' + '; '.join(violations)
                    break
                runtime = preflight_module.verify_runtime_idle(report, MODEL)
                if current_model() != identity:
                    reason = 'Local model or server identity changed'
                    break
                append_event(journal, {'kind': 'runtime_idle_check', 'id': job['id'],
                                       'unix': time.time(), 'runtime': runtime})
                if remaining_budget(deadline_unix, initial_remaining, monotonic_started) < RESERVE_SECONDS:
                    reason = 'Budget reserve reached after resource check'
                    break
                number = len(attempts) + 1
                stream_path = f'streams/attempt-{number:03}.jsonl'
                started = {'kind': 'attempt_started', 'id': job['id'], 'split': job['split'],
                           'attempt_number': number, 'stream_path': stream_path,
                           'messages_sha256': job['messages_sha256'], 'unix': time.time()}
                append_event(journal, started)
                attempts[job['id']] = started
                raw_path = args.out / stream_path
                raw_path.parent.mkdir(parents=True, exist_ok=True)
                request_started, request_error = time.monotonic(), None
                try:
                    with raw_path.open('xb') as raw:
                        def on_line(line):
                            raw.write(line)
                            raw.flush()
                            chunk = json.loads(line)
                            if not isinstance(chunk, dict):
                                raise ValueError('Non-object stream event')
                            return chunk.get('done') is True or bool(chunk.get('error'))
                        try:
                            stream_chat({'model': MODEL, 'messages': job['messages'], 'stream': True,
                                         'truncate': False, 'shift': False,
                                         'options': OPTIONS, 'keep_alive': '30s'}, on_line)
                        finally:
                            raw.flush()
                            os.fsync(raw.fileno())
                except Exception as error:
                    request_error = {'type': type(error).__name__, 'message': str(error),
                                     'server_cancellation': 'unverified; automatic resume blocked'}
                raw_bytes = raw_path.read_bytes() if raw_path.exists() else b''
                decoded = decode_stream(raw_bytes)
                final = decoded['raw_final_response']
                if request_error is None and (decoded['stream_error'] or final is None or final.get('error') or final.get('done') is not True):
                    request_error = {'type': 'InvalidServerCompletion',
                                     'message': decoded['stream_error'] or str((final or {}).get('error') or 'No completed response'),
                                     'server_cancellation': 'unverified; automatic resume blocked'}
                expected_prompt_tokens = report['tokens'][job['id']]['prompt_tokens']
                if request_error is None and (type(final.get('prompt_eval_count')) is not int
                                              or final['prompt_eval_count'] != expected_prompt_tokens):
                    request_error = {'type': 'PromptTokenMismatch',
                                     'message': f"Observed prompt_eval_count={final.get('prompt_eval_count')} differs from verified {expected_prompt_tokens}",
                                     'server_cancellation': 'Terminal response received; input-count discrepancy unresolved'}
                row = {'id': job['id'], 'job': public_job(job), 'attempt_number': number,
                       'utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic() - request_started,
                       'stream_path': stream_path, 'stream_sha256': digest_bytes(raw_bytes),
                       **decoded, 'request_error': request_error,
                       'expected_prompt_tokens': expected_prompt_tokens,
                       'observed_prompt_tokens': (final or {}).get('prompt_eval_count'),
                       'score': completed_score(decoded['content'], job, final, request_error)}
                append_event(args.out / 'responses.jsonl', row)
                append_event(journal, {'kind': 'attempt_finished', 'id': job['id'], 'unix': time.time(),
                                       'response_sha256': canonical_hash(row)})
                responses[job['id']] = row
                print(f"{args.phase} {sum(row['job']['split'] == args.phase for row in responses.values())}/"
                      f"{20 if args.phase == 'calibration' else 40} {job['id']} "
                      f"usable={row['score']['usable']} local_match={row['score']['local_match']}", flush=True)
                if request_error is not None:
                    reason = 'Request failed; server cancellation/state unresolved. No automatic retry or resume.'
                    break
                snapshot = resource_module.snapshot()
                violations = resource_module.violations(snapshot, report['resource_baseline'])
                append_event(journal, {'kind': 'resource_check', 'stage': 'after', 'id': job['id'],
                                       'unix': time.time(), 'snapshot': snapshot, 'violations': violations})
                if violations:
                    reason = 'Resource stop: ' + '; '.join(violations)
                    break
        except BaseException as error:
            reason = f'Execution stopped: {type(error).__name__}: {error}'
            raise
        finally:
            append_event(journal, {'kind': 'session_finished', 'phase': args.phase, 'unix': time.time(),
                                   'remaining_seconds': remaining_budget(deadline_unix, initial_remaining, monotonic_started),
                                   'reason': reason})
            write_summary(args.out, jobs, responses, reason)
        return write_summary(args.out, jobs, responses, reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('calibration', 'evaluation'))
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--prompt', type=Path, required=True)
    parser.add_argument('--provenance', type=Path, required=True)
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--preflight', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
