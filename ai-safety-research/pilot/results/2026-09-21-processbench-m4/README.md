# M4 ProcessBench preflight — September 21, 2026

**Stopped at the resource gate. Zero generated answers; no calibration or evaluation attempted.** The existing total remains 232 completions. This is a runtime feasibility observation, not a model-accuracy result.

## What ran

Authenticated read-only inspection confirmed the Tailscale target as an Apple M4 with 16 GiB RAM. Its installed Llama-3.2 3B Q4_K_M model, Ollama 0.34.0, bundled backend and tokenizer identities matched the pinned configuration. No downloads or installations were performed.

The [session protocol](../../PROCESSBENCH_M4_SESSION.md), SSH transport and preflight were frozen at commit `017f1d708943876bda16bba67cc32b97c9ebaa14`. Research scripts and data were supplied through SSH in memory; research records were stored on the controller. The temporary localhost service used port 11435 and owned process group 36748. The ordinary Ollama service was not modified.

One explicitly non-generating debug-render request loaded the existing model with an 8,192-token context. The immediately following resource sample breached every prospective threshold, so the helper stopped before examining the returned render or tokenizing any prompt. Consequently, this run neither validates the corrected render parser live nor establishes context fit. There was no subject request or retry.

## Observations

| Resource | Before load | After load | After service cleanup |
| --- | ---: | ---: | ---: |
| Memory-pressure level | 1 (normal) | 2 | 1 (normal) |
| Free-memory percentage | 36% | 15% | 42% |
| Swap used (bytes) | 7,861,111,357 | 9,541,055,938 | 9,532,667,330 |
| Cumulative swapouts (bytes) | 36,507,942,912 | 38,187,892,736 | 38,187,892,736 |

Swap usage grew by 1,679,944,581 bytes (1.565 GiB), exceeding 256 MiB; additional swapouts were 1,679,949,824 bytes (1.565 GiB), exceeding 128 MiB. Normal pressure and at least 20% free memory were also required. These are system-wide measurements on a shared office Mac; they do not isolate the model's contribution from concurrent activity or prove this M4 can never run the configuration.

The preflight lasted 6.68 seconds. Independent read-only cleanup verification completed 42.75 seconds after preflight start: ports 11435 and 58358 were closed, the owned process group was absent, and no owned processes remained. Pressure normalized; swap usage remained elevated. The temporary service was also running idle during preparation before the preflight; the preflight duration is not total machine occupancy.

## Evidence

- [Raw preflight report](preflight.json): request audit, source/model/runtime hashes, resource snapshots, and explicit blocked status.
- [Cleanup observation](cleanup.json): fresh target-local resource, port and process-group checks.
- [Installed-model inventory](m4-inventory.json) and [read-only transport check](transport-readonly-check.json): metadata captured without generation.
- [Service lifecycle](service-lifecycle.json): start/stop events and hash of the controller-held full runtime log. The full log includes incidental startup environment output and is not published.
- [Derived summary](summary.json), [independent review](INDEPENDENT_REVIEW.md), and [archive checksums](SHA256SUMS).

No research files, datasets, scripts or results were persisted on the M4 or its external SSD. Existing model files were read in place. This describes the research workflow, not a forensic guarantee that macOS or the installed runtime wrote no ordinary caches, swap or logs.

## Next step

Keep this failed session closed. Arrange a quieter M4 window with more available memory, then document a fresh preflight with the same frozen gates. A smaller context would require a separate prospective configuration and exact token-fit validation. Do not relax the resource limits, reuse this blocked report, or interpret untouched cohorts as failed predictions. Calibration remains gated on a successful preflight; evaluation remains gated on the original calibration thresholds.
