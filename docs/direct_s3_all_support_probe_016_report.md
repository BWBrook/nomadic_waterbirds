# Goal 016 Direct S3 All-Support Probe

Accessed date: `2026-05-31`.

## Scope

This bounded rehearsal computed base DEA Water Observations metrics across the current event-window support set for `2018-01`, `2022-11`, and `2024-12` using direct public S3 COG reads and the Goal 015 support-intersecting WRS path/row scene-selection policy.

No full event-window extraction, lag metrics, time-history metrics, biodiversity analysis, or ecological interpretation was run.

## Compute Route

Run host label: `deep-server-ts`.
Remote working path: `/data/codex/repos/nomadic_waterbirds_goal016`.
Remote compute used: `True`.

## Row Status

Expected rows: `33`.
Observed rows: `33`.

| Status | Rows |
| --- | ---: |
| computed_direct_s3_metrics | 33 |

## Support Summary

| Support | Path rows | Computed months | Blocked months | Quality-high months | Wet months |
| --- | --- | ---: | ---: | ---: | ---: |
| nwb001_ramsar_component_359 | 092/081;092/082 | 3 | 0 | 2 | 0 |
| nwb001_ramsar_ref337 | 092/081;092/082 | 3 | 0 | 2 | 0 |
| nwb002_ramsar_ref1291 | 092/081;093/080;093/081 | 3 | 0 | 3 | 0 |
| nwb003_ramsar_component_121 | 091/080 | 3 | 0 | 3 | 0 |
| nwb003_ramsar_ref993 | 091/080;092/080 | 3 | 0 | 2 | 0 |
| nwb004_ramsar_component_354 | 093/085;094/085 | 3 | 0 | 2 | 0 |
| nwb004_ramsar_component_369 | 094/085 | 3 | 0 | 3 | 0 |
| nwb004_ramsar_ref265 | 093/085;094/085 | 3 | 0 | 2 | 0 |
| nwb005_dea_waterbody_r4ysdndx8_v3 | 094/080;095/080 | 3 | 0 | 3 | 0 |
| nwb005_dea_waterbody_r4yss38r6_v3 | 094/080;095/080 | 3 | 0 | 3 | 0 |
| nwb005_ramsar_ref791 | 094/080;095/080 | 3 | 0 | 3 | 0 |

## Comparison Summary

| Comparison status | Rows |
| --- | ---: |
| missing_or_blocked_reference | 8 |
| wetness_diff | 6 |
| wetness_within_tolerance_denominator_diff | 14 |
| within_tolerance | 11 |

`NWB002` Goal 015/014 comparisons all within tolerance: `True`.
Area comparisons use a predeclared `5.0` m2 absolute tolerance to allow cross-host floating-point summation differences while preserving exact count and proportion tolerances.

Legacy comparisons are validation context. Denominator-only differences are separated from wetness-field differences in the comparison CSV.

Wetness-field legacy differences are:

| Support | Month | Reference | Wetness differing fields |
| --- | --- | --- | --- |
| nwb004_ramsar_component_354 | 2022-11 | goal007_legacy_event_window | current_proportion_wet |
| nwb004_ramsar_component_369 | 2018-01 | goal009_full_window_context | current_wet_area_m2;current_proportion_wet;wet_pixel_observation_count;dry_pixel_observation_count |
| nwb004_ramsar_component_369 | 2024-12 | goal007_legacy_event_window | current_wet_area_m2;current_proportion_wet;wet_pixel_observation_count;dry_pixel_observation_count |
| nwb004_ramsar_ref265 | 2022-11 | goal007_legacy_event_window | current_wet_area_m2;current_proportion_wet;wet_pixel_observation_count;dry_pixel_observation_count |
| nwb004_ramsar_ref265 | 2024-12 | goal007_legacy_event_window | current_wet_area_m2;current_proportion_wet;wet_pixel_observation_count;dry_pixel_observation_count |
| nwb005_ramsar_ref791 | 2022-11 | goal007_legacy_event_window | current_wet_area_m2 |

## Recommendation For Goal 017

Review legacy wetness-field differences before any direct-S3 scale-up.
