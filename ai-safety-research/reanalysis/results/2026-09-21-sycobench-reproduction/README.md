# SycoBench-600 published-log reproduction

September 21, 2026. **Stage 1 passed.** All **133 numeric cells**, including **42 confidence-interval endpoints**, match the pinned published table within the prespecified tolerance. All **35 displayed cells** in the manuscript's main table also match by model and column. This reproduces calculations on the author's released outputs; it does not repeat model generation or establish a new research contribution.

## Result and population

| Check | Observed result |
| --- | --- |
| Frozen implementation/protocol | `b4e0a27cd9d1575e572f1184c513eade2bb8bd0a` |
| Release files verified | 25; byte size, Git blob identity and SHA-256 recorded |
| Source logs | Seven models; 12,465 question–variant records before intersection |
| Common population | 555 question IDs × three variants = 1,665 records per model |
| Numeric comparison | 133/133 pass; maximum absolute difference `2.220446049250313e-16` |
| Confidence intervals | 42/42 endpoints pass; 2,000 replicates, fixed seeds 0/1/2 |
| Undefined bootstrap replicates | Zero across the 21 metric/model calculations |
| Main manuscript table | 35/35 displayed cells match |
| Stored parser/correctness/prompt consistency | No discrepancies; no incomplete variant sets |
| Original validation report | Exact match, including the known 45 missing Mistral IDs |
| New model requests | Zero; historical local completions remain 240 |

Six logs contain 600 IDs and 1,800 records; the Mistral log contains 555 IDs and 1,665 records. Intersection filtering preserves original record order and yields 11,655 retained question–variant records across models. Each record contains baseline and follow-up fields; these counts are not counts of independent questions or newly generated responses.

## Correction denominators

Both the exported `nW_eff` and the actual flag-defined correction denominator agree for every retained model cohort. The source-code distinction identified before execution therefore does not produce a denominator discrepancy in this table.

| Model | Baseline correct (`nC`) | Baseline wrong (`nW`) | Eligible corrections / exported `nW_eff` |
| --- | ---: | ---: | ---: |
| Claude-3.5-Haiku | 1,214 | 451 | 451 |
| Claude-Sonnet-4 | 1,546 | 119 | 107 |
| Gemini-2.5-Flash | 1,587 | 78 | 78 |
| GPT-4o | 1,387 | 278 | 278 |
| GPT-4o-mini | 1,317 | 348 | 348 |
| Llama-4-Maverick | 1,127 | 538 | 371 |
| Mistral-7B | 1,053 | 612 | 594 |

The reproduced rates and intervals are in [main_results.csv](main_results.csv). This table remains the original measurement: a noncorrect pressure response need not adopt the suggested answer, and correction outcomes are conditional on available follow-ups.

## Provenance limitation

All seven logs record historical question-file SHA-256 `3c2d71f250f32b9f5f8885d2881439605460a3dd84713b9fdfe122c2bb5078f5`, while the released question file hashes to `ae41f4b94ac46fb0109778546a091534208881cf74eea87c43ce24736bb8dd4d`. The pinned runner hashes raw file bytes; no historical byte snapshot was recovered. The discrepancy is disclosed, not normalized away.

Independent checks found agreement of the released question labels/metadata, prompts, stored parses and correctness fields. This establishes consistency of the present artifacts, not recovery of the historical dataset or human verification of every gold answer. `clean_reproduction: true` means the frozen numerical and consistency checks passed **with this explicitly permitted provenance qualification**.

The [source audit](../../SOURCE_METHODS_AUDIT.md) also records less precise manuscript wording around unavailable versus unparseable corrections, repeated stems across ID clusters, and the original metric definitions. These limitations are substantially acknowledged by the source authors; they are not claimed as new discoveries.

## Measured cost and verification

The analysis used **8.427 seconds wall time**, **8.335 seconds CPU time** and **313.203 MiB peak resident memory** on the controller. The external wrapper finished in 8.561 seconds under a 600-second limit, exit code zero. Wall time includes Git metadata waits; CPU and peak memory describe the Python process and exclude Git subprocess usage. Downloads, development and review time are excluded. No M4 connection, model loading or office-application changes occurred.

Before execution, 20 synthetic unit tests passed, alongside an independent 72-comparison bootstrap check and manuscript alignment/mismatch checks. The [implementation review](../../INDEPENDENT_REVIEW.md) predates the run. No source, protocol, parser, cohort or tolerance was changed after observing this run.

## Evidence

- [Independent result review](INDEPENDENT_REVIEW.md).
- [Acceptance protocol](../../REPRODUCTION_PROTOCOL.md), [adapter](../../reproduce.py), [tests](../../test_reproduce.py).
- [Every numeric/display comparison](comparison.json), [population and denominators](analysis.json), [validation audit](validation.json), [status](status.json).
- [Source/code/protocol hashes](provenance.json), [measured runtime](runtime.json), [bounded execution record](execution.json).

## Next decision

Stage 1 is complete. Before computing any alternative result, review the closest measurement literature and freeze one focused sensitivity question, its estimand, populations, missing-output rules and uncertainty procedure. A candidate is separating explicit adoption of the suggested wrong choice from other noncorrect or unparseable answers on the fixed official baseline-correct cohort. Its novelty remains unverified. No alternative parser, adoption-rate calculation, ranking comparison or stem-cluster sensitivity was run here.

## Attribution

Source: Debu Sinha, *SycoBench-600: Measuring Sycophancy and Correction Selectivity in LLM Assistants*, [Findings of ACL 2026](https://aclanthology.org/2026.findings-acl.1759/), [release v1.0.0](https://github.com/debu-sinha/sycobench-600/releases/tag/v1.0.0), commit `5193ce408bd73b401c4c5911f490e2bbad84a082`. Released data and derived tables are [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); upstream code is MIT licensed ([notice](../../UPSTREAM_LICENSE.txt)). Changes: independent standard-library reconstruction, provenance/consistency checks and derived reports. No author endorsement is implied. Raw logs are not redistributed here.
