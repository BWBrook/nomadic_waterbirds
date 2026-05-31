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

Read `Goal.md` first, then `Plan.md`, then the required documents listed in
`Goal.md`.

## Useful Searches

```bash
rg -n "wetness_diff|wetness_differing_fields|denominator_differing_fields|review_before_scale_up" docs scripts settings tests
rg -n "asset_key_hash|item_id_hash|path_rows|support_area_m2|geometry_hash|n_pixel_u|valid_support_area" docs scripts settings tests
rg -n "direct_s3_all_support|event_window_hydrology|support_intersecting" docs scripts settings tests
```

## Target Row Extraction

```bash
python3 - <<'PY'
import csv

with open("docs/direct_s3_all_support_probe_016_comparison.csv", newline="", encoding="utf-8") as handle:
    rows = [row for row in csv.DictReader(handle) if row["comparison_status"] == "wetness_diff"]

print("wetness_diff rows", len(rows))
for row in rows:
    print(row["support_id"], row["month"], row["reference_source"], row["wetness_differing_fields"])

if len(rows) != 6:
    raise SystemExit(f"expected 6 wetness_diff rows, found {len(rows)}")
PY
```

## Suggested Staging Checks

Before writing live artefacts:

```bash
mkdir -p artifacts/legacy_wetness_difference_triage_017/raw
mkdir -p artifacts/legacy_wetness_difference_triage_017/intermediate
mkdir -p artifacts/legacy_wetness_difference_triage_017/output
git check-ignore artifacts/legacy_wetness_difference_triage_017/raw/probe.json
git check-ignore artifacts/legacy_wetness_difference_triage_017/intermediate/probe.npy
git check-ignore artifacts/legacy_wetness_difference_triage_017/output/probe.json
```

Raw S3 listings, STAC JSON, rasters, masks, arrays, and temporary rerun outputs
must remain ignored.

## Optional Remote Rerun Sketch

Only use this if static evidence cannot classify one or more target rows.

```bash
ssh deep-server-ts 'hostname; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true'
ssh deep-server-ts 'mkdir -p /data/codex/repos'
```

Use:

```text
/data/codex/repos/nomadic_waterbirds_goal017
```

Run one target row first, then only the remaining unresolved target rows.

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/legacy_wetness_difference_triage_017.json >/dev/null
python3 -m json.tool docs/legacy_wetness_difference_triage_017_manifest.json >/dev/null
```

CSV shape:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/legacy_wetness_difference_triage_017_audit.csv": {
        "candidate_id",
        "support_id",
        "month",
        "reference_source",
        "root_cause_class",
        "evidence_basis",
        "scale_up_recommendation",
    },
    "docs/legacy_wetness_difference_triage_017_item_delta.csv": {
        "support_id",
        "month",
        "reference_source",
        "computed_path_rows",
        "reference_readable_scene_count",
        "computed_readable_scene_count",
        "item_delta_status",
    },
    "docs/legacy_wetness_difference_triage_017_metric_delta.csv": {
        "support_id",
        "month",
        "reference_source",
        "field",
        "computed_value",
        "reference_value",
        "abs_difference",
        "difference_class",
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

with open("docs/legacy_wetness_difference_triage_017_audit.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
if len(rows) != 6:
    raise SystemExit(f"expected 6 audit rows, found {len(rows)}")
if any(not row["root_cause_class"] or not row["scale_up_recommendation"] for row in rows):
    raise SystemExit("blank classification or recommendation in audit")
print("audit grid ok")
PY
```

Tests and hygiene:

```bash
git diff --check
python3 -m unittest tests.test_goal017_legacy_wetness_difference_triage
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
git commit -m "Triage legacy wetness differences"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include root-cause counts, any current direct-S3 defect
status, whether bounded reruns were needed, validation outcomes, commit/push
status, residual risks, and the recommended Goal 018.
