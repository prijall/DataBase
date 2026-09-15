# Research state

Updated: September 15, 2026. This file is the handoff for continuing on another computer or in another assistant conversation.

## Objective

Conduct independent AI safety research with AI assistance, local experiments, and an eventual defensible conference submission. Current candidate: whether anti-sycophancy interventions affect verified reasoning-error detection differently in user-correction and standalone-review contexts.

**Novelty remains unverified.** The [audit](NOVELTY_AUDIT.md) supersedes the initial reading list's provisional direction. Broad claims about stubbornness, evidence-based updating, and verifier strictness overlap existing work.

## Available work

- [Initial ten-paper reading notes](PAPER_SUMMARIES.md).
- [Ten-study follow-up novelty audit](NOVELTY_AUDIT.md).
- [Local baseline pilot](pilot/README.md): ten generated arithmetic problems, thirty mechanically checked traces, deterministic scorer, resumable Ollama runner, and regression checks.
- [Example audit sheet](pilot/EXAMPLES.md): shows all equalities and error labels. Independent human review is still outstanding.

## Execution status

The pilot implementation passed **eleven regression tests** and all arithmetic-label checks. We ran **42 local diagnostic calls**: three 12-call suitability slices and six simple controls. The full 120-call sweep was stopped because the JSON protocols produced no correct initial answers and substantial trace-format failures.

Read the [protocol screen report and raw results](pilot/results/2026-09-15-protocol-screen/README.md). Both models solved one control problem correctly with ordinary worked reasoning, so the failure cannot be generalized to all arithmetic capability. Allowing a `working` JSON field did not fix the issue. No activation-steering experiment has run.

Recorded client execution totaled about 85 seconds, excluding idle periods and development. No research process or automation is left running.

## Constraints and separation

- Personal time: 4–6 hours/week. Shared-machine experiment budget: nine machine-hours/week combined.
- Experimental inference stays local. Current test uses an existing local Ollama installation; no remote model API is required.
- The active machine has an installed `llama3.2:3b`; M4 access and throughput have not been reverified.
- This is personal research; no employer datasets or credentials belong in the repository.

## Continue from home

The working branch is `codex/ai-safety-reading-notes`; additions are proposed in [prijall/DataBase PR #1](https://github.com/prijall/DataBase/pull/1). Until merged, use the PR's branch to see the latest work. The office connection has read access to the personal repository, so publication uses a fork and pull request.

After merging while signed into the personal account, clone or pull the repository at home. Read this file, then the latest result report. Before switching machines, commit and push research files and update this state. GitHub does not automatically contain chat history, model weights, or ignored run directories.

## Next decision

The next engineering task is a separately versioned protocol allowing ordinary worked reasoning followed by a delimited machine-readable verdict. Validate it on simple controls before another suitability slice. The current initial-correct cohort is empty, so pressure-induced errors cannot be estimated. Inspect [the ten examples](pilot/EXAMPLES.md), then revise error-position and error-count confounds before building steering or freezing a test set. Continue the literature checks listed in the audit before claiming novelty.
