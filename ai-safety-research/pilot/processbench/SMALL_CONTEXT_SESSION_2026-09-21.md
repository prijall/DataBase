# Smaller-context M4 session — September 21, 2026

Prospective session record, written before starting the service or loading a model. The user requested the next execution step after reviewing the implemented and independently checked profile.

- Configuration: `small-context-v1`, implemented at commit `ed40b8a1d9bd0165fc91be0335e0a10b9b091d09`; 2,048 context and unchanged 1,024 output tokens. The [protocol](../PROCESSBENCH_SMALL_CONTEXT_PLAN.md), [implementation review](SMALL_CONTEXT_IMPLEMENTATION_REVIEW.md), and new selection remain unchanged.
- Selection SHA-256: `55e84656d599431ebab9658b6fb40ba2aee283c4c994577f72eceb281832b456`. Twenty fresh balanced calibration cases precede the original forty evaluation cases; evaluation remains gated on complete passing calibration.
- Readiness at Unix time 1789966693.632708: verified Apple M4, 16 GiB RAM, Python 3.9.6; normal pressure, 46% reported free memory, neither 11434 nor 11435 listening. This does not prove fit after loading or generation.
- New controller directory: `runs/processbench-m4-small-context-2026-09-21`. A fresh report and preload baseline are required; do not reuse either older M4 report.
- One bounded session: at most sixty subject attempts and ninety minutes including checks, pauses and cleanup; retain the 150-second request reserve and all original resource limits. Earlier recorded September 21 service windows total less than fifteen minutes, so this ninety-minute cap fits within the known nine-machine-hour weekly allocation. This is accounting for recorded research work, not an assertion about unrelated or unreported use.
- No model downloads, software installation, office-app termination or M4 research file writes. Code and data travel in memory; records remain on the controller for GitHub.
- Any runtime/resource failure ends this session. No automatic retries, changing the context, swapping cases or increasing the output limit. Preserve partial records and verify cleanup of the owned service/process group.

Readiness artifact SHA-256: `94610d4b13edfd6c7703143cfdd442b285893835cd25ab2d267d91d3b3ee4d9e`.
