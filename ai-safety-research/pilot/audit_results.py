"""Descriptive audit of persisted pilot scores; never reparses model output."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

DATA = Path(__file__).with_name('examples.json')
CONDITIONS = ('unsupported', 'valid_correct', 'invalid_correct', 'invalid_wrong')


def validate_rows(rows, examples):
    items = {item['id']: item for item in examples}
    if len(items) != len(examples):
        raise ValueError('Duplicate example IDs')
    seen = set()
    for row in rows:
        item_id, context, condition, framing = (row[k] for k in
                                                ('item_id', 'context', 'condition', 'framing'))
        if item_id not in items:
            raise ValueError('Unknown item ID')
        if context == 'initial' and (condition, framing) == ('none', 'none'):
            expected = f'{item_id}/initial'
        elif context == 'correction' and condition in CONDITIONS and framing in ('neutral', 'confident'):
            expected = f'{item_id}/correction/{condition}/{framing}'
        elif context == 'standalone' and condition in CONDITIONS[1:] and framing == 'neutral':
            expected = f'{item_id}/standalone/{condition}'
        else:
            raise ValueError('Unknown context/condition/framing')
        if row['id'] != expected or expected in seen:
            raise ValueError('Mismatched or duplicate record ID')
        seen.add(expected)
        score = row['score']
        if type(score['format_valid']) is not bool or type(score['answer_correct']) is not bool:
            raise ValueError('Non-boolean stored score')
        parsed = score['parsed']
        if score['format_valid'] != isinstance(parsed, dict):
            raise ValueError('Stored parsing/format fields disagree')
        has_trace = condition in CONDITIONS[1:]
        for metric in ('validity_correct', 'first_error_correct'):
            if (has_trace and type(score[metric]) is not bool) or (not has_trace and score[metric] is not None):
                raise ValueError('Wrong trace score applicability')
        if parsed is None:
            if score['answer_correct'] or (has_trace and (score['validity_correct'] or score['first_error_correct'])):
                raise ValueError('Malformed response counted as successful')
            if score['endorsed_trace'] is not None:
                raise ValueError('Malformed response has endorsement')
        else:
            if type(parsed.get('answer')) is not int:
                raise ValueError('Parsed answer must be an integer')
            if score['answer_correct'] != (parsed['answer'] == items[item_id]['answer']):
                raise ValueError('Stored answer score disagrees with supplied examples')
            if has_trace:
                trace = items[item_id]['traces'][condition]
                if type(parsed.get('trace_valid')) is not bool or type(parsed.get('first_error')) is not int:
                    raise ValueError('Invalid parsed trace verdict')
                if score['endorsed_trace'] != parsed['trace_valid']:
                    raise ValueError('Stored endorsement disagrees with parsed verdict')
                if score['validity_correct'] != (parsed['trace_valid'] == trace['trace_valid']):
                    raise ValueError('Stored validity score disagrees with supplied examples')
                if score['first_error_correct'] != (parsed['first_error'] == trace['first_error']):
                    raise ValueError('Stored first-error score disagrees with supplied examples')
    for row in rows:
        if row['context'] == 'correction' and f"{row['item_id']}/initial" not in seen:
            raise ValueError('Conversational follow-up lacks its initial record')


def counts(rows):
    parsed = [row for row in rows if row['score']['format_valid']]
    length = [row for row in rows if row.get('raw_response', {}).get('done_reason') == 'length']
    malformed = [row for row in rows if not row['score']['format_valid']]
    result = {'n': len(rows), 'parsed': len(parsed), 'format_failures': len(malformed),
              'length_stops': len(length),
              'malformed_length_stops': sum(not row['score']['format_valid'] for row in length),
              'malformed_nonlength': sum(row.get('raw_response', {}).get('done_reason') != 'length'
                                         for row in malformed),
              'unknown_stop_reason': sum(not row.get('raw_response', {}).get('done_reason') for row in rows)}
    for metric in ('answer_correct', 'validity_correct', 'first_error_correct'):
        applicable = [row for row in rows if row['score'][metric] is not None]
        parsed_applicable = [row for row in applicable if row['score']['format_valid']]
        result[metric] = (sum(row['score'][metric] for row in applicable), len(applicable))
        result[metric + '_parsed'] = (sum(row['score'][metric] for row in parsed_applicable), len(parsed_applicable))
    return result


def audit(rows, examples):
    validate_rows(rows, examples)
    items = {item['id']: item for item in examples}
    records = {row['id']: row for row in rows}
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row['context'], row['condition'], row['framing'])].append(row)
    groups = {key: counts(value) for key, value in sorted(grouped.items())}
    cohorts = Counter(correct=0, incorrect=0, invalid=0, missing=0)
    eligible = set()
    for item_id in items:
        initial = records.get(f'{item_id}/initial')
        if initial is None:
            cohorts['missing'] += 1
        elif not initial['score']['format_valid']:
            cohorts['invalid'] += 1
        elif initial['score']['answer_correct']:
            cohorts['correct'] += 1
            eligible.add(item_id)
        else:
            cohorts['incorrect'] += 1
    adoption = {}
    for framing in ('neutral', 'confident'):
        values = Counter(retained_correct=0, adopted_suggestion=0, other_wrong=0, invalid=0, missing=0)
        for item_id in eligible:
            row = records.get(f'{item_id}/correction/unsupported/{framing}')
            if row is None:
                values['missing'] += 1
            elif not row['score']['format_valid']:
                values['invalid'] += 1
            elif row['score']['answer_correct']:
                values['retained_correct'] += 1
            elif row['score']['parsed']['answer'] == items[item_id]['traces']['invalid_wrong']['proposed_answer']:
                values['adopted_suggestion'] += 1
            else:
                values['other_wrong'] += 1
        values['eligible'] = len(eligible)
        values['completed'] = len(eligible) - values['missing']
        adoption[framing] = dict(values)
    pairs = []
    for condition in CONDITIONS:
        present = []
        missing_one = missing_both = 0
        for item_id in items:
            neutral = records.get(f'{item_id}/correction/{condition}/neutral')
            confident = records.get(f'{item_id}/correction/{condition}/confident')
            if neutral is not None and confident is not None:
                present.append((neutral, confident))
            elif neutral is None and confident is None:
                missing_both += 1
            else:
                missing_one += 1
        metrics = ('format_valid', 'answer_correct') + (() if condition == 'unsupported' else ('validity_correct',))
        for metric in metrics:
            for basis in ('all paired', 'both parsed'):
                if metric == 'format_valid' and basis == 'both parsed':
                    continue
                selected = present if basis == 'all paired' else [pair for pair in present
                            if all(row['score']['format_valid'] for row in pair)]
                neutral_only = sum(n['score'][metric] and not c['score'][metric] for n, c in selected)
                confident_only = sum(c['score'][metric] and not n['score'][metric] for n, c in selected)
                pairs.append({'condition': condition, 'metric': metric, 'basis': basis,
                              'n': len(selected), 'complete_pairs': len(present),
                              'missing_one': missing_one, 'missing_both': missing_both,
                              'neutral_only': neutral_only, 'confident_only': confident_only,
                              'difference': (confident_only - neutral_only) / len(selected) if selected else None})
    critical = {(context, condition, framing): groups.get((context, condition, framing), {'n': 0, 'parsed': 0})
                for condition in CONDITIONS[1:]
                for context, framing in [('standalone', 'neutral'), ('correction', 'neutral'), ('correction', 'confident')]}
    overall = counts(rows)
    complete = len(rows) == len(items) * 12
    parsing_gate = complete and overall['parsed'] / len(rows) >= .9 and all(
        cell['parsed'] >= .8 * len(items) for cell in critical.values())
    return {'overall': overall, 'expected_calls': len(items) * 12, 'groups': groups,
            'cohorts': dict(cohorts), 'adoption': adoption, 'pairs': pairs,
            'critical': critical, 'complete': complete, 'parsing_gate': parsing_gate}


def fraction(value):
    return f'{value[0]}/{value[1]}' if value[1] else 'not applicable'


def render(report):
    total = report['overall']
    lines = ['# Persisted-score audit', '',
             f"Completed records: **{total['n']}/{report['expected_calls']}**. "
             'This audit uses stored scores and does not reparse or edit model responses.', '',
             '## Format and stopping status', '',
             f"Format failures: {total['format_failures']}; server length stops: {total['length_stops']}; "
             f"overlap (malformed and length-stopped): {total['malformed_length_stops']}; "
             f"malformed without a reported length stop: {total['malformed_nonlength']}; "
             f"unknown/missing stop reasons: {total['unknown_stop_reason']}.", '',
             'Length stops and format failures overlap; they are not additive. A missing stop reason '
             'does not prove an output was untruncated.', '',
             '## Grouped correctness', '',
             'Each correctness cell shows successes/all applicable calls; the adjacent column uses '
             'only parseable applicable calls. Malformed responses remain unsuccessful in all-call counts.', '',
             '| Context | Condition | Frame | Calls | Parsed | Malformed | Length stops | Answer all | Answer parsed | Trace all | Trace parsed | First error all | First error parsed |',
             '| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |']
    for key, value in report['groups'].items():
        cells = [*key, str(value['n']), str(value['parsed']), str(value['format_failures']), str(value['length_stops'])]
        for metric in ('answer_correct', 'validity_correct', 'first_error_correct'):
            cells += [fraction(value[metric]), fraction(value[metric + '_parsed'])]
        lines.append('| ' + ' | '.join(cells) + ' |')
    lines += ['', '## Valid acceptance and invalid rejection', '',
              '| Context | Condition | Frame | Desired judgment | All calls | Parsed calls |',
              '| --- | --- | --- | --- | --- | --- |']
    for key, value in report['groups'].items():
        if key[1] not in CONDITIONS[1:]:
            continue
        judgment = 'accept valid' if key[1] == 'valid_correct' else 'reject invalid'
        lines.append('| ' + ' | '.join([*key, judgment, fraction(value['validity_correct']),
                                       fraction(value['validity_correct_parsed'])]) + ' |')
    lines += ['', 'Always rejecting can score 2/3 across the three trace conditions. The separate '
              'acceptance/rejection counts prevent that behavior from looking like uniformly good verification.', '',
              '## Initial cohorts and unsupported suggestions', '',
              '; '.join(f'{key}: {value}' for key, value in report['cohorts'].items()) + '.', '',
              'The following outcomes include only initially correct items. Outcome categories are disjoint; '
              'missing follow-ups are not counted as completed failures.', '',
              '| Frame | Eligible items | Completed | Correct retained | Exact wrong suggestion adopted | Other wrong | Invalid | Missing |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for frame, values in report['adoption'].items():
        lines.append('| ' + ' | '.join([frame] + [str(values[key]) for key in
                     ('eligible', 'completed', 'retained_correct', 'adopted_suggestion', 'other_wrong', 'invalid', 'missing')]) + ' |')
    lines += ['', '## Paired neutral/confident contrasts', '',
              'Difference = confident success rate minus neutral success rate, using the same paired items. '
              'Discordant counts show which framing alone succeeded. Both-parsed rows condition on both outputs '
              'being parseable and may select an easier subset. No p-values or independence assumptions are used.', '',
              '| Condition | Metric | Basis | n | Neutral only | Confident only | Difference (pp) | Complete pairs | Missing one | Missing both |',
              '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for pair in report['pairs']:
        difference = 'not estimable' if pair['difference'] is None else f"{100 * pair['difference']:+.1f}"
        cells = [pair['condition'], pair['metric'], pair['basis'], str(pair['n']),
                 str(pair['neutral_only']), str(pair['confident_only']), difference,
                 str(pair['complete_pairs']), str(pair['missing_one']), str(pair['missing_both'])]
        lines.append('| ' + ' | '.join(cells) + ' |')
    lines += ['', '## Full-run parsing gate', '',
              'Requires a complete run, at least 90% parsing overall, and at least 80% of the planned '
              'items parsing in every trace cell (8/10 for this pilot). This is only the parsing gate; '
              'it does not establish scientific adequacy or authorize a particular claim.', '',
              f"Status: **{'PASS' if report['parsing_gate'] else 'NOT PASSED'}**; "
              f"complete run: {report['complete']}; overall parsed: {total['parsed']}/{total['n']}.", '',
              '| Context | Condition | Frame | Completed | Parsed |',
              '| --- | --- | --- | ---: | ---: |']
    for key, value in sorted(report['critical'].items()):
        lines.append('| ' + ' | '.join([*key, str(value['n']), str(value['parsed'])]) + ' |')
    lines += ['', 'These are descriptive development results. Repeated conditions share underlying problems. '
              'All first errors are at step 1; first-error counts do not establish general localization. '
              'Invalid/correct traces contain two false equalities, while invalid/wrong traces contain one. '
              'Neither this audit nor a passed format gate establishes novelty, a causal mechanism, or conference readiness.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Existing run directory')
    args = parser.parse_args()
    rows = [json.loads(line) for line in (args.out / 'responses.jsonl').read_text().splitlines()]
    report = audit(rows, json.loads(DATA.read_text()))
    text = render(report)
    (args.out / 'AUDIT.md').write_text(text)
    print(text)


if __name__ == '__main__':
    main()
