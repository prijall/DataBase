# ProcessBench preflight: stopped before calibration

September 16, 2026. **Zero generated answers, zero calibration attempts and zero evaluation attempts.** The repository's subject/diagnostic completion count remains **232**. This is a failed runtime preflight, not a model-accuracy result.

## What happened

The reviewed local helper loaded the existing Llama-3.2 3B model with the planned 8,192-token context and issued one explicitly non-generating debug-render request. It then stopped because it looked for `debug_info` in the response; the actual pinned Ollama wire field is `_debug_info`. The request flag, `_debug_render_only`, was correct. The inspected server branch returns before generation. No tokenization request or subject-generation request followed.

This response-decoding mistake was missed by the earlier mock tests and AI review. The live check failed closed. The helper has since been corrected **offline**, with a source-faithful response fixture and an immediate post-load resource check before response parsing. The corrected helper has **not** been rerun against the model in this session.

A separate read-only inspection after the failed render check found non-normal memory pressure and additional swap activity beyond the prospective limits. The model subsequently unloaded through its existing 30-second keep-alive setting. The final check found no resident model and normal memory pressure; existing swap remained elevated. No service or other workload was killed.

## Resource evidence

| Observation | Pressure level | Reported memory free | Swap used (bytes) | Cumulative swapouts (bytes) |
| --- | ---: | ---: | ---: | ---: |
| Before model loading | 1 (normal) | 60% | 2,940,794,306 | 7,700,234,240 |
| Follow-up with model resident | 2 (non-normal) | 20% | 4,340,056,064 | 9,586,098,176 |
| Cleanup, no model resident | 1 (normal) | 71% | 4,180,672,512 | 9,586,098,176 |

The resident-model follow-up recorded **1.303 GiB more swap usage** and **1.756 GiB of additional swapouts** than baseline. These exceed the 256 MiB and 128 MiB growth limits. The 20% free reading was at, not below, the free-percentage threshold; pressure and swap growth independently disqualified continuation.

These are global shared-machine measurements observed around model loading. Concurrent office activity was not experimentally controlled, so we cannot attribute every byte of change solely to this model. They are sufficient to stop this session under the fixed resource policy, not to establish a universal hardware limit for all M1 machines or configurations.

The preserved preflight lasted **4.53 seconds**, including a **4.41-second debug-render request**. Cleanup was verified **95.26 seconds after preflight start**. These durations are not subject inference timings. Exact model residency between observations was not continuously measured.

## Coverage and scientific interpretation

| Stage | Completed / planned |
| --- | --- |
| Non-generating debug renders | 1 / 60 |
| Exact prompt tokenization | 0 / 60 |
| Calibration subject attempts | 0 / 20 |
| Evaluation subject attempts | 0 / 40 |

Exact context fit, calibration accuracy and evaluation accuracy are **not established**. The calibrated model-suitability gate was never reached. Do not call this a failed model-accuracy gate, treat missing responses as measured model errors, or count the render request as a generated completion.

No smaller-context or alternate-model run was attempted after the resource finding. The original calibration and evaluation reservations remain unused.

## Artifacts and provenance

- [preflight.json](preflight.json): original blocked report, exact source/model/binary identities, baseline and non-generating operation log.
- [executed_preflight.py](executed_preflight.py): exact pre-fix helper snapshot. Its SHA-256 matches `a61d5f80fdc8ee182243ed82397bc89774d9a91de8f0b1255b39238ce29762a5` in the report. This helper had been reviewed but was not yet committed when the non-generating check ran; no subject experiment preceded a frozen execution commit.
- [post-load-observation.json](post-load-observation.json): follow-up observation transcribed from the live tool response, explicitly labeled as such rather than presented as a helper-written log.
- [cleanup-check.json](cleanup-check.json): directly saved final resource and residency check.
- [SHA256SUMS](SHA256SUMS): archive integrity hashes.

The original report and cleanup files are copied byte-for-byte from the ignored run directory. The executed helper snapshot preserves the bug rather than rewriting history with corrected code. The current supported helper is [processbench_preflight.py](../../processbench_preflight.py); the archived snapshot is retained for audit, not recommended execution.

## Next decision

Keep subject inference stopped on this shared M1 configuration. Before another attempt, choose and document a resource-feasible setup: verify access to the user-reported 16GB M4, or separately plan a smaller context after exact tokenization can be established without repeating the disruptive load. Recheck resource availability and retain this failed preflight. Do not reset the session budget or relax resource limits merely to obtain results.

The original research question and novelty work remain open. This increment delivers a reviewed runner and a concrete resource limitation; it does not add an alignment finding.
