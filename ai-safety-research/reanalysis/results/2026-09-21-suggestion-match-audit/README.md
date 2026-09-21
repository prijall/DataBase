# Suggestion-match diagnostic and human-review packet

September 21, 2026. **Machine analysis complete; human review pending.** This is a descriptive extension of the reproduced SycoBench release. The taxonomy is established prior work; no novel safety effect, causal persuasion estimate or conference-readiness claim is made.

**If you will review the examples, open [the packet](review_packet.md) and [review guide](../../HUMAN_REVIEW_GUIDE.md) before reading the counts below or the separate identity key.** Copy [the blank form](review_form.json) before editing it. Record any prior exposure honestly. Source text and selection context can still reveal information; this is incomplete masking.

## Frozen execution

- Protocol/code frozen at `b7a219255ee497b3f717cc230d0e747b3ccc006f` before the first component aggregation or sample selection.
- Same seven source logs, 555 shared IDs and each model's original baseline-correct cohort. Stage 1 outputs and imported adapter hashes verified; no primary scores changed.
- All seven partitions close exactly: `K+A+O+U=N=Stage1.nC`; `A+O+U` equals the original wrong-suggestion error numerator.
- Sixteen new synthetic tests passed; all 36 Stage 1/2 tests passed together. Independent pre-run checks covered all 60 valid gold/suggestion/parse combinations and 60 inconsistent-score rejections.
- One bounded CPU run, exit 0, no model requests, no M4 use. Our historical generated-completion count remains 240.

## Descriptive counts

`N` is the model-specific baseline-correct cohort. `K` is a final official parse equal to gold; `A` equals the suggested wrong option; `O` is another parsed wrong option; `U` has no parsed option. These are released final responses, potentially after formatting retries.

| Model | N | K | A | O | U | A/N (%) | A/(A+O+U) (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude-3.5-Haiku | 1214 | 636 | 549 | 29 | 0 | 45.22 | 94.98 |
| Claude-Sonnet-4 | 1546 | 1246 | 189 | 90 | 21 | 12.23 | 63.00 |
| Gemini-2.5-Flash | 1587 | 1513 | 57 | 17 | 0 | 3.59 | 77.03 |
| GPT-4o | 1387 | 1272 | 99 | 16 | 0 | 7.14 | 86.09 |
| GPT-4o-mini | 1317 | 1266 | 41 | 10 | 0 | 3.11 | 80.39 |
| Llama-4-Maverick | 1127 | 1015 | 65 | 30 | 17 | 5.77 | 58.04 |
| Mistral-7B | 1053 | 398 | 524 | 131 | 0 | 49.76 | 80.00 |

No model has an empty noncorrect denominator. The full-precision values are in [counts.json](counts.json) and [counts.csv](counts.csv); rows retain alphabetical source-model order and are not a model ranking.

Every model has some noncorrect responses that parse to an option other than the supplied suggestion. Two models also have unparseable responses in this cohort. Consequently, official wrong-suggestion correctness loss and parsed suggestion matching are different observed quantities in this release. This does **not** show that the source's formal WrongFlip metric is wrong: it explicitly measures correctness loss. Neither category proves internal agreement, persuasion, sincerity or a reasoning mechanism. A parsed match itself still requires textual interpretation.

## What the review packet contains

The frozen one-per-model/category rule selected **23 cases**. The remaining **five strata are empty** and were not replaced. The packet preserves question/options, baseline response, follow-up message, final answer and recorded retry/first-response fields. The separate key records provenance and automatic labels; it is excluded from the review form, not kept secret.

All 23 human labels, evidence fields and notes are blank. The reviewer identity/date/exposure fields are also blank. No human annotation or inter-rater agreement is claimed. The sample deliberately covers machine categories, so its eventual disagreement fraction cannot estimate population parser accuracy. Repeated question families and known baseline-correct eligibility further limit independence and masking.

## Resource record

The recorded run used **1.055 seconds wall time**, **0.925 seconds process CPU** and **286.984 MiB peak resident memory**. The external 600-second wrapper finished in 1.181 seconds. CPU/RSS exclude child processes; downloads, implementation and review are excluded. See [runtime](runtime.json) and [execution](execution.json).

## Interpretation and next decision

The [focused literature audit](../../STAGE2_LITERATURE_AUDIT.md) identifies direct overlap with PARROT and broader precedents for measurement sensitivity. The baseline-correct cohorts differ by model, the wrong suggestion is deterministic, and there is no matched neutral follow-up isolating suggestion content. We report no causal effect, significance test, resampling interval, re-ranking or general prevalence claim. The historical question-file hash discrepancy in all seven logs remains unresolved, as documented in Stage 1.

Next, the researcher should complete the qualitative first-pass review under the [frozen rubric](../../STAGE2_PROTOCOL.md#human-review-rubric), saving labels separately from the blank archive. Preserve uncertainties and disagreements. Decide afterward whether there is a substantive, literature-distinct question warranting a larger independently annotated sample and another independent released artifact. Otherwise retain this as a replication note and do not keep expanding a weak contribution.

## Evidence and attribution

[Independent result review](INDEPENDENT_REVIEW.md) · [Protocol](../../STAGE2_PROTOCOL.md) · [Implementation review](../../STAGE2_INDEPENDENT_REVIEW.md) · [Provenance](provenance.json) · [Status](status.json). No upstream inference code was executed and no model was used to supply human labels.

Derived from Debu Sinha's [SycoBench-600 v1.0.0](https://github.com/debu-sinha/sycobench-600/releases/tag/v1.0.0), release commit `5193ce408bd73b401c4c5911f490e2bbad84a082`, [Findings of ACL 2026 paper](https://aclanthology.org/2026.findings-acl.1759/). Data, response excerpts and derived tables retain [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) attribution; upstream code's [MIT notice](../../UPSTREAM_LICENSE.txt) is retained. Changes consist of a descriptive partition, deterministic review selection and unannotated review forms. No source-author endorsement is implied.
