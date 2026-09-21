"""Offline checks; never connect to SSH or run models."""
import argparse
import ast
import base64
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import processbench_remote as remote
import processbench_preflight as preflight
import processbench_run as runner


def worker_check(tail):
    result = subprocess.run([sys.executable, '-B', '-'], input=remote.WORKER + '\n' + tail,
                            text=True, capture_output=True, timeout=5)
    if result.returncode:
        raise AssertionError(result.stderr)
    return [json.loads(line) for line in result.stdout.splitlines()]


class WorkerTests(unittest.TestCase):
    def test_python39_and_fixed_ssh(self):
        ast.parse(remote.WORKER, feature_version=(3, 9))
        ast.parse(Path(remote.__file__).read_text(), feature_version=(3, 9))
        self.assertEqual(remote.SSH[-2:], ['prabs@100.74.220.25', '/usr/bin/python3 -B -'])
        for flag in ('BatchMode=yes', 'StrictHostKeyChecking=yes', 'ControlMaster=no', 'ControlPath=none'):
            self.assertIn(flag, remote.SSH)

    def test_bundle_identity_and_ports(self):
        request = {'bundle': remote.bundle()}
        output = worker_check('''
pf, resources = load_bundle(json.loads(%r))
emit({'port': pf.API_PORT, 'code': pf.file_hash(pf.__file__),
      'resources': pf.file_hash(resources.__file__), 'bytecode': sys.dont_write_bytecode})
''' % json.dumps(request))[0]
        self.assertEqual(output['port'], 11435)
        self.assertTrue(output['bytecode'])
        self.assertEqual(output['code'], request['bundle']['processbench_preflight']['sha256'])
        self.assertEqual(output['resources'], request['bundle']['processbench_resources']['sha256'])
        self.assertEqual(preflight.API_PORT, 11434)
        self.assertEqual(preflight.bindings([], preflight.MODEL, preflight.OPTIONS)['api_port'], 11434)

    def test_source_tampering_rejected(self):
        request = {'bundle': remote.bundle()}
        request['bundle']['processbench_resources']['source'] += '\n# changed\n'
        output = worker_check('''
try:
    load_bundle(json.loads(%r))
except ValueError as error:
    emit({'error': str(error)})
''' % json.dumps(request))
        self.assertIn('hash mismatch', output[0]['error'])

    def test_remote_filesystem_mutation_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'forbidden')
            output = worker_check('''
from pathlib import Path
for operation in (lambda: open(%r, 'w'), lambda: Path(%r).mkdir(), lambda: os.system('true')):
    try:
        operation()
    except PermissionError as error:
        emit({'blocked': str(error)})
''' % (path, path))
            self.assertEqual(len(output), 3)
            self.assertFalse(Path(path).exists())

    def test_stream_is_original_watchdog_with_only_port_change(self):
        tree = ast.parse((remote.ROOT / 'processbench_run.py').read_text())
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                 and n.name in ('RequestDeadlineExceeded', 'stream_chat')]
        expected = ast.unparse(ast.Module(body=nodes, type_ignores=[])) + '\n'
        self.assertEqual(remote.stream_source(), expected.replace('11434', '11435'))
        self.assertIn('sock.shutdown(socket.SHUT_RDWR)', remote.stream_source())

    def test_inmemory_blocked_report_no_file(self):
        request = {'bundle': remote.bundle(), 'action': 'create_preflight', 'transport': {},
                   'budget_started_unix': time.time(), 'jobs': []}
        output = worker_check('emit(dispatch(json.loads(%r)))' % json.dumps(request))[0]
        self.assertEqual(output['status'], 'blocked')
        self.assertEqual(output['generation_requests'], 0)
        self.assertEqual(output['budget_started_unix'], request['budget_started_unix'])
        self.assertIn('sixty', output['reason'])

    def test_report_mismatch_and_expiry(self):
        request = {'bundle': remote.bundle(), 'transport': {}, 'jobs': []}
        script = '''
request = json.loads(%r)
pf, _ = load_bundle(request)
request['report'] = dict(pf.bindings([], pf.MODEL, pf.OPTIONS), status='passed',
    transport=request['transport'], budget_started_unix=time.time() - 6000)
for modification in ({}, {'budget_started_unix': time.time(), 'api_port': 11434},
                     {'budget_started_unix': time.time(), 'transport': {'changed': True}}):
    try:
        check_report(pf, dict(request, report=dict(request['report'], **modification)))
    except ValueError as error:
        emit({'error': str(error)})
''' % json.dumps(request)
        self.assertEqual(len(worker_check(script)), 3)


