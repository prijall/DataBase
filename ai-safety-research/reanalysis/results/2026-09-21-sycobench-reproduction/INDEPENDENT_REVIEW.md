# Independent review of the completed reproduction

September 21, 2026. **Pass for the stated Stage 1 reproduction target, with the provenance limitation below.** This is review of saved artifacts and source records; the full analysis and bootstrap were not rerun.

## Identity and execution

- Frozen implementation commit: `b4e0a27cd9d1575e572f1184c513eade2bb8bd0a`. Adapter, tests and protocol bytes independently match both that commit and the recorded SHA-256 hashes.
- All **25 consumed release files**, including seven model logs, match recorded byte sizes, SHA-256 hashes, Git blob identities and the pinned release tree. The tree hash also matches.
- All **five derived-output hashes** recorded in `provenance.json` match the saved files. `execution.json` records exit 0, empty stderr, no timeout and a 600-second external bound.
- Recorded analysis time: **8.427251875 seconds wall**, **8.334503 seconds process CPU**. Peak resident memory: **328,417,280 bytes (313.203125 MiB)**. Wrapper wall time is 8.561422167 seconds. Wall time includes Git waits; CPU and peak RSS measure the analysis process and exclude subprocess usage. These are recorded measurements, not an independently repeated resource benchmark.

## Independent result checks

1. Compared saved CSV values directly with the pinned published CSV: **all 133 numeric cells agree within 1e-12**, including **42 confidence-interval endpoints**; maximum absolute difference is **2.220446049250313e-16**. Model identities and integer counts agree exactly.
2. Inspected the seven manuscript main-table rows against reproduced values and checked the saved row/column comparisons: **all 35 displayed cells match**. This checks the main table, not every number or claim in the paper.
3. Re-derived the question-ID intersection from the source logs: **555 IDs**. Each model retains **1,665 unique question/variant records**, with variants 0/1/2 for every retained ID: **11,655 model-specific records total**. Saved ordered trial lists and their hashes match the source order.
4. Independently counted source baseline cohorts, eligible corrections, updates, no-change, both-`None` corrections, pressure-error numerators and joint PRA numerators. They agree with the saved analysis for all seven models. Exported `nW_eff` equals actual correction eligibility in this released population; the implementation continues to distinguish their definitions.
5. Independently reapplied the inspected parser rules to **52,189 observed baseline/perturbation records across the full released population**, excluding correction placeholders marked skipped or missing. Stored parses, correctness and available exact-letter flags all agree. This count includes records outside the common 555-question analysis population.
6. The reproduced upstream validation report equals the pinned release report exactly. Its known warning is Mistral's 45 missing IDs. Saved audits show no incomplete variant sets, cross-model prompt mismatches or blocking discrepancies. The bootstrap metadata records the frozen seeds, 2,000 replicates per metric and zero undefined replicates; interval outputs match the target without a new bootstrap run in this review.

## Provenance limitation and interpretation

All seven logs store question-file hash `3c2d71f250f32b9f5f8885d2881439605460a3dd84713b9fdfe122c2bb5078f5`; the released question file hashes to `ae41f4b94ac46fb0109778546a091534208881cf74eea87c43ce24736bb8dd4d`. Each mismatch is explicitly retained in `validation.json`. The audit does not recover or certify the exact historical input bytes used during generation. Current artifact consistency and successful numeric reproduction do not erase that limitation.

The evidence supports faithful reproduction of the released table under its original rules. It does not independently reproduce model generation, verify every question's gold answer, establish causal mechanisms, or demonstrate a novel research result. No model or hardware calls were made for this review; the project's generated-completion count remains **240**. Alternative parser and uncertainty analyses require a separate prospective plan.
