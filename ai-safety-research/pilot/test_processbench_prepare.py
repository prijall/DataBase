"""Offline parsing parity cases, provenance checks, and nonleaking selection."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import processbench_prepare as adapter


class PreparationTests(unittest.TestCase):
    def examples(self, n=40):
        return [{'id': f'example-{i}', 'generator': 'synthetic-test',
                 'problem': f'Invented problem {i}', 'steps': ['First step', 'Second step'],
                 'final_answer_correct': i % 2 == 0, 'label': -1 if i % 2 == 0 else 1}
                for i in range(n)]

    def test_official_last_boxed_integer_behavior(self):
        cases = [(r'Answer \boxed{-1}', -1),
                 (r'\boxed{1} then \boxed{0} trailing prose', 0),
                 (r'\boxed{1} then \boxed{unknown}', None),
                 (r'\boxed{ +01 }', 1),
                 (r'\boxed{٢}', 2),
                 (r'\boxed{-2}', -2), (r'\boxed{900}', 900),
                 (r'\boxed{1.0}', None), ('1', None), (r'\boxed{', None),
                 ('\\boxed{\n-1\n}', -1), (r'\boxed{{1}}', None)]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(adapter.extract_prediction(text), expected)

    def test_primary_score_preserves_exact_index_and_reports_range_separately(self):
        self.assertTrue(adapter.score_output(r'\boxed{1} ignored prose', 1, 3)['official_match'])
        incorrect_index = adapter.score_output(r'\boxed{0}', 1, 3)
        self.assertFalse(incorrect_index['official_match'])
        self.assertTrue(incorrect_index['strict_index_valid'])
        for text in (r'\boxed{-2}', r'\boxed{3}', 'missing'):
            result = adapter.score_output(text, -1, 3)
            self.assertFalse(result['official_match'])
            self.assertFalse(result['strict_index_valid'])
        self.assertTrue(adapter.score_output(r'\boxed{-1}', -1, 3)['official_match'])
        with self.assertRaises(ValueError):
            adapter.score_output('text', True, 3)

    def test_harmonic_mean_is_not_pooled_accuracy(self):
        scores = [adapter.score_output(r'\boxed{-1}', -1, 2),
                  adapter.score_output(r'\boxed{0}', 0, 2),
                  adapter.score_output(r'\boxed{0}', 1, 2)]
        report = adapter.aggregate_scores(scores)
        self.assertEqual(report['classes']['correct']['accuracy_percent'], 100)
        self.assertEqual(report['classes']['error']['accuracy_percent'], 50)
        self.assertAlmostEqual(report['harmonic_mean_percent'], 200/3)
        zero = adapter.aggregate_scores([adapter.score_output('none', -1, 2),
                                         adapter.score_output('none', 0, 2)])
        self.assertEqual(zero['harmonic_mean_percent'], 0.0)
        self.assertIn('explicit deviation', zero['undefined_convention'])
        self.assertIsNone(adapter.aggregate_scores(scores[:1])['harmonic_mean_percent'])

    def test_prompt_rendering_is_one_user_with_zero_based_tags(self):
        template = '{problem}\n--\n{tagged_response}\nEnd \\boxed{{}}.'
        example = self.examples(1)[0]
        example['steps'] = [' α ', 'a\nb']
        messages = adapter.render_messages(example, template)
        self.assertEqual(messages, [{'role': 'user', 'content':
            'Invented problem 0\n--\n<paragraph_0>\n α \n</paragraph_0>\n\n'
            '<paragraph_1>\na\nb\n</paragraph_1>\nEnd \\boxed{}.'}])

    def test_problem_group_normalization_preserves_case(self):
        self.assertEqual(adapter.problem_group(' Cafe\u0301  A\nB\t'), adapter.problem_group('Café A B'))
        self.assertNotEqual(adapter.problem_group('Café A B'), adapter.problem_group('café A B'))

    def test_splits_are_balanced_order_invariant_and_group_disjoint(self):
        examples = self.examples()
        duplicate = copy.deepcopy(examples[0])
        duplicate['id'] = 'duplicate-solution'
        duplicate['problem'] = '  Invented\nproblem 0 '
        duplicate['label'] = 1
        examples.append(duplicate)
        selected = adapter.select_splits(examples, 4, 6)
        self.assertEqual(selected, adapter.select_splits(list(reversed(examples)), 4, 6))
        groups = {}
        for name, quota in (('calibration', 4), ('evaluation', 6)):
            rows = selected[name]
            self.assertEqual(len(rows), 2 * quota)
            self.assertEqual(sum(row['label'] == -1 for row in rows), quota)
            groups[name] = {adapter.problem_group(row['problem']) for row in rows}
            self.assertEqual(len(groups[name]), len(rows))
        self.assertFalse(groups['calibration'] & groups['evaluation'])

    def test_insufficient_unique_groups_fail_without_splitting_siblings(self):
        examples = self.examples(4)
        for example in examples:
            example['problem'] = 'Same problem'
        with self.assertRaisesRegex(ValueError, 'cannot fill'):
            adapter.select_splits(examples, 1, 1)

    def test_schema_rejects_duplicate_ids_boolean_labels_and_bad_indices(self):
        examples = self.examples(4)
        for mutation in ('duplicate', 'boolean', 'out-of-range', 'empty-step'):
            changed = copy.deepcopy(examples)
            if mutation == 'duplicate':
                changed[1]['id'] = changed[0]['id']
            elif mutation == 'boolean':
                changed[0]['label'] = True
            elif mutation == 'out-of-range':
                changed[0]['label'] = 2
            else:
                changed[0]['steps'] = ['']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                adapter.validate_examples(changed)

    def write_inputs(self, directory):
        path = Path(directory)
        data = path / 'data.json'
        prompt = path / 'prompt.txt'
        provenance = path / 'provenance.json'
        data.write_text(json.dumps(self.examples(), ensure_ascii=False))
        prompt.write_text('  {problem}\n{tagged_response}\nAnswer in \\boxed{{}}.  ')
        metadata = {'repository_revision': adapter.REPOSITORY_REVISION,
                    'dataset_revision': adapter.DATASET_REVISION,
                    'files': {'data': {'sha256': adapter.sha256(data.read_bytes())},
                              'prompt': {'sha256': adapter.sha256(prompt.read_bytes())}}}
        provenance.write_text(json.dumps(metadata))
        return data, prompt, provenance

    def test_hash_and_revision_failures_are_detected_before_preparation(self):
        with tempfile.TemporaryDirectory() as directory:
            data, prompt, provenance = self.write_inputs(directory)
            originals = data.read_bytes()
            data.write_bytes(originals + b' ')
            with self.assertRaisesRegex(ValueError, 'data hash mismatch'):
                adapter.load_inputs(data, prompt, provenance)
            data.write_bytes(originals)
            metadata = json.loads(provenance.read_text())
            metadata['dataset_revision'] = 'unreviewed'
            provenance.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError, 'Unexpected source revisions'):
                adapter.load_inputs(data, prompt, provenance)

    def test_template_rejects_unreviewed_substitutions(self):
        with tempfile.TemporaryDirectory() as directory:
            data, prompt, provenance = self.write_inputs(directory)
            prompt.write_text('{problem} {tagged_response} {label}')
            metadata = json.loads(provenance.read_text())
            metadata['files']['prompt']['sha256'] = adapter.sha256(prompt.read_bytes())
            provenance.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError, 'Unexpected prompt'):
                adapter.load_inputs(data, prompt, provenance)

    def test_preparation_only_writes_metadata_not_prompts_or_results(self):
        with tempfile.TemporaryDirectory() as directory:
            data, prompt, provenance = self.write_inputs(directory)
            out = Path(directory) / 'prepared'
            manifest = adapter.prepare(data, prompt, provenance, out, 4, 6)
            self.assertEqual(list(out.iterdir()), [out / 'selection.json'])
            serialized = (out / 'selection.json').read_text()
            self.assertEqual(json.loads(serialized), manifest)
            self.assertNotIn('Invented problem', serialized)
            self.assertNotIn('First step', serialized)
            self.assertEqual(manifest['problem_group_overlap'], 0)
            self.assertIn('No model calls', manifest['execution_status'])
            self.assertEqual(manifest['splits']['calibration']['count'], 8)
            self.assertEqual(manifest['splits']['evaluation']['count'], 12)
            with self.assertRaises(FileExistsError):
                adapter.prepare(data, prompt, provenance, out, 4, 6)

    def test_length_summaries_include_utf8_bytes_without_claiming_tokens(self):
        examples = self.examples()
        for example in examples:
            example['steps'][0] += ' café α'
        manifest = adapter.make_manifest(examples, '{problem}\n{tagged_response}', {}, {}, 2, 2)
        for split in manifest['splits'].values():
            for record in split['records']:
                self.assertGreater(record['rendered_utf8_bytes'], record['rendered_characters'])
                self.assertNotIn('token_count', record)
        self.assertIn('do not prove context fit', manifest['limitations'][0])


if __name__ == '__main__':
    unittest.main()
