# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Operating Rules

- Follow `AGENTS.md`.
- Read `/Users/bwbrook/.codex/AGENTS.md` before choosing compute.
- Default to a tiny local Mac mini smoke test.
- Use ignored local scratch paths for raw official data.
- Commit only code/config, docs, manifests, and small summaries.
- Do not download biodiversity data, submit access requests, use credentials,
  run full historical extraction, or make ecological claims.

## Suggested Commands

Orient:

```bash
git status --short --branch
git log --oneline --decorate -8
rg --files
git check-ignore -v data/scratch/goal004/example.tmp artifacts/hydrology_smoke/raw/example.tmp || true
```

Validation:

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
python3 -m json.tool docs/hydrology_smoke_test_manifest.json >/dev/null
python3 - <<'PY'
import csv
from pathlib import Path

path = Path("docs/hydrology_smoke_test_summary.csv")
with path.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
ids = {row.get("candidate_id") for row in rows}
required = {"NWB001", "NWB002", "NWB003", "NWB004", "NWB005"}
missing = required - ids
if missing:
    raise SystemExit(f"missing smoke summary rows for: {sorted(missing)}")
print(f"summary ok: {len(rows)} rows across {len(ids & required)} required candidates")
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
rg -n 'TO''DO|TB''D|FIX''ME|lor''em' docs scripts settings AGENTS.md README.md || true
git status --short --branch
```

Use a small link-checking approach of your choice for local Markdown links in
new or edited docs. Record the command or method in the goal log.

If code/config is added, run language-appropriate syntax checks such as:

```bash
python3 -m py_compile scripts/<script>.py
```

or the R equivalent if using R.

Finish:

```bash
git add docs scripts settings
git commit -m "Run hydrology extraction smoke test"
git push origin main
git status --short --branch
```

Adjust the final `git add` paths to match actual changed files.

## Reporting Rules

Update:

- `docs/goals/004-hydrology-extraction-smoke-test/Log.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

Final response should include candidates attempted, metric/access status,
staging paths, cleanup status, compute decision, validation outcomes,
commit/push status, residual risks, and recommended Goal 005.
