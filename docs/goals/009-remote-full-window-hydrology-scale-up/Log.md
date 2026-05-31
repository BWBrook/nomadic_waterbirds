# Goal 009 Log - Remote Full-Window Hydrology Scale-Up

## Supervisor Preparation

- 2026-05-31: Supervisor reviewed Goal 008 outputs and confirmed the action
  repo was clean and synced at `26ed2d3` (`Correct Goal 008 validation
  evidence`).
- 2026-05-31: Supervisor verified the Goal 008 Narran crosswalk shape:
  44 rows, including one parent support, four unresolved named/context
  candidates, and 39 DEA parent-overlap screens. Narran remains parent-only
  for event-window hydrology.
- 2026-05-31: Supervisor reviewed the Goal 008 compute memo and remote
  rehearsal. `deep-server-ts` is viable for hydrology scale-up, while direct
  `deep-server` timed out and remote GitHub SSH was unavailable.
- 2026-05-31: Supervisor noted the true blocker was upstream DEA STAC
  `HTTP 503` responses reproduced from both remote and local probes.
- 2026-05-31: Lab-leader note emphasised that remote/HPC goals should direct
  action agents to read `/Users/bwbrook/work/nectar` carefully. Goal 009
  therefore requires the relevant `nectar` workflow and machine docs before
  remote work.
- 2026-05-31: Goal package written for publication into the action repo under
  `docs/goals/009-remote-full-window-hydrology-scale-up/`.

## Executor Checkpoints

`nomad` should update this log during execution.
