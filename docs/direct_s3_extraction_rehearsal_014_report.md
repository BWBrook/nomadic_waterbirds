# Goal 014 Direct S3 Extraction Rehearsal

Accessed date: `2026-05-31`.

## Scope

This bounded rehearsal computed base DEA Water Observations metrics for `NWB002` Narran Lake Nature Reserve only, using direct public S3 COG reads for the Goal 013 derived path/rows `092/081`, `093/080`, and `093/081` in `2018-01`, `2022-11`, and `2024-12`.

No full `2018-01` through `2024-12` extraction, all-support extraction, biodiversity analysis, or derived time-history hydrology metrics were run.

## Item-Set Validation

Item-set status: `matched_goal013_item_sets`.

| Month | Direct S3 Water Observations item count |
| --- | ---: |
| 2018-01 | 9 |
| 2022-11 | 11 |
| 2024-12 | 11 |

The direct-S3 item counts and hashes were checked against Goal 013 before raster reads.

## Direct-S3 Base Metrics

| Month | Readable scenes | Clear obs | Invalid obs | Wet area m2 | Wet proportion | Quality |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2018-01 | 9 | 624647 | 220786 | 437.142883 | 5e-06 | quality_high |
| 2022-11 | 11 | 697574 | 335733 | 18173724.0 | 0.214966 | quality_high |
| 2024-12 | 11 | 903165 | 130142 | 4356122.5 | 0.051526 | quality_high |

The `2018-01` row is a bounded rehearsal metric for a month previously recorded as endpoint-blocked in Goal 009, not recovery of the full historical window.

## Comparison

| Month | Target | Status | Differing fields | Recommendation |
| --- | --- | --- | --- | --- |
| 2018-01 | goal009_full_window_status_row | new_direct_s3_rehearsal_row_for_endpoint_blocked_month |  | record as bounded rehearsal evidence only; not full-window recovery |
| 2022-11 | goal007_event_window_stac_metrics | mismatch_beyond_tolerance | readable_scene_count;invalid_obs_count;clear_obs_fraction | do_not_scale; first build a path-row-filtered STAC or no-data-adjusted comparator baseline |
| 2024-12 | goal007_event_window_stac_metrics | mismatch_beyond_tolerance | readable_scene_count;invalid_obs_count;clear_obs_fraction | do_not_scale; first build a path-row-filtered STAC or no-data-adjusted comparator baseline |

Overall comparison status: `overlap_mismatch_beyond_tolerance`.

For overlapping months, current wet area, current wet proportion, wet observation count, dry observation count, valid support area, and quality flag are the fields that matter most for base wetness equivalence. The strict comparison also includes observation-denominator fields such as readable scene count, invalid observations, and clear-observation fraction.

Where the strict comparison differs, the manifest records whether the pattern is consistent with legacy STAC bbox-only no-data scenes that are outside the Goal 013 support-derived path/row set.

## Recommendation For Goal 015

do_not_scale; run a comparator-baseline repair goal before full-window direct S3 extraction.
