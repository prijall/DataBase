"""Bounded local verification-only screen on thirty existing arithmetic traces."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile
import time

import pilot

ROOT = Path(__file__).resolve().parent
SYSTEM = ('Check every numbered numerical equality independently. The chain is VALID only '
          'if every equality is true. If any equality is false, the chain is INVALID. '
          'Output exactly VALID or INVALID without explanation.')
CONDITIONS = ('valid_correct', 'invalid_wrong', 'invalid_correct')
OPTIONS = {'temperature': 0, 'seed': 42, 'num_ctx': 2048, 'num_predict': 16, 'num_thread': 2}
GATE = {'minimum_usable': 27, 'minimum_usable_per_cell': 9,
        'minimum_valid_acceptance': 8, 'minimum_invalid_wrong_rejection': 8}


def parse_response(content):
    if not isinstance(content, str):
        return None
    value = content.strip()
    if not re.fullmatch(r'(VALID|INVALID)\.?', value, flags=re.IGNORECASE | re.ASCII):
        return None
    return value.rstrip('.').upper()


def score(content, gold_valid, response):
    parsed = parse_response(content)
    completed = (response.get('done') is True and not response.get('error')
                 and response.get('done_reason') == 'stop')
    usable = parsed is not None and completed
    return {'parsed': parsed, 'format_valid': parsed is not None, 'completed': bool(completed),
            'usable': bool(usable),
            'validity_correct': bool(usable and (parsed == 'VALID') == gold_valid),
            'endorsed_trace': (parsed == 'VALID') if usable else None}


def jobs(examples):
    planned = []
    for item in examples:
        for condition in CONDITIONS:
            trace = item['traces'][condition]
            pairs = zip(trace['expressions'], trace['expressions'][1:])
            question = 'Check this chain of numerical equalities:\n' + '\n'.join(
                f'{index}. {left} = {right}' for index, (left, right) in enumerate(pairs, 1))
            planned.append({'id': f"{item['id']}/{condition}", 'item_id': item['id'],
                            'condition': condition, 'gold_valid': trace['trace_valid'],
                            'messages': [{'role': 'system', 'content': SYSTEM},
                                         {'role': 'user', 'content': question}]})
    random.Random(42).shuffle(planned)
    return planned


@contextmanager
def run_lock(directory):
    """Only one writer or summarizer may work on a run directory at a time."""
    with (directory / '.writer.lock').open('a') as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('Run directory is already in use') from error
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_write(path, text):
    """Replace a small artifact only after all new bytes have reached its temp file."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix=path.name + '.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def append_record(path, record):
    # Thirty small records permit atomic replacement while preserving the log prefix.
    previous = path.read_text() if path.exists() else ''
    if previous and not previous.endswith('\n'):
        raise ValueError('Refusing to append to an unterminated log')
    atomic_write(path, previous + json.dumps(record) + '\n')


def checked_records(directory, planned):
    records = pilot.load_records(directory / 'responses.jsonl')
    expected = {job['id']: job for job in planned}
    for key, row in records.items():
        if key not in expected:
            raise ValueError('Unknown saved job ID')
        job = expected[key]
        for field in ('item_id', 'condition', 'gold_valid', 'messages'):
            if row[field] != job[field]:
                raise ValueError(f'Saved {field} differs from current job')
        message = row['raw_response'].get('message')
        raw_content = message.get('content', '') if isinstance(message, dict) else ''
        if row['content'] != raw_content:
            raise ValueError('Saved content disagrees with raw response text')
        if row['score'] != score(row['content'], job['gold_valid'], row['raw_response']):
            raise ValueError('Stored score disagrees with raw response')
    return records


