# Independent check of the six-output review

September 21, 2026. **Post-hoc, independent AI-assisted check; human review remains pending.** This appendix checks [OUTPUT_REVIEW.md](OUTPUT_REVIEW.md) against the six archived [raw responses](responses.jsonl) and their corresponding pinned source records. It adds no benchmark labels, rescoring or experimental calls. The source file matches its recorded SHA-256 `fb1c59dfd1e83e1c5a48dbe598db27e4bc0b8bc524a09445f2d4b69178f61349`.

## Mathematical and descriptive checks

No material mathematical discrepancy was found in the existing review. The following independent calculations support its descriptions:

| Case | Check against the problem and supplied solution |
|---|---|
| `gsm8k-63` | Weekly cost is `25 + 6 + 16 = 47`; five weeks cost **235**. The first incorrect price appears in tagged paragraph 2, which charges 8 for the skirt. The model's unboxed `3` fails the frozen interface and zero-based label. With no explanation, a numbering mistake and a missed earliest error cannot be distinguished. |
| `gsm8k-147` | Jame is currently 22; in eight years he is 30, his cousin is `2×30−5 = 55`, and the cousin is currently 47. Their gap is **25**. The model correctly notices `2×22 = 44`, but its proposed `44−8 = 36` does not repair the age relationship. Its correct error index therefore coexists with an unreliable explanation. |
| `gsm8k-40` | `194×150 = 29,100` is correct; `194×490 = 95,060`, giving a difference of **65,960**. The source first errs in paragraph 1. The model selects 0 without supplying a reason. |
| `gsm8k-143` | The stated monthly group requirements imply `2×(200+400+100) = 1,400` bananas. Paragraph 1 changes a group requirement into a per-animal requirement and invents an animal count. The model selects the introductory paragraph 0 without explaining why. |
| `gsm8k-234` | Under the problem's stipulated relationship, `50 + (50/2 + 4) = 79`. The supplied arithmetic is consistent with that premise. This check does not substitute contemporary geography for the word problem or infer why the model selected 0. |
| `gsm8k-204` | Starting with 48 gives `48−14−7−9 = 18`, then `18/3−1 = 5`. The supplied solution is consistent. The model's proposed raccoon rewrite uses `x−21`, omitting the pigeons' nine fries; its unboxed index 7 does not identify a mathematical error in the supplied equation. |

The distinction between format and task failure is supported: three responses contain a validly formatted but incorrect index, while two lack a boxed integer. The two unboxed visible indices also disagree with the gold labels; merely adding boxes would not rescue these records. That hypothetical observation is **not a new score or parser rule**. The single correct extracted index does not certify every statement in its accompanying critique. The text does not reveal hidden reasoning or establish a causal failure mechanism.

## What the admission thresholds mean

The [original plan](../../PROCESSBENCH_PLAN.md) specified all twenty records, at least **18/20 usable outputs**, and at least **8/10 completion-gated exact matches in each class**. These thresholds appear unchanged in September 16 commit `48b4647`, the first M4 execution freeze `017f1d7`, and this run's freeze `5d73d85`. The plan explicitly calls them pragmatic engineering thresholds, not a statistical power calculation or evidence of general competence.

They are researcher-selected requirements for admitting a candidate verifier to the next stage, not official ProcessBench thresholds, a significance test, or proof that population accuracy exceeds 80%. Their suitability for a future intervention study would require a separately justified design and uncertainty analysis. They must not be lowered after viewing these outputs. Here, the erroneous class has one match in four attempts, so its best possible final result is `1+6 = 7/10`; the existing gate cannot pass. The recorded stop reason nevertheless remains memory pressure, and the cohort remains incomplete.

## Three questions for the researcher's own review

1. **Case 63:** mark the first incorrect price in the tagged source. Does the model's bare `3` explain whether it meant paragraph 3 or the third paragraph? Record what is observed and what remains ambiguous, without guessing an intended label.
2. **Case 147:** independently derive the present ages and gap. Which statements in the model's critique are correct, and which remain wrong despite its correct final index? In your intended research, would an index-only success measure everything you care about?
3. **Case 204:** track the fries through every animal. Is there any mathematical error at source paragraph 7, and where does the model's proposed rewrite lose nine fries? Separate suggestions about writing from actual errors in the solution.

Record any disagreements with this appendix separately, with the supporting paragraph and calculation. Keep the frozen gold labels, raw outputs, parser and primary scores unchanged. These are now development cases; this check provides no authorization to generate or inspect evaluation answers.
