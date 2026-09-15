"""Checks for audit denominators, partial pairs, and refusal of corrupt records."""

import copy
import json
import unittest

import audit_results as audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.examples = json.loads(audit.DATA.read_text())[:2]

    def row(self, index=0, context='initial', condition='none', framing='none',
            answer=None, verdict=True, malformed=False, reason='stop'):
        item = self.examples[index]
        has_trace = condition in audit.CONDITIONS[1:]
        answer = item['answer'] if answer is None else answer
        error = 0 if verdict else 1
        parsed = None if malformed else {'answer': answer, 'trace_valid': verdict if has_trace else None,
                                         'first_error': error if has_trace else None}
        trace = item['traces'][condition] if has_trace else None
        record_id = f"{item['id']}/{context}"
        if context == 'correction':
            record_id += f'/{condition}/{framing}'
        elif context == 'standalone':
            record_id += f'/{condition}'
        return {'id': record_id, 'item_id': item['id'], 'context': context, 'condition': condition,
                'framing': framing, 'raw_response': {'done_reason': reason},
                'score': {'parsed': parsed, 'format_valid': not malformed,
                          'answer_correct': not malformed and answer == item['answer'],
                          'validity_correct': None if not has_trace else not malformed and verdict == trace['trace_valid'],
                          'first_error_correct': None if not has_trace else not malformed and error == trace['first_error'],
                          'endorsed_trace': verdict if has_trace and not malformed else None}}

    def test_format_denominators_and_length_overlap(self):
        rows = [self.row(), self.row(1, malformed=True, reason='length')]
        report = audit.audit(rows, self.examples)
        counts = report['overall']
        self.assertEqual(counts['answer_correct'], (1, 2))
        self.assertEqual(counts['answer_correct_parsed'], (1, 1))
        self.assertEqual(counts['malformed_length_stops'], 1)
        self.assertEqual(counts['malformed_nonlength'], 0)
        self.assertFalse(report['parsing_gate'])
        self.assertEqual(report['cohorts'], {'correct': 1, 'incorrect': 0, 'invalid': 1, 'missing': 0})

    def test_always_reject_is_separated_from_valid_acceptance(self):
        rows = [self.row(context='standalone', condition=condition, framing='neutral', verdict=False)
                for condition in audit.CONDITIONS[1:]]
        report = audit.audit(rows, self.examples)
        self.assertEqual(report['overall']['validity_correct'], (2, 3))
        groups = report['groups']
        self.assertEqual(groups[('standalone', 'valid_correct', 'neutral')]['validity_correct'], (0, 1))
        self.assertEqual(groups[('standalone', 'invalid_correct', 'neutral')]['validity_correct'], (1, 1))
        text = audit.render(report)
        self.assertIn('accept valid', text)
        self.assertIn('reject invalid', text)

    def test_missing_pairs_and_parsing_do_not_disappear(self):
        rows = [self.row(), self.row(1),
                self.row(context='correction', condition='unsupported', framing='neutral'),
                self.row(context='correction', condition='unsupported', framing='confident', malformed=True),
                self.row(1, context='correction', condition='unsupported', framing='neutral')]
        report = audit.audit(rows, self.examples)
        pairs = [p for p in report['pairs'] if p['condition'] == 'unsupported' and p['metric'] == 'answer_correct']
        self.assertEqual(pairs[0]['n'], 1)
        self.assertEqual(pairs[0]['neutral_only'], 1)
        self.assertEqual(pairs[0]['difference'], -1)
        self.assertEqual(pairs[0]['missing_one'], 1)
        self.assertEqual(pairs[1]['n'], 0)
        self.assertIsNone(pairs[1]['difference'])

    def test_adoption_is_disjoint_from_other_wrong_and_missing(self):
        suggestion = self.examples[0]['traces']['invalid_wrong']['proposed_answer']
        rows = [self.row(), self.row(1),
                self.row(context='correction', condition='unsupported', framing='confident', answer=suggestion),
                self.row(1, context='correction', condition='unsupported', framing='confident', answer=-100)]
        report = audit.audit(rows, self.examples)
        self.assertEqual(report['adoption']['confident']['adopted_suggestion'], 1)
        self.assertEqual(report['adoption']['confident']['other_wrong'], 1)
        self.assertEqual(report['adoption']['confident']['completed'], 2)
        self.assertEqual(report['adoption']['neutral']['missing'], 2)

    def test_duplicate_mismatched_and_inconsistent_scores_rejected(self):
        row = self.row()
        with self.assertRaises(ValueError):
            audit.audit([row, row], self.examples)
        changed = copy.deepcopy(row)
        changed['id'] = 'bad-id'
        with self.assertRaises(ValueError):
            audit.audit([changed], self.examples)
        changed = copy.deepcopy(row)
        changed['score']['answer_correct'] = False
        with self.assertRaises(ValueError):
            audit.audit([changed], self.examples)

    def test_complete_good_format_gate_requires_every_planned_cell(self):
        rows = []
        for index in range(2):
            rows.append(self.row(index))
            for condition in audit.CONDITIONS:
                for framing in ('neutral', 'confident'):
                    rows.append(self.row(index, 'correction', condition, framing))
            for condition in audit.CONDITIONS[1:]:
                rows.append(self.row(index, 'standalone', condition, 'neutral'))
        report = audit.audit(rows, self.examples)
        self.assertTrue(report['parsing_gate'])
        self.assertEqual(report['overall']['n'], 24)
        self.assertFalse(audit.audit(rows[:-1], self.examples)['parsing_gate'])


if __name__ == '__main__':
    unittest.main()
