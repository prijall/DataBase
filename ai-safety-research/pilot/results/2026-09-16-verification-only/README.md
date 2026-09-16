# Verification-only feasibility results

**Decision: both models failed the frozen primary feasibility gate.** All sixty planned local calls were recorded. Stop this screen; neither result justifies advancing to an anti-sycophancy intervention study.

The [protocol](../../VERIFICATION_ONLY_PROTOCOL.md), [runner](../../verification_only.py), tests and manuscript Methods were committed before inference at `9b5d5734f7ec79c87f68b3313d1186c7534139a7`. There were no outcome-based prompt, parser, token-budget or example revisions, and no replacement calls. This is adaptive development following earlier failures, not a confirmatory preregistration.

## Design

Each installed model reviewed the same thirty existing numerical traces once, in the same fixed shuffled order. The request asked only for `VALID` or `INVALID`, without explanation. Answer generation, error localization and conversational history were removed. The frozen parser accepts the whole label case-insensitively, optional final period and surrounding whitespace; successful scoring also requires a normal server stop.

The primary set contains ten valid/correct and ten invalid/wrong traces. Ten invalid/correct traces form a separate diagnostic. Temperature was zero, seed 42, context 2048, output allowance sixteen tokens, two CPU threads requested, and JSON-format constraints omitted. Models ran sequentially through local Ollama. The protocol changes several factors together relative to v3; it does not isolate a causal explanation for different behavior.

## Outcomes

| Measure | Llama 3.2 3B | Qwen3-VL 2B Instruct, text only |
| --- | ---: | ---: |
| Recorded calls | 30/30 | 30/30 |
| Lexically valid labels | 30/30 | 0/30 |
| Usable labels | 30/30 | 0/30 |
| Valid/correct traces accepted, all calls | 10/10 | 0/10 |
| Invalid/wrong traces rejected, all calls | 0/10 | 0/10 |
| Invalid/correct traces rejected, all calls | 0/10 | 0/10 |
| Primary balanced successful-verdict score | 50% | 0% |
| Length stops | 0/30 | 30/30 |
| Primary gate | Fail | Fail |

All-call scores include unusable outputs as unsuccessful. Qwen's zero successful-verdict score is **not an estimate of completed classification accuracy**: usable-conditional accuracy is not estimable. This table does not establish a model-capability ranking.

### Llama: usable constant-label outputs

Every raw response is `VALID`. Llama accepts all valid traces but misses every injected error in both invalid conditions. Its 50% primary balanced accuracy reflects an always-accept output pattern on this set; it does not establish random guessing or general inability to verify arithmetic. For each of the ten underlying problems, only the valid member of the primary pair succeeds. Neither invalid variant succeeds on any problem.

### Qwen: output-contract failures and truncation

Every response has `done_reason=length` at sixteen generated tokens and fails the whole-label parser. Raw responses contain extra text: the first begins with `INVALID` and then starts an explanation. The frozen rule does not extract or credit that prefix. All thirty calls remain recorded, and none produces a usable completed judgment. No missing stop statuses or server-error flags were observed.

These observations combine instruction/format noncompliance with the short generation allowance. They cannot distinguish all underlying causes or establish zero verification ability. Extending an already observed prefix containing extra prose would not itself make that whole response a single valid label; a larger budget is not a demonstrated remedy.

## Integrity, resources and artifacts

An independent AI reviewer reproduced all sixty scores, checked every prompt against its assigned trace and exact gold label, verified randomized order and model identities, and matched code/dependency/protocol/data/system hashes to the frozen commit. Every prompt is unique within its run. Independent AI review is not an independent human example audit.

The integrated suite passed **48 tests**, including sixteen verification-only tests covering truncation, partial runs, class-specific gates, paired denominators, raw-response integrity and resume protection. [Analysis provenance](ANALYSIS_MANIFEST.json) and [artifact checksums](SHA256.json) make the archived evidence auditable.

Recorded client execution was **52.079 seconds**: Llama 15.856 seconds and Qwen 36.223 seconds. This excludes development, idle gaps and model residency. The work used the existing shared M1 setup and installed models; no downloads, remote experimental inference or additional devices were used. The repository now contains **232 recorded experimental/diagnostic completions**, including the preceding 172 calls.

- Llama: [raw responses](llama32/responses.jsonl), [manifest](llama32/manifest.json), [summary](llama32/SUMMARY.md), [session log](llama32/sessions.jsonl).
- Qwen: [raw responses](qwen3vl/responses.jsonl), [manifest](qwen3vl/manifest.json), [summary](qwen3vl/SUMMARY.md), [session log](qwen3vl/sessions.jsonl).
- [Working manuscript](../../../paper/manuscript.md) incorporates these findings alongside the [earlier v3 results](../2026-09-15-freeform-v3/README.md).

## Limitations and next decision

There are ten reused underlying problems, not thirty independent observations per model. Error positions are fixed; invalid/correct traces contain two false equalities versus one in invalid/wrong traces. There are no held-out data, label-mapping controls, repeated-call stability tests or causal isolation of individual protocol changes. Neither sycophancy, activation steering nor internal reasoning faithfulness is measured.

Stop inference for this screen. The next deliverable is an **offline measurement-validation plan**: inspect these failures, select a published verification interface and its documented scorer for a bounded baseline replication, and specify separate calibration material, generation settings and stop rules before new inference. Resume the conversational research question only once valid acceptance and invalid rejection are both reliable enough for the intended measurement. The paper records these development outcomes; novelty and conference readiness remain open.
