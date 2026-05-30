# Hydrology Smoke Test Report

## Purpose

Goal 004 tested whether the project can execute a tiny hydrology-only path from
public DEA metadata to Water Observations pixel values without downloading
biodiversity data or committing raw source products.

This is not ecological analysis. The probe windows are tiny analyst-chosen
3x3-pixel AOIs used only to test access, bit-field decoding, provenance, and
summary-table shape.

## Compute Decision

The smoke test ran locally on the Mac mini. No compute-routing memo was needed:
the run streamed small public STAC responses and 3x3-pixel GDAL reads from DEA
Cloud-Optimized GeoTIFFs, completed in 40.383 seconds, and created no raw
source files.

## Workflow

Executable files:

- [scripts/hydrology_smoke_test_004.py](../scripts/hydrology_smoke_test_004.py)
- [settings/hydrology_smoke_test_004.json](../settings/hydrology_smoke_test_004.json)

Committed outputs:

- [hydrology_smoke_test_manifest.json](hydrology_smoke_test_manifest.json)
- [hydrology_smoke_test_summary.csv](hydrology_smoke_test_summary.csv)

Access method:

1. Read the five `include_in_next_extraction_smoke=yes` candidates from
   [prototype_wetland_unit_crosswalk.csv](prototype_wetland_unit_crosswalk.csv).
2. Query the DEA STAC search endpoint for `ga_ls_wo_3` items near each tiny
   probe AOI for three target months.
3. Stream a 3x3 pixel window from each selected public Water Observations
   GeoTIFF through GDAL `/vsis3/`.
4. Decode the Water Observations bit field into clear, invalid, wet, dry, and
   quality fields.
5. Write only small manifest and summary files to `docs/`.

## Candidates Attempted

| Candidate | Months attempted | Status | Notes |
| --- | --- | --- | --- |
| NWB001 Macquarie Marshes | 2019-01, 2022-11, 2024-03 | Computed tiny-probe metrics | Public STAC and COG path worked. Probe AOI is not an official marsh mask. |
| NWB002 Narran Lake Nature Reserve | 2019-01, 2022-11, 2024-03 | Computed tiny-probe metrics | Public STAC and COG path worked. Probe AOI is not a lake/floodplain mask. |
| NWB003 Gwydir Wetlands | 2019-01, 2022-11, 2024-03 | Computed tiny-probe metrics | Public STAC and COG path worked. Probe AOI is not a broader Gwydir wetland mask. |
| NWB004 Kerang Wetlands | 2019-01, 2022-11, 2024-03 | Computed tiny-probe metrics | Public STAC and COG path worked. Probe AOI is not a named-lake subunit. |
| NWB005 Currawinya Lakes | 2019-01, 2022-11, 2024-03 | Computed tiny-probe metrics | Public STAC and COG path worked. Probe AOI is not a Lake Numalla/Lake Wyara mask. |

## Metrics Computed

For each candidate/month row, the smoke test computed:

- STAC item count and selected Water Observations asset
- 3x3 support area
- clear and invalid observation counts
- clear observation fraction
- current wet area and valid support area
- current proportion wet
- wet and dry pixel counts
- invalid bit counts for no data, contiguity, low solar angle, terrain shadow,
  high slope, cloud shadow, and cloud
- quality flag
- wet-month flag

The run produced 15 rows: 5 candidates x 3 months. All 15 rows reached
`computed_tiny_probe_metrics` and `quality_high`.

## Metrics Deferred

These fields from [hydrology_metric_spec.md](hydrology_metric_spec.md) remain
deferred until real candidate masks or subunits exist:

- one-month and three-month lags
- trailing three-month wetness
- cumulative and consecutive wet months
- wetting novelty after dry spells
- drying velocity
- regional water availability and scarcity indices
- Waterbodies overlap/subunit summaries

Those metrics need official wetland masks or documented subunits, not
analyst-chosen 3x3 probe windows.

## Raw Data And Cleanup

Ignored staging paths:

- `data/scratch/goal004/`
- `artifacts/hydrology_smoke/raw/`
- `artifacts/hydrology_smoke/intermediate/`
- `artifacts/hydrology_smoke/output/`

No raw source files were downloaded. The ignored staging directories exist but
contain no files. The committed manifest records an empty `staged_raw_files`
array and empty `staged_file_sizes_bytes` object.

## Conclusion

The project is ready for a fuller hydrology prototype that stages official
geometry or masks in ignored paths and computes monthly Water Observations
metrics for real candidate supports. The next step should still be
hydrology-only and should not introduce biodiversity data.

The smoke test proves:

- DEA STAC search is reachable locally.
- Public Water Observations assets can be opened through GDAL `/vsis3/`.
- Tiny Water Observations windows can be decoded into the metric-spec base
  fields.
- Provenance can be captured in a small manifest without committing raw source
  data.

It does not prove:

- that Ramsar or ecological wetland boundaries are correct supports
- that DEA Waterbodies overlap is adequate
- that vegetated floodplain inundation is captured well
- that any bird-response or ecological role claim is supported
