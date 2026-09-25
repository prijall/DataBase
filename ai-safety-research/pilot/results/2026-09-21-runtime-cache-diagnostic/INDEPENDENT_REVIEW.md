# Independent outcome review — cache-disabled diagnostic

September 21, 2026. **Closed after a failed non-generating preflight; zero generation attempts.** This review used saved controller evidence only, without hardware connections, model calls or execution-code changes.

## Verified evidence

- Archived preflight, preparation, readiness and cleanup files are byte-identical to their controller originals. Eight execution/protocol files match frozen commit `22083d1`. The complete transport binding, worker/source hashes, launcher hash and four synthetic job hashes recompute correctly. The jobs contain no benchmark material or gold labels.
- The raw log contains exactly one `/api/chat` request, consistent with the reviewed render-only path. The report records six received metadata/debug operations, zero generation requests and no completed token checks. There is no run-start marker, subject journal, response file, generation stream or cache-uptake admission file in either run or archive. No retry is evidenced.
- Every published lifecycle event and runtime excerpt matches the original log; its SHA-256 agrees across the manifest and extracts. The log explicitly reports disabled prompt-state caching, context 2,048 and a separate **224 MiB active KV buffer**. These are post-hoc runtime observations, not a passed preflight or proof of token fit. Loading includes ordinary runtime warmup; zero subject generation does not mean zero model computation.

## Resource failure and cleanup

The pre-load baseline was pressure **1**, free memory **43%**. Immediately after the debug request, pressure was **2** and free memory **19%**. Recomputed violations match the saved stop reason: both pressure and free-memory limits failed. Swap usage and cumulative swapouts were unchanged at every recorded preflight observation.

The debug request lasted **5.403 seconds**. Preflight stopped **5.570 seconds after its baseline**, or **31.636 seconds after service startup**. The separate cleanup observation occurred **70.574 seconds after startup**, within the 600-second envelope. It records pressure 1, 39% free memory, no owned processes, owned-group absence, and closed ports 11434, 11435 and 63712. The service lifecycle separately records requested STOP and successful cleanup of group 50944.

## Interpretation

The setting demonstrably reached the backend, but it did not make this particular load pass the unchanged guards under the observed shared workload. This is neither a matched causal test of cache memory nor evidence of general hardware incapacity or model accuracy. No generation performance was measured. All four planned synthetic requests remained unattempted; the historical completion total stays **240**. The benchmark calibrations and forty unused evaluation cases remain unchanged. This closed diagnostic authorizes no retry.
