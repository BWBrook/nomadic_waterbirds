# Goal 011 Hydrology Acquisition Route Decision

Accessed date for current official source checks: `2026-05-31`.

## Recommendation

Do not launch another full `2018-01` through `2024-12` hydrology recovery run
on the current per-support/month STAC workflow.

The next executable hydrology goal should be a bounded acquisition redesign
that prototypes two official DEA routes in parallel:

1. A scientifically equivalent STAC metadata cache, starting with
   candidate-month caches and escalating to month/support-set caches only after
   item-coverage tests pass.
2. A direct public S3 or S3-inventory index prototype for known
   `ga_ls_wo_3` path/row/month keys, with item-set comparison against STAC
   when DEA STAC is available again.

This keeps DEA Water Observations (Landsat) as the primary evidence source,
while reducing the chance of another expensive run dominated by endpoint
failures. Lower-evidence products such as DEA Water Observations Statistics and
DEA Waterbodies should remain context, diagnostics, or UID-specific fallback
evidence only. They should not replace monthly support-level Water
Observations metrics for reaction-norm analysis.

## Evidence Reviewed

Current official DEA documentation confirms that
[DEA Water Observations (Landsat)](https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/?tab=overview)
is the relevant primary product: `ga_ls_wo_3`, 30 m raster, coverage from
`1986-08-16` to present, daily and ongoing updates, and individual Landsat
scene observations useful for analyses needing particular times rather than
long-term summaries.

DEA's
[AWS guide](https://knowledge.dea.ga.gov.au/guides/setup/AWS/data_and_metadata/)
documents `s3://dea-public-data` in `ap-southeast-2`, public programmatic
access with `AWS_NO_SIGN_REQUEST=Yes`, Cloud Optimised GeoTIFF storage, and
Water Observations under `derivative/ga_ls_wo_3`. DEA's
[STAC guide](https://knowledge.dea.ga.gov.au/notebooks/How_to_guides/Downloading_data_with_STAC/)
documents the Explorer STAC endpoint as a route for searching metadata and
streaming/downloading cloud data. DEA's
[FAQ](https://knowledge.dea.ga.gov.au/guides/about/faq/) distinguishes STAC
and `odc-stac` for bounding-box/time-range queries from direct S3 access when
specific file paths are known.

Official lower-evidence routes were also checked:

- [Water Observations Statistics](https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-statistics-landsat/)
  provides annual, seasonal, and multi-year `count_wet`, `count_clear`, and
  `frequency` products, not monthly scene-level event-window metrics.
- [DEA Waterbodies](https://knowledge.dea.ga.gov.au/data/product/dea-waterbodies-landsat/?tab=description)
  provides polygon outlines and per-waterbody wet-surface time series, but the
  documentation warns about limitations in vegetated wetlands, narrow rivers,
  patchy waterbodies, and area estimates.
- The [DEA Sandbox](https://knowledge.dea.ga.gov.au/guides/setup/Sandbox/sandbox/)
  and [Open Data Cube loading guide](https://knowledge.dea.ga.gov.au/notebooks/Beginners_guide/04_Loading_data/)
  show official datacube-style routes, including NCI/Sandbox compatibility for
  DEA notebooks, but this repo has not yet run the project support masks in
  those environments.

## Query-Pattern Audit

The current event-window workflow calls `stac_search` inside
`process_event_window`, within the loop over every support and every month.
The Goal 009 full-window table has 11 supports and 84 months, so the status
quo attempts 924 live STAC searches. With the current three-attempt retry
policy, that can become 2772 HTTP attempts before any COG reads are counted.

Goal 009 produced the expected 924 support-month rows, but only 145 computed.
The remaining 779 rows were retained as classified
`transient_endpoint_failure` blocked rows. Goal 010 then correctly stopped
before recovery because Mac mini probes returned HTTP 503 for the three probe
months, and `deep-server-ts` remained unstable.

The cache opportunities are:

- Candidate-month cache: 5 candidates by 84 months, or 420 searches. This is a
  54.5% search reduction before retry attempts.
- Month/support-set cache: 84 month-level searches. This is a 90.9% search
  reduction before retry attempts, but requires stronger pagination and
  item-filtering tests.
- Direct S3 or inventory index: zero live STAC searches if path/row/month item
  discovery can be proven complete.

Details are in
[hydrology_stac_query_pattern_011.csv](hydrology_stac_query_pattern_011.csv).

## Live Probe

The bounded Goal 011 probe wrote only ignored JSON under
`artifacts/hydrology_access_route_011/output/`.

Command:

```bash
python3 scripts/hydrology_acquisition_route_probe_011.py --host-label mac-mini-goal011 --output artifacts/hydrology_access_route_011/output/route_probe_macmini_011.json
```

Results:

- Public S3 prefix list for
  `derivative/ga_ls_wo_3/1-6-0/093/080/2022/11/` returned HTTP 200 and five
  sample keys.
- HEAD on a known `ga_ls_wo_3` Water Observations COG returned HTTP 200,
  `Content-Type: image/tiff`, and `Content-Length: 3365877`.
- A one-item STAC search for `ga_ls_wo_3`, `2022-11`, and the tiny Narran
  probe box returned HTTP 503.

This does not prove a complete S3-only acquisition route, but it does show
that public object access can work during a live STAC outage.

## Route Decision

The status quo is not recommended as the next primary path. It is
scientifically equivalent when it works, but Goal 009 and Goal 010 show that
the current loop has too many opportunities to fail against an unstable live
endpoint.

Candidate-month STAC caching is the nearest equivalent redesign. It still uses
official STAC discovery and the same Water Observations COG assets, but it
queries each candidate/month once and then reuses cached metadata for child
supports. The safe cache key is `collection|month|candidate_bbox_hash`, with a
committed compact manifest and ignored item-cache JSON.

Month/support-set caching is the stronger reduction target. The safe cache key
is `collection|month|support_set_bbox_hash`, but the prototype must prove that
the unioned bounding box, pagination, and item filtering do not miss support
intersections.

Direct S3 or S3 inventory is worth prototyping immediately because the public
S3 probes succeeded while STAC failed. It should not be treated as equivalent
until one candidate/month path-row index is compared with STAC or a datacube
query after service recovery.

The NCI/datacube route is official and likely robust for larger work, but it
requires separate environment/account setup and code adaptation. It is a good
contingency if S3/index and cached-STAC prototypes fail.

Water Observations Statistics and DEA Waterbodies are not substitutes for the
monthly event-window metric contract. They can support context, screening, or
selected open-water UID diagnostics, but they lose the support-level monthly
scene aggregation needed for current wetness, lagged wetness, novelty after dry
periods, drying velocity, and hydroperiod persistence.

Full route details are in
[hydrology_acquisition_options_011.csv](hydrology_acquisition_options_011.csv).

## Recommended Goal 012

Recommended Goal 012: build a bounded hydrology metadata acquisition prototype
that:

- creates ignored metadata caches for one candidate across three probe months;
- implements candidate-month STAC cache writing and reading, but only launches
  STAC work after a strict endpoint preflight passes;
- builds a direct S3 or S3-inventory path-row/month index for the same
  candidate/months;
- compares cached STAC item sets, direct S3/index item sets, and existing smoke
  COG paths where overlap is available;
- records compact item-count and hash manifests in Git while keeping item JSON,
  inventories, rasters, and temporary arrays ignored.

Success should be defined as a reproducible route decision for one candidate
and three months, not a full hydrology extraction.
