"""Offline replacement calibration; preserve the original evaluation reservation.

No network, model calls, response inspection, or prompt-length filtering.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path

import processbench_prepare as preparation

ROOT = Path(__file__).resolve().parent
ORIGINAL_SELECTION = ROOT / 'processbench' / 'selection.json'
ORIGINAL_SELECTION_SHA256 = '2fb187e84c18bf6587334d72853577b4a94569fe8ad42cab5d739670c433bab8'
SELECTION_VERSION = 'processbench-small-context-exclude-original-groups-v1'


def canonical_hash(value):
    return preparation.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8'))


def verified_original(examples, template, provenance, input_hashes):
    original_bytes = ORIGINAL_SELECTION.read_bytes()
    if preparation.sha256(original_bytes) != ORIGINAL_SELECTION_SHA256:
        raise ValueError('Original selection byte hash differs from pinned artifact')
    original = json.loads(original_bytes)
    expected = preparation.make_manifest(examples, template, provenance, input_hashes)
    if original != expected:
        raise ValueError('Original selection differs from pinned-source reconstruction')
    return original


def select_calibration(examples, excluded_groups):
    preparation.validate_examples(examples)
    groups = defaultdict(list)
    for example in examples:
        group = preparation.problem_group(example['problem'])
        if group not in excluded_groups:
            groups[group].append(example)
    selected, counts = [], Counter(valid=0, error=0)
    for group in sorted(groups, key=lambda value: (preparation.rank('group', value), value)):
        for example in sorted(groups[group],
                              key=lambda value: (preparation.rank('record', value['id']), value['id'])):
            category = 'valid' if example['label'] == -1 else 'error'
            if counts[category] < 10:
                selected.append(example)
                counts[category] += 1
                break  # One record per group, including mixed-label sibling groups.
        if counts['valid'] == counts['error'] == 10:
            break
    if counts['valid'] != 10 or counts['error'] != 10:
        raise ValueError('Remaining groups cannot fill fixed calibration quotas; no reselection')
    return selected


def summarize_selection(selected, template):
    records = []
    for example in selected:
        messages = preparation.render_messages(example, template)
        content = messages[0]['content']
        records.append({
            'id': example['id'], 'problem_group_sha256': preparation.problem_group(example['problem']),
            'gold_label': example['label'], 'label_class': 'valid' if example['label'] == -1 else 'error',
            'step_count': len(example['steps']), 'rendered_characters': len(content),
            'rendered_utf8_bytes': len(content.encode('utf-8')),
            'messages_sha256': canonical_hash(messages)})
    return {
        'records': records, 'count': len(records),
        'class_counts': dict(Counter(record['label_class'] for record in records)),
        'problem_group_count': len({record['problem_group_sha256'] for record in records}),
        'rendered_character_lengths': preparation.length_summary([row['rendered_characters'] for row in records]),
        'rendered_utf8_byte_lengths': preparation.length_summary([row['rendered_utf8_bytes'] for row in records])}


def make_manifest(examples, template, provenance, input_hashes):
    original = verified_original(examples, template, provenance, input_hashes)
    excluded = sorted({record['problem_group_sha256']
                       for split in ('calibration', 'evaluation')
                       for record in original['splits'][split]['records']})
    if len(excluded) != 60:
        raise ValueError('Expected 60 distinct original problem groups')
    calibration = summarize_selection(select_calibration(examples, set(excluded)), template)
    evaluation = deepcopy(original['splits']['evaluation'])
    if set(row['problem_group_sha256'] for row in calibration['records']) & set(excluded):
        raise ValueError('Original-group exclusion failed')
    return {
        'artifact_type': 'offline-selection-only', 'selection_version': SELECTION_VERSION,
        'code_sha256': preparation.sha256(Path(__file__).read_bytes()),
        'original_preparation_code_sha256': original['code_sha256'],
        'original_selection_sha256': ORIGINAL_SELECTION_SHA256,
        'source_provenance': provenance, 'input_sha256': input_hashes,
        'population': deepcopy(original['population']),
        'excluded_problem_groups': excluded,
        'selection_rule': {
            'salt': preparation.SALT, 'calibration_per_label': 10, 'evaluation_per_label': 20,
            'group_normalization': original['selection_rule']['group_normalization'],
            'ordering': 'Original group and record hash ranks; skip all original 60 groups; fill calibration quotas',
            'reservation': 'Exclude all siblings of all original calibration and evaluation groups from new calibration',
            'within_split': 'At most one solution per normalized problem group',
            'evaluation': 'Exact original evaluation split including record fields and order',
            'filtering': 'No model outcomes, prompt lengths, or alternative salts used for selection',
            'status': 'Our adapted subsets, not official benchmark splits'},
        'splits': {'calibration': calibration, 'evaluation': evaluation},
        'problem_group_overlap': 0, 'interface': deepcopy(original['interface']),
        'execution_status': 'Offline new reservation only; no new model calls or measured performance',
        'limitations': deepcopy(original['limitations'])}


def load_jobs(data_path, prompt_path, provenance_path, selection_path):
    examples, template, provenance, hashes = preparation.load_inputs(data_path, prompt_path, provenance_path)
    selection_bytes = selection_path.read_bytes()
    selection = json.loads(selection_bytes)
    if selection != make_manifest(examples, template, provenance, hashes):
        raise ValueError('Small-context selection differs from deterministic pinned-source reconstruction')
    indexed = {example['id']: example for example in examples}
    jobs = []
    for split in ('calibration', 'evaluation'):
        for entry in selection['splits'][split]['records']:
            example = indexed[entry['id']]
            messages = preparation.render_messages(example, template)
            if canonical_hash(messages) != entry['messages_sha256']:
                raise ValueError('Rendered message hash differs from selection')
            jobs.append({
                'id': example['id'], 'split': split, 'gold_label': example['label'],
                'step_count': len(example['steps']), 'messages': messages,
                'messages_sha256': entry['messages_sha256'],
                'problem_group_sha256': entry['problem_group_sha256']})
    return jobs, dict(hashes, selection=preparation.sha256(selection_bytes),
                      original_selection=ORIGINAL_SELECTION_SHA256)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('data', 'prompt', 'provenance', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    inputs = preparation.load_inputs(args.data, args.prompt, args.provenance)
    manifest = make_manifest(*inputs)
    # Never replace an earlier selection artifact silently.
    with args.out.open('x') as output:
        output.write(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'out': str(args.out), 'selection_version': SELECTION_VERSION,
                      'counts': {name: value['count'] for name, value in manifest['splits'].items()}}))


if __name__ == '__main__':
    main()
