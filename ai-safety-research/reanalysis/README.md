# Public-log reproduction

Reconstruct the published SycoBench-600 camera-ready table using a local, standard-library CPU analysis. This is a reproduction of released outputs, not new model inference.

**Latest work:** [descriptive Stage 2 audit](results/2026-09-21-suggestion-match-audit/README.md) complete. Start the [human-review guide](HUMAN_REVIEW_GUIDE.md) and [23-case packet](results/2026-09-21-suggestion-match-audit/review_packet.md) before reading its counts/key. [Stage 1 reproduction](results/2026-09-21-sycobench-reproduction/README.md) remains unchanged: all 133 numeric values matched. The [literature audit](STAGE2_LITERATURE_AUDIT.md) finds direct prior work; novelty remains unestablished.

- [Frozen acceptance protocol](REPRODUCTION_PROTOCOL.md)
- [Source and measurement audit](SOURCE_METHODS_AUDIT.md)
- [Pinned release tree](../public-data/sycobench-v1.0.0-tree.json)
- [Earlier feasibility inspection](../PUBLIC_LOG_REANALYSIS_FEASIBILITY.md)

The runner reads an ignored controller cache and verifies inputs against the pinned Git tree. No upstream inference client is executed. The original parser, stored scores, common question population and paper-specific bootstrap are preserved. Alternative scoring and clustering require a separate analysis plan.

## Run locally

From the repository root, first populate an ignored cache with the pinned release files listed in the result provenance. Preserve their repository-relative paths. For each Git blob, `gh api repos/debu-sinha/sycobench-600/git/blobs/BLOB_SHA -H 'Accept: application/vnd.github.raw+json'` returns the original bytes; the adapter independently verifies byte size and Git identity before analysis. No weights or model API are needed.

```sh
python3 -B -m unittest discover -s ai-safety-research/reanalysis -p 'test_*.py' -v
python3 -B ai-safety-research/reanalysis/reproduce.py \
  --cache ai-safety-research/pilot/runs/sycobench-release-inspection \
  --tree ai-safety-research/public-data/sycobench-v1.0.0-tree.json \
  --protocol ai-safety-research/reanalysis/REPRODUCTION_PROTOCOL.md \
  --out ai-safety-research/pilot/runs/sycobench-reproduction-check
```

Use a fresh output directory: existing results are never overwritten. The archived run uses an external 600-second subprocess timeout; apply the same bound when rerunning. `main_results.csv` and `comparison.json` hold numeric reproduction, `validation.json` holds integrity checks, `analysis.json` records population/denominators, `provenance.json` binds inputs and implementation, and `runtime.json` separately records measured resource use. `status.json` distinguishes numerical agreement from audit acceptance.

## Run the bounded Stage 2 diagnostic

The [Stage 2 protocol](STAGE2_PROTOCOL.md) fixes descriptive counts and a maximum 28-case human-review sample; it changes no parser or original score. Code/test/protocol bytes must match HEAD, and the imported Stage 1 adapter and archive must match their pinned hashes.

```sh
python3 -B ai-safety-research/reanalysis/decompose.py \
  --cache ai-safety-research/pilot/runs/sycobench-release-inspection \
  --tree ai-safety-research/public-data/sycobench-v1.0.0-tree.json \
  --stage1 ai-safety-research/reanalysis/results/2026-09-21-sycobench-reproduction \
  --protocol ai-safety-research/reanalysis/STAGE2_PROTOCOL.md \
  --out ai-safety-research/pilot/runs/suggestion-match-check
```

Use a fresh output directory and the same external 600-second bound as the archived run. Human labels are separate work: preserve the generated blank form and fill a copy after reading the rubric. `review_key.json` contains labels and identities that should remain unseen until the first pass is saved.

## Attribution

Source: Debu Sinha, *SycoBench-600*, [Findings of ACL 2026](https://aclanthology.org/2026.findings-acl.1759/), [release v1.0.0](https://github.com/debu-sinha/sycobench-600/releases/tag/v1.0.0), commit `5193ce408bd73b401c4c5911f490e2bbad84a082`. The author's code is MIT licensed ([retained notice](UPSTREAM_LICENSE.txt)); dataset, logs and generated tables are [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Our derived tables retain this attribution and license notice. Changes consist of an independent standard-library reproduction and added provenance/consistency audits; the author does not endorse this analysis.

Full raw logs remain in ignored storage. Selected attributed response excerpts appear in the human-review packet; derived reports and manifests are versioned for review from GitHub. Our historical total of 240 generated completions is separate and unchanged.