class FakeProcess:
    pid = 1234567
    def __init__(self, events, code=0):
        self.stdin = io.BytesIO()
        self.stdout = io.BytesIO(b''.join(json.dumps(e).encode() + b'\n' for e in events))
        self.stderr = io.BytesIO()
        self.returncode = code
    def wait(self): return self.returncode
    def poll(self): return self.returncode


class ControllerTests(unittest.TestCase):
    def test_stream_raw_data_retained_and_no_retry_on_error(self):
        raw = b'{"done":false,"message":{"content":"partial"}}\n'
        process = FakeProcess([{'line': base64.b64encode(raw).decode()}, {'error': 'deadline'}])
        seen = []
        with patch.object(remote.subprocess, 'Popen', return_value=process) as popen:
            with self.assertRaisesRegex(RuntimeError, 'unverified'):
                remote.rpc('stream_subject', {}, {}, on_line=seen.append)
        self.assertEqual(seen, [raw])
        popen.assert_called_once()

    def test_transport_requires_final_result_and_rejects_extra_data(self):
        for events in ([], [{'result': {}}, {'result': {}}], [{'line': 'aA=='}]):
            with patch.object(remote.subprocess, 'Popen', return_value=FakeProcess(events)):
                with self.assertRaises((RuntimeError, ValueError)):
                    remote.rpc('metadata', {}, {})

    def test_success_and_bound_timeout(self):
        with patch.object(remote.subprocess, 'Popen', return_value=FakeProcess([{'result': {'ok': True}}])):
            with patch.object(remote.threading, 'Timer') as timer:
                self.assertEqual(remote.rpc('metadata', {}, {}), {'ok': True})
                self.assertEqual(timer.call_args.args[0], 30)

    def test_preflight_dispatch_is_durable_and_cannot_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(data=None, prompt=None, provenance=None, selection=None,
                                      preflight=Path(directory) / 'report.json')
            def fail(*a, **k):
                saved = json.loads(args.preflight.read_text())
                self.assertEqual(saved['status'], 'dispatching')
                self.assertEqual(saved['budget_started_unix'], k['budget_started_unix'])
                raise TimeoutError('lost SSH')
            with patch.object(runner, 'load_jobs', return_value=([], {})):
                with patch.object(remote, 'rpc', side_effect=fail) as rpc:
                    with self.assertRaises(TimeoutError):
                        remote.create_preflight(args)
                    first = args.preflight.read_bytes()
                    with self.assertRaisesRegex(ValueError, 'already exists'):
                        remote.create_preflight(args)
                    self.assertEqual(first, args.preflight.read_bytes())
                    rpc.assert_called_once()

    def test_complete_blocked_preflight_replaces_dispatch_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(data=None, prompt=None, provenance=None, selection=None,
                                      preflight=Path(directory) / 'report.json')
            def blocked(action, sources, binding, **fields):
                return dict(status='blocked', reason='memory', transport=binding,
                            jobs_sha256=runner.canonical_hash([]),
                            budget_started_unix=fields['budget_started_unix'])
            with patch.object(runner, 'load_jobs', return_value=([], {})):
                with patch.object(remote, 'rpc', side_effect=blocked):
                    with self.assertRaisesRegex(ValueError, 'memory'):
                        remote.create_preflight(args)
            self.assertEqual(json.loads(args.preflight.read_text())['status'], 'blocked')

    def test_real_local_transport_timeout_preserves_partial_chunk(self):
        # Substitute a local sleepy child for SSH; no remote or model request.
        raw = b'{"done":false}\n'
        event = json.dumps({'line': base64.b64encode(raw).decode()})
        real_popen, real_timer = subprocess.Popen, remote.threading.Timer
        program = 'import sys,time; sys.stdin.buffer.read(); print(%r,flush=True); time.sleep(5)' % event
        def local_process(*args, **kwargs):
            return real_popen([sys.executable, '-B', '-c', program], **kwargs)
        seen = []
        with patch.object(remote.subprocess, 'Popen', side_effect=local_process):
            with patch.object(remote.threading, 'Timer', side_effect=lambda seconds, callback: real_timer(.2, callback)):
                with self.assertRaisesRegex(TimeoutError, 'cancellation unverified'):
                    remote.rpc('stream_subject', {}, {}, on_line=seen.append)
        self.assertEqual(seen, [raw])

    def test_wrapper_restores_runner_even_after_error(self):
        import processbench_resources as resources
        before = (runner.stream_chat, runner.current_model, runner.RESERVE_SECONDS,
                  preflight.verify_preflight, resources.snapshot)
        args = argparse.Namespace(data=None, prompt=None, provenance=None, selection=None)
        with patch.object(runner, 'load_jobs', return_value=([], {})):
            with self.assertRaisesRegex(RuntimeError, 'test'):
                with remote.remote_runner(args):
                    self.assertEqual(runner.RESERVE_SECONDS, 150)
                    raise RuntimeError('test')
        self.assertEqual(before, (runner.stream_chat, runner.current_model, runner.RESERVE_SECONDS,
                                 preflight.verify_preflight, resources.snapshot))


