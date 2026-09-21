# Local reasoning-validity pilot

[Research state](../RESEARCH_STATE.md) · [Novelty audit](../NOVELTY_AUDIT.md) · [Inspect all examples](EXAMPLES.md)

This is an unsteered development screen, not the final benchmark or a novelty claim. It tests local inference, scoring, and whether the task exposes useful variation before investing in activation steering.

**Current result:** the [verification-only screen](results/2026-09-16-verification-only/README.md) recorded sixty calls. Llama returned `VALID` for every trace; Qwen generated extra text and exhausted the sixteen-token limit on every call. Both failed the gate. The [v3 results](results/2026-09-15-freeform-v3/README.md) and [earlier 42-call report](results/2026-09-15-protocol-screen/README.md) remain archived. No intervention study has run. Results are incorporated in the [working manuscript](../paper/manuscript.md).

## Offline ProcessBench preparation

The [source audit](PUBLISHED_INTERFACE_AUDIT.md) and [bounded plan](PROCESSBENCH_PLAN.md) document the next measurement step. The independent [adapter](processbench_prepare.py) verifies pinned inputs and prepares separate calibration/evaluation selections without network or model calls. See the plan for download and reproduction commands. The [first live preflight](results/2026-09-16-processbench-preflight/README.md) stopped before subject inference, leaving both cohorts unused at that stage. The [September 21 M4 preflight](results/2026-09-21-processbench-m4/README.md) also stopped before subject inference: its immediate post-load memory guard failed before the corrected response reader or tokenization ran. Cleanup is verified; that session is closed and cannot resume.

## Latest ProcessBench session

The [2,048-token session](results/2026-09-21-processbench-small-context/README.md) passed sixty exact-token checks (290–789 prompt tokens) and verified the actual loaded context. It recorded six of twenty calibration responses: four usable, one correct, two malformed extractions, and no length stops or request errors. Memory pressure reached level 2 after the sixth response; the fixed guard stopped execution. Cleanup is verified. The archive now contains **240 generated completions**.

The new calibration has six used and fourteen unattempted cases; the original twenty-case calibration is retired and all forty evaluation cases remain untouched. The error class has one match in four observed cases, leaving at most seven matches out of ten even if every remaining case succeeded—below the fixed eight-match gate. The actual stop was resource pressure and the cohort remains incomplete; this arithmetic is not a completed accuracy estimate. Fixing memory alone cannot rescue that gate.

The screen is closed. No automatic retry or configuration change is authorized. Next work is targeted runtime/cache investigation and human review of the six outputs, preserving primary scores. The [implementation guide](PROCESSBENCH_SMALL_CONTEXT_IMPLEMENTATION.md) retains the executed configuration and reproduction commands, not an instruction to restart.

## Original ProcessBench local execution (reproduction reference)

The [execution addendum](PROCESSBENCH_EXECUTION.md) implements the bounded plan for the currently audited Mac/Ollama installation. The runner requires a committed protocol, an exact-token preflight report, and pinned source files. It refuses evaluation unless calibration passes. Do not reuse this machine-specific preflight on another computer or runtime version.

After downloading the source files using the [plan](PROCESSBENCH_PLAN.md), prepare ignored local jobs from this directory:

```sh
mkdir -p runs/processbench-session
python3 - <<'PYJOBS'
from pathlib import Path
import json
from processbench_run import load_jobs
jobs, _ = load_jobs(Path('runs/processbench-source/gsm8k.json'),
                   Path('runs/processbench-source/critique_template.txt'),
                   Path('processbench/provenance.json'), Path('processbench/selection.json'))
Path('runs/processbench-session/jobs.json').write_text(json.dumps(jobs) + '\n')
PYJOBS
python3 processbench_preflight.py --jobs runs/processbench-session/jobs.json --out runs/processbench-session/preflight.json
python3 processbench_run.py calibration --data runs/processbench-source/gsm8k.json --prompt runs/processbench-source/critique_template.txt --provenance processbench/provenance.json --selection processbench/selection.json --preflight runs/processbench-session/preflight.json --out runs/processbench-session/subject-run
```

Read the calibration summary before invoking `evaluation` with the same paths; the runner also enforces the gate. Preflight loads the existing local model but requests no generated answer. Preserve a blocked report or ambiguous attempt and inspect it; do not remove files to bypass a stop or reset the fixed session budget.

## Memory-only M4 transport

The reviewed [SSH transport](processbench_remote.py) uses an isolated target loopback service and sends Python code and input data through stdin and process memory. Research files and artifacts stay on the controller. The [session rules](PROCESSBENCH_M4_SESSION.md) describe service ownership, fixed target/runtime checks, a 90-second model-request deadline, a 100-second transport cap, and a 150-second reserve within the unchanged 90-minute cohort budget.

All September 21 M4 sessions are closed after resource stops. Preserve the first failed preflight and the second passed preflight with its two partial calibration records; **do not resume either closed session or change its settings**. The following original-profile commands are retained as reproduction references. Use the [smaller-context guide](PROCESSBENCH_SMALL_CONTEXT_IMPLEMENTATION.md) for the later, also closed screen:

```sh
python3 processbench_remote.py create-preflight --data runs/processbench-source/gsm8k.json --prompt runs/processbench-source/critique_template.txt --provenance processbench/provenance.json --selection processbench/selection.json --preflight runs/NEW-SESSION/preflight.json --out runs/NEW-SESSION/subject-run
# Only after the fresh preflight passes; retain the same paths and budget:
python3 processbench_remote.py calibration --data runs/processbench-source/gsm8k.json --prompt runs/processbench-source/critique_template.txt --provenance processbench/provenance.json --selection processbench/selection.json --preflight runs/NEW-SESSION/preflight.json --out runs/NEW-SESSION/subject-run
```

`NEW-SESSION` is a placeholder for a newly documented session. Use `evaluation` only after the unchanged calibration gate passes. The CLI durably records preflight dispatch before SSH and subject attempts before requests. Interrupted or ambiguous requests cannot be retried automatically; deleting a marker to reset the budget is not a valid resume.

## Verification-only reproduction

Use the separately frozen [protocol](VERIFICATION_ONLY_PROTOCOL.md) and [runner](verification_only.py). On macOS/Linux, from this directory with local Ollama running:

```sh
python3 -m unittest -v
python3 verification_only.py run --model llama3.2:3b --out runs/llama32-verification-only-v1 --max-calls 30 --max-seconds 600
python3 verification_only.py run --model qwen3-vl:2b-instruct --out runs/qwen3vl-verification-only-v1 --max-calls 30 --max-seconds 600
python3 verification_only.py summarize --out runs/llama32-verification-only-v1
```

Run models sequentially. These commands document the completed screen. The runner freezes thirty unique jobs per model, locks its output directory, preserves raw results atomically, and rejects changed code, dependencies, protocol, data or model settings on resume. Its summary separates lexical parsing, completed usable labels, truncation, primary valid/invalid performance and the secondary invalid/correct diagnostic. Missing or truncated outputs cannot pass as correct labels. The current integrated suite contains 127 tests, including 79 ProcessBench checks.

## Earlier freeform pilot: requirements and execution

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
