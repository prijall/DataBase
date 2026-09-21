# Bounded cache-disabled runtime diagnostic

September 21, 2026. Prospective engineering protocol, frozen in Git before execution. This is not a benchmark, a calibration retry, or an alignment experiment.

## Decision and scope

Research must coexist with the usual office workload. The user explicitly declined a quiet-machine window. Do not close office applications, clear caches, reboot, change office services, download models, or relax resource limits. Defer larger installed models. One diagnostic may test the source-supported `LLAMA_ARG_CACHE_RAM=0` setting on the existing Llama 3.2 3B runtime. The [source audit](RUNTIME_MEMORY_AUDIT_2026-09-21.md) documents its meaning and limits.

The two ProcessBench calibrations remain closed, with their original scores, gates and reservations unchanged. All forty evaluation cases remain untouched. Runtime success does not authorize a new scientific run.

## Fixed configuration and inputs

- Use the previously verified M4, existing Ollama 0.34.0 binary, Llama manifest `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`, and existing pinned template/tokenizer/binary checks.
- Owned temporary service on localhost port 11435 only; separate prompt-state RAM cache explicitly disabled in that service's environment. Preserve active KV representation. No persistent remote research files: supply code through SSH and store evidence only on the controller for GitHub.
- Diagnostic profile `runtime-cache-diagnostic-v1`: context 2,048, temperature zero, seed 42, two threads, **at most one output token per request**. No accuracy objective or gold labels. Four fixed, newly authored neutral synthetic inputs are defined and hashed by the reviewed implementation. No benchmark material or office data.
- Freeze this protocol, implementation, synthetic inputs, tests and source hashes before execution. Do not change or retry the configuration after seeing outcomes.

## Admission and bounded execution

1. Obtain a fresh pre-load resource baseline; require no competing resident model and the original admission checks. Keep pressure level 1, free memory at least 20%, swap-used growth at most 256 MiB and additional swapouts at most 128 MiB relative to baseline. Stop on any violation or uncertain transport state.
2. Record an exclusive durable dispatch marker before the non-generating preflight. Verify exact rendering/tokenization for the four synthetic inputs, pinned runtime identity, actual context, idle state and resources. Render-only requests are not generated completions and are counted separately.
3. Verify the service's allowlisted environment record and backend initialization message explicitly report disabled prompt-state caching. An absent or ambiguous signal stops the diagnostic before generation. Never dump full environments.
4. Only after those checks, issue at most four sequential requests, once each. Journal each attempt durably before its RPC; preserve raw output and before/after resources. Verify output-token ceiling and exact prompt counts. No automatic retry or resume, no scoring, no admission to evaluation.
5. Bound owned service lifetime to ten minutes, including loading and cleanup, with a hard watchdog and a 150-second reserve before generation. Use the existing 90-second HTTP, 95-second worker and 100-second SSH request ceilings or stricter remaining-budget limits. Stop promptly once finished or blocked.
6. Terminate only the owned process group, then independently verify its absence, closed service/backend ports and current resources. Publish cleanup evidence, including any uncertainty or failure. Leave no research runner scheduled or active.

## Interpretation and reporting

A completed check establishes that this particular configuration was applied and this tiny workload stayed within the guards. It does not establish that cache growth caused earlier pressure, that a twenty-case or long-output run fits, or that reasoning improved. The archived default-cache run is not a matched control. Office activity is uncontrolled, and disabling saved states need not preserve bit-identical outputs.

Count actual generated diagnostic completions separately from the 240 historical completions, including partial or failed requests transparently. Archive source/code/protocol hashes, preflight, journal, raw responses, allowlisted lifecycle/cache observations and cleanup. Update the research state and manuscript with operational findings only. The next scientific work remains an offline task-matched design and human review, followed by a separate prospective decision.
