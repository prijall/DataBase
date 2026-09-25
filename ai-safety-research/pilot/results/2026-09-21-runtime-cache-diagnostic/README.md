# Cache-disabled runtime diagnostic: loading still crossed the guards

September 21, 2026. **Closed after non-generating preflight; zero new completions.** Code and prospective protocol were frozen at `22083d1`. The independently reviewed implementation passed 137 offline tests. Research ran alongside the usual office workload without changing office applications or services.

## Result

The temporary service explicitly set `LLAMA_ARG_CACHE_RAM=0`; the backend log confirmed that the separate prompt-state RAM cache was disabled. It reported a 2,048-token context and a separate 224 MiB active KV buffer. This demonstrates observed uptake of the setting, not successful preflight or improved model quality.

The first render-only request loaded the existing Llama 3.2 3B model. The immediate resource check recorded pressure level **2** and **19% free memory**, compared with pre-load pressure **1** and **43% free memory**. Swap usage and swapouts did not grow against baseline. Both the pressure and free-memory guards failed. Execution stopped before render validation, exact tokenization, idle-state verification or any of the four planned one-token generation requests. No retry or benchmark operation followed.

The preparation stage stopped 5.57 seconds after its pre-load baseline, or 31.64 seconds after controller service startup. Independent cleanup was observed 70.57 seconds after startup: pressure level **1**, **39% free memory**, no owned processes, and closed ports 11434, 11435 and 63712. The owned service group 50944 reported successful requested cleanup. No research files were persisted on the M4; records stayed on the controller.

## Counts and interpretation

| Operation | Count |
| --- | ---: |
| Non-generating debug/render requests | 1 |
| Completed exact prompt token checks | 0 |
| Planned synthetic generation requests | 4 |
| Attempted synthetic generation requests | 0 |
| New generated completions | 0 |
| Historical generated completions, unchanged | 240 |

Disabling this cache was **insufficient to admit this particular load under the observed office workload**. Concurrent office activity is uncontrolled. This is not proof that caching caused earlier pressure, a matched comparison against the earlier run, or evidence of general hardware incapacity. No scientific accuracy result was produced. Both failed ProcessBench calibration reservations remain closed; all forty evaluation cases are untouched.

The current decision is to defer further M4 loading and larger-model trials under these conditions and continue the [offline task-matched design](../../../TASK_MATCHED_DESIGN_DRAFT.md), literature comparison and human review. The closed diagnostic authorizes no retry.

## Evidence

- [Preflight](preflight.json), [durable preparation record](preparation.json), [readiness](readiness.json), [cleanup](cleanup.json) and [summary](SUMMARY.json).
- [Frozen inputs and code bindings](manifest.json), [service lifecycle](service-lifecycle.json) and [exact runtime log excerpts](runtime-observations.json). The full controller log is retained outside Git; its SHA-256 binds the published excerpts.
- [Prospective protocol](../../RUNTIME_CACHE_DIAGNOSTIC_PROTOCOL.md), [source audit](../../RUNTIME_MEMORY_AUDIT_2026-09-21.md) and [offline implementation review](../../RUNTIME_CACHE_IMPLEMENTATION_REVIEW.md).

The summary and extracted log records were constructed after the run from preserved evidence. No subject journal, responses or generation streams exist because the run phase was never entered. `SHA256SUMS` covers the published archive; no earlier result records or scores were replaced.
