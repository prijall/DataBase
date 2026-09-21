# ProcessBench local adaptation

Primary extraction follows the published last-boxed-integer rule. Completion-gated local success additionally requires a normal server stop and an in-range prediction. These scores describe this small resource-adapted subset, not a published-score replication.

Stop/status: Resource stop: memory pressure is not normal.

| Cohort | Recorded / planned | Usable | Official exact matches / recorded | Local exact matches / planned | Length stops | Request errors |
| --- | --- | ---: | --- | --- | ---: | ---: |
| calibration | 6/20 | 4 | 1/6 | 1/20 | 0 | 0 |
| evaluation | 0/40 | 0 | 0/0 | 0/40 | 0 | 0 |

### Calibration class scores

| Class | Recorded / planned | Usable | Official matches / recorded | Local matches / planned | Conditional local accuracy |
| --- | --- | ---: | --- | --- | --- |
| valid | 2/10 | 1 | 0/2 | 0/10 | 0.0% |
| error | 4/10 | 3 | 1/4 | 1/10 | 33.3% |

Observed-output official-compatible harmonic mean: 0.00%. Partial/unused cohort; this is not a completed planned-cohort score.
Malformed extractions: 2; out-of-range indices: 0; missing calls: 14.


### Evaluation class scores

| Class | Recorded / planned | Usable | Official matches / recorded | Local matches / planned | Conditional local accuracy |
| --- | --- | ---: | --- | --- | --- |
| valid | 0/20 | 0 | 0/0 | 0/20 | not estimable |
| error | 0/20 | 0 | 0/0 | 0/20 | not estimable |

Observed-output official-compatible harmonic mean: not estimable. Partial/unused cohort; this is not a completed planned-cohort score.
Malformed extractions: 0; out-of-range indices: 0; missing calls: 40.

Calibration gate: **NOT PASSED**.

The harmonic mean combines error-free and erroneous-solution exact accuracies, not precision and recall. Our documented zero/zero convention is zero; an absent class is unavailable. Missing and failed calls remain unsuccessful against planned denominators for local feasibility. Raw streams are preserved; source prompts are reconstructed from pinned downloads and message hashes.
