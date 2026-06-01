# eBird Request Text 023

Goal 023 provides paste-ready text for Barry review. It does not send, finalise,
or automate an eBird request.

## Project Title

Hydrological reaction norms of Australia's nomadic waterbirds

## Short Purpose

We seek a bounded eBird Basic Dataset extract to test whether complete eBird
checklists with sampling-event and effort metadata can support observation-aware
hydrological reaction-norm analyses for Australian nomadic waterbirds.

## Detailed Description

This research examines how nomadic and wetland-dependent Australian waterbirds
respond to current wetness, lagged wetness, wetland persistence, drying,
wetting after dry periods, and regional water availability. The pilot links
complete eBird checklist observation units to an existing monthly hydrology
support table derived from Digital Earth Australia Water Observations.

The pilot is deliberately constrained. The requested observation window is
`2018-01-01` through `2024-12-31`. The spatial focus is the current Goal 020
hydrology support set for five eastern and inland wetland complexes:
Macquarie Marshes, Narran Lake Nature Reserve, Gwydir Wetlands, Kerang
Wetlands, and Currawinya Lakes. These correspond to 11 current hydrology
supports used in the project. The request does not expand the project to a
national analysis.

The analytical role of eBird is complete-checklist occurrence/non-detection and
effort-aware relative-count design. We are not treating opportunistic presence
records as absences, and we are not using the eBird Observational Dataset or
GBIF occurrence route as a substitute for sampling-event metadata.

Species and guild choices remain provisional and reviewable. The first screen
focuses on Australian waterbird species and guilds with plausible hydrological
responses, including waterfowl, grebes, cormorants/darters, herons/egrets,
ibis/spoonbills, pelicans, rails/coots, and separately treated colonial
breeding indicators where appropriate. No final species list or final guild
membership is locked by this request.

## Product And Field Needs

Please provide the eBird Basic Dataset raw observation product, with associated
sampling-event/checklist metadata needed to identify complete checklists and
model observation effort.

Required field groups include:

- checklist or sampling-event identifiers;
- observation identifiers;
- taxonomy fields and taxonomy-version context;
- observation date and, where available, start time;
- complete-checklist status;
- protocol or compatible observation-method fields;
- duration, distance, party size, number of observers, and other effort fields
  available for the checklist;
- count values or presence codes, preserving the distinction between numeric
  counts and present-only values;
- latitude/longitude or provider-approved spatial precision/location metadata;
- locality, region, state, and country fields;
- sensitive-species, hidden, private, or spatial-generalisation indicators
  where supplied and permitted;
- reviewed, validity, category, or quality-control status where supplied;
- request ID, data version, citation, and terms/version metadata.

## Sensitive Species And Location Handling

The project will respect eBird sensitive-species and location-suppression
rules. Sensitive or generalised records will not be published at restricted
site-level precision. If record precision is too coarse or restricted for safe
support assignment, those records will be routed to a support-level privacy
bucket or excluded from core fitting until an approved handling rule exists.

The request purpose requires enough sensitive-record metadata to determine
whether a record can be assigned to a Goal 020 support without breaching eBird
terms. The project does not require public release of raw sensitive locations.

## Data Handling And Terms Statement

Raw eBird data will be available only to authorised project users under the
approved eBird request purpose and data-use terms. Raw records will not be
redistributed, placed in public Git repositories, or passed to unauthorised
users. Derived summaries will cite eBird and Cornell Lab of Ornithology as
required, retain data-version and request provenance, and avoid exposing
restricted sensitive-location information.

The project will keep raw deliveries in ignored local data paths and commit
only metadata-only provenance, validation summaries, code, settings, and
documentation.

## Intended Outputs

Expected outputs are observation-aware research summaries, not raw eBird data
redistribution. Candidate outputs include:

- effort-aware occurrence/non-detection models for complete-checklist units;
- relative-count summaries with effort and detectability covariates;
- hydrological reaction curves for provisional species and guilds;
- support-month coverage and sampling-density diagnostics;
- sensitivity analyses for hydrology row quality, spatial precision, and
  observer effort;
- manuscript figures, tables, and supplementary provenance that cite eBird and
  respect sensitive-record restrictions.

Any derived products shared outside the authorised project team will be
aggregated, cited, and checked against the approved eBird terms before release.

## Scope Boundary For The Request

This request is limited to the Goal 022 pilot envelope:

- eBird Basic Dataset complete-checklist route;
- `2018-01-01` through `2024-12-31`;
- current 11 Goal 020 hydrology supports for the five named wetland complexes;
- provisional Goal 021 waterbird species/guild screen;
- no final species-list decision;
- no ALA, GBIF, Birdata, or EAWS substitution for absence/non-detection
  inference.
