# Narran Named-Subunit Evidence Report

## Purpose

Goal 008 reviewed whether Narran named features can be promoted from
unresolved names to hydrology supports. The review deliberately separates
official names, approximate location evidence, vector geometry, DEA Waterbody
relationships, and event-window inclusion.

This is hydrology-support evidence only. It does not make bird abundance,
breeding, refuge, drought-response, or conservation-priority claims.

## Workflow

Executable files:

- [../scripts/narran_subunit_evidence_008.py](../scripts/narran_subunit_evidence_008.py)
- [../settings/narran_subunit_evidence_008.json](../settings/narran_subunit_evidence_008.json)

Committed outputs:

- [narran_named_subunit_crosswalk.csv](narran_named_subunit_crosswalk.csv)
- [narran_named_subunit_evidence_manifest.json](narran_named_subunit_evidence_manifest.json)

Raw source files were staged only under ignored paths:

| Staged file | Bytes | Commit status |
| --- | ---: | --- |
| `artifacts/narran_subunit_evidence/raw/ramsar_goal008_narran_subset.geojson` | 28523 | Not committed |
| `artifacts/narran_subunit_evidence/raw/ga_ls_wb_3_v3.zip` | 46502008 | Not committed |
| `artifacts/narran_subunit_evidence/raw/dcceew_narran_page.html` | 95756 | Not committed |
| `artifacts/narran_subunit_evidence/raw/AU995RIS_2207_en.pdf` | 663297 | Not committed |
| `artifacts/narran_subunit_evidence/raw/AU995_ECD160815.pdf` | 7045674 | Not committed |
| `artifacts/narran_subunit_evidence/raw/narran-lake-nature-reserve-draft-plan-of-management-250346.pdf` | 5009252 | Not committed |
| `artifacts/narran_subunit_evidence/raw/data_nsw_wetland_vegetation_narran_2024_25.html` | 119655 | Not committed |
| `artifacts/narran_subunit_evidence/raw/wetland_vegetation_narran_2024_25_data_quality.pdf` | 34117 | Not committed |

## Source Review

Reviewed official or primary public sources:

- DCCEEW Narran Lake Nature Reserve Ramsar page:
  <https://www.dcceew.gov.au/water/wetlands/australian-ramsar-wetlands/narran-lake-nature-reserve>
- Ramsar Information Sheet 2022:
  <https://rsis.ramsar.org/RISapp/files/RISrep/AU995RIS_2207_en.pdf>
- Narran Lake Nature Reserve ecological character description:
  <https://rsis.ramsar.org/RISapp/files/34152861/documents/AU995_ECD160815.pdf>
- NSW draft plan of management 2025:
  <https://www.environment.nsw.gov.au/sites/default/files/2025-09/narran-lake-nature-reserve-draft-plan-of-management-250346.pdf>
- Data.NSW Wetland Vegetation of Narran Lakes 2024-25:
  <https://www.data.nsw.gov.au/data/dataset/wetland-vegetation-of-narran-lakes-2024-25>
- DEA Waterbodies v3 public shapefile:
  <https://dea-public-data.s3.ap-southeast-2.amazonaws.com/derivative/dea_waterbodies/3-0-0/shapefile/ga_ls_wb_3_v3.zip>

The official sources verify the existence and hydrological context of Clear
Lake, Back Lake, Long Arm, and the lignum/channelised floodplain. The ECD also
provides approximate areas for Clear Lake, Back Lake, and Long Arm, but those
figures are not standalone vector geometry. The NSW 2024-25 vegetation product
is useful landscape-scale context, but its metadata and quality statement do
not make it a support-ready named subunit layer for this goal.

## Crosswalk Result

The crosswalk has 44 rows:

| Evidence class | Rows | Included in current event-window hydrology |
| --- | ---: | ---: |
| Official Ramsar parent support | 1 | 1 |
| Unresolved named/context candidates | 4 | 0 |
| DEA Waterbody parent-overlap screens | 39 | 0 |

The largest DEA Waterbody parent-overlap screens were:

| DEA UID | Parent overlap m2 | Fraction of parent | Fraction of DEA polygon |
| --- | ---: | ---: | ---: |
| `r68yg7gjm_v3` | 12692700.0 | 0.15013920 | 1.00000000 |
| `r68ye5u73_v3` | 602966.329 | 0.00713236 | 0.42162529 |
| `r68ygsx64_v3` | 273600.0 | 0.00323636 | 1.00000000 |
| `r68ygxm31_v3` | 74700.0 | 0.00088361 | 1.00000000 |
| `r68yu56km_v3` | 65160.143 | 0.00077077 | 0.99178300 |

These DEA rows are useful open-water screens. They do not prove that any UID is
Clear Lake, Back Lake, Long Arm, or lignum/channelised floodplain.

## Narran Decision

Narran remains parent-only for event-window hydrology:

- `nwb002_ramsar_ref1291` stays included as the official Ramsar parent support.
- `nwb002_named_clear_lake_unresolved` stays unresolved.
- `nwb002_named_back_lake_unresolved` stays unresolved.
- `nwb002_named_long_arm_unresolved` is added as unresolved.
- `nwb002_lignum_channelised_floodplain_unresolved` is added as unresolved
  vegetation/floodplain context.
- All 39 DEA Waterbody overlaps are retained as screens only, not named
  supports.

This is a stronger evidence state than Goal 007 because the unresolved status
now covers Long Arm, lignum/channelised floodplain context, current NSW
vegetation-map metadata, and explicit DEA parent-overlap screens. It still does
not justify named-subunit hydrology extraction for Narran.

## Conclusion

No public official or primary source reviewed in Goal 008 exposed defensible
standalone vector geometry or a verified DEA UID relationship for Clear Lake,
Back Lake, Long Arm, or the lignum/channelised floodplain. The honest support
decision is therefore to keep Narran as the official Ramsar parent support for
hydrology until a later source-geometry or digitisation goal can review a
support-ready subunit layer.
