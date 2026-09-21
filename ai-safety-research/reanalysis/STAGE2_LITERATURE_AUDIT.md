# Stage 2: focused measurement literature check

September 21, 2026. **Decision: proceed only as a descriptive replication/measurement diagnostic. Do not claim a new taxonomy or a conference-ready contribution.** Stage 1 results and validation counts were already known; Stage 2 component counts and selected review responses have not been inspected when this plan is written.

## Closest primary sources

| Source/version | Inspected evidence | Consequence for this project |
| --- | --- | --- |
| Çelebi, Ezerceli and El Hussieni, **PARROT**, [2511.17220v2](https://arxiv.org/html/2511.17220v2), December 1, 2025 | §3.4 and Table 1 distinguish following an incorrect suggestion from changing to another wrong answer. §3.2 describes paired base/manipulated prompts; Appendix A reports category distributions. | Direct overlap: separating suggestion matching from other correctness loss is already established. Applying it to another release is a diagnostic, not a new behavioral taxonomy. |
| Fanous et al., **SycEval**, [2502.08177v4](https://arxiv.org/html/2502.08177v4), September 19, 2025 | Methods separate response correctness categories, describe rebuttal evaluation, and include human checks of automated judgments. | Distinguishing correctness, response failure and evaluation validity is not new. This paper uses different tasks and judging; its rates cannot be compared directly with our letter parser. |
| Ye et al., **What Counts as AI Sycophancy?**, [2605.21778v1](https://arxiv.org/html/2605.21778v1), May 20, 2026 | Abstract, introduction and taxonomy distinguish behaviors studied under the same label; the review covers 70 papers and an expert survey. | Broad construct ambiguity is already documented. Our claim must concern a specific operational measurement, not a newly discovered ambiguity of “sycophancy.” |
| Young, **Measuring Faithfulness Depends on How You Measure**, [2603.20172v2](https://arxiv.org/html/2603.20172v2), March 23, 2026 | §§3–4 and discussion compare classifiers on fixed reasoning traces and disclose lack of human ground-truth labels. | Generic classifier sensitivity and possible ranking changes are also established. This concerns hint acknowledgment, not our MCQ answer-selection task; its limitations motivate review but do not prove an unoccupied gap here. |
| Sinha, **SycoBench-600**, [pinned release source audit](SOURCE_METHODS_AUDIT.md) | The paper/code define WrongFlip as loss of correctness, disclose parsing/missingness issues, and use separate correction populations. | A lower suggestion-match rate would not demonstrate a misimplemented WrongFlip metric. Preserve its definition and test only interpretations that equate it with agreement. |

These are inspected primary manuscripts. arXiv records were checked for versions; this document does not independently establish proceedings acceptance for the four arXiv entries. Earlier versions of PARROT, SycEval and Young were encountered during search; the decisions above use the latest versions verified here. No study beyond SycoBench's released calculations has been reproduced by this project.

## Search scope and limits

Queries included `sycophancy benchmark "suggested answer" "incorrect" agreement measurement`, `LLM sycophancy "unparseable" "adoption"`, and `sycophancy evaluation "answer switching" "agreement" benchmark`, followed by exact-title primary-source retrieval. Secondary results were discovery leads only. This is a focused overlap check, not a systematic review or proof that no related work exists. Absence of a word in one paper is not evidence of novelty.

## Bounded next step

1. Preserve the original parser and fixed baseline-correct cohorts. Decompose released wrong-suggestion outputs into retained correctness, suggested-letter match, other parsed wrong choice, and no parsed choice.
2. Report finite-release counts and fractions without significance tests, causal attribution or model rankings.
3. Prepare at most 28 examples with model and automatic labels hidden from the reviewer. Human annotations remain blank until a person supplies them; one person's review is qualitative and cannot establish population parser accuracy.
4. Interpret only after checking the original response text, retry metadata and the existing paper's formal definition. Do not turn every mechanically measured difference into an alignment claim.

## Contribution decision

**Already occupied:** the taxonomy, “measurement choices matter,” and an arithmetic difference between two metric definitions. **Still unresolved:** whether a validated measurement issue has a substantive consequence that generalizes beyond one released benchmark. A credible extension would need an explicit claim, adequately sized independent human annotation, an additional independent artifact and a comparison against the nearest methods. None is established by this bounded diagnostic; the right outcome may be a useful replication note and a decision to stop this direction.

The [Stage 2 protocol](STAGE2_PROTOCOL.md) therefore defines a small diagnostic and review packet, not a paper acceptance target. It remains compatible with shared office hardware and requires no model inference.
