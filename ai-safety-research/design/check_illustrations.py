"""Check four exposed development illustrations with exact sequential arithmetic.

Executor: researcher on the controller. Standard library only; no model, network,
expression evaluation, benchmark scoring, or changes to frozen pilot artifacts.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SYMBOLS = {'add': '+', 'subtract': '−', 'multiply': '×', 'exact_divide': '÷'}
EXAMPLE_KEYS = {'id', 'question', 'initial', 'operations', 'final_truth',
                'correct_proposal', 'false_proposal', 'evidence_equalities'}


def exact_fields(value, keys, location):
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(location + ': missing or unknown fields')


def integer(value, location):
    if type(value) is not int:
        raise ValueError(location + ': require an integer, excluding Boolean values')
    return value


def operation(left, name, right):
    """Interpret a fixed operation name, never source text or Python eval."""
    left = Fraction(integer(left, 'left operand'))
    right = Fraction(integer(right, 'right operand'))
    if type(name) is not str or name not in SYMBOLS:
        raise ValueError('Unknown operation')
    if name == 'add':
        value = left + right
    elif name == 'subtract':
        value = left - right
    elif name == 'multiply':
        value = left * right
    else:
        if not right:
            raise ValueError('Division by zero')
        value = left / right
    if value.denominator != 1:
        raise ValueError('Operation gives a noninteger intermediate')
    return value.numerator


def check_example(example):
    exact_fields(example, EXAMPLE_KEYS, 'example')
    for name in ('id', 'question'):
        if type(example[name]) is not str or not example[name].strip():
            raise ValueError(name + ': require a nonempty string')
    state = integer(example['initial'], 'initial')
    for name in ('final_truth', 'correct_proposal', 'false_proposal'):
        integer(example[name], name)
    steps, equalities = example['operations'], example['evidence_equalities']
    if not isinstance(steps, list) or len(steps) != 2:
        raise ValueError('Require the two sequential operations of each illustration')
    if not isinstance(equalities, list) or len(equalities) != len(steps):
        raise ValueError('Require one evidence equality per operation')
    computed, rendered, sequence = [], [], []
    for index, (step, evidence) in enumerate(zip(steps, equalities), 1):
        exact_fields(step, {'operation', 'operand', 'expected'}, 'operation ' + str(index))
        integer(step['operand'], 'operation operand')
        integer(step['expected'], 'expected intermediate')
        result = operation(state, step['operation'], step['operand'])
        if result != step['expected']:
            raise ValueError('Intermediate mismatch at step ' + str(index))
        exact_fields(evidence, {'left', 'operation', 'right', 'equals'}, 'evidence ' + str(index))
        for name in ('left', 'right', 'equals'):
            integer(evidence[name], 'evidence ' + name)
        # Arithmetic truth alone is insufficient: evidence must follow these
        # operands and this exact operation order, with no substituted steps.
        evidence_result = operation(evidence['left'], evidence['operation'], evidence['right'])
        if evidence_result != evidence['equals']:
            raise ValueError('False evidence equality at step ' + str(index))
        if (evidence['left'] != state or evidence['operation'] != step['operation']
                or evidence['right'] != step['operand'] or evidence['equals'] != result):
            raise ValueError('Evidence differs from sequential specification at step ' + str(index))
        rendered.append(f"{state} {SYMBOLS[step['operation']]} {step['operand']} = {result}")
        sequence.append(f"{step['operation']} {step['operand']}")
        computed.append(result)
        state = result
    if state != example['final_truth']:
        raise ValueError('Final truth differs from computed result')
    if example['correct_proposal'] != state:
        raise ValueError('Correct proposal differs from truth')
    if example['false_proposal'] == state:
        raise ValueError('False proposal equals truth')
    return {'id': example['id'], 'question': example['question'],
            'formal_sequence': 'start ' + str(example['initial']) + '; ' + '; '.join(sequence),
            'computed_intermediates': computed, 'computed_final': state,
            'correct_proposal': example['correct_proposal'], 'false_proposal': example['false_proposal'],
            'checked_evidence': rendered, 'arithmetic_valid': True}


def check_document(document):
    exact_fields(document, {'schema', 'status', 'human_review', 'source', 'examples'}, 'document')
    required = {'schema': 'task-matched-illustrations-v1', 'status': 'exposed_development_illustrations',
                'human_review': 'pending', 'source': '../TASK_MATCHED_DESIGN_DRAFT.md'}
    if any(document[name] != value for name, value in required.items()):
        raise ValueError('Illustration schema, exposure status, source, or review status changed')
    if not isinstance(document['examples'], list) or len(document['examples']) != 4:
        raise ValueError('This artifact contains exactly four development illustrations')
    rows = [check_example(example) for example in document['examples']]
    if len({row['id'] for row in rows}) != 4:
        raise ValueError('Duplicate illustration IDs')
    return {'schema': 'task-matched-illustration-audit-v1', 'status': 'arithmetic_checks_passed',
            'example_count': 4, 'exposure': 'development_only_not_held_out',
            'human_review': 'pending', 'model_calls': 0,
            'scope': 'Structured arithmetic and evidence only; prose interpretation and study design need human review.',
            'examples': rows}


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_audit(path):
    raw = path.read_bytes()
    document = json.loads(raw, object_pairs_hook=unique_keys)
    audit = check_document(document)
    audit['input_sha256'] = hashlib.sha256(raw).hexdigest()
    audit['checker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    audit['source_draft_sha256'] = hashlib.sha256((ROOT / '../TASK_MATCHED_DESIGN_DRAFT.md').read_bytes()).hexdigest()
    return audit


def review_sheet(audit):
    lines = ['# Four development illustrations: arithmetic review', '',
             '**Exposed development examples; human review pending.** No model calls, held-out examples, or capability result.', '',
             'Exact sequential arithmetic and evidence equalities passed. The checker does not establish that the prose matches the intended task or that the research design is valid.', '',
             'Full equality sequences below are ground-truth audit material, not six-cell follow-up stimuli. The revised design separates first-intermediate information from final-answer disclosure.', '']
    for row in audit['examples']:
        lines += ['## ' + row['id'], '', row['question'], '',
                  '- Formal order: `' + row['formal_sequence'] + '`.',
                  '- Computed intermediate values: ' + ', '.join(map(str, row['computed_intermediates'])) + '.',
                  '- Final truth / correct proposal: **' + str(row['computed_final']) + '**.',
                  '- Predefined false proposal: **' + str(row['false_proposal']) + '**.',
                  '- Checked evidence: `' + '; '.join(row['checked_evidence']) + '`.', '',
                  '- [ ] Human: prose and formal operation order agree.',
                  '- [ ] Human: equality notation is clear and distractor is intentional.',
                  '- [ ] Human: answer-revealing evidence and false-proposal conflict are suitable for the intended question.', '']
    lines += ['## Provenance', '', 'Input SHA-256: `' + audit['input_sha256'] + '`', '',
              'Checker SHA-256: `' + audit['checker_sha256'] + '`', '',
              'Source draft SHA-256: `' + audit['source_draft_sha256'] + '`', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'illustrations.json')
    parser.add_argument('--format', choices=('json', 'markdown'), default='json', help='Stdout format when --out is absent')
    parser.add_argument('--out', type=Path, help='Explicit controller output directory for audit.json and REVIEW.md')
    args = parser.parse_args()
    audit = load_audit(args.input)
    encoded = json.dumps(audit, indent=2, ensure_ascii=False) + '\n'
    rendered = review_sheet(audit)
    if args.out is None:
        print(encoded if args.format == 'json' else rendered, end='')
    else:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / 'audit.json').write_text(encoded)
        (args.out / 'REVIEW.md').write_text(rendered)
        print(json.dumps({'examples_checked': 4, 'human_review': 'pending', 'out': str(args.out)}))


if __name__ == '__main__':
    main()
