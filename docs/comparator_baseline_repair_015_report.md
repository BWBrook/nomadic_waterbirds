# Goal 015 Comparator Baseline Repair

Accessed date: `2026-05-31`.

## Scope

This bounded repair covers `NWB002` Narran Lake Nature Reserve only, the Goal 013 support-derived path/rows `092/081`, `093/080`, and `093/081`, and the Goal 014 probe months `2018-01`, `2022-11`, and `2024-12`.

No full-window extraction, all-support extraction, biodiversity analysis, or ecological interpretation was run.

## Scene-Selection Policy

For support-level monthly Water Observations metrics, include only scenes from WRS-2 path/rows whose official footprints intersect the support geometry; do not count STAC bbox-only scenes outside that derived path/row set as readable scenes or invalid observations.

STAC bbox results are discovery metadata. For support-level metrics, bbox-only Water Observations scenes outside the support-intersecting WRS path/row set are excluded before scene counting or denominator accounting.

## Repaired Comparator Baseline

STAC route status: `available`.

| Month | Status | Readable scenes | STAC bbox items | Bbox-only extras | Wet area m2 | Wet proportion |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2018-01 | repaired_pathrow_filtered_stac_comparator | 9 | 12 | 3 | 437.142883 | 5e-06 |
| 2022-11 | repaired_pathrow_filtered_stac_comparator | 11 | 15 | 4 | 18173724.0 | 0.214966 |
| 2024-12 | repaired_pathrow_filtered_stac_comparator | 11 | 14 | 3 | 4356122.5 | 0.051526 |

The repaired comparator rows reuse the Goal 014 metric values only after STAC metadata filtered to the support path/rows matches the Goal 014 direct-S3 asset-key hash for the same month.

## Comparisons

| Month | Comparison | Status | Differing fields | Recommendation |
| --- | --- | --- | --- | --- |
| 2018-01 | repaired_comparator_vs_goal014_direct_s3 | within_tolerance |  | use_repaired_comparator_for_next_bounded_scale_step |
| 2022-11 | repaired_comparator_vs_goal014_direct_s3 | within_tolerance |  | use_repaired_comparator_for_next_bounded_scale_step |
| 2024-12 | repaired_comparator_vs_goal014_direct_s3 | within_tolerance |  | use_repaired_comparator_for_next_bounded_scale_step |
| 2022-11 | legacy_goal007_bbox_stac_vs_repaired_comparator | mismatch_beyond_tolerance | readable_scene_count;invalid_obs_count;clear_obs_fraction | legacy_denominator_artifact_explained_use_repaired_baseline |
| 2024-12 | legacy_goal007_bbox_stac_vs_repaired_comparator | mismatch_beyond_tolerance | readable_scene_count;invalid_obs_count;clear_obs_fraction | legacy_denominator_artifact_explained_use_repaired_baseline |
| 2018-01 | legacy_goal009_status_context | legacy_blocked_no_metric_comparison |  | record_2018_01_as_bounded_repaired_comparator_only_not_full_window_recovery |

Overall repaired-comparator status: `repaired_comparator_matches_direct_s3`.

## Legacy Denominator Effect

| Month | Extra bbox-only scenes | Extra invalid/no-data observations | Effect status | Wetness effect |
| --- | ---: | ---: | --- | --- |
| 2022-11 | 4 | 375748 | bbox_only_denominator_effect_confirmed | denominator_only |
| 2024-12 | 3 | 281811 | bbox_only_denominator_effect_confirmed | denominator_only |

For both overlapping months, the extra invalid/no-data observations equal the bbox-only scene count multiplied by the support-mask pixel count. Wet area, wet proportion, wet/dry observation counts, valid support area, quality flag, and wet-month flag are unchanged.

## Recommendation For Goal 016

Scale cautiously from the repaired path-row-filtered comparator baseline. The next bounded step should expand either all supports across the same three probe months or `NWB002` across the full event window, but it should not use legacy bbox-only denominator rows as the validation baseline.
