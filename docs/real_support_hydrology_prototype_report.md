# Real-Support Hydrology Prototype Report

## Purpose

Goal 005 computed bounded monthly DEA Water Observations metrics over documented
official Ramsar supports for the five Goal 004 candidates. It differs from Goal
004 by using real support masks and aggregating every readable Water
Observations scene in each target month, rather than choosing one clear 3x3
probe-pixel scene.

This is hydrology-support prototype evidence only. It is not bird-response,
breeding, abundance, refuge, or ecological-role analysis.

## Compute Decision

The prototype ran locally on the Mac mini. No compute-routing memo was needed:
the raw Ramsar subset was 497145 bytes, the fresh validation run completed in
72.884 seconds, and the largest reference grid was Currawinya Lakes at
3388770 cells with 1676254 support-mask pixels, below the configured
5000000-cell local stop threshold.

## Workflow

Executable files:

- [../scripts/official_support_hydrology_005.py](../scripts/official_support_hydrology_005.py)
- [../settings/official_support_hydrology_005.json](../settings/official_support_hydrology_005.json)

Committed outputs:

- [official_support_geometry_summary.csv](official_support_geometry_summary.csv)
- [official_support_geometry_manifest.json](official_support_geometry_manifest.json)
- [real_support_hydrology_prototype_summary.csv](real_support_hydrology_prototype_summary.csv)
- [real_support_hydrology_prototype_manifest.json](real_support_hydrology_prototype_manifest.json)

Processing steps:

1. Query the DCCEEW Geospatial Ramsar Wetlands service for the five candidate
   REFCODEs.
2. Stage the returned raw GeoJSON subset only under ignored `artifacts/`.
3. Union Ramsar components by candidate support and rasterize each support to a
   30 m `EPSG:3577` reference grid.
4. Query DEA STAC for `ga_ls_wo_3` items intersecting each support/month.
5. Warp every readable Water Observations scene to the support grid with
   nearest-neighbour resampling.
6. Decode the Water Observations bit field into monthly base metrics and
   quality flags.

## Results

The run produced 15 hydrology rows: five supports by the three Goal 004 months
(`2019-01`, `2022-11`, `2024-03`). All rows reached
`computed_real_support_metrics`.

| Candidate | 2019-01 wet proportion | 2022-11 wet proportion | 2024-03 wet proportion | Quality notes |
| --- | ---: | ---: | ---: | --- |
| NWB001 Macquarie Marshes | 0.000233 | 0.056122 | 0.002158 | All months `quality_minimum`; Ramsar/floodplain caveat remains. |
| NWB002 Narran Lake Nature Reserve | 0.000000 | 0.214966 | 0.067097 | All months `quality_high`; lignum/floodplain caveat remains. |
| NWB003 Gwydir Wetlands | 0.001032 | 0.019048 | 0.004055 | All months `quality_minimum`; Ramsar parcels are narrow supports. |
| NWB004 Kerang Wetlands | 0.309072 | 0.738985 | 0.466819 | 2022-11 is `quality_fail` because clear-observation fraction was too low. |
| NWB005 Currawinya Lakes | 0.000154 | 0.051861 | 0.023988 | All months `quality_high`; whole-complex subunit split is deferred. |

## Metrics Computed

For every support/month row, the prototype computed the Goal 003 base monthly
fields where readable scenes were available:

- `n_scene_m`
- `n_pixel_u`
- `clear_obs_count`
- `invalid_obs_count`
- `clear_obs_fraction`
- `current_wet_area_m2`
- `valid_support_area_m2`
- `current_proportion_wet`
- wet and dry pixel-observation counts
- per-bit invalid counts
- quality flag
- wet-month flag

The support IDs are official-support IDs such as `nwb001_ramsar_ref337`; no
Goal 004 `*_probe_3x3` support IDs are used.

## Deferred Metrics

Lag, novelty, drying velocity, hydroperiod persistence, and regional water
availability remain deferred. They require a longer monthly series and a
settled set of regional peer supports.

DEA Waterbodies open-water subunits also remain deferred. They should be used
next to split multi-lake and open-water supports, not to replace vegetated or
diffuse Ramsar/floodplain supports.

## Caveats

Water Observations may under-detect inundation in vegetated or mixed
water/vegetation pixels. This is especially important for Macquarie Marshes,
Narran lignum/floodplain habitat, and Gwydir wetland vegetation.

Ramsar supports are official and reproducible, but they are not final
ecological wetland-response units. They are anchors for this hydrology-only
prototype.

The Kerang 2022-11 row has high wet proportion but fails the configured
minimum quality rule because the clear-observation fraction is below 0.20.
That row should be retained as evidence, not interpreted as a robust wetness
estimate.

## Conclusion

Goal 005 proves that official Ramsar supports can be staged reproducibly and
used for bounded monthly Water Observations metrics on the local Mac mini. The
project is ready for a next hydrology-only goal that adds subunit geometry,
especially DEA Waterbodies or official lake-level components, before any
biodiversity download or ecological interpretation.
