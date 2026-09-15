# Output Usability and Trace Rejection in a Local Arithmetic Verification Pilot

**Working manuscript — development results, September 15, 2026.** This draft describes completed pilot observations and will be updated from archived results. It is not a completed intervention study. Novelty remains unverified; the title and scope are provisional. Both bounded v3 evaluations are complete; no intervention was run.

## Abstract

Evaluating whether language models respond appropriately to corrections requires separating answer correctness, evidence validity, and output usability. We present a small development pilot designed to test these measurements before studying anti-sycophancy interventions. Ten arithmetic questions generate valid traces, invalid traces with correct conclusions, and invalid traces with incorrect conclusions. An exact checker labels each numerical equality. A completed local Llama 3.2 3B run contains 120 initial, conversational, and standalone responses under a freeform-calculation protocol. All ten initial answers are correct, but only 60 of 120 responses satisfy the complete output contract. Among 41 parseable trace judgments, every trace is rejected, including eight valid traces. A separately labeled, post-hoc presentation audit recovers one additional verdict and leaves 59 outputs unusable under its conservative rule. Llama fails the full parsing gate; Qwen3-VL stops at its initial gate with two valid, correct answers out of ten. These observations identify an unsuitable measurement interface and asymmetric accepted outputs on this development set; they do not establish a sycophancy mechanism or intervention effect. Fixed error positions, unequal error counts, narrow task coverage, and absent held-out evaluation constrain the interpretation.

## 1. Introduction

A useful assistant should reconsider a mistaken answer when presented with good evidence while resisting an unsupported suggestion that makes its answer worse. Measuring these behaviors requires distinguishing the correctness of a proposed conclusion from the validity of the reasoning offered for it. An argument can reach the right numerical answer through false intermediate equalities. Conversely, a model that rejects every argument may appear successful on invalid examples while failing to recognize valid evidence.

Our broader candidate question concerns whether anti-sycophancy interventions change sensitivity to verified errors in conversational versus standalone review. Here we test a prerequisite: can small local models produce interpretable answers and trace judgments through the proposed interface? No intervention is evaluated.

## 2. Related work

The [related-work review](related_work.md) and [reference file](references.bib) provide the evolving source-level comparison. The repository's [novelty audit](../NOVELTY_AUDIT.md) identifies substantial overlap with work on rational updating, persuasive rebuttals, process-error detection, and verifier steering. In particular, the proposed project cannot claim evidence-sensitive correction, flawed reasoning with correct final answers, or a strictness-versus-acceptance trade-off as new simply by testing smaller models.

Our immediate distinction is methodological: we use restricted, mechanically checked numerical equalities to inspect the proposed measurement interface before evaluating an intervention. That restriction makes labels auditable but sharply limits task coverage. Whether a later controlled interaction study would contribute beyond existing research remains an open literature question.

## 3. Methods

### 3.1 Development data

The [dataset](../pilot/examples.json) contains ten questions from two arithmetic families: a parenthesized sum followed by multiplication and subtraction, and a sum of two products. Each question has three traces with three numbered equalities: valid reasoning with a correct conclusion, invalid reasoning with the same correct conclusion, and invalid reasoning with an incorrect conclusion. A Python checker evaluates a restricted arithmetic grammar using exact rational arithmetic; it does not execute arbitrary expressions or judge unrestricted natural-language proofs. The [example audit](../pilot/EXAMPLES.md) exposes every equality and label.

All injected first errors occur at step one. Invalid traces returning to the correct conclusion contain two false equalities, whereas invalid traces ending incorrectly contain one. The current construction therefore does not isolate conclusion correctness from error count. Examples were created with AI assistance and checked mechanically; no independent human annotation is claimed.

### 3.2 Conditions and local execution

Each full run begins with ten initial answers. For each question, four follow-up conditions—an unsupported wrong answer and the three trace types—are crossed with neutral or confident wording, producing 80 conversational responses. The model's original initial response is preserved verbatim in every corresponding conversation. Thirty additional calls review the traces without that initial conversation. Follow-ups are deterministically shuffled. The 120 calls share ten underlying questions and are not independent observations.

The completed freeform-v3 run uses the installed `llama3.2:3b` model, reported as 3.2B parameters with Q4_K_M quantization, through local Ollama 0.34.0. Settings are temperature zero, seed 42, a 2,048-token context, a 512-token generation limit, and two requested CPU threads. The model writes ordinary calculations followed by a single delimited JSON verdict. Ollama's JSON-format constraint is omitted. Exact model and template identities are recorded in the [manifest](../pilot/results/2026-09-15-freeform-v3/llama32/manifest.json). The second model, `qwen3-vl:2b-instruct`, is a quantized vision-language model used with text only under the same requested settings. Experimental inference runs sequentially on shared local hardware.

### 3.3 Scoring and development decisions

The strict verdict contains an integer answer, a Boolean trace-validity judgment when applicable, and the first false-equality index. Zero indicates a fully valid trace; null trace fields apply only when no trace is supplied. Malformed or inconsistent verdicts fail the complete-response score, even when the response contains a correct number. Answer accuracy, trace validity, and first-error accuracy are reported separately, with all-call and parsed-only denominators.

The [v3 protocol](../pilot/PROTOCOL_V3.md) was frozen before its first model call. Advancing beyond initial questions requires at least eight parseable and five correct answers out of ten. The later parsing gate requires a complete run, at least 90% parsing overall, and at least eight parseable outputs in each ten-item trace cell. These are pragmatic development thresholds, not validated standards. The wider development sequence is adaptive rather than preregistered.

