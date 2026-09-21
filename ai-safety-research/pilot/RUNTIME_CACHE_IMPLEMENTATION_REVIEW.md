# Independent runtime-cache diagnostic implementation review

September 21, 2026. **Offline review passed; this document reports no live execution.** The reviewer made no hardware connections or model requests. Only this review document was added; execution code was not edited by the reviewer.

## Reviewed scope and controls

- The [diagnostic protocol](RUNTIME_CACHE_DIAGNOSTIC_PROTOCOL.md) is implemented as a separate controller and named worker profile. Inputs are exactly four fixed synthetic list-completion prompts, without benchmark content or gold labels. The controller exposes no call-count or generation-length override. Requests use context 2,048 and `num_predict=1`; received output counts outside zero to one are rejected and stop further calls.
- The worker validates the complete four-job list, including message hashes, and binds the diagnostic purpose, schema and `benchmark_admission: false`. The diagnostic profile cannot use the benchmark job loader and is absent from the benchmark CLI's profile choices. It has no accuracy scorer or evaluation-admission path.
- Exclusive, flushed and fsynced preparation/run markers precede their remote actions. Each subject attempt is journaled before dispatch. A second invocation is refused; interrupted attempts are reported separately from recorded and unattempted requests. Partial raw streams are preserved, and cancellation uncertainty remains explicit.
- The original model, template, parameter and bundled binary/library checks are retained. Actual resident context must equal 2,048. Before each request the controller refreshes full identity, verifies the backend belongs to the logged owned service, records that evidence, and checks the unchanged resource limits against the original pre-load baseline.
- `--cache-ram-mib 0` is the only supported cache override. It affects the owned service's environment and emits only allowlisted environment evidence. Generation requires the backend's explicit cache-disabled initialization message, with no contradictory cache-enabled message. Missing or ambiguous uptake evidence blocks the diagnostic.
- The diagnostic budget begins at controller service startup. Its owned-service watchdog initiates shutdown twelve seconds before the 600-second boundary to reserve cleanup time. Worker and SSH preflight caps also shrink with remaining service time. Each generation retains the 90/95/100-second HTTP/worker/SSH ceilings and a fresh 150-second reserve check after admission operations. STOP, EOF, signals and watchdog cleanup target only the owned process group. Cleanup still needs independent live verification.

## Validation

The complete offline suite passed **137 tests**, including the forty targeted transport, service and diagnostic tests. Tests cover four-call maximum, no replay, non-benchmark inputs, profile separation, resource stops, interrupted-attempt counts, backend ownership, expired service budget, durable preparation failure and cache-uptake admission. `git diff --check` passed.

Additional independent checks confirmed that a diagnostic preflight's worker alarm and SSH cap shorten as the service budget is consumed. These checks used local mocked dispatch/processes and made no network requests.

The original preparation code, benchmark runner, preflight helper, resource helper and both selection artifacts are byte-identical to commit `5d73d858be2e7069a9881f5c6299371b87e9af31`. Existing benchmark profiles retain their 8,192/2,048 context settings and 1,024-token output allowance. The default service path retains its prior environment behavior and 5,400-second watchdog; the cache-disabled diagnostic path has the separate 600-second envelope.

## Remaining live checks and limits

Freeze the reviewed implementation, tests and protocol before execution. A fresh diagnostic preflight must establish actual context, exact token counts, model identity, cache-setting uptake and resource headroom under the current office workload. Any failure ends this diagnostic without retry or benchmark access. Preserve the owned-service termination and independent port/process/resource observations afterward.

Even four successful one-token requests would establish only this tiny workload's behavior. They would not demonstrate long-output feasibility, prove that caching caused earlier pressure, improve the closed calibration scores, or authorize evaluation. Historical benchmark evidence and admission thresholds remain unchanged.
