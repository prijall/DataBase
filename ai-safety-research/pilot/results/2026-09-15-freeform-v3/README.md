# Freeform v3 development results

**Outcome:** 130 local calls completed. Llama completed its 120-call baseline but failed the full-run parsing gate. Qwen stopped after ten initial calls because it failed the initial gate. No intervention or activation-steering experiment ran.

These are development measurements on ten reused arithmetic problems. They establish limitations of this tested interface, not a general alignment effect or a conference-ready contribution. The [working manuscript](../../../paper/manuscript.md) incorporates the verified results.

## Main results

| Model | Calls | Strictly parseable | Correct initial answers / initial calls | Length stops | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Llama 3.2 3B | 120/120 | 60/120 | 10/10 | 1 | Full baseline completed; parsing gate failed |
| Qwen3-VL 2B Instruct, text only | 10/120 | 2/10 | 2/10 | 3 | Initial gate failed; remaining 110 calls not run |

Qwen's two correct answers were its only parseable answers. The other eight belong to the malformed cohort, not the naturally wrong cohort. All four length stops across models also produced malformed outputs; they are not additional format failures.

### Llama answer and trace judgments

| Measure | Successes / all applicable calls | Successes / parseable applicable calls |
| --- | ---: | ---: |
| Answer correct | 57/120 | 57/60 |
| Trace judgment correct | 33/90 | 33/41 |
| First-error index correct | 23/90 | 23/41 |
| Valid trace accepted | 0/30 | 0/8 |
| Invalid trace rejected | 33/60 | 33/33 |

Every one of the 41 parseable trace verdicts rejected the trace. Thus strong rejection among parsed invalid traces coexists with zero acceptance among parsed valid traces. The combined trace score must not be presented as uniformly useful verification. All injected first errors are at step one, so the localization count does not establish general localization ability.

All ten initial Llama answers were correct, leaving natural correction acceptance **not estimable**. For unsupported wrong suggestions, neutral framing yielded two correct and eight malformed responses; confident framing yielded seven correct and three malformed responses. None of the nine parseable responses adopted the suggested wrong answer. Eleven malformed responses prevent an overall resistance claim. Only one item had both unsupported-framing outputs parseable; paired conditional comparisons are correspondingly limited.

## Separate post-hoc presentation audit

The [fixed recovery rule](../../PRESENTATION_AUDIT_PLAN.md) was specified after inspecting six early Llama failures. It recovers explicit terminal fields only, with no inferred judgments or repairs. It leaves the frozen strict scores and gate decisions unchanged.

| Model | Strict-valid | Additional recoveries | Still unusable |
| --- | ---: | ---: | ---: |
| Llama | 60 | 1 | 59 |
| Qwen | 2 | 0 | 8 |

The single recovered Llama verdict gives the correct answer and rejects the invalid trace, but identifies step two rather than the true first error at step one. This narrow audit does not show that every remaining response is human-uninterpretable.

## Methods and provenance

The [v3 protocol](../../PROTOCOL_V3.md) was committed before inference. It changes the system prompt, available freeform calculations, delimiters and output allowance together relative to earlier screens; no single-factor causal attribution is possible. Both models used the same unchanged runner, data, system prompt, seed and options. Model digests, quantization, templates, server version and code commits are in the manifests. Llama was run first, then Qwen, on the shared local machine.

An independent code-review agent reproduced every raw score and planned prompt, checked code/data/system hashes and compared archived files byte for byte with their source runs. AI review does not substitute for independent human validation. The runner and two analysis modules passed 32 regression tests. No model download or hosted experimental inference was used; Claude assisted with methods review separately.

Recorded v3 client sessions total **1,505.20 seconds (25.09 minutes)**: Llama 1,423.19 seconds and Qwen 82.01 seconds. This excludes between-session idle time, model residency, development and hosted-assistant work. The earlier [42-call diagnostic screen](../2026-09-15-protocol-screen/README.md) is retained separately. Together, the repository records **172 experimental/diagnostic completions**.

## Reproduce and inspect

- Llama: [manifest](llama32/manifest.json), [raw responses](llama32/responses.jsonl), [strict summary](llama32/SUMMARY.md), [detailed audit](llama32/AUDIT.md), [presentation audit](llama32/PRESENTATION_AUDIT.md).
- Qwen: [manifest](qwen3vl/manifest.json), [raw responses](qwen3vl/responses.jsonl), [strict summary](qwen3vl/SUMMARY.md), [detailed audit](qwen3vl/AUDIT.md), [presentation audit](qwen3vl/PRESENTATION_AUDIT.md).
- [Analysis manifest](ANALYSIS_MANIFEST.json) records analysis versions and the tested environment. [Checksums](SHA256.json) cover archived artifacts; the checksum file excludes itself.
- [Pilot guide](../../README.md) contains commands. To reproduce an older run, use its recorded code commit and matching model/server identities; do not attempt to resume an archive using changed code.

## Next decision

Stop output-protocol revisions for this work session. Plan a small verification-only feasibility test that separates explicit trace judgments from answer generation. A usable interface, balanced error construction, calibrated difficulty, independent example review, held-out data and a matched intervention/control plan remain necessary before the intended intervention study. Novelty checks remain open. The manuscript records these development findings and limitations while that research continues.
