"""Fixed M4 SSH transport. Research code/data exist remotely only in process memory.

All artifacts and durable attempt journals are written on the controller. Remote
transport failures do not establish server cancellation and must not be retried.
"""
import argparse
import ast
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time

TARGET = 'prabs@100.74.220.25'
API_PORT = 11435
ROOT = Path(__file__).resolve().parent
REMOTE_RESERVE = 150
PROFILE_NAMES = ('original', 'small-context-v1')
SMALL_PROFILE_FILES = {'profile_plan': 'PROCESSBENCH_SMALL_CONTEXT_PLAN.md',
                       'profile_selector': 'processbench_small_selection.py',
                       'profile_selection': 'processbench/selection-small-context.json'}


def profile_options(profile):
    if profile not in PROFILE_NAMES:
        raise ValueError('Unknown execution profile')
    return {'temperature': 0, 'seed': 42, 'num_ctx': 2048 if profile == 'small-context-v1' else 8192,
            'num_predict': 1024, 'num_thread': 2}


def job_loader(profile):
    profile_options(profile)
    if profile == 'small-context-v1':
        from processbench_small_selection import load_jobs
    else:
        from processbench_run import load_jobs
    return load_jobs

SSH = ['/usr/bin/ssh', '-T', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'ControlMaster=no', '-o', 'ControlPath=none', '-o', 'ConnectTimeout=10',
       TARGET, '/usr/bin/python3 -B -']

