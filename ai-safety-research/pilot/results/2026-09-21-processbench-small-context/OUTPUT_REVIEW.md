# Post-hoc review of six calibration outputs

September 21, 2026. **Qualitative, AI-assisted review after observing the outputs; not independently validated annotations or new benchmark labels.** Only the six attempted IDs were inspected against their corresponding problems and provided solutions. This review does not change extraction, gold labels, scores or stopping rules, and does not salvage answers from prose.

## Recorded outcomes

All six responses ended normally. Four contained an extractable in-range index; one matched the published earliest-error label. Two lacked a boxed integer. These are counts for a stopped calibration prefix, not a completed cohort or evidence of general model accuracy. In particular, the two missing extractions were **not generation-length stops**.

The actual runtime stop was a resource stop. Independently, the frozen adequacy gate had already become unattainable: the erroneous-solution class had **1 correct among 4 attempted**, with only 6 cases remaining. Even six further successes would yield **7/10**, below the required 8/10. Finishing the remaining cases cannot rescue admission without forbidden retries, substitutions or changed thresholds.

| Example | Frozen gold → extracted index | Visible behavior and limited interpretation |
| --- | --- | --- |
| `gsm8k-63` | `2 → missing` | Reproduces the supplied solution and ends with unboxed index `3`. The supplied solution first swaps a clothing price in paragraph 2. The answer gives no explanation for choosing 3, so a missed earliest error and an indexing mistake cannot be distinguished from the text alone. Adding a box around the visible numeral would still not match the frozen zero-based gold label. |
| `gsm8k-147` | `1 → 1` | Correct index, with a valid local observation that twice 22 is 44, not 46. However, the suggested correction retains the solution's wrong age setup, accepts a later age-difference calculation without repairing its inputs, and criticizes a concluding answer statement on presentation grounds. Exact-index success here does not validate the entire critique. |
| `gsm8k-40` | `1 → 0` | Reproduces the solution and selects paragraph 0 without an explanatory critique. Paragraph 0's multiplication, 194 × 150 = 29,100, is correct; the next paragraph miscalculates 194 × 490, which equals 95,060. This is an incorrect earlier-error selection with a usable format. Its cause is not established. |
| `gsm8k-143` | `1 → 0` | Reproduces the solution and selects its introductory paragraph without explaining why. The next paragraph introduces unsupported animal counts and changes the quantities described in the problem. The observed output does not demonstrate that it checked those assumptions. |
| `gsm8k-234` | `-1 → 0` | Rejects paragraph 0 without explanation although the benchmark marks this solution error-free. The arithmetic follows the problem's stipulated relationship. This is a false rejection under the frozen task; the response supplies no reasoning that would justify another interpretation or a changed gold label. |
| `gsm8k-204` | `-1 → missing` | Gives extensive editorial suggestions while repeatedly calling the calculations correct, then names unboxed index `7`. One suggested rewrite also loses the nine fries eaten by the pigeons, using `x − 21` where the provided solution uses `x − 30`. The source solution is gold-labeled error-free. This combines missing required output, an unsupported error claim and an incorrect proposed correction; it is not merely a missing-box issue. |

## What the text supports

The visible failures span both the output interface and the underlying judgment. Two answers omit the box, while three other answers give validly formatted but incorrect indices. Five responses largely reproduce the supplied solution before judging it; reproduction alone is not evidence of verification. The sixth emphasizes prose quality and introduces a mathematical mistake in a proposed rewrite. Conversely, the one correct index includes a genuine local arithmetic observation alongside unreliable additional criticism.

These descriptions are not a validated taxonomy, evidence of hidden reasoning, or a causal explanation for failure. The six selected-prefix cases are too few and unbalanced to support model-wide conclusions. They also do not establish that reducing context helped or harmed reasoning: the earlier configuration used different calibration cases. All six attempted cases are now development evidence and must never be presented as held-out tests in subsequent work.

## Next scientific decision

Stop automatic prompt/context revisions on these examples. Resolving a runtime or cache issue would not reopen this cohort's already-unattainable adequacy gate. Have the researcher manually review this six-case table against the problems, source steps and raw outputs, especially the difference between identifying the earliest mathematical error and offering writing advice. Record any disagreements with this qualitative review separately; retain the original benchmark scores.

Before designing conversational pressure or an alignment intervention, decide whether an independently adequate local verifier can provide the required baseline measurement. That decision needs a separately justified model/interface and fresh calibration reservation, followed by the existing resource and adequacy gates; it is not an instruction to run another experiment now. If that baseline cannot be established within the available hardware/time, reconsider the research question rather than interpreting these errors as an alignment effect. Leave the unused evaluation reservation untouched.

Evidence: [archived raw responses](responses.jsonl) (controller originals: `subject-run/responses.jsonl`) and pinned ProcessBench `gsm8k.json`, joined only on the six attempted IDs. Raw response scores remain the authoritative quantitative record; this file adds an explicitly post-hoc reading of their visible content.
