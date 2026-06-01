# Goal 021 Bird Observation Linkage Design and Access Protocol

## Purpose

This packet defines a first constrained, observation-design lane that links
officially documented biodiversity streams to the Goal 020 hydrology-ready
support-month table for prototype interpretation work only. No biodiversity data
have been downloaded, requested, or processed in this goal.

## Decision Recommendation

**First constrained lane:** eBird complete-checklist records should be the primary
pilot lane, because it is the best-supported source of effort-aware observation
structure for non-detection and relative-count response formulations, while
respecting effort covariates and sensitivity restrictions.

**Recommended status:** `ready_for_bird_data_access_feasibility` with the
following explicit caveat:

- No core hydrology inference should use Goal 020 `sensitivity_only` rows (23 support-months); they are retained for sensitivity and coverage reporting only.
- Four comparator-audit rows from Goal 018 stay in the table and must be treated as
  caveated (`caveat_code` includes `legacy_stac_comparator_not_obtained`) with
  explicit sensitivity checks before interpretation.

## Scope Carried Forward From Goal 020

- Carry forward 924-row hydrology support-month readiness table.
- Use only `core_eligible` and `core_eligible_with_caveat` rows for core linkage
  formulations.
- Retain all 23 `quality_fail` (`sensitivity_only`) rows visible for reporting.
- Keep the four Goal 018 comparator-caveat rows as caveat rows, never dropped.
- Keep design and protocol at the `support_id × month` grain for now.

## Proposed First Linkage Architecture

We define each proposed observation unit as an `(observation_unit, support_id, month)`
join target with stream-specific pre-processing rules. Candidate streams remain role-specific:

- **eBird complete checklists**: primary lane for occurrence/non-detection and
  relative-count proxy.
- **Birdata 2 ha 20 minute standardised records**: secondary lane for calibration/sensitivity and possible validation.
- **ALA**: supplementary presence/context lane (taxonomy, range, historical context),
  never non-detection.
- **EAWS**: independent validation lane for breeding and abundance-direction evidence
  where rights and fields permit.

## Hydrology Join Contract

The machine-readable file
[`bird_hydrology_join_contract_021.csv`](bird_hydrology_join_contract_021.csv)
holds lane-level rules for spatial and temporal joins, eligibility by hydrology
class, forbidden uses, and validation checks. In brief:

- `support_id` and `month` are the hydrology key for all lanes.
- Core lane joins:
  - stream observations assigned to one or more `support_id` polygons;
  - month alignment to the hydrology month for all analyses;
  - required use only of `core_eligible` / `core_eligible_with_caveat`;
  - `quality_fail` rows are excluded from core fitting.
- Sensitivity reporting joins:
  - `sensitivity_only` rows may be retained for coverage summaries and method
    limitations discussion only.

## Observation-Grain and Response Layer Separation

Response-layer contracts are explicit and non-overlapping:

1. **Occurrence / non-detection layer**
   - lane: eBird complete-checklist complete lists and explicitly observed absences.
2. **Relative count / abundance proxy layer**
   - lane: eBird checklist totals and effort-linked counts; Birdata where permitted.
3. **Breeding evidence layer**
   - lane: targeted breeding-confirmed fields (Birdata/EAWS if available).
4. **Validation-only layer**
   - lane: ALA occurrence context, EAWS independent checks and non-core diagnostics.

Each layer should be declared separately in downstream model code and not collapsed
into a single response type.

## Provisional Candidate Species/Guild Screen

The initial screening table
[`candidate_species_guild_screen_021.csv`](candidate_species_guild_screen_021.csv)
contains provisional, reviewable choices (`status` = `recommended_pilot`,
`candidate`, `defer`, `needs_lab_leader_decision`), with each row intentionally
marked as non-final.

Highlights:

- Pilot lane candidates prioritise taxa with stronger checklist structure and
  broad wetland-state contrast in pilot regions.
- Colonial breeders are carried separately from short-visibility foraging taxa.
- Coastal/tidal/tolerantly detected taxa are tagged as `needs_lab_leader_decision`
  unless explicit tide/route controls are agreed.

## Access Protocol and Permission Controls

The protocol file
[`biodiversity_data_access_protocol_021.md`](biodiversity_data_access_protocol_021.md)
documents request questions and permission checks for each stream.
It is intentionally process-first, so no protected/ private data access is implied.

## Governance Controls Added in this Goal

- Explicitly prohibits:
  - using ALA as an absence source;
  - treating geospatially coarse or sensitive-suppressed records as exact
    non-detection points for core layers;
  - fitting any models from this goal outputs.
- Retains raw data restrictions:
  - no biodiversity records are committed in this goal.
- Leaves all four streams and candidate rows explicitly provisional.

## Gate and Recommendation

Goal 021 satisfies constrained design readiness for the next access/funding and
feasibility steps.

Recommended next step: launch a focused access-feasibility or data-request prep goal
that requests, at minimum, a small pilot eBird/Birdata scope after the permission
questions in this protocol are approved.
