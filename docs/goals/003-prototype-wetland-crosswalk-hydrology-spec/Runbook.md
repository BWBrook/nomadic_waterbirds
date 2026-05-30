# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Operating Rules

- Follow `AGENTS.md`.
- Keep this goal to public metadata, tiny access checks, structured design
  tables, and documentation.
- Do not download bulk data, submit access requests, or use credentials.
- Do not commit raw source geometry, rasters, or biodiversity data.
- Commit and push only the validated design package.

## Suggested Commands

Orient:

```bash
git status --short --branch
git log --oneline --decorate -6
rg --files
```

Validation:

```bash
git diff --check
find . -type f -size +5M -not -path './.git/*'
rg -n 'TO''DO|TB''D|FIX''ME|lor''em' docs AGENTS.md README.md || true
python3 - <<'PY'
import csv
from pathlib import Path

path = Path("docs/prototype_wetland_unit_crosswalk.csv")
required = {
    "candidate_id",
    "candidate_name",
    "state_or_region",
    "primary_named_source",
    "primary_source_id_or_url",
    "geometry_source",
    "geometry_licence_or_terms",
    "dea_waterbodies_support",
    "water_observations_summary_needed",
    "geofabric_context",
    "public_biodiversity_or_eaws_alignment",
    "boundary_or_habitat_caveat",
    "prototype_role",
    "include_in_next_extraction_smoke",
}
with path.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    missing = required - set(reader.fieldnames or [])
    rows = list(reader)
if missing:
    raise SystemExit(f"missing required columns: {sorted(missing)}")
if not (5 <= len(rows) <= 8):
    raise SystemExit(f"expected 5-8 candidate rows, found {len(rows)}")
print(f"crosswalk ok: {len(rows)} rows")
PY
git status --short --branch
```

Use a small link-checking approach of your choice for local Markdown links in
new or edited docs. Record the command or method in the goal log.

Finish:

```bash
git add docs
git commit -m "Specify prototype wetland crosswalk and hydrology metrics"
git push origin main
git status --short --branch
```

Adjust the final `git add` paths if other documentation files are changed.

## Reporting Rules

Update:

- `docs/goals/003-prototype-wetland-crosswalk-hydrology-spec/Log.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

Final response should include changed files, selected candidate wetlands,
hydrology metric summary, access checks, validation outcomes, commit/push
status, residual risks, and recommended Goal 004.
