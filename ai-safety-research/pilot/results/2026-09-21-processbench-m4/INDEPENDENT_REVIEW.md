# Independent outcome review — September 21, 2026

**Outcome: resource preflight blocked; no ProcessBench subject experiment ran.** This review inspected controller-side evidence and source code only. It made no hardware connections or model requests and did not modify frozen execution code.

## Evidence and provenance

- The archived `preflight.json`, `cleanup.json`, `m4-inventory.json`, and `transport-readonly-check.json` are byte-identical to their original controller run files.
- The preflight, resource helper, SSH adapter, service helper, runner, and M4 session policy exactly match execution commit `017f1d708943876bda16bba67cc32b97c9ebaa14`. The complete transport binding, including bundled source, transformed stream, worker, service-helper and policy hashes, matches the saved preflight.
- The original service log's launch-code hash matches the exact `REMOTE_CODE` in that committed service helper. The full log's SHA-256 is `0dedaeb60f973e33f342ca584df251d32c5ca01d9e7b31e11a762c15fca23a5c`; published lifecycle events are extracted from this controller-retained log.
- Independent regeneration from the pinned dataset and prompt reproduced all 60 jobs, with 60 distinct problem groups and job hash `97e9f98f7bfdc9976111b98e8f063447b6f89f2d67a455f582f1264e9420a9d5`, exactly matching the preflight. Dataset, prompt and selection hashes also passed the existing reconstruction checks.
- The inspected runtime identity is Llama-3.2 3B Q4_K_M on Ollama 0.34.0; recorded model, template, parameters, bundled backend and library hashes match the frozen pins. The M4 inventory reports 16 GiB RAM and Python 3.9.6.

## Observed result

The preflight logged six received API operations: two resident-model checks, one version check, one model-list check, one model-description check, and **one debug-only chat request**. Reviewed source sends `_debug_render_only: true`; the immediately following resource check stopped execution before response interpretation or tokenization. There are **zero validated token counts, zero subject completions, and no calibration/evaluation scores**. Runtime loading included its ordinary internal warmup; zero subject completions does not mean zero model computation.

| Resource | Pre-load baseline | Immediately after debug loading |
|---|---:|---:|
| Kernel pressure level | 1 | 2 |
| Reported memory free | 36% | 15% |
| Swap used, bytes | 7,861,111,357 | 9,541,055,938 |
| Cumulative swapouts, bytes | 36,507,942,912 | 38,187,892,736 |

Swap usage increased by **1,679,944,581 bytes (1,602.12 MiB)** and swapouts by **1,679,949,824 bytes (1,602.125 MiB)**. All four fixed resource limits failed. Existing baseline swap alone was not the rejection criterion. These are shared-machine observations, not an isolated causal estimate of model memory consumption.

The recorded preflight lasted **6.679 seconds**, including a **4.454-second** debug request. This interval excludes earlier service startup and read-only setup and is not total research-session time.

## Cleanup and interpretation

The service log records requested STOP, server return code 0 and owned process-group absence. A separate saved cleanup observation, approximately **42.752 seconds after preflight start**, reports both the public port 11435 and observed backend port 58358 closed, no owned processes, and the owned group absent. Pressure returned to level 1 with 42% memory free; swap usage and cumulative swapouts remained elevated. Full resource recovery is therefore not claimed.

The independently rerun offline ProcessBench suite passed **61 tests**, including the seven service lifecycle tests. Tests support implementation checks; the live outcome remains a **failed resource preflight**. This evidence supplies no benchmark accuracy, no model ranking, and no conclusion that the same model cannot run under different machine conditions. Both reserved cohorts remain unused, and no inference retry is authorized by this review.
