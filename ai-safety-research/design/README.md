# Four task-matched development illustrations

This directory makes the **four existing illustrations** in the [design draft](../TASK_MATCHED_DESIGN_DRAFT.md) executable and reviewable. It is not a new benchmark, a dataset generator, a model runner, or authorization to run experiments. All four examples are already exposed; human review is pending. Full two-step equalities are ground-truth audit material, not the six-cell follow-up prompts in the revised draft. The draft supplies only the first equality in its intermediate condition and a separate final-answer control; no prompt runner is implemented here.

- [illustrations.json](illustrations.json): ordered operation specifications, expected intermediate values, final truth, true/false proposals, and structured evidence equalities.
- [check_illustrations.py](check_illustrations.py): standard-library exact arithmetic validation.
- [checked/REVIEW.md](checked/REVIEW.md): generated manual-review sheet.
- [checked/audit.json](checked/audit.json): deterministic audit with input, checker and source-draft hashes.

## Use on the controller

From the repository root:

```sh
python3 -B ai-safety-research/design/check_illustrations.py
python3 -B ai-safety-research/design/check_illustrations.py --format markdown
python3 -B ai-safety-research/design/check_illustrations.py --out ai-safety-research/design/checked
python3 -B -m unittest discover -s ai-safety-research/design -v
```

Without `--out`, the checker writes only to stdout. An explicit output directory receives `audit.json` and `REVIEW.md`; rerunning regenerates those local review artifacts. No network, model, SSH, or external Python packages are used.

## What is checked

Starting from an integer, operations execute sequentially using `Fraction`: `add`, `subtract`, `multiply`, or `exact_divide`. Every intermediate must remain an integer. Each stored intermediate, final truth, and correct proposal must match the computed values; the false proposal must differ. Each evidence equality must be arithmetically true **and** use the operands and operation from the corresponding sequential step.

The schema rejects missing/unknown fields, unknown operations, Boolean/noninteger numeric values, zero or nonexact division, duplicate JSON keys or IDs, and wrong illustration/step counts. No expression strings are executed. A small operation interpreter avoids importing the earlier pilot's model/network runner or duplicating its expression parser; frozen pilot files remain untouched.

## What still needs human review

The checker does not interpret the natural-language questions, establish that certainty wording is controlled, or validate an experimental design. A person must compare the question with its formal order and review distractors, answer-revealing evidence, the false-proposal/evidence conflict, and the [design draft's](../TASK_MATCHED_DESIGN_DRAFT.md) outstanding methodological choices. Passing arithmetic checks is not a human approval or capability result. Record any human review separately; do not mark it complete based on this audit.