A secondary presentation audit was specified after inspecting the first six Llama format failures. It accepts only a unique terminal three-field JSON object or three complete scalar lines satisfying the original semantic checks. It does not infer judgments from prose, repair nulls, or select between competing verdicts. Original strict scores and gate decisions remain unchanged.

## 4. Results

### 4.1 Earlier elicitation screens

The [42-call diagnostic archive](../pilot/results/2026-09-15-protocol-screen/README.md) contains three 12-call screens and six control calls. Direct JSON elicitation produced zero correct initial answers out of ten for both Llama and Qwen. A subsequent Llama protocol requesting a JSON `working` field also produced zero out of ten. Both models nevertheless solved one arithmetic control correctly when asked for ordinary worked calculations. These comparisons changed multiple prompting and output factors; they do not identify JSON formatting as the cause of failure or establish general arithmetic incapacity.

### 4.2 Completed Llama freeform run

Llama passed the v3 initial gate with ten parseable, correct answers. The complete run subsequently failed the full parsing gate. Table 1 summarizes the [persisted-score audit](../pilot/results/2026-09-15-freeform-v3/llama32/AUDIT.md); raw responses remain archived separately.

| Measure | Successful / all applicable calls | Successful / parseable applicable calls |
| --- | ---: | ---: |
| Complete output contract | 60/120 | — |
| Answer correctness | 57/120 | 57/60 |
| Trace-validity correctness | 33/90 | 33/41 |
| First-error correctness | 23/90 | 23/41 |
| Acceptance of valid traces | 0/30 | 0/8 |
| Rejection of invalid traces | 33/60 | 33/33 |

**Table 1.** Descriptive development counts. Parsed-only columns condition on successful output production and can select an easier or systematically different subset.

Every one of the 41 parseable trace judgments rejects the supplied trace. Thus, the high parsed-only rejection rate on invalid examples coexists with zero valid-trace acceptance. This observation concerns the parseable outputs under this protocol; malformed responses do not establish either acceptance or rejection. One output reports a length stop and is malformed. The other 59 malformed outputs do not report length stops, so recorded truncation alone cannot explain the format failures.

All initial answers are correct, leaving no naturally incorrect initial cohort for measuring acceptance of a valid correction. In the unsupported-suggestion condition, nine of twenty follow-ups parse and all nine retain the correct answer; eleven are malformed. No exact adoption of the wrong suggestion is observed among those nine, which does not establish general resistance to pressure. Framing comparisons also change parsing rates and are not interpreted as a causal sycophancy effect.

### 4.3 Qwen initial screen

The [Qwen audit](../pilot/results/2026-09-15-freeform-v3/qwen3vl/AUDIT.md) records two parseable, correct initial answers and eight malformed responses. Three malformed responses report length stops. The initial gate fails, so the remaining 110 calls are not executed; there are no Qwen trace judgments or conversational follow-ups to compare. Together, v3 contributes 130 calls, bringing the archived total including prior diagnostics to 172.

### 4.4 Presentation-only diagnostic

The [post-hoc audit](../pilot/results/2026-09-15-freeform-v3/llama32/PRESENTATION_AUDIT.md) recovers one additional verdict, leaving 59 outputs unusable under its fixed conservative rule. The recovered verdict has a correct answer and trace-validity judgment but an incorrect first-error index. Consequently, presentation-only extraction addresses only a small fraction of this run's failures. It neither changes the original 60/120 parsing result nor retroactively passes the gate. The same [presentation audit for Qwen](../pilot/results/2026-09-15-freeform-v3/qwen3vl/PRESENTATION_AUDIT.md) recovers no additional verdicts. Both bounded evaluations therefore end without advancing to intervention experiments.

## 5. Discussion and limitations

The completed run separates successful initial arithmetic from failure of the broader generation-and-verification interface. High answer accuracy conditional on parsing is insufficient when half of all responses fail the required contract. Similarly, rejecting invalid traces is insufficient when every parseable valid-trace judgment also rejects. These diagnostics justify withholding intervention experiments until the measurement task supports both valid acceptance and invalid rejection.

The evidence remains narrow. Ten reused questions cannot establish general alignment behavior. Fixed first-error positions prevent a genuine localization test; unequal error counts confound conclusion comparisons. Conversational and standalone conditions differ in history and prior calculations, so their contrast does not isolate commitment. One confidence phrase provides limited rhetorical coverage. Quantization, one completed full run, and a second model stopped at screening do not support broad model comparisons. Held-out and repeated-call evaluations remain absent.

The earlier protocol revisions changed prompts, output constraints, and available computation together. Their outcomes establish only package-level feasibility differences. The post-hoc extraction analysis is explicitly selected after failures and cannot serve as confirmatory evidence. Written calculations are observable text, not proof of faithful internal reasoning. The next methodological question is whether a separately planned verification-only interface yields usable, balanced judgments before expanding the dataset or introducing steering.

## 6. Reproducibility and AI assistance

The [pilot guide](../pilot/README.md) supplies commands and environment requirements. The archived Llama manifest records execution commit `fc043ce97ea515d880557dd60b62067f00720000`, script and dataset hashes, model digest, template hash, and generation settings. [Raw conversations](../pilot/results/2026-09-15-freeform-v3/llama32/responses.jsonl) and [session logs](../pilot/results/2026-09-15-freeform-v3/llama32/sessions.jsonl) preserve outputs and client timing. Reproduction should use the recorded version rather than silently resume with edited code.

AI assistants contributed literature synthesis, implementation, methods review, and drafting. The [Claude review](../pilot/reviews/claude-methods-review.txt) and protocol record advice and adoption decisions, not validated evidence. Hosted research assistance is separate from local inference. Human authors must verify claims, references, examples, code, and the eventual venue's disclosure requirements.
