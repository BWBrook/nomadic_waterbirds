# Goal 018 Path-Row Comparator Reconstruction

Accessed date: `2026-06-01`.

## Scope

This bounded reconstruction covers the four Goal 017 material rows classified as `insufficient_reference_evidence`. It does not launch full-window direct-S3 production or alter legacy output tables.

## Route Status Counts

| Route status | Rows |
| --- | ---: |
| stac_unavailable_direct_s3_provenance_only | 4 |

## Readiness Counts

| Readiness class | Rows |
| --- | ---: |
| ready_with_legacy_baseline_retired | 4 |

## Item-Set Comparison Counts

| Comparison status | Rows |
| --- | ---: |
| comparator_unavailable | 4 |
| item_sets_match | 4 |

Independent STAC comparator evidence obtained for all material targets: `no`.
Current direct-S3 defect found: `no`.
Bounded raster reruns used: `False`.

## Material Target Readiness

| Support | Month | Route status | Readiness class | Recommendation |
| --- | --- | --- | --- | --- |
| nwb004_ramsar_component_369 | 2018-01 | stac_unavailable_direct_s3_provenance_only | ready_with_legacy_baseline_retired | Legacy row can be retired as a blocking baseline; direct-S3 item provenance matches Goal 016, but independent STAC comparator evidence was unavailable. |
| nwb004_ramsar_ref265 | 2022-11 | stac_unavailable_direct_s3_provenance_only | ready_with_legacy_baseline_retired | Legacy row can be retired as a blocking baseline; direct-S3 item provenance matches Goal 016, but independent STAC comparator evidence was unavailable. |
| nwb004_ramsar_component_369 | 2024-12 | stac_unavailable_direct_s3_provenance_only | ready_with_legacy_baseline_retired | Legacy row can be retired as a blocking baseline; direct-S3 item provenance matches Goal 016, but independent STAC comparator evidence was unavailable. |
| nwb004_ramsar_ref265 | 2024-12 | stac_unavailable_direct_s3_provenance_only | ready_with_legacy_baseline_retired | Legacy row can be retired as a blocking baseline; direct-S3 item provenance matches Goal 016, but independent STAC comparator evidence was unavailable. |

## Interpretation

All four material legacy rows have reconstructed direct-S3 item provenance matching the committed Goal 016 item counts and hashes. Independent STAC comparator evidence was unavailable for at least one material row, so the legacy rows should be retired as blocking baselines on provenance grounds rather than independent STAC equivalence.

## Recommendation For Goal 019

Proceed to Goal 019 as a remote, restartable full-window direct-S3 hydrology production preflight or production run, retaining the support-intersecting WRS path-row scene-selection policy.
