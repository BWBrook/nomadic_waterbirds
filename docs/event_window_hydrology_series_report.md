# Event-Window Hydrology Series Report

## Purpose

Goal 007 extended the parent/subunit hydrology prototype from three selected
months to a bounded monthly event-window series. The series computes Goal 003
base monthly Water Observations metrics plus first-pass time-history fields
needed for later reaction-norm design.

This is hydrology-support and time-history evidence only. It is not ecological
modelling and does not make claims about bird abundance, breeding, refuge value,
or nomadic response.

## Compute Decision

The default `2018-01` through `2024-12` event window was probed first. The run
took roughly ten minutes before reaching support 2 of 13, making the full
local run likely to challenge the two-hour Goal 007 threshold, especially with
large Currawinya parent geometry still ahead.

The committed series therefore uses the documented fallback event window
`2020-01` through `2024-12` inclusive. This retains the 2022 wet/flood period,
recent post-wet conditions, and enough monthly history for 1-month and
3-month lags, trailing wetness, 12-month cumulative wet-month counts,
consecutive wet/dry metrics, novelty flags, and drying velocity. No
compute-routing memo was needed because the fallback completed locally in
2476.313 seconds.

## Workflow

Executable files:

- [../scripts/event_window_hydrology_007.py](../scripts/event_window_hydrology_007.py)
- [../settings/event_window_hydrology_007.json](../settings/event_window_hydrology_007.json)

Committed outputs:

- [named_subunit_crosswalk.csv](named_subunit_crosswalk.csv)
- [named_subunit_evidence_manifest.json](named_subunit_evidence_manifest.json)
- [event_window_hydrology_series.csv](event_window_hydrology_series.csv)
- [event_window_hydrology_summary.csv](event_window_hydrology_summary.csv)
- [event_window_hydrology_series_manifest.json](event_window_hydrology_series_manifest.json)

The workflow stages raw Ramsar, DEA Waterbodies, and WetlandInfo KMZ inputs
only under ignored `artifacts/` paths, builds the support crosswalk, processes
monthly DEA Water Observations scenes over each included support, and appends
time-history metrics.

## Series Coverage

The series contains 660 support-month rows: 11 included supports by 60 months.
Of these, 659 rows reached `computed_event_window_metrics`. One row,
`nwb004_ramsar_ref265` in `2023-01`, is retained as
`blocked_event_window_processing_error` after a read timeout.

Quality summary across all rows:

| Quality flag | Rows |
| --- | ---: |
| `quality_high` | 271 |
| `quality_minimum` | 307 |
| `quality_fail` | 82 |

## Derived Metrics

The script computed these first-pass time-history fields for every row:

- `wet_area_lag_1m`
- `wet_prop_lag_1m`
- `wet_area_lag_3m`
- `wet_prop_lag_3m`
- `wet_prop_trailing_3m`
- `wetting_delta_1m`
- `wetting_delta_3m`
- `novel_after_dry_flag`
- `dry_spell_length_prior`
- `cumulative_wet_months_12m`
- `consecutive_wet_months`
- `consecutive_dry_months_prior`
- `drying_velocity_1m`
- `drying_velocity_3m`

Regional water availability remains deferred. It needs a reviewed regional peer
support design and should not be inferred from this bounded support set alone.

## Compact Summary

| Support | Computed months | Blocked months | Quality fail months | Wet months | Max wet proportion | Max wet month | Novel-after-dry count |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Macquarie Marshes parent | 60 | 0 | 6 | 1 | 0.056122 | 2022-11 | 1 |
| Macquarie Marshes Nature Reserve | 60 | 0 | 6 | 1 | 0.055790 | 2022-11 | 1 |
| Narran Lake Nature Reserve parent | 60 | 0 | 0 | 38 | 0.279118 | 2020-03 | 4 |
| Gwydir Wetlands parent | 60 | 0 | 14 | 3 | 0.148435 | 2022-10 | 1 |
| Old Dromana | 60 | 0 | 13 | 1 | 0.102340 | 2022-10 | 0 |
| Kerang Wetlands parent | 59 | 1 | 21 | 39 | 0.629713 | 2023-02 | 0 |
| Reedy Lake | 60 | 0 | 4 | 56 | 0.748615 | 2022-11 | 0 |
| Lake Charm | 60 | 0 | 15 | 45 | 0.834917 | 2020-08 | 0 |
| Currawinya Lakes parent | 60 | 0 | 0 | 11 | 0.105288 | 2020-03 | 4 |
| DEA Waterbody `r4yss38r6_v3` | 60 | 0 | 0 | 58 | 0.568273 | 2020-05 | 0 |
| DEA Waterbody `r4ysdndx8_v3` | 60 | 0 | 3 | 51 | 0.988500 | 2020-08 | 2 |

## Interpretation Boundaries

The event-window series demonstrates that lag, novelty, drying, and
hydroperiod-style fields can be produced over reviewed parent/subunit supports.
Quality-fail and timeout rows are preserved rather than interpolated.

The series should not be read as final ecological evidence. Ramsar parent
supports remain official anchors, Ramsar components remain official but narrow
subunits, DEA Waterbodies remain open-water screens, and Narran named subunits
remain unresolved until stronger geometry is verified.

## Conclusion

Goal 007 produces a reviewable event-window hydrology series with explicit
time-history metrics and a clearer named-subunit evidence crosswalk. The next
step should decide whether to scale the full 2018-2024 event window on a larger
machine or keep the fallback window while preparing biodiversity-access and
validation design.
