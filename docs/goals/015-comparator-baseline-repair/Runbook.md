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
rg -n "bbox|path_row|readable_scene_count|invalid_obs_count|clear_obs_fraction|no_data|direct_s3|comparison" docs scripts settings tests
rg -n "current_wet_area|current_proportion_wet|wet_pixel|dry_pixel|quality_flag" scripts tests docs
```

## Suggested Staging Checks

Before writing live artefacts:

```bash
mkdir -p artifacts/comparator_baseline_repair_015/raw
mkdir -p artifacts/comparator_baseline_repair_015/intermediate
mkdir -p artifacts/comparator_baseline_repair_015/output
git check-ignore artifacts/comparator_baseline_repair_015/raw/probe.json
git check-ignore artifacts/comparator_baseline_repair_015/intermediate/probe.npy
git check-ignore artifacts/comparator_baseline_repair_015/output/probe.json
```

Raw STAC item JSON, S3 listings, rasters, arrays, and temporary extraction
outputs must remain ignored.

## Comparison Guidance

Use Goal 014 direct-S3 rows as the extraction target:

- `docs/direct_s3_extraction_rehearsal_014_summary.csv`

Use existing legacy rows only to explain the old mismatch:

- `docs/event_window_hydrology_series.csv` for `2022-11` and `2024-12`
- `docs/direct_s3_extraction_comparison_014.csv` for the mismatch hints

The repaired comparator should be path-row-filtered to `092/081`, `093/080`,
and `093/081` for `NWB002`.

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/comparator_baseline_repair_015.json >/dev/null
python3 -m json.tool docs/comparator_baseline_repair_015_manifest.json >/dev/null
```

CSV:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/pathrow_filtered_comparator_015_summary.csv": {
        "candidate_id",
        "support_id",
        "month",
        "status",
        "readable_scene_count",
        "clear_obs_count",
        "invalid_obs_count",
        "current_wet_area_m2",
        "current_proportion_wet",
        "quality_flag",
    },
    "docs/comparator_baseline_repair_015_comparison.csv": {
        "month",
        "comparison_type",
        "comparison_status",
        "differing_fields",
        "recommendation",
    },
    "docs/legacy_denominator_effect_015.csv": {
        "month",
        "legacy_extra_scene_count",
        "observed_extra_invalid_or_no_data",
        "effect_status",
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
PY
```

Tests and hygiene:

```bash
git diff --check
python3 -m unittest tests.test_goal015_comparator_baseline_repair
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
git commit -m "Repair hydrology comparator baseline"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include STAC/path-row-filtered comparator status,
comparison to Goal 014 direct-S3 rows, legacy denominator-effect explanation,
scene-selection policy decision, validation outcomes, commit/push status,
residual risks, and the recommended Goal 016.
