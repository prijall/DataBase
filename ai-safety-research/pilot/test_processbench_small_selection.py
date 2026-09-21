"""Portable synthetic tests for the offline small-context reservation."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import processbench_prepare as preparation
import processbench_small_selection as small


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.data = self.root / 'data.json'
        self.prompt = self.root / 'prompt.txt'
        self.provenance = self.root / 'provenance.json'
        self.original = self.root / 'original.json'
        self.selection = self.root / 'new.json'
        self.examples = []
        # Every textual group has NFC/whitespace aliases with opposite labels.
        # Excluding IDs alone would leak one of these unselected siblings.
        for index in range(100):
            for alias in (0, 1):
                self.examples.append({
                    'id': f'case-{index:03d}-{alias}', 'generator': 'fixture',
                    'problem': f'Problem {index} café' if alias == 0 else f'  Problem\t{index}  cafe\u0301\n',
                    'steps': ['1 + 1 = 2', '2 + 2 = 4'],
                    'label': -1 if alias == 0 else 1,
                    'final_answer_correct': alias == 0})
        self.data.write_text(json.dumps(self.examples))
        self.prompt.write_text('Problem: {problem}\nSteps: {tagged_response}')
        self.provenance.write_text(json.dumps({
            'repository_revision': preparation.REPOSITORY_REVISION,
            'dataset_revision': preparation.DATASET_REVISION,
            'files': {name: {'sha256': preparation.sha256(path.read_bytes())}
                      for name, path in (('data', self.data), ('prompt', self.prompt))}}))
        self.inputs = preparation.load_inputs(self.data, self.prompt, self.provenance)
        self.old_manifest = preparation.make_manifest(*self.inputs)
        self.original.write_text(json.dumps(self.old_manifest, indent=2) + '\n')
        self.old_sha = preparation.sha256(self.original.read_bytes())
        original_patch = patch.object(small, 'ORIGINAL_SELECTION', self.original)
        hash_patch = patch.object(small, 'ORIGINAL_SELECTION_SHA256', self.old_sha)
        original_patch.start()
        hash_patch.start()
        self.addCleanup(original_patch.stop)
        self.addCleanup(hash_patch.stop)

    def write_selection(self, manifest=None):
        if manifest is None:
            manifest = small.make_manifest(*self.inputs)
        self.selection.write_text(json.dumps(manifest, indent=2) + '\n')
        return manifest

    def load_jobs(self):
        return small.load_jobs(self.data, self.prompt, self.provenance, self.selection)

    def test_balance_alias_exclusions_and_exact_evaluation(self):
        new = self.write_selection()
        calibration = new['splits']['calibration']
        self.assertEqual(calibration['count'], 20)
        self.assertEqual(calibration['class_counts'], {'valid': 10, 'error': 10})
        groups = {row['problem_group_sha256'] for row in calibration['records']}
        excluded = set(new['excluded_problem_groups'])
        self.assertEqual(len(excluded), 60)
        self.assertEqual(len(groups), 20)
        self.assertFalse(groups & excluded)
        self.assertEqual(new['splits']['evaluation'], self.old_manifest['splits']['evaluation'])
        forbidden_ids = {row['id'] for row in self.examples
                         if preparation.problem_group(row['problem']) in excluded}
        self.assertEqual(len(forbidden_ids), 120)  # Both siblings of every original group.
        self.assertFalse(forbidden_ids & {row['id'] for row in calibration['records']})
        jobs, hashes = self.load_jobs()
        self.assertEqual(len(jobs), 60)
        self.assertEqual(hashes['original_selection'], self.old_sha)
        self.assertEqual(hashes['selection'], preparation.sha256(self.selection.read_bytes()))
        self.assertTrue(all(small.canonical_hash(row['messages']) == row['messages_sha256'] for row in jobs))

    def test_input_order_invariance(self):
        expected = small.make_manifest(*self.inputs)
        examples, template, provenance, hashes = self.inputs
        actual = small.make_manifest(list(reversed(examples)), template, provenance, hashes)
        self.assertEqual(actual, expected)

    def test_original_byte_pin_rejects_whitespace_edit(self):
        self.original.write_text(self.original.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'Original selection byte hash'):
            small.make_manifest(*self.inputs)

    def test_original_reconstruction_mismatch(self):
        examples, template, provenance, hashes = self.inputs
        changed = deepcopy(examples)
        selected_id = self.old_manifest['splits']['calibration']['records'][0]['id']
        next(row for row in changed if row['id'] == selected_id)['steps'][0] = 'Changed source step'
        with self.assertRaisesRegex(ValueError, 'Original selection differs'):
            small.make_manifest(changed, template, provenance, hashes)

    def test_data_source_hash_mismatch(self):
        self.write_selection()
        self.data.write_text(self.data.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'data hash mismatch'):
            self.load_jobs()

    def test_prompt_source_hash_mismatch(self):
        self.write_selection()
        self.prompt.write_text(self.prompt.read_text() + ' instruction')
        with self.assertRaisesRegex(ValueError, 'prompt hash mismatch'):
            self.load_jobs()

    def test_evaluation_order_and_record_tampering_rejected(self):
        base = small.make_manifest(*self.inputs)
        for mode in ('order', 'field'):
            with self.subTest(mode=mode):
                changed = deepcopy(base)
                records = changed['splits']['evaluation']['records']
                if mode == 'order':
                    records[0], records[1] = records[1], records[0]
                else:
                    records[0]['messages_sha256'] = '0' * 64
                self.write_selection(changed)
                with self.assertRaisesRegex(ValueError, 'deterministic pinned-source'):
                    self.load_jobs()

    def test_selector_code_binding_tamper_rejected(self):
        changed = small.make_manifest(*self.inputs)
        changed['code_sha256'] = '0' * 64
        self.write_selection(changed)
        with self.assertRaisesRegex(ValueError, 'deterministic pinned-source'):
            self.load_jobs()

    def test_quota_failure_does_not_reallocate(self):
        groups = sorted({preparation.problem_group(row['problem']) for row in self.examples})
        # Only 19 mixed-label groups remain: cannot produce 20 unique problems.
        with self.assertRaisesRegex(ValueError, 'cannot fill fixed calibration quotas'):
            small.select_calibration(self.examples, set(groups[:-19]))


if __name__ == '__main__':
    unittest.main()
