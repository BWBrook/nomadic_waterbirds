# Runbook

Use this runbook as the practical checklist for Goal 021.

## 1. Start

```bash
cd /Users/bwbrook/papers/nomadic_waterbirds
git status --short --branch
git log --oneline -5
rg --files docs | sort
```

Confirm the repo is clean and includes Goal 020 commit `c4715f3` or a later
commit.

Update `docs/goals/021-bird-observation-linkage-design/Log.md` before editing.

## 2. Read Context

Read the files listed in `Goal.md`, especially:

```bash
sed -n '1,220p' docs/hydrology_to_bird_linkage_gate_020.md
sed -n '1,220p' docs/direct_s3_full_window_hydrology_020_audit_report.md
python3 -m json.tool docs/direct_s3_full_window_hydrology_020_manifest.json >/tmp/goal021_manifest_check.json
sed -n '1,220p' docs/data_stream_register.md
sed -n '1,220p' docs/analysis_plan.md
sed -n '1,220p' docs/validation_plan.md
```

Inspect the first few rows and schemas of:

```bash
python3 - <<'PY'
import csv
for path in [
    "docs/direct_s3_full_window_hydrology_020_readiness.csv",
    "docs/direct_s3_full_window_hydrology_020_support_summary.csv",
    "docs/direct_s3_full_window_hydrology_020_month_summary.csv",
]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(path, len(rows), rows[0].keys())
PY
```

## 3. Source Checks

Use current public/official pages only if needed to verify access routes or
terms. Record any new source in `docs/source_evidence_register.md` with an
accessed date.

Do not download data exports. Header checks, documentation pages, and small
HTML/API documentation probes are acceptable.

## 4. Create Design Artefacts

Create the required Markdown, CSV, JSON, script, settings, and test files.

CSV expectations:

- `bird_hydrology_join_contract_021.csv` should have one row per proposed
  observation-linkage grain or lane.
- `bird_observation_unit_schema_021.csv` should have one row per proposed
  future analyst-facing field.
- `candidate_species_guild_screen_021.csv` should contain provisional
  candidates only. Include a status column that distinguishes `recommended_pilot`,
  `candidate`, `defer`, and `needs_lab_leader_decision`.

## 5. Validate

Run:

```bash
# Default validation is read-only; it leaves the tracked manifest unchanged.
python3 scripts/validate_bird_linkage_design_021.py
python3 -m unittest tests.test_goal021_bird_linkage_design
python3 -m unittest discover -s tests -p 'test*.py'
python3 -m json.tool settings/bird_linkage_design_021.json >/dev/null
python3 -m json.tool docs/bird_linkage_design_021_manifest.json >/dev/null
git diff --check
```

To deliberately regenerate the tracked manifest after review, run the
explicit write mode separately:

```bash
python3 scripts/validate_bird_linkage_design_021.py --write-manifest
```

Run guardrail checks:

```bash
find . -type f -size +5M -not -path './.git/*' -print
find . -type f \( -name '*.shp' -o -name '*.gpkg' -o -name '*.geojson' -o -name '*.parquet' -o -name '*.sqlite' -o -name '*.duckdb' -o -name '*.rds' -o -name '*.zip' -o -name '*.tif' -o -name '*.nc' \) -not -path './.git/*' -print
rg -n --pcre2 '(?i)(todo|tbd|fixme|placeholder|lorem)' docs scripts tests settings
```

Run a local Markdown link check using the repo's existing approach or a small
script. Ensure links added by this goal resolve locally.

Check GitHub visibility:

```bash
gh repo view --json isPrivate,defaultBranchRef,nameWithOwner
```

## 6. Publish

If validation passes and the changed-file scope is only this goal's intended
files:

```bash
git status --short --branch
git add \
  docs/README.md \
  docs/data_stream_register.md \
  docs/decision_log.md \
  docs/source_evidence_register.md \
  docs/bird_observation_linkage_design_021.md \
  docs/bird_hydrology_join_contract_021.csv \
  docs/bird_observation_unit_schema_021.csv \
  docs/candidate_species_guild_screen_021.csv \
  docs/biodiversity_data_access_protocol_021.md \
  docs/bird_linkage_design_021_manifest.json \
  docs/goals/021-bird-observation-linkage-design/Log.md \
  scripts/validate_bird_linkage_design_021.py \
  settings/bird_linkage_design_021.json \
  tests/test_goal021_bird_linkage_design.py
git commit -m "Design bird observation linkage lane"
git push origin main
git status --short --branch
```

Omit `docs/source_evidence_register.md` from staging if it was not changed.

## 7. Final Response

Report the decision, candidate lane, validation evidence, changed files,
commit hash, push status, residual risks, and recommended Goal 022.
