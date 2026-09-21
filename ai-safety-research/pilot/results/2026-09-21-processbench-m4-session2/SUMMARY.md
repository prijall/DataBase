# ProcessBench local adaptation

Primary extraction follows the published last-boxed-integer rule. Completion-gated local success additionally requires a normal server stop and an in-range prediction. These scores describe this small resource-adapted subset, not a published-score replication.

Stop/status: Resource stop: memory free percentage below 20.

| Cohort | Recorded / planned | Usable | Official exact matches / recorded | Local exact matches / planned | Length stops | Request errors |
| --- | --- | ---: | --- | --- | ---: | ---: |
| calibration | 2/20 | 1 | 1/2 | 1/20 | 1 | 0 |
| evaluation | 0/40 | 0 | 0/0 | 0/40 | 0 | 0 |

### Calibration class scores

| Class | Recorded / planned | Usable | Official matches / recorded | Local matches / planned | Conditional local accuracy |
| --- | --- | ---: | --- | --- | --- |
| valid | 0/10 | 0 | 0/0 | 0/10 | not estimable |
| error | 2/10 | 1 | 1/2 | 1/10 | 100.0% |

Observed-output official-compatible harmonic mean: not estimable. Partial/unused cohort; this is not a completed planned-cohort score.
Malformed extractions: 0; out-of-range indices: 1; missing calls: 18.


### Evaluation class scores

| Class | Recorded / planned | Usable | Official matches / recorded | Local matches / planned | Conditional local accuracy |
| --- | --- | ---: | --- | --- | --- |
| valid | 0/20 | 0 | 0/0 | 0/20 | not estimable |
| error | 0/20 | 0 | 0/0 | 0/20 | not estimable |

Observed-output official-compatible harmonic mean: not estimable. Partial/unused cohort; this is not a completed planned-cohort score.
Malformed extractions: 0; out-of-range indices: 0; missing calls: 40.

Calibration gate: **NOT PASSED**.

The harmonic mean combines error-free and erroneous-solution exact accuracies, not precision and recall. Our documented zero/zero convention is zero; an absent class is unavailable. Missing and failed calls remain unsuccessful against planned denominators for local feasibility. Raw streams are preserved; source prompts are reconstructed from pinned downloads and message hashes.
