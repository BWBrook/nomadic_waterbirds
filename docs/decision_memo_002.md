# Decision Memo 002 - Data Access And Wetland Unit Feasibility

## Recommendation

Proceed to a small MDB/eastern-inland prototype using a hybrid wetland-unit
strategy.

The prototype should use named wetland complexes for interpretation, DEA
Water Observations for authoritative hydrological metrics, DEA Waterbodies v3
as open-water subunits where appropriate, and Geofabric for hydrological
context and blocking. Biodiversity streams should remain access-gated until
their request and reuse terms are satisfied.

## Rationale

The current official sources support hydrology-first progress. DEA Water
Observations is current, national, long-running, event-scale, and openly
licensed [S01]. DEA Waterbodies v3 gives a practical way to test open-water
subunits quickly, but its own documentation makes clear that wet surface area
is not depth, volume, or full ecological wetland function [S03]. Named wetland
sources are interpretable but have age, boundary, and licensing caveats [S19,
S20, S21]. The strongest prototype is therefore a comparison, not a premature
final unit choice.

The biodiversity streams are credible but not yet operational. eBird EBD is
request-based and purpose-specific [S05, S06]. Birdata extracts require
BirdLife approval and may not be redistributed [S09]. EAWS has strong
validation value and a public database surface, but export and reuse
permissions still need inspection [S14]. ALA is useful for taxonomy and
presence context, but provider terms and sensitivity constraints rule out using
it as an absence stream [S11, S12].

## Alternatives Considered

1. Use DEA Waterbodies as the sole wetland-unit layer.
   - Rejected for now because it may omit vegetated or diffuse floodplain
     habitat important to waterbirds [S03].
2. Use only named DIWA/Ramsar polygons.
   - Rejected for now because DIWA is stale and boundary/current-condition
     authority needs checking [S19, S20].
3. Use grid cells as the only spatial support.
   - Rejected for now because grid cells are hydrologically powerful but weak
     for management-facing wetland roles.
4. Begin with eBird or Birdata extraction.
   - Deferred because access requests and terms must be handled before data
     ingestion [S05, S06, S09].

## Decisions Made

- Use DEA Water Observations as the first hydrology authority.
- Use DEA Waterbodies v3 only as a prototype subunit/screening layer, not as
  the final wetland-unit system.
- Use named wetland complexes as interpretation/reporting units, with explicit
  geometry and boundary uncertainty.
- Keep eBird, Birdata, and EAWS outside the repo until request, export, and
  reuse terms are recorded.
- Treat ALA as taxonomy/presence context only, not an absence or trend stream.

## Unresolved Risks

- eBird access approval and reuse constraints for the exact project purpose.
- Birdata access, inclusion of eBird-imported surveys, and raw/derived sharing
  restrictions.
- EAWS public database exportability and permission for project-scale reuse.
- Whether DEA Waterbodies adequately covers the floodplain/vegetated wetland
  components of candidate prototype sites.
- Whether DIWA/Ramsar/CAPAD geometries align well enough with DEA rasters and
  biodiversity records.
- Sensitive species and location handling across all biodiversity streams.

## Recommended Goal 003

Create a prototype wetland-unit crosswalk and hydrology metric specification
for a small MDB/eastern-inland pilot. Goal 003 should:

- identify a handful of candidate named wetland complexes from official sources
- record official geometry, licence, and boundary caveats
- test overlap with DEA Waterbodies geohashes and define where Water
  Observations raster summaries are required
- specify monthly hydrology metrics and invalid-observation rules
- inspect public EAWS/eBird/Birdata/ALA feasibility surfaces without submitting
  requests or downloading bulk biodiversity data
