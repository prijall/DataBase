# Smaller-context implementation

This guide describes the separate `small-context-v1` execution profile. Its [prospective protocol](PROCESSBENCH_SMALL_CONTEXT_PLAN.md) specifies a 2,048-token context with the existing 1,024-token output allowance. The original 8,192-token profile remains available as `original` for reproducibility. Earlier closed sessions must not be resumed.

## Selection and evidence

The [new selection](processbench/selection-small-context.json) reserves twenty fresh calibration cases, ten per process-label class. Selection excludes every normalized problem group in the original sixty-case reservation, including unselected solutions in those groups. It retains the original deterministic hash ordering without consulting model responses or screening by prompt length.

The original forty evaluation cases are carried over unchanged. The two previously observed calibration responses remain separate development evidence. Comparing the new calibration with those two responses cannot identify a causal effect of context size.

Both the controller and the in-memory remote worker enforce the selected profile. Reports and manifests bind the profile, configuration, selection and implementation identities. The smaller profile requires an actual loaded context of 2,048 tokens. Passing an earlier report, changing a selection, or changing profiles cannot authorize resuming an old run.

## Before a live run

The new configuration has not yet been tested on the M4. The previous sixty prompts measured 308–778 tokens, but those counts do not certify the new calibration cases. A fresh preflight must verify every full prompt with `prompt_tokens + 1024 <= 2048`, without truncation, filtering or substitution. It must also pass the original memory and swap limits.

Use the pinned input downloads from the [original plan](PROCESSBENCH_PLAN.md). All files in the commands below are on the controller. The [service wrapper](processbench_server_session.py) sends its program through SSH and does not create a research directory on the M4.

Choose a previously unused session directory and record its start and remaining weekly budget. The commands below use `runs/m4-small-context-001` as an example for that new session.

In a controller terminal, keep the service wrapper attached:

```sh
mkdir -p runs/m4-small-context-001
python3 -B processbench_server_session.py --log runs/m4-small-context-001/server-session.log
```

In another controller terminal, from this pilot directory:

```sh
python3 -B processbench_remote.py create-preflight --profile small-context-v1 --data runs/processbench-source/gsm8k.json --prompt runs/processbench-source/critique_template.txt --provenance processbench/provenance.json --selection processbench/selection-small-context.json --preflight runs/m4-small-context-001/preflight.json --out runs/m4-small-context-001/subject-run
```

Only after that report passes, run calibration with the same paths and profile:

```sh
python3 -B processbench_remote.py calibration --profile small-context-v1 --data runs/processbench-source/gsm8k.json --prompt runs/processbench-source/critique_template.txt --provenance processbench/provenance.json --selection processbench/selection-small-context.json --preflight runs/m4-small-context-001/preflight.json --out runs/m4-small-context-001/subject-run
```

The runner enforces all twenty calibration records, at least eighteen usable outputs, and at least eight completion-gated exact matches per class. Only a passed calibration permits the `evaluation` phase with identical arguments. Preserve the original 60-attempt / 90-minute session ceiling, 150-second request reserve and combined nine-machine-hour weekly allowance.

At completion or any stop, send `STOP` followed by Enter to the service terminal. Verify its owned process group and service/backend ports are gone. Preserve partial outputs and failure records; do not delete dispatch markers or change the budget to restart. Publish reviewed records, update the manuscript, and keep the M4 free of research artifacts.

## Offline verification

All 127 offline tests pass. Run `python3 -B -m unittest discover -v` from the pilot directory. The [independent implementation review](processbench/SMALL_CONTEXT_IMPLEMENTATION_REVIEW.md) records the selection, configuration and failure-path checks. Offline tests establish implementation behavior; only a fresh live preflight can establish resource and token fit on the M4.
