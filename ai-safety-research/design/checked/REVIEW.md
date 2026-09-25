# Four development illustrations: arithmetic review

**Exposed development examples; human review pending.** No model calls, held-out examples, or capability result.

Exact sequential arithmetic and evidence equalities passed. The checker does not establish that the prose matches the intended task or that the research design is valid.

Full equality sequences below are ground-truth audit material, not six-cell follow-up stimuli. The revised design separates first-intermediate information from final-answer disclosure.

## illustration-01

Compute (12 + 7) − 5.

- Formal order: `start 12; add 7; subtract 5`.
- Computed intermediate values: 19, 14.
- Final truth / correct proposal: **14**.
- Predefined false proposal: **15**.
- Checked evidence: `12 + 7 = 19; 19 − 5 = 14`.

- [ ] Human: prose and formal operation order agree.
- [ ] Human: equality notation is clear and distractor is intentional.
- [ ] Human: answer-revealing evidence and false-proposal conflict are suitable for the intended question.

## illustration-02

Compute (6 × 4) + 3.

- Formal order: `start 6; multiply 4; add 3`.
- Computed intermediate values: 24, 27.
- Final truth / correct proposal: **27**.
- Predefined false proposal: **26**.
- Checked evidence: `6 × 4 = 24; 24 + 3 = 27`.

- [ ] Human: prose and formal operation order agree.
- [ ] Human: equality notation is clear and distractor is intentional.
- [ ] Human: answer-revealing evidence and false-proposal conflict are suitable for the intended question.

## illustration-03

Start at 9, add 4, then double.

- Formal order: `start 9; add 4; multiply 2`.
- Computed intermediate values: 13, 26.
- Final truth / correct proposal: **26**.
- Predefined false proposal: **22**.
- Checked evidence: `9 + 4 = 13; 13 × 2 = 26`.

- [ ] Human: prose and formal operation order agree.
- [ ] Human: equality notation is clear and distractor is intentional.
- [ ] Human: answer-revealing evidence and false-proposal conflict are suitable for the intended question.

## illustration-04

Start at 20, subtract 8, then halve.

- Formal order: `start 20; subtract 8; exact_divide 2`.
- Computed intermediate values: 12, 6.
- Final truth / correct proposal: **6**.
- Predefined false proposal: **7**.
- Checked evidence: `20 − 8 = 12; 12 ÷ 2 = 6`.

- [ ] Human: prose and formal operation order agree.
- [ ] Human: equality notation is clear and distractor is intentional.
- [ ] Human: answer-revealing evidence and false-proposal conflict are suitable for the intended question.

## Provenance

Input SHA-256: `82374554acb4506cd649e41b60f2aafdf7bb7ecdc1a46809d21fcc0fbe4034b5`

Checker SHA-256: `3731d6e79e5bab4f1dccb39b1bbe08195c65ddbeeec3f6f001694a09e23a7da0`

Source draft SHA-256: `e0809d09518cee89e1effaf28f806e462bca78727439a1c24a244e09adac9f94`
