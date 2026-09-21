# Output Usability and Verification Failures in Local Arithmetic Pilots

**Working manuscript — development results, September 21, 2026.** This draft describes completed pilot observations and will be updated from archived results. It is not a completed intervention study. Novelty remains unverified; the title and scope are provisional. The freeform-v3 and verification-only evaluations are complete, with 232 archived calls across all development stages; no intervention was run.

## Abstract

Evaluating responses to corrections requires separating answer correctness, evidence validity, and output usability. We report an adaptive local development study using ten arithmetic questions and thirty mechanically checked traces. Across 232 calls, two small quantized models were screened before any anti-sycophancy intervention. In a 120-call freeform Llama 3.2 3B run, all ten initial answers were correct, but only 60 responses satisfied the complete output contract. All 41 parseable trace judgments rejected their traces, including eight valid traces. Qwen3-VL produced two valid, correct initial responses out of ten and failed the advance gate. A subsequent verification-only screen requested binary labels for all thirty traces per model. Llama returned usable VALID labels for every trace, yielding 50% primary balanced accuracy; Qwen's thirty responses all reached the sixteen-token limit without usable labels. Both models failed the verification-only gate. These are interface-level feasibility results, not evidence of general arithmetic incapacity, a sycophancy mechanism, or an intervention effect. Fixed error positions, unequal error counts, reused development examples, and jointly changed protocols constrain interpretation.

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

Each full freeform-v3 run begins with ten initial answers. For each question, four follow-up conditions—an unsupported wrong answer and the three trace types—are crossed with neutral or confident wording, producing 80 conversational responses. The model's original initial response is preserved verbatim in every corresponding conversation. Thirty additional calls review the traces without that initial conversation. Follow-ups are deterministically shuffled. The 120 calls share ten underlying questions and are not independent observations.

The completed freeform-v3 run uses the installed `llama3.2:3b` model, reported as 3.2B parameters with Q4_K_M quantization, through local Ollama 0.34.0. Settings are temperature zero, seed 42, a 2,048-token context, a 512-token generation limit, and two requested CPU threads. The model writes ordinary calculations followed by a single delimited JSON verdict. Ollama's JSON-format constraint is omitted. Exact model and template identities are recorded in the [manifest](../pilot/results/2026-09-15-freeform-v3/llama32/manifest.json). The second model, `qwen3-vl:2b-instruct`, is a quantized vision-language model used with text only under the same requested settings. Experimental inference runs sequentially on shared local hardware.

### 3.3 Scoring and development decisions

The freeform-v3 strict verdict contains an integer answer, a Boolean trace-validity judgment when applicable, and the first false-equality index. Zero indicates a fully valid trace; null trace fields apply only when no trace is supplied. Malformed or inconsistent verdicts fail the complete-response score, even when the response contains a correct number. Answer accuracy, trace validity, and first-error accuracy are reported separately, with all-call and parsed-only denominators.

The [v3 protocol](../pilot/PROTOCOL_V3.md) was frozen before its first model call. Advancing beyond initial questions requires at least eight parseable and five correct answers out of ten. The later parsing gate requires a complete run, at least 90% parsing overall, and at least eight parseable outputs in each ten-item trace cell. These are pragmatic development thresholds, not validated standards. The wider development sequence is adaptive rather than preregistered.

A secondary presentation audit was specified after inspecting the first six Llama format failures. It accepts only a unique terminal three-field JSON object or three complete scalar lines satisfying the original semantic checks. It does not infer judgments from prose, repair nulls, or select between competing verdicts. Original strict scores and gate decisions remain unchanged.

### 3.4 Verification-only feasibility screen

Following the v3 failures, a separately specified [verification-only protocol](../pilot/VERIFICATION_ONLY_PROTOCOL.md) removed answer generation, first-error localization, and conversation history. Each model received the thirty unchanged numerical traces in a fixed shuffled order and was asked for a single validity label. The frozen parser accepted ASCII case-insensitive `VALID` or `INVALID`, optionally followed by one period, with surrounding whitespace removed. A usable label additionally required a normal, successful server stop; truncated or unknown-status outputs could not count as correct. The output allowance was sixteen tokens, with other requested sampling settings retained.

