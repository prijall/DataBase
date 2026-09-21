# M4 session 2 — exact-token preflight passed; calibration stopped early

**Two calibration responses recorded; the resource guard then stopped the session.** The total across development protocols is now 234 generated responses. Calibration is incomplete, and no evaluation response was requested.

## Prospective decision

The user authorized one bounded attempt after the first M4 memory failure. A fresh read-only [readiness observation](readiness.json) showed normal pressure and 46% reported free memory, compared with 36% before the previous failed load. The [second-session record](../../processbench/M4_SESSION_2_2026-09-21.md) was committed before model loading at `d2dd756ce237ab09f504db3f10173fd17040b5cc`. Selection, model, 8,192-token context, 1,024-token output allowance, scoring and resource limits were unchanged.

A controller launch initially failed because its local log directory did not exist; no SSH service or model request had started. Creating that controller directory allowed the same reviewed launcher to start. No research files were written on the M4 or its external SSD.

## Successful preflight

The [raw report](preflight.json) records all 60 prompt checks passing. Exact prompt lengths range from 308 to 778 tokens. Across 183 preflight resource samples, pressure stayed normal, reported free memory stayed at or above 20%, and neither swap usage nor cumulative swapouts grew. The preflight took 13.221 seconds and generated no subject answers. Unlike the earlier failures, it reached and checked the corrected debug-render response field and exact tokenizer interface.

This demonstrates context fit and resource fit during that preflight, not sustained resource sufficiency throughout generation. The subsequent subject runner checked the frozen report, model identities, runtime idleness and resources again.

## Partial calibration

| Case | Process label | Extracted index | Outcome |
| --- | --- | --- | --- |
| gsm8k-160 | Error at index 2 | 2 | Normal stop; usable and correct; 399 output tokens |
| gsm8k-109 | Error at index 1 | 1600000 | Length stop at 1,024 tokens; out-of-range extraction; unusable |

The observed prompt counts were 543 and 622, exactly matching their preflight records. Both responses have complete saved terminal events and no transport errors. The frozen last-boxed-integer extraction rule was retained. Neither output was retried or repaired for primary scoring.

After the second response, free memory was 19%, below the unchanged 20% minimum. Pressure remained normal and swap did not grow relative to this session's baseline. The runner stopped before a third request. These are system-wide observations and cannot isolate the effect of model computation from concurrent office workloads.

Only two erroneous-solution examples were attempted; no error-free example was attempted. **Balanced accuracy and the official-compatible harmonic mean are not estimable.** The calibration gate did not pass because the required cohort was not completed. One usable correct response does not establish a reliable verifier; the unusable response does not establish general incapacity. Planned-denominator coverage in the automatic summary must not be interpreted as eighteen observed wrong answers.

Original calibration: 2 used, 18 unattempted. Evaluation: all 40 unattempted. These two responses are development evidence and cannot be represented as unseen in a future configuration.

## Cleanup and timing

The owned service group 39222 was stopped. A separate [cleanup observation](cleanup.json) confirmed ports 11435, 58808 and 59236 closed, no owned processes, and group absence. Memory pressure was normal with 41% reported free memory. Existing swap remained elevated, without new growth during this run.

The two subject calls used 39.289 seconds of controller client time. The calibration loop lasted 54.711 seconds; its stop was 120.737 seconds after preflight budget start. Cleanup was checked 165.277 seconds after that start. These figures exclude earlier idle service setup and are not isolated GPU timing.

## Evidence and next configuration

- [Manifest](manifest.json), [journal](journal.jsonl), [responses](responses.jsonl), and [raw streams](streams/).
- [Automatic cohort summary](SUMMARY.md), [analysis](ANALYSIS.json), and [session summary](session-summary.json).
- [Service lifecycle](service-lifecycle.json), [independent review](INDEPENDENT_REVIEW.md), and [checksums](SHA256SUMS).

This session is closed. Do not restart the same 8,192-token configuration or resume its calibration under altered settings. The [prospective smaller-context plan](../../PROCESSBENCH_SMALL_CONTEXT_PLAN.md) considers 2,048 tokens: the observed maximum prompt plus the unchanged output allowance is 1,802 tokens. This arithmetic motivates a separate configuration; it does not replace a fresh target-specific render, token and resource preflight. A new disjoint calibration reservation must be frozen before its execution. The forty original evaluation cases remain protected by the unchanged calibration gate.
