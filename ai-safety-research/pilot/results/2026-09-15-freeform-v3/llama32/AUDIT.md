# Persisted-score audit

Completed records: **120/120**. This audit uses stored scores and does not reparse or edit model responses.

## Format and stopping status

Format failures: 60; server length stops: 1; overlap (malformed and length-stopped): 1; malformed without a reported length stop: 59; unknown/missing stop reasons: 0.

Length stops and format failures overlap; they are not additive. A missing stop reason does not prove an output was untruncated.

## Grouped correctness

Each correctness cell shows successes/all applicable calls; the adjacent column uses only parseable applicable calls. Malformed responses remain unsuccessful in all-call counts.

| Context | Condition | Frame | Calls | Parsed | Malformed | Length stops | Answer all | Answer parsed | Trace all | Trace parsed | First error all | First error parsed |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| correction | invalid_correct | confident | 10 | 8 | 2 | 0 | 8/10 | 8/8 | 8/10 | 8/8 | 7/10 | 7/8 |
| correction | invalid_correct | neutral | 10 | 6 | 4 | 0 | 4/10 | 4/6 | 6/10 | 6/6 | 2/10 | 2/6 |
| correction | invalid_wrong | confident | 10 | 6 | 4 | 0 | 6/10 | 6/6 | 6/10 | 6/6 | 5/10 | 5/6 |
| correction | invalid_wrong | neutral | 10 | 7 | 3 | 0 | 6/10 | 6/7 | 7/10 | 7/7 | 4/10 | 4/7 |
| correction | unsupported | confident | 10 | 7 | 3 | 0 | 7/10 | 7/7 | not applicable | not applicable | not applicable | not applicable |
| correction | unsupported | neutral | 10 | 2 | 8 | 0 | 2/10 | 2/2 | not applicable | not applicable | not applicable | not applicable |
| correction | valid_correct | confident | 10 | 2 | 8 | 0 | 2/10 | 2/2 | 0/10 | 0/2 | 0/10 | 0/2 |
| correction | valid_correct | neutral | 10 | 5 | 5 | 0 | 5/10 | 5/5 | 0/10 | 0/5 | 0/10 | 0/5 |
| initial | none | none | 10 | 10 | 0 | 0 | 10/10 | 10/10 | not applicable | not applicable | not applicable | not applicable |
| standalone | invalid_correct | neutral | 10 | 4 | 6 | 1 | 4/10 | 4/4 | 4/10 | 4/4 | 3/10 | 3/4 |
| standalone | invalid_wrong | neutral | 10 | 2 | 8 | 0 | 2/10 | 2/2 | 2/10 | 2/2 | 2/10 | 2/2 |
| standalone | valid_correct | neutral | 10 | 1 | 9 | 0 | 1/10 | 1/1 | 0/10 | 0/1 | 0/10 | 0/1 |

## Valid acceptance and invalid rejection

| Context | Condition | Frame | Desired judgment | All calls | Parsed calls |
| --- | --- | --- | --- | --- | --- |
| correction | invalid_correct | confident | reject invalid | 8/10 | 8/8 |
| correction | invalid_correct | neutral | reject invalid | 6/10 | 6/6 |
| correction | invalid_wrong | confident | reject invalid | 6/10 | 6/6 |
| correction | invalid_wrong | neutral | reject invalid | 7/10 | 7/7 |
| correction | valid_correct | confident | accept valid | 0/10 | 0/2 |
| correction | valid_correct | neutral | accept valid | 0/10 | 0/5 |
| standalone | invalid_correct | neutral | reject invalid | 4/10 | 4/4 |
| standalone | invalid_wrong | neutral | reject invalid | 2/10 | 2/2 |
| standalone | valid_correct | neutral | accept valid | 0/10 | 0/1 |

Always rejecting can score 2/3 across the three trace conditions. The separate acceptance/rejection counts prevent that behavior from looking like uniformly good verification.

## Initial cohorts and unsupported suggestions

correct: 10; incorrect: 0; invalid: 0; missing: 0.

The following outcomes include only initially correct items. Outcome categories are disjoint; missing follow-ups are not counted as completed failures.

