# SycoBench-600 published-log reproduction protocol

Date: September 21, 2026. Stage 1 only. Freeze this document and reviewed implementation in Git before aggregating the released outcomes. Published target values have already been inspected: this is a prospective implementation/acceptance plan, not a blinded study or a preregistration of the original experiment.

## Purpose and source

Reproduce the seven rows of the authors' camera-ready `main_results.csv` from their released logs, preserving their measurement rules. This establishes a trustworthy analysis baseline; it does not establish a new safety finding or independently replicate model generation.

- Source: [SycoBench-600 v1.0.0](https://github.com/debu-sinha/sycobench-600/releases/tag/v1.0.0), commit `5193ce408bd73b401c4c5911f490e2bbad84a082`.
- Verify all consumed release files against byte sizes and Git blob identities in [the saved release tree](../public-data/sycobench-v1.0.0-tree.json); record SHA-256 hashes in the reproduction manifest. The tree SHA-256 is `b20ab896157faa6c3984ec73b5abe16c4db6c9a32fae49b22b92d46c676e4c9e`.
- Inputs: seven `results/raw_camera_ready` JSON logs, `data/questions.json`, published table, and the source files needed to audit parsing, prompts, validation, point metrics and bootstrap. Author code is read as source, not executed or imported.
- Preserve attribution to Debu Sinha. Code is MIT licensed; released data/logs/tables are CC BY 4.0. Keep raw logs in an ignored controller cache; publish derived summaries and provenance.

## Population and scoring

1. Audit model identity, unique `(question_id, variant)` identities, required structure, gold labels, question/prompt metadata and the three prompt variants. Derive the common question-ID intersection across the seven logs; preserve each log's record order. Do not force a desired count.
2. Preserve official stored scoring and formatting fields for primary reproduction. Independently recompute the release parser, correctness and formatting flags and record discrepancies; never silently replace fields to obtain a match. Historical metadata hashes and upstream validation warnings must be reported and investigated separately from structural failures.
3. Preserve all official denominators, including baseline-correct pressure rates, unconditional PRA, and baseline-wrong correction eligibility. Report both exported `nW_eff` (which subtracts `_missing_data`) and the actual correction denominator (which excludes `skipped` or `_missing_data`). Check whether these coincide in the released population.
4. Keep original definitions: Syco averages three correct-to-incorrect pressure rates; it is not restricted to adopting the suggested wrong letter. Correction no-change compares parsed responses, including `None == None` when otherwise eligible. Selectivity subtracts quantities from different conditional populations.
5. Reproduce validation warnings against the release report. Missing IDs outside the common population are not automatically a failed reproduction. Duplicate identities, inconsistent gold labels, corrupt source identity or an unexplained scoring discrepancy block a clean reproduction claim.

## Confidence intervals and acceptance

- Use the paper-specific question-cluster bootstrap, 2,000 replicates, sampling the same number of question IDs with replacement, retaining all variants within each sampled ID.
- Preserve first-encounter question order and Python `random.Random(seed)._randbelow` choice semantics. Seeds: Syco 0, stubbornness 1, PRA 2. Do not substitute the generic NumPy bootstrap.
- Match the original sorted, noninterpolated percentile indices `int(0.025 * 2000) = 50` and `int(0.975 * 2000) = 1950`, including undefined-value ordering.
- Compare all 19 numeric columns across all seven rows: **133 numeric cells**, including **42 interval endpoints**. Model labels and integer counts must match exactly. Probability-valued estimates and endpoints must have absolute error **at most 1e-12**. Undefined states must agree. This is deterministic numerical parity, not a statistical tolerance.
- A manuscript display comparison is separate and uses its printed rounding precision; matching a number somewhere in its text is insufficient evidence of row-wise agreement.
- Report every mismatch. Stop Stage 1 if a discrepancy cannot be resolved transparently from source semantics. Do not change tolerances, populations, parsers or targets after seeing a mismatch. Implementation bug fixes require recorded changes and a new code freeze before rerunning.

## Execution and records

Use a standard-library implementation on the controller CPU, loading model logs sequentially. No network calls from the analysis runner, model inference, SSH, M4 loading, service changes or office application changes. Bound the full run externally to 600 seconds; measure wall time, CPU time and peak resident memory separately from deterministic scientific outputs. This timeout is a run bound, not a memory-isolation guarantee.

Before execution: review implementation, run substantive synthetic tests and commit the protocol/source. After execution: retain code/protocol/source hashes, common IDs, coverage/validation audits, reproduced table, per-cell comparison and separate resource record; independently review results. Keep our prior **240 generated completions unchanged**: these logs contain other researchers' outputs.

Sensitivity analyses, alternative parsers, text-family resampling, new hypotheses and new model experiments are outside this run. A successful reproduction permits planning a separate analysis; it does not itself demonstrate novelty or conference readiness.
