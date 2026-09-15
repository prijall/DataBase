# Novelty audit: reasoning validity under anti-sycophancy interventions

Date: September 15, 2026. Prepared with AI assistance.

[Research index](README.md) · [Initial reading list](PAPER_SUMMARIES.md)

## Decision

**Do not claim the broad question as novel. Proceed only with a bounded diagnostic pilot of a narrower interaction.**

The follow-up search found substantial work missing from the initial reading list. Evidence-sensitive updating, persuasive flawed reasoning, process-error detection, and steering the acceptance/rejection trade-off all have close precedents. A new dataset name or a smaller model would not by itself establish a contribution.

The narrower candidate is:

> Does an anti-sycophancy intervention alter sensitivity to verified reasoning errors specifically when the reasoning is presented as a user correction, beyond its effect on neutral verification of the same reasoning?

This is a hypothesis worth screening, not a confirmed gap. A pilot can establish measurability and local feasibility; it cannot prove novelty or conference readiness.

## Search scope and evidence levels

Searched public web indexes for arXiv, ACL Anthology, OpenReview, publisher pages, and author repositories. Used methods sections, benchmark definitions, and relevant appendices to assess the closest matches. No experiments or repository implementations were rerun.

Representative executed queries:

- `sycophancy valid invalid reasoning correction evidence activation steering benchmark`
- `LLM correct incorrect feedback rationale validity sycophancy RefuteBench`
- `"sycophancy" "valid" "invalid" reasoning`
- `"sycophancy" "evidence" "steering" correction`
- `"anti-sycophancy" "invalid" reasoning`
- `"sycophancy" "proof" "validity"`
- `"ProcessBench" identify erroneous steps reasoning`
- `"CriticBench" critique correction benchmark`

This was a targeted search and limited citation tracing, not an exhaustive systematic review. “Not identified” below refers to inspected material, not proof of absence. Preprints and repository claims are not treated as independently validated results.

## Overlap matrix

