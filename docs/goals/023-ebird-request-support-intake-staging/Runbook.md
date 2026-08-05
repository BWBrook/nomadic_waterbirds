# Runbook

Use this runbook as the practical checklist for Goal 023.

## 1. Start

```bash
cd /Users/bwbrook/papers/nomadic_waterbirds
git status --short --branch
git log --oneline -5
rg --files docs | sort
sed -n '1,180p' .gitignore
```

Confirm the repo is clean and includes Goal 022 commit `9bee436` or later.

Update `docs/goals/023-ebird-request-support-intake-staging/Log.md` before
editing.

## 2. Read Context

Read the files listed in `Goal.md`, especially:

```bash
sed -n '1,260p' docs/bird_data_access_feasibility_022.md
sed -n '1,320p' docs/ebird_pilot_request_package_022.md
sed -n '1,160p' docs/bird_data_access_matrix_022.csv
sed -n '1,180p' docs/ebird_required_fields_022.csv
python3 -m json.tool docs/bird_data_access_022_manifest.json >/tmp/goal023_goal022_manifest_check.json
sed -n '1,220p' docs/bird_observation_linkage_design_021.md
sed -n '1,160p' docs/candidate_species_guild_screen_021.csv
sed -n '1,220p' docs/hydrology_to_bird_linkage_gate_020.md
sed -n '1,220p' docs/data_stream_register.md
```

Inspect Goal 020 row-class counts:

```bash
python3 - <<'PY'
import csv
from collections import Counter

with open("docs/direct_s3_full_window_hydrology_020_readiness.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("rows", len(rows))
print(Counter(row["readiness_class"] for row in rows))
print("caveat rows", sum("legacy_stac_comparator_not_obtained" in row.get("caveat_code", "") for row in rows))
PY
```

## 3. Source Checks

Use current official/public eBird pages only if needed to verify details not
already settled in Goal 022, such as request route, product names,
sampling-event/effort metadata, citation, terms, or sensitive species handling.

Do not log in, inspect account-specific pages, submit forms, use credentials,
download records, or capture browser screenshots.

Record checked sources in `docs/source_evidence_register.md` if they are new
or more specific than existing entries. Include accessed date.

## 4. Create Artefacts

Create the required Markdown, CSV, JSON, script, settings, and test files.

Submission-support expectations:

- `docs/ebird_request_submission_checklist_023.md` separates pre-submit
  review, live-form fill, action-time confirmation, and post-submit provenance.
- `docs/ebird_request_text_023.md` includes paste-ready project title, short
  purpose, detailed description, sensitive-species justification, data
  handling/terms statement, intended outputs, and product/field request text.
- Both files state that Goal 023 did not submit the eBird request.

Intake-staging expectations:

- `docs/ebird_intake_staging_plan_023.md` keeps raw delivery under ignored
  `data/*` paths and commits metadata-only provenance patterns.
- `docs/ebird_intake_qa_contract_023.csv` should include one row per future QA
  check. Use controlled categories such as `inventory`, `provenance`, `terms`,
  `schema`, `sampling_event`, `checklist_completeness`, `sensitive_records`,
  `spatial`, `temporal`, `support_assignment`, `duplicates`, and `handoff`.
- Controlled severities should be `blocker`, `warning`, or `note`.
- Controlled stages should be `pre_parse`, `quarantine`, `schema_audit`,
  `linkage_preflight`, or `release_gate`.

## 5. Validate

Run:

```bash
# Default validation is read-only; it leaves the tracked manifest unchanged.
python3 scripts/validate_ebird_request_intake_023.py
python3 -m unittest tests.test_goal023_ebird_request_intake
python3 -m unittest discover -s tests -p 'test*.py'
python3 -m json.tool settings/ebird_request_intake_023.json >/dev/null
python3 -m json.tool docs/ebird_request_023_manifest.json >/dev/null
git diff --check
```

To deliberately regenerate the tracked manifest after review, run the
explicit write mode separately:

```bash
python3 scripts/validate_ebird_request_intake_023.py --write-manifest
```

Run guardrail checks:

```bash
find . -type f -size +5M -not -path './.git/*' -print
find . -type f \( -name '*.shp' -o -name '*.gpkg' -o -name '*.geojson' -o -name '*.parquet' -o -name '*.sqlite' -o -name '*.duckdb' -o -name '*.rds' -o -name '*.zip' -o -name '*.tif' -o -name '*.nc' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.png' \) -not -path './.git/*' -print
git status --short --porcelain | awk '{print $2}' | while read p; do case "$p" in *.shp|*.gpkg|*.geojson|*.parquet|*.sqlite|*.duckdb|*.rds|*.zip|*.tif|*.nc|*.jpg|*.jpeg|*.png) echo "$p";; esac; done
rg -n --pcre2 '(?i)(password\s*=|token\s*=|secret\s*=|api[_-]?key|cookie:|set-cookie|submitted the eBird request|request was submitted)' docs scripts tests settings -g '!docs/goals/**'
rg -n --pcre2 '(?i)(todo|tbd|fixme|placeholder|lorem)' docs scripts tests settings -g '!docs/goals/**/Runbook.md'
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
  docs/ebird_request_submission_checklist_023.md \
  docs/ebird_request_text_023.md \
  docs/ebird_intake_staging_plan_023.md \
  docs/ebird_intake_qa_contract_023.csv \
  docs/ebird_request_023_manifest.json \
  docs/goals/023-ebird-request-support-intake-staging/Goal.md \
  docs/goals/023-ebird-request-support-intake-staging/Plan.md \
  docs/goals/023-ebird-request-support-intake-staging/Runbook.md \
  docs/goals/023-ebird-request-support-intake-staging/Log.md \
  scripts/validate_ebird_request_intake_023.py \
  settings/ebird_request_intake_023.json \
  tests/test_goal023_ebird_request_intake.py
git commit -m "Prepare eBird request support package"
git push origin main
git status --short --branch
```

Add `docs/source_evidence_register.md` to staging only if it was changed by
new official/public source checks.

## 7. Final Response

Report the request-support status, submission boundary, intake-staging design,
validation evidence, changed files, commit hash, push status, residual risks,
and recommended next step.
