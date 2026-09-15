# Freeform v3: development protocol

Frozen before the first v3 model call on September 15, 2026. The commit containing this file and the runner is recorded in each run manifest. This is an adaptive development plan, not a preregistered confirmatory study.

## Question and scope

Can the installed local models produce usable arithmetic answers and trace judgments when allowed ordinary calculations before a final structured verdict? If so, characterize their responses to the fixed neutral/confident wording and conversational/standalone contexts. These are diagnostic descriptions on ten reused development items.

## Methods

- Models: installed `llama3.2:3b` and `qwen3-vl:2b-instruct`, run sequentially through local Ollama. The latter is a vision-language model used with text only. Record actual digests, quantization, server version and template hashes.
- Unchanged examples: ten questions, thirty traces; exact arithmetic checker. Each full run contains ten initial calls, eighty conversational follow-ups, and thirty standalone reviews.
- Elicitation: unconstrained ordinary calculations followed by one `<FINAL_JSON>` block with the three original verdict fields. Strict parser; malformed outputs remain in the logs. No automatic retries or tolerant extraction.
- Settings: temperature 0, seed 42, context 2048, output limit 512 tokens, two CPU threads requested, one model at a time. No cross-device or repeated-call determinism claim.
- Raw messages, model responses, stop reasons, token counts, timings and scores are retained. `done_reason=length` is reported separately as truncation, including its overlap with malformed output.
- Prompt, available calculations, delimiters and token allowance change together relative to prior screens. This assesses a protocol package; it cannot identify the cause of any improvement.

## Advance and stop rules

1. Run the ten initial questions per model. Advance to the remaining 110 calls if at least **8/10 parse** and **5/10 have correct parsed answers**. Otherwise archive that failed screen and inspect it before proposing a separately versioned revision.
2. Completing the baseline does not require a naturally wrong cohort: trace verification remains measurable. Natural correction acceptance is explicitly **not estimable** if that cohort is empty.
3. Before considering any intervention, require at least **90% overall parsing** and **8/10 parsing in each relevant trace cell**. Review valid-trace acceptance and invalid-trace rejection separately. Always rejecting is not verification success.
4. An intervention additionally needs a fixed comparison plan and matched control, reused baseline initial responses, and correction of known dataset confounds. No activation-steering claim or run is authorized by passing this screen alone; it needs a separate local implementation.
5. Preserve failed, partial, and completed runs. Stop between calls at the runner's time limit and respect the user's combined nine-machine-hour weekly budget. These numerical gates are pragmatic development choices, not established standards.

## Analysis

Report all-call successful verdict counts and secondary parsed-only rates, each with denominators. Keep answer accuracy, trace judgments and first-error accuracy separate. Report initially correct, parseable-wrong and malformed cohorts; exact adoption of an unsupported wrong suggestion versus other errors; neutral/confident paired discordances using complete item pairs only. No p-values or claim of independent observations across variants. Ten problems underlie the 120 calls.

## Limitations to carry into the paper

All errors start at step one. Invalid/correct traces contain two false equalities, while invalid/wrong traces contain one. Consequently neither genuine localization nor a pure effect of conclusion correctness is identifiable. Context also changes history and prior calculations; it does not isolate commitment. One confidence phrase, two arithmetic families, small quantized models, no held-out data and no independent human example audit limit generalization. Written reasoning is not evidence of internal faithfulness. Novelty remains unverified.

## Independent AI reviews and decisions

A Codex methods agent proposed the initial capability/format gates and separate acceptance/rejection reporting. Claude Max independently reviewed the sanitized brief; its full response is retained in `reviews/claude-methods-review.txt` as AI-generated advice, not verified evidence.

Accepted from Claude: separate generation and verification, log truncation, inspect task floor/ceiling, add controls and fix confounds before interventions. Deferred: difficulty calibration, repeated-call reproducibility checks and held-out evaluation until this bounded baseline is usable. Rejected for this screen: tolerant/coerced parsing and format re-asks, which would create a new elicitation/scoring procedure.

Two review suggestions need correction: comparing JSON-only with freeform-plus-delimiters still changes multiple factors and is **not** single-factor attribution. A numeric equality chain with the same correct start/end values cannot contain exactly one false equality; balancing errors requires a valid construction, not simply removing the compensating error. Claude's runtime, power and quantization claims were not independently validated and are not adopted as findings.
