# Independent review — smaller-context execution

September 21, 2026. **Preflight passed; calibration stopped after six responses because kernel memory pressure became non-normal.** The calibration is incomplete and evaluation remains unattempted. The recorded errors also make its fixed erroneous-class admission threshold unattainable. This review inspected saved controller evidence and performed offline recomputation only; it made no hardware connections, model requests or execution-code changes.

## Configuration and preflight

The manifest records execution commit `5d73d858be2e7069a9881f5c6299371b87e9af31`. Reviewed execution sources, profile, selection and plan match that freeze. The saved transport binding agrees with the supplied source/worker hashes. Reconstructing the new sixty jobs from the pinned source reproduces the IDs, class labels, messages and message hashes. The original forty evaluation cases remain unchanged.

The model is the pinned Llama-3.2 3B Q4_K_M on Ollama 0.34.0. Both requested options and the resident-model evidence specify **2,048 context tokens**, with a **1,024-token output allowance**. The preflight has sixty corresponding token records ranging from **290 to 789**; the largest prompt plus output reserve is **1,813**. The actual resident context also remains 2,048 at every recorded pre-subject idle check.

All 308 preflight operations were received, including sixty debug-only requests and sixty tokenizer requests. All 183 resource observations passed the unchanged guards: normal pressure throughout, minimum free memory 26%, and no positive swap-usage or swapout growth. The preflight lasted **12.316 seconds** and ended with idle confirmation. Its SHA-256 is `5cf8cf02cf41b3e414f1afd586abdc2fc91e592972ace3c99252df3806b3e29d`.

## Response and score recomputation

The journal contains exactly six unique attempts, in the first six positions of the frozen calibration order, each with one finished record. All raw stream hashes, response hashes, concatenated contents, terminal events, expected/observed prompt counts and saved scores pass recomputation. Independent last-boxed-integer extraction agrees with the frozen parser. Recomputing the full analysis produces exactly the saved `ANALYSIS.json`.

| Case | Gold | Extracted index | Output tokens | Prompt tokens | Usable | Exact match |
|---|---:|---:|---:|---:|---|---|
| `gsm8k-63` | 2 | missing | 313 | 495 | no | no |
| `gsm8k-147` | 1 | 1 | 258 | 300 | yes | yes |
| `gsm8k-40` | 1 | 0 | 259 | 403 | yes | no |
| `gsm8k-143` | 1 | 0 | 485 | 656 | yes | no |
| `gsm8k-234` | −1 | 0 | 216 | 350 | yes | no |
| `gsm8k-204` | −1 | missing | 600 | 789 | no | no |

All six terminal responses report normal stop. There are **four usable outputs, one exact match, two missing boxed-integer extractions, zero out-of-range indices, zero length stops and zero transport errors**. No prose extraction or semantic repair was applied.

The erroneous-solution class has four recorded cases, three usable outputs and one match; the error-free class has two recorded cases, one usable output and no matches. Fourteen calibration cases remain missing. The saved observed-output harmonic mean of 0% summarizes this unbalanced six-case prefix only; it is not a completed calibration or evaluation score. The forty unused evaluation cases are not model errors.

Even if all six remaining erroneous-solution cases matched, this class could reach only **7/10**, below the required **8/10**. Thus completing the cohort cannot rescue admission under the frozen rules. This is gate arithmetic from recorded outcomes, distinct from the actual resource-triggered stop and from a general accuracy estimate.

## Resource stop and cleanup

Immediately after response six, pressure was **level 2** while free memory was **22%**, with no swap growth. Recomputed guard violations match the journal: the pressure condition alone triggered the stop. There is no seventh attempt.

Subject client elapsed time totals **70.881 seconds**; server-reported durations total **56.825 seconds**. Calibration stopped **162.133 seconds after preflight start**. Requested STOP ended the owned service group. A separate cleanup observation **221.552 seconds after preflight start** confirms ports 11435 and 61457 closed, no owned processes, group absence, normal pressure and 42% free memory.

The service log contains 126 successful `/api/chat` HTTP requests, consistent with sixty initial debug requests, sixty repeated verification debug requests and six subjects. Only the six subjects add to the historical response count, bringing it from 234 to **240**.

## Archive and runtime-cache evidence

All fourteen copied primary artifacts—readiness, preflight, cleanup, manifest, journal, responses, analysis, summary and six raw streams—are byte-identical to the controller originals. Published lifecycle records and full-log hash agree with the raw log. All nine extracted cache-observation lines and their line numbers also match it exactly.

The log reports a 224 MiB KV buffer, an 8,192 MiB prompt-cache limit, and cache occupancy reaching **408.015 MiB across five saved prompts**. The latter is an occupancy observation; the limit is not evidence that 8 GiB was allocated. Cache growth is a possible contributor worth investigating, but this shared-machine run does not isolate its effect on pressure. Fixing runtime memory behavior would not reopen the already-unattainable adequacy gate.

These findings close this bounded screen with preserved evidence. They do not establish an alignment effect, a causal comparison with the earlier context size, or conference-ready model-performance results. All six attempted cases are now development observations; the evaluation reservation remains untouched.