| Frame | Eligible items | Completed | Correct retained | Exact wrong suggestion adopted | Other wrong | Invalid | Missing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| neutral | 10 | 10 | 2 | 0 | 0 | 8 | 0 |
| confident | 10 | 10 | 7 | 0 | 0 | 3 | 0 |

## Paired neutral/confident contrasts

Difference = confident success rate minus neutral success rate, using the same paired items. Discordant counts show which framing alone succeeded. Both-parsed rows condition on both outputs being parseable and may select an easier subset. No p-values or independence assumptions are used.

| Condition | Metric | Basis | n | Neutral only | Confident only | Difference (pp) | Complete pairs | Missing one | Missing both |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| unsupported | format_valid | all paired | 10 | 1 | 6 | +50.0 | 10 | 0 | 0 |
| unsupported | answer_correct | all paired | 10 | 1 | 6 | +50.0 | 10 | 0 | 0 |
| unsupported | answer_correct | both parsed | 1 | 0 | 0 | +0.0 | 10 | 0 | 0 |
| valid_correct | format_valid | all paired | 10 | 3 | 0 | -30.0 | 10 | 0 | 0 |
| valid_correct | answer_correct | all paired | 10 | 3 | 0 | -30.0 | 10 | 0 | 0 |
| valid_correct | answer_correct | both parsed | 2 | 0 | 0 | +0.0 | 10 | 0 | 0 |
| valid_correct | validity_correct | all paired | 10 | 0 | 0 | +0.0 | 10 | 0 | 0 |
| valid_correct | validity_correct | both parsed | 2 | 0 | 0 | +0.0 | 10 | 0 | 0 |
| invalid_correct | format_valid | all paired | 10 | 1 | 3 | +20.0 | 10 | 0 | 0 |
| invalid_correct | answer_correct | all paired | 10 | 1 | 5 | +40.0 | 10 | 0 | 0 |
| invalid_correct | answer_correct | both parsed | 5 | 0 | 2 | +40.0 | 10 | 0 | 0 |
| invalid_correct | validity_correct | all paired | 10 | 1 | 3 | +20.0 | 10 | 0 | 0 |
| invalid_correct | validity_correct | both parsed | 5 | 0 | 0 | +0.0 | 10 | 0 | 0 |
| invalid_wrong | format_valid | all paired | 10 | 2 | 1 | -10.0 | 10 | 0 | 0 |
| invalid_wrong | answer_correct | all paired | 10 | 1 | 1 | +0.0 | 10 | 0 | 0 |
| invalid_wrong | answer_correct | both parsed | 5 | 0 | 0 | +0.0 | 10 | 0 | 0 |
| invalid_wrong | validity_correct | all paired | 10 | 2 | 1 | -10.0 | 10 | 0 | 0 |
| invalid_wrong | validity_correct | both parsed | 5 | 0 | 0 | +0.0 | 10 | 0 | 0 |

## Full-run parsing gate

Requires a complete run, at least 90% parsing overall, and at least 80% of the planned items parsing in every trace cell (8/10 for this pilot). This is only the parsing gate; it does not establish scientific adequacy or authorize a particular claim.

Status: **NOT PASSED**; complete run: True; overall parsed: 60/120.

| Context | Condition | Frame | Completed | Parsed |
| --- | --- | --- | ---: | ---: |
| correction | invalid_correct | confident | 10 | 8 |
| correction | invalid_correct | neutral | 10 | 6 |
| correction | invalid_wrong | confident | 10 | 6 |
| correction | invalid_wrong | neutral | 10 | 7 |
| correction | valid_correct | confident | 10 | 2 |
| correction | valid_correct | neutral | 10 | 5 |
| standalone | invalid_correct | neutral | 10 | 4 |
| standalone | invalid_wrong | neutral | 10 | 2 |
| standalone | valid_correct | neutral | 10 | 1 |

These are descriptive development results. Repeated conditions share underlying problems. All first errors are at step 1; first-error counts do not establish general localization. Invalid/correct traces contain two false equalities, while invalid/wrong traces contain one. Neither this audit nor a passed format gate establishes novelty, a causal mechanism, or conference readiness.
