# Working paper

[Read the manuscript](manuscript.md) · [Current research state](../RESEARCH_STATE.md) · [Evidence outline](../PAPER_OUTLINE.md)

## Stage

This is an evolving manuscript built alongside the experiments. As of September 21, 2026, it reports **232 archived calls**: 42 earlier diagnostics, 130 freeform-v3 calls, and sixty verification-only calls. The two v3 models failed their respective suitability gates. In verification-only evaluation, Llama returned VALID for all thirty traces; Qwen produced thirty length-stopped, unusable responses. Both failed the gate. Qwen's conditional verification accuracy is not estimable. No further inference is running for this experiment batch. The draft contains no completed intervention study or verified novelty claim and is not ready for conference submission.

The manuscript also records the [ProcessBench adaptation](../pilot/PROCESSBENCH_PLAN.md) and two blocked runtime preflights. The [September 21 M4 check](../pilot/results/2026-09-21-processbench-m4/README.md) stopped on memory guards after one non-generating debug load, with zero exact token checks or subject answers. Cleanup is verified. The session is closed and cannot resume; both cohorts remain unused. These operational findings add no model-accuracy results and do not establish general M4 infeasibility.

## Files

- [manuscript.md](manuscript.md): prose, methods, tables, interpretation, and limitations.
- [related_work.md](related_work.md): source-level comparison maintained with the literature review.
- [references.bib](references.bib): bibliographic records for checked primary sources.

## Update the paper with research progress

1. Archive completed, failed, or deliberately stopped runs with raw outputs, manifests, and session logs.
2. Verify analysis against those artifacts and record code/data versions. Keep frozen primary scores separate from post-hoc diagnostics.
3. Update Methods and Results from the verified archive, linking each table or empirical paragraph to its supporting report or raw records. Preserve denominators and missing/non-estimable outcomes.
4. Revise Discussion, Abstract, and the title to match the evidence. Label running work as pending; do not turn planned experiments into completed findings.
5. Update this status and [research state](../RESEARCH_STATE.md) in the same publication step. Commit the draft alongside the new evidence so its history remains traceable.

The existing [paper outline](../PAPER_OUTLINE.md) tracks outstanding methodological and novelty requirements. Failed screens remain part of the record. AI-generated literature notes and reviews require source verification; human authors remain responsible for the eventual paper.

## Evidence currently incorporated

| Evidence | Manuscript use |
| --- | --- |
| [42-call diagnostic report](../pilot/results/2026-09-15-protocol-screen/README.md) | Earlier protocol development and limitations |
| [Frozen v3 protocol](../pilot/PROTOCOL_V3.md) | Conditions, scoring, advance/stop rules |
| [Llama strict-score audit](../pilot/results/2026-09-15-freeform-v3/llama32/AUDIT.md) | Main descriptive results and failed parsing gate |
| [Llama presentation audit](../pilot/results/2026-09-15-freeform-v3/llama32/PRESENTATION_AUDIT.md) | Separately labeled post-hoc diagnostic |
| [Qwen initial-screen audit](../pilot/results/2026-09-15-freeform-v3/qwen3vl/AUDIT.md) and [presentation audit](../pilot/results/2026-09-15-freeform-v3/qwen3vl/PRESENTATION_AUDIT.md) | Failed initial gate; no follow-ups or presentation recoveries |
| [Verification-only protocol](../pilot/VERIFICATION_ONLY_PROTOCOL.md) and [sixty-call archive](../pilot/results/2026-09-16-verification-only/README.md) | Binary interface, primary/secondary comparisons, failed gates, and timing |
| [Llama binary summary](../pilot/results/2026-09-16-verification-only/llama32/SUMMARY.md) and [Qwen binary summary](../pilot/results/2026-09-16-verification-only/qwen3vl/SUMMARY.md) | Per-condition scores, unusable/truncated outputs, and paired outcomes |
| [Novelty audit](../NOVELTY_AUDIT.md) | Scope and overlap with prior work |
| [M4 preflight and cleanup](../pilot/results/2026-09-21-processbench-m4/README.md) | Section 4.7: resource stop, no subject outcomes, closed session |
