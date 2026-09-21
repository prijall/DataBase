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


if __name__ == '__main__':
    unittest.main()
