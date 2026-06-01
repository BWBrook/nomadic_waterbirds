# Log

Goal: Full-window direct-S3 hydrology production

Status: Not started.

## Supervisor Setup

- 2026-06-01: Goal 019 packet created after Goal 018 reconstructed direct-S3
  item provenance for the four material legacy comparator rows, found no
  current direct-S3 defect, and recommended a remote restartable full-window
  direct-S3 hydrology production run.

## Execution Checkpoints

- Pending: starting state, required reading, remote probe, ignored staging
  checks, preflight, production decision, production run if authorised by
  preflight, validation, commit, and push.

## Notes

- Use `deep-server-ts` as the preferred host and
  `/data/codex/repos/nomadic_waterbirds_goal019` as the remote working path.
- Do not launch production if preflight fails.
- If production launches, emit exactly one status-classified row for each of
  924 expected support-months.
- Keep raw S3 listings, rasters, masks, arrays, and remote caches in ignored
  staging only.
