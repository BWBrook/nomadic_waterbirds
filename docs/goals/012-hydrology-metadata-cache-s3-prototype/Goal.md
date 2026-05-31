# Goal: Hydrology Metadata Cache And S3 Prototype

## Objective

Build a bounded hydrology metadata-acquisition prototype that tests whether
the project can avoid the unstable per-support/month STAC search pattern while
preserving the DEA Water Observations evidence target.

Prototype two routes for one candidate and three probe months:

1. candidate-month STAC metadata caching, launched only if a strict endpoint
   preflight passes;
2. direct public S3 or S3-inventory-style path-row/month item discovery.

The goal is a route-equivalence and acquisition-design proof. It is not a full
hydrology extraction, a recovery run, or an ecological interpretation.

## Why This Matters

Goal 011 showed that the current full-window workflow can require 924 live STAC
searches and up to 2772 HTTP attempts before COG reads. Candidate-month caching
could reduce live STAC searches to 420, while month/support-set caching could
reduce them to 84 if item coverage can be proven.

Goal 011 also showed that public S3 prefix listing and a known Water
Observations COG `HEAD` request worked while a one-item DEA STAC search
returned HTTP 503. This suggests direct public object discovery may be a useful
parallel route, but it is not scientifically equivalent until item sets can be
compared against STAC, Open Data Cube metadata, or another official metadata
source.

## Operating Mode

Metadata-acquisition prototype; route comparison; strict evidence boundary;
small live probes; no full support-month hydrology metrics.

## Scope

In scope:

- read repo instructions, Goal 011 report/manifest/tables/log, Goal 009/010
  blocker evidence, current hydrology code, and the relevant `nectar`
  compute/data-placement guidance;
- choose one primary prototype candidate from the current five-candidate
  support set, with a default preference for `NWB002` Narran Lake Nature
  Reserve because it remained blocked in the full-window run and has a known
  Goal 011 S3 path-row/month probe;
- use three probe months that cover early, flood/wet, and recent periods, with
  a default of `2018-01`, `2022-11`, and `2024-12` unless the evidence shows a
  better bounded set;
- implement or extend small scripts/config/tests needed to:
  - derive a candidate bbox/support-set cache key;
  - run a strict STAC endpoint preflight;
  - write/read ignored candidate-month STAC metadata caches when STAC is
    available;
  - discover direct public S3 path-row/month Water Observations items or use a
    bounded public S3-inventory-style index;
  - compare route item sets by stable IDs, asset keys, counts, and hashes
    where both routes are available;
- commit compact Markdown, CSV, JSON, script, setting, and test outputs that
  make the route decision reviewable;
- keep raw item JSON, S3 listings/inventories, rasters, arrays, and temporary
  route caches ignored;
- update docs navigation, source evidence, data stream register, decision log,
  and this goal log;
- commit and push the validated package to `main`.

Out of scope:

- running the full `2018-01` through `2024-12` hydrology extraction;
- recovering Goal 009 blocked support-month rows;
- computing or revising wet area, wet proportion, lags, novelty, drying
  velocity, or ecological interpretation metrics;
- changing wetland supports, subunit definitions, species streams, or
  manuscript claims;
- substituting Water Observations Statistics, DEA Waterbodies, or other
  lower-evidence products for the monthly DEA Water Observations metric
  contract;
- committing raw rasters, full STAC item dumps, full S3 inventories,
  GeoPackages, shapefiles, NetCDF, Parquet, RDS, SQLite/DuckDB stores,
  archives, or bulky derived products.

## Read First

- `/Users/bwbrook/papers/nomadic_waterbirds/AGENTS.md`
- `/Users/bwbrook/.codex/AGENTS.md`
- `/Users/bwbrook/work/nectar/docs/workflows/control-plane-doctrine.md`
- `/Users/bwbrook/work/nectar/docs/workflows/compute-resource-selection.md`
- `/Users/bwbrook/work/nectar/docs/workflows/project-integration.md`
- `/Users/bwbrook/work/nectar/docs/workflows/data-placement.md`
- `/Users/bwbrook/work/nectar/docs/workflows/smoke-tests.md`
- `/Users/bwbrook/work/nectar/docs/machines/deep-server.md`
- `/Users/bwbrook/work/nectar/docs/exchange/current_status.md`
- `docs/hydrology_acquisition_route_011_report.md`
- `docs/hydrology_acquisition_route_011_manifest.json`
- `docs/hydrology_acquisition_options_011.csv`
- `docs/hydrology_stac_query_pattern_011.csv`
- `docs/stac_resilience_009_report.md`
- `docs/remote_full_window_hydrology_009_report.md`
- `docs/stac_recovery_010_report.md`
- `docs/event_window_hydrology_series_2018_2024.csv`
- `scripts/hydrology_acquisition_route_probe_011.py`
- `scripts/event_window_hydrology_007.py`
- `settings/remote_full_window_hydrology_009.json`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Confirm the repo is at or beyond `0250859` (`Assess hydrology acquisition
  routes`).
- Inspect files with `rg --files`.
- Confirm ignored staging paths before any live probe writes files.
- Treat unexpected dirty state as a blocker unless it is only this goal's
  files.

## Required Deliverables

Create:

- `docs/hydrology_metadata_cache_s3_012_report.md`: supervisor-facing route
  prototype report with a clear recommendation for the next hydrology step.
- `docs/hydrology_metadata_cache_s3_012_manifest.json`: machine-readable
  provenance for candidate/month choice, route probes, cache keys, source URLs,
  host facts, item counts, hashes, comparison statuses, and ignored staging
  paths.
