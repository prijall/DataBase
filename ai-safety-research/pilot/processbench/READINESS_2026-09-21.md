# M4 readiness and closed session — September 21, 2026

**Outcome: resource preflight blocked; cleanup verified.** The archive remains at **232 generated completions**. No ProcessBench subject answer or exact prompt token check completed, and both reserved cohorts remain unused. Read the [archived report](../results/2026-09-21-processbench-m4/README.md).

## Completed checks

- Verified authenticated access to the Apple M4 with 16 GiB RAM, Python 3.9.6, Ollama 0.34.0, and matching installed model, template, default-parameter, tokenizer executable and library identities.
- Completed independent offline review of the corrected preflight and memory-only SSH transport. The integrated suite passes 109 tests, including 61 ProcessBench checks.
- Froze the session at commit `017f1d708943876bda16bba67cc32b97c9ebaa14` under the [M4 session rules](../PROCESSBENCH_M4_SESSION.md). The isolated service used target loopback port 11435; resource and process checks ran on the M4.
- Supplied code and request inputs through SSH stdin and process memory. No research scripts, datasets, results, or artifacts were persisted on the M4. Research records were saved on the controller for the GitHub archive.

## Observed stop and cleanup

The first explicitly non-generating debug-render request completed, but its immediate post-load memory check failed. Pressure rose from level 1 to level 2, free memory fell from 36% to 15%, and swap usage and swapouts each grew by approximately 1.565 GiB. All four original resource guards were crossed. The corrected response reader was present but not reached: the guard stopped execution before response validation and exact tokenization. This check therefore does not finish live validation of that reader.

The report spans 6.679 seconds from budget start. Independent cleanup was recorded 42.752 seconds after that start: pressure level 1, 42% free memory, ports 11435 and 58358 closed, and the owned research process group absent. These times exclude earlier idle service setup. Swap usage remained elevated. No background research process or scheduled restart remains.

Global memory readings cannot isolate model loading from concurrent office work. This result does not establish general M4 infeasibility or a model-accuracy result.

## Next step

This session is closed and its blocked preflight cannot be resumed. Preserve both this report and the [earlier M1 failure](../results/2026-09-16-processbench-preflight/README.md). A future low-workload session needs sufficient available memory, a fresh documented budget, and a new target-specific preflight. Keep resource limits, generation settings, and calibration thresholds unchanged.

Only a successful resource and exact-token preflight may precede the fixed 20-case calibration. The 40-case evaluation remains gated on all 20 calibration records, at least 18 usable predictions, and at least 8/10 completion-gated exact judgments in each class. See the [pilot guide](../README.md) for the transport CLI and the [session rules](../PROCESSBENCH_M4_SESSION.md) for service ownership and cleanup.
