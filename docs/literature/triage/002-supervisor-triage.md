# Supervisor Triage: Traceable Literature Mining

Date: 2026-05-31

Source report:
`docs/literature/reports/002-traceable-literature-mining.md`

Identifier file:
`docs/literature/identifiers/nomadic_waterbirds_identifiers.txt`

## Verdict

The GPT-5.5 Pro second-pass report is useful and appropriately conservative.
It should be treated as a source-mining and manuscript-planning artefact, not
as a substitute for reading the key sources.

The verification caveat is acceptable: the browsing environment could not bulk
open arbitrary `doi.org` URLs, so the report only treats identifiers as
verified where they appear in publisher, PubMed/PMC, official catalogue,
institutional, or comparable primary metadata. Guessed or weakly inferred
identifiers were excluded from the import file.

## Counts Checked

- annotated sources: 79
- identifier rows: 79
- unique identifiers: 79
- DOI-like identifiers: 77
- PMID identifiers: 1
- ISBN identifiers: 1
- claim-to-citation rows: 14
- manual-verification items: 11

Use-priority counts:

- must cite: 36
- likely cite: 20
- methods support: 17
- background only: 6

## Manuscript Implications

- The paper should not be framed as a static SDM. The literature supports a
  dynamic, observation-aware hydrology-response framing.
- "Hydrological reaction norm" remains a useful phrase if defined as an
  estimated response surface of occurrence, count intensity, or breeding
  probability against hydrological state/history. Avoid implying genetic or
  individual-level plasticity.
- Breeding, occurrence, abundance, breeding initiation, breeding persistence,
  fledging, and recruitment are distinct endpoints.
- Regional water availability should be described as analyst-defined landscape
  wetness context unless movement or behavioural data support stronger claims.
- DEA surface-water products are strong hydrology inputs but incomplete habitat
  proxies. Vegetated inundation, depth, salinity, substrate, disturbance, and
  food availability remain caveats.
- eBird, Birdata, and ALA should not be treated as equivalent observation
  streams. Complete eBird checklists with effort and protocol information are
  more defensible for detection/non-detection modelling than incidental records.
- EAWS is a strong independent structured comparator, not ground truth.
- False refugia and ecological traps should remain cautious hypotheses unless
  attraction plus lower fitness or demographic cost can be demonstrated.

## Machine-Readable Extracts

Created from the report:

- `docs/literature/tables/literature_claim_matrix.csv`
- `docs/literature/verification/manual_verification_queue.csv`

The claim matrix should feed the manuscript claim/evidence plan. The manual
verification queue should drive targeted source-checking before manuscript
drafting.

## Recommended Next Use

Do not ask the hydrology workflow to absorb this report immediately. The next
hydrology step is still Goal 009 recovery/resume planning after transient DEA
endpoint failures.

After the hydrology evidence state is reviewed, run a narrow
literature-integration goal to:

- import identifiers into Zotero or the project bibliography workflow
- verify the highest-priority manual items
- update the manuscript claim/evidence plan from
  `literature_claim_matrix.csv`
- decide which sources are must-cite in the Introduction, Methods, Study
  system, Discussion, and limitations sections
- keep source-derived claims separate from project-generated results