# This program and its inputs are sent on stdin, never as a remote file. The
# in-process audit hook prevents the bundled helpers from creating artifacts.
WORKER = r'''
import sys, os, signal, time, json, hashlib, types, base64
import http.client, socket, threading
sys.dont_write_bytecode = True

def emit(value):
    print(json.dumps(value, ensure_ascii=False, allow_nan=False), flush=True)

def guard(event, args):
    if event == 'open':
        mode, flags = args[1], args[2]
        if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
            raise PermissionError('Remote research filesystem writes are forbidden')
    if event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.rename', 'os.link', 'os.symlink', 'os.chmod', 'os.chown', 'os.truncate', 'os.utime'):
        raise PermissionError('Remote filesystem mutation is forbidden')
    if event == 'subprocess.Popen':
        allowed = [
            ['/usr/sbin/sysctl', 'kern.memorystatus_vm_pressure_level', 'vm.swapusage'],
            ['/usr/bin/memory_pressure', '-Q'], ['/usr/bin/vm_stat'],
            ['/bin/ps', '-axo', 'pid=,ppid=,command=']]
        if args[1] not in allowed:
            raise PermissionError('Only audited read-only resource/process commands are allowed')
    if event in ('os.system', 'os.exec', 'os.posix_spawn', 'os.spawn'):
        raise PermissionError('Remote shell/exec forbidden')

sys.addaudithook(guard)

def load_bundle(request):
    modules, hashes = {}, {}
    for name in ('processbench_resources', 'processbench_preflight'):
        item = request['bundle'][name]
        actual = hashlib.sha256(item['source'].encode()).hexdigest()
        if actual != item['sha256']:
            raise ValueError('Bundled source hash mismatch')
        module = types.ModuleType(name)
        module.__file__ = '/__memory_only__/' + name + '.py'
        sys.modules[name] = module
        exec(compile(item['source'], module.__file__, 'exec'), module.__dict__)
        modules[name] = module
        hashes[module.__file__] = actual
    pf = modules['processbench_preflight']
    real_hash = pf.file_hash
    pf.file_hash = lambda path: hashes[str(path)] if str(path) in hashes else real_hash(path)
    pf.API_PORT = 11435
    profile = request.get('transport', {}).get('profile', 'original')
    if profile not in ('original', 'small-context-v1'):
        raise ValueError('Unknown execution profile')
    options = dict(pf.OPTIONS, num_ctx=2048 if profile == 'small-context-v1' else 8192)
    supplied = request.get('transport', {}).get('options', options)
    if supplied != options:
        raise ValueError('Execution profile/options mismatch')
    pf.OPTIONS = options
    if profile == 'small-context-v1':
        original_loaded_state = pf.loaded_state
        def exact_loaded_state(require_loaded=False):
            resident = original_loaded_state(require_loaded)
            if resident and resident[0].get('context_length') != 2048:
                raise ValueError('Small-context profile requires exactly 2048 resident tokens')
            return resident
        pf.loaded_state = exact_loaded_state
    return pf, modules['processbench_resources']

def check_report(pf, request):
    report = request['report']
    if report.get('transport') != request['transport']:
        raise ValueError('Remote transport binding changed')
    if report.get('status') != 'passed':
        raise ValueError('Passed preflight required')
    for name, value in pf.bindings(request['jobs'], pf.MODEL, pf.OPTIONS).items():
        if report.get(name) != value:
            raise ValueError('Preflight source/job/config binding changed: ' + name)
    started = report.get('budget_started_unix')
    if type(started) not in (int, float) or not 0 <= time.time() - started < 5400 - 150:
        raise ValueError('Original session budget invalid or exhausted')
    return report

def dispatch(request):
    pf, resources = load_bundle(request)
    action = request['action']
    if action == 'metadata':
        return pf.inspect_identity(pf.MODEL, pf.OPTIONS)
    if action == 'resource_snapshot':
        return resources.snapshot()
    if action == 'create_preflight':
        started = request['budget_started_unix']
        if type(started) not in (int, float) or not 0 <= time.time() - started < 30:
            raise ValueError('Controller/target clock or preflight dispatch delay invalid')
        report = dict(pf.bindings(request['jobs'], pf.MODEL, pf.OPTIONS),
                      transport=request['transport'], budget_started_unix=started,
                      resource_baseline=None, status='checking', operations=[],
                      generation_requests=0, runtime_state='not_inspected')
        pf._AUDIT = report
        try:
            pf.validate_jobs(request['jobs'])
            baseline = pf.resource_snapshot()
            report['resource_baseline'] = baseline
            pf.resource_check(baseline, None)
            if pf.loaded_state():
                raise ValueError('Fresh preflight requires no resident model')
            report.update(pf.run_checks(request['jobs'], pf.MODEL, pf.OPTIONS, baseline, started))
            report['status'] = 'passed'
        except Exception as error:
            report['status'] = 'blocked'
            report['reason'] = type(error).__name__ + ': ' + str(error)
        finally:
            pf._AUDIT = None
            report['finished_unix'] = time.time()
            report['operation_counts'] = {endpoint: sum(row['endpoint'] == endpoint for row in report['operations'])
                for endpoint in sorted({row['endpoint'] for row in report['operations']})}
        return report
    report = check_report(pf, request)
    if action == 'verify_preflight':
        refreshed = pf.run_checks(request['jobs'], pf.MODEL, pf.OPTIONS,
                                  report['resource_baseline'], report['budget_started_unix'])
        for key in ('tokens', 'model_digest', 'server_version', 'template_sha256', 'model_path',
                    'binary_sha256', 'library_sha256', 'parameters_sha256'):
            if report.get(key) != refreshed[key]:
                raise ValueError('Preflight identity/tokenization changed: ' + key)
        return report
    if action == 'runtime_idle':
        return pf.verify_runtime_idle(report, pf.MODEL)
    if action != 'stream_subject':
        raise ValueError('Unknown remote action')
    # Controller already checked current identity/resources/idle before journaling.
    # This single request may never initiate a second subject or retry.
    payload = request['payload']
    expected = {'model': pf.MODEL, 'messages': payload.get('messages'), 'stream': True,
                'truncate': False, 'shift': False, 'options': pf.OPTIONS, 'keep_alive': '30s'}
    if payload != expected:
        raise ValueError('Subject configuration differs from frozen settings')
    matches = [j for j in request['jobs'] if j['id'] == request['job_id']]
    if len(matches) != 1 or matches[0]['messages'] != payload['messages']:
        raise ValueError('Subject ID/prompt mismatch')
    if report['tokens'][request['job_id']]['messages_sha256'] != pf.digest(payload['messages']):
        raise ValueError('Subject prompt differs from exact token preflight')
    stream_source = request['bundle']['stream']
    if hashlib.sha256(stream_source['source'].encode()).hexdigest() != stream_source['sha256']:
        raise ValueError('Streaming source hash mismatch')
    namespace = dict(time=time, threading=threading, socket=socket, http=http,
                     json=json, REQUEST_SECONDS=90)
    exec(compile(stream_source['source'], '/__memory_only__/stream.py', 'exec'), namespace)
    def forward(line):
        emit({'line': base64.b64encode(line).decode('ascii')})
        chunk = json.loads(line)
        if not isinstance(chunk, dict):
            raise ValueError('Non-object stream event')
        return chunk.get('done') is True or bool(chunk.get('error'))
    namespace['stream_chat'](payload, forward, 90)
    return {'completed_transport': True}

def main(request):
    durations = {'create_preflight': 900, 'verify_preflight': 900,
                 'stream_subject': 95, 'metadata': 25, 'resource_snapshot': 25, 'runtime_idle': 25}
    if request.get('action') not in durations:
        raise ValueError('Unknown remote action')
    # SIGALRM defaults to process termination: survives controller disappearance.
    signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.alarm(durations[request['action']])
    try:
        result = dispatch(request)
        emit({'result': result})
    except Exception as error:
        emit({'error': type(error).__name__ + ': ' + str(error), 'server_cancellation': 'unverified'})
    finally:
        signal.alarm(0)
'''


