# Goal 013 Support Path-Row Coverage And Metadata Equivalence

Accessed date for current official source checks: `2026-05-31`.

## Scope

This is a metadata and coverage prototype only. It does not compute wet area, wet proportion, lags, novelty, drying velocity, persistence, or ecological response metrics.

## Path/Row Source And Coverage

Path/row source: [Landsat World Reference System - 2 Descending (Daytime) Shapefile](https://www.usgs.gov/media/files/landsat-world-reference-system-2-descending-daytime-shapefile), staged under ignored `artifacts/support_pathrow_metadata_013/raw/WRS2_descending.zip` with SHA-256 `9e6467f7709999683a41a71f9b0e388b6b84a5f59732ca797c5266c72eb9ce76`.

The prototype rebuilt the current event-window support set and derived geometry intersections against the official WRS-2 descending footprint layer for `11` supports.

`NWB002` complete derived path/row set: `092/081, 093/080, 093/081`.

Coverage is labelled `complete` because the crosswalk used support geometry intersection. WRS scene footprints overlap, so intersection areas in the CSV are per-scene evidence and are not additive support area estimates.

## Direct S3 Item Sets

Direct public S3 listing was run for the complete `NWB002` path/row set and the three Goal 012 probe months.

| Month | Complete-path/row S3 Water Observations item count |
| --- | ---: |
| 2018-01 | 9 |
| 2022-11 | 11 |
| 2024-12 | 11 |

The Goal 012 known `093/080` slice was reproduced, and the derived support coverage added the other intersecting path/row slices listed above. Raw S3 listings and HEAD metadata remain under ignored `artifacts/` paths.

## Official Comparator Status

Final equivalence status: `equivalent`.

DEA STAC was probed first under the strict preflight. STAC bbox results were then filtered to the derived WRS path/row set before comparison with direct S3 assets, because bbox search can include scene footprints outside the support geometry-derived path/row set.

- 2018-01: filtered STAC=9, direct S3=9, bbox-only STAC extras=3, equal=True
- 2022-11: filtered STAC=11, direct S3=11, bbox-only STAC extras=4, equal=True
- 2024-12: filtered STAC=11, direct S3=11, bbox-only STAC extras=3, equal=True

The local Open Data Cube/`odc-stac` comparator availability check was still recorded as a contingency route; this Mac mini environment does not currently include those modules.

## Recommendation For Goal 014

Recommended Goal 014: build a bounded direct-S3 extraction rehearsal for `NWB002` only, using the derived complete path/row set and the same three probe months. Keep it as a read/aggregation rehearsal with strict validation against STAC-derived metadata and no full `2018-01` through `2024-12` run until the bounded extraction path passes.
