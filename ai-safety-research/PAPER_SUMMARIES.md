# Paper summaries: sycophancy, correction, and activation steering

[Research index](README.md) · [Research implications and reading order](RESEARCH_DIRECTION.md)

Reviewed September 15, 2026. These summaries cover the full manuscripts and relevant appendices; key quantitative tables were also visually checked. Results below are reported by the authors, not independently reproduced here. “Limitations” and “Project relevance” include our assessment of the evidence.

## Terms

- **Sycophancy:** adapting an answer to agree with a user at the expense of truth or independent judgment. Agreement alone is not necessarily sycophancy.
- **Activation steering:** changing a model's internal activations during inference to influence its behavior.
- **Probe:** a small classifier trained to detect information in activations. Detection does not establish that intervening on that information improves behavior.
- **Percentage points (pp):** the absolute difference between percentages. Moving from 50% to 40% is a 10-point decrease, not a 10% relative decrease.

## 1. Towards Understanding Sycophancy in Language Models

**Source:** [Paper — ICLR 2024](https://arxiv.org/abs/2310.13548). Reviewed manuscript: [v4 PDF](https://arxiv.org/pdf/2310.13548v4).

### Question

Why do assistants agree with users at the expense of truth, and does human feedback contribute?

### Method and findings

The authors evaluate five models on changing feedback with user preferences, abandoning correct answers after challenges, following incorrect suggestions, and repeating false assumptions.

They analyze human preference data and compare truthful and sycophantic responses. Agreement with users' beliefs predicts preference judgments; convincing false answers can receive favorable evaluations.

Optimizing preference models has **mixed effects** across sycophancy tests. The paper does not establish reinforcement learning from human feedback as the sole cause.

### Limitations

The models are historical, some evaluation uses model judges, and the preference analysis is partly observational. Agreement itself is not necessarily an error.

### Project relevance

Define the target precisely: **changing a correct answer because of unsupported user pressure** is more measurable than “being agreeable.” Evaluate correctness, tone, and willingness to reconsider separately.

## 2. Steering Llama 2 via Contrastive Activation Addition

**Source:** [Paper — ACL 2024](https://aclanthology.org/2024.acl-long.828/).

### Question

Can a simple internal intervention control behaviors such as sycophancy, refusal, and hallucination without updating model weights?

### Method and findings

The authors collect activations for contrasting responses and subtract their averages:

```text
v = mean(h_positive) - mean(h_negative)
h_steered = h + alpha * v
```

The coefficient `alpha` controls strength and direction. Llama 2 experiments show behavioral changes in multiple-choice and open-ended evaluations. Effects depend on the layer, behavior, and strength.

**Measurement detail:** Table 12's TruthfulQA change from **0.60 to 0.62** measures average probability assigned to the correct option, not an increase from 60% to 62% answer accuracy.

### Limitations

Some behavioral test sets are small, open-ended evaluation uses a model judge, and capability checks do not establish comprehensive preservation of ability.

### Project relevance

This is the foundational implementation paper. Treat steering as an intervention whose benefits and collateral effects both require measurement, not as a universal “honesty switch.”

## 3. Large Language Models Cannot Self-Correct Reasoning Yet

**Source:** [Paper — ICLR 2024](https://arxiv.org/abs/2310.01798). Reviewed manuscript: [v2 PDF](https://arxiv.org/pdf/2310.01798v2).

### Question

Can models improve reasoning by reviewing their answers without reliable external feedback?

### Method and findings

The authors distinguish **intrinsic self-correction**, where the model decides whether and how to revise, from **oracle-assisted correction**, where ground-truth information determines when correction is needed.

They test reasoning benchmarks with several models and repeated correction rounds. In Table 3, GPT-4's GSM8K accuracy falls from **95.5% to 91.5%, then 89.0%** under intrinsic self-correction. Oracle-assisted correction improves results.

Revision repairs some mistakes but damages some correct answers. The model struggles to distinguish those situations.

### Limitations

The results concern particular historical models, prompts, and tasks. They do not establish that all newer models, or systems with verifiers and external evidence, cannot self-correct.

### Project relevance

Report both **wrong → correct** and **correct → wrong** transitions. More reasoning rounds or debating agents should not automatically be treated as improvements.

## 4. Dual-Stance Evaluation of Sycophancy: The Structure of Agreement and the Limits of Intervention

**Source:** [Paper — 2026 preprint](https://arxiv.org/abs/2606.11205). Reviewed manuscript: [v1 PDF](https://arxiv.org/pdf/2606.11205v1).

### Question

Does a model agree with contradictory user positions, and does reducing that tendency damage appropriate agreement?

### Method and findings

The evaluation presents opposing stances on the same topics. The main experiment uses Llama 3 8B, 25 topics, two stances per topic, and repeated sampled responses.

Steering reduces agreement with both sides, but effects depend on topic type and conversational framing. It can also reduce agreement with correct factual statements.

Representation-geometry measurements do not independently establish the mechanism causing these differences.

### Limitations

The central evaluation is small and mostly concerns one model. Repeated generations increase sampling precision without increasing topic diversity.

The main text describes parser validation as human validation, while Appendix B identifies Claude as the independent judge. Strong steering produces more unparseable responses.

### Project relevance

A model can appear less sycophantic simply by agreeing less often. Establish whether its disagreements are **correct and justified**.

## 5. Stubborn or Sycophantic? GEPA-Evolved Prompts Under Pressure

**Source:** [Manuscript](https://ahmedtaha.io/documents/Stubborn-or-Sycophantic.pdf). The reviewed PDF is marked under review at COLM 2026; this is not evidence of main-conference acceptance.

### Question

Do automatically optimized anti-sycophancy prompts preserve acceptance of correct suggestions?

### Method and findings

The authors compare prompts across three small model families using 600 questions with three paraphrases each.

- **WrongFlip:** an initially correct answer becomes incorrect after a wrong suggestion.
- **Update:** an initially incorrect answer becomes correct after a correct suggestion.

For Llama, the compact prompt lowers WrongFlip from **99.2% to 45.5%**, but also lowers Update from **97.2% to 51.2%** (Table 1): a substantial trade-off.

### Limitations

Prompts also change initial answers. Different conditions can therefore contain different initially correct and initially wrong question sets. Results combine changes in initial competence with changes in responsiveness.

The main table contains single-run point estimates.

### Project relevance

This directly overlaps the original research question. For a cleaner comparison, reuse the **same initial answers and eligible questions** across intervention conditions.

## 6. SWAY: A Counterfactual Computational Linguistic Approach to Measuring and Mitigating Sycophancy

**Source:** [Paper — 2026 preprint](https://arxiv.org/abs/2604.02423). Reviewed manuscript: [v1 PDF](https://arxiv.org/pdf/2604.02423v1).

### Question

How do wording changes, such as stronger commitment or reversing a stated preference, affect model judgments?

### Method and findings

SWAY constructs matched prompt variations and measures response-distribution differences across six models and three judgment, preference, and debate tasks.

Simple anti-sycophancy instructions work inconsistently. Counterfactual examples generally reduce measured sensitivity, although some models retain effects or overcorrect.

An appendix evidence experiment uses model-generated supporting and opposing arguments; answers shift in corresponding directions.

### Limitations

Many questions lack objectively verifiable answers, so lower framing sensitivity does not automatically mean higher truthfulness.

The evidence experiment does **not** establish sensitivity to logically valid versus invalid derivations. Independent validation of the generated arguments' factual or logical quality is not established.

### Project relevance

Borrow the matched-prompt design: hold substantive content constant while varying user confidence or framing. Separate **sensitivity to evidence** from **sensitivity to social pressure**.

## 7. Sycophancy Hides Linearly in the Attention Heads

**Source:** [Paper — EACL 2026](https://aclanthology.org/2026.eacl-long.324/).

### Question

Where does sycophancy-related information appear inside small models, and which locations are useful intervention targets?

### Method and findings

Using Gemma 3 4B and Llama 3.2 3B, the authors train probes on different internal components and compare steering interventions.

Attention-head interventions outperform several alternatives. For Llama, harmful correct-to-incorrect flips fall from **51.7% to 25.0%**, while second-answer accuracy rises from **37.2% to 49.3%**. For Gemma, harmful flips fall from **40.7% to 34.4%** (Tables 3–4).

Strong probe performance does not necessarily identify the most effective intervention location.

### Limitations

The study covers two models, uses model-assisted correctness judgments, and does not center a matched valid-correction test. Initial-answer accuracy also changes between intervention conditions.

Attention patterns alone do not constitute a complete causal explanation.

### Project relevance

This is relevant to small-model constraints. Study it after CAA, but implement a simple residual-stream baseline before adding attention-head selection and intervention complexity.

## 8. Gated Activation Steering for Reducing Sycophancy & Hallucination in Medical Question Answering

**Source:** [Paper — 2026 preprint](https://arxiv.org/abs/2608.23666). Reviewed manuscript: [v1 PDF](https://arxiv.org/pdf/2608.23666v1).

### Question

Can selective steering reduce harmful behavior while limiting unnecessary interference?

### Method and findings

The system learns behavior detectors and steering directions, then adjusts intervention strength using detector outputs and token position.

MedGemma 1.5 4B and Gemma 3 12B are evaluated on medical-record questions and escalating misleading pressure. The authors report substantial improvements alongside some harmful interventions.

They also test 100 correction examples with an **injected incorrect previous answer**. Gemma shows no explicit premise-denial failures; MedGemma shows two. This narrow measure does not prove every answer is correct.

### Limitations

Medical data, additional judges, calibration components, and GPU experiments make the complete pipeline expensive to reproduce. Injected wrong histories differ from naturally occurring errors.

Semantic similarity to baseline responses does not guarantee preserved factual accuracy.

### Project relevance

Conditional steering is a later extension. First establish whether an always-on intervention harms valid correction, then test whether a gate improves the trade-off.

## 9. Dissociating the Internal Representations of Sycophancy in LLMs

**Source:** [Paper — 2026 preprint](https://arxiv.org/abs/2607.07003). Reviewed manuscript: [v3 PDF](https://arxiv.org/pdf/2607.07003v3).

### Question

Do factual sycophancy and opinion-based agreement share an internal representation?

### Method and findings

The authors construct factual and opinion conversations, label responses, and train probes on Gemma 3 12B and Llama 3.1 8B.

Probes perform well within each category. Transfer is stronger in Gemma than Llama. Shared and category-specific steering directions are also compared.

A direction capturing one form of sycophancy may not transfer uniformly to another.

### Limitations

The dataset uses synthetic histories and substantial model-assisted processing. Activations are extracted **after the response**: classification performance is not equivalent to predicting sycophancy before generation.

Simple text-feature classifiers already perform strongly, suggesting response wording explains part of the separability. Steering comparisons also involve validation-based choices.

### Project relevance

Specify the targeted behavior. Avoid treating factual capitulation, preference agreement, and reasoning failures as interchangeable, or describing one successful direction as a general alignment mechanism.

## 10. Reducing Sycophancy in Small Language Models with Runtime Activation Steering: Efficacy, Stubbornness, and Capability Trade-offs

**Source:** [Supplementary manuscript and repository](https://github.com/and270/selective-sycophancy-steering), specifically [paper/main.tex](https://github.com/and270/selective-sycophancy-steering/blob/main/paper/main.tex). This is the repository manuscript reviewed on September 15, 2026, not a verified peer-reviewed conference publication. The linked branch may change.

### Question

Does steering small models improve resistance to false pressure while damaging acceptance of correct suggestions?

### Method and findings

Four checkpoints use separate fitting, layer-selection, and evaluation splits. Initial answers are frozen across interventions.

Evaluation covers false pressure, correction of natural and injected mistakes, neutral token-distribution changes, and mathematics.

At the strongest reported intervention, Qwen 4B's pressure-error rate falls by **15.72 pp**, while natural correction acceptance falls by **1.94 pp**. Gemma E4B shows a larger benefit and correction cost.

Smaller checkpoints improve much less despite detectable internal signals.

### Limitations

The task uses binary answers and short pressure templates. Model comparisons have precision and intervention-scale confounds. Capability checks are limited; the repository has not been rerun here.

### Project relevance

This is the closest overlap with the original proposal. Frozen initial answers, natural correction tests, and small-model steering trade-offs are already present; those alone do not establish novelty.
