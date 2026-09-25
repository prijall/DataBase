"""Offline diagnostic checks; all subject/SSH operations are mocked."""
import argparse
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import runtime_cache_probe as probe
import processbench_remote as remote
from test_processbench_remote import worker_check


class DiagnosticTests(unittest.TestCase):
    def args(self, directory):
        return argparse.Namespace(out=Path(directory), service_log=Path(directory) / 'service.log')

    def report(self, started=None):
        return {'status': 'passed', 'transport': {'profile': probe.PROFILE}, 'purpose': probe.PROFILE,
                'benchmark_admission': False, 'jobs_sha256': probe.records.canonical_hash(probe.jobs()),
                'budget_started_unix': time.time() if started is None else started,
                'resource_baseline': {'pressure_level': 1, 'free_percent': 50,
                                     'swap_used_bytes': 0, 'swapouts_bytes': 0},
                'tokens': {job['id']: {'prompt_tokens': 30} for job in probe.jobs()},
                **{key: 'pinned' for key in ('model_digest', 'server_version', 'template_sha256',
                     'parameters_sha256', 'model_path', 'binary_sha256', 'library_sha256')}}

    def fixtures(self, args, report):
        (args.out / 'preflight.json').write_text(json.dumps(report))
        (args.out / 'preparation.json').write_text(json.dumps({'service_evidence': {'owned_pid': 123}}))

    def simulated_rpc(self, report, fail_after=None, interrupted=False, parent=123):
        count = [0]
        def call(action, sources, binding, on_line=None, **fields):
            if action == 'verify_preflight':
                return report
            if action == 'resource_snapshot':
                value = dict(report['resource_baseline'])
                if fail_after is not None and count[0] >= fail_after:
                    value['pressure_level'] = 2
                return value
            if action == 'metadata':
                return {key: report[key] for key in ('model_digest', 'server_version', 'template_sha256',
                     'parameters_sha256', 'model_path', 'binary_sha256', 'library_sha256')}
            if action == 'runtime_idle':
                return {'runner': {'parent_pid': parent}}
            if action == 'stream_subject':
                count[0] += 1
                self.assertTrue((self.active_args.out / 'journal.jsonl').exists())
                self.assertIn('attempt_started', (self.active_args.out / 'journal.jsonl').read_text())
                self.assertEqual(fields['payload']['options']['num_predict'], 1)
                if interrupted:
                    raise KeyboardInterrupt()
                on_line(json.dumps({'model': probe.records.MODEL, 'message': {'content': 'x'},
                                    'done': True, 'done_reason': 'length', 'eval_count': 1,
                                    'prompt_eval_count': 30}).encode() + b'\n')
                return {'completed_transport': True}
            raise AssertionError(action)
        return call, count

    def invoke(self, args, report, fake):
        self.active_args = args
        with patch.object(probe, 'freeze', return_value='frozen'), \
                patch.object(probe, 'bindings', return_value=({}, report['transport'])), \
                patch.object(probe, 'inspect_service_log', return_value={'owned_pid': 123}), \
                patch.object(remote, 'rpc', side_effect=fake):
            return probe.run(args)

    def test_fixed_nonbenchmark_jobs_and_profile(self):
        jobs = probe.jobs()
        self.assertEqual(len(jobs), 4)
        self.assertEqual(len({job['id'] for job in jobs}), 4)
        self.assertTrue(all(set(job) == {'id', 'messages', 'messages_sha256'} for job in jobs))
        self.assertEqual(remote.profile_options(probe.PROFILE),
                         {'temperature': 0, 'seed': 42, 'num_ctx': 2048, 'num_predict': 1, 'num_thread': 2})
        self.assertNotIn(probe.PROFILE, remote.PROFILE_NAMES)
        with self.assertRaises(ValueError):
            remote.job_loader(probe.PROFILE)

    def test_worker_diagnostic_validation_is_non_admitting(self):
        request = {'bundle': remote.bundle(), 'jobs': probe.jobs(),
                   'transport': {'profile': probe.PROFILE, 'options': remote.profile_options(probe.PROFILE)}}
        output = worker_check('''
request = json.loads(%r)
pf, resources = load_bundle(request)
pf.validate_jobs(request['jobs'])
emit(pf.bindings(request['jobs'], pf.MODEL, pf.OPTIONS))
try:
    pf.validate_jobs([dict(request['jobs'][0], gold_label=0)])
except ValueError as error:
    emit({'error': str(error)})
''' % json.dumps(request))
        self.assertIs(output[0]['benchmark_admission'], False)
        self.assertEqual(output[0]['options']['num_predict'], 1)
        self.assertEqual(output[0]['schema'], 'runtime-cache-diagnostic-preflight-v1')
        self.assertIn('four fixed synthetic', output[1]['error'])

    def test_exactly_four_calls_and_no_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            args, report = self.args(directory), self.report()
            self.fixtures(args, report)
            fake, count = self.simulated_rpc(report)
            result = self.invoke(args, report, fake)
            self.assertEqual(count[0], 4)
            self.assertEqual((result['attempted'], result['recorded'], result['unattempted']), (4, 4, 0))
            self.assertTrue(result['no_accuracy_score'])
            self.assertIs(result['benchmark_admission'], False)
            with self.assertRaises(FileExistsError):
                self.invoke(args, report, fake)
            self.assertEqual(count[0], 4)

    def test_resource_stop_no_extra_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            args, report = self.args(directory), self.report()
            self.fixtures(args, report)
            fake, count = self.simulated_rpc(report, fail_after=1)
            result = self.invoke(args, report, fake)
            self.assertEqual(count[0], 1)
            self.assertEqual(result['unattempted'], 3)
            self.assertIn('Resource stop', result['status'])

    def test_interrupted_attempt_is_ambiguous_not_unattempted(self):
        with tempfile.TemporaryDirectory() as directory:
            args, report = self.args(directory), self.report()
            self.fixtures(args, report)
            fake, count = self.simulated_rpc(report, interrupted=True)
            with self.assertRaises(KeyboardInterrupt):
                self.invoke(args, report, fake)
            summary = json.loads((args.out / 'SUMMARY.json').read_text())
            self.assertEqual((summary['attempted'], summary['recorded'], summary['ambiguous_attempts'],
                              summary['unattempted']), (1, 0, 1, 3))
            with self.assertRaises(FileExistsError):
                self.invoke(args, report, fake)
            self.assertEqual(count[0], 1)

    def test_unowned_backend_refused_before_subject(self):
        with tempfile.TemporaryDirectory() as directory:
            args, report = self.args(directory), self.report()
            self.fixtures(args, report)
            fake, count = self.simulated_rpc(report, parent=999)
            with self.assertRaisesRegex(ValueError, 'does not belong'):
                self.invoke(args, report, fake)
            self.assertEqual(count[0], 0)

    def test_expired_service_budget_does_not_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            args, report = self.args(directory), self.report(time.time() - 451)
            self.fixtures(args, report)
            fake, count = self.simulated_rpc(report)
            with self.assertRaisesRegex(ValueError, 'budget unavailable'):
                self.invoke(args, report, fake)
            self.assertEqual(count[0], 0)

    def test_prepare_marker_survives_transport_loss_and_uses_service_start(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.args(directory)
            started = time.time() - 20
            with patch.object(probe, 'freeze', return_value='frozen'), \
                    patch.object(probe, 'bindings', return_value=({}, {'profile': probe.PROFILE})), \
                    patch.object(probe, 'inspect_service_log', return_value={'budget_started_unix': started}), \
                    patch.object(remote, 'rpc', side_effect=TimeoutError('lost')) as rpc:
                with self.assertRaises(TimeoutError):
                    probe.prepare(args)
                marker = json.loads((args.out / 'preflight.json').read_text())
                self.assertEqual(marker['budget_started_unix'], started)
                self.assertEqual(marker['status'], 'dispatching')
                with self.assertRaises(FileExistsError):
                    probe.prepare(args)
                rpc.assert_called_once()

    def test_service_log_requires_cache_uptake_and_owned_diagnostic_lifetime(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'service.log'
            started = time.time()
            header = {'event': 'local_start', 'cache_ram_mib': 0, 'budget_started_unix': started,
                      'remote_code_sha256': remote.sha(probe.service.remote_code(0).encode()),
                      'launcher_file_sha256': remote.sha(Path(probe.service.__file__).read_bytes())}
            environment = {'event': 'service_environment', 'cache_ram_override': 0,
                           'allowlisted_environment': {'LLAMA_ARG_CACHE_RAM': '0'}}
            spawn = {'event': 'spawned', 'pid': 123, 'pgid': 123, 'watchdog_seconds': 600,
                     'budget_started_unix': started}
            text = json.dumps(header) + '\nSESSION ' + json.dumps(environment) + '\nSESSION ' + json.dumps(spawn) + '\n'
            path.write_text(text)
            with self.assertRaisesRegex(ValueError, 'not verified'):
                probe.inspect_service_log(path, True)
            path.write_text(text + 'prompt cache is disabled - use `--cache-ram N` to enable it\n')
            self.assertEqual(probe.inspect_service_log(path, True)['owned_pid'], 123)
            path.write_text(path.read_text() + 'SESSION {"event":"cleanup"}\n')
            with self.assertRaises(ValueError):
                probe.inspect_service_log(path, True)


if __name__ == '__main__':
    unittest.main()
