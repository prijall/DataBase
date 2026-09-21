# Research state

Updated: September 21, 2026. **M4 preflight blocked by resource guards; cleanup verified and session closed.** This file is the handoff for continuing on another computer or in another assistant conversation.

## Objective

Conduct independent AI safety research with AI assistance, local experiments, and an eventual defensible conference submission. Current candidate: whether anti-sycophancy interventions affect verified reasoning-error detection differently in user-correction and standalone-review contexts.

**Novelty remains unverified.** The [audit](NOVELTY_AUDIT.md) supersedes the initial reading list's provisional direction. Broad claims about stubbornness, evidence-based updating, and verifier strictness overlap existing work.

## Available work

- [Working manuscript](paper/manuscript.md), [verified related work](paper/related_work.md), and [manuscript update workflow](paper/README.md).
- [Initial ten-paper reading notes](PAPER_SUMMARIES.md).
- [Ten-study follow-up novelty audit](NOVELTY_AUDIT.md).
- [Local baseline pilot](pilot/README.md): ten generated arithmetic problems, thirty mechanically checked traces, deterministic scorer, resumable Ollama runner, and regression checks.
- [Example audit sheet](pilot/EXAMPLES.md): shows all equalities and error labels. Independent human review is still outstanding.

## Execution status

The repository archives **232 local experimental/diagnostic completions**: 42 earlier calls, 130 freeform-v3 calls and sixty verification-only calls. The ProcessBench code and memory-only SSH transport passed independent offline review before the latest runtime check. The integrated suite passes 109 tests, including 61 ProcessBench checks.

**Latest runtime finding:** the September 21 [M4 preflight](pilot/results/2026-09-21-processbench-m4/README.md), frozen at commit `017f1d708943876bda16bba67cc32b97c9ebaa14`, stopped after one non-generating debug-render request. The corrected response reader was in place but not reached: the memory check precedes response validation and tokenization. Memory pressure rose from normal level 1 to level 2, free memory fell from 36% to 15%, and swap usage and swapouts each increased by approximately 1.565 GiB. These crossed the original guards. Zero exact token checks and zero calibration/evaluation answers completed. Global measurements cannot isolate model loading from concurrent office activity or establish general M4 infeasibility.

Cleanup independently confirmed pressure level 1, 42% free memory, closed ports 11435 and 58358, and absence of the owned research process group. The session is closed; its blocked report cannot be resumed. No research files were persisted on the M4: Python code and input data were supplied through SSH stdin and memory; records remain on the controller and in the GitHub archive. The earlier [M1 failure](pilot/results/2026-09-16-processbench-preflight/README.md) remains preserved.

**Latest completed model experiment:** the [September 16 verification-only screen](pilot/results/2026-09-16-verification-only/README.md) completed all thirty planned calls per model. Llama produced thirty usable `VALID` labels, accepting all valid traces and missing all twenty invalid traces (50% primary balanced accuracy). Qwen produced thirty extra-text responses, all truncated at sixteen tokens and unusable under the fixed parser. Its usable-conditional accuracy is not estimable. Both primary gates failed; neither outcome supports an intervention study. The manuscript now incorporates both screens.

Read the [protocol screen report and raw results](pilot/results/2026-09-15-protocol-screen/README.md). Both models solved one control problem correctly with ordinary worked reasoning, so the failure cannot be generalized to all arithmetic capability. Allowing a `working` JSON field did not fix the issue. No activation-steering experiment has run.

The [completed v3 report](pilot/results/2026-09-15-freeform-v3/README.md) records Llama's 120-call baseline (60 strictly parsed) and Qwen's ten-call initial screen (two strictly parsed and correct). Llama passed its initial gate but failed the full parsing gate; Qwen failed its initial gate and stopped before the other 110 calls. All 41 parseable Llama trace judgments reject the trace, including eight valid traces. Its naturally wrong initial cohort is empty, so natural correction acceptance is **not estimable**.

The separate post-hoc presentation audit recovers one Llama verdict and none for Qwen. It leaves primary scores and failed gates unchanged. No intervention ran. These are development findings about the tested interface and examples, not a general alignment effect. The working manuscript contains the verified results and limitations.

