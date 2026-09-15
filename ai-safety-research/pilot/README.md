# Local reasoning-validity pilot

[Research state](../RESEARCH_STATE.md) · [Novelty audit](../NOVELTY_AUDIT.md) · [Inspect all examples](EXAMPLES.md)

This is an unsteered development screen, not the final benchmark or a novelty claim. It tests local inference, scoring, and whether the task exposes useful variation before investing in activation steering.

**Current result:** [Freeform-v3](results/2026-09-15-freeform-v3/README.md) produced a complete Llama baseline (60/120 strictly parsed) and a stopped Qwen initial screen (2/10 parsed). Both failed their applicable gate. The [earlier 42-call report](results/2026-09-15-protocol-screen/README.md) remains archived. The commands below reproduce development work; no intervention study has run. Results are incorporated in the [working manuscript](../paper/manuscript.md).

## Requirements and execution

Python 3.10+ and a running local Ollama server at `127.0.0.1:11434`, with the chosen model already installed. No Python package installation, API keys, external inference, or automatic model downloads are needed. The server's normal local template is used; this runner does not expose activation hooks.

From this directory:

```sh
python3 pilot.py check
python3 -m unittest -v
python3 pilot.py run --model llama3.2:3b --freeform --out runs/llama32-freeform-v3 --max-calls 10 --max-seconds 600
# Only after passing the frozen initial gate:
python3 pilot.py run --model llama3.2:3b --freeform --out runs/llama32-freeform-v3 --max-calls 110 --max-seconds 2400
python3 audit_results.py --out runs/llama32-freeform-v3
python3 presentation_audit.py --out runs/llama32-freeform-v3
```

Repeating the run command resumes it. Completed calls are not regenerated. Dataset, code, model digest, server version, and protocol must match to resume; otherwise choose a new directory. Use the recorded commit when reproducing an older protocol. Do not edit a dataset or script midway through a run. Avoid simultaneous writers to the same directory. Malformed or duplicate log records stop loading instead of silently being discarded.

The time limit applies per invocation, reserves one request timeout before starting a call, and stops between requests. A timed-out request may continue briefly on the server; the limit is not a global process kill. Sessions record client elapsed time; independently manage the combined nine-machine-hour weekly budget across all machines. Start one runner at a time on shared hardware.

## What is measured

- Ten initial answers.
- Eight correction variants per question: four evidence conditions × neutral/confident framing.
- Three standalone trace reviews per question.

Total: 120 completions. Initial answers are preserved verbatim in all correction branches, including malformed initial outputs. The malformed cohort is reported separately from naturally wrong parseable answers.

The model returns JSON fields `answer`, `trace_valid`, and `first_error`. First-error indices are 1-based; zero means no erroneous equality; null means no trace. Exact parsing deliberately treats malformed or internally inconsistent JSON as unsuccessful, even if part of the answer looks right. Raw outputs remain available for auditing this choice.

With `--worked`, the separately named `worked-v2` protocol additionally requests a nonempty `working` string before the verdict fields and permits up to 384 generated tokens instead of 128. This revision followed a failed `direct-v1` screen. It changes the system prompt, available written calculations, and token limit together; it is not a controlled attribution of the failure to any one factor. Written calculations are retained for inspection but are not scored as proof of faithful internal reasoning.

With `--freeform`, [v3](PROTOCOL_V3.md) permits ordinary calculations before one strict `<FINAL_JSON>` block, omits constrained JSON decoding, and permits 512 generated tokens. It changes several factors together and does not identify their separate effects. Output modes are mutually exclusive. Initial advance requires at least 8/10 parseable and 5/10 correct answers. The full-run parsing gate requires at least 90% overall parsing and 8/10 per trace cell. Both tested models failed their applicable gate.

`audit_results.py` reports all-call and parsed-only rates, valid acceptance versus invalid rejection, initial cohorts, exact suggestion adoption, paired framing discordances, and truncation/format overlap. The separately specified [post-hoc presentation audit](PRESENTATION_AUDIT_PLAN.md) recovers only explicit terminal fields; it never changes primary scores or passes a failed gate.

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
- `AUDIT.md`: detailed descriptive analysis from stored strict scores.
- `PRESENTATION_AUDIT.md` and `PRESENTATION_RECOVERY.jsonl`: separate post-hoc diagnostics, including preserved original scores and extracted candidates.

Transient runs are ignored by Git. Small, reviewed research-only run artifacts can be copied into a versioned `results/` directory so the reported numbers are auditable from home. Large outputs and model weights remain outside Git; record their locations and hashes in research notes and maintain a personal backup.

## API references

The runner uses Ollama's [chat endpoint](https://docs.ollama.com/api/chat) and [installed-model inventory](https://docs.ollama.com/api/tags). JSON output formatting, greedy generation, and a fixed seed are recorded protocol choices; exact cross-device bitwise reproduction is not promised.
