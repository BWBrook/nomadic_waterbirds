# Hydrology Metric Specification

## Purpose

This specification defines the monthly hydrology metrics for a later executable
smoke test. It uses DEA Water Observations (Landsat) as the authoritative
source for dynamic wet/dry metrics and treats DEA Waterbodies as an optional
subunit/screening layer.

No hydrology data were extracted for Goal 003.

## Source Product

Primary product:

- DEA Water Observations (Landsat), `ga_ls_wo_3`
- 30 m raster observations from Landsat 5, 7, 8, and 9
- coverage from 16 August 1986 to present
- bit-field values encoding water and invalid-observation conditions [S01]

DEA Waterbodies v3 may be used to find open-water subunits and inspect
published waterbody time-series behaviour, but final monthly reaction-norm
metrics should be calculated from Water Observations over the selected wetland
support [S03].

## Spatial Supports

For each named wetland complex, calculate metrics for:

1. named-complex mask: the reporting and interpretation unit
2. candidate DEA Waterbodies subunits: open-water screening units, where
   geohashes overlap the named complex
3. optional analysis subunits: lake, marsh, or floodplain components where the
   official boundary and hydrology make a whole-complex summary misleading

Every metric table must include `candidate_id`, `support_id`, `support_type`,
`support_area_m2`, `source_geometry`, and `source_geometry_caveat`.

## Monthly Aggregation Window

Use calendar months in local date terms derived from observation acquisition
date. Retain the original observation dates so later goals can re-aggregate to
seasonal or event windows.

## Support-Relevant Scene Selection

For support-level monthly Water Observations metrics, first derive the WRS-2
path/rows whose official scene footprints intersect the support geometry. STAC
bbox searches may be used to discover candidate metadata, but monthly metrics
must count and summarise only scenes from those support-intersecting path/rows.

Bbox-only STAC hits outside the derived support path/row set must not be
counted as readable scenes, no-data observations, invalid observations, or
monthly denominator terms for that support. Each output row should record the
path/row set and enough item-set provenance to audit the scene-selection rule.

## Pixel Classification Rules

For each Water Observations pixel value:

- `water_bit = 128`
- invalid or caution bits:
  - no data: `1`
  - contiguity: `2`
  - low solar angle: `4`
  - terrain shadow: `8`
  - high slope: `16`
  - cloud shadow: `32`
  - cloud: `64`

For core monthly wet-area metrics:

- clear dry pixel-observation: value `0`
- clear wet pixel-observation: value `128`
- invalid pixel-observation: any value with one or more invalid/caution bits
  set, including combinations such as cloud plus water or cloud shadow plus
  water

Keep counts of each invalid bit class. Do not silently recode invalid water
combinations as wet.

## Monthly Base Metrics

For wetland support `u`, month `m`, pixel size `a = 900 m2`, and all Water
Observations scenes in that month:

- `n_scene_m`: number of observation dates intersecting the support.
- `n_pixel_u`: number of pixels in the support mask.
- `clear_obs_count`: count of pixel-observations with value `0` or `128`.
- `invalid_obs_count`: count of pixel-observations with invalid/caution bits.
- `clear_obs_fraction`: `clear_obs_count / (n_scene_m * n_pixel_u)`.
- `pixel_clear_count`: number of clear observations per pixel in the month.
- `pixel_wet_count`: number of clear wet observations per pixel in the month.
- `pixel_wet_fraction`: `pixel_wet_count / pixel_clear_count` for pixels with
  at least one clear observation.
- `current_wet_area_m2`: `sum(pixel_wet_fraction * a)` across pixels with at
  least one clear observation.
- `valid_support_area_m2`: `count(pixels with at least one clear observation)
  * a`.
- `current_proportion_wet`: `current_wet_area_m2 / valid_support_area_m2`.

Also record invalid-bit counts by class:

- `no_data_count`
- `contiguity_count`
- `low_solar_angle_count`
- `terrain_shadow_count`
- `high_slope_count`
- `cloud_shadow_count`
- `cloud_count`

## Lag Metrics

