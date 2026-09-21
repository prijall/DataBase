# Research state

Updated: September 21, 2026. **Smaller-context calibration stopped after six responses; cleanup verified and session closed.** This file is the handoff for continuing on another computer or in another assistant conversation.

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

The repository now archives **240 generated completions**: 232 earlier diagnostic/development calls, two original-context ProcessBench responses, and six smaller-context responses. The smaller-context implementation passed **127 offline tests**, including 79 ProcessBench checks, before execution.

**Latest result:** the [smaller-context M4 session](pilot/results/2026-09-21-processbench-small-context/README.md), frozen at `5d73d85`, passed exact-token preflight for all sixty newly selected prompts. Counts range from 290 to 789, with a maximum 1,813 including the unchanged 1,024-token output reserve. The actual loaded context was 2,048. Calibration recorded **6/20** responses: four usable, one correct, two malformed extractions, no out-of-range indices, and no length stops or request errors. Valid-class coverage was 2/10, with one usable and zero correct; error-class coverage was 4/10, with three usable and one correct. The observed-output harmonic mean is computable but does not constitute a completed benchmark score. Fourteen missing cases are unattempted observations, not incorrect predictions; the gate was not passed and evaluation did not run.

After the sixth response, pressure rose to level 2 while free memory was 22%. The non-normal-pressure guard stopped execution; neither swap usage nor swapouts grew against baseline. Cleanup confirmed pressure level 1, 42% free memory, closed ports 11435 and 61457, and absence of the owned research process group. No research files persisted on the M4; records stayed on the controller for GitHub. The session is closed and cannot be automatically retried or changed under the same plan.

The earlier [8,192-token session](pilot/results/2026-09-21-processbench-m4-session2/README.md) remains separate: two observed calibration responses, one usable/correct and one length-stopped/out of range, followed by a free-memory stop. Its original twenty-case calibration has been retired. The new calibration has six used and fourteen unattempted cases. All forty original evaluation cases remain untouched.

Historical resource stops remain archived: the [first M4 session](pilot/results/2026-09-21-processbench-m4/README.md) stopped after one non-generating debug load before response validation/tokenization, and the [earlier M1 attempt](pilot/results/2026-09-16-processbench-preflight/README.md) also generated no subject answers. Global resource readings do not isolate model loading from office activity or establish general hardware incapacity.

**Latest completed model experiment:** the [September 16 verification-only screen](pilot/results/2026-09-16-verification-only/README.md) completed all thirty planned calls per model. Llama produced thirty usable `VALID` labels, accepting all valid traces and missing all twenty invalid traces (50% primary balanced accuracy). Qwen produced thirty extra-text responses, all truncated at sixteen tokens and unusable under the fixed parser. Its usable-conditional accuracy is not estimable. Both primary gates failed; neither outcome supports an intervention study. The manuscript now incorporates both screens.

Read the [protocol screen report and raw results](pilot/results/2026-09-15-protocol-screen/README.md). Both models solved one control problem correctly with ordinary worked reasoning, so the failure cannot be generalized to all arithmetic capability. Allowing a `working` JSON field did not fix the issue. No activation-steering experiment has run.

The [completed v3 report](pilot/results/2026-09-15-freeform-v3/README.md) records Llama's 120-call baseline (60 strictly parsed) and Qwen's ten-call initial screen (two strictly parsed and correct). Llama passed its initial gate but failed the full parsing gate; Qwen failed its initial gate and stopped before the other 110 calls. All 41 parseable Llama trace judgments reject the trace, including eight valid traces. Its naturally wrong initial cohort is empty, so natural correction acceptance is **not estimable**.

The separate post-hoc presentation audit recovers one Llama verdict and none for Qwen. It leaves primary scores and failed gates unchanged. No intervention ran. These are development findings about the tested interface and examples, not a general alignment effect. The working manuscript contains the verified results and limitations.

Recorded v3 client sessions total **1,505.20 seconds (25.09 minutes)**. The verification-only screen added **52.079 seconds**; earlier diagnostics recorded about 85 seconds. These figures exclude development, hosted AI assistance, idle gaps and model residency. This work session left no inference runner or scheduled research automation active.

## Constraints and separation

- Personal time: 4–6 hours/week. Shared-machine experiment budget: nine machine-hours/week combined. Research must coexist with the usual office workload; the user declined a quiet-machine window. Do not close office applications or assume exclusive hardware access. Larger model trials are deferred.
- Experimental inference stays local. Current test uses an existing local Ollama installation; no remote model API is required.
- V3 and verification-only calls used installed models sequentially on an Apple M1 with 8 GiB RAM. September 21 inspection verified an Apple M4 with 16 GiB RAM and matching installed runtime identities; two later M4 configurations passed token preflight and produced separate partial calibrations of two and six responses. Neither completed the planned calibration.
- Claude Max assisted with a sanitized methods review; experimental inference remained local.
- This is personal research; no employer datasets or credentials belong in the repository.

