# Paper outline and evidence map

[Read the working manuscript](paper/manuscript.md) · [Manuscript update workflow](paper/README.md)

This is a working manuscript structure for an independent research project. The repository currently contains development experiments, not a completed paper. The title, contribution, and abstract must follow the eventual evidence; novelty and conference acceptance are not established.

**Working subject:** verifying numerical reasoning during conversational correction, with a possible later study of anti-sycophancy interventions.

## 1. Introduction

Explain why distinguishing truthful correction from social pressure matters, and why final-answer correctness and supporting-trace validity are separate targets. State the precise question supported by the final experimental design.

**Inputs:** [research direction](RESEARCH_DIRECTION.md) for motivation and the superseding [novelty audit](NOVELTY_AUDIT.md) for scope.

**Still needed:** a verified gap relative to the closest work and a concise contribution statement. Do not claim that reasoning correction, invalid reasoning with correct answers, or verification steering is new merely because this pilot combines them.

## 2. Related work

Organize the comparison around sycophancy and rational updating; self-correction and conversational evaluation; process verification and error localization; and steering or other anti-sycophancy interventions. Compare the exact conditions, outcomes, and interventions, rather than listing papers individually.

**Inputs:** [paper summaries](PAPER_SUMMARIES.md) and [novelty audit](NOVELTY_AUDIT.md), including the primary-source links and remaining reading gaps.

**Still needed:** verify the cited versions and bibliographic metadata, finish incomplete primary-source checks, and update the search before submission. Cite the original research, not these AI-assisted summaries, as evidence for prior findings.

## 3. Methods

### Task and data

Describe the arithmetic grammar, question families, exact checker, trace construction, and separate labels for answer correctness, trace validity, and first false equality. Distinguish development items from any later held-out evaluation.

**Inputs:** [example audit](pilot/EXAMPLES.md), [dataset](pilot/examples.json), and the checker in [pilot.py](pilot/pilot.py).

### Experimental conditions

Specify initial answering, conversational correction, standalone review, evidence conditions, and neutral/confident wording. Explain how an initial model response is preserved verbatim across correction branches and how malformed initial responses form a separate cohort.

**Inputs:** [frozen v3 protocol](pilot/PROTOCOL_V3.md), [runner](pilot/pilot.py), and actual prompts in each run's `responses.jsonl`.

### Inference and scoring

Report model names and digests, quantization, server version, templates, generation settings, output protocol, strict parser, stopping rules, and truncation handling from the run manifests. Present all-call success rates with denominators and parsed-only rates as secondary diagnostics. Ten items, rather than 120 calls, underlie a full development run.

**Inputs:** [pilot guide](pilot/README.md), [tests](pilot/test_pilot.py), [v3 protocol](pilot/PROTOCOL_V3.md), run `manifest.json` files, and raw scores.

**Still needed:** remove or explicitly redesign error-position and error-count confounds, audit examples independently, calibrate difficulty, and freeze a held-out comparison plan. Any intervention requires its own implementation, matched control, and protocol. No intervention results currently exist.

## 4. Results

Use the [research state](RESEARCH_STATE.md) to locate completed artifacts. Populate this section only from archived observations and reproducible analysis.

| Planned result | Required evidence |
| --- | --- |
| Protocol feasibility | Parsing, parsed-answer accuracy, truncation, and observed advance/stop decisions for every attempted protocol |
| Answer versus trace judgment | Separate answer, trace-verdict, and first-error counts by model and condition |
| Conversational conditions | Complete paired observations, neutral/confident discordances, and clear denominators |
| Updating behavior | Initially correct, parseable-wrong, and malformed cohorts; exact adoption of unsupported suggestions versus other wrong answers |
| Any future intervention effect | Frozen matched comparison, held-out data, appropriate uncertainty estimates, and raw intervention/control runs |

The [42-call diagnostic report](pilot/results/2026-09-15-protocol-screen/README.md) records failed direct-v1/worked-v2 screens and sanity checks. The [130-call v3 report](pilot/results/2026-09-15-freeform-v3/README.md) records Llama's completed baseline and Qwen's stopped initial screen. Both failed their applicable gate; their verified results are incorporated in the manuscript. These are development findings about the tested interfaces, not evidence of sycophancy.

If a cohort is empty, write **not estimable**. Do not manufacture model mistakes or report independent-observation uncertainty from correlated variants of the same question. Preserve negative results and any changes made after inspecting development outputs.

## 5. Discussion and limitations

Explain what the final design identifies and what remains ambiguous. The current pilot cannot isolate commitment from conversational history, conclusion correctness from unequal error counts, or genuine localization from a fixed first-error position. A protocol revision that changes multiple factors cannot establish which factor caused an improvement.

Discuss dataset size, reused items, narrow task families, wording coverage, small quantized models, output failures, and the difference between written calculations and faithful internal reasoning. Separate potential safety relevance from measured outcomes.

**Inputs:** limitations in [v3 protocol](pilot/PROTOCOL_V3.md), [pilot guide](pilot/README.md), [novelty audit](NOVELTY_AUDIT.md), and completed run reports.

## 6. Reproducibility and research process

Provide the exact code commit, commands, model/server identities, data and artifact checksums, raw prompts/responses, scoring code, machine-time accounting, and the tested environment. Keep model weights and credentials outside Git. Describe local experimental inference separately from AI assistance used for coding, literature synthesis, and methods review.

**Inputs:** [pilot guide](pilot/README.md), run manifests and `sessions.jsonl`, archived checksum files, [Claude review brief](pilot/reviews/claude-methods-brief.txt), [Claude review](pilot/reviews/claude-methods-review.txt), and the documented adoption/correction decisions in [v3 protocol](pilot/PROTOCOL_V3.md).

Before submission, verify the selected venue's current disclosure and reproducibility requirements. Human authors must validate the claims, references, data, and code.

## Manuscript assembly order

1. Finish and archive the bounded development run, including failures.
2. Resolve the methodological and novelty gaps before expanding the claim.
3. Freeze and execute the final comparison; produce tables directly from archived outputs.
4. Write Methods and Results, then Related Work, Discussion, and Introduction.
5. Write the title and abstract last, matching the actual contribution and its limits.

A successful development run is a foundation for that process, not a completed conference submission.
