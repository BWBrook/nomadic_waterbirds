# Goal 003 Log - Prototype Wetland Crosswalk And Hydrology Metric Specification

## Supervisor Preparation

- 2026-05-30: Supervisor reviewed Goal 002 outputs, verified action repo state,
  and spot-checked key official sources.
- 2026-05-30: Supervisor selected a structured crosswalk and metric-spec goal
  before executable hydrology extraction.
- 2026-05-30: Goal package written for publication into the action repo under
  `docs/goals/003-prototype-wetland-crosswalk-hydrology-spec/`.

## Executor Checkpoints

`nomad` should update this log during execution.

- 2026-05-30: Executor started Goal 003 from
  `/Users/bwbrook/papers/nomadic_waterbirds`; confirmed clean `main` tracking
  `origin/main`, latest commit `dc1aff7` (`Add Goal 003 wetland crosswalk
  brief`), and current tree containing Goal 001-002 outputs plus the Goal 003
  packet. Read `AGENTS.md`, Goal 003 `Goal.md`, `Plan.md`, `Runbook.md`, and
  the Goal 002 feasibility documents.
- 2026-05-30: Selected 7 candidate wetland complexes for the prototype
  crosswalk: Macquarie Marshes, Narran Lake Nature Reserve, Gwydir Wetlands,
  Kerang Wetlands, Currawinya Lakes, the Coorong/Lakes Alexandrina and Albert,
  and Coongie Lakes. Marked 5 for the next extraction smoke and 2 as deferred
  edge comparators.
- 2026-05-30: Drafted `docs/prototype_wetland_unit_crosswalk.csv` and
  `docs/prototype_wetland_unit_crosswalk.md`; initial CSV parse confirmed 7
  rows and all required columns.
- 2026-05-30: Drafted `docs/hydrology_metric_spec.md` with monthly Water
  Observations base metrics, invalid-observation rules, lag, hydroperiod,
  novelty, drying, regional availability, and quality flags.
- 2026-05-30: Drafted `docs/product_access_probe_003.md` from public
  metadata/header probes; no temporary files or raw source datasets were
  created.
- 2026-05-30: Drafted `docs/decision_memo_003.md` and updated
  `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, and `docs/README.md`.
- 2026-05-30: Validation checkpoint completed before commit: `git diff
  --check` passed; `find . -type f -size +5M -not -path './.git/*'` found no
  large files; targeted unfinished-language scan found no matches in new or
  edited Goal 003 docs; local Markdown link check resolved 34 local links; CSV
  parse confirmed all required columns and 7 candidate rows; raw-data extension
  scan found no committed shapefile, GeoPackage, GeoJSON, raster, NetCDF,
  Parquet, RDS, archive, or similar source-data files.
- 2026-05-30: Prototype design package committed as `c012cfb` (`Specify
  prototype wetland crosswalk and hydrology metrics`) and pushed to
  `origin/main`.
