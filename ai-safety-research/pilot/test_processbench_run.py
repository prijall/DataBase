"""No-inference tests for durable attempts, absolute deadlines, and raw-derived gates."""

import argparse
from contextlib import ExitStack
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import processbench_prepare as preparation
import processbench_run as runner


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.jobs = []
        for split, count in (('calibration', 20), ('evaluation', 40)):
            for index in range(count):
                key = f'{split}-{index:02}'
                messages = [{'role': 'user', 'content': key}]
                self.jobs.append({'id': key, 'split': split, 'gold_label': -1 if index % 2 == 0 else 1,
                                  'step_count': 3, 'messages': messages,
                                  'messages_sha256': runner.canonical_hash(messages),
                                  'problem_group_sha256': key})
        self.by_text = {job['messages'][0]['content']: job for job in self.jobs}
        self.calls = []
        self.identity = {'model_digest': runner.MODEL_DIGEST, 'server_version': '0.34.0',
                         'template_sha256': 'template-hash', 'details': {}}
        self.report = dict(self.identity, budget_started_unix=time.time(), resource_baseline={'test': 'baseline'},
                           tokens={job['id']: {'prompt_tokens': 123, 'messages_sha256': job['messages_sha256']}
                                   for job in self.jobs})
        self.preflight = SimpleNamespace(__file__=__file__, verify_preflight=Mock(return_value=self.report),
                                         verify_runtime_idle=Mock(return_value={'runner': 'idle'}))
        self.resources = SimpleNamespace(__file__=__file__, snapshot=Mock(return_value={'test': 'sample'}),
                                         violations=Mock(return_value=[]))

    def args(self, base, phase='calibration'):
        base = Path(base)
        preflight = base / 'preflight.json'
        if not preflight.exists():
            preflight.write_text('{"immutable": true}\n')
        return argparse.Namespace(phase=phase, data=base / 'data.json', prompt=base / 'prompt.txt',
                                  provenance=base / 'provenance.json', selection=base / 'selection.json',
                                  preflight=preflight, out=base / 'run')

    @contextlib.contextmanager
    def environment(self, transport=None):
        modules = {'processbench_preflight': self.preflight, 'processbench_resources': self.resources}
        with ExitStack() as stack:
            stack.enter_context(patch.object(runner, 'load_jobs', return_value=(self.jobs, {'data': 'fixed'})))
            stack.enter_context(patch.object(runner.importlib, 'import_module', side_effect=lambda name: modules[name]))
            stack.enter_context(patch.object(runner, 'current_model', return_value=self.identity))
            stack.enter_context(patch.object(runner, 'git_revision', return_value='frozen-test-commit'))
            stack.enter_context(patch.object(runner, 'dependencies', return_value={'runner': 'fixed-test-hash'}))
            stack.enter_context(patch.object(runner, 'stream_chat', side_effect=transport or self.correct_transport))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            yield

    def chunks(self, payload, on_line, prediction=None, reason='stop', count=123):
        self.assertEqual(payload['model'], runner.MODEL)
        self.assertEqual(payload['options'], runner.OPTIONS)
        self.assertTrue(payload['stream'])
        self.assertFalse(payload['truncate'])
        self.assertFalse(payload['shift'])
        self.assertEqual(payload['keep_alive'], '30s')
        self.assertNotIn('format', payload)
        job = self.by_text[payload['messages'][0]['content']]
        self.calls.append(job['id'])
        label = job['gold_label'] if prediction is None else prediction
        on_line((json.dumps({'model': runner.MODEL, 'message': {'content': f'Work. \\boxed{{{label}}}'},
                             'done': False}) + '\n').encode())
        on_line((json.dumps({'model': runner.MODEL, 'message': {'content': ''}, 'done': True,
                             'done_reason': reason, 'prompt_eval_count': count, 'eval_count': 9}) + '\n').encode())

    def correct_transport(self, payload, on_line):
        self.chunks(payload, on_line)

    def test_calibration_then_evaluation_are_fixed_single_attempts(self):
        with tempfile.TemporaryDirectory() as directory, self.environment():
            args = self.args(directory)
            result = runner.run(args)
            self.assertTrue(result['calibration']['calibration_gate_passed'])
            self.assertEqual(len(self.calls), 20)
            self.assertEqual(result['evaluation']['recorded'], 0)
            runner.run(args)
            self.assertEqual(len(self.calls), 20)
            args.phase = 'evaluation'
            result = runner.run(args)
            self.assertEqual(result['evaluation']['recorded'], 40)
            self.assertEqual(len(self.calls), 60)
            self.assertEqual(len(set(self.calls)), 60)
            _, attempts, responses = runner.read_history(args.out, self.jobs)
            self.assertEqual(len(attempts), 60)
            self.assertEqual(len(responses), 60)
            runner.run(args)
            self.assertEqual(len(self.calls), 60)
            # No upstream input text is copied into persisted metadata or raw outputs.
            manifest = json.loads((args.out / 'manifest.json').read_text())
            self.assertTrue(all('messages' not in job for job in manifest['protocol']['jobs']))
            self.assertTrue(all('messages' not in row['job'] for row in responses.values()))

    def test_evaluation_refused_before_calibration_and_after_failed_gate(self):
        with tempfile.TemporaryDirectory() as directory, self.environment():
            with self.assertRaisesRegex(ValueError, 'calibration gate'):
                runner.run(self.args(directory, 'evaluation'))
            self.assertEqual(self.calls, [])
        def wrong_valid(payload, on_line):
            self.chunks(payload, on_line, prediction=1)
        with tempfile.TemporaryDirectory() as directory, self.environment(wrong_valid):
            args = self.args(directory)
            report = runner.run(args)
            self.assertEqual(len(self.calls), 20)
            self.assertFalse(report['calibration']['calibration_gate_passed'])
            args.phase = 'evaluation'
            with self.assertRaisesRegex(ValueError, 'calibration gate'):
                runner.run(args)
            self.assertEqual(len(self.calls), 20)

    def test_truncated_boxed_answers_keep_official_score_but_fail_local_gate(self):
        def length_stopped(payload, on_line):
            self.chunks(payload, on_line, reason='length')
        with tempfile.TemporaryDirectory() as directory, self.environment(length_stopped):
            result = runner.run(self.args(directory))['calibration']
            self.assertEqual(result['official_exact_matches'], 20)
            self.assertEqual(result['local_exact_matches'], 0)
            self.assertEqual(result['usable'], 0)
            self.assertEqual(result['length_stops'], 20)
            self.assertIsNone(result['classes']['valid']['conditional_local_accuracy'])
            self.assertFalse(result['calibration_gate_passed'])

    def test_timeout_retains_partial_stream_and_blocks_automatic_resume(self):
        def timeout(payload, on_line):
            self.calls.append('attempt')
            job = self.by_text[payload['messages'][0]['content']]
            on_line((json.dumps({'message': {'content': f'\\boxed{{{job["gold_label"]}}}'}, 'done': False}) + '\n').encode())
            raise runner.RequestDeadlineExceeded('synthetic deadline')
        with tempfile.TemporaryDirectory() as directory, self.environment(timeout):
            args = self.args(directory)
            result = runner.run(args)['calibration']
            self.assertEqual(result['recorded'], 1)
            self.assertEqual(result['request_errors'], 1)
            self.assertEqual(result['local_exact_matches'], 0)
            row = runner.read_lines(args.out / 'responses.jsonl')[0]
            self.assertTrue(row['score']['official_match'])
            self.assertEqual(row['request_error']['type'], 'RequestDeadlineExceeded')
            self.assertTrue((args.out / row['stream_path']).read_bytes())
            with self.assertRaisesRegex(ValueError, 'cancellation/state review'):
                runner.run(args)
            self.assertEqual(len(self.calls), 1)

    def test_durable_journal_precedes_call_and_ambiguous_interruption_blocks_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.args(directory)
            def interrupted(payload, on_line):
                events = runner.read_lines(args.out / 'journal.jsonl')
                self.assertEqual(events[-1]['kind'], 'attempt_started')
                self.calls.append('started')
                raise KeyboardInterrupt('simulate process interruption')
            with self.environment(interrupted):
                with self.assertRaises(KeyboardInterrupt):
                    runner.run(args)
                self.assertIn('Execution stopped: KeyboardInterrupt', (args.out / 'SUMMARY.md').read_text())
                with self.assertRaisesRegex(ValueError, 'Ambiguous interrupted attempt'):
                    runner.run(args)
            self.assertEqual(self.calls, ['started'])

    def test_raw_derived_score_tampering_prevents_evaluation(self):
        with tempfile.TemporaryDirectory() as directory, self.environment():
            args = self.args(directory)
            runner.run(args)
            path = args.out / 'responses.jsonl'
            rows = runner.read_lines(path)
            rows[0]['score']['local_match'] = False
            path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
            args.phase = 'evaluation'
            with self.assertRaisesRegex(ValueError, 'Saved score differs'):
                runner.run(args)
            self.assertEqual(len(self.calls), 20)

    def test_prompt_count_mismatch_stops_after_one_recorded_call(self):
        def mismatched_count(payload, on_line):
            self.chunks(payload, on_line, count=122)
        with tempfile.TemporaryDirectory() as directory, self.environment(mismatched_count):
            args = self.args(directory)
            result = runner.run(args)['calibration']
            self.assertEqual(result['recorded'], 1)
            self.assertEqual(result['usable'], 0)
            row = runner.read_lines(args.out / 'responses.jsonl')[0]
            self.assertEqual(row['request_error']['type'], 'PromptTokenMismatch')
            self.assertEqual(row['observed_prompt_tokens'], 122)
            self.assertEqual(row['expected_prompt_tokens'], 123)
            with self.assertRaisesRegex(ValueError, 'cancellation/state review'):
                runner.run(args)

    def test_changed_preflight_cannot_reset_persisted_budget(self):
        with tempfile.TemporaryDirectory() as directory, self.environment():
            args = self.args(directory)
            runner.run(args)
            args.preflight.write_text('{"immutable": false}\n')
            with self.assertRaisesRegex(ValueError, 'Resume refused'):
                runner.run(args)
            self.assertEqual(len(self.calls), 20)

    def test_pauses_and_resource_capture_count_against_global_budget(self):
        self.report['budget_started_unix'] = time.time() - runner.BUDGET_SECONDS + 10
        with tempfile.TemporaryDirectory() as directory, self.environment():
            args = self.args(directory)
            result = runner.run(args)['calibration']
            self.assertEqual(result['recorded'], 0)
            self.assertEqual(self.calls, [])
            self.assertIn('Budget reserve', (args.out / 'SUMMARY.md').read_text())
        clock = {'now': 1000.0}
        self.report['budget_started_unix'] = 1000 - runner.BUDGET_SECONDS + 140
        def slow_snapshot():
            clock['now'] += 20
            return {'test': 'sample'}
        self.resources.snapshot.side_effect = slow_snapshot
        with tempfile.TemporaryDirectory() as directory, self.environment(), patch.object(runner.time, 'time', side_effect=lambda: clock['now']), patch.object(runner.time, 'monotonic', side_effect=lambda: clock['now']):
            result = runner.run(self.args(directory))['calibration']
            self.assertEqual(result['recorded'], 0)
            self.assertEqual(self.calls, [])

    def test_resource_and_workload_stops_do_not_attempt_subject(self):
        self.resources.violations.return_value = ['memory pressure']
        with tempfile.TemporaryDirectory() as directory, self.environment():
            result = runner.run(self.args(directory))['calibration']
            self.assertEqual(result['recorded'], 0)
            self.assertEqual(self.calls, [])
        self.resources.violations.return_value = []
        self.preflight.verify_runtime_idle.side_effect = ValueError('Another workload is active')
        with tempfile.TemporaryDirectory() as directory, self.environment():
            args = self.args(directory)
            with self.assertRaisesRegex(ValueError, 'Another workload'):
                runner.run(args)
            events = runner.read_lines(args.out / 'journal.jsonl')
            self.assertFalse(any(event['kind'] == 'attempt_started' for event in events))
            self.assertEqual(self.calls, [])

    def test_preflight_failure_is_logged_as_blocked_without_subject_call(self):
        self.preflight.verify_preflight.side_effect = ValueError('Unverified tokens')
        with tempfile.TemporaryDirectory() as directory, self.environment():
            args = self.args(directory)
            with self.assertRaisesRegex(ValueError, 'Unverified tokens'):
                runner.run(args)
            events = runner.read_lines(args.out / 'journal.jsonl')
            self.assertEqual(events[-1]['kind'], 'preflight_blocked')
            self.assertTrue((args.out / 'SUMMARY.md').exists())
            self.assertEqual(self.calls, [])

    def test_decode_rejects_wrong_model_and_data_after_final_event(self):
        wrong = (json.dumps({'model': 'other-model', 'message': {'content': '\\boxed{-1}'}, 'done': True}) + '\n').encode()
        self.assertIn('unexpected model', runner.decode_stream(wrong)['stream_error'])
        final = (json.dumps({'model': runner.MODEL, 'message': {'content': '\\boxed{-1}'}, 'done': True,
                             'done_reason': 'stop', 'prompt_eval_count': 123}) + '\n').encode()
        self.assertIn('after terminal', runner.decode_stream(final + b'{}\n')['stream_error'])

    def test_absolute_watchdog_interrupts_readline_without_waiting_for_newline(self):
        closed = threading.Event()
        shutdown_called = threading.Event()
        class FakeSocket:
            def settimeout(self, seconds):
                pass
            def shutdown(self, how):
                shutdown_called.set()
                closed.set()
            def close(self):
                closed.set()
        class DripResponse:
            status = 200
            def readline(self, limit):
                # Simulates a peer keeping a read active forever without a newline.
                if closed.wait(2):
                    raise OSError('socket shutdown interrupted read')
                raise AssertionError('Absolute watchdog did not interrupt the read')
        class FakeConnection:
            def __init__(self, host, port, timeout):
                assert (host, port) == ('127.0.0.1', 11434)
                self.sock = FakeSocket()
            def connect(self):
                pass
            def request(self, method, path, body, headers):
                assert (method, path) == ('POST', '/api/chat')
                assert self.auto_open == 0
            def getresponse(self):
                return DripResponse()
            def close(self):
                self.sock.close()
        started = time.monotonic()
        with patch.object(runner.http.client, 'HTTPConnection', FakeConnection):
            with self.assertRaises(runner.RequestDeadlineExceeded):
                runner.stream_chat({}, lambda line: False, deadline_seconds=.05)
        self.assertTrue(shutdown_called.is_set())
        self.assertLess(time.monotonic() - started, 1)

    def test_offline_input_loader_rejects_changed_selection(self):
        examples = [{'id': f'fixture-{i}', 'generator': 'unit-test', 'problem': f'Problem {i}',
                     'steps': ['Step one', 'Step two'], 'final_answer_correct': i % 2 == 0,
                     'label': -1 if i % 2 == 0 else 1} for i in range(80)]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data, prompt, provenance = base / 'data.json', base / 'prompt.txt', base / 'provenance.json'
            data.write_text(json.dumps(examples))
            prompt.write_text('{problem}\n{tagged_response}\nReturn \\boxed{{}}')
            metadata = {'repository_revision': preparation.REPOSITORY_REVISION,
                        'dataset_revision': preparation.DATASET_REVISION,
                        'files': {'data': {'sha256': preparation.sha256(data.read_bytes())},
                                  'prompt': {'sha256': preparation.sha256(prompt.read_bytes())}}}
            provenance.write_text(json.dumps(metadata))
            selection = preparation.prepare(data, prompt, provenance, base / 'prepared')
            path = base / 'prepared' / 'selection.json'
            jobs, hashes = runner.load_jobs(data, prompt, provenance, path)
            self.assertEqual(len(jobs), 60)
            self.assertIn('selection', hashes)
            selection['splits']['evaluation']['records'][0]['gold_label'] = 99
            path.write_text(json.dumps(selection))
            with self.assertRaisesRegex(ValueError, 'Selection differs'):
                runner.load_jobs(data, prompt, provenance, path)


if __name__ == '__main__':
    unittest.main()
