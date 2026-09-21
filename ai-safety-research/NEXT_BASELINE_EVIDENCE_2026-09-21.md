# Next baseline: evidence and a bounded decision

September 21, 2026. Primary-source desk review and inspection of the controller's saved metadata only: no model loads, new answers, hardware calls, or changes to frozen code/protocols. **Next concrete step: draft and human-review a short, task-matched measurement design.** The user has confirmed there is **no quiet M4 window**: research must coexist with ordinary office workload. Defer Qwen3.5 4B, Mistral and Gemma model trials under this constraint. Retain the model evidence below for a later eligibility decision; it does not schedule a larger-model experiment. This is a decision memo, not a registered experiment or an instruction to run one.

## What is already settled

The research record contains **240 subject calls**. The latest six-case ProcessBench prefix had four usable predictions and one exact match; all six stopped normally. The erroneous-solution class had one match in four attempts, so even six remaining successes could reach only 7/10, below the frozen 8/10 requirement. Its actual resource stop and its unattainable adequacy gate are distinct findings. Preserve both. Do not rerun cases, lower thresholds, pool configurations, or restart this cohort after a runtime fix. See the [qualitative output review](pilot/results/2026-09-21-processbench-small-context/OUTPUT_REVIEW.md).

## Published verification results put the gate in perspective