The primary comparison was balanced between ten valid/correct and ten invalid/wrong traces; ten invalid/correct traces were secondary. The feasibility gate required all thirty recorded responses, at least 27 usable labels overall and nine in every condition, and at least eight successful judgments in each primary class. A primary pass could coexist with failure on invalid traces ending correctly and would not establish verification independent of conclusions. Both models completed the fixed thirty calls without outcome-based revisions or retries. This protocol changed multiple task and output factors together, so its comparison with v3 does not identify an isolated cause.

### 3.5 Published-interface adaptation (subject evaluation not yet executed)

After the failed screens, we inspected the pinned official ProcessBench critic template and greedy scorer (Zheng et al., 2025). The reference interface permits prose critique and extracts the last boxed integer, using zero-based paragraph indices and −1 for an error-free solution. This differs from our earlier labels and whole-response parsing contracts. Its aggregate is the harmonic mean of exact-index accuracies for erroneous and error-free solutions, rather than precision/recall F1. The [source audit](../pilot/PUBLISHED_INTERFACE_AUDIT.md) records the immutable sources and behavioral details.

Our [prospective local plan](../pilot/PROCESSBENCH_PLAN.md) reserves 20 calibration and 40 evaluation solutions from the pinned GSM8K domain, balanced by process label and disjoint by whitespace-normalized problem text, with one solution per selected group. The original 400-case domain contains 193 error-free and 207 erroneous solutions. This reservation is held out from our own development, not from unknown model pretraining. The offline adapter prepares IDs and prompt-size metadata and checks scoring semantics without generating responses. The local runner and exact-token preflight helper are implemented; their first live preflight stopped before subject inference, as reported separately below.

The planned installed Llama-3.2 3B run uses 1,024 generated tokens and an 8,192-token total context, subject to resource and token preflights; the published ordinary greedy allowance is 8,192 generated tokens. Model, quantization, backend, sample and generation changes make this a feasibility adaptation, not replication of a published score. Calibration must yield at least 18/20 normally completed in-range predictions and at least 8/10 completion-gated exact matches per class before evaluation. Official-compatible and completion-gated scores will remain distinct. No ProcessBench subject inference has run, and this plan contributes no results to the tables below. The [execution addendum](../pilot/PROCESSBENCH_EXECUTION.md) specifies exact template/token preflight, relative swap and memory-pressure stops, durable attempt logging and a 90-second absolute request deadline within the 90-minute cohort budget.

The [M4 session addendum](../pilot/PROCESSBENCH_M4_SESSION.md) specifies a second execution target after the shared-M1 resource stop. Read-only inspection verified an Apple M4 with 16 GiB RAM and matching installed model/tokenizer identities. Scripts and request data are supplied through memory over SSH, with all research records stored on the controller. Resource measurements execute on the M4. The selected cases, prompts, model generation settings and calibration thresholds are unchanged; transport deadlines and isolated service startup are documented before subject inference. The September 21 preflight subsequently stopped at the unchanged resource guards before tokenization or subject inference; Section 4.7 reports that outcome.

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

The [Qwen audit](../pilot/results/2026-09-15-freeform-v3/qwen3vl/AUDIT.md) records two parseable, correct initial answers and eight malformed responses. Three malformed responses report length stops. The initial gate fails, so the remaining 110 calls are not executed; there are no Qwen trace judgments or conversational follow-ups to compare. Together, v3 contributed 130 calls, bringing the archived total at that stage to 172 including prior diagnostics.

### 4.4 Presentation-only diagnostic

The [post-hoc audit](../pilot/results/2026-09-15-freeform-v3/llama32/PRESENTATION_AUDIT.md) recovers one additional verdict, leaving 59 outputs unusable under its fixed conservative rule. The recovered verdict has a correct answer and trace-validity judgment but an incorrect first-error index. Consequently, presentation-only extraction addresses only a small fraction of this run's failures. It neither changes the original 60/120 parsing result nor retroactively passes the gate. The same [presentation audit for Qwen](../pilot/results/2026-09-15-freeform-v3/qwen3vl/PRESENTATION_AUDIT.md) recovers no additional verdicts. Both v3 evaluations therefore ended without advancing to intervention experiments.

