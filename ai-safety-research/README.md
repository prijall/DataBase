# AI safety research

**Stage: development pilot and working manuscript.** [Read the paper](paper/manuscript.md) · [Latest runtime check](pilot/results/2026-09-21-processbench-m4/README.md) · [Research state](RESEARCH_STATE.md)

## Research question

Can a model distinguish a correct answer from a valid supporting calculation when responding to a user's proposed correction? The broader candidate asks whether anti-sycophancy interventions change this distinction. The current pilots test whether the proposed measurements are usable before an intervention study. **Novelty remains unverified.**

## Work completed

| Work | Evidence |
| --- | --- |
| Literature review and overlap assessment | [Paper summaries](PAPER_SUMMARIES.md), [novelty audit](NOVELTY_AUDIT.md) |
| Ten development questions and thirty checked traces | [Example audit](pilot/EXAMPLES.md), [dataset](pilot/examples.json) |
| Local runner, strict scoring, resumable logs, automated checks | [Runner](pilot/pilot.py), [tests](pilot/test_pilot.py) |
| Forty-two diagnostic calls, including failed output protocols | [Diagnostic report and raw results](pilot/results/2026-09-15-protocol-screen/README.md) |
| Revised freeform protocol, advance/stop rules, independent AI methods review | [Frozen v3 protocol](pilot/PROTOCOL_V3.md), [Claude review](pilot/reviews/claude-methods-review.txt) |
| 130 additional local calls, strict scoring and separate extraction audit | [V3 results and raw artifacts](pilot/results/2026-09-15-freeform-v3/README.md) |
| Sixty verification-only calls under a separately frozen protocol | [September 16 results](pilot/results/2026-09-16-verification-only/README.md), [protocol](pilot/VERIFICATION_ONLY_PROTOCOL.md) |
| Published-interface audit and offline ProcessBench preparation | [Source audit](pilot/PUBLISHED_INTERFACE_AUDIT.md), [bounded plan](pilot/PROCESSBENCH_PLAN.md), [selection manifest](pilot/processbench/selection.json) |
| Local ProcessBench runner and live preflight stop before calibration | [Execution rules](pilot/PROCESSBENCH_EXECUTION.md), [preflight evidence](pilot/results/2026-09-16-processbench-preflight/README.md) |
| M4 memory-only SSH transport and resource stop before calibration | [M4 archive](pilot/results/2026-09-21-processbench-m4/README.md), [session rules](pilot/PROCESSBENCH_M4_SESSION.md) |
| Working manuscript, verified result tables and four checked references | [Manuscript](paper/manuscript.md), [related work](paper/related_work.md), [bibliography](paper/references.bib) |

## Latest work

The September 21 [M4 preflight](pilot/results/2026-09-21-processbench-m4/README.md) stopped on the first non-generating model load: memory pressure and swap growth exceeded the fixed limits. No prompt tokenization or subject answers completed. Cleanup confirmed normal pressure, closed research service ports, and no owned research processes. **The total remains 232 calls; both reserved cohorts are unused.** Research code and inputs passed through memory over SSH; records were saved on the controller for GitHub, with no research files persisted on the M4.

## Latest completed experiment

The [verification-only screen](pilot/VERIFICATION_ONLY_PROTOCOL.md) asked each model for a binary judgment on thirty existing traces. Both runs are complete. Llama returned usable `VALID` labels for all thirty, missing every invalid trace. Qwen generated extra text and hit the sixteen-token limit on all thirty calls, leaving no usable classifications. Both failed the frozen gate.

The repository records **232 calls total** across development protocols. The verification-only model calls took 52.1 seconds of recorded client execution; inference remained local and sequential. Qwen's zero usable-label score does not establish zero reasoning ability. No intervention has run.

## Reading and writing map

- **Literature:** [detailed summaries](PAPER_SUMMARIES.md) and [novelty audit](NOVELTY_AUDIT.md). The audit supersedes the earlier [research direction](RESEARCH_DIRECTION.md).
- **Methods and reproduction:** [pilot guide](pilot/README.md), [frozen protocol](pilot/PROTOCOL_V3.md), code and checked examples above.
- **Results:** [current research state](RESEARCH_STATE.md) links the completed archives; failed and partial screens remain part of the record.
- **Manuscript:** [working paper](paper/manuscript.md), [update workflow](paper/README.md), and [evidence outline](PAPER_OUTLINE.md). Update the draft alongside each verified research increment.

## Next stage and limits

The [September 21 readiness record](pilot/processbench/READINESS_2026-09-21.md) now includes verified M4 access and a completed, blocked runtime check. The integrated offline suite passes 109 tests, including 61 ProcessBench checks. That session is closed and cannot resume from its failed report. Next: establish a low-workload session with enough available memory and perform a fresh documented preflight, keeping the resource and calibration gates unchanged. Global memory readings do not identify the cause or show that the M4 is generally unsuitable.

The [ProcessBench plan](pilot/PROCESSBENCH_PLAN.md) reserves 20 calibration and 40 evaluation cases. No ProcessBench answers have been generated. In the earlier synthetic development traces, every injected first error is at step one, and invalid traces with correct versus wrong conclusions have different error counts. Ten reused questions, two arithmetic families, and one confidence phrase cannot support broad alignment claims. Reliable measurements, corrected confounds and held-out data are needed before the intended intervention study.

The examples need an independent human audit. AI assistants helped prepare code, notes, and methods advice; their reviews are not verified evidence. Written calculations are not proof of faithful internal reasoning. The literature's reported experiments have not been independently reproduced here; consult linked primary sources before citing them. Manuscript or repository availability does not establish conference acceptance.
