# Goal 008 Log - Narran Subunit Evidence And Remote Hydrology Rehearsal

## Supervisor Preparation

- 2026-05-31: Supervisor reviewed Goal 007 outputs and confirmed the action
  repo was clean and synced at `afea5fc` (`Record Goal 007 clean-tree
  validation`).
- 2026-05-31: Supervisor parsed Goal 007 crosswalk and series outputs:
  15 crosswalk rows, 11 included supports, 660 support-month rows,
  659 computed rows, one retained Kerang read-timeout row, and quality counts
  of 271 high, 307 minimum, and 82 fail.
- 2026-05-31: Supervisor archived the broad Deep Research review under
  `docs/literature/`, added a triage note, and created a source-verification
  queue. The report supports the dynamic hydrology and observation-process
  framing but is not yet source-verified manuscript evidence.
- 2026-05-31: Supervisor tightened repo-local compute guidance after Goal 007
  needed a fallback event window on the Mac mini. Goal 008 explicitly
  authorises a `deep-server` probe and remote hydrology rehearsal.
- 2026-05-31: Goal package written for publication into the action repo under
  `docs/goals/008-narran-subunit-and-remote-hydrology-rehearsal/`.

## Executor Checkpoints

`nomad` should update this log during execution.

- 2026-05-31: Executor started Goal 008 in
  `/Users/bwbrook/papers/nomadic_waterbirds` on `main`; `git status
  --short --branch` reported a clean tree tracking `origin/main`.
- 2026-05-31: Confirmed repo is beyond the required Goal 007 checkpoint:
  current `HEAD` was `eee404f` (`Archive literature review and add Goal 008
  brief`), after `afea5fc` (`Record Goal 007 clean-tree validation`).
- 2026-05-31: Read repo-local and global `AGENTS.md`, the Goal 008 package,
  and the `nectar` control-plane docs required by `Goal.md`.
- 2026-05-31: Confirmed proposed Goal 008 staging paths are ignored:
  `data/scratch/goal008/`, `artifacts/narran_subunit_evidence/raw/`,
  `artifacts/remote_hydrology_rehearsal/raw/`,
  `artifacts/remote_hydrology_rehearsal/intermediate/`, and
  `artifacts/remote_hydrology_rehearsal/output/`.
- 2026-05-31: Added a failing Goal 008 unit test before implementation; it
  failed because `scripts/narran_subunit_evidence_008.py` did not yet exist.
- 2026-05-31: Implemented `scripts/narran_subunit_evidence_008.py` and
  `settings/narran_subunit_evidence_008.json`; the focused test then passed.
- 2026-05-31: Completed the bounded official/public Narran source review for
  DCCEEW/Ramsar, NSW plan, RSIS/ECD, Data.NSW vegetation-map metadata, and DEA
  Waterbodies parent overlaps. The generated crosswalk has 44 rows: one
  parent support, four unresolved named/context candidates, and 39 DEA
  Waterbody parent-overlap screens.
- 2026-05-31: Narran source conclusion: Clear Lake, Back Lake, Long Arm, and
  the lignum/channelised floodplain have official name/location/hydrology
  support, but no public standalone vector subunit geometry or named DEA UID
  relationship was verified in this goal. Narran remains parent-only for
  event-window hydrology.
- 2026-05-31: `ssh deep-server` timed out on the direct campus alias. The
  documented `deep-server-ts` alias succeeded and landed on `deep-server` as
  `bwbrook`: 64 logical CPUs, 125 GiB RAM, `/data` 13T total with 4.5T
  available, Python 3.12.3, GDAL 3.8.4, and Git 2.43.0.
- 2026-05-31: Remote GitHub SSH from `deep-server` returned `Permission
  denied (publickey)`, matching the control-plane note that source should be
  supplied by bundle/rsync from the Mac mini when direct GitHub auth is absent.
- 2026-05-31: Staged a remote working copy at
  `/data/codex/repos/nomadic_waterbirds_goal008` using `.git` plus the
  unignored source file list via `rsync`; raw local artifacts were not sent as
  source files.
- 2026-05-31: Remote tests passed on `deep-server-ts` with `python3 -m
  unittest discover -s tests -p "test*.py"`: 6 tests OK after the Goal 008
  GDAL portability test was added.
- 2026-05-31: Remote Narran evidence script passed on `deep-server-ts`,
  producing 44 crosswalk rows and 39 DEA parent-overlap screens.
- 2026-05-31: First remote hydrology smoke exposed a small portability issue:
  the shared rasterisation helper requested the OGR `MEM` vector driver, while
  `deep-server` GDAL 3.8 exposes `Memory`. Added a tested fallback in
  `scripts/official_support_hydrology_005.py`.
- 2026-05-31: Second remote hydrology smoke built the Narran parent reference
  grid successfully (`403 x 414`, 166842 grid cells, 93937 support-mask
  pixels) but DEA STAC returned `HTTP Error 503: Service Temporarily
  Unavailable`.
- 2026-05-31: Confirmed the STAC blocker was upstream rather than remote-host
  specific: remote probes for `2020-03`, `2022-11`, `2024-11`, and `2024-12`
  and local probes for `2020-03` and `2024-12` all returned HTTP 503.
- 2026-05-31: Full `2018-01` through `2024-12` remote event-window run was not
  launched because DEA STAC was unavailable; launching the stretch run would
  produce blocked rows rather than useful hydrology scale-up evidence.
- 2026-05-31: Drafted Goal 008 reports/manifests and updated project
  navigation, source evidence, data stream register, and decision log.
- 2026-05-31: Validation passed before commit: `git diff --check`, Python
  compile checks for changed scripts, 6 local unit tests, JSON parsing,
  Narran CSV/manifest shape checks, ignored staging-path checks, committed
  file-size and raw-extension hygiene, local Markdown link check
  (`127` links, none missing), and unfinished-marker scan all passed.
- 2026-05-31: Committed and pushed Goal 008 package to `origin/main` as
  `9b60e0e` (`Resolve Narran evidence and rehearse remote hydrology`).