### 4.5 Completed verification-only screen

The [verification-only archive](../pilot/results/2026-09-16-verification-only/README.md) adds sixty calls, bringing the recorded total to 232. Both models produced responses for every planned job, but neither passed the frozen feasibility gate. Table 2 separates recorded coverage, usable outputs, and successful judgments.

| Measure | Llama 3.2 3B | Qwen3-VL 2B Instruct |
| --- | ---: | ---: |
| Recorded responses | 30/30 | 30/30 |
| Usable labels | 30/30 | 0/30 |
| Length-stopped outputs | 0/30 | 30/30 |
| Valid-trace acceptance, all calls | 10/10 | 0/10 |
| Invalid/wrong rejection, all calls | 0/10 | 0/10 |
| Invalid/correct rejection, all calls | 0/10 | 0/10 |
| Primary balanced all-call score | 50.0% | 0.0% |
| Valid acceptance / usable valid outputs | 10/10 | Not estimable |
| Invalid/wrong rejection / usable outputs | 0/10 | Not estimable |
| Invalid/correct rejection / usable outputs | 0/10 | Not estimable |
| Problems with both primary traces successful | 0/10 | 0/10 |

**Table 2.** The primary balanced score averages valid acceptance and invalid/wrong rejection over ten planned calls each. Malformed and truncated outputs count as unsuccessful. Qwen's zero is an interface-level all-call score, not a measurement of mathematical accuracy conditional on usable predictions.

Llama emitted the literal label VALID for every trace, including all twenty invalid traces. Its [summary](../pilot/results/2026-09-16-verification-only/llama32/SUMMARY.md) therefore shows complete output usability but no successful invalid-trace rejection. Qwen's [summary](../pilot/results/2026-09-16-verification-only/qwen3vl/SUMMARY.md) shows thirty malformed, length-stopped outputs, each consuming the sixteen-token generation allowance. Some raw text begins with a label followed by explanation; extracting that prefix would change the frozen rule. With no usable labels, Qwen's conditional verification accuracy is not estimable. The result establishes failure of this constrained interface, not general mathematical incapacity. No additional inference or intervention followed this bounded screen.

### 4.6 Runtime preflight stopped before ProcessBench calibration

The [archived runtime check](../pilot/results/2026-09-16-processbench-preflight/README.md) contains one explicitly non-generating debug-render request and no calibration or evaluation attempts. The helper initially read `debug_info` instead of the actual `_debug_info` response field and failed closed before tokenization. The request's render-only flag was correct. Earlier mock tests and AI review missed this wire-schema mismatch; the reader and fixture were corrected offline, with resource sampling moved immediately after loading and before response validation. No live retry followed.

A subsequent shared-machine observation with the 8,192-token model context resident showed memory-pressure level 2 versus baseline 1, approximately 1.303 GiB additional swap usage and 1.756 GiB additional swapouts. These changes exceeded the prospective resource limits. Cleanup verified that the model had unloaded and pressure returned to normal; swap usage remained elevated. Global memory measurements do not isolate the model's contribution from concurrent office activity. The preflight lasted 4.53 seconds, and cleanup was checked 95.26 seconds after its start. No exact prompt tokenization or model-accuracy measurement completed, and the total remains 232 generated completions. Both reserved ProcessBench cohorts remain unused.

### 4.7 M4 preflight stopped at the resource guard

The September 21 [M4 archive](../pilot/results/2026-09-21-processbench-m4/README.md) records a separate session on the verified 16 GiB Apple M4, using the corrected helper and an isolated loopback service. One explicitly non-generating debug-render request completed. The immediate post-load resource check then failed: pressure rose from level 1 to level 2, free memory fell from 36% to 15%, and swap usage and swapouts each grew by approximately 1.565 GiB. The resource check precedes response validation, so the corrected render reader was not reached or live-validated. No exact token checks or subject answers completed. The report spans 6.68 seconds from budget start to recorded failure.

