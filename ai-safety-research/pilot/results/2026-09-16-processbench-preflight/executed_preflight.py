"""Pinned Ollama debug rendering + bundled tokenizer; never request generation.

This deliberately supports one installed model and server version. Debug rendering
loads the existing model. It does not call completion. Review before first use.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import time
import urllib.request

import processbench_resources

VERSION = '0.34.0'
MODEL = 'llama3.2:3b'
MODEL_DIGEST = 'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
OPTIONS = {'temperature': 0, 'seed': 42, 'num_ctx': 8192, 'num_predict': 1024, 'num_thread': 2}
BINARY = Path('/Applications/Ollama.app/Contents/Resources/llama-server')
BINARY_SHA256 = '12a8bd0922404bb941fcd4f3fb56ea32251acfdd11e6af8aa99c8703557c23d6'
LIBRARY = BINARY.with_name('libllama.0.3.0.dylib')
LIBRARY_SHA256 = '207fecc90bd3279588ce08c3cfef690d914317d30eb91d07a359881b3d4fb6ff'
SOURCE = {'ollama_commit': 'd8ab4b4f0ca24b51d3a46b3bf4f462e58ce66b1f',
          'llama_cpp_commit': '0f3a71be15af836d277c9f918adfafb45732677e'}
SCHEMA = 'processbench-exact-token-preflight-v1'
BUDGET_SECONDS = 5400
SYSTEM_PREFIX = '<|start_header_id|>system<|end_header_id|>\n\nCutting Knowledge Date: December 2023'
TEMPLATE_SHA256 = '966de95ca8a62200913e3f8bfbf84c8494536f1b94b49166851e76644e966396'
PARAMETERS_SHA256 = '2801e61a8848e505a6e20beeaea63cca1600200f6720e5f916ba7d6da5c3ba39'
_AUDIT = None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def resource_snapshot():
    value = processbench_resources.snapshot()
    if _AUDIT is not None:
        _AUDIT.setdefault('resource_observations', []).append(value)
    return value


def resource_check(current, baseline):
    reasons = processbench_resources.violations(current, baseline)
    if reasons:
        raise ValueError('Resource guard: ' + '; '.join(reasons))
    return current


def request_json(port, path, payload=None, timeout=60):
    """Fixed loopback; proxies/redirects disabled; only non-generating endpoints."""
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Invalid loopback port')
    if port == 11434:
        if path not in ('/api/version', '/api/tags', '/api/show', '/api/ps', '/api/chat'):
            raise ValueError('Endpoint refused')
        if path == '/api/chat' and (not isinstance(payload, dict) or payload.get('_debug_render_only') is not True):
            raise ValueError('Only explicitly debug-only chat requests are permitted')
    elif path not in ('/tokenize', '/slots'):
        raise ValueError('Only runner tokenization and idle inspection are permitted')

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise ValueError('Loopback redirect refused')

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    body = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(f'http://127.0.0.1:{port}{path}', data=body,
                                     headers={'Content-Type': 'application/json'})
    event = {'port': port, 'endpoint': path, 'started_unix': time.time(), 'status': 'attempting'}
    if _AUDIT is not None:
        _AUDIT.setdefault('operations', []).append(event)
        if path == '/api/chat':
            _AUDIT['runtime_state'] = 'unverified_after_debug_request'
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(8 * 1024 * 1024 + 1)
        event['status'] = 'received'
    except Exception as error:
        event['status'] = 'failed'
        event['reason'] = str(error)
        raise
    finally:
        event['finished_unix'] = time.time()
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError('Unexpectedly large preflight response')
    return json.loads(raw)


def validate_jobs(jobs):
    if not isinstance(jobs, list) or len(jobs) != 60:
        raise ValueError('Require exactly the frozen sixty jobs')
    seen, split_counts = set(), {'calibration': 0, 'evaluation': 0}
    for job in jobs:
        if not isinstance(job.get('id'), str) or job['id'] in seen:
            raise ValueError('Missing/duplicate job ID')
        seen.add(job['id'])
        if job.get('split') not in split_counts:
            raise ValueError('Unknown split')
        split_counts[job['split']] += 1
        messages = job.get('messages')
        if not isinstance(messages, list) or len(messages) != 1 or set(messages[0]) != {'role', 'content'}:
            raise ValueError('Require exactly one plain user message')
        if messages[0]['role'] != 'user' or not isinstance(messages[0]['content'], str) or not messages[0]['content']:
            raise ValueError('Invalid user message')
        if job.get('messages_sha256') != digest(messages):
            raise ValueError('Message hash mismatch')
        if type(job.get('step_count')) is not int or job['step_count'] < 1:
            raise ValueError('Invalid step count')
        if type(job.get('gold_label')) is not int or not -1 <= job['gold_label'] < job['step_count']:
            raise ValueError('Invalid gold label')
    if split_counts != {'calibration': 20, 'evaluation': 40}:
        raise ValueError('Unexpected split counts')


def inspect_identity(model, options):
    if model != MODEL or options != OPTIONS:
        raise ValueError('Only the fixed model/configuration is supported')
    version = request_json(11434, '/api/version').get('version')
    if version != VERSION:
        raise ValueError('Unaudited server version; refusing even debug requests')
    tags = request_json(11434, '/api/tags')['models']
    matches = [entry for entry in tags if entry.get('name') == model]
    if len(matches) != 1 or matches[0].get('digest') != MODEL_DIGEST or matches[0].get('remote_host'):
        raise ValueError('Installed model identity mismatch')
    shown = request_json(11434, '/api/show', {'model': model})
    if shown.get('remote_host') or shown.get('remote_model') or shown.get('system') or shown.get('messages'):
        raise ValueError('Remote model or additional model instructions refused')
    template = shown.get('template')
    if not isinstance(template, str) or hashlib.sha256(template.encode()).hexdigest() != TEMPLATE_SHA256:
        raise ValueError('Unexpected installed template')
    parameters = shown.get('parameters')
    if not isinstance(parameters, str) or hashlib.sha256(parameters.encode()).hexdigest() != PARAMETERS_SHA256:
        raise ValueError('Unexpected installed stop/default parameters')
    match = re.search(r'^FROM (/.*/sha256-[0-9a-f]{64})$', shown.get('modelfile', ''), re.MULTILINE)
    if match is None:
        raise ValueError('Cannot bind local GGUF path')
    if file_hash(BINARY) != BINARY_SHA256 or file_hash(LIBRARY) != LIBRARY_SHA256:
        raise ValueError('Bundled tokenizer binary/library changed')
    return {'model_digest': MODEL_DIGEST, 'server_version': version,
            'template_sha256': hashlib.sha256(template.encode()).hexdigest(),
            'parameters_sha256': PARAMETERS_SHA256,
            'model_path': match[1], 'model_details': matches[0].get('details'),
            'binary_sha256': BINARY_SHA256, 'library_sha256': LIBRARY_SHA256}


def loaded_state(require_loaded=False):
    models = request_json(11434, '/api/ps')['models']
    if len(models) > 1 or any(entry.get('name') != MODEL or entry.get('digest') != MODEL_DIGEST for entry in models):
        raise ValueError('Another model is resident; shared workload must not be displaced')
    if require_loaded and (not models or type(models[0].get('context_length')) is not int
                           or models[0]['context_length'] < OPTIONS['num_ctx']):
        raise ValueError('Requested context capacity was not confirmed')
    return models


def discover_runner(model_path):
    output = subprocess.run(['/bin/ps', '-axo', 'pid=,ppid=,command='], check=True,
                            capture_output=True, text=True, timeout=10).stdout
    found = []
    for line in output.splitlines():
        fields = line.strip().split(None, 2)
        if len(fields) != 3:
            continue
        try:
            argv = shlex.split(fields[2])
        except ValueError:
            continue
        if not argv or argv[0] != str(BINARY):
            continue
        def value(*names):
            for index, argument in enumerate(argv):
                for name in names:
                    if argument == name and index + 1 < len(argv):
                        return argv[index + 1]
                    if argument.startswith(name + '='):
                        return argument[len(name) + 1:]
            return None
        if value('--model', '-m') != model_path:
            continue
        port = value('--port')
        if port is None or not port.isdigit() or value('--host') not in (None, '127.0.0.1', 'localhost'):
            raise ValueError('Cannot safely identify runner loopback port')
        if int(port) == 11434:
            raise ValueError('Runner port conflicts with public API')
        found.append({'pid': int(fields[0]), 'port': int(port), 'parent_pid': int(fields[1])})
    if len(found) != 1:
        raise ValueError('Expected one exact-model bundled runner')
    return found[0]


def ensure_idle(port):
    slots = request_json(port, '/slots', timeout=10)
    if not isinstance(slots, list) or not slots or any(slot.get('is_processing') is not False for slot in slots):
        raise ValueError('Runner idle state could not be verified')
    if _AUDIT is not None:
        _AUDIT['runtime_state'] = 'idle_confirmed'


def verify_runtime_idle(report, model):
    """Refresh exact runner discovery; no cached-port assumptions or model load."""
    if model != MODEL or report.get('model_digest') != MODEL_DIGEST:
        raise ValueError('Wrong runtime model')
    if request_json(11434, '/api/version').get('version') != VERSION:
        raise ValueError('Runtime server version changed')
    if file_hash(BINARY) != BINARY_SHA256 or file_hash(LIBRARY) != LIBRARY_SHA256:
        raise ValueError('Runtime binary/library changed')
    resident = loaded_state(require_loaded=True)
    runner = discover_runner(report['model_path'])
    ensure_idle(runner['port'])
    return {'runner': runner, 'resident_models': resident}


def tokenize(port, rendered):
    result = request_json(port, '/tokenize', {'content': rendered, 'add_special': True,
                                            'parse_special': True}, timeout=15)
    tokens = result.get('tokens')
    if not isinstance(tokens, list) or not tokens or any(type(token) is not int or token < 0 for token in tokens):
        raise ValueError('Unexpected tokenizer response')
    # This installed template has no explicit BOS; llama.cpp adds exactly one.
    if tokens[0] != 128000 or tokens.count(128000) != 1:
        raise ValueError('Unexpected BOS handling; do not adjust counts silently')
    return tokens


def run_checks(jobs, model, options, baseline, budget_started):
    validate_jobs(jobs)
    identity = inspect_identity(model, options)
    resource_check(resource_snapshot(), baseline)
    counts, runner, resident = {}, None, None
    initially_resident = loaded_state()
    if initially_resident:
        if initially_resident[0].get('context_length') != options['num_ctx']:
            raise ValueError('Resident context differs; do not reconfigure a shared runner')
        runner = discover_runner(identity['model_path'])
        ensure_idle(runner['port'])
    if _AUDIT is not None:
        _AUDIT['tokens'] = counts
        _AUDIT.update(identity)
    for job in jobs:
        if time.time() - budget_started >= BUDGET_SECONDS - 90:
            raise ValueError('Session budget cannot cover preflight and cleanup')
        resource_check(resource_snapshot(), baseline)
        if runner:
            ensure_idle(runner['port'])
        response = request_json(11434, '/api/chat', {
            'model': model, 'messages': job['messages'], 'stream': False,
            '_debug_render_only': True, 'truncate': False, 'shift': False,
            'options': options, 'keep_alive': '30s'}, timeout=60)
        rendered = response.get('debug_info', {}).get('rendered_template')
        content = job['messages'][0]['content']
        if not isinstance(rendered, str) or not rendered.startswith(SYSTEM_PREFIX) or rendered.count(content) != 1:
            raise ValueError('Debug rendering missing, changed, or truncated the user message')
        if response.get('eval_count', 0) != 0 or response.get('message', {}).get('content'):
            raise ValueError('Unexpected generated output in debug-only response')
        resident = loaded_state(require_loaded=True)
        resource_check(resource_snapshot(), baseline)
        current_runner = discover_runner(identity['model_path'])
        if runner and current_runner != runner:
            raise ValueError('Runner changed during preflight')
        runner = current_runner
        ensure_idle(runner['port'])
        tokens = tokenize(runner['port'], rendered)
        if len(tokens) + options['num_predict'] > options['num_ctx']:
            raise ValueError(f'Context reserve exceeded for {job["id"]}')
        counts[job['id']] = {'prompt_tokens': len(tokens), 'rendered_sha256': hashlib.sha256(rendered.encode()).hexdigest(),
                             'messages_sha256': job['messages_sha256'], 'tokens_sha256': digest(tokens)}
    ensure_idle(runner['port'])
    resource_check(resource_snapshot(), baseline)
    if inspect_identity(model, options) != identity:
        raise ValueError('Model identity changed during preflight')
    return {'tokens': counts, 'runner': runner, 'resident_models': resident, **identity}


def bindings(jobs, model, options):
    return {'schema': SCHEMA, 'jobs_sha256': digest(jobs), 'model': model, 'options': options,
            'sources': SOURCE, 'preflight_code_sha256': file_hash(__file__),
            'resource_code_sha256': file_hash(processbench_resources.__file__)}


def create_preflight(report_path, jobs, model=MODEL, options=None):
    global _AUDIT
    options = OPTIONS.copy() if options is None else options
    path = Path(report_path)
    if path.exists():
        raise ValueError('Preflight reports are immutable; verify the existing report')
    started = time.time()
    report = {**bindings(jobs, model, options), 'budget_started_unix': started,
              'resource_baseline': None, 'status': 'checking', 'operations': [],
              'generation_requests': 0, 'runtime_state': 'not_inspected'}
    path.parent.mkdir(parents=True, exist_ok=True)
    if _AUDIT is not None:
        raise ValueError('Concurrent preflight calls are unsupported')
    _AUDIT = report
    try:
        validate_jobs(jobs)
        baseline = resource_snapshot()
        report['resource_baseline'] = baseline
        resource_check(baseline, None)
        # A fresh ownership baseline must precede loading; never adopt shared state.
        if loaded_state():
            raise ValueError('Fresh preflight requires no resident model')
        report.update(run_checks(jobs, model, options, baseline, started))
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'blocked'
        report['reason'] = str(error)
        raise
    finally:
        _AUDIT = None
        report['finished_unix'] = time.time()
        report['operation_counts'] = {endpoint: sum(event['endpoint'] == endpoint for event in report['operations'])
                                      for endpoint in sorted({event['endpoint'] for event in report['operations']})}
        with path.open('x') as stream:
            stream.write(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    return report


def verify_preflight(report_path, jobs, model, options):
    """Recheck identity/rendering/token counts without rewriting report or budget."""
    report = json.loads(Path(report_path).read_text())
    expected = bindings(jobs, model, options)
    if report.get('status') != 'passed' or any(report.get(key) != value for key, value in expected.items()):
        raise ValueError('Preflight status/provenance mismatch')
    started = report.get('budget_started_unix')
    if type(started) not in (int, float) or not 0 <= time.time() - started < BUDGET_SECONDS - 90:
        raise ValueError('Preflight session budget is invalid or expired')
    refreshed = run_checks(jobs, model, options, report['resource_baseline'], started)
    for key in ('tokens', 'model_digest', 'server_version', 'template_sha256', 'model_path',
                'binary_sha256', 'library_sha256', 'parameters_sha256'):
        if report.get(key) != refreshed[key]:
            raise ValueError('Preflight identity or exact tokenization changed: ' + key)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=Path, required=True, help='Frozen sixty jobs as a JSON list')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    jobs = json.loads(args.jobs.read_text())
    report = (verify_preflight(args.out, jobs, MODEL, OPTIONS) if args.verify else create_preflight(args.out, jobs))
    print(json.dumps({'status': report['status'], 'jobs': len(report['tokens']),
                      'maximum_prompt_tokens': max(row['prompt_tokens'] for row in report['tokens'].values())}))


if __name__ == '__main__':
    main()
