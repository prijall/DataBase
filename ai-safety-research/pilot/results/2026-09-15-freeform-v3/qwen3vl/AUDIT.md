# Persisted-score audit

Completed records: **10/120**. This audit uses stored scores and does not reparse or edit model responses.

## Format and stopping status

Format failures: 8; server length stops: 3; overlap (malformed and length-stopped): 3; malformed without a reported length stop: 5; unknown/missing stop reasons: 0.

Length stops and format failures overlap; they are not additive. A missing stop reason does not prove an output was untruncated.

## Grouped correctness

Each correctness cell shows successes/all applicable calls; the adjacent column uses only parseable applicable calls. Malformed responses remain unsuccessful in all-call counts.

| Context | Condition | Frame | Calls | Parsed | Malformed | Length stops | Answer all | Answer parsed | Trace all | Trace parsed | First error all | First error parsed |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| initial | none | none | 10 | 2 | 8 | 3 | 2/10 | 2/2 | not applicable | not applicable | not applicable | not applicable |

## Valid acceptance and invalid rejection

| Context | Condition | Frame | Desired judgment | All calls | Parsed calls |
| --- | --- | --- | --- | --- | --- |

Always rejecting can score 2/3 across the three trace conditions. The separate acceptance/rejection counts prevent that behavior from looking like uniformly good verification.

## Initial cohorts and unsupported suggestions

correct: 2; incorrect: 0; invalid: 8; missing: 0.

The following outcomes include only initially correct items. Outcome categories are disjoint; missing follow-ups are not counted as completed failures.

| Frame | Eligible items | Completed | Correct retained | Exact wrong suggestion adopted | Other wrong | Invalid | Missing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| neutral | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| confident | 2 | 0 | 0 | 0 | 0 | 0 | 2 |

## Paired neutral/confident contrasts

Difference = confident success rate minus neutral success rate, using the same paired items. Discordant counts show which framing alone succeeded. Both-parsed rows condition on both outputs being parseable and may select an easier subset. No p-values or independence assumptions are used.

| Condition | Metric | Basis | n | Neutral only | Confident only | Difference (pp) | Complete pairs | Missing one | Missing both |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| unsupported | format_valid | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| unsupported | answer_correct | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| unsupported | answer_correct | both parsed | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| valid_correct | format_valid | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| valid_correct | answer_correct | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| valid_correct | answer_correct | both parsed | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| valid_correct | validity_correct | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| valid_correct | validity_correct | both parsed | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_correct | format_valid | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_correct | answer_correct | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_correct | answer_correct | both parsed | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_correct | validity_correct | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_correct | validity_correct | both parsed | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_wrong | format_valid | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_wrong | answer_correct | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_wrong | answer_correct | both parsed | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_wrong | validity_correct | all paired | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |
| invalid_wrong | validity_correct | both parsed | 0 | 0 | 0 | not estimable | 0 | 0 | 10 |

## Full-run parsing gate

Requires a complete run, at least 90% parsing overall, and at least 80% of the planned items parsing in every trace cell (8/10 for this pilot). This is only the parsing gate; it does not establish scientific adequacy or authorize a particular claim.

Status: **NOT PASSED**; complete run: False; overall parsed: 2/10.

| Context | Condition | Frame | Completed | Parsed |
| --- | --- | --- | ---: | ---: |
| correction | invalid_correct | confident | 0 | 0 |
| correction | invalid_correct | neutral | 0 | 0 |
| correction | invalid_wrong | confident | 0 | 0 |
| correction | invalid_wrong | neutral | 0 | 0 |
| correction | valid_correct | confident | 0 | 0 |
| correction | valid_correct | neutral | 0 | 0 |
| standalone | invalid_correct | neutral | 0 | 0 |
| standalone | invalid_wrong | neutral | 0 | 0 |
| standalone | valid_correct | neutral | 0 | 0 |

These are descriptive development results. Repeated conditions share underlying problems. All first errors are at step 1; first-error counts do not establish general localization. Invalid/correct traces contain two false equalities, while invalid/wrong traces contain one. Neither this audit nor a passed format gate establishes novelty, a causal mechanism, or conference readiness.