For each support:

- `wet_area_lag_1m`: `current_wet_area_m2` in the previous calendar month.
- `wet_prop_lag_1m`: `current_proportion_wet` in the previous calendar month.
- `wet_area_lag_3m`: `current_wet_area_m2` 3 calendar months before `m`.
- `wet_prop_lag_3m`: `current_proportion_wet` 3 calendar months before `m`.
- `wet_prop_trailing_3m`: mean `current_proportion_wet` over months `m-1` to
  `m-3`, excluding months failing minimum quality.

Keep the single-month lag and trailing 3-month summary separate.

## Hydroperiod And Cumulative Wet Months

Define a support as wet in month `m` when:

- the month passes minimum data quality, and
- `current_proportion_wet >= 0.05`, or a candidate-specific threshold is
  justified in the candidate metadata.

Derived metrics:

- `wet_month_flag`
- `cumulative_wet_months_12m`: count of wet months in the previous 12 months,
  including `m`
- `consecutive_wet_months`: run length of wet months ending at `m`
- `consecutive_dry_months_prior`: run length of dry months immediately before
  `m`

The 0.05 threshold is a prototype default, not a final ecological threshold.

## Wetting Novelty

Calculate:

- `wetting_delta_1m = current_proportion_wet - wet_prop_lag_1m`
- `wetting_delta_3m = current_proportion_wet - wet_prop_trailing_3m`
- `novel_after_dry_flag = current_proportion_wet >= 0.05 and
  consecutive_dry_months_prior >= 2`
- `dry_spell_length_prior = consecutive_dry_months_prior`

These metrics should identify newly wet basins after dry periods without
confusing novelty with permanent wetness.

## Drying Velocity

Calculate:

- `drying_velocity_1m = wet_prop_lag_1m - current_proportion_wet`
- `drying_velocity_3m = wet_prop_trailing_3m - current_proportion_wet`
- `rapid_drying_flag = drying_velocity_1m >= 0.10`, subject to later
  sensitivity review

Positive drying velocity means the support has become drier.

## Regional Water Availability

For each focal support, calculate regional water availability from the same
monthly Water Observations metrics over candidate peer supports.

Prototype regional supports:

- all candidate wetland supports within the same Geofabric basin or sub-basin
- candidate buffers around support centroids at 50, 100, and 250 km where
  geometry allows
- all smoke-test supports, excluding the focal support, as a first coarse
  scarcity index

Metrics:

- `regional_wet_area_m2`
- `regional_valid_area_m2`
- `regional_proportion_wet`
- `regional_support_count`
- `regional_scarcity_index = 1 - regional_proportion_wet`

Do not use regional water metrics until the included regional supports are
documented.

## Minimum Data-Quality Flags

Each support-month should carry:

- `quality_high`: at least 2 observation dates, at least 80% of support pixels
  clear at least once, and `clear_obs_fraction >= 0.40`
- `quality_minimum`: at least 1 observation date, at least 50% of support
  pixels clear at least once, and `clear_obs_fraction >= 0.20`
- `quality_fail`: does not meet `quality_minimum`
- `quality_large_waterbody_gap`: candidate Waterbodies subunit has missing
  daily observations under the Waterbodies 90% observed rule [S03]
- `quality_vegetated_wetland_caution`: candidate support contains known
  vegetated/mixed water pixels where Water Observations may underestimate
  inundation [S01]

Core analyses should use `quality_minimum` or better. Sensitivity checks should
repeat central summaries with `quality_high` only.

## Missingness Policy

- Do not interpolate wet area for the extraction smoke test.
- Preserve missing months and invalid-observation counts.
- Later models may represent missing hydrology with explicit missingness or
  observation-quality covariates, but this must be justified in a model-design
  goal.

## Output Table Contract

The later extraction smoke test should write one row per
`candidate_id`/`support_id`/month with all base, lag, novelty, drying,
regional, and quality fields above, plus provenance fields:

- `dea_product`
- `dea_product_version`
- `processing_date`
- `geometry_hash`
- `metric_spec_version`
- `notes`
