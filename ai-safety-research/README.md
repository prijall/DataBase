# AI safety research

**Stage: development pilot.** [Latest state and results](RESEARCH_STATE.md) · [Run the experiments](pilot/README.md) · [Build the paper](PAPER_OUTLINE.md)

## Research question

Can a model distinguish a correct answer from a valid supporting calculation when responding to a user's proposed correction? The broader candidate asks whether anti-sycophancy interventions change this distinction. The current pilot establishes usable local measurements before testing an intervention. **Novelty remains unverified.**

## Work completed

| Work | Evidence |
| --- | --- |
| Literature review and overlap assessment | [Paper summaries](PAPER_SUMMARIES.md), [novelty audit](NOVELTY_AUDIT.md) |
| Ten development questions and thirty checked traces | [Example audit](pilot/EXAMPLES.md), [dataset](pilot/examples.json) |
| Local runner, strict scoring, resumable logs, automated checks | [Runner](pilot/pilot.py), [tests](pilot/test_pilot.py) |
| Forty-two diagnostic calls, including failed output protocols | [Diagnostic report and raw results](pilot/results/2026-09-15-protocol-screen/README.md) |
| Revised freeform protocol, advance/stop rules, independent AI methods review | [Frozen v3 protocol](pilot/PROTOCOL_V3.md), [Claude review](pilot/reviews/claude-methods-review.txt) |

## Current experiment

The [v3 protocol](pilot/PROTOCOL_V3.md) permits ordinary calculations before a delimited final verdict. Each eligible model completes 120 calls over ten underlying questions: initial answers, conversational corrections, and standalone trace reviews. Local inference runs sequentially on shared hardware within the nine-machine-hour weekly allowance.

V3 execution is underway; the [research state](RESEARCH_STATE.md) is the current record of completed runs and outcomes. Passing a development gate does not establish a scientific effect. No activation-steering experiment has been completed.

## Reading and writing map

- **Literature:** [detailed summaries](PAPER_SUMMARIES.md) and [novelty audit](NOVELTY_AUDIT.md). The audit supersedes the earlier [research direction](RESEARCH_DIRECTION.md).
- **Methods and reproduction:** [pilot guide](pilot/README.md), [frozen protocol](pilot/PROTOCOL_V3.md), code and checked examples above.
- **Results:** [current research state](RESEARCH_STATE.md) links the completed archives; failed and partial screens remain part of the record.
- **Manuscript:** [paper outline](PAPER_OUTLINE.md) maps each section to its supporting artifacts and remaining work.

## Next stage and limits

Use the frozen gates to assess v3, then fix dataset confounds and create held-out evaluation before a matched intervention study. Every injected first error is at step one, and invalid traces with correct versus wrong conclusions have different error counts. Ten reused questions, two arithmetic families, and one confidence phrase cannot support broad alignment claims. An empty naturally incorrect initial cohort makes natural correction acceptance unmeasurable.

The examples need an independent human audit. AI assistants helped prepare code, notes, and methods advice; their reviews are not verified evidence. Written calculations are not proof of faithful internal reasoning. The literature's reported experiments have not been independently reproduced here; consult linked primary sources before citing them. Manuscript or repository availability does not establish conference acceptance.
