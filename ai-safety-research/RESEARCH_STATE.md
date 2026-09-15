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

The pilot implementation has passed eight regression tests and all arithmetic-label checks. Local model inference is the next execution step; update this section with the resulting run location and limitations after it finishes.

## Constraints and separation

- Personal time: 4–6 hours/week. Shared-machine experiment budget: nine machine-hours/week combined.
- Experimental inference stays local. Current test uses an existing local Ollama installation; no remote model API is required.
- The active machine has an installed `llama3.2:3b`; M4 access and throughput have not been reverified.
- This is personal research; no employer datasets or credentials belong in the repository.

## Continue from home

The working branch is `codex/ai-safety-reading-notes`; additions are proposed in [prijall/DataBase PR #1](https://github.com/prijall/DataBase/pull/1). Until merged, use the PR's branch to see the latest work. The office connection has read access to the personal repository, so publication uses a fork and pull request.

After merging while signed into the personal account, clone or pull the repository at home. Read this file, then the latest result report. Before switching machines, commit and push research files and update this state. GitHub does not automatically contain chat history, model weights, or ignored run directories.

## Next decision

Inspect the baseline outputs for parsing failures and task ceiling/floor effects. If there are no naturally wrong initial answers, correction acceptance cannot be estimated on these items. Revise development tasks and error-position controls before building steering or freezing a test set. Continue the literature checks listed in the audit before claiming novelty.
