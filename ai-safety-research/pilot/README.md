# Local reasoning-validity pilot

[Research state](../RESEARCH_STATE.md) · [Novelty audit](../NOVELTY_AUDIT.md) · [Inspect all examples](EXAMPLES.md)

This is an unsteered development screen, not the final benchmark or a novelty claim. It tests local inference, scoring, and whether the task exposes useful variation before investing in activation steering.

**Current result:** Both direct-v1 and worked-v2 failed the initial suitability screen. See the [42-call diagnostic report](results/2026-09-15-protocol-screen/README.md). The commands below document reproduction; a full sweep is not recommended until the output protocol is revised.

## Requirements and execution

Python 3.10+ and a running local Ollama server at `127.0.0.1:11434`, with the chosen model already installed. No Python package installation, API keys, external inference, or automatic model downloads are needed. The server's normal local template is used; this runner does not expose activation hooks.

From this directory:

```sh
python3 pilot.py check
python3 -m unittest -v
python3 pilot.py run --model llama3.2:3b --worked --out runs/llama32-worked-v2 --max-calls 12 --max-seconds 180
```

Repeating the run command resumes it. Completed calls are not regenerated. Dataset, code, model digest, server version, and protocol must match to resume; otherwise choose a new directory. Do not edit a dataset or script midway through a run. Avoid simultaneous writers to the same directory. Malformed or duplicate log records stop loading instead of silently being discarded.

The time limit applies per invocation, reserves one request timeout before starting a call, and stops between requests. A timed-out request may continue briefly on the server; the limit is not a global process kill. Sessions record client elapsed time; independently manage the combined nine-machine-hour weekly budget across all machines. Start one runner at a time on shared hardware.

## What is measured

- Ten initial answers.
- Eight correction variants per question: four evidence conditions × neutral/confident framing.
- Three standalone trace reviews per question.

Total: 120 completions. Initial answers are preserved verbatim in all correction branches, including malformed initial outputs. The malformed cohort is reported separately from naturally wrong parseable answers.

The model returns JSON fields `answer`, `trace_valid`, and `first_error`. First-error indices are 1-based; zero means no erroneous equality; null means no trace. Exact parsing deliberately treats malformed or internally inconsistent JSON as unsuccessful, even if part of the answer looks right. Raw outputs remain available for auditing this choice.

With `--worked`, the separately named `worked-v2` protocol additionally requests a nonempty `working` string before the verdict fields and permits up to 384 generated tokens instead of 128. This revision followed a failed `direct-v1` screen. It changes the system prompt, available written calculations, and token limit together; it is not a controlled attribution of the failure to any one factor. Written calculations are retained for inspection but are not scored as proof of faithful internal reasoning.

Answer correctness, trace-validity correctness, and error localization are separate measures. A correct answer with false endorsement of its flawed supporting trace is visible in the raw scores. Summary ratios are descriptive counts, not statistically independent samples or confidence intervals.

## Checker and known design limits

Ground truth uses Python AST parsing restricted to integer literals, signs, parentheses, addition, subtraction, multiplication, and division, evaluated with exact rational arithmetic. No arbitrary `eval` or model judge is used. This certifies the displayed numeric equalities, not arbitrary natural-language arguments.

Each item has three trace variants. The invalid/correct trace contains two false equalities: one introduces a wrong intermediate expression and another returns to the correct calculation. The invalid/wrong trace has one false equality followed by locally valid steps. All first errors occur at step one. These are intentional plumbing examples; error count and position are confounds that must be corrected before a final study. Only two closely related arithmetic families appear, so this is not a general reasoning benchmark.

The examples and labels were prepared with AI assistance and checked mechanically. No independent human audit is claimed. The researcher should inspect [EXAMPLES.md](EXAMPLES.md) before finalizing any research dataset.

If every initial answer is correct, natural correction acceptance is **not estimable**. That would motivate new development problems, not synthetic mistakes represented as genuine model outputs. A successful runner does not establish a useful scientific effect.

## Outputs and continuing from home

Each run directory contains:

- `manifest.json`: model identity, quantization, template/code/data hashes, generation settings and code commit.
- `responses.jsonl`: exact conversations, server responses, timings and deterministic scores.
- `sessions.jsonl`: elapsed time for each execution slice.
- `SUMMARY.md`: counts and cohort denominators, regenerated by `python3 pilot.py summarize --out runs/llama32-worked-v2`.

Transient runs are ignored by Git. Small, reviewed research-only run artifacts can be copied into a versioned `results/` directory so the reported numbers are auditable from home. Large outputs and model weights remain outside Git; record their locations and hashes in research notes and maintain a personal backup.

## API references

The runner uses Ollama's [chat endpoint](https://docs.ollama.com/api/chat) and [installed-model inventory](https://docs.ollama.com/api/tags). JSON output formatting, greedy generation, and a fixed seed are recorded protocol choices; exact cross-device bitwise reproduction is not promised.
