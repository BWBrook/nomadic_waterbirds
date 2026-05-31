# STAC Recovery Report 010

Goal 010 tested whether DEA STAC and remote COG access were stable enough to
recover the Goal 009 `2018-01` through `2024-12` full-window hydrology table.

## Decision

Recovery was not launched. The service-stability preflight failed before a
large blocked-row recovery run was justified.

| Gate | Result |
| --- | --- |
| Mac mini endpoint probe | `service_unavailable_503` |
| `deep-server-ts` endpoint probe | `transient_endpoint_failure` |
| Blocked-row sample size | 33 selected rows |
| Blocked-row computation | Not launched after endpoint gate failed |
| Full recovery run | Not launched |

The Mac mini probe returned `HTTP 503` after three attempts for `2018-01`,
`2022-11`, and `2024-12`. The `deep-server-ts` probe was also unstable: one
month exhausted retry after read timeouts, while the two available months only
succeeded after three attempts.

## Goal 009 Starting Point

| Check | Value |
| --- | ---: |
| Rows | 924 |
| Supports | 11 |
| Months | 84 |
| Computed rows | 145 |
| Blocked rows | 779 |
| `quality_high` rows | 59 |
| `quality_minimum` rows | 73 |
| `quality_fail` rows | 792 |

## Blocked-Row Sample

A deterministic 33-row sample was selected from Goal 009 blocked rows. It covers
all 10 supports with blocked rows and the early, wet/flood, and recent periods.
The selected sample is recorded in `docs/stac_recovery_010_manifest.json`.

The sample was not computed because the endpoint probes already failed the Goal
010 launch gate. Launching blocked-row computation under the observed endpoint
state would have repeated the Goal 009 failure mode at additional cost without
moving the project closer to a usable hydrology table.

## Recovery Status

No Goal 010 recovery CSV was written. Goal 009 outputs were preserved unchanged.
The project still needs either a later recovery attempt under stable DEA STAC
conditions, or a separate decision about alternate hydrology acquisition routes.

Machine-readable evidence is in `docs/stac_recovery_010_manifest.json`.
