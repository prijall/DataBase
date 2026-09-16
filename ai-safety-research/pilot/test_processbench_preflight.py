"""Mocked safety, binding and report tests. No model calls or network access."""

import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import processbench_preflight as preflight


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.jobs = []
        for index in range(60):
            messages = [{'role': 'user', 'content': f'Fixture problem {index}'}]
            self.jobs.append({'id': str(index), 'split': 'calibration' if index < 20 else 'evaluation',
                              'gold_label': -1, 'step_count': 3, 'messages': messages,
                              'messages_sha256': preflight.digest(messages)})
        self.baseline = {'captured_unix': time.time(), 'pressure_level': 1, 'free_percent': 80,
                         'swap_used_bytes': 0, 'swapouts_bytes': 0}
        self.identity = {'model_digest': preflight.MODEL_DIGEST, 'server_version': preflight.VERSION,
                         'template_sha256': preflight.TEMPLATE_SHA256, 'model_path': '/fixture/model',
                         'parameters_sha256': preflight.PARAMETERS_SHA256,
                         'binary_sha256': preflight.BINARY_SHA256, 'library_sha256': preflight.LIBRARY_SHA256}

    def test_forbids_generation_and_misspelled_debug_option(self):
        with patch.object(preflight.urllib.request, 'build_opener') as network:
            for port, endpoint, payload in [(11434, '/api/chat', {'debug_render_only': True}),
                                            (11434, '/api/generate', {}), (12345, '/completion', {})]:
                with self.assertRaises(ValueError):
                    preflight.request_json(port, endpoint, payload)
            network.assert_not_called()

    def test_job_hash_role_and_coverage_guards(self):
        preflight.validate_jobs(self.jobs)
        for change in ('hash', 'role', 'duplicate', 'missing'):
            jobs = copy.deepcopy(self.jobs)
            if change == 'hash':
                jobs[0]['messages'][0]['content'] += 'changed'
            elif change == 'role':
                jobs[0]['messages'][0]['role'] = 'system'
                jobs[0]['messages_sha256'] = preflight.digest(jobs[0]['messages'])
            elif change == 'duplicate':
                jobs[-1]['id'] = jobs[0]['id']
            else:
                jobs.pop()
            with self.assertRaises(ValueError):
                preflight.validate_jobs(jobs)

    def test_pins_template_before_debug_request(self):
        responses = [{'version': preflight.VERSION},
                     {'models': [{'name': preflight.MODEL, 'digest': preflight.MODEL_DIGEST}]},
                     {'template': preflight.SYSTEM_PREFIX + '\nAdded instruction'}]
        with patch.object(preflight, 'request_json', side_effect=responses) as api:
            with self.assertRaisesRegex(ValueError, 'template'):
                preflight.inspect_identity(preflight.MODEL, preflight.OPTIONS)
            self.assertEqual(api.call_count, 3)
            self.assertNotIn('/api/chat', [call.args[1] for call in api.call_args_list])

    def test_records_resource_failure_before_any_load(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'preflight.json'
            with patch.object(preflight, 'resource_snapshot', side_effect=ValueError('telemetry unavailable')), \
                    patch.object(preflight, 'request_json') as network:
                with self.assertRaisesRegex(ValueError, 'telemetry'):
                    preflight.create_preflight(path, self.jobs)
                network.assert_not_called()
            report = json.loads(path.read_text())
            self.assertEqual(report['status'], 'blocked')
            self.assertIsNone(report['resource_baseline'])
            self.assertEqual(report['generation_requests'], 0)
            self.assertEqual(report['operations'], [])

    def test_records_resident_model_refusal_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(preflight, 'resource_snapshot', return_value=self.baseline), \
                patch.object(preflight, 'loaded_state', return_value=[{'name': preflight.MODEL}]):
            path = Path(directory) / 'preflight.json'
            with self.assertRaisesRegex(ValueError, 'resident'):
                preflight.create_preflight(path, self.jobs)
            original = path.read_bytes()
            self.assertEqual(json.loads(original)['resource_baseline'], self.baseline)
            with self.assertRaisesRegex(ValueError, 'immutable'):
                preflight.create_preflight(path, self.jobs)
            self.assertEqual(path.read_bytes(), original)

    def test_tokenizer_flags_and_duplicate_bos_refused(self):
        with patch.object(preflight, 'request_json', return_value={'tokens': [128000, 12, 13]}) as api:
            self.assertEqual(len(preflight.tokenize(12345, 'fixture')), 3)
            self.assertEqual(api.call_args.args[2], {'content': 'fixture', 'add_special': True, 'parse_special': True})
        for tokens in ([12, 13], [128000, 128000], []):
            with patch.object(preflight, 'request_json', return_value={'tokens': tokens}):
                with self.assertRaises(ValueError):
                    preflight.tokenize(12345, 'fixture')

    def run_mocked_checks(self, rendered_transform=lambda value: value, token_count=10,
                          wire_field='_debug_info', pressure_after_debug=False):
        debug_seen = False

        def resources():
            if pressure_after_debug and debug_seen:
                return {**self.baseline, 'pressure_level': 2}
            return self.baseline

        def fake_api(port, endpoint, payload=None, timeout=60):
            nonlocal debug_seen
            self.assertEqual((port, endpoint), (11434, '/api/chat'))
            self.assertIs(payload['_debug_render_only'], True)
            self.assertIs(payload['truncate'], False)
            self.assertIs(payload['shift'], False)
            self.assertEqual(payload['messages'][0]['role'], 'user')
            text = preflight.SYSTEM_PREFIX + '\n' + payload['messages'][0]['content']
            debug_seen = True
            # Fixture wire keys taken from pinned Ollama api/types.go: the
            # ChatResponse tag is _debug_info; the nested tag is rendered_template.
            return {wire_field: {'rendered_template': rendered_transform(text)}}

        with patch.object(preflight, 'inspect_identity', return_value=self.identity), \
                patch.object(preflight, 'resource_snapshot', side_effect=resources), \
                patch.object(preflight, 'loaded_state', return_value=[{'context_length': 8192}]), \
                patch.object(preflight, 'discover_runner', return_value={'pid': 1, 'port': 12345, 'parent_pid': 2}), \
                patch.object(preflight, 'ensure_idle'), \
                patch.object(preflight, 'tokenize', return_value=[128000] + [5] * (token_count - 1)), \
                patch.object(preflight, 'request_json', side_effect=fake_api) as requests:
            result = preflight.run_checks(self.jobs, preflight.MODEL, preflight.OPTIONS, self.baseline, time.time())
            self.assertEqual(requests.call_count, 60)
            return result

    def test_all_sixty_bound_renderings_counted(self):
        result = self.run_mocked_checks()
        self.assertEqual(len(result['tokens']), 60)
        self.assertEqual(result['tokens']['0']['prompt_tokens'], 10)
        self.assertEqual(result['tokens']['0']['messages_sha256'], self.jobs[0]['messages_sha256'])

    def test_busy_resident_refused_before_first_debug(self):
        with patch.object(preflight, 'inspect_identity', return_value=self.identity), \
                patch.object(preflight, 'resource_snapshot', return_value=self.baseline), \
                patch.object(preflight, 'loaded_state', return_value=[{'context_length': 8192}]), \
                patch.object(preflight, 'discover_runner', return_value={'port': 12345}), \
                patch.object(preflight, 'ensure_idle', side_effect=ValueError('busy runner')), \
                patch.object(preflight, 'request_json') as api:
            with self.assertRaisesRegex(ValueError, 'busy'):
                preflight.run_checks(self.jobs, preflight.MODEL, preflight.OPTIONS, self.baseline, time.time())
            api.assert_not_called()

    def test_truncated_user_content_and_overflow_refused(self):
        with self.assertRaisesRegex(ValueError, 'truncated'):
            self.run_mocked_checks(rendered_transform=lambda text: text[:-1])
        with self.assertRaisesRegex(ValueError, 'reserve'):
            self.run_mocked_checks(token_count=7169)

    def test_actual_source_wire_tag_and_wrong_tag_rejection(self):
        report = self.run_mocked_checks(wire_field='_debug_info')
        self.assertEqual(len(report['tokens']), 60)
        with self.assertRaisesRegex(ValueError, 'Debug rendering'):
            self.run_mocked_checks(wire_field='debug_info')

    def test_post_load_pressure_precedes_response_schema_failure(self):
        with self.assertRaisesRegex(ValueError, 'Resource guard'):
            self.run_mocked_checks(wire_field='debug_info', pressure_after_debug=True)

    def test_verification_preserves_budget_and_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            started = time.time() - 30
            refreshed = {**self.identity, 'tokens': {'0': {'prompt_tokens': 3}}}
            report = {**preflight.bindings(self.jobs, preflight.MODEL, preflight.OPTIONS), **refreshed,
                      'status': 'passed', 'budget_started_unix': started, 'resource_baseline': self.baseline}
            path.write_text(json.dumps(report))
            before = path.read_bytes()
            with patch.object(preflight, 'run_checks', return_value=refreshed) as checks:
                returned = preflight.verify_preflight(path, self.jobs, preflight.MODEL, preflight.OPTIONS)
                self.assertEqual(checks.call_args.args[-1], started)
            self.assertEqual(returned['budget_started_unix'], started)
            self.assertEqual(path.read_bytes(), before)
            changed = copy.deepcopy(refreshed)
            changed['tokens']['0']['prompt_tokens'] = 4
            with patch.object(preflight, 'run_checks', return_value=changed):
                with self.assertRaisesRegex(ValueError, 'changed'):
                    preflight.verify_preflight(path, self.jobs, preflight.MODEL, preflight.OPTIONS)


if __name__ == '__main__':
    unittest.main()
