# Research state

Updated: September 15, 2026. This file is the handoff for continuing on another computer or in another assistant conversation.

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

The runner and two analysis modules passed **32 regression tests**, exact arithmetic checks, and independent AI review. The repository now archives **172 local experimental/diagnostic completions**: 42 earlier calls and 130 freeform-v3 calls.

Read the [protocol screen report and raw results](pilot/results/2026-09-15-protocol-screen/README.md). Both models solved one control problem correctly with ordinary worked reasoning, so the failure cannot be generalized to all arithmetic capability. Allowing a `working` JSON field did not fix the issue. No activation-steering experiment has run.

The [completed v3 report](pilot/results/2026-09-15-freeform-v3/README.md) records Llama's 120-call baseline (60 strictly parsed) and Qwen's ten-call initial screen (two strictly parsed and correct). Llama passed its initial gate but failed the full parsing gate; Qwen failed its initial gate and stopped before the other 110 calls. All 41 parseable Llama trace judgments reject the trace, including eight valid traces. Its naturally wrong initial cohort is empty, so natural correction acceptance is **not estimable**.

The separate post-hoc presentation audit recovers one Llama verdict and none for Qwen. It leaves primary scores and failed gates unchanged. No intervention ran. These are development findings about the tested interface and examples, not a general alignment effect. The working manuscript contains the verified results and limitations.

Recorded v3 client sessions total **1,505.20 seconds (25.09 minutes)**. Earlier calls recorded about 85 seconds. These figures exclude development, hosted AI assistance, idle gaps and model residency. No inference runner or scheduled research automation is left active.

## Constraints and separation

- Personal time: 4–6 hours/week. Shared-machine experiment budget: nine machine-hours/week combined.
- Experimental inference stays local. Current test uses an existing local Ollama installation; no remote model API is required.
- V3 used installed Llama and Qwen models sequentially on an Apple M1 with 8 GiB RAM. M4 access and throughput were not used or reverified.
- Claude Max assisted with a sanitized methods review; experimental inference remained local.
- This is personal research; no employer datasets or credentials belong in the repository.

## Continue from home

The earlier [PR #1](https://github.com/prijall/DataBase/pull/1) and [PR #2](https://github.com/prijall/DataBase/pull/2) are merged. PR #2 was merged while experiments continued, so the completed results and manuscript are proposed in [PR #3](https://github.com/prijall/DataBase/pull/3), on `codex/reasoning-pilot-experiments`. Until merged, use PR #3's branch for the latest work. The office connection has read access to the personal repository, so publication uses a fork and pull request.

After merging while signed into the personal account, clone or pull the repository at home. Read this file, then the latest result report. Before switching machines, commit and push research files and update this state. GitHub does not automatically contain chat history, model weights, or ignored run directories.

## Next decision

Stop protocol revisions for this work session. Plan a small **verification-only feasibility test** before dataset expansion or steering. Inspect [the ten examples](pilot/EXAMPLES.md), then address error-position and error-count confounds, calibrate difficulty, obtain independent example review, and freeze held-out data and a matched intervention/control plan. Continue the remaining literature checks before claiming novelty.

With every completed research increment, archive and verify evidence, update the manuscript's Methods/Results/Discussion and abstract as appropriate, then update the concise README and this handoff in the same commit. Preserve failed runs, denominators and primary/post-hoc distinctions. The [paper outline](PAPER_OUTLINE.md) maps manuscript sections to evidence and outstanding work. The draft is not yet ready for conference submission.
