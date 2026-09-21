# DataBase

SQL and database work, with a separate workspace for my independent AI safety research.

## AI safety research

**Stage: development experiments and working paper.** Read the [research workspace](ai-safety-research/README.md), [manuscript](ai-safety-research/paper/manuscript.md), and [current research state](ai-safety-research/RESEARCH_STATE.md).

The [2,048-token M4 calibration](ai-safety-research/pilot/results/2026-09-21-processbench-small-context/README.md) passed exact-token preflight and recorded six calibration responses before a memory-pressure stop: four usable, one correct. The archive now records **240 generated completions**. Calibration remains incomplete; all forty evaluation cases are untouched. Cleanup is verified, and research files remain on the controller and GitHub.

A subsequent [cache-disabled loading check](ai-safety-research/pilot/results/2026-09-21-runtime-cache-diagnostic/README.md) also hit the resource guards, before generating answers. Cleanup is verified. Research must coexist with office work; the next step is the [offline task design](ai-safety-research/TASK_MATCHED_DESIGN_DRAFT.md), with further model loading deferred.
