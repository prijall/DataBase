# M4 execution session — September 21, 2026

This prospective addendum implements the user's request to run on the M4 **without saving research files or artifacts there**. It preserves the [selected cases and scientific thresholds](PROCESSBENCH_PLAN.md). No change is made to previous scores, the calibration/evaluation reservation, or the failed September 16 evidence.

## Target and storage

Read-only SSH inspection confirmed the user-provided `prabs` account on Apollo is an Apple M4 with 17,179,869,184 bytes (16 GiB) of RAM. Python 3.9.6, Ollama 0.34.0 and the selected Llama-3.2 3B model already exist. Model manifest, template layer and bundled tokenizer executable/library identities match the earlier pinned configuration. No model or software download is required.

All project code, downloaded benchmark inputs, journals, outputs, reports and server logs remain on the controller machine and are published to the personal GitHub research repository. SSH delivers code and request data through memory using Python's standard library and `-B` (no Python bytecode cache writes). No clone, script file, dataset file, result directory, PID file or experiment artifact is created on the M4 or its external SSD. Existing installed model files are read in place. Normal operating-system and existing inference-runtime activity is not a claim of a forensic zero-write operating system.

## Temporary isolated service

The existing Ollama binary runs as a foreground child of a temporary SSH-controlled process, on **127.0.0.1:11435**, separate from the normal 11434 endpoint. The launcher refuses to start if this port is already occupied. It sets cloud inference off, parallelism to one, a maximum of one loaded model, and disables CLI history. It does not install a launch service or change persistent settings.

The service wrapper owns its process group. STOP, EOF, connection termination or its 5,400-second watchdog triggers termination of only that owned group. Logs stream to the controller. Cleanup must verify that this service and its model process ended; no pre-existing service or unrelated workload is killed.

The different API port is an execution detail, recorded in provenance. Metadata, tokenizer, runner-process and memory checks all execute **on the M4**. There is no forwarding arrangement that mistakes controller memory or processes for target measurements.

## In-memory adapter and provenance

The adapter sends the reviewed source modules to a fresh Python process through SSH stdin and loads them as in-memory modules. Source hashes bind the exact supplied bytes; existing binary/model checks read the real target files. A restricted worker audit hook rejects filesystem mutations and unapproved subprocess commands. Raw subject output returns through SSH; the original controller-side runner retains its durable attempt-before-request journal, scorer and evaluation gate.

Record the controller commit, helper/adapter/worker source hashes, fixed SSH target, actual API port, remote Python/hardware identity, model and backend hashes, token counts and resource observations. A previous machine's or session's report cannot authorize this run. The September 16 failed preflight remains archived and is not reused.

## Budgets and scientific settings

- Same model, prompt, seed 42, temperature zero, 8,192-token context, 1,024-token output ceiling and two requested CPU threads.
- Same 20 calibration cases; advance only after all 20 are recorded, at least 18 normal in-range outputs, and at least 8/10 completion-gated exact matches in each process-label class.
- Same 40 evaluation cases, only after the calibration gate passes; no repeated subject attempt or outcome-based selection.
- Same 60-attempt / 90-minute combined cohort ceiling, including loading, remote checks, pauses and cleanup. The temporary service also has its own 90-minute lifetime cap.
- Model HTTP requests retain the 90-second absolute watchdog. The remote worker has a 95-second outer deadline and SSH transport a 100-second cap, accounting for dispatch/return overhead. Reserve at least **150 seconds** before each subject attempt for transport, resource checks and cleanup. These transport allowances do not raise the model's token or generation-time limits.
- A complete preflight/verification action has an additional 900-second cap and remains subject to the cohort budget. A transport or runtime error stops further attempts and does not trigger an automatic retry.

## Resource policy

Keep the existing limits: normal kernel pressure, at least 20% reported memory free, no more than 256 MiB additional swap usage and no more than 128 MiB additional swapouts compared with this session's pre-load baseline. Existing swap alone is not a failure; growth is measured. Read-only initial inspection found normal pressure with 35% reported memory free and substantial existing swap. This is **not** a successful load test or proof of adequate headroom.

Fresh resource checks before and immediately after loading determine whether the cohort may start. If they fail, preserve the preflight evidence, shut down the owned service, and leave both cohorts unused. Do not relax limits, clear system caches, close office applications, or reduce the fixed context after viewing subject outcomes merely to obtain a passing run.

## Publication

Freeze the reviewed execution code and this addendum before subject generation. Archive either the verified calibration/evaluation outputs or the failed preflight, then update the concise README, research handoff and manuscript. Keep non-generating operations separate from subject completions. The M4 remains an execution target, not a storage location for this project.
