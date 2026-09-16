# Verification-only development screen

Recorded responses: **30/30**. Gate: **NOT PASSED**. Complete run: True.

Lexical format accepts only VALID or INVALID, case-insensitively, with outer whitespace and at most one final period. A usable outcome additionally requires done=true, no server error, and done_reason=stop. Length-stopped labels are unsuccessful even if lexically valid.

Lexically valid: 30/30; usable: 30/30; reported length stops: 0; lexically valid length-stop overlap: 0; malformed length-stop overlap: 0; missing stop reasons: 0; execution failures: 0.

| Condition | Role | Recorded / planned | Completed | Lexically valid | Usable | Malformed | Length stops | Malformed + length | Correct / all recorded | Correct / usable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| valid_correct | primary: accept valid | 10/10 | 10/10 | 10/10 | 10/10 | 0/10 | 0/10 | 0/10 | 10/10 | 10/10 |
| invalid_wrong | primary: reject invalid | 10/10 | 10/10 | 10/10 | 10/10 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 |
| invalid_correct | secondary descriptive | 10/10 | 10/10 | 10/10 | 10/10 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 |

Primary comparison: 10/20 correct across recorded calls (20 planned: ten valid and ten invalid/wrong traces).

Primary balanced accuracy: **50.0%**; computed only for a complete run as the mean of valid acceptance and invalid/wrong rejection rates, each over ten planned items.

## Paired outcomes by underlying problem

Each row uses only complete recorded pairs; malformed and truncated outputs remain unsuccessful. Missing records are shown separately. These are related traces, not independent observations. Invalid-condition differences also confound error count.

| First condition | Second condition | Complete pairs | Both successful | Only first | Only second | Neither | Missing one | Missing both |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid_correct | invalid_wrong | 10 | 0 | 10 | 0 | 0 | 0 | 0 |
| invalid_wrong | invalid_correct | 10 | 0 | 0 | 0 | 10 | 0 | 0 |

Gate requires all thirty responses, at least 27 usable overall, at least 9 usable in each ten-item condition, at least 8/10 valid traces correctly accepted, and at least 8/10 invalid/wrong traces correctly rejected. Malformed, truncated, and failed outputs are unsuccessful, never omitted from the all-call denominator. Partial runs do not pass.

The thirty calls share ten development problems. Invalid/correct traces are secondary because their error count differs from invalid/wrong traces. All first errors occur at step one. This is a jointly changed protocol feasibility screen, not an isolated causal test against earlier protocols, a held-out benchmark, or an intervention result. Continue to the fixed thirty calls regardless of intermediate scores; do not add retries.
