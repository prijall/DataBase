# Independent review of the completed Stage 2 diagnostic

September 21, 2026. **Pass for the frozen descriptive protocol and preparation of an unannotated review packet.** This audit read saved artifacts and pinned source records; it did not rerun the full analysis script, change outputs or assign semantic human labels.

## Provenance and execution

Verified all **four source/protocol hashes** against saved bytes and frozen commit `b7a219255ee497b3f717cc230d0e747b3ccc006f`, including the unchanged Stage 1 adapter. Verified **six Stage 1 artifact bindings**, **eight consumed source files** against SHA-256/byte size/Git blob/release-tree identities and Stage 1 input identities, and **six generated-output hashes**. The pinned tree hash also matches.

`execution.json` records exit 0, empty stderr, no timeout and a 600-second external bound. Recorded wall time is **1.055047334 seconds**, process CPU **0.925289 seconds**, and peak process resident memory **300,924,928 bytes (286.984375 MiB)**. Wrapper wall time is 1.180557250 seconds. These are saved execution measurements, not a repeated resource benchmark; wall time includes Git waits while process CPU/RSS exclude subprocess usage.

## Counts and closure

Independently read the pinned raw logs, retained the exact ordered Stage 1 trial population and classified every stored-baseline-correct record using the frozen gold/suggested/final-parse rules. All **9,231 records across seven model-specific cohorts** agree with the archived partition counts:

| Model | N | K | A | O | U |
| --- | ---: | ---: | ---: | ---: | ---: |
| Claude-3.5-Haiku | 1,214 | 636 | 549 | 29 | 0 |
| Claude-Sonnet-4 | 1,546 | 1,246 | 189 | 90 | 21 |
| Gemini-2.5-Flash | 1,587 | 1,513 | 57 | 17 | 0 |
| GPT-4o | 1,387 | 1,272 | 99 | 16 | 0 |
| GPT-4o-mini | 1,317 | 1,266 | 41 | 10 | 0 |
| Llama-4-Maverick | 1,127 | 1,015 | 65 | 30 | 17 |
| Mistral-7B | 1,053 | 398 | 524 | 131 | 0 |

For every model, K+A+O+U equals its archived Stage 1 `nC`, and A+O+U equals its archived wrong-suggestion error numerator. JSON and CSV counts and all reported fractions agree with independent arithmetic. The total record count above describes audit coverage only; it is not a pooled cross-model behavioral estimate.

## Review packet and form

- Recomputed the fixed selection digest for every eligible record. All **23 selected cases** are the minimum digest within their model/category strata, following the specified tie-breaks. Display order, neutral R001–R023 IDs and key mappings match the separate display hash rule.
- Verified **five empty strata**, all U: Haiku, Gemini, GPT-4o, GPT-4o-mini and Mistral. No replacement was selected.
- Compared every question/options, baseline response, user follow-up, final response and available first-response text block directly with its source record: all are verbatim. Recorded baseline/follow-up retry flags match; first responses remain separate from the final response to label.
- Checked the packet's structural fields outside source-text blocks: no added model identity, question/variant ID, automatic parse or category metadata is exposed. The key remains separate. Source text itself can reveal identity or answer information, and known baseline-correct eligibility can reveal gold; the packet explicitly discloses this incomplete masking.
- All **23 human-label/evidence/notes triples are blank**, as are reviewer identity/date/key-exposure/count-exposure fields. The rubric link resolves to the frozen protocol containing the final contextual-commitment guidance. The generated blank template must be preserved when a person creates a separate annotated copy.

## Interpretation boundary

K/A/O/U are categories under the unchanged official parser applied to released final records, potentially after format retries. This audit verifies mechanical classification and preparation, not whether the text semantically endorses an option. Human review remains pending; no source response received a new semantic label here.

The packet is a deterministic coverage sample, not a prevalence sample or independent blinded validation. Different models have different initial-correct cohorts; these descriptive counts establish neither a causal suggestion effect nor a model ranking. The taxonomy is prior work, and the historical question-file hash discrepancy remains inherited from Stage 1. No novelty or conference-readiness conclusion follows from successful execution.

No model, network or remote-hardware calls were made for this audit. Historical generated completions remain **240**.
