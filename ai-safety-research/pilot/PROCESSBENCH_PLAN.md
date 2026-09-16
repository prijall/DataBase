# ProcessBench interface: local measurement-validation plan

Prepared September 16, 2026. **Offline preparation; zero new model calls.** The prior 232 calls and their frozen scores are unchanged. This is a feasibility adaptation, not a replication of published model scores or an alignment intervention.

## Why this next step

Our binary screen produced constant acceptance from Llama and unusable truncated prose from Qwen. The next step tests a published interface that permits critique before an error index. ProcessBench provides expert-labeled solutions with errors at different paragraph positions. This addresses an important limitation of our first-step-only synthetic examples, but does not isolate the cause of earlier failures. Data, task, prompt, extraction and generation allowance all change together.

The [source audit](PUBLISHED_INTERFACE_AUDIT.md) specifies the exact upstream behavior; the [offline verification report](processbench/VERIFICATION.md) records implementation and selection checks. [Provenance](processbench/provenance.json) pins source revisions and file hashes. The existing installed Llama-3.2 3B model is the single planned critic; we will not use the benchmark solution's `generator` field as the identity of our critic. Qwen's failed binary screen remains archived; no second model or new weight download is part of this phase.

## Dataset and separation

- Source: the pinned ProcessBench `gsm8k` domain, 400 solutions, independently counted as 193 error-free and 207 erroneous. This is a benchmark domain, not an official training split.
- Independent inspection found 375 distinct exact problem strings. All solutions whose problem strings match after whitespace normalization belong to one group. This guards against repeated textual problems; it does not prove absence of semantic paraphrases or model pretraining contamination.
- Reserve **20 calibration examples** (10 error-free, 10 erroneous) and **40 evaluation examples** (20 of each). Select deterministically using hashed group ordering, without model outputs. Save exact IDs, group hashes, selection parameters, class counts and input hashes in [selection.json](processbench/selection.json).
- A group cannot appear in both portions. Unselected siblings of a selected group remain excluded from the other portion. Within each portion, choose at most one solution per group so there is no repeated textual problem in the planned sample.
- The evaluation portion is held out from our prompt development only. It is a small balanced subset of a public benchmark, not a private test set or a representative estimate for all mathematics.
- Existing synthetic traces are not added to either portion. Do not inspect evaluation model outputs during calibration, swap difficult cases, or move calibration successes into evaluation.

## Planned local configuration

| Setting | Fixed choice for this adaptation |
| --- | --- |
| Critic | Installed `llama3.2:3b`, Q4_K_M |
| Expected model digest | `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72` |
| Execution | Existing Ollama, local loopback only, one request at a time |
| Prompt | Hashed official critic template, one user message, original paragraph text, zero-based tags; no added task system prompt |
| Generation | Temperature 0, seed 42, one sample; no voting or JSON constraint |
| Context / generation ceilings | 8,192 total context tokens / 1,024 generated tokens |
| CPU threads / residency | Two threads / 30-second keep-alive |
| Per-request deadline | 90 seconds, followed by cancellation and stop on timeout |
| Session budget | At most 60 attempted subject requests and 90 minutes of combined wall time, including loading, pauses and failed calls |

These are prospective settings. The paper's ordinary greedy critic permits **8,192 generated tokens** and uses a different model/backend; our 1,024-token ceiling is a substantial resource adaptation. A failed capped run cannot establish inability under the published configuration. No causal comparison with our prior 16-token binary screen is planned.

The current host is the shared M1 with 8 GiB RAM. The context allocation's memory fit and throughput are **unmeasured**. Before execution, the runner must record Ollama version, exact model digest and chat-template hash, verify that the installed template adds no unintended task-specific system instruction, and verify each selected prompt's token count plus generation reserve fits the context. Character/byte summaries in the offline manifest are preliminary size checks, not token measurements. Do not silently truncate problem text or steps. If a reliable token preflight is unavailable, resolve it before running the cohort.

Also check other inference activity and available memory. Stop for sustained memory pressure, disruptive swap, office work interference, a model/version mismatch or an unverified context fit. The runner must reserve at least one full request deadline plus cleanup time before starting another call. A client timeout alone does not prove server cancellation: verify that this request has ended before resuming or unloading our model; if cancellation cannot be verified, stop the session and report the unresolved server state. The 90-minute cap includes overhead, so it may permit fewer than 60 requests. Do not evict another user's workload or automatically use a Tailscale node. A failed infrastructure preflight produces a logged blocked run, not missing examples silently removed from denominators.

## Scoring and reporting

The primary benchmark-compatible prediction is the **last boxed integer** in the response. `-1` means no erroneous paragraph; otherwise the gold label is a zero-based earliest-error index. Exact-index matches are required: rejecting a solution at the wrong paragraph is incorrect. Preserve upstream extraction behavior even when it accepts later prose, multiple boxes or unusual integer spellings.

