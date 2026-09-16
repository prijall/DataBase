# Local ProcessBench execution addendum

September 16, 2026. This addendum operationalizes the [prospective plan](PROCESSBENCH_PLAN.md). Selection, model, prompt, generation allowance, scoring and calibration thresholds remain unchanged. Freeze this document and the reviewed code in Git before subject inference. Record that commit in the run manifest.

## Subject calls versus preflight operations

Subject inference uses the installed `llama3.2:3b` through local Ollama, sequentially, with the fixed 8,192-token context and 1,024-token generation ceiling. Calibration contains the 20 already reserved IDs. Evaluation contains the 40 separately reserved IDs and is gated on successful calibration. Never regenerate a failed or interrupted subject request automatically.

Preflight may read model metadata, load the existing model, render chat templates and tokenize text. These operations do not generate subject answers; archive their operations and timing separately from subject completions. The 90-minute combined execution budget starts before the final preflight and includes model loading, calibration, evaluation, pauses and cleanup. It excludes earlier software development and offline unit tests.

For this installed Ollama version, the verified render-only field is **`_debug_render_only`**, with a leading underscore. An unrecognized spelling could be ignored and generate an answer. Pin server version and confirm the render-only response shape; fail closed if unsupported. Source authority: [Ollama request types](https://github.com/ollama/ollama/blob/d8ab4b4f0ca24b51d3a46b3bf4f462e58ce66b1f/api/types.go) and [chat handler](https://github.com/ollama/ollama/blob/d8ab4b4f0ca24b51d3a46b3bf4f462e58ce66b1f/server/routes.go). Use the bundled model tokenizer to count the actual rendered prompt including special-token handling. Preserve token counts and hashes, without publishing upstream prompt text or token sequences that reconstruct it.

The installed model template includes its default knowledge-cutoff header. This is disclosed model-template behavior, not an added verification instruction. Require the exact reviewed template hash, no configured task-specific system text, no tools, and one user message containing the official benchmark template. Compare actual prompt evaluation counts against the preflight counts and stop on an unexplained mismatch; do not accept silent context truncation.

## Shared-machine resource gate

The read-only guard uses macOS `sysctl`, `memory_pressure -Q` and `vm_stat`. A missing or unparseable reading blocks execution. Check before model loading, after loading, and around every subject request. Compare cumulative changes against the initial preflight baseline so model-loading pressure is included.

Stop immediately if any of the following is observed:

- Kernel memory-pressure level differs from normal (`1`).
- Reported system-wide memory free percentage falls below 20%.
- Swap usage increases by more than 256 MiB from the baseline.
- Cumulative swapouts increase by more than 128 MiB from the baseline.
- Another model workload is present, model/context identity differs, or available telemetry cannot establish the required state.

These conservative engineering thresholds protect the shared computer; they are not scientific outcome gates. Existing swap at baseline is recorded rather than treated as evidence that this research caused it. No workload is evicted. No service is restarted and no Tailscale device is used automatically.

## Deadlines, interruption and evidence

Each subject request has a 90-second absolute deadline. Reserve at least 130 seconds before starting another request: 90 seconds for the request, up to 30 seconds for resource probes, and 10 seconds for cleanup overhead. The entire cohort allows at most 60 attempted subject requests within 90 minutes; overhead may reduce the number possible. Persist the original budget start across resumes.

Write and flush an attempt record before sending each request. An attempted ID with no finished record is ambiguous and blocks automatic continuation. Record raw model output, final status, errors, timing, request options, example ID and message hash. Derive scores again from raw outputs during summary/evaluation admission rather than trusting saved Boolean scores. Resource or communication errors stop the session, even if the remaining scientific gate could still pass.

Closing a timed-out client connection is not proof that server computation stopped. Record unresolved cancellation, stop further subject requests, and verify the server state before declaring cleanup complete. Do not kill a shared Ollama service to force cancellation. Preserve partial output when available and all failed attempts; do not substitute a fresh answer under the same ID.

## Reporting

Keep official-compatible extraction and completion-gated local scores separate. For each process-label class report planned, attempted and completed counts, usable predictions, exact-index matches, malformed outputs and length stops. If calibration fails, retain all calibration evidence and leave evaluation unrun. The 18/20 usability condition and 8/10 exact-match condition in each class assess different things.

Archive the preflight report, attempt journal, raw outputs, summaries and code/source identities. Update the paper from verified results only. A stop during preflight adds zero subject calls and is a resource finding, not a model-accuracy finding.
