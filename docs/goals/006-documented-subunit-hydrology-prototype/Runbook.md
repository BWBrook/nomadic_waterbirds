# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Operating Rules

- Follow `AGENTS.md`.
- Read `/Users/bwbrook/.codex/AGENTS.md` before choosing compute.
- Default to the Mac mini for this bounded prototype.
- Use ignored local scratch paths for raw official data.
- Commit only code/config, tests, docs, manifests, and small summaries.
- Do not download biodiversity data, submit access requests, use credentials,
  run full historical extraction, launch remote/HPC work, or make ecological
  claims.

## Suggested Commands

Orient:

```bash
git status --short --branch
git log --oneline --decorate -10
rg --files
git check-ignore -v data/scratch/goal006/example.tmp artifacts/subunit_supports/raw/example.tmp artifacts/subunit_hydrology/raw/example.tmp || true
```

Syntax/config checks, adjusted to actual files:

```bash
python3 -m py_compile scripts/<goal006-script>.py
python3 -m json.tool settings/<goal006-settings>.json >/dev/null
python3 -m json.tool docs/subunit_support_registry_manifest.json >/dev/null
python3 -m json.tool docs/subunit_hydrology_prototype_manifest.json >/dev/null
python3 -m unittest
```

CSV shape checks:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

required = {"NWB001", "NWB002", "NWB003", "NWB004", "NWB005"}
registry_path = Path("docs/subunit_support_registry.csv")
with registry_path.open(newline="", encoding="utf-8") as handle:
    registry_rows = list(csv.DictReader(handle))
ids = {row.get("candidate_id") for row in registry_rows}
missing = required - ids
if missing:
    raise SystemExit(f"missing subunit registry rows for: {sorted(missing)}")
if any(not row.get("parent_support_id") or not row.get("subunit_id") for row in registry_rows):
    raise SystemExit("registry rows must include parent_support_id and subunit_id")
print(f"subunit registry ok: {len(registry_rows)} rows across {len(ids & required)} required candidates")

summary_path = Path("docs/subunit_hydrology_prototype_summary.csv")
with summary_path.open(newline="", encoding="utf-8") as handle:
    summary_rows = list(csv.DictReader(handle))
bad = [row for row in summary_rows if not row.get("parent_support_id") or not row.get("subunit_id")]
if bad:
    raise SystemExit("hydrology rows must include parent_support_id and subunit_id")
print(f"subunit hydrology summary ok: {len(summary_rows)} rows")
PY
```

Git/data hygiene checks:

```bash
git diff --check
python3 - <<'PY'
from pathlib import Path
import subprocess

paths = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
large = [p for p in paths if Path(p).is_file() and Path(p).stat().st_size > 5_000_000]
if large:
    raise SystemExit("committed files larger than 5 MB: " + ", ".join(large))
print("committed-size check ok")
PY
python3 - <<'PY'
from pathlib import Path
import subprocess

blocked = {
    ".shp", ".dbf", ".shx", ".prj", ".gpkg", ".geojson", ".tif", ".tiff",
    ".nc", ".parquet", ".rds", ".zip", ".tar", ".gz", ".sqlite", ".duckdb",
}
paths = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
hits = [p for p in paths if Path(p).suffix.lower() in blocked]
if hits:
    raise SystemExit("committed raw/source-data extensions: " + ", ".join(hits))
print("committed raw-extension check ok")
PY
rg -n 'TO''DO|TB''D|FIX''ME|lor''em|place''holder' docs scripts settings tests AGENTS.md README.md || true
git status --short --branch
```

Use a small link-checking approach of your choice for local Markdown links in
new or edited docs. Record the command or method in the goal log.

Finish:

```bash
git add docs scripts settings tests
git commit -m "Prototype documented subunit hydrology"
git push origin main
git status --short --branch
```

Adjust the final `git add` paths to match actual changed files.

## Reporting Rules

Update:

- `docs/goals/006-documented-subunit-hydrology-prototype/Log.md`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

Final response should include subunit sources attempted, registry coverage,
hydrology metric status, staging paths and file sizes, compute decision,
validation outcomes, commit/push status, residual risks, and recommended Goal
007.