ProcessBench's **greedy** GSM8K results are below. These are different checkpoints tested on the full benchmark domain, not estimates for our installed models or balanced calibration sample. “Error” requires the exact earliest-error index; “correct” requires recognizing an error-free solution. The reported F1 is their harmonic mean. Table 9 is the appropriate single-sample comparison; the paper's main open-model results use eight-sample voting. [ProcessBench, ACL 2025, Table 9](https://aclanthology.org/2025.acl-long.50.pdf#page=15)

| Published critic | Error accuracy | Correct accuracy | Harmonic mean |
| --- | ---: | ---: | ---: |
| Llama-3.1-8B-Instruct | 36.7% | 17.1% | 23.3% |
| Qwen2.5-7B-Instruct | 36.7% | 66.3% | 47.3% |
| Qwen2.5-Math-7B-Instruct | 14.5% | 99.0% | 25.3% |
| QwQ-32B-Preview | 74.9% | 67.4% | 70.9% |

The official greedy evaluator permits 8,192 output tokens, or 32,768 for QwQ. Our 1,024-token allowance is a substantial adaptation. These numbers therefore do not establish a direct ranking against our short, quantized local runs. [Pinned official evaluator](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/run_eval.py#L51)

**Our interpretation:** requiring 8/10 in each class is defensible as a conservative admission rule for a study that needs an already useful verifier. It prevents a model that accepts everything or rejects everything from qualifying. It is not a literature-derived expected performance level, evidence of implementation fidelity, or a statistical guarantee of 80% population accuracy. Ten cases per class provide a noisy screen: one answer changes a class score by ten percentage points. Published smaller-model weaknesses make failure plausible; they do not justify weakening an already-observed gate. Passing would still require independent evaluation and an intervention design that handles baseline errors.

ProcessBench's earliest-error localization in multi-paragraph solutions is also harder and broader than a short controlled correction decision. It need not be the universal admission test for every version of the original safety question. Choosing a different task prospectively requires a task-specific adequacy justification; it cannot retroactively reopen or relabel the failed ProcessBench gate.

## Qwen3.5 4B: evidence retained; model trial deferred

The official card describes a post-trained 4B language model with a vision encoder and a hybrid attention layout. It supports thinking and non-thinking modes, defaults to thinking, and reports reasoning/instruction benchmarks. **No ProcessBench result appears in the reviewed card.** Its recommended output allowances are 32,768 tokens for most queries and 81,920 for complex benchmarks, and its sampling guidance differs from our greedy setting. These are substantial compatibility questions for a 1,024-token screen. Do not silently treat a short non-thinking run as the card's reasoning configuration. [Official Qwen3.5-4B card](https://huggingface.co/Qwen/Qwen3.5-4B)

Ollama's current `qwen3.5:4b` listing shows a **3.4 GB Q4_K_M** artifact, abbreviated digest `2a654d98e6fb`, and package metadata of 4.66B parameters. That page's shared benchmark readme features **Qwen3.5-397B-A17B**, not the 4B model: its numbers must not be attributed to this candidate. [Official Ollama tag listing](https://ollama.com/library/qwen3.5:4b)

The separately captured local metadata confirms manifest `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`, Q4_K_M, `qwen35` / 4.7B package metadata, a present 3,389,971,840-byte model blob (3.16 GiB), and `qwen3.5` renderer/parser names. Its declared minimum Ollama version is 0.17.1, below installed 0.34.0. This verifies packaging/version eligibility, not successful execution or scorer compatibility. The read-only observation recorded normal pressure, 45% free memory and both service ports closed, with zero model requests. Weight-file size and idle headroom do not establish loaded peak memory. Evidence: [archived installed-model metadata](pilot/INSTALLED_MODELS_2026-09-21.json).

Ollama can return thinking text separately from final content. A model switch therefore requires an explicit, tested scoring-channel contract; concatenating fields or searching whichever field yields a matching box would change measurement. Freeze the chosen mode and preserve both fields when emitted. [Official thinking API documentation](https://docs.ollama.com/capabilities/thinking)

Do not plug Qwen's name into the Llama preflight. The verified package has a named Qwen renderer/parser; its rendering path, tokenizer, special-token behavior and non-generating preflight support require their own validation. Qwen prompt counts are unmeasured. Llama's 2,048-token fit does not justify that context for Qwen, and a nominal 1,024-token budget must have an explicitly verified accounting rule for thinking and final output. A prospective runtime-cache setting also needs verified live uptake and resource observations; an available flag alone is not evidence that memory now fits.

## Decision under ordinary office workload

| Option | Decision now | Reason |
| --- | --- | --- |
| Qwen3.5 4B, Mistral or Gemma trial | **Defer** | Sustained fit alongside ordinary office activity is unestablished. No quiet window will be assumed or requested as a prerequisite. More parameters or idle free memory do not establish eligibility. |
| Restart failed Llama calibration | **Closed** | Its original adequacy gate is unattainable. A cache change cannot reopen it. |
| Bounded Llama cache diagnostic | Engineering-only, subject to its separately reviewed protocol | Can check live uptake and the resource behavior of a tiny workload; cannot certify a scientific baseline or a larger model. |
| Offline design for short answer updating | **Proceed with design and human review** | Preserves the safety question while reducing dependence on long solution critique. Novelty and eventual model competence remain open questions. |

The M1 has already failed relevant resource checks. Do not close office applications, clear system caches, alter shared services, increase resource limits or schedule unattended inference to create a passing condition. No downloads, training or broad model sweep are recommended. The nine combined machine-hours/week ceiling and 4–6 human hours/week remain constraints, not targets that must be consumed.

## What the cache diagnostic can establish

The [pinned-source runtime audit](pilot/RUNTIME_MEMORY_AUDIT_2026-09-21.md) identifies `LLAMA_ARG_CACHE_RAM=0` as a supported way to disable the separate saved prompt-state cache in the owned service. It does not disable the active KV buffer or all current-slot prefix reuse. The draft [diagnostic controller](pilot/runtime_cache_probe.py) separates non-generating preparation from a maximum of **four distinct synthetic calls, each capped at one generated token**, under a ten-minute combined budget. No ProcessBench material, answer-quality objective or benchmark admission is part of that design.

Review scope: the source audit, draft controller and [prospective diagnostic protocol](pilot/RUNTIME_CACHE_DIAGNOSTIC_PROTOCOL.md) were read offline. Execution remains subject to their independent review and freeze. An explicit service setting plus the backend's disabled-cache initialization message can establish uptake. Resources around a completed tiny workload can establish only that **those operations, during that observed office workload**, stayed inside the guards. Report aborted/partial probes as such. Count any generated tokens/calls separately as runtime diagnostics; a debug-only load remains a non-generating operation.

A pass would not establish that the cache caused earlier pressure, that 20 long generations now fit, that normal office load is stable across days, that a larger checkpoint is eligible, or that a model can perform the research task. The archived default-cache session is not a matched causal control. Keep the same model identity, 2,048 context, KV representation, thread count and resource guards; no additional cache settings should be tuned in response to probe results. The old scientific gate remains closed regardless of this engineering outcome.

## Concrete next offline study-design decision

**Develop a proposal about answer updating under evidence and user confidence, using short arithmetic questions with executable ground truth.** Limit the proposed measurement to final answer correctness and changes between turns. This is a candidate direction, not a verified research gap or an authorization to generate new model answers.

Deliver these four artifacts for human review before another scientific run:

1. **A one-page question and estimand.** For example: among questions initially answered correctly, how much does a confident unsupported suggestion increase adoption of an incorrect answer relative to an otherwise matched neutral suggestion? Separately, among initially wrong answers, how often does a correct, explicit calculation support a correction? Report the complete baseline coverage alongside these conditional groups. These are different denominators and must not be merged into one “sycophancy” score.
2. **A small development set with exact checks.** Draft roughly 12 problem families with short integer arithmetic and distinct substitutions. A deterministic checker supplies the correct answer and verifies every proposed corrective calculation. A human checks the language, units, ambiguity and whether the evidence actually supports its conclusion. These drafts are development material; future held-out questions must come from reserved families/instances whose outcomes have not been inspected.
3. **Matched follow-up controls.** Cross confidence wording with presence/absence of an explicit calculation; hold the suggested answer fixed within a comparison. Include both true and false suggestions and neutral repetition controls. Match length and content as closely as the manipulation permits, randomize execution order prospectively and keep independent conversations for paired conditions. This allows separate investigation of sensitivity to confidence and responsiveness to valid evidence without treating every answer change as a failure.
4. **A feasibility and novelty decision.** Check the closest rational-updating/sycophancy work already in the [novelty audit](NOVELTY_AUDIT.md), specify the unresolved contribution, and decide whether this design would resolve it. Prespecify a short output interface, denominators for format failures, baseline coverage and a task-specific adequacy requirement justified by the intended effect. A new task's rule must be chosen before observing its outputs; it does not revise the failed ProcessBench threshold. If there is no clear additional contribution, stop or redesign before collecting data.

Allocate the next 4–6 human hours to reading the nearest papers, drafting these controls and manually checking examples. AI agents can assist with drafts, exact checkers and independent review, but the researcher should own the hypotheses, example validation and interpretation. No part of this offline work requires a quiet computer or loading another model.

## Conditions before any later inference decision

First establish that a short, separately frozen workload can coexist with normal office use under unchanged guards. A one-token cache probe alone is insufficient: any later representative runtime/interface check needs its own bounded design, fresh synthetic inputs, explicit call accounting and a stop rule. Do not automatically extend the probe into calibration.

Only after a task and runtime are both eligible should one model and one new calibration be considered. Preserve all previously exposed cases as development evidence and keep the original 40 evaluation cases unused. If full ProcessBench critique is still deemed necessary, the existing 18/20 usability and 8/10-per-class adequacy requirements continue to govern that role; there is no permission here to lower them. A future Qwen decision additionally needs Qwen-specific renderer/token/response-channel validation and a frozen thinking mode with an honest generation-budget description. Its eligibility remains deferred, and no Llama context-fit result transfers to it.

If normal office use cannot support even the eventual short-task workload, pursue offline design, literature synthesis and collaboration until the constraint changes. The present feasibility record demonstrates careful experimental decisions; it does not itself establish an alignment contribution or conference acceptance.
