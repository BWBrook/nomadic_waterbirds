# eBird Intake Staging Plan 023

## Purpose

This plan defines the future intake path for any eBird Basic Dataset delivery.
It is metadata-only and does not open, stage, parse, transform, or validate raw
eBird records in Goal 023.

## Core Rule

Raw eBird files, private request responses, account details, screenshots,
terms records with restricted text, and provider-delivered archives must stay
out of Git. The repository may commit only provenance schemas, checksums,
validation summaries, settings, scripts, and documentation.

## Ignored Staging Roots

Future raw delivery should use ignored paths already covered by `.gitignore`:

```text
data/ebird_raw/request_<request_id>/
data/ebird_quarantine/request_<request_id>/
data/ebird_work/request_<request_id>/
data/ebird_private_terms/request_<request_id>/
```

The committed project may later add metadata-only notes under `docs/`, for
example:

```text
docs/ebird_request_<request_id>_provenance.md
docs/ebird_request_<request_id>_qa_summary.md
```

Those notes must not contain raw records, private response text, credentials,
or restricted sensitive-location details.

## Future Intake Sequence

1. Delivery receipt

Record metadata only: request ID, delivery date, sender/source route, product
names, delivery filenames, file sizes, checksums, eBird data version, terms
version or citation text, and analyst initials.

2. Quarantine

Place delivered files in `data/ebird_quarantine/request_<request_id>/`. Do not
open or parse record rows until inventory, terms, and checksum checks pass.

3. Inventory and checksum gate

Confirm that all expected products are present, filenames match the request
metadata, checksums are stable, and archives are not committed or copied into
tracked paths.

4. Terms and sensitive-record gate

Confirm that the approved purpose, redistribution limits, citation
requirements, sensitive-species handling, and spatial-precision restrictions
are recorded before schema inspection.

5. Header/schema gate

Inspect headers only after the quarantine and terms gates pass. Required field
groups are defined in [ebird_required_fields_022.csv](ebird_required_fields_022.csv)
and the QA contract in [ebird_intake_qa_contract_023.csv](ebird_intake_qa_contract_023.csv).

6. Linkage preflight

Before deriving analysis tables, confirm date-window conformance, complete
checklist eligibility, sampling-event/effort metadata, sensitive-record
routing, duplicate/shared-checklist logic, and support-assignment readiness.

7. Release gate

Only after the QA contract passes may a later goal create derived
checklist-level or species-by-checklist analysis tables. Any derived table must
include request ID, data version, support assignment status, and terms/citation
provenance.

## Metadata-Only Provenance Pattern

Future provenance notes should include:

```text
request_id:
request_submitted_by:
request_submission_date:
delivery_received_date:
data_version:
citation_text_pointer:
terms_version_pointer:
approved_purpose_summary:
raw_storage_root:
quarantine_root:
product_files:
  - file_name:
    size_bytes:
    sha256:
    product_role:
row_counts_after_header_audit:
  observations:
  sampling_events:
  locations:
sensitive_record_restrictions:
field_omissions_or_unexpected_fields:
qa_contract_version:
analyst_initials:
review_status:
```

Use pointers for restricted terms or private correspondence if their contents
cannot be committed.

## Stop Rules

Stop before parsing records if any of the following occur:

- sampling-event or effort metadata are missing or not joinable to raw
  observations;
- complete-checklist status cannot be identified;
- terms, citation, request-purpose, or redistribution constraints are unclear;
- sensitive-record restrictions prevent support assignment or cannot be
  represented through an approved privacy bucket;
- delivery files lack stable checksums or expected product identity;
- observation dates cannot be restricted to `2018-01-01` through
  `2024-12-31`;
- support assignment cannot be performed without generating unapproved
  geometry or exposing restricted location precision;
- duplicate/shared checklist handling cannot be audited;
- any raw record, private response, credential, screenshot, or bulky archive
  appears in a tracked Git path.

## First Derived Tables Allowed Only In A Later Goal

Goal 023 does not create derived bird tables. A later approved intake goal may
create, after QA:

- checklist-level observation units;
- species/guild by checklist detection and non-detection tables;
- support-month coverage and sampling-density diagnostics;
- duplicate/shared-checklist audit;
- sensitive-record support-assignment audit;
- hydrology join QA table.
