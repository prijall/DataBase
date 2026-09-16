# AI safety research

**Stage: development pilot and working manuscript.** [Read the paper](paper/manuscript.md) · [Latest results](pilot/results/2026-09-16-verification-only/README.md) · [Research state](RESEARCH_STATE.md)

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
| Working manuscript, verified result tables and four checked references | [Manuscript](paper/manuscript.md), [related work](paper/related_work.md), [bibliography](paper/references.bib) |

## Latest experiment

The [verification-only screen](pilot/VERIFICATION_ONLY_PROTOCOL.md) asked each model for a binary judgment on thirty existing traces. Both runs are complete. Llama returned usable `VALID` labels for all thirty, missing every invalid trace. Qwen generated extra text and hit the sixteen-token limit on all thirty calls, leaving no usable classifications. Both failed the frozen gate.

The repository records **232 calls total** across development protocols. Today's model calls took 52.1 seconds of recorded client execution; inference remained local and sequential. Qwen's zero usable-label score does not establish zero reasoning ability. No intervention has run.

## Reading and writing map

- **Literature:** [detailed summaries](PAPER_SUMMARIES.md) and [novelty audit](NOVELTY_AUDIT.md). The audit supersedes the earlier [research direction](RESEARCH_DIRECTION.md).
- **Methods and reproduction:** [pilot guide](pilot/README.md), [frozen protocol](pilot/PROTOCOL_V3.md), code and checked examples above.
- **Results:** [current research state](RESEARCH_STATE.md) links the completed archives; failed and partial screens remain part of the record.
- **Manuscript:** [working paper](paper/manuscript.md), [update workflow](paper/README.md), and [evidence outline](PAPER_OUTLINE.md). Update the draft alongside each verified research increment.

## Next stage and limits

Next: prepare an offline measurement-validation plan using a published verification interface and scorer, with separate calibration material and fixed settings before further inference. Every injected first error is at step one, and invalid traces with correct versus wrong conclusions have different error counts. Ten reused questions, two arithmetic families, and one confidence phrase cannot support broad alignment claims. Reliable measurements, corrected confounds and held-out data are needed before the intended intervention study.

The examples need an independent human audit. AI assistants helped prepare code, notes, and methods advice; their reviews are not verified evidence. Written calculations are not proof of faithful internal reasoning. The literature's reported experiments have not been independently reproduced here; consult linked primary sources before citing them. Manuscript or repository availability does not establish conference acceptance.
