# Literature decision: evidence × confidence arithmetic

September 21, 2026. **Offline, AI-assisted methods review; no new experiments.** Compared with [TASK_MATCHED_DESIGN_DRAFT.md](TASK_MATCHED_DESIGN_DRAFT.md). This is a scoped comparison, not an exhaustive novelty assessment or independent reproduction of published results.

## Decision

**Do not present the current draft as a new conference contribution.** It is a reasonable measurement-development or controlled-replication exercise, but its central distinction and experimental ingredients overlap substantially with existing work. A shorter task, executable labels, local execution, or a smaller checkpoint does not by itself establish a valuable new scientific result. This conclusion does not rule out a contribution after a narrower question and broader literature check.

## Versions and retrieval coverage

Primary full texts were freshly retrieved on September 21, 2026. Versioned links below fix what was reviewed; repository code, raw data, and implementation fidelity were not audited.

| Paper | Version and inspected coverage |
| --- | --- |
| Ma et al., *Sycophancy Suppression Can Impair Rational Updating: Anti-Sycophancy Should Preserve the Ability to Update* | [v1, August 27, 2026](https://arxiv.org/html/2608.26511v1): §§2–6, Appendix A; [PDF](https://arxiv.org/pdf/2608.26511v1) limitations and evidence prompts. |
| Yang and Yeung, *Resist and Update: Counterfactual Report Coordinates for Incentive-Compatible LLMs* | [v2, July 21, 2026](https://arxiv.org/html/2607.12985v2): §§3–7, particularly §6.5; [PDF](https://arxiv.org/pdf/2607.12985v2). Earlier v1 was also consulted; v2 governs this comparison. |
| Kim and Khashabi, *Challenging the Evaluator: LLM Sycophancy Under User Rebuttal* | [v1, September 20, 2025](https://arxiv.org/html/2509.16533v1): §§3–4, Appendices A/D; [PDF](https://arxiv.org/pdf/2509.16533v1) supplies actual prompt boxes. |

Some prompt boxes were absent from extracted HTML and recovered from PDFs. No paper was inaccessible. An uninspected repository or unreported detail is **unknown**, not evidence that a method or control does not exist.

## 1. Sycophancy Suppression Can Impair Rational Updating

The study partitions examples by initial correctness, distinguishing unsupported correct-to-wrong changes from evidence-driven wrong-to-correct changes. Conditions include pressure, reference evidence, and the same evidence framed as a user's claim. Numerical reasoning is already represented by AQuA, and Llama-3.2-3B-Instruct is among its backbones. The work additionally evaluates training and activation interventions. Our behavioral draft cannot inherit those intervention or mechanistic claims. [§§2–6](https://arxiv.org/html/2608.26511v1)

Thus neither the two types of updating, numerical questions, initial-correct denominators, nor small-model evaluation is new here. Our exact confidence-by-calculation crossing differs in implementation, but this alone is a weak extension. A relevant boundary is that the paper explicitly leaves unreliable, conflicting, and false evidence outside its controlled evidence setup. Evidence provenance also varies by analysis: Appendix A distinguishes earlier generated TruthfulQA notes from later source-grounded evaluation notes; describing all evidence uniformly would be inaccurate. [Appendix A and PDF limitations](https://arxiv.org/pdf/2608.26511v1)

## 2. Resist and Update

Its controlled task has externally known Bayesian targets, object evidence, reliability-weighted testimony, and matched pressure/style/prestige conditions. Natural-question transfer includes reliable correction while a user proposes a different wrong answer. Most importantly, **v2 §6.5 already describes a fully counterbalanced crossing of truth, prior agreement, source reliability, and pressure wording**, including false-but-declared-reliable cases. Its target follows the reliability-implied posterior, rather than unconditional agreement with objective truth. [§§3–4, 6.4–6.5](https://arxiv.org/html/2607.12985v2)

This blocks a broad claim that our factorial design newly separates evidence from pressure or newly uses known truth. Our exact-calculation validity is a different construct from source reliability; that difference needs a specific hypothesis, not a generic novelty statement. The paper also studies internal interventions beyond our proposed measurements. The older [NOVELTY_AUDIT.md](NOVELTY_AUDIT.md) links v1: its narrower comparison must not substitute for this v2 assessment. [§§5–7](https://arxiv.org/html/2607.12985v2)

## 3. Challenging the Evaluator

This study forms disagreeing answer pairs from model responses to multiple-choice questions and keeps the challenging response fixed across downstream conditions. It varies full, truncated, or absent reasoning; casual and assertive rebuttals; and conversational versus simultaneous judging. Adoption is reported conditional on initial correctness. Incorrect reasoning and persuasive language are already central concerns. [§§3–4](https://arxiv.org/html/2509.16533v1)

Our draft uses generated exact arithmetic and a compact paired factorial instead of sampled model arguments and these particular rebuttal templates. That improves experimental control for our question, but does not establish that reasoning presence, confidence, or conditional adoption is a new object of study. The original prompts are available in Appendix D; an empty HTML prompt section must not be interpreted as missing disclosure. [PDF Appendix D](https://arxiv.org/pdf/2509.16533v1)

## A narrower candidate — not a verified gap

An offline question worth checking is: **Does confidence change sensitivity to a locally falsifiable derivation error when the proposed conclusion remains correct?** Construct matched valid and invalid short derivations, keep the correct conclusion identical, and vary confidence independently. This separates conclusion correctness from justification validity more directly than the current valid-evidence-versus-no-evidence draft.

However, the three papers above already cover substantial neighboring territory. Absence of this exact contrast in the inspected conditions is not proof of absence from the literature. Before adopting it, review proof-verification, misleading-rationale, outcome-versus-process, and sycophancy studies, including the separately researched supplemental comparisons. Confirm that the contrast adds knowledge beyond an existing benchmark ablation. If not, stop this candidate and choose a clearly labeled replication or a specific public-data reanalysis question.

## Concrete next step and limits

1. Human-review a one-page claim-to-prior-work table and a few development-only examples. Specify what observation would resolve a remaining scientific uncertainty.
2. Check whether available public data already permits that analysis before designing new model calls. Parser repair alone is not presumed novel.
3. Only after a defensible question exists, set prospective task adequacy and resource requirements. Ordinary office workload remains mandatory; this memo authorizes no model run, larger-model escalation, or quiet-window assumption.

Prior failed cohorts, scores, and admission gates remain closed and unchanged. A runtime diagnostic cannot establish scientific adequacy. No exposed development or calibration example becomes held-out evaluation data.
