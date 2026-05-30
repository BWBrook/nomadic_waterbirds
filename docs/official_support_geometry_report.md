# Official Support Geometry Report

## Purpose

Goal 005 moved the hydrology prototype from Goal 004's analyst-chosen 3x3
probe pixels to documented official wetland supports. This report records the
support source checked, what was staged, which support definitions were used,
and the candidate-level geometry caveats.

This is a support-geometry and hydrology-input step only. It is not a final
wetland-unit decision and it does not contain raw coordinates or committed
geometry files.

## Source Checked

The prototype used the DCCEEW Geospatial Ramsar Wetlands ArcGIS service:

- Ramsar service layer:
  `https://gis.environment.gov.au/gispubmap/rest/services/ogc_services/Ramsar_Wetlands/MapServer/0`
- Data.gov.au catalogue record:
  `https://www.data.gov.au/data/dataset/ramsar-wetlands-of-australia2`
- Service query staged for Goal 005:
  `REFCODE IN (337,1291,993,265,791)`, returned as GeoJSON in `EPSG:4326`.

The service exposed current official Ramsar records for all five Goal 005
candidates. The staged raw subset remains outside Git at:

```text
artifacts/hydrology_supports/raw/ramsar_goal005_subset.geojson
```

The staged file is 497145 bytes with SHA-256:

```text
3486b9639434995ee3d24eaa8b064860508288366b4a4a9d4741ed9988b63bd7
```

## Supports Used

| Candidate | Support ID | Support type | Components | Area ha | Status |
| --- | --- | --- | ---: | ---: | --- |
| NWB001 Macquarie Marshes | `nwb001_ramsar_ref337` | Official Ramsar named-complex union | 2 | 19303.728 | Included |
| NWB002 Narran Lake Nature Reserve | `nwb002_ramsar_ref1291` | Official Ramsar named-complex geometry | 1 | 8453.955 | Included |
| NWB003 Gwydir Wetlands | `nwb003_ramsar_ref993` | Official Ramsar named-complex union | 4 | 842.458 | Included |
| NWB004 Kerang Wetlands | `nwb004_ramsar_ref265` | Official Ramsar named-complex union | 14 | 9792.805 | Included |
| NWB005 Currawinya Lakes | `nwb005_ramsar_ref791` | Official Ramsar named-complex geometry | 1 | 150863.516 | Included |

Machine-readable details are in
[official_support_geometry_summary.csv](official_support_geometry_summary.csv)
and
[official_support_geometry_manifest.json](official_support_geometry_manifest.json).

## Candidate Caveats

Macquarie Marshes: the official Ramsar components are usable named-complex
anchors, but they may not cover the broader ecological floodplain relevant to
waterbirds and vegetated wetland dynamics.

Narran Lake Nature Reserve: the official Ramsar reserve boundary is usable, but
lake/open-water and lignum/floodplain habitats remain distinct subunit
questions.

Gwydir Wetlands: the official Ramsar parcels are much smaller than the broader
Gwydir wetland ecosystem, so these metrics should not be read as whole-system
hydrology.

Kerang Wetlands: the official Ramsar union preserves the named complex but
hides important lake-level heterogeneity across saline, freshwater, regulated,
deep-marsh, and tree-dominated components.

Currawinya Lakes: the whole Ramsar complex is large enough for this bounded
prototype, but later analysis should split Lake Numalla, Lake Wyara, springs,
and smaller waterholes before interpretation.

## Geometry Conclusion

Goal 005 established an executable official-support path for all five
candidates. The support registry is ready for bounded Water Observations
processing, with two limits carried forward:

- Ramsar boundaries are official governance/reporting supports, not necessarily
  final ecological wetland-response units.
- DEA Waterbodies open-water subunits remain useful but were not needed to
  replace the Ramsar supports in this run.