An independent cleanup observation 42.75 seconds after budget start confirmed normal pressure level 1, 42% free memory, closed service and runner ports (11435 and 58358), and absence of the owned research process group. These times exclude earlier idle service setup. Swap usage remained elevated. These global measurements cannot separate model loading from concurrent machine activity; they do not establish that an M4 with this capacity is generally unable to run the protocol. The session is closed, and its blocked report cannot authorize resumption. A future attempt requires a resource-feasible low-workload session and a fresh documented preflight without relaxing the existing guards. Both reserved cohorts remain unused, and the generated-completion total remains 232.

## 5. Discussion and limitations

The completed Llama v3 run separates successful initial arithmetic from failure of the broader generation-and-verification interface. High answer accuracy conditional on parsing is insufficient when half of all responses fail the required contract. Similarly, rejecting invalid traces is insufficient when every parseable valid-trace judgment also rejects. The binary screen adds a different failure: Llama produces only VALID, while Qwen exhausts the short token allowance on every call. These diagnostics justify withholding intervention experiments until the measurement task supports both valid acceptance and invalid rejection.

The evidence remains narrow. Ten reused questions cannot establish general alignment behavior. Fixed first-error positions prevent a genuine localization test; unequal error counts confound conclusion comparisons. Conversational and standalone conditions differ in history and prior calculations, so their contrast does not isolate commitment. One confidence phrase provides limited rhetorical coverage. Two quantized models with different patterns of unusable output do not support broad model-family comparisons. Held-out and repeated-call evaluations remain absent.

The earlier protocol revisions changed prompts, output constraints, and available computation together. Their outcomes establish only package-level feasibility differences. The post-hoc extraction analysis is explicitly selected after failures and cannot serve as confirmatory evidence. Written calculations are observable text, not proof of faithful internal reasoning. The verification-only screen did not yield usable, balanced judgments for either model. The separate prospective ProcessBench plan addresses the next measurement check; this completed screen supplies no basis for expanding an intervention study.

## 6. Reproducibility and AI assistance

The [pilot guide](../pilot/README.md) supplies commands and environment requirements. The archived Llama freeform manifest records execution commit `fc043ce97ea515d880557dd60b62067f00720000`, script and dataset hashes, model digest, template hash, and generation settings. [Raw conversations](../pilot/results/2026-09-15-freeform-v3/llama32/responses.jsonl) and [session logs](../pilot/results/2026-09-15-freeform-v3/llama32/sessions.jsonl) preserve outputs and client timing. The verification-only [Llama manifest](../pilot/results/2026-09-16-verification-only/llama32/manifest.json) and [Qwen manifest](../pilot/results/2026-09-16-verification-only/qwen3vl/manifest.json) both record commit `9b5d5734f7ec79c87f68b3313d1186c7534139a7`, including protocol-document and dependency hashes. Their session logs record approximately 15.9 and 36.2 seconds of client execution, respectively (52.1 seconds combined), excluding development, idle time, and short post-request keep-alive periods. Reproduction should use the recorded versions rather than silently resume with edited code.

The M4 preflight was frozen at commit `017f1d708943876bda16bba67cc32b97c9ebaa14`. Its [archive](../pilot/results/2026-09-21-processbench-m4/README.md) preserves source and runtime identities, resource observations, the failed report, and cleanup evidence. The SSH transport supplies code and inputs in memory without saving research files on the M4; research records are stored on the controller and versioned in GitHub. No calibration or evaluation response is implied by a debug-render request. Closed or blocked reports must remain immutable rather than being reused to reset budgets.

AI assistants contributed literature synthesis, implementation, methods review, and drafting. The [Claude review](../pilot/reviews/claude-methods-review.txt) and protocol record advice and adoption decisions, not validated evidence. Hosted research assistance is separate from local inference. Human authors must verify claims, references, examples, code, and the eventual venue's disclosure requirements.
