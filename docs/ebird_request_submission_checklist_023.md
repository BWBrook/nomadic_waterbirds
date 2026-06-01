# eBird Request Submission Checklist 023

## Status

Goal 023 prepares submission support only. nomad did not submit the eBird request,
must not use Barry's account, and must not fill or finalise any live eBird form.

The final submit/send action requires Barry's direct confirmation at action
time.

## Fixed Request Envelope

- Product route: eBird Basic Dataset raw observations plus sampling-event and
  effort metadata sufficient to identify complete checklists.
- Observation window: `2018-01-01` through `2024-12-31`.
- Wetland complexes: Macquarie Marshes, Narran Lake Nature Reserve, Gwydir
  Wetlands, Kerang Wetlands, and Currawinya Lakes.
- Current support set: the 11 Goal 020 hydrology supports listed in
  [ebird_pilot_request_package_022.md](ebird_pilot_request_package_022.md).
- Core hydrology rows: `core_eligible` and `core_eligible_with_caveat` only.
- Sensitivity accounting: all 23 `sensitivity_only` rows remain visible and
  outside core fitting.
- Caveat handling: four Goal 018 legacy-comparator caveat rows remain caveated,
  not dropped.
- Species and guild scope: provisional Goal 021 review screen only; no final
  species list or guild membership is locked by this request package.

## Pre-Submit Review

- Review the Goal 022 eBird package:
  [ebird_pilot_request_package_022.md](ebird_pilot_request_package_022.md).
- Confirm that the request remains an EBD complete-checklist pilot, not an
  eBird Observational Dataset, GBIF, ALA, Birdata, or EAWS substitute.
- Confirm that requested fields cover checklist identity, observation identity,
  date, complete-list status, protocol, duration, distance, party size, count,
  location precision, sensitive-record flags, taxonomy, data version, request
  ID, terms, and citation.
- Confirm that sensitive or location-suppressed records may be handled through
  provider-approved precision or support-level privacy buckets.
- Confirm that all downstream raw eBird delivery will remain under ignored
  `data/*` paths, with only metadata-only provenance committed to Git.
- Confirm that the request text does not make a final species-list decision.

## Live-Form Fill Steps For Barry Or Browser-Capable Helper

- Log in to eBird only as Barry or an explicitly authorised human delegate.
- Use the official eBird Basic Dataset request route described in the source
  register entries S56-S59.
- Paste the reviewed blocks from
  [ebird_request_text_023.md](ebird_request_text_023.md) into the matching form
  fields where appropriate.
- Choose the smallest product and field set that preserves complete-checklist,
  sampling-event, effort, location-precision, sensitive-record, taxonomy,
  terms, and citation requirements.
- Do not attach or generate new geometry from Goal 023. Describe the named
  wetland complexes and Goal 020 support relationship in text unless Barry
  separately approves a geometry workflow.
- Pause before the final submit/send control.

## Action-Time Confirmation Script

Before the final submit/send action, the human operator should read aloud or
type this confirmation:

```text
I, Barry W. Brook, confirm that the next submit/send action will send an
eBird Basic Dataset request to Cornell/eBird under my logged-in account for
the bounded nomadic-waterbirds pilot covering 2018-01-01 through 2024-12-31,
the current 11 Goal 020 hydrology supports, complete-checklist sampling-event
metadata, and the provisional Goal 021 species/guild review scope. I confirm
that nomad has not submitted this request and that this final action is my
direct human confirmation.
```

If Barry does not provide this confirmation, stop before final submission.

## Post-Submit Provenance Capture

After a human sends the request, record metadata only. Do not commit raw eBird
files, private request responses, account details, or screenshots.

Minimum metadata to capture outside raw-data Git paths:

- request ID or confirmation reference;
- submission date and submitting human;
- request purpose text version;
- product names and requested field groups;
- eBird data version or delivery version when supplied;
- terms/citation text version or a local note pointing to where the restricted
  terms record is stored;
- delivery filenames and checksums when files are received;
- notes on sensitive-record restrictions and any field omissions.

The first future intake action should follow
[ebird_intake_staging_plan_023.md](ebird_intake_staging_plan_023.md) before
opening or parsing any delivered record file.
