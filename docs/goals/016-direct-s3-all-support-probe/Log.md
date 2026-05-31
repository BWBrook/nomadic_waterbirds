# Log

Goal: Direct S3 all-support probe

Status: Not started.

## Supervisor Setup

- 2026-05-31: Goal 016 packet created after Goal 015 repaired the hydrology
  comparator baseline and formalised support-intersecting WRS path/rows as the
  production scene-selection policy. This goal should test the direct-S3 route
  across all current event-window supports for the same three probe months
  before any full event-window extraction.

## Execution Checkpoints

- Starting state:
- Required reading complete:
- Ignored staging confirmed:
- Compute-routing memo complete:
- `deep-server-ts` probe complete or blocked:
- Remote smoke complete or blocker recorded:
- 33-row all-support extraction rehearsal complete or blocked:
- Comparison to Goal 015/014 and legacy rows complete:
- Reports/manifests/CSV outputs written:
- Registers/docs/logs updated:
- Validation complete:
- Commit/push complete:

## Notes

- Keep raw S3 listings, rasters, masks, arrays, remote logs, and other bulky
  generated files in ignored staging only.
- Do not shrink the support grid silently. Every expected support/month needs
  either a computed row or a classified blocked row.
