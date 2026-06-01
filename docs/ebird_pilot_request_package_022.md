# eBird Pilot Request Package 022

## Purpose Statement For Barry Review

We seek a bounded eBird Basic Dataset extract to test whether complete
checklists can support effort-aware hydrological reaction-norm analyses for
Australian nomadic waterbirds. The pilot will link complete-checklist
observation units to monthly hydrology support rows from the existing
Goal 019/020 DEA Water Observations layer. The analytical intent is occurrence
/ non-detection and relative-count design, not absolute abundance estimation.

No request is submitted in Goal 022.

## Requested Product Route

Primary product route: eBird Basic Dataset request for raw observations plus
the sampling-event/effort metadata needed to identify complete checklists and
model observation effort.

Do not substitute the eBird Observational Dataset or GBIF route for the pilot:
official eBird documentation describes that occurrence route as lacking
sampling-event metadata such as effort.

## Spatial And Temporal Scope

Temporal scope:

- observation dates from `2018-01-01` through `2024-12-31`;
- downstream monthly join to Goal 020 hydrology month labels;
- no cross-month carry-forward before an explicit lag model is defined.

Spatial scope:

- current Goal 020 support set:
  - `nwb001_ramsar_component_359`
  - `nwb001_ramsar_ref337`
  - `nwb002_ramsar_ref1291`
  - `nwb003_ramsar_component_121`
  - `nwb003_ramsar_ref993`
  - `nwb004_ramsar_component_354`
  - `nwb004_ramsar_component_369`
  - `nwb004_ramsar_ref265`
  - `nwb005_dea_waterbody_r4ysdndx8_v3`
  - `nwb005_dea_waterbody_r4yss38r6_v3`
  - `nwb005_ramsar_ref791`
- request text should describe the corresponding named wetland complexes and
  states rather than attaching or generating a new geometry export in this
  goal;
- later ingestion must assign checklist locations to `support_id` using a
  documented, privacy-aware rule.

## Species And Guild Scope

Use the Goal 021 candidate screen as a provisional review screen only:

- include recommended-pilot guilds as request-screen candidates;
- keep `candidate` and `needs_lab_leader_decision` rows visible for review;
- do not lock a final species list or final guild membership in the request
  package;
- treat colonial breeding evidence separately from foraging/occurrence
  response layers.

## Required eBird Field Groups

The field-level request and ingestion needs are listed in
[ebird_required_fields_022.csv](ebird_required_fields_022.csv).

Minimum required groups:

- checklist/event identifiers;
- observation identifier and taxon fields;
- date and time fields;
- complete-checklist flag;
- protocol and birding-primary-purpose indicators where available;
- duration, distance, party size, and effort-area or effort-distance metadata;
- count or count code;
- latitude/longitude or provider-approved spatial precision fields;
- locality, region, country/state, and location metadata;
- sensitive-species or suppression/generalisation indicators;
- reviewed/validity/category fields needed to respect eBird quality control;
- licence, citation, request ID, and data-version provenance.

## Inclusion Rules

Include in future pilot processing only if:

- checklist is complete under eBird's complete-checklist definition;
- observation date falls inside `2018-01-01` to `2024-12-31`;
- location can be assigned to a Goal 020 support or an explicit support-level
  privacy bucket;
- required effort metadata are present for the intended response layer;
- record is usable under eBird's purpose-specific terms and sensitive-species
  rules;
- hydrology row is `core_eligible` or `core_eligible_with_caveat` for core
  analyses.

## Exclusion Or Risk Flags

Flag or exclude before core modelling:

- incomplete or incidental checklists;
- missing duration, distance, party size, protocol, or complete-list status;
- private, hidden, sensitive, or spatially generalised records that cannot be
  assigned safely to a support;
- ambiguous support assignment near support boundaries;
- repeated submissions or shared checklists that require deduplication;
- counts that are `X`/present-only or otherwise not comparable as counts;
- hydrology rows classified as `sensitivity_only`;
- any row lacking licence or request-provenance context.

## Expected Future Derived Tables

Do not create these tables in Goal 022. A later approved intake goal should
derive:

- checklist-level observation units;
- species/guild by checklist detections and non-detections;
- support-month coverage table;
- effort and sampling-density diagnostics;
- duplicate/shared-checklist audit;
- sensitive-record support assignment audit;
- hydrology join QA table.

## Submission Notes

Barry should review and, if approved, submit the request outside Goal 022 using
his own eBird account. The request should state that raw eBird data will remain
private to authorised users, will not be redistributed, will be cited, and will
be used only for the described non-commercial research purpose.
