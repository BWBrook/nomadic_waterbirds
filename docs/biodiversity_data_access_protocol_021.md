# Biodiversity Data Access Protocol and Permission Checklist (Goal 021)

## Purpose

This protocol records the proposed access sequence for observation streams required by
the first constrained linkage design. It does not request or process any biodiversity
data in this goal.

## Current access status used by design

- No requests submitted yet.
- No raw records downloaded.
- All rows in this goal are provisional and support review by supervisor/lab leader.

## General intake controls (applies to all streams)

1. Read official terms before any request.
2. Keep raw IDs, sensitive species, and location-precision constraints in raw form or
   pseudonymised form only as permitted by stream policy.
3. Keep a per-stream licence ledger with:
   - licence name/version
   - effective date
   - redistribution and derivative constraints
   - sensitive-record rules
4. Record every record-include/exclude decision with a reason code.
5. Track overlap/duplicate logic where streams may share surveys or records.

## eBird complete checklists

**Access route:** logged-in user request flow, purpose-specific terms.

**Official sources used in this goal context:** S05, S06, S07, S08.

**Request actions now (process-only, no download):**
- Finalise purpose statement for occurrence and effort-aware relative-count pilot.
- Require complete-checklist-only extraction for non-detection support.
- Confirm that sensitive-species suppression/generalisation terms are supported in any downstream tables.
- Confirm if checklist metadata quality filters are required for valid effort covariates.

**Eligibility questions before any request is sent:**
- Is complete-checklist-only export available for the planned fields?
- Can sensitivity-suppressed records be represented via support-level assignment?
- What are the exact permitted downstream fields for effort and location precision?
- Can derived summaries be shared under the current terms?

**Use in this goal:**
- Proposed as primary lane for occurrence/non-detection and relative-count proxy.
- Marked as `recommended_pilot` pending protocol approvals.

## Birdata (2 ha 20 min standardised)

**Access route:** access request to BirdLife Australia via official form.

**Official sources used in this goal context:** S09, S10.

**Permission questions now (documented for next goal):**
- Is the requested extract permitted for a hydrology-linkage pilot of the stated scope?
- Does the extract include eBird-imported surveys, and can those be deduplicated?
- What reuse/distribution terms apply to raw extract and derived tables?
- What is the expected lag for request review and data refresh?

**Use in this goal:**
- Proposed as secondary/calibration lane only.
- Final role remains `candidate`; treated as validation/sensitivity until approval and harmonisation.

## ALA

**Access route:** API/download mechanisms where allowed by provider rules.

**Official sources used in this goal context:** S11, S12, S13.

**Questions before any request:**
- Which provider terms apply per record class?
- Are sensitive records returned with acceptable suppression levels for support assignment?
- Can historical occurrence records be used for context-only support without absence claims?

**Use in this goal:**
- Presence/taxonomy/range context lane only.
- Never used for absences.
- Remains `validation_only`.

## EAWS

**Access route:** public EAWS portal/reports and/or formal agreement path.

**Official source used in this goal context:** S14.

**Questions before any request/download:**
- Are public field definitions available for breeding and survey-intensity variables?
- What reuse/export constraints apply to aerial survey outputs?
- Can wetland-to-`support_id` crosswalk be documented without proprietary leakage?
- Are counts directly comparable across years and survey rounds?

**Use in this goal:**
- Independent validation lane for breeding/abundance direction.
- `status: candidate` in this design packet; final inclusion pending approvals.

## Data governance decisions made in Goal 021

- Keep ALA as context-only (never absence-inference).
- Keep Birdata and EAWS as secondary lanes until request permissions are explicitly cleared.
- Keep all rows provisional and reviewable; no final species list.
- Keep `sensitivity_only` hydrology rows out of core fitting until a later explicit decision.
