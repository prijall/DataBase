# Related work

## Evidence-sensitive updating and conversational evaluation

Answer changes following user feedback have different interpretations depending on the initial answer and the evidence supplied. Ma et al. distinguish unsupported changes away from correct answers from evidence-supported corrections of initially wrong answers. Their evaluation includes human-written AQuA rationales and presents supporting evidence both as a reference and as a user's claim. They report trade-offs across preference optimization, supervised fine-tuning, and activation steering. Consequently, preserving justified updating while reducing unsupported agreement is already an established research question. Our pilot adopts the distinction between initial-answer cohorts but does not evaluate an anti-sycophancy intervention. [Ma et al., 2026](https://arxiv.org/html/2608.26511v1) (`ma2026sycophancy`).

Conversational presentation is also an existing object of study. Kim and Khashabi compare user rebuttals with a single-turn judge setting that presents the original and challenging responses together. Their conditions include complete reasoning, truncated reasoning, answer-only challenges, and informal feedback. They find that presentation and reasoning content affect persuasion; a separate analysis assesses argument quality with an LLM judge. Our conversational-versus-standalone comparison therefore cannot establish that framing matters for the first time. Its narrower methodological feature is that every supplied arithmetic equality has an exact, executable validity label. The contexts still differ in history and prior calculations, so their contrast does not isolate the effect of commitment. [Kim and Khashabi, 2025](https://arxiv.org/html/2509.16533v1) (`kim-khashabi-2025-challenging`).

## Process verification and verifier strictness

ProcessBench evaluates whether a model identifies the earliest erroneous step or accepts an entirely correct mathematical solution. Its 3,400 cases have expert annotations, and its analysis explicitly includes incorrect reasoning that reaches a correct final answer. Separating answer correctness from process validity is therefore an established requirement, rather than a contribution of this pilot. Our generated equality chains provide a much narrower development setting with mechanically checkable labels. They do not match ProcessBench's difficulty, scale, annotation process, or variation in error position. [Zheng et al., 2025](https://arxiv.org/html/2412.06559v4) (`zheng-etal-2025-processbench`).

Zhou et al. study the tendency of generative verifiers to accept or reject reasoning steps. Their VerifySteer method combines a correctness probe with selective interventions at verification-paragraph boundaries, addressing the trade-off between accepting valid reasoning and detecting errors. This work motivates reporting these outcomes separately and comparing any future conversational effect against ordinary verification behavior. It also means that changing verifier strictness through steering, including in small models, would not alone constitute a new contribution. The present experiments contain no activation intervention and do not reproduce VerifySteer. [Zhou et al., 2026](https://arxiv.org/html/2605.20745v1) (`zhou2026hidden`).

## Updated design comparison

Yang and Yeung's *Resist and Update* v2 includes crossed truth, agreement, reliability and pressure conditions (§6.5). Factorial evidence-versus-pressure control is therefore not a contribution by itself. [Version 2](https://arxiv.org/html/2607.12985v2) (`yang2026resist`).

SycoBench-600 already reports correction selectivity with separate initial-answer populations and documents parser limitations. [Sinha, 2026](https://aclanthology.org/2026.findings-acl.1759/) (`sinha2026sycobench`). Ping et al. cross role, evidence, interaction structure and grounding in medical conversations. [Version 2](https://arxiv.org/html/2608.01017v2) (`ping2026givein`). These studies strengthen the decision to keep our revised arithmetic design as a development instrument while investigating a specific, reproducible public-log measurement question. The [updated comparison](../DESIGN_LITERATURE_COMPARISON_2026-09-21.md) and [supplement](../SUPPLEMENTAL_DESIGN_AUDIT_2026-09-21.md) record inspected sections and limits.

## Scope of the present study

These precedents motivate an unresolved question: whether an anti-sycophancy intervention changes sensitivity to verified reasoning errors differently across conversational and standalone contexts. The current pilot tests a prerequisite—whether the chosen local models and elicitation protocol yield usable, separately scored answers and trace judgments. It neither resolves that interaction nor establishes an unoccupied research gap. The supplied traces confound conclusion correctness with the number of false equalities, and all injected errors begin at the first step. A defensible extension requires addressing these limitations, checking additional related work, and evaluating a fixed intervention plan on held-out problems.

---

## Citation verification notes

Metadata and the cited methods were checked against primary sources on September 15, 2026. These notes support manuscript preparation; they are not part of the related-work argument.

| BibTeX key | Verified source and relevant evidence | Bibliographic treatment |
| --- | --- | --- |
| `ma2026sycophancy` | [arXiv record](https://arxiv.org/abs/2608.26511); manuscript §§2–3, §4.2, Appendix B. | arXiv preprint, version 1. The record reports acceptance to Findings of EMNLP 2026; no proceedings record was verified here. |
| `kim-khashabi-2025-challenging` | [Official proceedings and author metadata](https://aclanthology.org/2025.findings-emnlp.1222/); manuscript §3.4 and reasoning-quality analysis. | Findings of EMNLP 2025. Author spelling follows the official BibTeX: Sung Won Kim. arXiv identifier: 2509.16533. |
| `zheng-etal-2025-processbench` | [Official proceedings and author metadata](https://aclanthology.org/2025.acl-long.50/); manuscript §3.3, Table 2, and §4.1. | ACL 2025 long paper. arXiv identifier: 2412.06559; inspected manuscript version 4. |
| `zhou2026hidden` | [arXiv record](https://arxiv.org/abs/2605.20745); manuscript §§3–4 and Appendix A. | arXiv preprint, version 1. VerifySteer is the method name; the bibliography uses the full paper title. |

The two conference entries use verified ACL Anthology metadata and DOIs. The two arXiv entries make no independently verified proceedings claim. This four-paper section is a targeted comparison, not an exhaustive novelty review; [the broader audit](../NOVELTY_AUDIT.md) records remaining checks.

Additional metadata and methods were checked September 21, 2026: `yang2026resist` and `ping2026givein` remain versioned arXiv entries; `sinha2026sycobench` uses official ACL Anthology metadata. Their experiments have not been reproduced in this repository.
