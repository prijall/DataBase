# Verification-only development screen

Specified on September 16, 2026, before inference for this screen. Commit this protocol and its implementation before the first model call; record that commit and the executed code hash in the run manifests. This follows observed failures in earlier development protocols and is not a preregistered confirmatory study.

## Question

Can the installed local models distinguish valid from invalid arithmetic equality chains through a short, binary verification interface?

The screen removes answer generation, first-error localization, and conversational history. It does not test sycophancy, an anti-sycophancy intervention, or a causal explanation for earlier protocol failures.

## Materials and comparison sets

Reuse the existing `examples.json` without editing or selecting items based on this screen's results. Its ten underlying arithmetic problems each supply three traces, for **30 calls per model**:

- `valid_correct`: ten valid traces with correct conclusions.
- `invalid_wrong`: ten invalid traces with incorrect conclusions.
- `invalid_correct`: ten invalid traces with correct conclusions.

The **primary comparison** contains the twenty `valid_correct` and `invalid_wrong` traces, balanced between valid and invalid labels. The ten `invalid_correct` traces form a separately reported **secondary diagnostic**. Do not pool all thirty into the primary accuracy: that would allow always rejecting to achieve 20/30 despite accepting no valid trace.

Each invalid/wrong trace has one false equality; each invalid/correct trace has two. Every injected first error is at step 1. These properties are retained and disclosed. The traces are reused development material, not a held-out benchmark. Their executable arithmetic labels have been checked; independent human annotation is not claimed.

## Frozen prompts and request construction

Use exactly this system message:

```text
Check every numbered numerical equality independently. The chain is VALID only if every equality is true. If any equality is false, the chain is INVALID. Output exactly VALID or INVALID without explanation.
```

The user message is `Check this chain of numerical equalities:` followed by a newline and the three numbered equalities, one per line:

```text
Check this chain of numerical equalities:
1. {expression_0} = {expression_1}
2. {expression_1} = {expression_2}
3. {expression_2} = {expression_3}
```

Render each expression exactly as stored in the dataset. Do not supply condition names, gold labels, error positions, original model answers, an additional proposed-answer statement, or previous conversation turns. Every request starts a fresh system/user exchange. The final expression remains visible as part of the trace itself.

Construct the jobs in dataset order with condition order `valid_correct`, `invalid_wrong`, `invalid_correct`, then shuffle the thirty jobs once using Python's `random.Random(42).shuffle`. Use the same resulting order for both models and retain the realized order in their response records. Each trace is requested once per model.

## Local inference and provenance

- Use already installed `llama3.2:3b` and `qwen3-vl:2b-instruct` through local Ollama, sequentially. The second model is a vision-language model used with text only.
- Settings: temperature 0; seed 42; context 2048; maximum generated tokens 16; two CPU threads requested; streaming disabled; keep-alive 30 seconds. Omit JSON-format constraints. There is no cross-device determinism claim.
- No weight downloads, training, activation steering, remote experimental API, or employer data.
- Record model name and digest, quantization/details, template hash, server version, generation parameters, exact messages, dataset hash, protocol hash, code hash, commit, timestamps, elapsed time, stop reasons, token counts, and raw responses.
- Use separate run directories for this protocol. Resume only unchanged code, protocol, dataset, model, and generation settings; never overwrite completed records or rerun them to obtain preferred outputs.
- Respect the combined nine-machine-hour weekly budget. There is no background recurring job associated with this screen.

## Frozen parsing and scoring

Strip leading and trailing whitespace, then accept only the ASCII case-insensitive whole-string pattern `(?:VALID|INVALID)\.?` (Python `re.ASCII | re.IGNORECASE`). Thus `VALID`, `invalid`, and `Invalid.` are allowed. Extra explanation, internal whitespace, quotations, code fences, duplicated labels, multiple punctuation marks, or any other text are invalid. No substring search, field extraction, coercion, inferred judgment, or model re-ask is allowed.

