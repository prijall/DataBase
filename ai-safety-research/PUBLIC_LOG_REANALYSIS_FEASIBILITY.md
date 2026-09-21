# Public-log reanalysis: a route without model loading

September 21, 2026. **Artifact feasibility established for one log; scientific contribution unverified.** This is the next bounded offline work item. It uses published model responses, ordinary CPU computation and no inference API, M4 session, downloads of weights or office data.

## Question worth checking

How stable are reported comparisons when unsuccessful answer formatting, explicit adoption of a false suggestion, and unavailable correction responses are kept distinct on a fixed question population?

This is a proposed measurement audit. The source authors already document parser and denominator limitations and invite alternative analysis. Discovering that a stricter parser changes a number is not enough for a paper. A contribution would need a substantive, reproducible conclusion about measurement, robustness or interpretation that is not already established, plus a broader novelty check.

## Verified source and feasible inputs

Use **SycoBench-600 v1.0.0**, author repository `debu-sinha/sycobench-600`, commit **`5193ce408bd73b401c4c5911f490e2bbad84a082`**. The release identifies camera-ready logs for seven models. Its code is MIT; its dataset and response logs are CC BY 4.0. Attribution must identify Debu Sinha, the paper and release, preserve the license link, and describe derived changes. [Author release](https://github.com/debu-sinha/sycobench-600/releases/tag/v1.0.0), [pinned artifact license](https://github.com/debu-sinha/sycobench-600/blob/5193ce408bd73b401c4c5911f490e2bbad84a082/DATA_LICENSE).

The Git tree lists seven raw JSON files of approximately 13–20 MB each. We fetched the smallest, Mistral-7B-Instruct-v0.3, verified its Git blob identity, and successfully decoded its **1,665 records**. Field names include original messages, raw response text, parsed choices, correctness, retry information, metadata and skipped correction fields. This confirms availability of useful raw structure for that file, not completeness or correctness across all seven. The source parser, metrics, prompts and license were read as text; no upstream program was executed. [Inspection manifest and content hashes](public-data/sycobench-v1.0.0-inspection.json).

The original raw-host request timed out; the public GitHub blob API supplied a byte-verified copy. Full response text remains in ignored controller storage. This repository publishes provenance and our derived work, not a second copy of the raw release. No model-quality statistics were computed during feasibility inspection, and no new completion was generated.

## Stage 1: reproduce the published measurement first

1. Fetch all seven files, question metadata and the metric/build code at the pinned commit. Verify blob/content hashes and record source licenses. Read all code paths before execution; use an analysis-only entry point with no inference client or credentials.
2. Validate schemas, model identities, gold labels, question/variant uniqueness, suggested choices, retries, response presence and missing/skipped records. Inventory completion metadata; do not assume every provider supplies comparable stop reasons.
3. Reconstruct the source's common question population and baseline eligibility exactly. Check the reported 555-question intersection from the files rather than silently imposing it. Keep actual-versus-expected discrepancies visible.
4. Reproduce published point estimates and denominators with the original parser and metric definitions, then the documented uncertainty procedure. Compare machine-readable tables within a stated numerical/rounding tolerance. Record CPU time and peak memory locally.
5. Stop and explain any unresolved mismatch before reporting a sensitivity result. Successful reproduction is a prerequisite, not the contribution.

## Stage 2: freeze a sensitivity analysis before computing it

Do this only after Stage 1 and a focused novelty review. Preserve the official result unchanged. Specify which claim each alternative metric addresses, instead of selecting a parser that improves a preferred model's score.

- Separate exact adoption of the user's proposed option from other incorrect answers and unparseable responses. A failed response contract is not automatically evidence of agreement.
- Report coverage and both components of correction selectivity with their own denominators. Never infer missing correction outcomes from the baseline or invent unobserved follow-ups.
- Distinguish fixed official baseline cohorts from parser-dependent reclassification. Both may be informative, but they estimate different populations.
- Use a prespecified conservative final-answer parser only as sensitivity analysis, with explicit abstention for ambiguity. Manually review a blinded sample of parser disagreements; preserve inter-rater disagreement rather than using another model as ground truth.
- For unavailable outcomes, report explicit assumptions or bounds instead of silently dropping them. Do not call malformed-but-recorded answers missing data. Missing baseline correctness creates an additional population-identification issue.
- Preserve paired variants and examine normalized-stem/template dependence. Decide the resampling unit from the dataset structure before comparing uncertainty estimates.

Do not claim a ranking reversal, parser error rate, robustness gap or new result until the planned analysis has actually run and been checked. One benchmark may only support a careful replication note. Evidence across an additional independent release would strengthen generality but is not promised or scheduled here.

## Practical next step

Implement an analysis-only source inventory and reproduction adapter, with source hashes and small hand-checked fixtures. Keep it separate from the inference runner and historical pilot scores. This fits the local-only workflow without assuming an idle M4; actual CPU/memory cost still needs measurement. Human review of ambiguous responses and the novelty argument remains part of the researcher's 4–6 weekly hours.