Recorded v3 client sessions total **1,505.20 seconds (25.09 minutes)**. The verification-only screen added **52.079 seconds**; earlier diagnostics recorded about 85 seconds. These figures exclude development, hosted AI assistance, idle gaps and model residency. This work session left no inference runner or scheduled research automation active.

## Constraints and separation

- Personal time: 4–6 hours/week. Shared-machine experiment budget: nine machine-hours/week combined.
- Experimental inference stays local. Current test uses an existing local Ollama installation; no remote model API is required.
- V3 and verification-only calls used installed models sequentially on an Apple M1 with 8 GiB RAM. September 21 inspection verified an Apple M4 with 16 GiB RAM and matching installed runtime identities; only a non-generating preflight ran there. No M4 inference throughput or accuracy was measured.
- Claude Max assisted with a sanitized methods review; experimental inference remained local.
- This is personal research; no employer datasets or credentials belong in the repository.

## Continue from home

[PR #1](https://github.com/prijall/DataBase/pull/1), [PR #2](https://github.com/prijall/DataBase/pull/2) and [PR #3](https://github.com/prijall/DataBase/pull/3) are merged. The experiment archives and manuscript are on `main`; the current M4 session evidence and documentation are tracked in [PR #4](https://github.com/prijall/DataBase/pull/4) on `codex/m4-research-readiness`. The office connection has read access to the personal repository, so publication uses a fork and pull request.

After merging while signed into the personal account, clone or pull the repository at home. Read this file, then the latest result report. Before switching machines, commit and push research files and update this state. GitHub does not automatically contain chat history, model weights, or ignored run directories.

## Next decision

The latest attempt is closed; no scheduled restart or background research process remains. Read the [September 21 readiness record](pilot/processbench/READINESS_2026-09-21.md) and [M4 session evidence](pilot/results/2026-09-21-processbench-m4/README.md). A future low-workload session needs enough available memory and a fresh target-specific preflight with a new documented budget. Preserve the failed reports; do not delete them, relax thresholds, or reuse the closed session to bypass a stop.

The **offline measurement-validation preparation is complete**: [source audit](pilot/PUBLISHED_INTERFACE_AUDIT.md), [local plan](pilot/PROCESSBENCH_PLAN.md), [provenance](pilot/processbench/provenance.json), and [selection](pilot/processbench/selection.json). The pinned GSM8K domain contains 400 solutions (193 error-free, 207 erroneous) and 375 distinct exact problem strings. The reserved 20 calibration and 40 evaluation cases are balanced by process label, separated by normalized problem text, and remain untouched. This is a local interface adaptation, not reproduction of published scores.

The runner and [memory-only M4 transport](pilot/PROCESSBENCH_M4_SESSION.md) are implemented and reviewed. Fixed generation settings remain Llama-3.2 3B, 8,192 total context and 1,024 output tokens, one sample, sequential execution. Exact token counts and resource fit must pass before any subject request. Calibration advances only with all 20 records, at least 18 normally completed in-range predictions, and at least 8/10 completion-gated exact judgments in each class. Only then may the untouched 40-case evaluation run. The cohort remains capped at 60 requests and 90 minutes; the remote transport reserves 150 seconds before another request. The [pilot guide](pilot/README.md) documents the CLI. No subject inference or intervention has been added.

Increasing Qwen's budget alone is not a demonstrated remedy: its observed prefixes already contain disallowed prose. Do not reinterpret those prefixes as successful judgments under the frozen rule.

Before returning to the conversational research question, establish reliable valid acceptance and invalid rejection. Then address error-position/error-count confounds, obtain independent example review, and freeze held-out data and matched intervention controls. Continue the remaining literature checks before claiming novelty.

With every completed research increment, archive and verify evidence, update the manuscript's Methods/Results/Discussion and abstract as appropriate, then update the concise README and this handoff in the same commit. Preserve failed runs, denominators and primary/post-hoc distinctions. The [paper outline](PAPER_OUTLINE.md) maps manuscript sections to evidence and outstanding work. The draft is not yet ready for conference submission.
