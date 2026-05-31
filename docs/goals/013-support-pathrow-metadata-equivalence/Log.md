# Log

Goal: Support path-row coverage and metadata equivalence

Status: Ready for action agent.

## Supervisor Setup

- 2026-05-31: Goal 013 packet created from Goal 012 metadata-acquisition
  prototype. This goal should test support-to-path/row completeness and an
  official metadata comparator before any direct-S3 extraction is promoted.

## Execution Checkpoints

- Starting state: 2026-05-31 on `main` at `e5e89e7` (`Add Goal 013 support path-row equivalence brief`), `git status --short --branch` reported `## main...origin/main`.
- Required reading complete: read Goal 013 `Goal.md`, `Plan.md`, `Runbook.md`, `Log.md`, repo/global `AGENTS.md`, required `nectar` control-plane docs, Goal 011/012 reports/manifests/tables/scripts/settings, event-window support table, source evidence register, and data stream register.
- Path/row source selected and staged or blocked: official USGS Landsat WRS-2 descending daytime shapefile selected; `WRS2_descending.zip` staged only under ignored `artifacts/support_pathrow_metadata_013/raw/`, 5268121 bytes, SHA-256 `9e6467f7709999683a41a71f9b0e388b6b84a5f59732ca797c5266c72eb9ce76`.
- Ignored staging confirmed: `artifacts/support_pathrow_metadata_013/{raw,intermediate,output}/probe.json` all matched `.gitignore:22 artifacts/*` before raw WRS, S3, STAC, or comparator artefacts were written.
- Support-to-path/row crosswalk drafted: `docs/support_pathrow_crosswalk_013.csv` has 21 geometry-intersection rows across all 11 current event-window supports; `NWB002` intersects `092/081`, `093/080`, and `093/081`.
- Direct S3 complete-path-row listing complete: `docs/support_pathrow_item_sets_013.csv` records `NWB002` complete-path/row Water Observations item counts of 9 for `2018-01`, 11 for `2022-11`, and 11 for `2024-12`; raw listings and HEAD metadata remain ignored.
- Official comparator probe complete or blocked: strict DEA STAC preflight returned HTTP 200 for all three probe months; after filtering STAC bbox results to the derived WRS path/row set, STAC and direct-S3 asset keys matched for all three months. Local ODC/`odc-stac` contingency probe is blocked by missing `datacube` and `odc.stac` modules.
- Equivalence status decided: `equivalent` for bounded `NWB002` metadata item sets only; not hydrology metrics and not a full-window extraction approval.
- Route recommendation drafted: recommended Goal 014 is a bounded direct-S3 extraction rehearsal for `NWB002` using the complete derived path/row set and same three months, with strict validation before any full-window run.
- Validation complete: 2026-05-31 validation passed before staging:
  - expected files found with `rg --files`;
  - `git diff --check`;
  - `python3 -m unittest tests.test_goal013_support_pathrow_metadata` (6 tests);
  - `python3 -m unittest discover -s tests -p 'test*.py'` (31 tests);
  - settings and manifest parsed with `python3 -m json.tool`;
  - CSV deliverables parsed with required columns and valid path/row values;
  - item-set CSV SHA-256 stayed stable under `--reuse-ignored-cache` rerun (`d35f611f7a22a8f2af1fddd466b5d455591e7c1c54b56a6b66abd1a80273439e`);
  - source URL coverage, ignored staging, committed-size, committed raw-extension, local Markdown-link, and unfinished-marker checks passed.
- Commit/push complete: pending final publication from the validated worktree; final commit SHA and push status to be reported by the action agent after Git operations.
