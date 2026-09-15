"""Checks for ground-truth validity, strict scoring, and frozen conversations."""

import json
from pathlib import Path
import tempfile
import unittest

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


if __name__ == '__main__':
    unittest.main()
