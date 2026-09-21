# Working paper

[Read the manuscript](manuscript.md) · [Current research state](../RESEARCH_STATE.md) · [Evidence outline](../PAPER_OUTLINE.md)

## Stage

This is an evolving manuscript built alongside the experiments. As of September 21, 2026, it reports **240 archived generated completions**: 232 calls from completed diagnostic/development screens, two original-context calibration responses, and six smaller-context calibration responses. The two v3 models failed their respective suitability gates. In verification-only evaluation, Llama returned VALID for all thirty traces; Qwen produced thirty length-stopped, unusable responses. Both failed the gate. Qwen's conditional verification accuracy is not estimable. No further inference is running for this experiment batch. The draft contains no completed intervention study or verified novelty claim and is not ready for conference submission.

The manuscript also records the [latest smaller-context session](../pilot/results/2026-09-21-processbench-small-context/README.md): passed exact-token preflight, six of twenty calibration responses, four usable outputs, one correct index, and a memory-pressure stop. Two extractions were malformed; no response reached the output cap or had a request error. Calibration remains incomplete and the forty evaluation cases are untouched. Cleanup is verified. No automatic retry or configuration revision follows from this result; runtime investigation and human output review are the next tasks.

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
| [Second M4 session](../pilot/results/2026-09-21-processbench-m4-session2/README.md) | Section 4.8: passed token preflight, two observed calibration responses, resource stop |
| [Smaller-context M4 session](../pilot/results/2026-09-21-processbench-small-context/README.md) | Section 4.9: six partial calibration responses and memory-pressure stop |

The subsequent [cache-disabled runtime diagnostic](../pilot/results/2026-09-21-runtime-cache-diagnostic/README.md) generated zero answers and is reported separately in Section 4.10. The draft total remains 240. Normal office workload is a firm constraint, and the next work is offline task design and human review.
