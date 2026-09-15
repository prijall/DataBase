# Research implications and reading order

[Research index](README.md) · [Detailed paper summaries](PAPER_SUMMARIES.md)

Status: proposed research direction, not a verified novelty claim or completed experiment.

## Main conclusion

Reducing sycophancy while preserving correct updates is an established research problem. A contribution needs to go beyond showing that anti-sycophancy can cause stubbornness. The supporting sources and their limitations are documented in the [paper summaries](PAPER_SUMMARIES.md).

## What is already covered

The reviewed literature studies user-pressure-induced errors, prompting and activation steering, the resistance/correction trade-off, conditional intervention, and behavioral subtypes. The closest overlap is the [supplementary small-model manuscript](https://github.com/and270/selective-sycophancy-steering).

A replication would be useful preparation and could reveal implementation issues. Reproducing the known trade-off alone is insufficient grounds for claiming a new contribution.

## Candidate extension: sensitivity to reasoning validity

> Do anti-sycophancy interventions preserve a model's ability to distinguish valid corrections from persuasive but invalid reasoning?

The aim is to test whether the model responds to reasoning quality, rather than merely agreement, confidence, or the proposed answer.

This remains a **candidate extension**. Citation tracing and a focused search on evidence-based correction, reasoning verification, and related evaluations are necessary before claiming a gap. Absence from this reading list is not evidence that no prior work exists.

### Proposed experimental factors

| Factor | Conditions |
| --- | --- |
| Proposed conclusion | Correct / incorrect |
| Supporting reasoning | Valid / contains a verified error |
| User presentation | Neutral / confident |

Construct only logically coherent combinations. A correct conclusion can follow from an invalid argument; a valid derivation from verified premises cannot establish a false conclusion. Do not assume a complete factorial design is possible under fixed, verified premises.

Use objectively checkable problems and independently verified derivations. A proposed correct answer without supporting reasoning tests suggestion acceptance, not reasoning verification.

### Evaluation principles

These are proposed design choices, not findings from a completed experiment:

1. Freeze genuine initial answers and eligible questions across intervention arms to isolate changes in correction behavior.
2. Keep naturally correct and naturally incorrect initial answers as separate cohorts; report their denominators.
3. Measure both correct-to-incorrect and incorrect-to-correct transitions.
4. Match substantive content while varying confidence or framing.
5. Separate correct conclusions from valid supporting arguments when scoring.
6. Include an unsteered baseline and a simple prompting baseline before more elaborate methods.
7. Choose steering settings on development data, then evaluate on held-out problem templates.
8. Record invalid outputs explicitly rather than silently dropping them.
9. Report uncertainty using the underlying problem as the sampling unit when multiple variants share a problem.
10. Measure task accuracy as well as intervention effects; unchanged response style or token probabilities do not establish preserved capability.

## Fit to the available research workflow

Planning constraints supplied by the researcher:

- 4–6 hours per week for reading, coding, reviewing results, and writing.
- At least nine total machine-hours per week available for permitted personal research.
- Experimental inference must run locally on shared office hardware.
- Available Macs described as an M1 with 8 GB RAM and an M4 with 16 GB RAM, plus external storage and Tailscale connectivity.

Hardware descriptions are planning inputs, not a fresh inventory or measured performance guarantee. Other connected devices should not count toward the experiment budget until access, resources, and availability are confirmed. Tailscale connectivity does not itself combine device memory.

Start with one small model and short, deterministic tasks. Measure actual throughput and memory use before fixing the experiment size. Begin with simple residual-stream steering; attention-head selection and learned gates add implementation and validation work.

Research agents can help organize sources, draft code, and critique analysis. Their generated claims and problem solutions still require checking. Agent orchestration is a research aid, not the subject of this proposed project.

The reviewed papers' GPU pipelines are not assumed to run unchanged within this Mac budget. A smaller pilot should establish feasibility before expanding models, intervention methods, or benchmarks.

## Reading priority

Read these first:

1. **CAA** — understand and implement the intervention.
2. **Stubborn or Sycophantic** — understand the evaluation trade-off.
3. **The supplementary small-model manuscript** — understand the closest overlap.
4. **SWAY** — learn matched experimental design.
5. **Cannot Self-Correct** — understand revision-evaluation pitfalls.

Then read **Towards Understanding Sycophancy** for motivation, **Dual-Stance** for appropriate-agreement controls, and the **attention-head**, **gated-steering**, and **representation** papers to assess whether methodological complexity is justified.

For each paper, record the hypothesis, models, prompts, split construction, intervention timing, outcome denominators, scoring method, strongest result, and what would falsify its interpretation.

## Next deliverables

1. A claim-by-claim overlap matrix, including additional papers found through citation tracing.
2. A small local pilot with verified valid/invalid reasoning and deterministic scoring.
3. A frozen evaluation protocol only after novelty checks and the feasibility pilot support proceeding.

Conference acceptance cannot be inferred from the topic alone. The eventual contribution must be supported by a precise claim, appropriate controls, reproducible evidence, and clear limits.