def analyze(records):
    rows = list(records.values())
    cells = {}
    for condition in CONDITIONS:
        selected = [row for row in rows if row['condition'] == condition]
        cells[condition] = {'n': len(selected),
                            'completed': sum(row['score']['completed'] for row in selected),
                            'format_valid': sum(row['score']['format_valid'] for row in selected),
                            'usable': sum(row['score']['usable'] for row in selected),
                            'malformed': sum(not row['score']['format_valid'] for row in selected),
                            'length_stops': sum(row['raw_response'].get('done_reason') == 'length' for row in selected),
                            'malformed_length_stops': sum(row['raw_response'].get('done_reason') == 'length'
                                                          and not row['score']['format_valid'] for row in selected),
                            'correct': sum(row['score']['validity_correct'] for row in selected)}
    usable = sum(cell['usable'] for cell in cells.values())
    complete = len(rows) == 30 and all(cell['n'] == 10 for cell in cells.values())
    passed = (complete and usable >= GATE['minimum_usable']
              and all(cell['usable'] >= GATE['minimum_usable_per_cell'] for cell in cells.values())
              and cells['valid_correct']['correct'] >= GATE['minimum_valid_acceptance']
              and cells['invalid_wrong']['correct'] >= GATE['minimum_invalid_wrong_rejection'])
    item_ids = [item['id'] for item in json.loads(pilot.DATA.read_text())]

    def paired(first, second):
        counts = dict(complete_pairs=0, both_success=0, only_first=0, only_second=0,
                      neither=0, missing_one=0, missing_both=0)
        for item_id in item_ids:
            left, right = records.get(f'{item_id}/{first}'), records.get(f'{item_id}/{second}')
            if left is None and right is None:
                counts['missing_both'] += 1
            elif left is None or right is None:
                counts['missing_one'] += 1
            else:
                counts['complete_pairs'] += 1
                a, b = left['score']['validity_correct'], right['score']['validity_correct']
                counts['both_success' if a and b else 'only_first' if a else 'only_second' if b else 'neither'] += 1
        return counts

    balanced_accuracy = ((cells['valid_correct']['correct'] / 10
                          + cells['invalid_wrong']['correct'] / 10) / 2) if complete else None
    return {'n': len(rows), 'complete': complete, 'cells': cells, 'usable': usable,
            'primary_balanced_accuracy': balanced_accuracy,
            'primary_pairs': paired('valid_correct', 'invalid_wrong'),
            'invalid_pairs': paired('invalid_wrong', 'invalid_correct'),
            'format_valid': sum(cell['format_valid'] for cell in cells.values()),
            'length_stops': sum(row['raw_response'].get('done_reason') == 'length' for row in rows),
            'lexical_length_overlap': sum(row['raw_response'].get('done_reason') == 'length'
                                         and row['score']['format_valid'] for row in rows),
            'malformed_length_overlap': sum(row['raw_response'].get('done_reason') == 'length'
                                           and not row['score']['format_valid'] for row in rows),
            'unknown_stop_reason': sum(not row['raw_response'].get('done_reason') for row in rows),
            'execution_failures': sum(row['raw_response'].get('done') is not True
                                      or bool(row['raw_response'].get('error')) for row in rows),
            'gate_passed': passed}


