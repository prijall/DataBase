"""Offline ProcessBench source verification, grouped selection, and scorer helpers.

No network or model inference. Supply locally downloaded, pinned inputs.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import statistics
import string
import unicodedata

REPOSITORY_REVISION = 'e8024636bcabdf8bd514440551b531d3f90dd18b'
DATASET_REVISION = '3bdcd5371ed567559a78f559c01c13a6deee7604'
SELECTION_VERSION = 'processbench-grouped-hash-v1'
SALT = SELECTION_VERSION + ':42'


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def problem_group(problem):
    """Text identity only: NFC and collapsed whitespace, without case folding."""
    normalized = ' '.join(unicodedata.normalize('NFC', problem).split())
    return sha256(normalized.encode('utf-8'))


def validate_examples(examples):
    if not isinstance(examples, list) or not examples:
        raise ValueError('Expected a nonempty JSON list of examples')
    seen = set()
    for example in examples:
        if not isinstance(example, dict):
            raise ValueError('Each example must be an object')
        for field in ('id', 'generator', 'problem'):
            if not isinstance(example.get(field), str) or not example[field].strip():
                raise ValueError(f'Missing or invalid {field}')
        if example['id'] in seen:
            raise ValueError('Duplicate example ID')
        seen.add(example['id'])
        steps = example.get('steps')
        if not isinstance(steps, list) or not steps or any(not isinstance(step, str) or not step.strip() for step in steps):
            raise ValueError('Steps must be a nonempty list of nonempty strings')
        label = example.get('label')
        if type(label) is not int or not -1 <= label < len(steps):
            raise ValueError('Gold label must be -1 or an existing zero-based step index')
        if type(example.get('final_answer_correct')) is not bool:
            raise ValueError('final_answer_correct must be Boolean')


def load_inputs(data_path, prompt_path, provenance_path):
    provenance_bytes = provenance_path.read_bytes()
    provenance = json.loads(provenance_bytes)
    if provenance.get('repository_revision') != REPOSITORY_REVISION or provenance.get('dataset_revision') != DATASET_REVISION:
        raise ValueError('Unexpected source revisions; this adapter audits only the pinned versions')
    blobs = {'data': data_path.read_bytes(), 'prompt': prompt_path.read_bytes()}
    hashes = {}
    for name, content in blobs.items():
        expected = provenance.get('files', {}).get(name, {}).get('sha256')
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
            raise ValueError(f'Missing or invalid {name} SHA-256 in provenance')
        hashes[name] = sha256(content)
        if hashes[name] != expected:
            raise ValueError(f'{name} hash mismatch')
    examples = json.loads(blobs['data'])
    validate_examples(examples)
    template = blobs['prompt'].decode('utf-8').strip()
    fields = []
    for _, field, spec, conversion in string.Formatter().parse(template):
        if field is not None:
            if field not in ('problem', 'tagged_response') or spec or conversion:
                raise ValueError('Unexpected prompt template field or formatting rule')
            fields.append(field)
    if Counter(fields) != Counter(('problem', 'tagged_response')):
        raise ValueError('Prompt must contain each published substitution field exactly once')
    hashes['provenance'] = sha256(provenance_bytes)
    return examples, template, provenance, hashes


def render_messages(example, template):
    # Independently expressed implementation of the audited public interface.
    paragraphs = '\n\n'.join('<paragraph_{0}>\n{1}\n</paragraph_{0}>'.format(index, step)
                              for index, step in enumerate(example['steps'])).strip()
    return [{'role': 'user', 'content': template.format(problem=example['problem'],
                                                       tagged_response=paragraphs)}]


def extract_prediction(text):
    """Published greedy behavior: convert the LAST boxed substring with Python int."""
    if not isinstance(text, str):
        return None
    matches = re.findall(r'\\boxed\{([^}]*)\}', text)
    if not matches:
        return None
    try:
        return int(matches[-1].strip())
    except (ValueError, TypeError):
        return None


def score_output(text, gold_label, step_count):
    if type(step_count) is not int or step_count < 1:
        raise ValueError('step_count must be a positive integer')
    if type(gold_label) is not int or not -1 <= gold_label < step_count:
        raise ValueError('Invalid gold label')
    prediction = extract_prediction(text)
    in_range = prediction is not None and -1 <= prediction < step_count
    return {'gold_label': gold_label, 'prediction': prediction,
            'official_match': prediction == gold_label,
            'strict_index_valid': in_range}


def aggregate_scores(scores):
    """Published aggregation, except the prespecified zero/zero convention is zero."""
    classes = {}
    for name, valid in (('error', False), ('correct', True)):
        rows = [row for row in scores if (row['gold_label'] == -1) == valid]
        correct = sum(row['official_match'] for row in rows)
        classes[name] = {'n': len(rows), 'matches': correct,
                         'accuracy_percent': 100 * correct / len(rows) if rows else None}
    a, b = (classes[name]['accuracy_percent'] for name in ('error', 'correct'))
    harmonic = None if a is None or b is None else 0.0 if a + b == 0 else 2 * a * b / (a + b)
    return {'classes': classes, 'harmonic_mean_percent': harmonic,
            'undefined_convention': 'null for an empty class; zero for zero-sum accuracies (explicit deviation from unguarded upstream division)'}


def rank(kind, value):
    return sha256(f'{SALT}:{kind}:{value}'.encode('utf-8'))


def select_splits(examples, calibration_per_label=10, evaluation_per_label=20):
    validate_examples(examples)
    if any(type(quota) is not int or quota < 1 for quota in (calibration_per_label, evaluation_per_label)):
        raise ValueError('Split quotas must be positive integers')
    grouped = defaultdict(list)
    for example in examples:
        grouped[problem_group(example['problem'])].append(example)
    ordered_groups = sorted(grouped, key=lambda group: (rank('group', group), group))
    for group in grouped:
        grouped[group].sort(key=lambda example: (rank('record', example['id']), example['id']))
    allocated = set()
    splits = {}
    for name, quota in (('calibration', calibration_per_label), ('evaluation', evaluation_per_label)):
        selected, counts = [], Counter(valid=0, error=0)
        for group in ordered_groups:
            if group in allocated:
                continue
            taken = []
            for example in grouped[group]:
                category = 'valid' if example['label'] == -1 else 'error'
                if counts[category] < quota:
                    taken.append(example)
                    counts[category] += 1
                    break  # At most one solution per normalized problem, within either cohort.
            if taken:
                allocated.add(group)  # Even unselected siblings are barred from the other split.
                selected.extend(taken)
            if counts['valid'] == counts['error'] == quota:
                break
        if counts['valid'] != quota or counts['error'] != quota:
            raise ValueError(f'Fixed group allocation cannot fill {name} quotas: {dict(counts)}; '
                             'no automatic reallocation or leakage is allowed')
        splits[name] = selected
    return splits


def length_summary(values):
    return {'minimum': min(values), 'median': statistics.median(values), 'maximum': max(values),
            'mean': statistics.mean(values)}


def make_manifest(examples, template, provenance, input_hashes, calibration_per_label=10, evaluation_per_label=20):
    splits = select_splits(examples, calibration_per_label, evaluation_per_label)
    selections = {}
    for name, selected in splits.items():
        records = []
        for example in selected:
            messages = render_messages(example, template)
            content = messages[0]['content']
            records.append({'id': example['id'], 'problem_group_sha256': problem_group(example['problem']),
                            'gold_label': example['label'], 'label_class': 'valid' if example['label'] == -1 else 'error',
                            'step_count': len(example['steps']), 'rendered_characters': len(content),
                            'rendered_utf8_bytes': len(content.encode('utf-8')),
                            'messages_sha256': sha256(json.dumps(messages, sort_keys=True, ensure_ascii=False).encode('utf-8'))})
        selections[name] = {'records': records, 'count': len(records),
                            'class_counts': dict(Counter(record['label_class'] for record in records)),
                            'problem_group_count': len({record['problem_group_sha256'] for record in records}),
                            'rendered_character_lengths': length_summary([record['rendered_characters'] for record in records]),
                            'rendered_utf8_byte_lengths': length_summary([record['rendered_utf8_bytes'] for record in records])}
    overlap = {record['problem_group_sha256'] for record in selections['calibration']['records']} & {
        record['problem_group_sha256'] for record in selections['evaluation']['records']}
    if overlap:
        raise ValueError('Problem-group leakage detected')
    return {'artifact_type': 'offline-selection-only', 'selection_version': SELECTION_VERSION,
            'code_sha256': sha256(Path(__file__).read_bytes()), 'source_provenance': provenance,
            'input_sha256': input_hashes,
            'population': {'records': len(examples),
                           'normalized_problem_groups': len({problem_group(example['problem']) for example in examples}),
                           'class_counts': dict(Counter('valid' if example['label'] == -1 else 'error' for example in examples))},
            'selection_rule': {'salt': SALT, 'calibration_per_label': calibration_per_label,
                               'evaluation_per_label': evaluation_per_label,
                               'group_normalization': 'Unicode NFC, collapse all whitespace, no case folding',
                               'ordering': 'SHA-256 salt:group:group-hash; then salt:record:ID; calibration allocated first',
                               'reservation': 'All siblings of a selected group are excluded from the other split',
                               'within_split': 'At most one solution per normalized problem group',
                               'status': 'Our adapted subsets, not official benchmark splits'},
            'splits': selections, 'problem_group_overlap': 0,
            'interface': {'messages': 'One user message; no system message; numbered paragraph tags start at zero',
                          'template_redistributed': False, 'source_data_redistributed': False,
                          'official_prediction': 'Last boxed substring converted with Python int; no range or finish-reason filter',
                          'strict_index_valid': 'Separate diagnostic: integer -1 or index within available steps; not a completion check',
                          'undefined_aggregate': 'Null for an empty class; zero for zero-sum accuracies, an explicit upstream deviation'},
            'execution_status': 'No model calls, generated responses, or measured model performance',
            'limitations': ['Character and UTF-8 byte counts exclude chat-template tokens and do not prove context fit.',
                            'Exact tokenizer and hardware preflight remain required before inference.',
                            'Text-normalized groups do not guarantee semantic or paraphrase disjointness.',
                            'This subset preparation does not reproduce the full published evaluation.']}


def prepare(data_path, prompt_path, provenance_path, out, calibration_per_label=10, evaluation_per_label=20):
    examples, template, provenance, hashes = load_inputs(data_path, prompt_path, provenance_path)
    manifest = make_manifest(examples, template, provenance, hashes, calibration_per_label, evaluation_per_label)
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'selection.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='Local pinned gsm8k.json')
    parser.add_argument('--prompt', type=Path, required=True, help='Local pinned critique_template.txt')
    parser.add_argument('--provenance', type=Path, required=True, help='Pinned source revisions and file hashes')
    parser.add_argument('--out', type=Path, required=True, help='Output directory for selection.json; existing manifests are not overwritten')
    parser.add_argument('--calibration-per-label', type=int, default=10)
    parser.add_argument('--evaluation-per-label', type=int, default=20)
    args = parser.parse_args()
    manifest = prepare(args.data, args.prompt, args.provenance, args.out,
                       args.calibration_per_label, args.evaluation_per_label)
    print(json.dumps({'out': str(args.out / 'selection.json'), 'population': manifest['population'],
                      'selection_counts': {name: split['count'] for name, split in manifest['splits'].items()},
                      'problem_group_overlap': manifest['problem_group_overlap'],
                      'execution_status': manifest['execution_status']}, indent=2))


if __name__ == '__main__':
    main()
