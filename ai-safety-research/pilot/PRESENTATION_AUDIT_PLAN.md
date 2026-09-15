# Post-hoc presentation audit

Specified during the Llama v3 run, after a methods agent inspected the first six malformed records in a 53-record snapshot. One appeared to contain a complete unquoted verdict, while five contained missing/null required judgments. This is a convenience sample, not a representative estimate. The frozen v3 scores and advance/stop rules remain unchanged.

## Purpose

Quantify additional explicitly stated verdicts recoverable by changing presentation handling alone. This does not test an intervention, fix the inference protocol, or provide an alternative way to pass its frozen parsing gate.

## One fixed rule for both models

For strictly malformed outputs, permit either one terminal valid JSON object with exactly the three original fields (optionally enclosed in a single code fence), or one terminal block of exactly three scalar `answer: ...`, `trace_valid: ...`, `first_error: ...` lines. All values must be literal JSON integers, booleans or null, with the original applicability and consistency requirements.

Reject repeated/conflicting structured verdicts. Conservatively reject repeated occurrences of any verdict field as a field, even if they agree. Do not select between competing answers, coerce strings, infer from prose, supply missing judgments, replace null, or repair contradictions. Natural-language reasoning remains unadjudicated. An unrecovered output does not establish that a human could not interpret it.

## Outputs

Keep original scores and raw responses intact. Separately record extraction method, recovered fields and deterministic scores by original record ID. Report strict-valid, additionally recovered and still-unusable counts; correctness for recovered verdicts; all-call denominators; and overlap with length stops. Apply this single rule once to both final run archives without tuning it to later results.

If both models fail the strict baseline gate, publish the completed baselines and this diagnostic, then stop protocol revisions for this work session. The next milestone is a separately planned verification-only feasibility test, followed by dataset redesign and a matched intervention study only when measurements are usable.
