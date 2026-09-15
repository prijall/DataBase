# Post-hoc presentation-only audit

**Secondary diagnostic only. Original strict scores and frozen gate decisions remain primary and unchanged.**

This fixed rule was specified after inspecting the first six Llama format failures. It is applied identically to both models, without model-specific exceptions. It is not a preregistered scoring procedure and cannot retroactively pass the frozen gate.

Rule: `presentation-only-v1`. Input `responses.jsonl` SHA-256: `2238c6dfd7f6dcf7c7a60a61fafbbcfd97de0011fb42a8e441b811b328c9408c`.

## Recovery rule

Recover only a terminal JSON object with exactly the three original fields, optionally inside one JSON code fence, or three terminal scalar lines with unique lowercase `answer`, `trace_valid`, and `first_error` keys. Scalar values must already be literal JSON integers, booleans, or null. The original parser checks types, trace applicability, and verdict consistency. A verdict field appearing more than once anywhere in the output causes rejection. Escaped JSON key spellings anywhere in the output are conservatively rejected rather than decoded for recovery. Malformed delimiter-bearing responses, missing fields, trailing prose, quoted booleans, null repairs, and competing verdicts are not recovered. No answers are inferred from prose and no mathematical reasoning is corrected.

## Output usability and truncation

Completed responses inspected: **120**.

| Category | Responses | Reported length stops | Unknown stop reason |
| --- | ---: | ---: | ---: |
| strict-valid | 60 | 0 | 0 |
| additionally-recovered | 1 | 0 | 0 |
| still-unusable | 59 | 1 | 0 |

Categories are disjoint. Length stops overlap each category; a missing stop reason does not establish absence of truncation.

## Correctness of additionally recovered verdicts

Recovered-only rates condition on successful extraction and are selected descriptive diagnostics. All-response columns retain the original applicable denominator; additional recoveries do not replace the strict scores.

| Measure | Original strict correct / all applicable responses | Correct / applicable recovered verdicts | Correct recoveries / all applicable responses |
| --- | --- | --- | --- |
| answer_correct | 57/120 | 1/1 | 1/120 |
| validity_correct | 33/90 | 1/1 | 1/90 |
| first_error_correct | 23/90 | 0/1 | 0/90 |

## Extraction counts

| Method | Additional recoveries |
| --- | ---: |
| terminal-scalar-lines | 1 |

Recovery records in `PRESENTATION_RECOVERY.jsonl` retain each original ID and score. The separate `score` field is populated only for additionally recovered candidates. The raw response archive is never modified. This audit can separate some presentation failures from incorrect judgments; it does not establish a scientific effect, reasoning faithfulness, novelty, or conference readiness.
