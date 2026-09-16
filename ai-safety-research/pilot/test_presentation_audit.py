"""Adversarial checks for conservative recovery and immutable primary scores."""

import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pilot
import presentation_audit as presentation


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.examples = pilot.make_examples()
        self.verdict = '{"answer": 67, "trace_valid": false, "first_error": 2}'

    def test_terminal_json_and_fence(self):
        for prefix, suffix, method in [('', '', 'terminal-json'),
                                       ('```json\n', '\n```', 'fenced-terminal-json'),
                                       ('```\n', '\n```', 'fenced-terminal-json')]:
            with self.subTest(method=method, prefix=prefix):
                actual, candidate, reason = presentation.extract('Calculations.\n' + prefix + self.verdict + suffix, True)
                self.assertEqual(actual, method)
                self.assertEqual(candidate, self.verdict)
                self.assertIsNone(reason)

    def test_terminal_scalar_lines_preserve_values(self):
        text = 'Calculations.\nanswer: 67\ntrace_valid: false\nfirst_error: 2\n'
        method, candidate, reason = presentation.extract(text, True)
        self.assertEqual(method, 'terminal-scalar-lines')
        self.assertIsNone(reason)
        self.assertEqual(json.loads(presentation.candidate_json(method, candidate)), json.loads(self.verdict))

    def test_initial_nulls_and_reordered_fields_are_accepted(self):
        content = 'Work.\nfirst_error: null\nanswer: -4\ntrace_valid: null'
        method, candidate, reason = presentation.extract(content, False)
        self.assertIsNone(reason)
        self.assertEqual(pilot.parse_response(presentation.candidate_json(method, candidate), False)['answer'], -4)

    def test_rejects_duplicate_competing_and_repeated_prose_fields(self):
        cases = [self.verdict + '\n' + self.verdict,
                 '{"answer": 12, "answer": 67, "trace_valid": false, "first_error": 2}',
                 'answer: 12\n' + self.verdict,
                 'ANSWER: 12\n' + self.verdict,
                 'Earlier "trace_valid": true.\n' + self.verdict]
        for content in cases:
            with self.subTest(content=content):
                self.assertIsNotNone(presentation.extract(content, True)[2])

    def test_rejects_escaped_duplicate_json_keys(self):
        for first_answer in (12, 67):
            content = ('{"answer": ' + str(first_answer)
                       + r', "\u0061nswer": 67, "trace_valid": false, "first_error": 2}')
            with self.subTest(first_answer=first_answer):
                method, candidate, reason = presentation.extract(content, True)
                self.assertIsNone(method)
                self.assertIsNone(candidate)
                self.assertEqual(reason, 'escaped JSON key spelling outside recovery rule')

    def test_rejects_earlier_verdict_with_escaped_field_names(self):
        earlier = (r'{"\u0061nswer": 12, "\u0074race_valid": true, '
                   r'"\u0066irst_error": 0}')
        self.assertEqual(presentation.extract(earlier + '\n' + self.verdict, True)[2],
                         'escaped JSON key spelling outside recovery rule')

    def test_rejects_missing_fields_prose_and_nonterminal_outputs(self):
        cases = ['The answer is 67 and the first error is 2.',
                 '{"answer": 67, "trace_valid": false}',
                 self.verdict + '\nThis is my verdict.',
                 'answer: 67\ntrace_valid: false\nfirst_error: 2\nDone.',
                 '<FINAL_JSON>\n' + self.verdict + '\n</FINAL_JSON>',
                 '```json\n' + self.verdict,
                 'answer: 67\n\ntrace_valid: false\nfirst_error: 2',
                 'Answer: 67\ntrace_valid: false\nfirst_error: 2',
                 self.verdict.replace('"first_error": 2', '"first_error": 2, "extra": 3')]
        for content in cases:
            with self.subTest(content=content):
                self.assertIsNotNone(presentation.extract(content, True)[2])

    def test_rejects_type_applicability_and_consistency_repairs(self):
        cases = [(self.verdict.replace('false', '"false"'), True),
                 (self.verdict.replace('false', 'null'), True),
                 (self.verdict.replace('2}', 'null}'), True),
                 (self.verdict.replace('false', 'true'), True),
                 (self.verdict, False),
                 ('answer: 67\ntrace_valid: false\nfirst_error: 0', True),
                 ('answer: 67.0\ntrace_valid: false\nfirst_error: 2', True),
                 ('answer: 1٢\ntrace_valid: false\nfirst_error: 2', True),
                 ('answer: 67\ntrace_valid: false\nfirst_error: 1٢', True),
                 ('answer: "67"\ntrace_valid: false\nfirst_error: 2', True),
                 ('answer: true\ntrace_valid: false\nfirst_error: 2', True),
                 ('answer: 67\ntrace_valid: False\nfirst_error: 2', True)]
        for content, has_trace in cases:
            with self.subTest(content=content, has_trace=has_trace):
                self.assertIsNotNone(presentation.extract(content, has_trace)[2])

    def row(self, content, item_index=0, condition='none', length=False):
        item = self.examples[item_index]
        trace = item['traces'].get(condition)
        context = 'standalone' if trace else 'initial'
        return {'id': f"{item['id']}/{context}" + (f'/{condition}' if trace else ''),
                'item_id': item['id'], 'context': context, 'condition': condition,
                'framing': 'neutral' if trace else 'none', 'content': content,
                'raw_response': {'done_reason': 'length' if length else 'stop'},
                'score': pilot.score(content, item, trace, freeform=True)}

    def test_separate_scores_do_not_repair_incorrect_reasoning(self):
        row = self.row(self.verdict, condition='invalid_correct', length=True)
        original = copy.deepcopy(row)
        recovered = presentation.audit([row], self.examples)[0]
        self.assertEqual(row, original)
        self.assertEqual(recovered['original_score'], original['score'])
        self.assertEqual(recovered['status'], 'additionally-recovered')
        self.assertTrue(recovered['score']['answer_correct'])
        self.assertTrue(recovered['score']['validity_correct'])
        self.assertFalse(recovered['score']['first_error_correct'])
        self.assertTrue(recovered['length_stop'])
        self.assertFalse(original['score']['format_valid'])

    def test_audit_partitions_primary_recovered_and_unusable(self):
        strict = ('Work.\n<FINAL_JSON>\n'
                  '{"answer": 67, "trace_valid": null, "first_error": null}\n</FINAL_JSON>')
        rows = [self.row(strict),
                self.row('answer: 76\ntrace_valid: null\nfirst_error: null', 1),
                self.row('not a verdict', 2, length=True)]
        results = presentation.audit(rows, self.examples)
        self.assertEqual([r['status'] for r in results],
                         ['strict-valid', 'additionally-recovered', 'still-unusable'])
        self.assertIsNone(results[0]['score'])
        self.assertIsNone(results[2]['score'])
        report = presentation.render(results, 'source-hash')
        self.assertIn('| strict-valid | 1 | 0 | 0 |', report)
        self.assertIn('| still-unusable | 1 | 1 | 0 |', report)
        self.assertIn('| answer_correct | 1/3 | 1/1 | 1/3 |', report)
        self.assertIn('cannot retroactively pass the frozen gate', report)

    def test_cli_only_writes_separate_audit_artifacts(self):
        row = self.row('answer: 67\ntrace_valid: null\nfirst_error: null')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            source = json.dumps(row) + '\n'
            (path / 'responses.jsonl').write_text(source)
            (path / 'SUMMARY.md').write_text('Frozen report.\n')
            with patch('sys.argv', ['presentation_audit.py', '--out', directory]), contextlib.redirect_stdout(io.StringIO()):
                presentation.main()
            self.assertEqual((path / 'responses.jsonl').read_text(), source)
            self.assertEqual((path / 'SUMMARY.md').read_text(), 'Frozen report.\n')
            self.assertTrue((path / 'PRESENTATION_AUDIT.md').is_file())
            recovered = json.loads((path / 'PRESENTATION_RECOVERY.jsonl').read_text())
            self.assertEqual(recovered['id'], row['id'])
            self.assertTrue(recovered['score']['answer_correct'])


if __name__ == '__main__':
    unittest.main()
