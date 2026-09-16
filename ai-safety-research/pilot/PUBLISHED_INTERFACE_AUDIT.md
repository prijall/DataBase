# Published verification interface: ProcessBench audit

Audited September 16, 2026. **This source audit involved no model inference, weights or changes to previous results.** The accompanying offline preparation separately downloaded the pinned GSM8K examples and recomputed their counts. This document informs a separate measurement-validation plan; it does not authorize a new run or promise improved results.

## Decision

Use ProcessBench's **generative critic interface** as the reference specification for the next offline implementation. It permits a written critique and asks for one error index. This is materially different from both our three-field freeform-v3 verdict and our explanation-free binary screen. A small local implementation should be described as a **ProcessBench-interface adaptation**, with all deviations listed. It must not be presented as reproduction of the paper's model scores.

The immediate deliverable is a verified prompt builder and scorer with synthetic fixtures, followed by a frozen data-selection and resource plan. No additional inference follows automatically from this audit.

## 1. Immutable primary sources

| Component | Inspected version | Reference |
| --- | --- | --- |
| Paper | arXiv `2412.06559v4`, May 26, 2025; ACL 2025 publication | [Versioned manuscript](https://arxiv.org/html/2412.06559v4), [official proceedings](https://aclanthology.org/2025.acl-long.50/) |
| Official evaluation repository | Commit `e8024636bcabdf8bd514440551b531d3f90dd18b`, May 20, 2025 | [Pinned source tree](https://github.com/QwenLM/ProcessBench/tree/e8024636bcabdf8bd514440551b531d3f90dd18b) |
| Critic template | `code/templates/critique_template.txt`, 488 bytes | [Exact template](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/templates/critique_template.txt) |
| Evaluation implementation | `code/run_eval.py` | [Pinned implementation](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/run_eval.py) |
| Dataset | Hugging Face revision `3bdcd5371ed567559a78f559c01c13a6deee7604`, December 27, 2024 | [Pinned dataset repository](https://huggingface.co/datasets/Qwen/ProcessBench/tree/3bdcd5371ed567559a78f559c01c13a6deee7604) |
| Dataset card | `README.md` at that revision | [Pinned card](https://huggingface.co/datasets/Qwen/ProcessBench/blob/3bdcd5371ed567559a78f559c01c13a6deee7604/README.md) |

The repository and dataset revisions were resolved through their official metadata APIs. Source files and metadata were read in memory. Hashes below refer to the exact retrieved bytes, before whitespace changes:

```text
critique_template.txt
  SHA-256 0e7dba24bfaa9dea379907e11b8dc701c6cd6e74453ab2ffc9b1d63237cc4434
run_eval.py
  SHA-256 66d09fc7a3d20d46f166d4bba4e04835f3d7473e1534b6908cd9045aefc7b704
dataset README.md
  SHA-256 525e4455e981213919c574146196258ddb63986c11637116f58d7ba8b990c6f5
```

## 2. Exact prompt and label convention

The linked, hashed **critique template is the exact prompt authority**; do not reconstruct it from the paraphrase here. The evaluator reads and strips the template before substitution. Each original solution paragraph is enclosed in `<paragraph_i>` and `</paragraph_i>` tags, using zero-based indices, with the step text preserved. The model receives the problem and tagged solution in **one user message, without a task-specific system message**. The model tokenizer applies its chat template with the generation prompt enabled. [Prompt construction, lines 19–32 and 46–47](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/run_eval.py#L19).

The task is paragraph-by-paragraph critique followed by the earliest erroneous paragraph index in `\boxed{...}`; `-1` means every paragraph is correct. The template contains literal `{problem}` and `{tagged_response}` substitution fields and escaped braces for the final boxed expression. The local adapter must preserve those substitutions and byte-check the template before constructing prompts. [Exact template](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/templates/critique_template.txt).

**Indexing differs from our synthetic pilot:** ProcessBench uses `0` for an error in the first paragraph and `-1` for no error. Our earlier pilot used `1` for its first false equality and `0` for a valid trace. Never apply the old mapping to ProcessBench labels. The dataset's `final_answer_correct` is a separate attribute and must not substitute for its process-error `label`. [Paper, §3.1 and §3.3](https://arxiv.org/html/2412.06559v4).

## 3. Official extraction and scoring behavior

The following describes the **greedy** code path:

- Extract the last regex match of `\\boxed\{([^}]*)\}` anywhere in the generated text; strip its contents; convert with Python `int`. Missing boxes or failed conversion produce `None`.
- Compare the resulting integer directly with the gold label. Missing, nonnumeric, and out-of-range predictions remain incorrect; they are not dropped.
- Multiple boxes, later prose, and normal Python integer spellings are accepted. There is no range check, contradiction adjudication, or completion/length-stop filter.
- Compute exact-index accuracy on erroneous examples and accuracy on error-free examples separately. Their harmonic mean is called F1; it is not precision/recall F1. A wrong error location fails even if the model correctly rejects the solution.

[Extractor and greedy path](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/run_eval.py#L12), [metrics](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/run_eval.py#L117).

**Implementation implications for our adapter:** preserve a field for the official-compatible prediction and score. Add diagnostics for malformed, out-of-range, multiple-box, and truncated outputs without silently changing that primary definition. If a separate completion-gated result is desired, name and report it as an adaptation. The upstream harmonic-mean expression lacks a zero-denominator guard: explicitly document any local convention for both class accuracies being zero; do not hide empty classes.

The optional voting path defaults to eight generations. It omits missing extractions, votes on extracted strings before integer conversion, then converts the winning string. It does not first combine equivalent numeric spellings or exclude nonnumeric strings from voting. No voting implementation is necessary for an initial greedy adapter. [Voting branch](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/run_eval.py#L97).

## 4. Dataset, splits, and license metadata

The pinned dataset card declares **Apache-2.0**, English, and one `default` configuration containing four named splits. These names denote benchmark domains, not a train/development/test partition:

| Split | File | Cases | Error-free / erroneous |
| --- | --- | ---: | ---: |
| `gsm8k` | `gsm8k.json` | 400 | 193 / 207 |
| `math` | `math.json` | 1,000 | 406 / 594 |
| `olympiadbench` | `olympiadbench.json` | 1,000 | 339 / 661 |
| `omnimath` | `omnimath.json` | 1,000 | 241 / 759 |

Split declarations and license come from the [pinned card](https://huggingface.co/datasets/Qwen/ProcessBench/blob/3bdcd5371ed567559a78f559c01c13a6deee7604/README.md); counts come from the [paper's Table 2 and Appendix B](https://arxiv.org/html/2412.06559v4). Counts have not been independently recomputed from downloaded examples in this audit. Fields include `id`, `generator`, `problem`, `steps`, `final_answer_correct`, and `label`.

The inspected GitHub tree contains **no repository license file**, and the dataset card does not establish a license for the separate code repository. Do not label copied evaluation code as Apache-2.0 on that basis. Preserve dataset attribution and provenance; review terms before redistributing upstream source material. An independently written adapter can document behavior through pinned references instead of silently relicensing copied files. [Complete official repository tree](https://github.com/QwenLM/ProcessBench/tree/e8024636bcabdf8bd514440551b531d3f90dd18b).

There is no official calibration split to adopt. A subset reserved for calibration would be **our split**, requiring a saved selection manifest. Keep all solutions sharing an underlying problem together when defining disjoint portions; verify duplicate/problem identity before claiming separation. Do not select examples using the evaluated model's successes or reuse calibration results as held-out evidence.

## 5. Model, token, and runtime settings

The official greedy script specifies temperature 0, seed 42, and **8,192 maximum generated tokens**, increased to 32,768 when the model path contains `QwQ`. It does not set a fixed context length. Default voting uses eight samples, temperature 1 and top-p 0.9; Qwen2.5-Math instead uses temperature 0.7, top-p 0.8, and top-k 20. [Generation settings](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/run_eval.py#L57).

The published main open-model results use voting; greedy results are reported separately. The paper's evaluation used vLLM on eight A100 80GB GPUs. Its critic-model comparisons include Qwen2, Qwen2.5, Qwen2.5-Math, Qwen2.5-Coder, Llama-3-family checkpoints, and QwQ-32B-Preview. The installed Llama-3.2 3B and Qwen3-VL 2B models do not reproduce the evaluated checkpoints. [Paper, §4.1 and Appendices D/F](https://arxiv.org/html/2412.06559v4).

Pinned runtime requirements are PyTorch 2.4.0, Transformers 4.46.1, and vLLM 0.6.3.post1. The script requests CUDA tensor parallelism, so running it unchanged is not an established option on the current Macs. [Requirements](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/requirements.txt), [runtime construction](https://github.com/QwenLM/ProcessBench/blob/e8024636bcabdf8bd514440551b531d3f90dd18b/code/run_eval.py#L50).

**Local planning inference:** an 8,192-token output allowance cannot fit within our previous 2,048-token total context alongside the input. A future runner must tokenize inputs and explicitly reserve output capacity, or disclose a lower output ceiling as a resource adaptation. Do not truncate benchmark steps to fit. Runtime and memory feasibility remain unmeasured; source-level settings alone do not prove that the published configuration fits a shared 8GB Mac.

## 6. What can be reproduced locally—and what cannot yet be claimed

| Proposed artifact or run | Defensible description | Conditions |
| --- | --- | --- |
| Offline prompt/scoring adapter | Reproduction of the inspected interface semantics | Pinned template, exact tagging/indexing, parity fixtures; no model-performance claim. |
| Fixed small subset on an installed quantized model through Ollama | Local ProcessBench-interface feasibility adaptation | Disclose subset, model/checkpoint, quantization, backend, context/output limits, parser and completion policy. |
| Complete GSM8K split with an installed model | Evaluation of that model on the GSM8K split | Preserve the benchmark interface and report all 400 cases; still not reproduction of a published model's result. |
| Reproducing an Appendix F greedy score | Published-result replication | Match the named checkpoint, data revision, prompt/chat-template behavior, scoring, and generation settings; investigate remaining backend/dtype differences. |
| Reproducing main-table voting results | Separate, larger replication | Match the voting procedure and generation settings as well; not implied by a one-sample pilot. |

The **minimum useful next artifact** is the first row. For a later inexpensive screen, a frozen small GSM8K selection with both process-label classes would establish only interface feasibility. No particular sample size or token cap is approved here; those choices belong in the resource and selection plan before inference. A class-balanced selection has a different distribution from the full split and must be labeled accordingly.

## 7. Why inspect this interface after our failures?

The reference interface gives generated critique somewhere to go, rather than treating any explanation as an error. Its scalar verdict also avoids requiring a separate regenerated answer and mutually consistent three-field JSON. These are reasons to test a published interface, **not evidence that it will solve our problems**.

Our Qwen binary outputs violated the whole-label contract before they were cut off; increasing the token allowance alone could not make those existing prefixes valid whole-label responses. ProcessBench changes the output contract as well as allowing a longer generation, so it is a distinct protocol. Llama's constant `VALID` responses demonstrated a classification failure under the binary screen; accommodating critique does not establish that it will detect errors. The ProcessBench task additionally requires error localization and contains more demanding mathematics, which could expose further limitations.

Any observed improvement would combine changes in task, data, prompt, response format, extraction, and generation allowance. It cannot be attributed to a single cause. New interface scoring also must not be applied retroactively to make the previous frozen gates pass.

## 8. Offline acceptance checks before any future run

1. Verify the template hash and exact prompt construction on synthetic fixtures, including zero-based paragraph tags, preserved internal whitespace, and absence of leaked gold fields.
2. Check scorer parity on missing boxes, nonnumeric last boxes, multiple conflicting boxes, signed integers, leading zeroes, out-of-range indices, nested braces, and boxed predictions followed by prose. Preserve the last-box policy even where it is permissive.
3. Keep official-compatible match, extraction diagnostics, and completion diagnostics separate. A completed response and an extractable response are different properties.
4. Define metric behavior for absent classes and a zero harmonic-mean denominator. Report class counts and component accuracies alongside the aggregate.
5. Pin the data revision, selected IDs, grouping/split logic, runtime/model identity, chat template, token budget, and stopping rules before inference. Verify resource fit without assuming the old 2K context suffices.
6. Keep this phase offline until the implementation, provenance, selection plan, and resource plan have been reviewed. No model request, weight acquisition, or broad benchmark sweep is part of this source audit.

Remaining uncertainties are concrete: local runtime fit, dataset-level duplicate/problem grouping, model suitability, and whether any eventual result supports a distinct research contribution. This audit resolves the reference interface; it does not resolve those questions.