def sha(value):
    return hashlib.sha256(value).hexdigest()


def stream_source():
    """Reuse reviewed deadline implementation; change only its fixed public port."""
    tree = ast.parse((ROOT / 'processbench_run.py').read_text())
    selected = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                and node.name in ('RequestDeadlineExceeded', 'stream_chat')]
    if len(selected) != 2:
        raise ValueError('Reviewed streaming definitions unavailable')
    class Port(ast.NodeTransformer):
        def visit_Constant(self, node):
            return ast.copy_location(ast.Constant(API_PORT), node) if node.value == 11434 else node
    module = ast.fix_missing_locations(Port().visit(ast.Module(body=selected, type_ignores=[])))
    return ast.unparse(module) + '\n'


def bundle():
    sources = {name: (ROOT / (name + '.py')).read_text()
               for name in ('processbench_preflight', 'processbench_resources')}
    sources['stream'] = stream_source()
    return {name: {'source': source, 'sha256': sha(source.encode())} for name, source in sources.items()}


def transport_binding(sources, profile='original'):
    options = profile_options(profile)
    profile_hashes = ({name: sha((ROOT / path).read_bytes()) for name, path in SMALL_PROFILE_FILES.items()}
                      if profile == 'small-context-v1' else {})
    return {'profile': profile, 'options': options, 'profile_sha256': profile_hashes,'kind': 'ssh-stdin-memory-only-v1', 'target': TARGET, 'api_port': API_PORT,
            'connector_sha256': sha(Path(__file__).read_bytes()), 'worker_sha256': sha(WORKER.encode()),
            'source_sha256': {name: item['sha256'] for name, item in sources.items()},
            'session_policy_sha256': sha((ROOT / 'PROCESSBENCH_M4_SESSION.md').read_bytes()),
            'session_helper_sha256': sha((ROOT / 'processbench_server_session.py').read_bytes()),
            'http_deadline_seconds': 90, 'worker_deadline_seconds': 95,
            'ssh_subject_deadline_seconds': 100, 'reserve_seconds': REMOTE_RESERVE}


def worker_program(request):
    encoded = base64.b64encode(json.dumps(request, ensure_ascii=False, allow_nan=False).encode()).decode('ascii')
    return (WORKER + '\nmain(json.loads(base64.b64decode(' + repr(encoded) + ')))\n').encode()


