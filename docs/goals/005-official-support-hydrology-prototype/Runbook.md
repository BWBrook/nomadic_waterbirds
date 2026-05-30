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
- Commit only code/config, docs, manifests, and small summaries.
- Do not download biodiversity data, submit access requests, use credentials,
  run full historical extraction, launch remote/HPC work, or make ecological
  claims.

## Suggested Commands

Orient:

```bash
git status --short --branch
git log --oneline --decorate -10
rg --files
git check-ignore -v data/scratch/goal005/example.tmp artifacts/hydrology_supports/raw/example.tmp artifacts/hydrology_real_support/raw/example.tmp || true
```

Syntax/config checks, adjusted to actual files:

```bash
python3 -m py_compile scripts/<goal005-script>.py
python3 -m json.tool settings/<goal005-settings>.json >/dev/null
python3 -m json.tool docs/official_support_geometry_manifest.json >/dev/null
python3 -m json.tool docs/real_support_hydrology_prototype_manifest.json >/dev/null
```

CSV shape checks:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

required = {"NWB001", "NWB002", "NWB003", "NWB004", "NWB005"}
geometry_path = Path("docs/official_support_geometry_summary.csv")
with geometry_path.open(newline="", encoding="utf-8") as handle:
    geometry_rows = list(csv.DictReader(handle))
ids = {row.get("candidate_id") for row in geometry_rows}
missing = required - ids
if missing:
    raise SystemExit(f"missing geometry/status rows for: {sorted(missing)}")
print(f"geometry summary ok: {len(geometry_rows)} rows across {len(ids & required)} required candidates")

hydrology_path = Path("docs/real_support_hydrology_prototype_summary.csv")
with hydrology_path.open(newline="", encoding="utf-8") as handle:
    hydrology_rows = list(csv.DictReader(handle))
bad_probe = [row for row in hydrology_rows if row.get("support_id", "").endswith("_probe_3x3")]
if bad_probe:
    raise SystemExit("hydrology summary still uses Goal 004 probe supports")
print(f"hydrology summary ok: {len(hydrology_rows)} rows")
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
rg -n 'TO''DO|TB''D|FIX''ME|lor''em|place''holder' docs scripts settings AGENTS.md README.md || true
git status --short --branch
```

Use a small link-checking approach of your choice for local Markdown links in
new or edited docs. Record the command or method in the goal log.

Finish:

```bash
git add docs scripts settings
git commit -m "Prototype official-support hydrology extraction"
git push origin main
git status --short --branch
```

Adjust the final `git add` paths to match actual changed files.

## Reporting Rules

Update:

- `docs/goals/005-official-support-hydrology-prototype/Log.md`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

Final response should include official supports attempted, hydrology metric
status, how this differs from Goal 004, staging paths and file sizes, compute
decision, validation outcomes, commit/push status, residual risks, and
recommended Goal 006.