Report exact accuracy separately for error-free and erroneous solutions, their denominators, and the harmonic mean of the two accuracies (called F1 by ProcessBench). This is not precision/recall F1. If both component accuracies are zero, report a local harmonic-mean convention of zero and disclose that the upstream expression has an undefined zero denominator. If either class is absent, report the aggregate as unavailable. Also report overall exact-match accuracy, malformed outputs, out-of-range indices, length stops and request errors.

Retain two distinct records:

1. **Official-compatible match:** extraction and integer equality alone, including a boxed answer present in a length-stopped response. This matches the inspected greedy scorer's lack of a finish-reason filter.
2. **Completion-gated local match:** requires a normal completed response and an in-range integer as well as the correct label. This additional measurement determines local feasibility; it must not replace or be mislabeled as the official score.

Missing or failed calls count as unsuccessful against the planned denominator in the local feasibility report. If a session stops early, report attempted coverage and the reason, and label the planned-cohort score accordingly; do not present a partial run as a completed benchmark score. Conditional accuracy is unavailable when there are no usable outputs. Do not salvage alternative boxes, infer intended labels, or rescore older experiments under these rules.

## Stages and stopping rules

1. **Offline phase (this increment):** verify pinned downloads, implement prompt construction and greedy scoring, compare against upstream semantics on synthetic fixtures, and save a reproducible grouped selection. No inference.
2. **Runner preparation (next increment):** implement resumable local execution, token/context and memory preflights, cancellation, timeout logging, budget accounting and exact provenance. Independently review the runner and freeze its code/configuration commit before subject inference. No automatic run is triggered by this document.
3. **Calibration:** attempt the 20 fixed calibration cases once each, subject to infrastructure stop rules. Advance only with all 20 records, at least 18 normally completed in-range predictions, and **at least 8/10 completion-gated exact matches in each class**. The 18/20 condition measures interface usability; the 8/10 conditions are deliberately demanding task-adequacy requirements for our intended intervention study. A failure of the latter does not invalidate the benchmark interface or mean we failed to implement it faithfully. These are pragmatic engineering thresholds, not a statistical power calculation or evidence of general competence.
4. **Evaluation:** only after passing calibration, run the 40 fixed evaluation cases with identical settings. No prompt edits, resampling, outcome-based case exclusions or budget increases. Report all outcomes even if performance falls. Use the same 80% per-class exact-match threshold as a descriptive suitability check; passing is not proof of a contribution.
5. **If calibration fails:** stop this planned cohort; leave evaluation unused. Inspect failures, document the failure mode, and decide whether a different capable local model or a different research question is justified. A revised configuration requires a new dated development plan and a fresh evaluation reservation; do not repeatedly tune on these 40 examples.

Count actual execution against the user's nine combined machine-hours per week; this phase caps itself at 1.5 hours. The timing estimate is a ceiling, not a throughput forecast. No process remains scheduled to run later.

## Interpretation and research value

The small screen can determine whether an installed model and published-style interface provide usable error-localization measurements on these cases. It cannot demonstrate an anti-sycophancy effect, novelty, scaling behavior, causal explanation for protocol differences, or likely conference acceptance. Public benchmark contamination, small sample size, quantization and changed generation settings limit interpretation.

If the measurement works, return to the actual research question: matched standalone and conversational judgments under controlled interventions, with varied error positions, matched error counts, correct/wrong conclusions and an independently reviewed held-out set. That requires another literature/novelty decision and experimental design. This preparation improves research reliability; it is not itself the intended paper contribution.

## Reproduce the offline preparation

Run from `ai-safety-research/pilot`. Downloads are public source files only, not weights; the adapter itself makes no network or model calls. `runs/` is ignored. The committed provenance records exact URLs and byte hashes; the adapter refuses mismatching input bytes.

```sh
mkdir -p runs/processbench-source
curl -fL 'https://huggingface.co/datasets/Qwen/ProcessBench/resolve/3bdcd5371ed567559a78f559c01c13a6deee7604/gsm8k.json' -o runs/processbench-source/gsm8k.json
curl -fL 'https://raw.githubusercontent.com/QwenLM/ProcessBench/e8024636bcabdf8bd514440551b531d3f90dd18b/code/templates/critique_template.txt' -o runs/processbench-source/critique_template.txt
python3 processbench_prepare.py --data runs/processbench-source/gsm8k.json --prompt runs/processbench-source/critique_template.txt --provenance processbench/provenance.json --out runs/processbench-prepared
python3 -m unittest discover -p 'test_*.py'
```

The preparation output contains selection metadata, not model responses or evidence of successful verification. Upstream examples, prompt and evaluator code are not vendored in this repository. Cite Zheng et al., *ProcessBench: Identifying Process Errors in Mathematical Reasoning*, ACL 2025, [official paper](https://aclanthology.org/2025.acl-long.50/), when using the benchmark.
