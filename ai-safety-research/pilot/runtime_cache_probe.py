"""Four-call synthetic runtime diagnostic, never a benchmark or admission gate.

All artifacts stay on the controller. Preparation and run are separate so the
owned service's cache-disabled log can be inspected before any generation.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

import processbench_remote as remote
import processbench_resources as resources
import processbench_run as records
import processbench_server_session as service

PROFILE = 'runtime-cache-diagnostic-v1'
BUDGET_SECONDS = 600
RESERVE_SECONDS = 150
PROTOCOL = remote.ROOT / 'RUNTIME_CACHE_DIAGNOSTIC_PROTOCOL.md'


def jobs():
    return remote.diagnostic_jobs()


def bindings():
    sources = remote.bundle()
    return sources, remote.transport_binding(sources, PROFILE)


def freeze():
    paths = ['runtime_cache_probe.py', 'test_runtime_cache_probe.py',
             'RUNTIME_CACHE_DIAGNOSTIC_PROTOCOL.md', 'processbench_remote.py',
             'processbench_server_session.py', 'test_processbench_server_session.py', 'processbench_run.py',
             'processbench_preflight.py', 'processbench_resources.py', 'verification_only.py']
    subprocess.check_call(['git', 'ls-files', '--error-unmatch', *paths], cwd=remote.ROOT,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(['git', 'diff', '--quiet', 'HEAD', '--', *paths], cwd=remote.ROOT)
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=remote.ROOT, text=True).strip()


def exclusive_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as output:
        output.write(json.dumps(value, indent=2, allow_nan=False) + '\n')
        output.flush()
        os.fsync(output.fileno())


def inspect_service_log(path, require_disabled):
    raw = path.read_bytes()
    events = []
    for line in raw.splitlines():
        if line.startswith(b'SESSION '):
            events.append(json.loads(line[8:]))
        elif line.startswith(b'{'):
            event = json.loads(line)
            if event.get('event') in ('local_start', 'local_end'):
                events.append(event)
    headers = [event for event in events if event.get('event') == 'local_start']
    environments = [event for event in events if event.get('event') == 'service_environment']
    spawned = [event for event in events if event.get('event') == 'spawned']
    if (len(headers) != 1 or headers[0].get('cache_ram_mib') != 0
            or headers[0].get('remote_code_sha256') != remote.sha(service.remote_code(0).encode())
            or headers[0].get('launcher_file_sha256') != remote.sha(Path(service.__file__).read_bytes())
            or len(environments) != 1 or environments[0].get('cache_ram_override') != 0
            or environments[0].get('allowlisted_environment') != {'LLAMA_ARG_CACHE_RAM': '0'}
            or len(spawned) != 1 or type(spawned[0].get('pid')) is not int or spawned[0]['pid'] <= 0
            or spawned[0].get('pid') != spawned[0].get('pgid')
            or spawned[0].get('watchdog_seconds') != 600
            or spawned[0].get('budget_started_unix') != headers[0].get('budget_started_unix')
            or any(event.get('event') in ('cleanup', 'local_end') for event in events)):
        raise ValueError('Current owned cache-disabled service evidence unavailable')
    disabled = b'prompt cache is disabled - use `--cache-ram N` to enable it' in raw
    if b'prompt cache is enabled, size limit:' in raw or (require_disabled and not disabled):
        raise ValueError('Backend cache-disabled initialization not verified')
    return {'source_log_sha256': remote.sha(raw), 'observed_bytes': len(raw),
            'owned_pid': spawned[0]['pid'], 'cache_disabled_observed': disabled,
            'budget_started_unix': headers[0]['budget_started_unix']}


def prepare(args):
    revision = freeze()
    sources, binding = bindings()
    service_evidence = inspect_service_log(args.service_log, False)
    started = service_evidence['budget_started_unix']
    if type(started) not in (int, float) or not 0 <= time.time() - started < BUDGET_SECONDS - RESERVE_SECONDS:
        raise ValueError('Owned service diagnostic budget invalid or exhausted')
    path = args.out / 'preflight.json'
    marker = {'status': 'dispatching', 'purpose': PROFILE, 'benchmark_admission': False,
              'git_commit': revision, 'transport': binding, 'budget_started_unix': started,
              'service_evidence': service_evidence, 'jobs_sha256': records.canonical_hash(jobs())}
    exclusive_json(path, marker)
    report = remote.rpc('create_preflight', sources, binding, jobs=jobs(), budget_started_unix=started)
    if (report.get('transport') != binding or report.get('jobs_sha256') != marker['jobs_sha256']
            or report.get('budget_started_unix') != started or report.get('purpose') != PROFILE
            or report.get('benchmark_admission') is not False
            or report.get('status') not in ('passed', 'blocked')):
        raise ValueError('Diagnostic preflight binding mismatch; dispatch remains unresolved')
    records.atomic_write(path, json.dumps(report, indent=2) + '\n')
    exclusive_json(args.out / 'preparation.json', marker)
    if report['status'] != 'passed':
        raise ValueError('Diagnostic preflight blocked: ' + report.get('reason', 'unknown'))
    evidence = inspect_service_log(args.service_log, True)
    exclusive_json(args.out / 'cache-uptake.json', evidence)
    return report


def summary(args, reason):
    responses = records.read_lines(args.out / 'responses.jsonl')
    attempts = [event for event in records.read_lines(args.out / 'journal.jsonl')
                if event.get('kind') == 'attempt_started']
    value = {'purpose': PROFILE, 'benchmark_admission': False, 'planned': 4,
             'attempted': len(attempts), 'recorded': len(responses),
             'ambiguous_attempts': len(attempts) - len(responses), 'unattempted': 4 - len(attempts),
             'request_errors': sum(row['request_error'] is not None for row in responses),
             'status': reason, 'no_accuracy_score': True}
    records.atomic_write(args.out / 'SUMMARY.json', json.dumps(value, indent=2) + '\n')
    return value


def run(args):
    revision = freeze()
    sources, binding = bindings()
    report = json.loads((args.out / 'preflight.json').read_text())
    expected = {'transport': binding, 'purpose': PROFILE, 'benchmark_admission': False,
                'jobs_sha256': records.canonical_hash(jobs()), 'status': 'passed'}
    if any(report.get(key) != value for key, value in expected.items()):
        raise ValueError('Diagnostic profile/preflight mismatch')
    started = report['budget_started_unix']
    if type(started) not in (int, float) or not 0 <= time.time() - started < BUDGET_SECONDS - RESERVE_SECONDS:
        raise ValueError('Original diagnostic budget unavailable')
    evidence = inspect_service_log(args.service_log, True)
    prepared = json.loads((args.out / 'preparation.json').read_text())
    if evidence['owned_pid'] != prepared['service_evidence']['owned_pid']:
        raise ValueError('Owned service changed after diagnostic preparation')
    exclusive_json(args.out / 'run-started.json', {'git_commit': revision, 'unix': time.time(),
                   'budget_started_unix': started, 'transport': binding, 'service_evidence': evidence})
    # Exclusive run marker deliberately rejects every second invocation, even
    # after a clean resource stop. There is no automatic resume/retry interface.
    deadline = started + BUDGET_SECONDS
    remaining_initial, monotonic_started = deadline - time.time(), time.monotonic()
    reason = 'Four synthetic runtime calls completed; no benchmark result'
    journal = args.out / 'journal.jsonl'
    try:
        checked = remote.rpc('verify_preflight', sources, binding, jobs=jobs(), report=report)
        if checked != report:
            raise ValueError('Diagnostic verification changed immutable report')
        for number, job in enumerate(jobs(), 1):
            if records.remaining_budget(deadline, remaining_initial, monotonic_started) < RESERVE_SECONDS:
                reason = 'Diagnostic budget reserve reached'
                break
            inspect_service_log(args.service_log, True)
            snapshot = remote.rpc('resource_snapshot', sources, binding)
            violations = resources.violations(snapshot, report['resource_baseline'])
            records.append_event(journal, {'kind': 'resource_check', 'stage': 'before', 'id': job['id'],
                                          'snapshot': snapshot, 'violations': violations})
            if violations:
                reason = 'Resource stop: ' + '; '.join(violations)
                break
            runtime = remote.rpc('runtime_idle', sources, binding, jobs=jobs(), report=report)
            if runtime['runner']['parent_pid'] != evidence['owned_pid']:
                raise ValueError('Backend does not belong to cache-disabled owned service')
            identity = remote.rpc('metadata', sources, binding)
            identity_keys = ('model_digest', 'server_version', 'template_sha256', 'parameters_sha256',
                             'model_path', 'binary_sha256', 'library_sha256')
            if any(identity.get(key) != report.get(key) for key in identity_keys):
                raise ValueError('Diagnostic model/template/runtime identity changed')
            records.append_event(journal, {'kind': 'runtime_identity_check', 'id': job['id'],
                'runtime': runtime, 'identity': {key: identity[key] for key in identity_keys},
                'owned_service_pid': evidence['owned_pid']})
            if records.remaining_budget(deadline, remaining_initial, monotonic_started) < RESERVE_SECONDS:
                reason = 'Diagnostic budget reserve reached after admission checks'
                break
            records.append_event(journal, {'kind': 'attempt_started', 'id': job['id'],
                'attempt_number': number, 'messages_sha256': job['messages_sha256'], 'unix': time.time()})
            stream_path = args.out / ('stream-%02d.jsonl' % number)
            error = None
            call_started = time.monotonic()
            try:
                with stream_path.open('xb') as output:
                    def on_line(line):
                        output.write(line)
                        output.flush()
                        chunk = json.loads(line)
                        return chunk.get('done') is True or bool(chunk.get('error'))
                    try:
                        remote.rpc('stream_subject', sources, binding, on_line=on_line,
                                   jobs=jobs(), report=report, job_id=job['id'],
                                   payload={'model': records.MODEL, 'messages': job['messages'],
                                            'options': remote.profile_options(PROFILE), 'stream': True,
                                            'truncate': False, 'shift': False, 'keep_alive': '30s'})
                    finally:
                        output.flush()
                        os.fsync(output.fileno())
            except Exception as caught:
                error = {'type': type(caught).__name__, 'message': str(caught),
                         'server_cancellation': 'unverified; no retry'}
            raw = stream_path.read_bytes() if stream_path.exists() else b''
            decoded = records.decode_stream(raw)
            final = decoded['raw_final_response'] or {}
            if error is None and (decoded['stream_error'] or final.get('done') is not True or final.get('error')
                    or final.get('done_reason') not in ('stop', 'length')
                    or type(final.get('eval_count')) is not int or not 0 <= final['eval_count'] <= 1
                    or final.get('prompt_eval_count') != report['tokens'][job['id']]['prompt_tokens']):
                error = {'type': 'DiagnosticCompletionMismatch', 'message': 'Unexpected completion/count/stream',
                         'server_cancellation': 'unverified; no retry'}
            row = {'id': job['id'], 'purpose': PROFILE, 'messages_sha256': job['messages_sha256'],
                   'attempt_number': number, 'elapsed_seconds': time.monotonic() - call_started,
                   'stream_sha256': remote.sha(raw), **decoded, 'request_error': error}
            records.append_event(args.out / 'responses.jsonl', row)
            records.append_event(journal, {'kind': 'attempt_finished', 'id': job['id'],
                                          'response_sha256': records.canonical_hash(row)})
            if error:
                reason = 'Request failed; server state unresolved; no retry'
                break
            snapshot = remote.rpc('resource_snapshot', sources, binding)
            violations = resources.violations(snapshot, report['resource_baseline'])
            records.append_event(journal, {'kind': 'resource_check', 'stage': 'after', 'id': job['id'],
                                          'snapshot': snapshot, 'violations': violations})
            if violations:
                reason = 'Resource stop: ' + '; '.join(violations)
                break
    except BaseException as error:
        reason = 'Stopped: ' + type(error).__name__ + ': ' + str(error)
        raise
    finally:
        records.append_event(journal, {'kind': 'session_finished', 'unix': time.time(), 'reason': reason})
        summary(args, reason)
    return summary(args, reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'run'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--service-log', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args) if args.phase == 'prepare' else run(args)))


if __name__ == '__main__':
    main()
