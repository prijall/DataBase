# Smaller-context M4 run — partial calibration and resource stop

**The 2,048-token preflight passed; calibration stopped after six responses when kernel memory pressure became non-normal.** Four responses were usable and one was correct. The archive total is now **240 generated responses**. Evaluation was not attempted.

## Frozen session and successful preflight

The [prospective session record](../../processbench/SMALL_CONTEXT_SESSION_2026-09-21.md) was committed at `5d73d858be2e7069a9881f5c6299371b87e9af31`, before model loading. It uses the reviewed `small-context-v1` profile, installed Llama-3.2 3B Q4_K_M, 2,048 context, unchanged 1,024-token output allowance, and the [fresh calibration manifest](../../processbench/selection-small-context.json). The original forty evaluation records were preserved.

The [preflight](preflight.json) passed all sixty exact prompt checks. Input counts were 290–789; the largest input plus the full output allowance was 1,813 tokens. The actual loaded context was 2,048. All 183 preflight resource observations passed: pressure stayed normal, free memory stayed at or above 26%, and neither swap usage nor cumulative swapouts grew. Preflight took 12.316 seconds and generated no subject answer. Its passed report did not guarantee sustained memory headroom during later generation.

## Six observed responses

| Case | Gold index | Extracted index | Output tokens | Fixed-rule outcome |
| --- | ---: | ---: | ---: | --- |
| gsm8k-63 | 2 | Missing | 313 | No boxed prediction; unusable |
| gsm8k-147 | 1 | 1 | 258 | Usable and correct |
| gsm8k-40 | 1 | 0 | 259 | Usable, incorrect index |
| gsm8k-143 | 1 | 0 | 485 | Usable, incorrect index |
| gsm8k-234 | -1 | 0 | 216 | Usable, incorrectly rejects valid solution |
| gsm8k-204 | -1 | Missing | 600 | No boxed prediction; unusable |

All six ended with normal server stops. None hit the output limit or had a transport error. Every observed prompt token count matched its preflight record. The two missing boxed predictions remain unusable; post-hoc interpretation does not replace the frozen extraction rule.

| Class | Attempted / planned | Usable | Exact matches / attempted |
| --- | --- | ---: | --- |
| Erroneous solution | 4/10 | 3 | 1/4 |
| Error-free solution | 2/10 | 1 | 0/2 |

Fourteen calibration cases remain unattempted, as do all forty evaluation cases. The observed-output class harmonic mean is 0% because both classes have observations and the error-free class has no match. This is a partial-output descriptive statistic, **not a completed benchmark score**. Missing cases are not observed wrong answers.

The actual stop reason was a resource guard. Separately, the fixed error-class gate was already unattainable: one success in four attempts leaves at most seven successes out of ten, even if the remaining six are all correct; eight are required. Completing or restarting this same cohort cannot rescue admission without prohibited retries, replacements or rule changes. This arithmetic does not establish general model incapacity.

## Resource stop and cleanup

After response six, kernel pressure was level 2 rather than normal level 1. Free memory was 22%, above its 20% cutoff, and neither swap usage nor cumulative swapouts had grown above the preload baseline. The triggering condition was pressure, not a length limit or a token mismatch. The runner stopped before request seven.

The owned service group 45071 was terminated. A separate [cleanup check](cleanup.json) verified ports 11435 and 61457 closed, the group absent and no owned processes. Pressure returned to normal with 42% free memory; substantial pre-existing swap remained. Research code and data traveled through SSH memory; no research files or artifacts were persisted on the M4 or its external SSD.

The two configured limits address different memory uses: the runtime reported a 224 MiB active KV buffer, while a separate prompt cache grew from zero to five saved prompts occupying 408.015 MiB, under an 8,192 MiB cache ceiling. [Filtered cache observations](runtime-cache-observations.json) preserve those log lines. Cache growth is a candidate for targeted runtime investigation, **not a causal attribution of system-wide pressure**; concurrent office workloads were not controlled.

## Timing and evidence

Six subject calls used 70.881 seconds of controller client time. The calibration loop lasted 117.996 seconds; it stopped 162.133 seconds after preflight budget start. Cleanup was checked 221.552 seconds after that start. Earlier service setup is excluded from these intervals. They are not isolated GPU timings.

- [Manifest](manifest.json), [journal](journal.jsonl), [responses](responses.jsonl), [raw streams](streams/).
- [Automatic summary](SUMMARY.md), [analysis](ANALYSIS.json), [session summary](session-summary.json).
- [Readiness](readiness.json), [service lifecycle](service-lifecycle.json), [independent review](INDEPENDENT_REVIEW.md), [checksums](SHA256SUMS).
- [Post-hoc qualitative output review](OUTPUT_REVIEW.md), separate from primary scoring.

## Decision

Close this bounded screen without evaluation or automatic retries. Preserve the six exposed calibration cases and all earlier failures. Review the outputs with the human researcher before selecting a different model/task or revising the research design; any future protocol must be prospective and must not present these observed cases as unseen. Investigate runtime memory/cache behavior separately with non-evaluation diagnostics before another benchmark run. A memory fix alone cannot change this cohort's failed admission arithmetic, and this run supplies no basis for starting the intended alignment intervention.
