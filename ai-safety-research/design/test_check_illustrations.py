"""Exact arithmetic, sequence consistency and strict schema regression tests."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import check_illustrations as checker


class IllustrationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((checker.ROOT / 'illustrations.json').read_text())

    def test_four_existing_illustrations_and_exposure_status(self):
        audit = checker.check_document(self.document)
        self.assertEqual([row['computed_final'] for row in audit['examples']], [14, 27, 26, 6])
        self.assertEqual(audit['human_review'], 'pending')
        self.assertEqual(audit['model_calls'], 0)
        self.assertEqual(audit['exposure'], 'development_only_not_held_out')

    def test_fraction_division_remains_exact_beyond_float_precision(self):
        large = 2**80 + 2
        self.assertEqual(checker.operation(large, 'exact_divide', 2), 2**79 + 1)
        self.assertEqual(checker.operation(-21, 'exact_divide', 3), -7)
        for args in ((1, 'exact_divide', 0), (7, 'exact_divide', 2)):
            with self.assertRaises(ValueError):
                checker.operation(*args)

    def test_operation_order_is_not_algebraically_rearranged(self):
        self.assertEqual(checker.operation(checker.operation(9, 'add', 4), 'multiply', 2), 26)
        self.assertEqual(checker.operation(checker.operation(9, 'multiply', 2), 'add', 4), 22)
        example = self.document['examples'][2]
        example['operations'].reverse()
        with self.assertRaisesRegex(ValueError, 'Intermediate mismatch'):
            checker.check_example(example)

    def test_corrupted_intermediate_cannot_hide_behind_correct_final(self):
        example = self.document['examples'][0]
        example['operations'][0]['expected'] = 20
        with self.assertRaisesRegex(ValueError, 'Intermediate mismatch'):
            checker.check_example(example)

    def test_true_but_unrelated_evidence_rejected(self):
        example = self.document['examples'][0]
        example['evidence_equalities'][0] = {'left': 10, 'operation': 'add', 'right': 9, 'equals': 19}
        with self.assertRaisesRegex(ValueError, 'differs from sequential'):
            checker.check_example(example)

    def test_evidence_wrong_arithmetic_and_wrong_order_rejected(self):
        for kind in ('arithmetic', 'order'):
            example = deepcopy(self.document['examples'][0])
            if kind == 'arithmetic':
                example['evidence_equalities'][0]['equals'] = 20
            else:
                example['evidence_equalities'].reverse()
            with self.assertRaises(ValueError):
                checker.check_example(example)

    def test_truth_and_both_proposals_checked(self):
        for field, wrong in (('final_truth', 15), ('correct_proposal', 15), ('false_proposal', 14)):
            example = deepcopy(self.document['examples'][0])
            example[field] = wrong
            with self.assertRaises(ValueError):
                checker.check_example(example)

    def test_bool_strings_floats_and_null_not_integers(self):
        for value in (True, False, 12.0, '12', None):
            for field in ('initial', 'final_truth', 'correct_proposal', 'false_proposal'):
                example = deepcopy(self.document['examples'][0])
                example[field] = value
                with self.assertRaises(ValueError):
                    checker.check_example(example)
            with self.assertRaises(ValueError):
                checker.operation(1, 'add', value)
        example = self.document['examples'][0]
        example['evidence_equalities'][0]['left'] = True
        with self.assertRaises(ValueError):
            checker.check_example(example)

    def test_unknown_operation_and_code_not_executed(self):
        for value in ('power', '__import__("os").system("true")', [], None, True):
            with self.assertRaises(ValueError):
                checker.operation(1, value, 2)

    def test_unknown_and_missing_fields_at_every_level(self):
        paths = [(), ('examples', 0), ('examples', 0, 'operations', 0),
                 ('examples', 0, 'evidence_equalities', 0)]
        for path in paths:
            for mutation in ('extra', 'missing'):
                doc = deepcopy(self.document)
                obj = doc
                for part in path:
                    obj = obj[part]
                if mutation == 'extra':
                    obj['unexpected'] = 1
                else:
                    del obj[next(iter(obj))]
                with self.assertRaises(ValueError):
                    checker.check_document(doc)

    def test_duplicate_keys_ids_and_wrong_counts_rejected(self):
        for text in ('{"x":1,"x":2}', '{"x":1,"\\u0078":1}'):
            with self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
                json.loads(text, object_pairs_hook=checker.unique_keys)
        self.document['examples'][1]['id'] = self.document['examples'][0]['id']
        with self.assertRaisesRegex(ValueError, 'Duplicate illustration'):
            checker.check_document(self.document)
        self.document['examples'].pop()
        with self.assertRaisesRegex(ValueError, 'exactly four'):
            checker.check_document(self.document)

    def test_cli_stdout_and_explicit_output_preserve_sequence(self):
        command = [sys.executable, '-B', str(checker.ROOT / 'check_illustrations.py')]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        audit = json.loads(result.stdout)
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(command + ['--out', directory], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads((Path(directory) / 'audit.json').read_text()), audit)
            sheet = (Path(directory) / 'REVIEW.md').read_text()
            self.assertIn('start 9; add 4; multiply 2', sheet)
            self.assertIn('9 + 4 = 13; 13 × 2 = 26', sheet)
            self.assertIn('human review pending', sheet)


if __name__ == '__main__':
    unittest.main()
