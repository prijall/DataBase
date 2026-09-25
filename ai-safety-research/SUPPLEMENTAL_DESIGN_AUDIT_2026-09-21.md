# Additional overlap and measurement audit

September 21, 2026. Primary-source desk review, supplementing the [three-paper comparison](DESIGN_LITERATURE_COMPARISON_2026-09-21.md). No new inference or reproduction of published scores. This is a targeted search, not a systematic review.

## Additional close studies

**SycoBench-600 (Sinha, Findings of ACL 2026).** Sections 3–5 describe matched misleading and correct suggestions, several prompt variants, deterministic answer extraction and initial-answer-conditioned metrics. The paper explicitly distinguishes the two populations underlying its correction-selectivity score and discloses missing correction observations and parser limitations. Thus correct-versus-incorrect feedback, condition-specific denominators and parser sensitivity are already recognized concerns. A smaller arithmetic version or merely replacing the parser would not establish a new contribution. The public artifacts offer a possible reproduction and sensitivity-analysis route, assessed [separately](PUBLIC_LOG_REANALYSIS_FEASIBILITY.md). [Official paper, §§3–5](https://aclanthology.org/2026.findings-acl.1759.pdf).

**Why LLMs Give In (Ping et al., arXiv v2, August 31, 2026).** Section 3.2 crosses user role, fabricated supporting sources, turn placement and answer grounding. Section 3.4 filters multi-turn trials by initial correctness and excludes unscorable responses. Therefore factorial conversational controls, grounding and conditional populations are not new simply because our domain is arithmetic. Their task uses medical claims and judged responses; it is not the same as checking arithmetic equalities. This difference alone does not demonstrate a research gap. Both v1 and the updated v2 methods were checked; v2 governs this comparison. Reasoning-trace associations were not independently validated. [Primary full text, §§3.2–3.6 and Appendix E](https://arxiv.org/html/2608.01017v2).

## Independent critique of our draft

These are our design judgments, not empirical findings:

1. Giving a worked solution ending in the answer permits copying; output correctness cannot establish reasoning verification.
2. A wrong proposal beside a correct solution creates contradictory cues. Correct-proposal and wrong-proposal cells are not interchangeable evidence conditions.
3. Certainty wording can also change length, insistence and perceived instruction strength. The identified intervention is the actual wording package.
4. Conditioning on initially correct problems supports a retention analysis; it supplies no correction-acceptance estimate if natural errors are absent.
5. Related numerical substitutions and repeated conditions are dependent. Family selection, problem-level pairing and missing-output treatment must be explicit.

The [revised draft](TASK_MATCHED_DESIGN_DRAFT.md) makes these limits explicit and separates intermediate-calculation information from final-answer disclosure. Its four arithmetic illustrations are mechanically checked, but human review remains pending. This improves a development instrument; it does not turn it into a novel study.

## Search and limits

Queries included `LLM sycophancy evidence confidence arithmetic correction factorial benchmark`, `sycophancy reasoning validity correct final answer false reasoning user correction benchmark`, and exact title searches. The official SycoBench paper, pinned author code, metric definitions and license were inspected. One author-released raw log was inspected structurally, without scoring it. An OpenReview result about mathematical yes-bias reached a browser-verification page; no methods claim is drawn from that inaccessible text. Several adjacent results were not fully reviewed and cannot be treated as excluded prior art.

**Decision:** do not claim originality for the generic evidence × confidence design. Advance the bounded public-log reproduction plan and human review. A later contribution requires a specific supported finding and comparison with prior measurement work; neither conference acceptance nor a novel gap is established.
