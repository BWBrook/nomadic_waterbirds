# Decision Memo 003 - Prototype Crosswalk And Hydrology Metric Contract

## Recommendation

Proceed to a small executable hydrology extraction smoke test in Goal 004.

Use the 5 smoke-test candidates in
[prototype_wetland_unit_crosswalk.csv](prototype_wetland_unit_crosswalk.csv):
Macquarie Marshes, Narran Lake Nature Reserve, Gwydir Wetlands, Kerang
Wetlands, and Currawinya Lakes. Keep the Coorong/Lower Lakes and Coongie Lakes
as deferred edge comparators.

## Rationale

The candidate set is now structured enough for an extraction smoke test:

- official named-source pages are recorded for each candidate
- geometry source and licence caveats are visible
- DEA Waterbodies support is classified as screening/subunit support, not final
  habitat support
- Water Observations summary needs are stated per candidate
- Geofabric context and public biodiversity/EAWS alignment surfaces are
  recorded without downloading biodiversity data
- monthly hydrology metrics and minimum quality flags are specified in
  [hydrology_metric_spec.md](hydrology_metric_spec.md)

## Decision

Goal 004 may perform a small hydrology-only extraction smoke test if it:

- uses only public DEA/official spatial data needed for the 5 smoke-test
  candidates
- writes raw source files only to ignored local paths
- commits only small derived summaries, manifests, and documentation
- does not request or download eBird, Birdata, ALA, or EAWS biodiversity data
- reports Water Observations validity, Waterbodies overlap, and geometry
  caveats before any biological analysis

## Alternatives Considered

1. Include all 7 candidates in the first extraction.
   - Deferred because Coorong/Lower Lakes and Coongie Lakes are large edge
     cases that may dominate first-pass complexity.
2. Use only DEA Waterbodies time series.
   - Rejected because vegetated and diffuse floodplain wetlands would be
     underrepresented.
3. Start with one wetland only.
   - Rejected because the first smoke test needs enough contrast to expose
     crosswalk and metric problems across floodplain, terminal, open-lake, and
     arid systems.

## Residual Risks

- Official Ramsar boundaries may not match ecological wetland complexes.
- DEA Water Observations may underestimate mixed vegetated wetland inundation.
- DEA Waterbodies overlap may be weak for Gwydir, Macquarie, and other
  floodplain units.
- Geofabric basin/context joins remain untested.
- Public EAWS database and eBird/Birdata access constraints remain unresolved
  for later biodiversity goals.

## Recommended Goal 004

Run a hydrology-only extraction smoke test for the 5 included candidates.
Goal 004 should create an ignored local scratch area, fetch only the minimum
public official geometry/product slices needed, derive candidate/support
manifests and 2-3 monthly Water Observations summaries for selected contrasting
months, validate the metric contract, and commit only small provenance,
manifest, and summary documentation.
