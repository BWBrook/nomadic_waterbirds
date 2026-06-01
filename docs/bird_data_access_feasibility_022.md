# Goal 022 Bird Data Access Feasibility

## Purpose

This memo converts the Goal 021 linkage design into a request-prep package for
Barry's review. It does not submit any data request, use credentials, log into
services, download biodiversity records, or process private/gated bird data.

## Headline Recommendation

**Decision status:** `ready_for_ebird_request_review`.

The first access lane should be a bounded eBird complete-checklist pilot for
the current 11 Goal 020 hydrology supports and the `2018-01` through `2024-12`
hydrology window. The request must include the raw eBird observation product and
the sampling-event/effort metadata needed to distinguish complete checklists,
protocol, duration, distance, party size, location precision, and sensitive
record handling.

The eBird Observational Dataset/GBIF-style occurrence route is not sufficient
for the pilot because official eBird documentation says it lacks sampling-event
metadata such as effort. The pilot therefore needs the eBird Basic Dataset
request path, plus any associated sampling-event file or field group available
under current eBird data-access terms.

## Stream-Level Status

- **eBird complete checklists:** `request_ready` for Barry review/submission,
  with the field and scope restrictions in
  [ebird_pilot_request_package_022.md](ebird_pilot_request_package_022.md).
- **Birdata:** `needs_clarification`; use only after BirdLife Australia
  confirms requested fields, reuse/derivative terms, sensitive-record handling,
  and whether eBird-imported surveys are included.
- **EAWS:** `needs_clarification`; keep as independent validation or
  breeding/abundance-context evidence until UNSW/public-database fields, export
  rights, and wetland-to-`support_id` crosswalk rules are confirmed.
- **ALA:** `context_only`; use for taxonomy, range, historical occurrence
  context, provider provenance, and sensitivity checks only. ALA records must
  never support absence or non-detection inference.

The machine-readable decisions are in
[bird_data_access_matrix_022.csv](bird_data_access_matrix_022.csv).

## Official Source Checks

Goal 022 checked current official/public documentation only. The checks are
recorded as S56-S66 in [source_evidence_register.md](source_evidence_register.md).

Key access conclusions:

- eBird Basic Dataset is the correct raw-observation request product and is
  available to logged-in users after a data-request form. Current eBird
  documentation says the EBD is updated monthly and supplied with
  documentation.
- eBird data-use terms remain purpose-specific: raw data cannot be passed to
  another user or redistributed in original form, derived products should be
  sent back to eBird, and sensitive species require an additional appropriate
  use check.
- eBird complete checklists mean birding was the primary purpose and all
  identified species were reported to the best of the observer's ability; this
  supports non-detection design only with effort and observation-process
  covariates.
- Birdata official pages confirm request-form access, no public sharing of
  provided files unless approved, case-by-case treatment for exact locations of
  sensitive records, and duplicate risk where eBird and Birdata overlap.
- EAWS is a long-running annual aerial survey with flooding and breeding-site
  information, but public web visibility does not by itself settle export or
  reuse rights for analytical tables.
- ALA remains useful for occurrence/taxonomy/context, but data-provider terms,
  sensitive-data restrictions, and authentication requirements for sensitive or
  private data make it unsuitable for absence inference.

## Pilot Envelope

The request envelope is deliberately bounded:

- `2018-01-01` through `2024-12-31`;
- the 11 current Goal 020 hydrology supports;
- the Goal 021 provisional candidate guild screen only, not a final species
  list;
- complete-checklist and effort-aware response design only;
- core hydrology linkage restricted to `core_eligible` and
  `core_eligible_with_caveat` support-months.

The 23 `sensitivity_only` hydrology support-month rows remain visible for
coverage and sensitivity summaries and are excluded from core fitting. The four
Goal 018 caveat rows stay caveated and visible.

## Feasibility Decision

The eBird pilot is request-ready for review because the current official
documentation supports the product/field route needed for complete-checklist
and effort-aware design. It is not analysis-ready: no data have been requested
or received, and the downstream pipeline must still validate field availability,
licence terms, sensitive-record treatment, support assignment, duplicate logic,
and sampling-density adequacy.

## Recommended Next Step

Recommended Goal 023: a supervisor-reviewed eBird request-submission and
intake-staging design gate, including approval of the request text, species/guild
scope, spatial envelope, sensitive-record handling, and a no-raw-data-in-Git
staging plan before any request is submitted.