| Study | Inspected evidence | Already covers | Remaining distinction or uncertainty |
| --- | --- | --- | --- |
| [Sycophancy Suppression Can Impair Rational Updating](https://arxiv.org/html/2608.26511v1) | Sections 2–4, 6; Appendix A and intervention accounting | Anti-sycophancy versus evidence-based updating; human-written math rationales; source framing; steering and training interventions | Matched corruption of reasoning while retaining the correct conclusion was not identified in the listed conditions. |
| [Resist and Update](https://arxiv.org/html/2607.12985v1) | Sections 3, 5–7 | Controlled evidence/pressure separation, known Bayesian targets, internal interventions, worked-solution correction examples | Manipulates stated source reliability; it does not establish our proposed derivation-error contrast. |
| [Challenging the Evaluator](https://arxiv.org/html/2509.16533v1) | Sections 3–4, reasoning-quality analysis | User rebuttals, reasoning depth, correctness, linguistic style, neutral judging | Reasoning quality uses an LLM judge on a subset. A paired, machine-verified error intervention combined with anti-sycophancy steering was not identified. |
| [SycEval](https://arxiv.org/html/2502.08177v4) | Methods, rebuttal construction, metrics | Math and medical questions, justifications and citations, helpful and harmful answer changes | Rhetorical strength is not a controlled measure of derivation validity. |
| [ProcessBench](https://arxiv.org/html/2412.06559v1) | Sections 3–4, Table 2 | Human-annotated first-error detection, including flawed reasoning with correct final answers | Supplies an existing verification task; creating such examples alone is not new. |
| [VerifySteer](https://arxiv.org/html/2605.20745v1) | Sections 3–5 and method description | Steering verifier strictness, accepting correct steps versus detecting errors, selective intervention | The inspected task concerns verification rather than matched user-correction pressure. It is a necessary methodological comparator. |
| [RefuteBench](https://arxiv.org/html/2402.13463v2) | Task definition, Sections 4–5 | Feedback acceptance, application, and generalization | QA includes counterfactual knowledge edits. Its desired instruction-following behavior is not the same as preserving real-world truth. |
| [CriticBench: Benchmarking LLMs for Critique-Correct Reasoning](https://arxiv.org/abs/2402.14809) | Abstract and [author repository](https://github.com/CriticBench/CriticBench) | Generation, critique, and correction across reasoning domains | Full protocol review remains outstanding; do not infer absence of a control from the abstract. |
| [FaithformBench](https://arxiv.org/abs/2608.10916) | Abstract only; HTML manuscript retrieval failed | Perturbed invalid reasoning and preservation of validity/invalidity during autoformalisation | Adjacent formal-verification work; full methods review remains outstanding. |
| [Sycophancy Construct Validity](https://github.com/lciric/sycophancy-construct-validity) | Repository README, evaluation and limitations | Reports polarity/style confounds and limits of interpreting probes as causal mechanisms | Repository-level evidence only; no independent rerun or publication-status verification. |

## Four papers that change the immediate plan

### 1. Sycophancy Suppression Can Impair Rational Updating

Ma et al. distinguish unsupported yielding from evidence-supported correction across four datasets and four open models. AQuA supplies human-written rationales; evidence is also reframed as a user's claim. They test DPO, SFT, and steering, and explore orthogonalization. Therefore, adding mathematical evidence or studying an update trade-off is already covered. The explicit four-condition protocol does not show matched valid/invalid derivations. Note that Table 1 is calibration-set performance, whereas intervention comparisons use held-out data. [Sections 2–4, 6 and Appendix A](https://arxiv.org/html/2608.26511v1)

### 2. Resist and Update

Yang and Ye use a synthetic Bayesian setting with computable posteriors. Stated testimony reliability determines whether disagreement should change the answer. Their intervention uses a counterfactual reference, with a more limited single-pass variant. This is already a controlled evidence-versus-pressure study, not merely an agreement benchmark. Its construction differs from checking the validity of supplied derivations; those differences need a scientific justification, not just different terminology. [Sections 3, 5–7](https://arxiv.org/html/2607.12985v1)

### 3. Challenging the Evaluator

Kim and Khashabi compare full, truncated, and answer-only rebuttals, casual assertions, and neutral judging. They report greater persuasion with more reasoning, including incorrect reasoning. A separate analysis scores argument quality with an LLM judge. Thus, “flawed reasoning persuades models” and “neutral review differs from rebuttal” are existing questions. A possible extension must isolate verified error content and intervention effects rather than repeat those observations. [Sections 3–4](https://arxiv.org/html/2509.16533v1)

### 4. VerifySteer

Zhou et al. extract verification-specific directions and intervene at verification paragraph boundaries. They explicitly study the trade-off between detecting errors and accepting correct reasoning, then introduce adaptive routing. Their model range includes a 1.7B checkpoint, so small-model steering is not a novelty claim. The reported fitting pipeline uses substantial sampling; reproducing its full method is not assumed to fit our budget. A neutral-verification comparison is essential to distinguish conversational effects from general strictness changes. [Sections 3–5](https://arxiv.org/html/2605.20745v1)

## Claims to avoid

- “Anti-sycophancy can make models stubborn” as the contribution.
- “We are the first to test evidence-based correction.”
- “Correct final answers establish valid reasoning.”
- “We introduce steering that trades error detection against accepting correct reasoning.”
- “Using small models or running locally makes the study scientifically novel.”
- “No matching search result proves the gap exists.”

## Proposed diagnostic pilot

These are design proposals, not completed work or fixed final-paper methods.

### Task construction

Create ten development problems in a restricted arithmetic or elementary-logic domain, each with three verified reasoning traces:

1. Correct conclusion with valid steps.
2. The same correct conclusion with a demonstrably invalid intermediate step.
3. An incorrect conclusion with invalid reasoning.

Use executable checks for the restricted operations and manually audit every pilot example. Record the first erroneous step and the correct answer separately. Do not call arbitrary natural-language proofs verified simply because a final calculation passes.

Match trace length, format, and error position where feasible. A correct conclusion cannot be made invalid; it is the argument supporting it that contains an error. A model may legitimately accept the correct answer while rejecting the supplied argument.

### Baseline calls

For one model:

- Ten initial answers, generated once and preserved verbatim.
- Four follow-up types per problem: unsupported wrong suggestion, valid/correct trace, invalid/correct trace, invalid/wrong trace.
- Two presentation styles per follow-up: neutral and confident.
- Thirty standalone verification calls: the three traces for each problem, without a prior model commitment or user-correction framing.

This is **120 planned completions**: `10 + 10 × 4 × 2 + 10 × 3`. It is a development screen, not enough evidence for a publication claim. Record initial-correct and initial-wrong cohorts separately. If natural errors are too rare, adjust development-task difficulty rather than fabricate model mistakes and call them natural.

Request an answer, a trace-validity judgment, and a first-error index where a trace exists. Mark the latter fields inapplicable for unsupported suggestions. Scoring must retain invalid outputs explicitly. Standalone and conversational tasks should use compatible output instructions; context differs intentionally.

### Intervention stage, only after baseline feasibility

Fit a simple anti-sycophancy direction on separate development material. Freeze the original conversation prefixes and compare unsteered, steered, prompt-baseline, and norm-matched random-direction conditions. Select layers and strengths without using the eventual test set.

Measure:

- Correct-answer retention under unsupported pressure.
- Correction acceptance on naturally wrong initial answers.
- Acceptance of fully valid traces.
- Rejection and first-error localization for invalid traces.
- False endorsement of invalid traces whose conclusion is nevertheless correct.
- The change in these verification measures in correction context versus standalone review.

Do not collapse answer accuracy and trace validity into one score. A context-specific difference suggests an interaction to investigate; it does not alone identify a causal psychological mechanism. Compare several strengths to see whether the effect is explained by a uniform accept/reject threshold shift. Cluster uncertainty estimates by underlying problem in the later, adequately sized evaluation.

### Local feasibility and stopping rules

Use one available small model first. Model choice, memory fit, and runtime remain unmeasured. Do not assume full VerifySteer training or large-model comparisons fit the M4. Keep all experimental inference local, share no office data, and cap combined experiment execution at the agreed nine machine-hours/week.

Advance beyond development only if the checker and parser work, baseline tasks avoid universal success/failure, and throughput supports a larger evaluation. Stop or redesign if the entire effect is a parsing artifact, generic disagreement, or ordinary verification degradation. A scientifically useful negative result is possible, but a weak pilot is not automatically publishable.

## Remaining literature checks

- Inspect the full CriticBench and FaithformBench methods; distinguish similarly named CriticBench projects by title and authors.
- Trace references and later citing work for VerifySteer and the three closest conversational studies.
- Inspect available benchmark implementations to determine whether proposed matched-error conditions already exist in released data.
- Search process-verification work for social framing, self-preference, and claimed authorship effects before asserting a context-specific gap.

## Division of work

AI assistants can prepare the generator, checker, inference scripts, and audit tables. A separate review pass should check the implementation against the written specification and sources. The researcher should inspect the ten examples, understand the outcomes, and review the final novelty argument with a human research contact when possible.

Current deliverable: this audit and the revised pilot specification. No model runs, verified pilot dataset, or steering implementation have been completed as part of this audit.