def summarize(directory):
    examples = json.loads(pilot.DATA.read_text())
    pilot.validate(examples)
    records = checked_records(directory, jobs(examples))
    report = analyze(records)
    lines = ['# Verification-only development screen', '',
             f"Recorded responses: **{report['n']}/30**. Gate: "
             f"**{'PASS' if report['gate_passed'] else 'NOT PASSED'}**. "
             f"Complete run: {report['complete']}.", '',
             'Lexical format accepts only VALID or INVALID, case-insensitively, with outer whitespace '
             'and at most one final period. A usable outcome additionally requires done=true, no server '
             'error, and done_reason=stop. Length-stopped labels are unsuccessful even if lexically valid.', '',
             f"Lexically valid: {report['format_valid']}/{report['n']}; usable: "
             f"{report['usable']}/{report['n']}; reported length stops: {report['length_stops']}; "
             f"lexically valid length-stop overlap: {report['lexical_length_overlap']}; "
             f"malformed length-stop overlap: {report['malformed_length_overlap']}; "
             f"missing stop reasons: {report['unknown_stop_reason']}; "
             f"execution failures: {report['execution_failures']}.", '',
             '| Condition | Role | Recorded / planned | Completed | Lexically valid | Usable | Malformed | Length stops | Malformed + length | Correct / all recorded | Correct / usable |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for condition, cell in report['cells'].items():
        parsed_rate = f"{cell['correct']}/{cell['usable']}" if cell['usable'] else 'not estimable'
        role = 'primary: accept valid' if condition == 'valid_correct' else (
            'primary: reject invalid' if condition == 'invalid_wrong' else 'secondary descriptive')
        lines.append(f"| {condition} | {role} | {cell['n']}/10 | {cell['completed']}/{cell['n']} | "
                     f"{cell['format_valid']}/{cell['n']} | {cell['usable']}/{cell['n']} | "
                     f"{cell['malformed']}/{cell['n']} | {cell['length_stops']}/{cell['n']} | "
                     f"{cell['malformed_length_stops']}/{cell['n']} | {cell['correct']}/{cell['n']} | {parsed_rate} |")
    primary = [report['cells'][condition] for condition in ('valid_correct', 'invalid_wrong')]
    balanced = ('not estimable (incomplete run)' if report['primary_balanced_accuracy'] is None else
                f"{100 * report['primary_balanced_accuracy']:.1f}%")
    lines += ['', f"Primary comparison: {sum(cell['correct'] for cell in primary)}/"
              f"{sum(cell['n'] for cell in primary)} correct across recorded calls "
              '(20 planned: ten valid and ten invalid/wrong traces).', '',
              f'Primary balanced accuracy: **{balanced}**; computed only for a complete run as the '
              'mean of valid acceptance and invalid/wrong rejection rates, each over ten planned items.', '',
              '## Paired outcomes by underlying problem', '',
              'Each row uses only complete recorded pairs; malformed and truncated outputs remain '
              'unsuccessful. Missing records are shown separately. These are related traces, not '
              'independent observations. Invalid-condition differences also confound error count.', '',
              '| First condition | Second condition | Complete pairs | Both successful | Only first | Only second | Neither | Missing one | Missing both |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for first, second, values in [('valid_correct', 'invalid_wrong', report['primary_pairs']),
                                  ('invalid_wrong', 'invalid_correct', report['invalid_pairs'])]:
        lines.append('| ' + ' | '.join([first, second] + [str(values[key]) for key in
                     ('complete_pairs', 'both_success', 'only_first', 'only_second', 'neither',
                      'missing_one', 'missing_both')]) + ' |')
    lines += ['',
              'Gate requires all thirty responses, at least 27 usable overall, at least 9 usable in '
              'each ten-item condition, at least 8/10 valid traces correctly accepted, and at least '
              '8/10 invalid/wrong traces correctly rejected. Malformed, truncated, and failed outputs '
              'are unsuccessful, never omitted from the all-call denominator. Partial runs do not pass.', '',
              'The thirty calls share ten development problems. Invalid/correct traces are secondary '
              'because their error count differs from invalid/wrong traces. All first errors occur at '
              'step one. This is a jointly changed protocol feasibility screen, not an isolated causal '
              'test against earlier protocols, a held-out benchmark, or an intervention result. '
              'Continue to the fixed thirty calls regardless of intermediate scores; do not add retries.', '']
    atomic_write(directory / 'SUMMARY.md', '\n'.join(lines))
    return report


def run(args):
    if not 1 <= args.max_calls <= 30 or not 1 <= args.timeout < args.max_seconds <= 32400:
        raise ValueError('Require 1..30 calls and 1 <= timeout < max-seconds <= 32400')
    examples = json.loads(pilot.DATA.read_text())
    pilot.validate(examples)
    planned = jobs(examples)
    model = next((entry for entry in pilot.api('tags')['models'] if entry['name'] == args.model), None)
    if model is None or model.get('remote_host') or ':cloud' in args.model or '-cloud' in args.model:
        raise ValueError('Choose an already installed local model; cloud models are disallowed')
    shown = pilot.api('show', {'model': args.model})
    if shown.get('remote_host') or shown.get('remote_model'):
        raise ValueError('Remote model refused')
    protocol = {'protocol_name': 'verification-only-v1', 'dataset_sha256': pilot.digest(examples),
                'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'pilot_dependency_sha256': hashlib.sha256(Path(pilot.__file__).read_bytes()).hexdigest(),
                'protocol_document_sha256': hashlib.sha256((ROOT / 'VERIFICATION_ONLY_PROTOCOL.md').read_bytes()).hexdigest(),
                'model': args.model, 'model_digest': model['digest'], 'details': model['details'],
                'template_sha256': pilot.digest(shown.get('template')), 'parameters': shown.get('parameters'),
                'system_sha256': pilot.digest(SYSTEM), 'system': SYSTEM, 'options': OPTIONS,
                'format': None, 'job_seed': 42, 'server_version': pilot.api('version')['version'],
                'parser': 'single-label-optional-period-v1', 'usable_stop_reason': 'stop',
                'planned_calls': 30, 'gate': GATE, 'intervention': 'none'}
    args.out.mkdir(parents=True, exist_ok=True)
    with run_lock(args.out):
        manifest = args.out / 'manifest.json'
        if manifest.exists():
            if json.loads(manifest.read_text())['protocol'] != protocol:
                raise ValueError('Resume refused: model, code, dataset, or protocol changed; use a new run directory')
        else:
            if (args.out / 'responses.jsonl').exists():
                raise ValueError('Responses exist without a manifest; refusing to infer their protocol')
            revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            atomic_write(manifest, json.dumps({'created_utc': datetime.now(timezone.utc).isoformat(),
                                              'git_commit': revision, 'protocol': protocol}, indent=2) + '\n')
        saved = checked_records(args.out, planned)
        started, calls = time.monotonic(), 0
        try:
            for job in planned:
                if job['id'] in saved:
                    continue
                if calls >= args.max_calls or time.monotonic() - started >= args.max_seconds - args.timeout:
                    print('Slice limit reached; resume with the same protocol and directory.', flush=True)
                    break
                request_started = time.monotonic()
                result = pilot.api('chat', {'model': args.model, 'messages': job['messages'], 'stream': False,
                                           'options': OPTIONS, 'keep_alive': '30s'}, args.timeout)
                message = result.get('message')
                content = message.get('content', '') if isinstance(message, dict) else ''
                row = dict(job, utc=datetime.now(timezone.utc).isoformat(),
                           elapsed_seconds=time.monotonic() - request_started,
                           content=content, raw_response=result,
                           score=score(content, job['gold_valid'], result))
                append_record(args.out / 'responses.jsonl', row)
                saved[row['id']] = row
                calls += 1
                print(f"{len(saved)}/30 {row['id']} format={row['score']['format_valid']} "
                      f"usable={row['score']['usable']} correct={row['score']['validity_correct']}", flush=True)
                if result.get('done') is not True or result.get('error'):
                    raise ValueError('Server execution failure recorded; no automatic retry')
        finally:
            append_record(args.out / 'sessions.jsonl', {'utc': datetime.now(timezone.utc).isoformat(),
                          'recorded_calls': calls, 'elapsed_seconds': time.monotonic() - started})
            summarize(args.out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    report = commands.add_parser('summarize')
    report.add_argument('--out', type=Path, required=True)
    runner = commands.add_parser('run')
    runner.add_argument('--model', required=True)
    runner.add_argument('--out', type=Path, required=True)
    runner.add_argument('--max-calls', type=int, default=30)
    runner.add_argument('--max-seconds', type=int, default=600)
    runner.add_argument('--timeout', type=int, default=60)
    args = parser.parse_args()
    if args.command == 'run':
        run(args)
    else:
        with run_lock(args.out):
            print(json.dumps(summarize(args.out), indent=2))


if __name__ == '__main__':
    main()
