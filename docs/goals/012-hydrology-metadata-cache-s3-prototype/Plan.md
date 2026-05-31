# Plan

## Purpose

Convert Goal 011's acquisition-route recommendation into a tiny, reviewable
prototype. The result should decide whether cached STAC metadata, direct public
S3/item indexing, or another official route should carry the next hydrology
extraction goal.

## Expected File Responsibilities

- `settings/hydrology_metadata_cache_s3_012.json`: candidate/months, route
  limits, cache keys, ignored staging paths, endpoint preflight thresholds, and
  output paths.
- `scripts/hydrology_metadata_cache_s3_012.py`: small route prototype for STAC
  preflight/cache fill where available, S3/index discovery, item hashing, and
  compact manifest/table output.
- `tests/test_goal012_hydrology_metadata_cache.py`: focused tests for pure
  functions and committed output contracts.
- `docs/hydrology_metadata_cache_s3_012_report.md`: narrative result,
  limitations, and next-step recommendation.
- `docs/hydrology_metadata_cache_s3_012_manifest.json`: machine-readable run
  provenance, route statuses, item-set hashes, and staging status.
- `docs/hydrology_metadata_item_sets_012.csv`: route-by-month item-set summary.
- `docs/hydrology_metadata_route_comparison_012.csv`: route comparison table.
- `docs/source_evidence_register.md`, `docs/data_stream_register.md`,
  `docs/decision_log.md`, `docs/README.md`: project context updates.
- `docs/goals/012-hydrology-metadata-cache-s3-prototype/Log.md`: live log.

## Task Sequence

1. Confirm repo state and required checkpoint.
2. Read required instructions, `nectar` docs, and Goal 011 evidence.
3. Review current hydrology code enough to reuse candidate/support metadata and
   avoid duplicating fragile assumptions.
4. Select the candidate and three probe months, recording the rationale.
5. Confirm local ignored staging paths before live route writes.
6. Write tests for cache-key construction, item-set hashing, route-status
   classification, and output shape.
7. Implement the small route prototype script/config.
8. Run the strict STAC preflight. If it fails, record unavailable status and
   continue with S3/index only.
9. Run the direct S3 or inventory-style route probe under bounded limits.
10. Compare item sets where both routes are available; otherwise record route
    viability and equivalence blocker.
11. Write compact CSV/JSON/Markdown outputs and update registers/logs.
12. Validate code, outputs, docs, links, Git/data hygiene, and repeated-hash
    stability.
13. Commit and push if validation passes.

## Self-Review Questions

- Did this goal avoid another full extraction attempt?
- Did it reduce dependence on repeated live STAC searches?
- Are technical viability and scientific equivalence clearly separated?
- Are full item JSON, S3 listings/inventories, rasters, and cache files kept
  out of Git?
- Can the next goal be issued without guessing which acquisition route to use?
