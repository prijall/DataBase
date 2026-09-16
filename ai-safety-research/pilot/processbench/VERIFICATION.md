# Offline preparation verification

September 16, 2026. This report checks software and selection artifacts, not model performance. No subject inference ran.

## Checks completed

- **60 regression tests passed:** 48 existing checks and 12 new offline preparation tests.
- An independent AI reviewer isolated the two pure upstream prompt/extraction functions from the pinned evaluator's syntax tree, without importing its CUDA or model dependencies.
- **400/400** rendered source prompts matched the upstream builder exactly. A separate **400/400** metadata-mutation check found that IDs, generator names, gold labels and final-answer-correctness fields do not enter the prompts.
- **24/24** adversarial strings produced the same predictions as upstream extraction followed by Python integer conversion, including multiple boxes, malformed last boxes, unusual integer spellings and out-of-range integers.
- Regenerating the selection produced **byte-identical JSON**. Reversing input order did not change the manifest. The root agent separately regenerated and byte-compared it using the documented CLI.
- All **60 selected message hashes** matched independently rendered upstream prompts.
- Calibration contains 20 records (10 error-free / 10 erroneous); evaluation contains 40 (20 / 20). There are 60 unique IDs and 60 distinct normalized problem groups, with no within-portion repeats or cross-portion overlap.
- Pinned data, prompt and evaluator hashes match the downloaded bytes. Adapter and provenance hashes match the selection manifest.
- The root agent checked 196 local Markdown links at this stage; none were missing. Git diff whitespace checks passed.

The full source population contains 400 unique IDs and 375 normalized textual problems; 24 problem groups have multiple solutions, with a maximum of three. All labels are integers equal to −1 or a valid zero-based paragraph index. Selected prompt sizes are at most 2,681 UTF-8 bytes for calibration and 2,903 for evaluation; these sizes exclude the model chat template and are **not token counts or memory-fit evidence**.

## Artifact identities

```text
processbench_prepare.py
574c9d6bcbfcf21a15e5ac878cbe892869bb47c8634920846dc69d0630feae28

selection.json
2fb187e84c18bf6587334d72853577b4a94569fe8ad42cab5d739670c433bab8
```

[Provenance](provenance.json) records upstream revisions, download URLs and source hashes. [Selection](selection.json) records exact IDs, grouping, source/code identities and message hashes. The [plan](../PROCESSBENCH_PLAN.md) supplies the reproduction command and prospective execution limits.

## Boundaries

The independent adapter preserves inspected greedy extraction semantics. Its zero harmonic-mean convention when both class accuracies are zero is an explicitly documented change from the upstream unguarded division. Empty-class aggregates remain unavailable. Index-range validity is a separate diagnostic; runtime completion gating has not been implemented in this offline module.

The adapter does not contact a model, download files, or measure accuracy. A reviewed local runner, exact token/context preflight, model/template identity checks and hardware checks are still required before calibration. AI review is supporting quality control, not a substitute for human responsibility or independent scientific replication.
