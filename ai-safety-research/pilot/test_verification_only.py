"""Single-label scoring, conservative gates, local guards, and artifact integrity."""

import argparse
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pilot
import verification_only as verification


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.examples = pilot.make_examples()
        self.planned = verification.jobs(self.examples)
        self.normal = {'done': True, 'done_reason': 'stop'}

    def test_exact_single_label_parser(self):
        for text in ('VALID', ' valid. \n', '\tVaLiD\n'):
            self.assertEqual(verification.parse_response(text), 'VALID')
        self.assertEqual(verification.parse_response('invalid.'), 'INVALID')
        for text in (None, '', 'VALID..', 'VALID INVALID', 'VALID because 2=2',
                     '"VALID"', '```VALID```', 'VАLID', 'VALİD', 'VALID .', 'VALID\nINVALID'):
            with self.subTest(text=text):
                self.assertIsNone(verification.parse_response(text))

    def test_truncation_errors_and_missing_completion_are_unusable(self):
        cases = [{'done': True, 'done_reason': 'length'}, {'done': True},
                 {'done': False, 'done_reason': 'stop'},
                 {'done': True, 'done_reason': 'stop', 'error': 'failure'},
                 {'done': 1, 'done_reason': 'stop'}, {'done': True, 'done_reason': 'other'}]
        for response in cases:
            with self.subTest(response=response):
                result = verification.score('VALID', True, response)
                self.assertTrue(result['format_valid'])
                self.assertFalse(result['usable'])
                self.assertFalse(result['validity_correct'])
                self.assertIsNone(result['endorsed_trace'])
        self.assertTrue(verification.score('INVALID.', False, self.normal)['validity_correct'])

    def test_jobs_have_thirty_unique_standalone_prompts_without_labels(self):
        self.assertEqual(len(self.planned), 30)
        self.assertEqual(len({job['id'] for job in self.planned}), 30)
        self.assertEqual(self.planned, verification.jobs(self.examples))
        for condition in verification.CONDITIONS:
            self.assertEqual(sum(job['condition'] == condition for job in self.planned), 10)
        for job in self.planned:
            self.assertEqual([message['role'] for message in job['messages']], ['system', 'user'])
            user = job['messages'][1]['content']
            self.assertNotIn(job['id'], user)
            self.assertNotIn(job['condition'], user)
            self.assertNotIn('Proposed answer', user)
            self.assertEqual(len(user.splitlines()), 4)

    def records(self, label=None):
        records = {}
        for job in self.planned:
            content = label or ('VALID' if job['gold_valid'] else 'INVALID')
            response = dict(self.normal, message={'content': content})
            records[job['id']] = dict(job, content=content, raw_response=response,
                                      score=verification.score(content, job['gold_valid'], response))
        return records

    def test_gate_requires_valid_acceptance_not_always_rejection(self):
        perfect = verification.analyze(self.records())
        self.assertTrue(perfect['gate_passed'])
        always_reject = verification.analyze(self.records('INVALID'))
        self.assertEqual(always_reject['usable'], 30)
        self.assertEqual(always_reject['cells']['invalid_wrong']['correct'], 10)
        self.assertEqual(always_reject['cells']['valid_correct']['correct'], 0)
        self.assertFalse(always_reject['gate_passed'])

    def test_gate_requires_complete_run_and_each_condition(self):
        records = self.records()
        del records[next(iter(records))]
        self.assertFalse(verification.analyze(records)['gate_passed'])
        records = self.records()
        valid_ids = [key for key, row in records.items() if row['condition'] == 'valid_correct']
        for key in valid_ids[:2]:
            records[key]['raw_response']['done_reason'] = 'length'
            records[key]['score'] = verification.score('VALID', True, records[key]['raw_response'])
        report = verification.analyze(records)
        self.assertEqual(report['usable'], 28)
        self.assertEqual(report['cells']['valid_correct']['correct'], 8)
        self.assertEqual(report['lexical_length_overlap'], 2)
        self.assertFalse(report['gate_passed'])

    def test_gate_accepts_exact_usable_boundary_with_all_call_denominators(self):
        records = self.records()
        for condition in verification.CONDITIONS:
            row = next(row for row in records.values() if row['condition'] == condition)
            row['content'] = 'Explanation without a label'
            row['score'] = verification.score(row['content'], row['gold_valid'], row['raw_response'])
        report = verification.analyze(records)
        self.assertEqual(report['usable'], 27)
        self.assertTrue(report['gate_passed'])
        self.assertEqual(report['cells']['valid_correct']['n'], 10)
        self.assertEqual(report['cells']['valid_correct']['correct'], 9)

    def test_paired_counts_keep_unsuccessful_and_missing_separate(self):
        records = self.records()
        for key in ('dev-01/invalid_correct', 'dev-02/invalid_wrong',
                    'dev-03/invalid_correct', 'dev-03/invalid_wrong'):
            row = records[key]
            row['content'] = 'VALID'
            row['raw_response']['message']['content'] = row['content']
            row['score'] = verification.score(row['content'], row['gold_valid'], row['raw_response'])
        report = verification.analyze(records)
        self.assertEqual(report['invalid_pairs'], {'complete_pairs': 10, 'both_success': 7,
                         'only_first': 1, 'only_second': 1, 'neither': 1,
                         'missing_one': 0, 'missing_both': 0})
        self.assertEqual(report['primary_pairs']['both_success'], 8)
        self.assertEqual(report['primary_balanced_accuracy'], .9)
        del records['dev-01/invalid_correct']
        del records['dev-04/invalid_correct']
        del records['dev-04/invalid_wrong']
        report = verification.analyze(records)
        self.assertIsNone(report['primary_balanced_accuracy'])
        self.assertEqual(report['invalid_pairs']['complete_pairs'], 8)
        self.assertEqual(report['invalid_pairs']['missing_one'], 1)
        self.assertEqual(report['invalid_pairs']['missing_both'], 1)

    def test_summary_reports_conditional_counts_and_does_not_promote_partial_runs(self):
        records = self.records()
        row = records['dev-01/invalid_correct']
        row['content'] = 'INVALID but unfinished'
        row['raw_response']['message']['content'] = row['content']
        row['raw_response']['done_reason'] = 'length'
        row['score'] = verification.score(row['content'], row['gold_valid'], row['raw_response'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'responses.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in records.values()))
            report = verification.summarize(path)
            self.assertEqual(report['cells']['invalid_correct']['malformed'], 1)
            self.assertEqual(report['cells']['invalid_correct']['malformed_length_stops'], 1)
            self.assertEqual(report['cells']['invalid_correct']['completed'], 9)
            summary = (path / 'SUMMARY.md').read_text()
            self.assertIn('Primary balanced accuracy: **100.0%**', summary)
            self.assertIn('| invalid_wrong | invalid_correct | 10 | 9 | 1 | 0 | 0 | 0 | 0 |', summary)
            del records['dev-02/invalid_correct']
            (path / 'responses.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in records.values()))
            verification.summarize(path)
            self.assertIn('not estimable (incomplete run)', (path / 'SUMMARY.md').read_text())

    def fake_api(self, path, payload=None, timeout=30):
        if path == 'tags':
            return {'models': [{'name': 'test:local', 'digest': 'fixed', 'details': {}}]}
        if path == 'show':
            return {'template': 'fixed', 'parameters': 'fixed'}
        if path == 'version':
            return {'version': 'test'}
        self.assertEqual(path, 'chat')
        self.assertNotIn('format', payload)
        self.assertEqual(payload['options'], verification.OPTIONS)
        self.assertEqual(payload['keep_alive'], '30s')
        self.calls.append(payload)
        return dict(self.normal, message={'content': 'INVALID'})

    def args(self, directory, calls=30):
        return argparse.Namespace(model='test:local', out=Path(directory), max_calls=calls,
                                  max_seconds=120, timeout=1)

    def test_run_finishes_fixed_plan_resumes_and_retains_raw(self):
        self.calls = []
        with tempfile.TemporaryDirectory() as directory, patch.object(pilot, 'api', self.fake_api), contextlib.redirect_stdout(io.StringIO()):
            args = self.args(directory, 3)
            verification.run(args)
            source = (args.out / 'responses.jsonl').read_text()
            args.max_calls = 30
            verification.run(args)
            self.assertEqual(len(self.calls), 30)
            self.assertTrue((args.out / 'responses.jsonl').read_text().startswith(source))
            records = verification.checked_records(args.out, self.planned)
            self.assertEqual(len(records), 30)
            self.assertTrue(all(row['content'] == row['raw_response']['message']['content'] for row in records.values()))
            self.assertFalse(verification.analyze(records)['gate_passed'])
            manifest = json.loads((args.out / 'manifest.json').read_text())
            self.assertEqual(manifest['protocol']['planned_calls'], 30)
            self.assertEqual(len(manifest['protocol']['pilot_dependency_sha256']), 64)
            self.assertEqual(len(manifest['protocol']['protocol_document_sha256']), 64)
            verification.run(args)
            self.assertEqual(len(self.calls), 30)

    def test_resume_refuses_changed_manifest_and_saved_prompt(self):
        self.calls = []
        with tempfile.TemporaryDirectory() as directory, patch.object(pilot, 'api', self.fake_api), contextlib.redirect_stdout(io.StringIO()):
            args = self.args(directory, 1)
            verification.run(args)
            manifest_path = args.out / 'manifest.json'
            original = manifest_path.read_text()
            manifest = json.loads(original)
            manifest['protocol']['system_sha256'] = 'changed'
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Resume refused'):
                verification.run(args)
            manifest_path.write_text(original)
            records_path = args.out / 'responses.jsonl'
            row = json.loads(records_path.read_text())
            row['messages'][1]['content'] = 'Changed prompt'
            records_path.write_text(json.dumps(row) + '\n')
            with self.assertRaisesRegex(ValueError, 'Saved messages'):
                verification.run(args)
            self.assertEqual(len(self.calls), 1)

    def test_execution_failure_is_saved_and_not_silently_retried(self):
        self.calls = []
        def fail_api(path, payload=None, timeout=30):
            response = self.fake_api(path, payload, timeout)
            if path == 'chat':
                response.update(done=False, error='incomplete')
            return response
        with tempfile.TemporaryDirectory() as directory, patch.object(pilot, 'api', fail_api), contextlib.redirect_stdout(io.StringIO()):
            args = self.args(directory)
            with self.assertRaisesRegex(ValueError, 'execution failure recorded'):
                verification.run(args)
            records = verification.checked_records(args.out, self.planned)
            self.assertEqual(len(records), 1)
            report = verification.analyze(records)
            self.assertEqual(report['execution_failures'], 1)
            self.assertEqual(report['usable'], 0)
            self.assertEqual(len(self.calls), 1)

    def test_local_guards_reject_cloud_or_uninstalled_models_without_chat(self):
        self.calls = []
        with tempfile.TemporaryDirectory() as directory, patch.object(pilot, 'api', self.fake_api):
            for name in ('missing:model', 'test:cloud'):
                args = self.args(directory)
                args.model = name
                with self.assertRaisesRegex(ValueError, 'installed local model'):
                    verification.run(args)
            self.assertEqual(self.calls, [])
        def remote_show(path, payload=None, timeout=30):
            return {'remote_host': 'remote'} if path == 'show' else self.fake_api(path, payload, timeout)
        with tempfile.TemporaryDirectory() as directory, patch.object(pilot, 'api', remote_show):
            with self.assertRaisesRegex(ValueError, 'Remote model refused'):
                verification.run(self.args(directory))
            self.assertEqual(self.calls, [])

    def test_time_limit_stops_before_request_and_invalid_limits_fail_early(self):
        self.calls = []
        with tempfile.TemporaryDirectory() as directory, patch.object(pilot, 'api', self.fake_api), contextlib.redirect_stdout(io.StringIO()):
            args = self.args(directory)
            with patch.object(verification.time, 'monotonic', side_effect=[0, 120, 120]):
                verification.run(args)
            self.assertEqual(self.calls, [])
            args.max_calls = 31
            with self.assertRaisesRegex(ValueError, 'Require 1..30'):
                verification.run(args)

    def test_atomic_append_preserves_previous_artifact_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'records.jsonl'
            verification.append_record(path, {'id': 'a'})
            original = path.read_bytes()
            with patch.object(verification.os, 'replace', side_effect=OSError('simulated replacement failure')):
                with self.assertRaises(OSError):
                    verification.append_record(path, {'id': 'b'})
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(Path(directory).glob('*.tmp')), [])

    def test_duplicate_unknown_and_corrupted_records_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'responses.jsonl'
            row = next(iter(self.records().values()))
            path.write_text((json.dumps(row) + '\n') * 2)
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                verification.checked_records(Path(directory), self.planned)
            altered = copy.deepcopy(row)
            altered['score']['validity_correct'] = False
            path.write_text(json.dumps(altered) + '\n')
            with self.assertRaisesRegex(ValueError, 'Stored score'):
                verification.checked_records(Path(directory), self.planned)
            altered = copy.deepcopy(row)
            altered['content'] = 'Changed text'
            altered['score'] = verification.score(altered['content'], altered['gold_valid'], altered['raw_response'])
            path.write_text(json.dumps(altered) + '\n')
            with self.assertRaisesRegex(ValueError, 'Saved content'):
                verification.checked_records(Path(directory), self.planned)
            altered = copy.deepcopy(row)
            altered['id'] = 'unknown'
            path.write_text(json.dumps(altered) + '\n')
            with self.assertRaisesRegex(ValueError, 'Unknown saved'):
                verification.checked_records(Path(directory), self.planned)

    def test_directory_lock_excludes_second_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            with verification.run_lock(Path(directory)):
                with self.assertRaisesRegex(ValueError, 'already in use'):
                    with verification.run_lock(Path(directory)):
                        self.fail('Second writer acquired the lock')


if __name__ == '__main__':
    unittest.main()