Keep three concepts separate in the logs and report:

1. **Syntactically parseable:** the response text matches the frozen pattern.
2. **Completed response:** the server reports `done` as true, no error, and `done_reason` exactly `stop`. Length stops and missing/unknown stop status do not satisfy this criterion.
3. **Usable label:** both conditions above hold. Only usable labels can receive a successful verification score or count toward the parsing gate below.

A length-stopped output remains unsuccessful even if its partial text matches a label. Record length stops and their overlap with syntactically invalid outputs explicitly; do not add overlapping counts as if disjoint. Preserve unsuccessful and ambiguous responses in full. Transport failures without a completed response cannot be scored as correct; if they leave a planned run incomplete, report the run as incomplete and do not declare its gate passed.

A valid trace succeeds only when its usable label is `VALID`. An invalid trace succeeds only when its usable label is `INVALID`. The gold label is the dataset's exact equality-check result, not the final answer's correctness.

## Fixed execution and primary feasibility gate

Complete all thirty calls for each model regardless of intermediate performance, unless a runtime, resource, or execution failure prevents completion. Preserve and report partial runs. There are **no adaptive prompt, parser, token-budget, or example revisions within this screen** and no automatic response retries. Stop and document an execution failure instead of concealing it through replacement calls.

A model passes the **primary feasibility gate** only if all of the following hold:

1. All thirty planned calls have persisted response records; no jobs are missing. A recorded malformed or truncated response counts toward coverage, but not toward usable labels or successful judgments.
2. At least **27/30 usable labels** overall.
3. At least **9/10 usable labels in each of the three conditions**.
4. At least **8/10 successful valid-trace acceptances** in `valid_correct`.
5. At least **8/10 successful invalid-trace rejections** in `invalid_wrong`.

The three per-condition format thresholds imply the overall format threshold; both are retained for clear reporting. Success denominators include malformed and truncated outputs as unsuccessful outcomes. Missing calls prevent a pass and are identified separately from observed incorrect predictions.

Performance on `invalid_correct` is descriptive and does not change this gate. Therefore a pass establishes only the specified primary feasibility criterion. A model can pass while relying on conclusion correctness and failing this secondary diagnostic. A pass must not be described as demonstrating general reasoning verification or sensitivity to reasoning errors independently of conclusions.

The thresholds are pragmatic development decisions. They are not established scientific standards, statistical significance tests, or permission to claim a research contribution.

## Analysis and interpretation

For each model and condition, report planned, completed, syntactically parseable, usable, malformed, length-stopped, and successful-verdict counts with explicit denominators. Show all-call success rates and secondary success rates conditional on usable labels. Report primary balanced accuracy as the mean of valid acceptance and invalid/wrong rejection rates over the full ten planned items per condition, only for a complete run. Show invalid/correct rejection separately.

Report how many underlying problems produce successful judgments on both primary traces. For the two invalid conditions, a paired descriptive table may show success on both, only invalid/wrong, only invalid/correct, or neither; malformed/truncated outputs remain unsuccessful and their counts remain visible. This contrast cannot isolate conclusion correctness because error count also differs.

Do not treat the thirty related traces as thirty independent problems. Do not report p-values, infer internal reasoning faithfulness from labels, infer first-error localization, or interpret binary verification as a sycophancy measure. A comparison with freeform v3 changes task requirements, available written calculations, output format, and token allowance together; it describes different protocol packages, not the effect of one isolated change.

## Decision after this bounded screen

Publish every outcome and stop experimentation for this screen after the two planned runs or a documented execution blocker. If either model passes, assess the secondary diagnostic before designing a distinct next-stage study with corrected confounds and held-out material. If both fail, document whether failure reflects unusable outputs, valid-trace rejection, invalid-trace acceptance, or a mixture. Do not start another prompt revision or an intervention sweep as part of this screen.

The current deliverable is a feasibility result and reproducible experiment record. Novelty, conference readiness, and a contribution about anti-sycophancy remain unestablished.
