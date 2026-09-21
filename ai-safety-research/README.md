# AI safety research

**Stage: public-data reproduction complete; contribution still to be established.** [Manuscript](paper/manuscript.md) · [Research state](RESEARCH_STATE.md) · [Latest runtime evidence](pilot/results/2026-09-21-runtime-cache-diagnostic/README.md)

## Current decision

The proposed arithmetic evidence × confidence study overlaps substantially with existing research. Keep it as a development instrument; novelty and conference readiness are not established. The revised draft addresses answer disclosure, conflicting cues, conditional populations and dependent observations.

The [SycoBench-600 reproduction](reanalysis/results/2026-09-21-sycobench-reproduction/README.md) passed: **133/133 numeric values**, including **42 confidence-interval endpoints**, and **35/35 manuscript display cells** matched. The seven-log analysis took 8.4 seconds and about 313 MiB peak memory. All seven historical dataset hashes differ from the released question file; this remains disclosed despite consistent current prompts and scoring. No inference ran.

Next, check novelty and freeze a narrow analysis separating exact adoption of a wrong suggestion from other noncorrect or unparseable responses. Numerical reproduction is a prerequisite, not yet a new safety contribution.

## Latest work

| Deliverable | Evidence |
| --- | --- |
| Fresh comparison with the three closest studies | [Versioned literature review](DESIGN_LITERATURE_COMPARISON_2026-09-21.md) |
| Additional benchmark overlap and design critique | [Supplemental audit](SUPPLEMENTAL_DESIGN_AUDIT_2026-09-21.md) |
| Revised development-only question and controls | [Task design](TASK_MATCHED_DESIGN_DRAFT.md) |
| Four exact-arithmetic illustrations; twelve passing tests | [Checker and human-review packet](design/README.md) |
| Seven-model published-log reproduction; twenty passing tests | [Results](reanalysis/results/2026-09-21-sycobench-reproduction/README.md), [protocol](reanalysis/REPRODUCTION_PROTOCOL.md), [source audit](reanalysis/SOURCE_METHODS_AUDIT.md) |
| Manuscript updated alongside the work | [Methods §3.8 and Results §4.11](paper/manuscript.md#411-published-log-reproduction), [related work](paper/related_work.md) |

## Existing experiment record

The archive contains **240 generated completions**: 232 earlier development/diagnostic responses, two original-context ProcessBench responses and six smaller-context responses. Both partial calibrations remain closed. All forty evaluation cases are untouched; no anti-sycophancy intervention ran. The later cache-disabled check generated no answers and stopped at its memory guards; cleanup was verified.

The [research state](RESEARCH_STATE.md) preserves counts and links to every historical archive. The [pilot guide](pilot/README.md) describes code and frozen protocols. [Initial paper summaries](PAPER_SUMMARIES.md) and the [historical novelty audit](NOVELTY_AUDIT.md) remain available with links to the newer assessment.

## Constraints and review

Research must coexist with normal office workload: 4–6 personal hours and at most nine combined machine-hours weekly. Further M4 loading and larger-model trials are deferred. Experimental inference remains local, and no research files are persisted on the M4. Public logs are another researcher's published outputs, not new local completions.

Arithmetic checks do not substitute for human review of wording, labels, novelty or interpretation. The four illustrations are exposed development material. The original published measurement has been reproduced; any changed measurement needs a separate plan; neither parser changes nor smaller models alone establish a contribution. The working manuscript is not ready for conference submission.
