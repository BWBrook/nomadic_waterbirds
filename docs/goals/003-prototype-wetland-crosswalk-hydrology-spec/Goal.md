# Goal: Prototype Wetland Crosswalk And Hydrology Metric Specification

## Objective

Build a structured prototype wetland-unit crosswalk and monthly hydrology metric
specification for a small Murray-Darling Basin/eastern-inland pilot, using only
public metadata and small official geometry/product-access checks.

## Why This Matters

Goal 002 showed that hydrology-first progress is feasible, but the paper's
scientific credibility depends on choosing spatial units that can support
dynamic hydrology, biodiversity alignment, reviewer-legible interpretation,
and uncertainty. Goal 003 should convert the feasibility recommendation into a
reviewable prototype design that a later extraction goal can execute.

The outcome should be a crosswalk and metric contract, not a hydrology dataset.

## Operating Mode

Full paper workflow plus scientific workflow design.

## Scope

In scope:

- select a small candidate set of named MDB/eastern-inland wetland complexes
  from official/public sources
- create a structured crosswalk between named complexes, official geometry or
  catalogue sources, DEA Waterbodies support, DEA Water Observations summary
  needs, Geofabric/basin context, and public biodiversity/EAWS alignment
  surfaces
- define monthly hydrology metrics and invalid-observation rules for DEA Water
  Observations
- run only small public metadata, endpoint, or geometry/product-access checks
  needed to classify feasibility
- update project planning documents and decision logs
- commit and push the validated prototype design package

Out of scope:

- bulk DEA, eBird, Birdata, ALA, or EAWS downloads
- submitting data access requests
- using credentials or private portals
- committing raw geometry or raw biodiversity/hydrology data
- fitting models or generating response results
- final wetland-unit, species-list, guild, or model-family decisions
- remote/HPC work

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/project_brief.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/source_evidence_register.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/data_access_feasibility.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/wetland_unit_feasibility.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/prototype_scope.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/decision_memo_002.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/data_stream_register.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/validation_plan.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `bf260c6` (`Record Goal 002 publication
  checkpoint`).
- Inspect the tree with `rg --files`.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Work

Create these deliverables:

- `docs/prototype_wetland_unit_crosswalk.csv`: structured candidate-unit table.
  Include at least 5 and at most 8 candidate wetland complexes. Required
  columns:
  - `candidate_id`
  - `candidate_name`
  - `state_or_region`
  - `primary_named_source`
  - `primary_source_id_or_url`
  - `geometry_source`
  - `geometry_licence_or_terms`
  - `dea_waterbodies_support`
  - `water_observations_summary_needed`
  - `geofabric_context`
  - `public_biodiversity_or_eaws_alignment`
  - `boundary_or_habitat_caveat`
  - `prototype_role`
  - `include_in_next_extraction_smoke`
- `docs/prototype_wetland_unit_crosswalk.md`: interpretation of the CSV,
  candidate selection rationale, rejected or deferred candidates, and unit
  support caveats.
- `docs/hydrology_metric_spec.md`: monthly DEA Water Observations metric
  contract. Include current wet area/proportion wet, clear-observation counts,
  invalid-observation handling, 1-month and 3-month lags, cumulative wet months,
  wetting novelty after dry spells, drying velocity, regional water
  availability, and minimum data-quality flags.
- `docs/product_access_probe_003.md`: a brief record of the official metadata,
  endpoint, or small public product-access checks performed. Record commands,
  URLs, sizes if anything temporary was fetched, and whether any temporary
  files were deleted or left ignored.
- `docs/decision_memo_003.md`: supervisor-facing recommendation on whether the
  project is ready for a small executable hydrology extraction smoke test, with
  alternatives and residual risks.
- updated `docs/data_stream_register.md` and `docs/decision_log.md`.
- updated `docs/README.md` if new documents need navigation.
- updated `docs/goals/003-prototype-wetland-crosswalk-hydrology-spec/Log.md`.

Candidate starting points to investigate, not mandatory inclusions:

- Macquarie Marshes
- Narran Lakes
- Gwydir Wetlands
- Booligal Wetlands or Lachlan Swamps
- Great Cumbung Swamp or Lowbidgee floodplain
- Kerang Lakes
- Lake Cowal
- Coorong and Lower Lakes, if useful as an edge or later comparator

Choose the final 5-8 candidates based on official-source support and prototype
value.

## Small Access-Check Rules

Allowed:

- official catalogue/metadata pages
- HTTP header checks or API metadata checks
- tiny public geometry/product samples if needed to determine fields or
  overlap feasibility
- temporary files in ignored locations, with sizes and cleanup recorded
- committed CSV/Markdown summaries derived from public metadata

Not allowed:

- bulk satellite, biodiversity, or survey downloads
- raw eBird, Birdata, ALA, or EAWS data
- private/credentialed access
- committed raw shapefiles, rasters, GeoPackages, or other source datasets
- any download whose size or licence would be unclear to a reviewer

## Scientific Guardrails

- Keep the final wetland-unit decision deferred.
- Do not let DEA Waterbodies stand in for vegetated/floodplain wetland habitat
  without caveats.
- Use DEA Water Observations as the authoritative metric source for monthly
  hydrological dynamics.
- Keep named wetland complexes as interpretation/reporting units unless the
  crosswalk shows a better prototype surface.
- Make uncertainty and boundary caveats visible per candidate unit.
- Do not treat biodiversity feasibility as biodiversity data.

## Validation Gates

The goal is complete only when these pass or a blocker is logged:

- `git status --short --branch` at start and finish
- `rg --files`
- `git diff --check`
- confirm no files larger than 5 MB were added
- inspect new Markdown/CSV files for unresolved stub language
- verify local Markdown links in new or edited docs resolve
- parse `docs/prototype_wetland_unit_crosswalk.csv` with a standard CSV parser
  and confirm required columns are present
- confirm the crosswalk includes 5-8 candidate rows
- confirm no raw data files were committed

If validation passes, commit and push the prototype design package to `main`.

## Checkpoint Rules

Update `docs/goals/003-prototype-wetland-crosswalk-hydrology-spec/Log.md` when:

- starting state is confirmed
- candidate wetland list is selected
- crosswalk CSV and interpretation are drafted
- hydrology metric spec is drafted
- product-access probe record is drafted
- decision memo is drafted
- validation is complete
- commit/push is complete or a blocker is recorded

## Decision Authority

You may autonomously:

- choose the final 5-8 candidate wetland complexes for the prototype table
- inspect official public metadata and small access surfaces
- classify candidates as include/defer/reject for the next extraction smoke
- define hydrology metric formulas and quality flags at specification level
- recommend the next goal
- commit and push validated documentation and small structured summary tables

Pause and ask Barry before:

- downloading bulk datasets
- submitting access requests
- using credentials or private portals
- committing raw source geometry or raster files
- making final wetland-unit or species/guild decisions
- adding executable analysis dependencies or large scripts
- launching remote compute

## Stop Conditions

Stop when one of these is true:

- the crosswalk, metric spec, access-probe record, and decision memo are
  complete, validated, committed, and pushed
- official sources cannot support a candidate set without human scientific
  choice
- the work would require bulk data, private access, or final scientific
  decisions outside this goal

## Final Response Requirements

Report:

- what changed
- candidate wetland complexes selected and why
- hydrology metrics specified
- product-access checks performed and whether any temporary files remain
- exact validation commands and outcomes
- commit hash and push status, or why no commit/push occurred
- residual risks
- recommended Goal 004
