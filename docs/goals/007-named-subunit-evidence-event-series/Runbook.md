# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Operating Rules

- Follow `AGENTS.md`.
- Read `/Users/bwbrook/.codex/AGENTS.md` before choosing compute.
- Default to the Mac mini for this bounded event-window prototype.
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
git check-ignore -v data/scratch/goal007/example.tmp artifacts/event_window_hydrology/raw/example.tmp artifacts/named_subunit_evidence/raw/example.tmp || true
```

Syntax/config checks, adjusted to actual files:

```bash
python3 -m py_compile scripts/<goal007-script>.py
python3 -m json.tool settings/<goal007-settings>.json >/dev/null
python3 -m json.tool docs/named_subunit_evidence_manifest.json >/dev/null
python3 -m json.tool docs/event_window_hydrology_series_manifest.json >/dev/null
python3 -m unittest discover -s tests -p 'test*.py'
```

CSV shape checks:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

crosswalk = list(csv.DictReader(Path("docs/named_subunit_crosswalk.csv").open(newline="", encoding="utf-8")))
included = [row for row in crosswalk if row.get("included_in_event_window") == "yes"]
if not included:
    raise SystemExit("no supports included in event-window crosswalk")
for row in included:
    if not row.get("support_id") or not row.get("support_type") or not row.get("evidence_status"):
        raise SystemExit("included crosswalk rows need support_id, support_type, and evidence_status")

series = list(csv.DictReader(Path("docs/event_window_hydrology_series.csv").open(newline="", encoding="utf-8")))
required_fields = {
    "support_id",
    "month",
    "status",
    "quality_flag",
    "wet_prop_lag_1m",
    "wet_prop_lag_3m",
    "wet_prop_trailing_3m",
    "wetting_delta_1m",
    "drying_velocity_1m",
    "consecutive_wet_months",
    "consecutive_dry_months_prior",
}
missing = required_fields - set(series[0]) if series else required_fields
if missing:
    raise SystemExit(f"event-window series missing fields: {sorted(missing)}")
print(f"crosswalk ok: {len(crosswalk)} rows, included {len(included)}")
print(f"event-window series ok: {len(series)} rows")
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
git commit -m "Build event-window hydrology series"
git push origin main
git status --short --branch
```

Adjust the final `git add` paths to match actual changed files.

## Reporting Rules

Update:

- `docs/goals/007-named-subunit-evidence-event-series/Log.md`
- `docs/source_evidence_register.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

Final response should include named-subunit evidence status, support-set
decision, event-window metric coverage, staging paths and file sizes, compute
decision, validation outcomes, commit/push status, residual risks, and
recommended Goal 008.
