"""Checks for ground-truth validity, strict scoring, and frozen conversations."""

import json
import argparse
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pilot


class PilotTests(unittest.TestCase):
    def test_exact_arithmetic(self):
        self.assertEqual(pilot.arithmetic('(7+2)*3-8'), 19)
        self.assertEqual(pilot.arithmetic('1/3+2/3'), 1)

    def test_rejects_executable_expressions(self):
        for expression in ['__import__("os")', 'x+1', '2**100', 'True', '[1][0]']:
            with self.assertRaises(ValueError):
                pilot.arithmetic(expression)

    def test_dataset_and_distinct_truth_labels(self):
        examples = pilot.make_examples()
        pilot.validate(examples)
        for item in examples:
            self.assertEqual(item['traces']['invalid_correct']['errors'], [1, 2])
            self.assertEqual(item['traces']['invalid_wrong']['errors'], [1])

    def test_independently_calculated_answers(self):
        self.assertEqual([x['answer'] for x in pilot.make_examples()],
                         [67, 76, 177, 405, 883, 127, 200, 381, 550, 1093])

    def test_checker_catches_corrupted_gold(self):
        examples = pilot.make_examples()
        examples[0]['traces']['invalid_correct']['first_error'] = 0
        with self.assertRaises(AssertionError):
            pilot.validate(examples)

    def test_no_truth_from_final_answer_alone(self):
        item = pilot.make_examples()[0]
        response = json.dumps({'answer': item['answer'], 'trace_valid': True, 'first_error': 0})
        result = pilot.score(response, item, item['traces']['invalid_correct'])
        self.assertTrue(result['answer_correct'])
        self.assertFalse(result['validity_correct'])

    def test_worked_protocol_is_scored_separately(self):
        content = json.dumps({'working': '12 + 7 = 19; 19 * 4 = 76; 76 - 9 = 67.',
                              'answer': 67, 'trace_valid': None, 'first_error': None})
        self.assertIsNone(pilot.parse_response(content, False))
        self.assertEqual(pilot.parse_response(content, False, worked=True)['answer'], 67)

    def test_freeform_verdict_is_separate_from_calculations(self):
        item = pilot.make_examples()[0]
        content = ('12 + 7 = 19; 19 * 4 = 76; 76 - 9 = 67.\n<FINAL_JSON>\n'
                   '{"answer": 67, "trace_valid": null, "first_error": null}\n</FINAL_JSON>')
        self.assertIsNone(pilot.parse_response(content, False))
        self.assertIsNone(pilot.parse_response(content, False, worked=True))
        self.assertTrue(pilot.score(content, item, freeform=True)['answer_correct'])
        self.assertEqual(set(pilot.parse_response(content, False, freeform=True)),
                         {'answer', 'trace_valid', 'first_error'})
        trace_content = content.replace('null, "first_error": null', 'true, "first_error": 0')
        result = pilot.score(trace_content, item, item['traces']['invalid_correct'], freeform=True)
        self.assertTrue(result['answer_correct'])
        self.assertFalse(result['validity_correct'])

    def test_freeform_rejects_ambiguous_or_incomplete_final_blocks(self):
        verdict = '{"answer": 67, "trace_valid": null, "first_error": null}'
        block = '<FINAL_JSON>\n' + verdict + '\n</FINAL_JSON>'
        cases = [None, verdict, block, ' \n' + block, 'work\n' + block + '\nextra',
                 'work\n' + block + '\n' + block,
                 'work\n<FINAL_JSON>\n' + verdict,
                 'work\n<FINAL_JSON>' + verdict + '</FINAL_JSON>',
                 'work\n<FINAL_JSON>\n```json\n' + verdict + '\n```\n</FINAL_JSON>',
                 'work\n' + block.replace('"answer": 67', '"answer": 0, "answer": 67')]
        for content in cases:
            with self.subTest(content=content):
                self.assertIsNone(pilot.parse_response(content, False, freeform=True))
        self.assertIsNone(pilot.parse_response('work\n' + block, False,
                                               worked=True, freeform=True))

    def test_freeform_cli_modes_are_mutually_exclusive(self):
        arguments = ['pilot.py', 'run', '--model', 'test:local', '--out', '/unused',
                     '--worked', '--freeform']
        with patch('sys.argv', arguments), patch.object(pilot, 'api') as api, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                pilot.main()
            self.assertEqual(raised.exception.code, 2)
            api.assert_not_called()

    def test_freeform_run_omits_json_constraint_and_retains_raw_text(self):
        content = ('12 + 7 = 19; 19 * 4 = 76; 76 - 9 = 67.\n<FINAL_JSON>\n'
                   '{"answer": 67, "trace_valid": null, "first_error": null}\n</FINAL_JSON>')
        payloads = []

        def fake_api(path, payload=None, timeout=30):
            if path == 'tags':
                return {'models': [{'name': 'test:local', 'digest': 'fixed', 'details': {}}]}
            if path == 'show':
                return {'template': 'fixed'}
            if path == 'version':
                return {'version': 'test'}
            self.assertEqual(path, 'chat')
            payloads.append(payload)
            return {'done': True, 'done_reason': 'stop', 'message': {'content': content}}

        with tempfile.TemporaryDirectory() as directory, patch.object(pilot, 'api', fake_api), contextlib.redirect_stdout(io.StringIO()):
            args = argparse.Namespace(model='test:local', out=Path(directory), max_calls=1,
                                      max_seconds=120, timeout=1, worked=False, freeform=True)
            pilot.run(args)
            self.assertNotIn('format', payloads[0])
            self.assertEqual(payloads[0]['options']['num_predict'], 512)
            self.assertEqual(payloads[0]['messages'][0]['content'], pilot.FREEFORM_SYSTEM)
            row = next(iter(pilot.load_records(args.out / 'responses.jsonl').values()))
            self.assertEqual(row['content'], content)
            self.assertEqual(row['raw_response']['message']['content'], content)
            self.assertTrue(row['score']['answer_correct'])
            protocol = json.loads((args.out / 'manifest.json').read_text())['protocol']
            self.assertEqual(protocol['protocol_name'], 'freeform-v3')
            self.assertIsNone(protocol['format'])
            self.assertEqual(protocol['verdict_parser'], 'single-final-json-block-v1')
            args.freeform = False
            with self.assertRaisesRegex(ValueError, 'Resume refused'):
                pilot.run(args)
            self.assertEqual(len(payloads), 1)

    def test_malformed_responses_fail_without_disappearing(self):
        item = pilot.make_examples()[0]
        for response in ['not JSON', '[]', '{"answer": 67}',
                         '{"answer": true, "trace_valid": null, "first_error": null}',
                         '{"answer": 67, "trace_valid": true, "first_error": 1}']:
            result = pilot.score(response, item, item['traces']['valid_correct'])
            self.assertFalse(result['format_valid'])
            self.assertFalse(result['answer_correct'])
            self.assertFalse(result['validity_correct'])

    def test_complete_plan_and_frozen_prefixes(self):
        examples, saved = pilot.make_examples(), {}
        planned = []
        for job in pilot.jobs(examples, saved, 42):
            planned.append(job)
            if job['context'] == 'initial':
                saved[job['id']] = {'content': 'unchanged original, even when invalid'}
        self.assertEqual(len(planned), 120)
        self.assertEqual(len({j['id'] for j in planned}), 120)
        self.assertEqual(sum(j['context'] == 'standalone' for j in planned), 30)
        for job in planned:
            if job['context'] == 'correction':
                self.assertEqual(job['messages'][2]['content'], 'unchanged original, even when invalid')
            for message in job['messages']:
                self.assertNotIn('"errors":', message['content'])

    def test_duplicate_records_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'responses.jsonl'
            path.write_text('{"id":"a"}\n{"id":"a"}\n')
            with self.assertRaises(ValueError):
                pilot.load_records(path)

    def test_resume_preserves_calls_and_rejects_changed_protocol(self):
        calls = []

        def fake_api(path, payload=None, timeout=30):
            if path == 'tags':
                return {'models': [{'name': 'test:local', 'digest': 'fixed', 'details': {}}]}
            if path == 'show':
                return {'template': 'fixed'}
            if path == 'version':
                return {'version': 'test'}
            self.assertEqual(path, 'chat')
            calls.append(payload['messages'])
            return {'done': True, 'message': {'content': json.dumps(
                {'answer': 0, 'trace_valid': None, 'first_error': None})}}

        with tempfile.TemporaryDirectory() as directory, patch.object(pilot, 'api', fake_api), contextlib.redirect_stdout(io.StringIO()):
            args = argparse.Namespace(model='test:local', out=Path(directory), max_calls=2,
                                      max_seconds=120, timeout=1)
            pilot.run(args)
            originals = (args.out / 'responses.jsonl').read_text()
            args.max_calls = 120
            pilot.run(args)
            self.assertEqual(len(calls), 120)
            self.assertTrue((args.out / 'responses.jsonl').read_text().startswith(originals))
            self.assertEqual(len(pilot.load_records(args.out / 'responses.jsonl')), 120)
            manifest = args.out / 'manifest.json'
            changed = json.loads(manifest.read_text())
            changed['protocol']['job_seed'] = 99
            manifest.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                pilot.run(args)


if __name__ == '__main__':
    unittest.main()