class ProfileTests(unittest.TestCase):
    @unittest.skipUnless((remote.ROOT / 'runs/processbench-source/gsm8k.json').exists(),
                         'Pinned optional offline source cache unavailable')
    def test_real_selection_profile_integration_and_cross_selection_rejection(self):
        args = argparse.Namespace(profile='small-context-v1',
            data=remote.ROOT / 'runs/processbench-source/gsm8k.json',
            prompt=remote.ROOT / 'runs/processbench-source/critique_template.txt',
            provenance=remote.ROOT / 'processbench/provenance.json',
            selection=remote.ROOT / 'processbench/selection-small-context.json')
        loader = remote.job_loader(args.profile)
        jobs, hashes = loader(args.data, args.prompt, args.provenance, args.selection)
        self.assertEqual(len(jobs), 60)
        self.assertEqual(sum(j['split'] == 'calibration' for j in jobs), 20)
        with self.assertRaises(ValueError):
            runner.load_jobs(args.data, args.prompt, args.provenance, args.selection)
        with self.assertRaises(ValueError):
            loader(args.data, args.prompt, args.provenance, remote.ROOT / 'processbench/selection.json')
        old_options, old_loader = runner.OPTIONS, runner.load_jobs
        with remote.remote_runner(args):
            self.assertEqual(runner.OPTIONS['num_ctx'], 2048)
            self.assertEqual(preflight.OPTIONS['num_ctx'], 8192)
            self.assertEqual(runner.load_jobs(args.data, args.prompt, args.provenance, args.selection), (jobs, hashes))
            binding = remote.transport_binding(remote.bundle(), args.profile)
            for name, filename in remote.SMALL_PROFILE_FILES.items():
                self.assertEqual(binding['profile_sha256'][name], remote.sha((remote.ROOT / filename).read_bytes()))
        self.assertIs(runner.OPTIONS, old_options)
        self.assertIs(runner.load_jobs, old_loader)

    def test_only_fixed_profiles_with_unchanged_output_and_defaults(self):
        original = remote.profile_options('original')
        small = remote.profile_options('small-context-v1')
        self.assertEqual(original, runner.OPTIONS)
        self.assertEqual(small, dict(original, num_ctx=2048))
        self.assertEqual(small['num_predict'], 1024)
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            remote.profile_options('arbitrary')

    def test_worker_propagates_profile_and_requires_exact_resident_context(self):
        request = {'bundle': remote.bundle(), 'transport': {'profile': 'small-context-v1',
                   'options': remote.profile_options('small-context-v1')}}
        script = """
pf, _ = load_bundle(json.loads(%r))
emit({'options': pf.OPTIONS, 'bindings': pf.bindings([], pf.MODEL, pf.OPTIONS)['options']})
for context in (2048, 8192, 1024):
    pf.request_json = lambda *a, **k: {'models': [{'name': pf.MODEL, 'digest': pf.MODEL_DIGEST,
                                                'context_length': context}]}
    try:
        pf.loaded_state(require_loaded=True)
        emit({'accepted_context': context})
    except ValueError as error:
        emit({'rejected_context': context})
""" % json.dumps(request)
        output = worker_check(script)
        self.assertEqual(output[0]['options'], remote.profile_options('small-context-v1'))
        self.assertEqual(output[0]['bindings'], output[0]['options'])
        self.assertEqual(output[1:], [{'accepted_context': 2048}, {'rejected_context': 8192},
                                    {'rejected_context': 1024}])

    def test_worker_rejects_unknown_profile_and_arbitrary_options(self):
        for profile, options in [('unknown', remote.profile_options('original')),
                                  ('small-context-v1', remote.profile_options('original')),
                                  ('small-context-v1', dict(remote.profile_options('small-context-v1'), num_predict=256))]:
            request = {'bundle': remote.bundle(), 'transport': {'profile': profile, 'options': options}}
            output = worker_check("""
try:
    load_bundle(json.loads(%r))
except ValueError as error:
    emit({'error': str(error)})
""" % json.dumps(request))
            self.assertEqual(len(output), 1)
            self.assertIn('profile', output[0]['error'])

    def test_worker_subject_rejects_original_options_without_http(self):
        request = {'bundle': remote.bundle(), 'action': 'stream_subject', 'jobs': [],
                   'transport': {'profile': 'small-context-v1', 'options': remote.profile_options('small-context-v1')},
                   'payload': {'model': preflight.MODEL, 'messages': [], 'stream': True,
                               'truncate': False, 'shift': False, 'options': remote.profile_options('original'),
                               'keep_alive': '30s'}}
        output = worker_check("""
request = json.loads(%r)
pf, resources = load_bundle(request)
request['report'] = dict(pf.bindings([], pf.MODEL, pf.OPTIONS), status='passed',
    transport=request['transport'], budget_started_unix=time.time())
try:
    dispatch(request)
except ValueError as error:
    emit({'error': str(error)})
""" % json.dumps(request))
        self.assertEqual(output, [{'error': 'Subject configuration differs from frozen settings'}])

    def test_worker_rejects_changed_job_selection(self):
        request = {'bundle': remote.bundle(), 'jobs': [],
                   'transport': {'profile': 'small-context-v1', 'options': remote.profile_options('small-context-v1')}}
        output = worker_check("""
request = json.loads(%r)
pf, resources = load_bundle(request)
request['report'] = dict(pf.bindings([], pf.MODEL, pf.OPTIONS), status='passed',
    transport=request['transport'], budget_started_unix=time.time())
request['jobs'] = [{'id': 'other-selection'}]
try:
    check_report(pf, request)
except ValueError as error:
    emit({'error': str(error)})
""" % json.dumps(request))
        self.assertIn('jobs_sha256', output[0]['error'])

    def test_controller_profile_and_loader_restored(self):
        import processbench_resources as resources
        original_options, original_loader = runner.OPTIONS, runner.load_jobs
        original_pf_options = preflight.OPTIONS.copy()
        args = argparse.Namespace(profile='small-context-v1', data=None, prompt=None,
                                  provenance=None, selection=None)
        loader = lambda *a: ([], {})
        with patch.object(remote, 'job_loader', return_value=loader):
            with patch.object(remote, 'SMALL_PROFILE_FILES', {}):
                with remote.remote_runner(args):
                    self.assertEqual(runner.OPTIONS['num_ctx'], 2048)
                    self.assertIs(runner.load_jobs, loader)
                    self.assertEqual(preflight.OPTIONS, original_pf_options)
        self.assertIs(runner.OPTIONS, original_options)
        self.assertIs(runner.load_jobs, original_loader)

    def test_cross_profile_report_rejected_before_rpc(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'preflight.json'
            report.write_text(json.dumps({'status': 'passed', 'transport': {'profile': 'original'}}))
            args = argparse.Namespace(profile='small-context-v1', data=None, prompt=None,
                                      provenance=None, selection=None)
            with patch.object(remote, 'job_loader', return_value=lambda *a: ([], {})):
                with patch.object(remote, 'SMALL_PROFILE_FILES', {}):
                    with remote.remote_runner(args):
                        with patch.object(remote, 'rpc') as rpc:
                            with self.assertRaisesRegex(ValueError, 'identity changed'):
                                preflight.verify_preflight(report, [], runner.MODEL, runner.OPTIONS)
                            rpc.assert_not_called()

    def test_small_preflight_uses_small_loader_and_binds_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(profile='small-context-v1', data=None, prompt=None,
                                      provenance=None, selection=None, preflight=Path(directory) / 'report.json')
            def blocked(action, sources, binding, **fields):
                self.assertEqual(binding['profile'], 'small-context-v1')
                self.assertEqual(binding['options']['num_ctx'], 2048)
                return dict(status='blocked', reason='test', transport=binding,
                            jobs_sha256=runner.canonical_hash([]), budget_started_unix=fields['budget_started_unix'])
            with patch.object(remote, 'job_loader', return_value=lambda *a: ([], {})) as loader:
                with patch.object(remote, 'SMALL_PROFILE_FILES', {}):
                    with patch.object(remote, 'rpc', side_effect=blocked):
                        with self.assertRaisesRegex(ValueError, 'test'):
                            remote.create_preflight(args)
                loader.assert_called_once_with('small-context-v1')
            self.assertEqual(json.loads(args.preflight.read_text())['transport']['profile'], 'small-context-v1')


if __name__ == '__main__':
    unittest.main()
