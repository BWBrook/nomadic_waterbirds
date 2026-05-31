# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Operating Rules

- Follow `AGENTS.md`.
- Read `/Users/bwbrook/.codex/AGENTS.md` and the `nectar` control-plane docs
  listed in `Goal.md`.
- Use the Mac mini as control plane; use `deep-server` for the authorised
  remote rehearsal if reachable.
- Stage raw public files and remote intermediates only under ignored paths.
- Commit only code/config, tests, docs, manifests, and small summaries.
- Do not download biodiversity data, submit access requests, use private
  credentials, commit raw source data, make ecological claims, or launch
  production HPC.

## Suggested Local Orientation

```bash
git status --short --branch
git log --oneline --decorate -10
rg --files
git check-ignore -v data/scratch/goal008/example.tmp artifacts/narran_subunit_evidence/raw/example.tmp artifacts/remote_hydrology_rehearsal/raw/example.tmp || true
```

## Suggested Deep-Server Probe

Use the exact live alias that works and record the result:

```bash
ssh deep-server 'hostname; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true'
```

If `deep-server` fails and `deep-server-ts` is documented as the right
Tailscale path, try:

```bash
ssh deep-server-ts 'hostname; nproc; free -h; df -h /data; python3 --version; gdalinfo --version || true'
```

Do not keep trying aliases indefinitely. Record the blocker if the documented
paths fail.

## Suggested Remote Working Pattern

Adjust only as needed after reading the control-plane docs:

```bash
ssh deep-server 'mkdir -p /data/codex'
ssh deep-server 'test -d /data/codex/nomadic_waterbirds_goal008/.git || git clone git@github.com:BWBrook/nomadic_waterbirds.git /data/codex/nomadic_waterbirds_goal008'
ssh deep-server 'cd /data/codex/nomadic_waterbirds_goal008 && git fetch --prune origin && git checkout main && git pull --ff-only'
ssh deep-server 'cd /data/codex/nomadic_waterbirds_goal008 && python3 --version && python3 -m unittest discover -s tests -p "test*.py"'
```

If Python/GDAL dependencies are missing, either install the minimal documented
dependency set or stop with a routing memo if setup becomes the main task.

## Validation Snippets

JSON checks:

```bash
python3 -m json.tool docs/narran_named_subunit_evidence_manifest.json >/dev/null
python3 -m json.tool docs/remote_hydrology_rehearsal_008_manifest.json >/dev/null
```

CSV shape checks, adjusted for actual outputs:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

crosswalk = list(csv.DictReader(Path("docs/narran_named_subunit_crosswalk.csv").open(newline="", encoding="utf-8")))
required = {"support_id", "display_name", "evidence_status", "geometry_status", "inclusion_decision", "caveat"}
if not crosswalk:
    raise SystemExit("Narran crosswalk has no rows")
missing = required - set(crosswalk[0])
if missing:
    raise SystemExit(f"Narran crosswalk missing fields: {sorted(missing)}")
names = {row.get("display_name", "").lower() for row in crosswalk}
for expected in ["narran", "clear lake", "back lake"]:
    if not any(expected in name for name in names):
        raise SystemExit(f"expected Narran crosswalk row not found: {expected}")
print(f"Narran crosswalk ok: {len(crosswalk)} rows")
PY
```

Git/data hygiene:

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
    ".shp", ".dbf", ".shx", ".prj", ".gpkg", ".geojson", ".kml", ".kmz",
    ".tif", ".tiff", ".nc", ".parquet", ".rds", ".zip", ".tar", ".gz",
    ".sqlite", ".duckdb",
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

## Finish

```bash
git add AGENTS.md docs scripts settings tests
git commit -m "Resolve Narran evidence and rehearse remote hydrology"
git push origin main
git status --short --branch
```

Adjust `git add` paths to the actual changed files.

## Reporting Rules

Final response should include Narran evidence status, compute-routing decision,
remote probe/rehearsal result, whether full-window hydrology was run, staging
paths and file sizes, validation outcomes, commit/push status, residual risks,
and recommended Goal 009.
