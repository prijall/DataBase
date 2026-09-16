# Research state

Updated: September 16, 2026. This file is the handoff for continuing on another computer or in another assistant conversation.

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

The inference and analysis tools passed **48 regression tests**, exact arithmetic checks, and independent AI review. The repository now archives **232 local experimental/diagnostic completions**: 42 earlier calls, 130 freeform-v3 calls and sixty verification-only calls.

**Latest result:** the [September 16 verification-only screen](pilot/results/2026-09-16-verification-only/README.md) completed all thirty planned calls per model. Llama produced thirty usable `VALID` labels, accepting all valid traces and missing all twenty invalid traces (50% primary balanced accuracy). Qwen produced thirty extra-text responses, all truncated at sixteen tokens and unusable under the fixed parser. Its usable-conditional accuracy is not estimable. Both primary gates failed; neither outcome supports an intervention study. The manuscript now incorporates both screens.

Read the [protocol screen report and raw results](pilot/results/2026-09-15-protocol-screen/README.md). Both models solved one control problem correctly with ordinary worked reasoning, so the failure cannot be generalized to all arithmetic capability. Allowing a `working` JSON field did not fix the issue. No activation-steering experiment has run.

The [completed v3 report](pilot/results/2026-09-15-freeform-v3/README.md) records Llama's 120-call baseline (60 strictly parsed) and Qwen's ten-call initial screen (two strictly parsed and correct). Llama passed its initial gate but failed the full parsing gate; Qwen failed its initial gate and stopped before the other 110 calls. All 41 parseable Llama trace judgments reject the trace, including eight valid traces. Its naturally wrong initial cohort is empty, so natural correction acceptance is **not estimable**.

The separate post-hoc presentation audit recovers one Llama verdict and none for Qwen. It leaves primary scores and failed gates unchanged. No intervention ran. These are development findings about the tested interface and examples, not a general alignment effect. The working manuscript contains the verified results and limitations.

Recorded v3 client sessions total **1,505.20 seconds (25.09 minutes)**. The verification-only screen added **52.079 seconds**; earlier diagnostics recorded about 85 seconds. These figures exclude development, hosted AI assistance, idle gaps and model residency. This work session left no inference runner or scheduled research automation active.

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

Stop inference for the completed screen. The next deliverable is an **offline measurement-validation plan**: review the existing failures, select a published verification interface and documented scoring procedure for a bounded baseline replication, and specify separate calibration material, generation settings and stopping rules before further inference. Increasing Qwen's budget alone is not a demonstrated remedy: its observed prefixes already contain disallowed prose. Do not reinterpret those prefixes as successful judgments under the frozen rule.

Before returning to the conversational research question, establish reliable valid acceptance and invalid rejection. Then address error-position/error-count confounds, obtain independent example review, and freeze held-out data and matched intervention controls. Continue the remaining literature checks before claiming novelty.

With every completed research increment, archive and verify evidence, update the manuscript's Methods/Results/Discussion and abstract as appropriate, then update the concise README and this handoff in the same commit. Preserve failed runs, denominators and primary/post-hoc distinctions. The [paper outline](PAPER_OUTLINE.md) maps manuscript sections to evidence and outstanding work. The draft is not yet ready for conference submission.
