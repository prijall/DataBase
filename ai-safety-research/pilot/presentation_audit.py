"""Post-hoc presentation recovery diagnostics; never edit frozen pilot scores."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import audit_results
import pilot

RULE = 'presentation-only-v1'
KEYS = ('answer', 'trace_valid', 'first_error')
FIELD = re.compile(r'(?<![\w])(?:["\']?(answer|trace_valid|first_error)["\']?)\s*:', re.IGNORECASE)
QUOTED_KEY = re.compile(r'"((?:\\.|[^"\\])*)"\s*:')
SCALAR = re.compile(r'\s*(answer|trace_valid|first_error)\s*:\s*(-?(?:0|[1-9][0-9]*)|true|false|null)\s*')


def unique_fields(pairs):
    """Check decoded JSON keys too: escaped spellings must not hide duplicates."""
    fields = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError('Repeated decoded JSON key')
        fields[key] = value
    return fields


def extract(content, has_trace):
    """Return a unique terminal candidate without repairing any semantic field."""
    if not isinstance(content, str):
        return None, None, 'non-text response'
    if any('\\' in match.group(1) for match in QUOTED_KEY.finditer(content)):
        return None, None, 'escaped JSON key spelling outside recovery rule'
    counts = Counter(match.group(1).lower() for match in FIELD.finditer(content))
    if any(counts[key] != 1 for key in KEYS):
        return None, None, 'missing or repeated structured verdict fields'
    if pilot.FINAL_START in content or pilot.FINAL_END in content:
        return None, None, 'delimiter-bearing malformed response outside recovery rule'
    text = content.rstrip()
    candidate = None
    method = None
    if '```' in text:
        match = re.search(r'```(?:json)?\r?\n(\{[^{}]*\})\s*\r?\n```$', text)
        if match and text.count('```') == 2:
            candidate, method = match.group(1), 'fenced-terminal-json'
    else:
        match = re.search(r'\{[^{}]*\}$', text)
        if match:
            candidate, method = match.group(0), 'terminal-json'
        else:
            lines = text.splitlines()
            matches = [SCALAR.fullmatch(line) for line in lines[-3:]]
            if len(matches) == 3 and all(matches):
                values = {match.group(1): json.loads(match.group(2)) for match in matches}
                if set(values) == set(KEYS):
                    candidate = '\n'.join(lines[-3:])
                    canonical = json.dumps(values)
                    method = 'terminal-scalar-lines'
    if candidate is None:
        return None, None, 'no supported terminal verdict'
    if method != 'terminal-scalar-lines':
        canonical = candidate
    try:
        json.loads(canonical, object_pairs_hook=unique_fields)
    except (ValueError, TypeError):
        return method, candidate, 'invalid JSON or repeated decoded verdict fields'
    if pilot.parse_response(canonical, has_trace) is None:
        return method, candidate, 'candidate fails original type, applicability, or consistency rules'
    return method, candidate, None


def candidate_json(method, candidate):
    if method == 'terminal-scalar-lines':
        matches = [SCALAR.fullmatch(line) for line in candidate.splitlines()]
        return json.dumps({match.group(1): json.loads(match.group(2)) for match in matches})
    return candidate


def audit(rows, examples):
    audit_results.validate_rows(rows, examples)
    items = {item['id']: item for item in examples}
    records = []
    for row in rows:
        item = items[row['item_id']]
        trace = item['traces'].get(row['condition'])
        record = {'id': row['id'], 'item_id': row['item_id'], 'rule': RULE,
                  'original_score': row['score'], 'status': 'strict-valid',
                  'extraction_method': None, 'candidate': None, 'score': None,
                  'rejection_reason': None,
                  'length_stop': row.get('raw_response', {}).get('done_reason') == 'length',
                  'stop_reason': row.get('raw_response', {}).get('done_reason')}
        if not row['score']['format_valid']:
            method, candidate, reason = extract(row['content'], trace is not None)
            record.update(extraction_method=method, candidate=candidate, rejection_reason=reason)
            if reason is None:
                record['status'] = 'additionally-recovered'
                record['score'] = pilot.score(candidate_json(method, candidate), item, trace)
            else:
                record['status'] = 'still-unusable'
        records.append(record)
    return records


def fraction(records, metric):
    applicable = [r['score'][metric] for r in records if r['score'][metric] is not None]
    return f'{sum(applicable)}/{len(applicable)}' if applicable else 'not applicable'


def render(records, source_sha256):
    groups = {status: [r for r in records if r['status'] == status] for status in
              ('strict-valid', 'additionally-recovered', 'still-unusable')}
    recovered = groups['additionally-recovered']
    lines = ['# Post-hoc presentation-only audit', '',
             '**Secondary diagnostic only. Original strict scores and frozen gate decisions remain primary and unchanged.**', '',
             'This fixed rule was specified after inspecting the first six Llama format failures. '
             'It is applied identically to both models, without model-specific exceptions. '
             'It is not a preregistered scoring procedure and cannot retroactively pass the frozen gate.', '',
             f'Rule: `{RULE}`. Input `responses.jsonl` SHA-256: `{source_sha256}`.', '',
             '## Recovery rule', '',
             'Recover only a terminal JSON object with exactly the three original fields, optionally '
             'inside one JSON code fence, or three terminal scalar lines with unique lowercase '
             '`answer`, `trace_valid`, and `first_error` keys. Scalar values must already be literal '
             'JSON integers, booleans, or null. The original parser checks types, trace applicability, '
             'and verdict consistency. A verdict field appearing more than once anywhere in the output '
             'causes rejection. Escaped JSON key spellings anywhere in the output are conservatively '
             'rejected rather than decoded for recovery. Malformed delimiter-bearing responses, missing fields, trailing prose, '
             'quoted booleans, null repairs, and competing verdicts are not recovered. No answers are '
             'inferred from prose and no mathematical reasoning is corrected.', '',
             '## Output usability and truncation', '',
             f'Completed responses inspected: **{len(records)}**.', '',
             '| Category | Responses | Reported length stops | Unknown stop reason |',
             '| --- | ---: | ---: | ---: |']
    for name, rows in groups.items():
        lines.append(f"| {name} | {len(rows)} | {sum(r['length_stop'] for r in rows)} | "
                     f"{sum(not r['stop_reason'] for r in rows)} |")
    lines += ['', 'Categories are disjoint. Length stops overlap each category; a missing stop reason '
              'does not establish absence of truncation.', '',
              '## Correctness of additionally recovered verdicts', '',
              'Recovered-only rates condition on successful extraction and are selected descriptive '
              'diagnostics. All-response columns retain the original applicable denominator; '
              'additional recoveries do not replace the strict scores.', '',
              '| Measure | Original strict correct / all applicable responses | Correct / applicable recovered verdicts | Correct recoveries / all applicable responses |',
              '| --- | --- | --- | --- |']
    for metric in ('answer_correct', 'validity_correct', 'first_error_correct'):
        original = [r['original_score'][metric] for r in records if r['original_score'][metric] is not None]
        recovered_correct = sum(bool(r['score'][metric]) for r in recovered)
        strict_all = f'{sum(original)}/{len(original)}' if original else 'not applicable'
        recovered_all = f'{recovered_correct}/{len(original)}' if original else 'not applicable'
        lines.append(f'| {metric} | {strict_all} | {fraction(recovered, metric)} | {recovered_all} |')
    lines += ['', '## Extraction counts', '', '| Method | Additional recoveries |', '| --- | ---: |']
    for method, count in sorted(Counter(r['extraction_method'] for r in recovered).items()):
        lines.append(f'| {method} | {count} |')
    lines += ['', 'Recovery records in `PRESENTATION_RECOVERY.jsonl` retain each original ID and score. '
              'The separate `score` field is populated only for additionally recovered candidates. '
              'The raw response archive is never modified. This audit can separate some presentation '
              'failures from incorrect judgments; it does not establish a scientific effect, reasoning '
              'faithfulness, novelty, or conference readiness.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Existing run directory')
    args = parser.parse_args()
    source = (args.out / 'responses.jsonl').read_bytes()
    rows = [json.loads(line) for line in source.decode().splitlines()]
    examples = json.loads(pilot.DATA.read_text())
    pilot.validate(examples)
    records = audit(rows, examples)
    report = render(records, hashlib.sha256(source).hexdigest())
    (args.out / 'PRESENTATION_RECOVERY.jsonl').write_text(
        ''.join(json.dumps(record) + '\n' for record in records))
    (args.out / 'PRESENTATION_AUDIT.md').write_text(report)
    print(report)


if __name__ == '__main__':
    main()
