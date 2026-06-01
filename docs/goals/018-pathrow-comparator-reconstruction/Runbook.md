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

## Target Row Extraction

```bash
python3 - <<'PY'
import csv

with open("docs/legacy_wetness_difference_triage_017_audit.csv", newline="", encoding="utf-8") as handle:
    rows = [row for row in csv.DictReader(handle) if row["root_cause_class"] == "insufficient_reference_evidence"]

print("material target rows", len(rows))
for row in rows:
    print(row["support_id"], row["month"], row["reference_source"], row["computed_path_rows"])

if len(rows) != 4:
    raise SystemExit(f"expected 4 material target rows, found {len(rows)}")
PY
```

## Useful Searches

```bash
rg -n "pathrow|path_row|asset_key_hash|item_id_hash|stac|direct_s3|support_intersecting" docs scripts settings tests
rg -n "insufficient_reference_evidence|tolerance_or_rounding_only|readiness|production" docs scripts settings tests
```

## Suggested Staging Checks

Before writing live artefacts:

```bash
mkdir -p artifacts/pathrow_comparator_reconstruction_018/raw
mkdir -p artifacts/pathrow_comparator_reconstruction_018/intermediate
mkdir -p artifacts/pathrow_comparator_reconstruction_018/output
git check-ignore artifacts/pathrow_comparator_reconstruction_018/raw/probe.json
git check-ignore artifacts/pathrow_comparator_reconstruction_018/intermediate/probe.npy
git check-ignore artifacts/pathrow_comparator_reconstruction_018/output/probe.json
```

Raw STAC item JSON, S3 listings, rasters, masks, arrays, and temporary rerun
outputs must remain ignored.

## Optional Remote Probe

Only use this if local route probes are slow or unstable, or if bounded
diagnostic raster reads are needed.

```bash
ssh deep-server-ts 'hostname; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true'
ssh deep-server-ts 'mkdir -p /data/codex/repos'
```

Use:

```text
/data/codex/repos/nomadic_waterbirds_goal018
```

## Validation Snippets

JSON:

```bash
python3 -m json.tool settings/pathrow_comparator_reconstruction_018.json >/dev/null
python3 -m json.tool docs/pathrow_comparator_reconstruction_018_manifest.json >/dev/null
```

CSV shape:

```bash
python3 - <<'PY'
import csv

required = {
    "docs/pathrow_comparator_reconstruction_018_targets.csv": {
        "candidate_id",
        "support_id",
        "month",
        "target_role",
        "goal017_root_cause_class",
    },
    "docs/pathrow_comparator_reconstruction_018_item_sets.csv": {
        "support_id",
        "month",
        "route",
        "route_status",
        "path_rows",
        "item_count",
        "asset_key_hash",
        "item_id_hash",
    },
    "docs/pathrow_comparator_reconstruction_018_comparison.csv": {
        "support_id",
        "month",
        "comparison_type",
        "comparison_status",
        "direct_s3_item_count",
        "comparator_item_count",
        "recommendation",
    },
    "docs/pathrow_comparator_reconstruction_018_readiness.csv": {
        "support_id",
        "month",
        "readiness_class",
        "route_status",
        "scale_up_recommendation",
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

with open("docs/pathrow_comparator_reconstruction_018_targets.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
material = [row for row in rows if row["target_role"] == "material"]
if len(material) != 4:
    raise SystemExit(f"expected 4 material targets, found {len(material)}")

with open("docs/pathrow_comparator_reconstruction_018_readiness.csv", newline="", encoding="utf-8") as handle:
    ready = list(csv.DictReader(handle))
material_ready = [row for row in ready if row.get("target_role", "material") == "material"]
if len(material_ready) != 4:
    raise SystemExit(f"expected 4 material readiness rows, found {len(material_ready)}")
if any(not row["readiness_class"] or not row["scale_up_recommendation"] for row in material_ready):
    raise SystemExit("blank readiness class or recommendation")
print("material readiness grid ok")
PY
```

Tests and hygiene:

```bash
git diff --check
python3 -m unittest tests.test_goal018_pathrow_comparator_reconstruction
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
git commit -m "Reconstruct path-row comparator evidence"
git push origin main
git status --short --branch
```

Adjust staged paths to actual changed files.

## Reporting Rules

Final response should include route status counts, item-set comparison counts,
readiness classes, any current direct-S3 defect status, validation outcomes,
commit/push status, residual risks, and the recommended Goal 019.
