# AI safety research

**Stage: offline design review and public-data reproduction preparation.** [Manuscript](paper/manuscript.md) · [Research state](RESEARCH_STATE.md) · [Latest runtime evidence](pilot/results/2026-09-21-runtime-cache-diagnostic/README.md)

## Current decision

The proposed arithmetic evidence × confidence study overlaps substantially with existing research. Keep it as a development instrument; novelty and conference readiness are not established. The revised draft addresses answer disclosure, conflicting cues, conditional populations and dependent observations.

The next bounded task is to **reproduce published SycoBench-600 metrics from released response logs**, then decide whether a prespecified sensitivity analysis can answer a useful new question. One pinned-release log has been decoded and its identity verified. No published score has been reproduced yet. This route uses local CPU analysis and requires no model loading.

## Latest work

| Deliverable | Evidence |
| --- | --- |
| Fresh comparison with the three closest studies | [Versioned literature review](DESIGN_LITERATURE_COMPARISON_2026-09-21.md) |
| Additional benchmark overlap and design critique | [Supplemental audit](SUPPLEMENTAL_DESIGN_AUDIT_2026-09-21.md) |
| Revised development-only question and controls | [Task design](TASK_MATCHED_DESIGN_DRAFT.md) |
| Four exact-arithmetic illustrations; twelve passing tests | [Checker and human-review packet](design/README.md) |
| Pinned public-log schema and source inspection | [Feasibility and reproduction plan](PUBLIC_LOG_REANALYSIS_FEASIBILITY.md), [hash manifest](public-data/sycobench-v1.0.0-inspection.json) |
| Manuscript updated alongside the work | [Discussion §5.1](paper/manuscript.md#51-offline-design-review-and-next-measurement-question), [related work](paper/related_work.md) |

## Existing experiment record

The archive contains **240 generated completions**: 232 earlier development/diagnostic responses, two original-context ProcessBench responses and six smaller-context responses. Both partial calibrations remain closed. All forty evaluation cases are untouched; no anti-sycophancy intervention ran. The later cache-disabled check generated no answers and stopped at its memory guards; cleanup was verified.

The [research state](RESEARCH_STATE.md) preserves counts and links to every historical archive. The [pilot guide](pilot/README.md) describes code and frozen protocols. [Initial paper summaries](PAPER_SUMMARIES.md) and the [historical novelty audit](NOVELTY_AUDIT.md) remain available with links to the newer assessment.

## Constraints and review

Research must coexist with normal office workload: 4–6 personal hours and at most nine combined machine-hours weekly. Further M4 loading and larger-model trials are deferred. Experimental inference remains local, and no research files are persisted on the M4. Public logs are another researcher's published outputs, not new local completions.

Arithmetic checks do not substitute for human review of wording, labels, novelty or interpretation. The four illustrations are exposed development material. A public-data reanalysis must reproduce the original measurement before changing it; neither parser changes nor smaller models alone establish a contribution. The working manuscript is not ready for conference submission.