- `docs/hydrology_metadata_item_sets_012.csv`: compact route item-set summary.
  Include at minimum candidate ID, month, route, path/row or bbox key, item
  count, item ID hash, asset key hash, route status, and cache path status.
- `docs/hydrology_metadata_route_comparison_012.csv`: route comparison and
  next-step table. Include scientific equivalence status, STAC dependence,
  S3/object-store dependence, failure mode, implementation cost, and
  recommendation.
- `scripts/hydrology_metadata_cache_s3_012.py`: bounded prototype script or
  equivalent small route module.
- `settings/hydrology_metadata_cache_s3_012.json`: prototype configuration.
- `tests/test_goal012_hydrology_metadata_cache.py`: focused tests for cache
  keys, manifest shape, route status classification, item-set hashing, and
  no-raw-commit assumptions.

Update:

- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`
- `docs/README.md`
- `docs/goals/012-hydrology-metadata-cache-s3-prototype/Log.md`

## Route-Prototype Requirements

Candidate and month selection:

- Use one candidate from `docs/prototype_wetland_unit_crosswalk.csv` and the
  current event-window support set.
- Default to `NWB002` Narran Lake Nature Reserve unless review of Goal 011 or
  S3 path-row coverage shows another candidate is more informative.
- Use exactly three months unless a route cannot be evaluated without one
  additional control month. If an extra month is added, justify it in the
  report and manifest.

STAC cache route:

- Run a strict STAC preflight before any cache fill. The preflight must define
  pass/fail before seeing the result.
- If STAC returns HTTP 503 or equivalent service instability, mark the STAC
  cache route as unavailable and do not keep retrying.
- If STAC passes, write full item JSON only to ignored storage and commit only
  compact hashes/counts/provenance.
- Cache key should start as
  `collection|candidate_id|month|candidate_bbox_hash`. If a safer key is used,
  explain why.

Direct S3 or inventory route:

- Use official DEA public object-store conventions or public inventory
  metadata only.
- Prefer metadata listing, key discovery, and `HEAD` checks over downloading
  rasters.
- If path-row/month discovery is incomplete, label it incomplete rather than
  presenting it as equivalent.
- Keep raw listings, inventories, and temporary indexes ignored.

Item-set comparison:

- When both routes produce item sets for a candidate/month, compare counts,
  stable item identifiers, Water Observations asset keys, and hashes.
- When STAC is unavailable, compare S3/index evidence only against known Goal
  011 COG paths or previously committed compact provenance, and label this as
  route viability rather than scientific equivalence.
- The report must say whether the next goal should:
  - implement cached STAC extraction;
  - implement direct S3/index-backed extraction;
  - run a stronger month/support-set cache prototype;
  - route to ODC/NCI/Sandbox;
  - or wait for service recovery.

## Compute And Data Placement

This goal should usually run on the Mac mini because it is metadata-light. Use
`deep-server-ts` only if route discovery requires Linux/GDAL behaviour,
network locality, or persistent `/data/codex` staging.

If remote work is used:

- read the `nectar` docs listed above;
- run a target-machine smoke test before live route discovery;
- stage remote clones and generated payloads under `/data/codex`;
- copy only compact summaries/manifests back into the repo;
- record remote paths and cleanup state in the manifest.

Ignored local staging should use paths such as:

- `artifacts/hydrology_metadata_cache_012/raw/`
- `artifacts/hydrology_metadata_cache_012/intermediate/`
- `artifacts/hydrology_metadata_cache_012/output/`

Confirm these paths are ignored before writing route artefacts.

## Scientific Guardrails

- This goal does not produce hydrology evidence for ecological analysis.
- Do not interpret wetness, refuge status, breeding, abundance, occurrence, or
  bird response.
- Do not replace the monthly Water Observations metric contract with a
  convenient summary product.
- The central scientific question remains dynamic hydrological reaction norms,
  not static wetland occupancy or static waterbody presence.
- Equivalence requires item-set evidence. A route that works technically is
  not automatically an evidence-equivalent route.

## Validation Gates

The goal is complete only when:

- `git status --short --branch` is recorded at start and finish;
- `rg --files` confirms expected files are present;
- `git diff --check` passes;
- focused Goal 012 tests pass;
- the full local test suite passes unless the goal records a narrow reason for
  targeted validation only;
- JSON manifests/settings parse with `python3 -m json.tool`;
- CSV deliverables parse and have required columns;
- item-set hashes are stable under repeated local execution from the same
  ignored cache;
- source URLs in claim-bearing docs have corresponding source-register entries
  or are recorded in the Goal 012 manifest;
- ignored staging paths are confirmed ignored;
- no committed files exceed 5 MB;
- no committed raw source-data extensions are present;
- local Markdown links in new/edited docs resolve;
- unfinished-marker scan finds no unresolved stub language.

If validation passes, commit and push the Goal 012 package to `main`.

## Checkpoint Rules

Update `Log.md` when:

- starting state is confirmed;
- required docs and Goal 011 evidence have been read;
- candidate and probe months are selected;
- ignored staging paths are confirmed;
- STAC preflight is complete;
- S3/index route probe is complete;
- item-set comparison is complete or explicitly blocked;
- route recommendation is drafted;
- validation is complete;
- commit/push is complete or a blocker is recorded.

## Decision Authority

You may decide:

- the final candidate/month selection within the bounds above;
- whether direct S3, S3 inventory, or both are practical for the bounded
  prototype;
- whether to use Mac mini only or add a small `deep-server-ts` rehearsal;
- whether the next step should be cached STAC, direct S3/index, ODC/NCI, a
  stronger cache prototype, or a wait condition.

Pause for Barry only if the prototype would require credentials, accounts,
large downloads, a new data product substitution, or a scientific narrowing of
the planned paper.
