# Goal 017 Legacy Wetness Difference Triage

Accessed date: `2026-05-31`.

## Scope

This compact triage audits the six Goal 016 rows labelled `wetness_diff` against legacy Goal 007/009 references. It does not launch full-window direct-S3 production or alter legacy output tables.

## Root-Cause Counts

| Root-cause class | Rows |
| --- | ---: |
| insufficient_reference_evidence | 4 |
| tolerance_or_rounding_only | 2 |

Current direct-S3 extraction defect found: `no`.
Bounded raster reruns used: `False`.

## Row Classifications

| Support | Month | Reference | Root-cause class | Recommendation |
| --- | --- | --- | --- | --- |
| nwb004_ramsar_component_369 | 2018-01 | goal009_full_window_context | insufficient_reference_evidence | Do not use this legacy row as a blocking validation baseline; build a path-row-filtered comparator or bounded item reconstruction before production scale-up. |
| nwb004_ramsar_component_354 | 2022-11 | goal007_legacy_event_window | tolerance_or_rounding_only | Treat as harmless for direct-S3 route promotion, while retaining rounded legacy values as provenance. |
| nwb004_ramsar_ref265 | 2022-11 | goal007_legacy_event_window | insufficient_reference_evidence | Do not use this legacy row as a blocking validation baseline; build a path-row-filtered comparator or bounded item reconstruction before production scale-up. |
| nwb005_ramsar_ref791 | 2022-11 | goal007_legacy_event_window | tolerance_or_rounding_only | Treat as harmless for direct-S3 route promotion, while retaining rounded legacy values as provenance. |
| nwb004_ramsar_component_369 | 2024-12 | goal007_legacy_event_window | insufficient_reference_evidence | Do not use this legacy row as a blocking validation baseline; build a path-row-filtered comparator or bounded item reconstruction before production scale-up. |
| nwb004_ramsar_ref265 | 2024-12 | goal007_legacy_event_window | insufficient_reference_evidence | Do not use this legacy row as a blocking validation baseline; build a path-row-filtered comparator or bounded item reconstruction before production scale-up. |

## Interpretation

Two rows are tolerance or rounding only: their wet/dry integer counts, support grid fields, valid support area, quality flag, and wet-month flag match, with only tiny rounded wet-area or proportion differences.

The four material rows share support geometry, pixel counts, valid support area, and clean Goal 016 direct-S3 status, but the legacy references do not contain item hashes or path-row sets. They are therefore classified as `insufficient_reference_evidence`, not as current direct-S3 extraction defects.

## Recommendation For Goal 018

Build a bounded all-support path-row-filtered comparator or item-provenance reconstruction for the material legacy rows before full-window direct-S3 production.