## Continue from home

[PR #1](https://github.com/prijall/DataBase/pull/1), [PR #2](https://github.com/prijall/DataBase/pull/2) and [PR #3](https://github.com/prijall/DataBase/pull/3) are merged. The experiment archives and manuscript are on `main`; the current M4 session evidence and documentation are tracked in [PR #4](https://github.com/prijall/DataBase/pull/4) on `codex/m4-research-readiness`. PR #4 is now merged; subsequent runtime-diagnostic work is on `codex/shared-workload-runtime`. The office connection has read access to the personal repository, so publication uses a fork and pull request.

After merging while signed into the personal account, clone or pull the repository at home. Read this file, then the latest result report. Before switching machines, commit and push research files and update this state. GitHub does not automatically contain chat history, model weights, or ignored run directories.

## Next decision

The latest scientific attempt is closed. A separately reviewed [four-call synthetic runtime diagnostic](pilot/RUNTIME_CACHE_DIAGNOSTIC_PROTOCOL.md) is being prepared to check a source-supported cache setting; it cannot reopen calibration or admit evaluation. See the [source audit](pilot/RUNTIME_MEMORY_AUDIT_2026-09-21.md) and [next-baseline evidence](NEXT_BASELINE_EVIDENCE_2026-09-21.md). Read the [smaller-context archive](pilot/results/2026-09-21-processbench-small-context/README.md) and [readiness record](pilot/processbench/READINESS_2026-09-21.md). Preserve all partial records and denominators: original calibration retired, new calibration six observed/fourteen unattempted, evaluation forty untouched.

The [smaller-context protocol](pilot/PROCESSBENCH_SMALL_CONTEXT_PLAN.md) permitted one bounded screen and has now stopped at its resource guard. It authorizes no automatic retry or further context, prompt, model, or parser changes. The next work is a targeted investigation of runtime/cache allocation and independent human review of the six outputs, using existing logs and scores. The [post-hoc output review](pilot/results/2026-09-21-processbench-small-context/OUTPUT_REVIEW.md) records AI-assisted qualitative interpretations, not independently validated labels. Treat any output interpretation as post-hoc; do not repair primary answers or promote observed successes into evaluation. The error class has one correct result in four attempts; even six further successes could yield only 7/10, below the required 8/10. Runtime repair alone cannot rescue this gate, although the actual stop was resource pressure and the cohort is incomplete. A new experiment needs a separate decision and documented plan. The [runtime observations](pilot/results/2026-09-21-processbench-small-context/runtime-cache-observations.json) show five cached prompts occupying 408.015 MiB under an 8,192 MiB configured cache limit; this is a possible contributor to investigate, not isolated causation. Global memory readings do not establish hardware incapacity, and the changed calibration cases prevent attributing output differences to context size.

The [source audit](pilot/PUBLISHED_INTERFACE_AUDIT.md), [original plan](pilot/PROCESSBENCH_PLAN.md), [provenance](pilot/processbench/provenance.json), and [selection](pilot/processbench/selection.json) remain the reference. The pinned GSM8K domain has 400 solutions (193 error-free, 207 erroneous), with 375 distinct exact problem strings. Original calibration and evaluation were balanced by process label and separated by normalized problem text. These are local adaptations, not published-score replications. Calibration requires all 20 records, at least 18 normally completed in-range predictions, and at least 8/10 completion-gated exact judgments per class before any held-out evaluation. Preserve the sixty-request/90-minute cap and the remote 150-second reserve; do not relax resource thresholds to finish a run.

Increasing Qwen's budget alone is not a demonstrated remedy: its observed prefixes already contain disallowed prose. Do not reinterpret those prefixes as successful judgments under the frozen rule.

Before returning to the conversational research question, establish reliable valid acceptance and invalid rejection. Then address error-position/error-count confounds, obtain independent example review, and freeze held-out data and matched intervention controls. Continue the remaining literature checks before claiming novelty.

With every completed research increment, archive and verify evidence, update the manuscript's Methods/Results/Discussion and abstract as appropriate, then update the concise README and this handoff in the same commit. Preserve failed runs, denominators and primary/post-hoc distinctions. The [paper outline](PAPER_OUTLINE.md) maps manuscript sections to evidence and outstanding work. The draft is not yet ready for conference submission.
