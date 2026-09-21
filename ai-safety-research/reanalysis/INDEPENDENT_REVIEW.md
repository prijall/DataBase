# Independent Stage 1 implementation review

September 21, 2026. Offline review before the first reproduction run. This review does not establish that the released table has been reproduced.

## Completed checks

- Read the pinned source parser, metric definitions, paper-specific bootstrap, builder, prompt definitions, validators and reproduction instructions without importing or executing author code. Read the published target CSV.
- Reviewed `REPRODUCTION_PROTOCOL.md`: seven models, 19 numeric columns (133 cells), 42 interval endpoints, exact counts, absolute tolerance 1e-12, fixed seeds 0/1/2 and 2,000 replicates, no population/scoring changes, and separate validation and runtime records are coherent.
- Independently checked all 18 entries then present in `reproduction-downloads.json`, including all seven raw logs, against local byte lengths, SHA-256, Git blob SHA-1 and saved release-tree entries. This was provenance validation, not outcome aggregation.
- Independently compared the adapter bootstrap with a separately written naive reference on **24 synthetic cohorts × three metrics = 72 comparisons**, using **200 replicates per comparison**. The reference draws question IDs with `random.Random(seed).choice`, concatenates every item in each sampled cluster, computes rates directly from the sampled items and sorts undefined values last. All interval endpoints agreed within 1e-12 and all undefined-replicate counts agreed exactly.
- Those synthetic cohorts exercise unequal cluster sizes, all three metric seeds, zero eligible denominators, skipped and missing corrections, and `None` parses. They do not use any released model outcomes. This is independent algorithmic checking against the inspected source definition, not execution of the upstream NumPy implementation.

## Source semantics preserved in the reviewed calculation core

The adapter retains first-seen question order, question-level resampling, the official stored correctness/format fields, unconditional PRA and baseline-correct pressure denominators. It distinguishes exported `nW_eff` from actual correction eligibility (`not skipped` and `not _missing_data`). `None == None` remains no-change when otherwise eligible. Percentiles use integer indices without interpolation and retain undefined replicates at the end. Syco measures loss of correctness under pressure; it does not prove adoption of the suggested answer.

## Final implementation checks and status

**No remaining implementation blocker for the protocol-bounded Stage 1 run after Git freeze.** Independently ran all **20 synthetic unit tests: passed**. Inspected the final acceptance changes: clean reproduction is separate from numeric parity; unresolved retained scoring/parser/prompt discrepancies, incomplete variant sets and released-warning mismatches block clean status. Historical dataset-hash differences remain disclosed. Absent correction placeholders are not spuriously reparsed. Output inside the verified source cache and reuse of an existing output directory are rejected. Adapter, tests and protocol must exactly match the recorded Git commit.

An additional independent synthetic manuscript check verified **35 row-and-column-aligned display cells**, then changed one value and confirmed exactly that cell failed. No released outcome calculation was needed. The runner contains no network/inference operations and does not execute upstream Python; subprocess use is limited to local read-only Git provenance checks. Inputs are loaded sequentially and checked against the pinned release tree. Wall time, process CPU time and process peak RSS are reported separately, with Darwin RSS units treated as bytes. Wall time includes waiting for local Git subprocesses; their CPU and memory are outside the process-only resource measurements. The 600-second external deadline is the parent execution controller's responsibility.

The 20 tests and these independent checks are bounded implementation evidence, not proof against every defect. Exact source/data provenance and all real-result validation and comparison records still need review after the first frozen execution.

No model, SSH or network requests were made for this review. No public performance metrics were calculated. The protocol and final implementation must be frozen before the authorized 600-second-bounded run. Source-gold validity, model-generation replication, statistical novelty and later sensitivity analyses are outside this review.

### Reviewed file identities

- `reproduce.py` SHA-256: `2e909ecad6e52a08e457f1574884b820533d9e71b48b23d7b3daec447586ae34`.
- `test_reproduce.py` SHA-256: `b0e2562ed72ab5f7f50d6e21a47c1d60433bd14929f9f1c337e401bd4ddd2b98`.
- `REPRODUCTION_PROTOCOL.md` SHA-256: `6dd6b69180854ad7b07a9636fd43d2e7e802cf9779f377bbee5e60389ecfb104`.