def rpc(action, sources, binding, on_line=None, **fields):
    """Exactly one SSH attempt; preserve received raw chunks before any failure."""
    timeout = 915 if action in ('create_preflight', 'verify_preflight') else 100 if action == 'stream_subject' else 30
    request = dict(fields, action=action, bundle=sources, transport=binding)
    process = subprocess.Popen(SSH, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    expired = threading.Event()
    def cancel():
        expired.set()
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    watchdog = threading.Timer(timeout, cancel)
    watchdog.daemon = True
    watchdog.start()
    errors = bytearray()
    def drain_errors():
        while True:
            block = process.stderr.read(4096)
            if not block:
                return
            if len(errors) < 65536:
                errors.extend(block[:65536 - len(errors)])
    reader = threading.Thread(target=drain_errors, daemon=True)
    reader.start()
    result, found = None, False
    try:
        process.stdin.write(worker_program(request))
        process.stdin.close()
        while True:
            line = process.stdout.readline(2 * 1024 * 1024 + 1)
            if not line:
                break
            if len(line) > 2 * 1024 * 1024 or found:
                raise ValueError('Oversized or post-terminal SSH response')
            event = json.loads(line)
            if set(event) == {'line'} and on_line is not None:
                on_line(base64.b64decode(event['line'], validate=True))
            elif set(event) == {'result'}:
                result, found = event['result'], True
            elif 'error' in event:
                raise RuntimeError('Remote operation failed; server state unverified: ' + event['error'])
            else:
                raise ValueError('Unexpected SSH protocol event')
        code = process.wait()
        if expired.is_set():
            raise TimeoutError('SSH deadline reached; remote server cancellation unverified; no retry')
        if code or not found:
            raise RuntimeError('SSH operation incomplete; server state unverified: ' + errors.decode(errors='replace'))
        return result
    finally:
        watchdog.cancel()
        if process.poll() is None:
            cancel()
        process.wait()
        reader.join(timeout=1)
        for stream in (process.stdin, process.stdout, process.stderr):
            if not stream.closed:
                stream.close()


def create_preflight(args):
    import processbench_run as runner
    profile = getattr(args, 'profile', 'original')
    jobs, _ = job_loader(profile)(args.data, args.prompt, args.provenance, args.selection)
    if args.preflight.exists():
        raise ValueError('Preflight report already exists; cannot reset its budget')
    sources = bundle()
    binding = transport_binding(sources, profile)
    started = time.time()
    marker = {'status': 'dispatching', 'transport': binding, 'budget_started_unix': started,
              'jobs_sha256': runner.canonical_hash(jobs), 'generation_requests': 0,
              'runtime_state': 'unverified; interrupted dispatch must not be retried'}
    args.preflight.parent.mkdir(parents=True, exist_ok=True)
    with args.preflight.open('x') as output:
        output.write(json.dumps(marker, indent=2, allow_nan=False) + '\n')
        output.flush()
        os.fsync(output.fileno())
    # Durable exclusive marker precedes any remote action. Failure preserves it.
    report = rpc('create_preflight', sources, binding, jobs=jobs, budget_started_unix=started)
    if (report.get('budget_started_unix') != started or report.get('transport') != binding
            or report.get('jobs_sha256') != marker['jobs_sha256']
            or report.get('status') not in ('passed', 'blocked')):
        raise ValueError('Remote preflight report binding invalid; dispatch remains unresolved')
    runner.atomic_write(args.preflight, json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    if report.get('status') != 'passed':
        raise ValueError('Remote preflight blocked: ' + report.get('reason', 'unknown reason'))
    return report


@contextmanager
def remote_runner(args):
    """Restore every patched interface on exit; original journals/gates unchanged."""
    import processbench_run as runner
    import processbench_preflight as pf
    import processbench_resources as resources
    profile = getattr(args, 'profile', 'original')
    loader = job_loader(profile)
    jobs, _ = loader(args.data, args.prompt, args.provenance, args.selection)
    sources, state = bundle(), {}
    binding = transport_binding(sources, profile)
    original = (runner.current_model, runner.stream_chat, runner.dependencies,
                runner.git_revision, runner.RESERVE_SECONDS, pf.verify_preflight,
                pf.verify_runtime_idle, resources.snapshot, runner.OPTIONS, runner.load_jobs)
    def verify(path, supplied_jobs, model, options):
        if supplied_jobs != jobs or model != runner.MODEL or options != runner.OPTIONS:
            raise ValueError('Controller job/config mismatch')
        report = json.loads(Path(path).read_text())
        if report.get('transport') != binding:
            raise ValueError('Frozen remote transport/source identity changed')
        checked = rpc('verify_preflight', sources, binding, jobs=jobs, report=report)
        if checked != report:
            raise ValueError('Remote verification rewrote immutable report')
        state['report'] = report
        return report
    def identity():
        value = rpc('metadata', sources, binding)
        return {'model_digest': value['model_digest'], 'details': value['model_details'],
                'template_sha256': value['template_sha256'], 'server_version': value['server_version'],
                'transport': binding}
    def streaming(payload, on_line, deadline_seconds=90):
        if deadline_seconds != 90:
            raise ValueError('Fixed subject deadline cannot change')
        matches = [job for job in jobs if job['messages'] == payload.get('messages')]
        if len(matches) != 1:
            raise ValueError('Cannot uniquely bind subject request')
        return rpc('stream_subject', sources, binding, on_line=on_line, jobs=jobs,
                   report=state['report'], payload=payload, job_id=matches[0]['id'])
    def dependencies(p, r):
        return dict(original[2](p, r), remote_connector=binding['connector_sha256'],
                    remote_worker=binding['worker_sha256'], remote_stream=sources['stream']['sha256'],
                    remote_session_policy=binding['session_policy_sha256'],
                    remote_session_helper=binding['session_helper_sha256'], **binding['profile_sha256'])
    def revision():
        value = original[3]()
        paths = ['processbench_remote.py', 'test_processbench_remote.py',
                 'PROCESSBENCH_M4_SESSION.md', 'processbench_server_session.py']
        if profile == 'small-context-v1':
            paths.extend(SMALL_PROFILE_FILES.values())
            paths.append('test_processbench_small_selection.py')
        subprocess.check_call(['git', 'ls-files', '--error-unmatch', *paths], cwd=ROOT,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call(['git', 'diff', '--quiet', 'HEAD', '--', *paths], cwd=ROOT)
        return value
    runner.current_model, runner.stream_chat = identity, streaming
    runner.dependencies, runner.git_revision = dependencies, revision
    runner.RESERVE_SECONDS = REMOTE_RESERVE
    runner.OPTIONS = profile_options(profile)
    runner.load_jobs = loader
    pf.verify_preflight = verify
    pf.verify_runtime_idle = lambda report, model: rpc('runtime_idle', sources, binding, jobs=jobs, report=report)
    resources.snapshot = lambda: rpc('resource_snapshot', sources, binding)
    try:
        yield runner
    finally:
        (runner.current_model, runner.stream_chat, runner.dependencies,
         runner.git_revision, runner.RESERVE_SECONDS, pf.verify_preflight,
         pf.verify_runtime_idle, resources.snapshot, runner.OPTIONS, runner.load_jobs) = original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('create-preflight', 'calibration', 'evaluation'))
    parser.add_argument('--profile', choices=PROFILE_NAMES, default='original')
    for name in ('data', 'prompt', 'provenance', 'selection', 'preflight', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.phase == 'create-preflight':
        report = create_preflight(args)
        print(json.dumps({'status': report['status'], 'jobs': len(report['tokens'])}))
    else:
        with remote_runner(args) as runner:
            runner.run(args)


if __name__ == '__main__':
    main()
