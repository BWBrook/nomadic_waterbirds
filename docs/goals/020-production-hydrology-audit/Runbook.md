# Runbook

## Working Directory

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Orientation

```bash
git status --short --branch
git log --oneline --decorate -10
rg --files
```

Read `Goal.md`, then `Plan.md`, then the required files listed in `Goal.md`.

## Quick Goal 019 Shape Checks

```bash
python3 - <<'PY'
import csv
from collections import Counter

with open("docs/direct_s3_full_window_hydrology_019_series.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

print("rows", len(rows))
print("supports", len({row["support_id"] for row in rows}))
print("months", len({row["month"] for row in rows}))
print("status", Counter(row["row_status"] for row in rows))
print("quality", Counter(row["quality_flag"] for row in rows))
if len(rows) != 924:
    raise SystemExit("expected 924 rows")
if Counter(row["quality_flag"] for row in rows).get("quality_fail", 0) != 23:
    raise SystemExit("expected 23 quality_fail rows")
PY
```

## Useful Searches

```bash
rg -n "quality_fail|quality_minimum|quality_high|clear_obs_fraction|derived_metric_status|regional_metric_status" docs scripts settings tests
rg -n "direct_s3_full_window_hydrology_019|hydrology_to_bird|bird-linkage|readiness" docs scripts settings tests
```

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/audit_direct_s3_full_window_hydrology_020.json >/dev/null
python3 -m json.tool docs/direct_s3_full_window_hydrology_020_manifest.json >/dev/null
```

CSV shape:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/direct_s3_full_window_hydrology_020_quality_fail_rows.csv": {
        "support_id", "month", "quality_flag", "quality_fail_reason",
        "bird_linkage_readiness", "recommended_use",
    },
    "docs/direct_s3_full_window_hydrology_020_readiness.csv": {
        "support_id", "month", "bird_linkage_readiness", "recommended_use",
        "quality_flag", "caveat_code",
    },
    "docs/direct_s3_full_window_hydrology_020_support_summary.csv": {
        "support_id", "row_count", "core_eligible_count",
        "sensitivity_only_count", "exclude_count",
    },
    "docs/direct_s3_full_window_hydrology_020_month_summary.csv": {
        "month", "row_count", "core_eligible_count",
        "sensitivity_only_count", "exclude_count",
    },
}

for path, cols in required.items():
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"{path} has no rows")
    missing = cols - set(rows[0])
    if missing:
        raise SystemExit(f"{path} missing columns {sorted(missing)}")
    print(path, "rows", len(rows))

with open("docs/direct_s3_full_window_hydrology_020_readiness.csv", newline="", encoding="utf-8") as handle:
    readiness = list(csv.DictReader(handle))
if len(readiness) != 924:
    raise SystemExit(f"expected 924 readiness rows, found {len(readiness)}")
if len({(row["support_id"], row["month"]) for row in readiness}) != 924:
    raise SystemExit("readiness support-month keys are not unique")

with open("docs/direct_s3_full_window_hydrology_020_quality_fail_rows.csv", newline="", encoding="utf-8") as handle:
    qfail = list(csv.DictReader(handle))
if len(qfail) != 23:
    raise SystemExit(f"expected 23 quality-fail rows, found {len(qfail)}")
print("audit shape ok")
PY
```

Tests and hygiene:

```bash
git diff --check
python3 -m unittest tests.test_goal020_hydrology_audit
python3 -m unittest discover -s tests -p 'test*.py'
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
    ".shp", ".dbf", ".shx", ".prj", ".gpkg", ".geojson", ".kml", ".kmz",
    ".tif", ".tiff", ".nc", ".parquet", ".rds", ".zip", ".tar", ".gz",
    ".sqlite", ".duckdb", ".npy", ".npz",
}
paths = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
hits = [p for p in paths if Path(p).suffix.lower() in blocked]
if hits:
    raise SystemExit("committed raw/source-data extensions: " + ", ".join(hits))
print("committed raw-extension check ok")
PY
UNFINISHED_PATTERNS="TO""DO|TB""D|FIX""ME|lor""em|place""holder"
rg -n "$UNFINISHED_PATTERNS" docs scripts settings tests AGENTS.md README.md || true
git status --short --branch
```

Use or adapt the repo's local Markdown link-check pattern and record the
method in `Log.md`.

## Finish

```bash
git add docs scripts settings tests
git commit -m "Audit full-window hydrology production"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include audit verdict, readiness-class counts,
quality-fail classifications, support/month risk concentrations, validation
outcomes, commit/push status, residual risks, and recommended Goal 021.
