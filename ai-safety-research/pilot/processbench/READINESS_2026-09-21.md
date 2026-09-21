# M4 readiness and closed session — September 21, 2026

**Latest outcome: second-session calibration stopped after two responses; cleanup verified.** The archive now contains **234 generated completions**. The [second M4 session](../results/2026-09-21-processbench-m4-session2/README.md), frozen at `d2dd756`, passed all sixty exact-token checks (308–778 prompt tokens; maximum 1,802 with the output reserve). It recorded two error-class calibration responses: one normally completed, usable, correct index and one length-stopped, out-of-range prediction. No valid-class example was attempted, so balanced performance is not estimable.

The post-second-call free-memory reading was 19%, triggering the unchanged guard; pressure was normal and recorded subject checks showed no swap growth. Cleanup confirmed pressure level 1, 41% free memory, closed ports 11435/58808/59236, and no owned research processes. Calibration is incomplete: two cases used, eighteen unattempted, all forty evaluation cases untouched. The session is closed. The [2,048-token proposal](../PROCESSBENCH_SMALL_CONTEXT_PLAN.md) is prospective, not implemented or executed. Keep all prior evidence and resource/calibration thresholds.

## First M4 session (historical)

The [first M4 preflight](../results/2026-09-21-processbench-m4/README.md) stopped before tokenization or subject generation. At that point the total was 232 and both cohorts were unused. The sections below preserve that earlier session's checks and stop.

## Completed checks

- Verified authenticated access to the Apple M4 with 16 GiB RAM, Python 3.9.6, Ollama 0.34.0, and matching installed model, template, default-parameter, tokenizer executable and library identities.
- Completed independent offline review of the corrected preflight and memory-only SSH transport. The integrated suite passes 109 tests, including 61 ProcessBench checks.
- Froze the session at commit `017f1d708943876bda16bba67cc32b97c9ebaa14` under the [M4 session rules](../PROCESSBENCH_M4_SESSION.md). The isolated service used target loopback port 11435; resource and process checks ran on the M4.
- Supplied code and request inputs through SSH stdin and process memory. No research scripts, datasets, results, or artifacts were persisted on the M4. Research records were saved on the controller for the GitHub archive.

## Observed stop and cleanup

The first explicitly non-generating debug-render request completed, but its immediate post-load memory check failed. Pressure rose from level 1 to level 2, free memory fell from 36% to 15%, and swap usage and swapouts each grew by approximately 1.565 GiB. All four original resource guards were crossed. The corrected response reader was present but not reached: the guard stopped execution before response validation and exact tokenization. This check therefore does not finish live validation of that reader.

The report spans 6.679 seconds from budget start. Independent cleanup was recorded 42.752 seconds after that start: pressure level 1, 42% free memory, ports 11435 and 58358 closed, and the owned research process group absent. These times exclude earlier idle service setup. Swap usage remained elevated. No background research process or scheduled restart remains.

Global memory readings cannot isolate model loading from concurrent office work. This result does not establish general M4 infeasibility or a model-accuracy result.

## First-session closure

This first session is closed and its blocked preflight cannot be resumed. Preserve both this report and the [earlier M1 failure](../results/2026-09-16-processbench-preflight/README.md). A separately documented second session subsequently passed preflight and began calibration, as summarized above. Its partial results remain separate from this failed first report.

A successful resource and exact-token preflight is required before calibration. The 40-case evaluation remains gated on all 20 calibration records, at least 18 usable predictions, and at least 8/10 completion-gated exact judgments in each class. See the [pilot guide](../README.md) for the transport CLI and the [session rules](../PROCESSBENCH_M4_SESSION.md) for service ownership and cleanup.
