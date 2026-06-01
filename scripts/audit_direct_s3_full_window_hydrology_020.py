#!/usr/bin/env python3
"""Goal 020 readiness audit for Goal 019 full-window direct-S3 hydrology."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import math
import platform
import socket
import subprocess
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO / "settings" / "audit_direct_s3_full_window_hydrology_020.json"
COMPUTED_STATUS = "computed_direct_s3_metrics"
COMPUTED_METRIC_FIELDS = [
    "support_id",
    "month",
    "row_status",
    "asset_key_hash",
    "item_id_hash",
    "current_wet_area_m2",
    "current_proportion_wet",
]
ITEM_SET_HASH_FIELDS = ["support_id", "month", "route_status", "item_count", "asset_key_hash", "item_id_hash"]
SUMMARY_HASH_FIELDS = ["summary_level", "support_id", "month", "row_hash"]
GOAL019_SERIES_HASH_FIELDS = [
    "support_id",
    "month",
    "row_status",
    "asset_key_hash",
    "item_id_hash",
    "current_wet_area_m2",
    "current_proportion_wet",
]

NON_FINITE_TOKENS = {"", "nan", "inf", "-inf", "None"}

BLOCKED_RAW_EXTENSIONS = {
    ".shp",
    ".dbf",
    ".shx",
    ".prj",
    ".gpkg",
    ".geojson",
    ".kml",
    ".kmz",
    ".tif",
    ".tiff",
    ".nc",
    ".parquet",
    ".rds",
    ".zip",
    ".tar",
    ".gz",
    ".sqlite",
    ".duckdb",
    ".npy",
    ".npz",
}

QUALITY_PASS = {"quality_high", "quality_minimum"}
QUALITY_FAIL_REASONS = {
    "low_clear_fraction",
    "low_clear_pixel_support",
    "low_support_area_after_mask",
    "low_scene_count",
    "derived_metric_boundary",
    "regional_metric_boundary",
    "provenance_or_hash_issue",
    "unexpected_nonfinite_metric",
    "other_documented_caveat",
}
DERIVED_METRIC_BOUNDARY_VALUES = {"not_derived_quality_fail"}
REGIONAL_METRIC_VALID_VALUES = {
    "",
    "not_computed_row_blocked_or_quality_fail",
    "computed_all_current_supports_excluding_focal",
}
READINESS_FIELDNAMES = [
    "support_id",
    "month",
    "quality_flag",
    "quality_fail_reason",
    "bird_linkage_readiness",
    "recommended_use",
    "caveat_code",
    "row_status",
    "item_set_status",
    "derived_metric_status",
    "regional_metric_status",
]
SUPPORT_SUMMARY_FIELDNAMES = [
    "support_id",
    "row_count",
    "core_eligible_count",
    "core_eligible_with_caveat_count",
    "sensitivity_only_count",
    "exclude_before_bird_linkage_count",
    "blocked_requires_recovery_count",
    "exclude_count",
    "quality_high_count",
    "quality_minimum_count",
    "quality_fail_count",
]
MONTH_SUMMARY_FIELDNAMES = [
    "month",
    "row_count",
    "core_eligible_count",
    "core_eligible_with_caveat_count",
    "sensitivity_only_count",
    "exclude_before_bird_linkage_count",
    "blocked_requires_recovery_count",
    "exclude_count",
    "quality_high_count",
    "quality_minimum_count",
    "quality_fail_count",
]
QUALITY_FAIL_FIELDNAMES = [
    "support_id",
    "month",
    "candidate_id",
    "support_type",
    "quality_flag",
    "quality_fail_reason",
    "bird_linkage_readiness",
    "recommended_use",
    "caveat_code",
    "clear_obs_fraction",
    "n_scene_m",
    "support_area_m2",
    "valid_support_area_m2",
    "derived_metric_status",
    "regional_metric_status",
]
NONFINITE_BASE_FIELDS = [
    "current_wet_area_m2",
    "current_proportion_wet",
    "support_area_m2",
    "valid_support_area_m2",
    "clear_obs_fraction",
    "n_pixel_u",
    "clear_pixel_count",
]
READINESS_CLASS_VOCABULARY = {
    "core_eligible",
    "core_eligible_with_caveat",
    "sensitivity_only",
    "exclude_before_bird_linkage",
    "blocked_requires_recovery",
}


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialise_csv_value(row.get(field, "")) for field in fieldnames})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def serialise_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, list):
        return ";".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    if isinstance(value, float):
        return str(round(value, 12))
    return str(value)


def stable_row_hash(rows: list[dict[str, Any]], fields: list[str]) -> str:
    payload = [
        {field: str(row.get(field, "")) for field in fields}
        for row in sorted(
            rows,
            key=lambda row: (str(row.get("support_id", "")), str(row.get("month", ""))),
        )
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:
        return "unknown"


def git_status() -> str:
    try:
        return subprocess.check_output(["git", "status", "--short", "--branch"], cwd=REPO, text=True).strip()
    except Exception:
        return "unknown"


def host_facts() -> dict[str, str]:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
    }


def month_sequence(start_month: str, end_month: str) -> list[str]:
    year, month = [int(part) for part in start_month.split("-")]
    end_year, end_month_number = [int(part) for part in end_month.split("-")]
    months: list[str] = []
    while (year, month) <= (end_year, end_month_number):
        months.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip()
    if text in NON_FINITE_TOKENS:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def is_blocked_raw_extension(path: Path) -> bool:
    parts = set(path.parts)
    if path.suffix.lower() == ".json" and ("raw" in parts or "intermediate" in parts):
        return True
    return path.suffix.lower() in BLOCKED_RAW_EXTENSIONS


def quality_fail_reason(row: dict[str, str], checks: dict[str, Any]) -> str:
    clear_obs_fraction = to_float(row.get("clear_obs_fraction"))
    if clear_obs_fraction is not None and clear_obs_fraction < float(checks.get("min_clear_obs_fraction", 0.2)):
        return "low_clear_fraction"

    support_area = to_float(row.get("support_area_m2"))
    valid_support_area = to_float(row.get("valid_support_area_m2"))
    if support_area and valid_support_area is not None:
        if (valid_support_area / support_area) < float(checks.get("min_clear_pixel_support_ratio", 0.5)):
            return "low_support_area_after_mask"

    scene_count = to_float(row.get("n_scene_m"))
    if scene_count is not None and scene_count < float(checks.get("min_scene_count", 1)):
        return "low_scene_count"

    if to_float(row.get("current_wet_area_m2")) is None:
        return "unexpected_nonfinite_metric"

    if row.get("derived_metric_status") in DERIVED_METRIC_BOUNDARY_VALUES:
        return "derived_metric_boundary"

    if row.get("regional_metric_status") not in REGIONAL_METRIC_VALID_VALUES:
        return "regional_metric_boundary"

    return "other_documented_caveat"


def classify_readiness(
    row: dict[str, str],
    reason: str,
    goal018_lookup: set[tuple[str, str]],
    checks: dict[str, Any],
) -> tuple[str, str, list[str]]:
    support_id = str(row.get("support_id", "")).strip()
    month = str(row.get("month", "")).strip()
    caveats: list[str] = []

    if row.get("row_status", "") != COMPUTED_STATUS:
        caveats.append("provenance_or_hash_issue")
        return "blocked_requires_recovery", "exclude_before_bird_linkage", caveats

    if row.get("quality_flag") == "quality_fail":
        caveats.append(reason or "low_clear_fraction")
        return "sensitivity_only", "sensitivity_only", caveats

    if row.get("quality_flag") not in QUALITY_PASS:
        caveats.append("other_documented_caveat")
        return "exclude_before_bird_linkage", "exclude_before_bird_linkage", caveats

    if (support_id, month) in goal018_lookup:
        caveats.append("legacy_stac_comparator_not_obtained")

    if row.get("derived_metric_status") == "derived_partial_history":
        caveats.append("derived_metric_partial_history")

    support_area = to_float(row.get("support_area_m2"))
    valid_support_area = to_float(row.get("valid_support_area_m2"))
    if support_area and valid_support_area is not None:
        if (valid_support_area / support_area) < float(checks.get("min_clear_pixel_support_ratio", 0.5)):
            caveats.append("low_support_area_after_mask")

    if row.get("regional_metric_status") not in REGIONAL_METRIC_VALID_VALUES:
        caveats.append("regional_metric_boundary")

    if caveats:
        return "core_eligible_with_caveat", "core_with_caveat", caveats

    return "core_eligible", "core", caveats


def validate_inputs(
    series_rows: list[dict[str, str]],
    item_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
    manifest: dict[str, Any],
    checks: dict[str, Any],
) -> None:
    expected_row_count = int(checks.get("expected_row_count", 924))
    expected_support_count = int(checks.get("expected_support_count", 11))
    expected_month_count = int(checks.get("expected_month_count", 84))
    quality_fail_expected_count = int(checks.get("quality_fail_expected_count", 23))
    expected_support_types = set(checks.get("expected_support_types", []))
    month_window = checks.get("month_window", {})
    start_month = month_window.get("start", "")
    end_month = month_window.get("end", "")

    if len(series_rows) != expected_row_count:
        raise RuntimeError(f"expected {expected_row_count} series rows, found {len(series_rows)}")
    if len(item_rows) != expected_row_count:
        raise RuntimeError(f"expected {expected_row_count} item-set rows, found {len(item_rows)}")

    support_ids = sorted({row.get("support_id", "") for row in series_rows})
    months = sorted({row.get("month", "") for row in series_rows})
    key_rows = [(row.get("support_id", ""), row.get("month", "")) for row in series_rows]
    key_counts = collections.Counter(key_rows)
    duplicates = sorted([key for key, count in key_counts.items() if count != 1])
    if duplicates:
        raise RuntimeError(f"support-month grid duplicates: {duplicates[:8]}")
    if len(support_ids) != expected_support_count:
        raise RuntimeError(
            f"expected {expected_support_count} supports, found {len(support_ids)}"
        )
    if len(months) != expected_month_count:
        raise RuntimeError(f"expected {expected_month_count} months, found {len(months)}")
    if start_month and end_month and set(months) != set(month_sequence(start_month, end_month)):
        raise RuntimeError(
            f"month window mismatch; expected contiguous period {start_month} through {end_month}"
        )

    expected_keys = {(support_id, month) for support_id in support_ids for month in month_sequence(start_month, end_month)}
    observed_keys = {(row.get("support_id", ""), row.get("month", "")) for row in series_rows}
    if expected_keys != observed_keys:
        missing = sorted(expected_keys - observed_keys)
        extra = sorted(observed_keys - expected_keys)
        raise RuntimeError(
            f"support-month grid mismatch; missing={missing[:8]}, extra={extra[:8]}"
        )

    if manifest.get("row_count") != len(series_rows):
        raise RuntimeError(
            f"manifest row_count mismatch: {manifest.get('row_count')} != {len(series_rows)}"
        )
    if manifest.get("support_count") != len(support_ids):
        raise RuntimeError(
            f"manifest support_count mismatch: {manifest.get('support_count')} != {len(support_ids)}"
        )
    if expected_support_types:
        observed_support_types = {row.get("support_type", "") for row in series_rows}
        missing = sorted(expected_support_types - observed_support_types)
        if missing:
            raise RuntimeError(f"goal-019 support_type mismatch; missing={missing}")

    overall = next((row for row in summary_rows if row.get("summary_level") == "overall"), None)
    if not overall:
        raise RuntimeError("goal-019 summary has no overall row")
    if int(overall.get("row_count", "0") or 0) != len(series_rows):
        raise RuntimeError("goal-019 summary overall row_count mismatch")
    if int(overall.get("computed_count", "0") or 0) != len(series_rows):
        raise RuntimeError("goal-019 summary overall computed_count mismatch")
    if int(overall.get("blocked_count", "0") or 0) != 0:
        raise RuntimeError("goal-019 summary indicates blocked rows")

    if int(overall.get("quality_fail_count", "0") or 0) != quality_fail_expected_count:
        raise RuntimeError(
            f"expected {quality_fail_expected_count} goal-019 quality_fail rows, found {overall.get('quality_fail_count')}"
        )

    status_counts = collections.Counter(row.get("row_status", "") for row in series_rows)
    if set(status_counts) != {COMPUTED_STATUS}:
        raise RuntimeError(f"non-computed row status found: {dict(status_counts)}")
    if status_counts.get(COMPUTED_STATUS, 0) != expected_row_count:
        raise RuntimeError("not all Goal 019 rows are computed")

    quality_counts = collections.Counter(row.get("quality_flag", "") for row in series_rows)
    if quality_counts.get("quality_fail", 0) != quality_fail_expected_count:
        raise RuntimeError("goal-019 quality_fail count mismatch")

    for row in series_rows:
        if row.get("row_status") != COMPUTED_STATUS:
            continue
        if not row.get("asset_key_hash") or not row.get("item_id_hash"):
            raise RuntimeError(
                f"computed row missing item hash at {(row.get('support_id', ''), row.get('month', ''))}"
            )
        for field in NONFINITE_BASE_FIELDS:
            raw = row.get(field, "")
            if raw == "":
                if field in {"current_wet_area_m2", "current_proportion_wet"}:
                    raise RuntimeError(f"computed row missing required metric {field} at {(row.get('support_id', ''), row.get('month', ''))}")
                continue
            value = to_float(raw)
            if value is None or math.isinf(value) or math.isnan(value):
                raise RuntimeError(
                    f"computed row has non-finite base metric {field}='{raw}' at {(row.get('support_id', ''), row.get('month', ''))}"
                )

    item_keys = {(row.get("support_id", ""), row.get("month", "")) for row in item_rows}
    if len(item_rows) != len(series_rows) or item_keys != {(row.get("support_id", ""), row.get("month", "")) for row in series_rows}:
        raise RuntimeError("item-set grid mismatch with goal-019 series grid")

    if manifest.get("series_row_hash") != stable_row_hash(series_rows, GOAL019_SERIES_HASH_FIELDS):
        raise RuntimeError("goal-019 series_row_hash mismatch")
    if manifest.get("item_set_row_hash") != stable_row_hash(item_rows, ITEM_SET_HASH_FIELDS):
        raise RuntimeError("goal-019 item_set_row_hash mismatch")
    if manifest.get("summary_row_hash") != stable_row_hash(summary_rows, SUMMARY_HASH_FIELDS):
        raise RuntimeError("goal-019 summary_row_hash mismatch")


def build_support_summary(series_rows: list[dict[str, str]], readiness_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_support_series = collections.defaultdict(list)
    for row in series_rows:
        by_support_series[row["support_id"]].append(row)

    by_support_ready = collections.defaultdict(list)
    for row in readiness_rows:
        by_support_ready[row["support_id"]].append(row)

    summary_rows = []
    for support_id in sorted(by_support_series):
        rows = by_support_series[support_id]
        ready_rows = by_support_ready[support_id]
        qcounts = collections.Counter(row["quality_flag"] for row in rows)
        rcounts = collections.Counter(row["bird_linkage_readiness"] for row in ready_rows)
        exclude_count = (
            rcounts.get("exclude_before_bird_linkage", 0)
            + rcounts.get("blocked_requires_recovery", 0)
        )
        summary_rows.append(
            {
                "support_id": support_id,
                "row_count": len(rows),
                "core_eligible_count": rcounts.get("core_eligible", 0),
                "core_eligible_with_caveat_count": rcounts.get("core_eligible_with_caveat", 0),
                "sensitivity_only_count": rcounts.get("sensitivity_only", 0),
                "exclude_before_bird_linkage_count": rcounts.get("exclude_before_bird_linkage", 0),
                "blocked_requires_recovery_count": rcounts.get("blocked_requires_recovery", 0),
                "exclude_count": exclude_count,
                "quality_high_count": qcounts.get("quality_high", 0),
                "quality_minimum_count": qcounts.get("quality_minimum", 0),
                "quality_fail_count": qcounts.get("quality_fail", 0),
            }
        )
    return summary_rows


def build_month_summary(series_rows: list[dict[str, str]], readiness_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_month_series = collections.defaultdict(list)
    for row in series_rows:
        by_month_series[row["month"]].append(row)

    by_month_ready = collections.defaultdict(list)
    for row in readiness_rows:
        by_month_ready[row["month"]].append(row)

    summary_rows = []
    for month in sorted(by_month_series):
        rows = by_month_series[month]
        ready_rows = by_month_ready[month]
        qcounts = collections.Counter(row["quality_flag"] for row in rows)
        rcounts = collections.Counter(row["bird_linkage_readiness"] for row in ready_rows)
        exclude_count = (
            rcounts.get("exclude_before_bird_linkage", 0)
            + rcounts.get("blocked_requires_recovery", 0)
        )
        summary_rows.append(
            {
                "month": month,
                "row_count": len(rows),
                "core_eligible_count": rcounts.get("core_eligible", 0),
                "core_eligible_with_caveat_count": rcounts.get("core_eligible_with_caveat", 0),
                "sensitivity_only_count": rcounts.get("sensitivity_only", 0),
                "exclude_before_bird_linkage_count": rcounts.get("exclude_before_bird_linkage", 0),
                "blocked_requires_recovery_count": rcounts.get("blocked_requires_recovery", 0),
                "exclude_count": exclude_count,
                "quality_high_count": qcounts.get("quality_high", 0),
                "quality_minimum_count": qcounts.get("quality_minimum", 0),
                "quality_fail_count": qcounts.get("quality_fail", 0),
            }
        )
    return summary_rows


def write_markdown_report(
    manifest: dict[str, Any],
    readiness_counts: collections.Counter,
    quality_fail_reasons: collections.Counter,
    quality_fail_rows: list[dict[str, str]],
    support_summary_rows: list[dict[str, str]],
    month_summary_rows: list[dict[str, str]],
) -> str:
    lines = [
        "# Goal 020 Hydrology-to-Bird Linkage Readiness Audit",
        f"\nAccessed date: `{manifest['accessed_date']}`.\n",
        "## Outcome",
        f"Decision: `{manifest['goal020_readiness_decision']}`.",
        f"Core table: `{manifest['goal019_series_row_count']}` rows (`11` supports, `84` months).",
        f"Quality-fail rows retained and classified: `{len(quality_fail_rows)}`.",
        "",
        "## Readiness classes",
        "| Class | Rows |",
        "| --- | ---: |",
        *[f"| {status} | {count} |" for status, count in sorted(readiness_counts.items())],
        "",
        "## Quality-fail reason mix",
        "| Reason | Rows |",
        "| --- | ---: |",
        *[f"| {reason} | {count} |" for reason, count in quality_fail_reasons.most_common()],
        "",
        "## Quality-fail support concentration",
        "| Support | Rows |",
        "| --- | ---: |",
        *[
            f"| {support} | {count} |"
            for support, count in collections.Counter(row["support_id"] for row in quality_fail_rows).most_common()
        ],
        "",
        "## Quality-fail month concentration",
        "| Month | Rows |",
        "| --- | ---: |",
        *[
            f"| {month} | {count} |"
            for month, count in collections.Counter(row["month"] for row in quality_fail_rows).most_common()
        ],
        "",
        "## Caveats carried forward",
        "- Keep the four Goal 018 legacy comparator caveat rows as `core_eligible_with_caveat` and do not drop them from primary tables.",
        "- Exclude all `quality_fail` rows from core-linkage model fitting; keep them for sensitivity and coverage reporting only.",
        "- Review `derived_partial_history` rows during sensitivity checks.",
        "",
        "## Decision memo",
        "- `Goal 020` supports proceeding to `Goal 021` as a constrained bird-linkage design gate.",
        "- Restriction: apply `core_eligible` plus `core_eligible_with_caveat` tables only, and explicitly route `sensitivity_only` rows out of core fitting.",
        "- Restriction: preserve the Goal 018 four-row comparator caveat in downstream design documentation.",
        "- Restriction: do not use `quality_fail` rows in final primary covariate-response statements.",
        "",
    ]

    support_table = [
        "## Support summary preview",
        "| Support | Core eligible | Core with caveat | Sensitivity only | Quality fail |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in support_summary_rows:
        support_table.append(
            f"| {row['support_id']} | {row['core_eligible_count']} | {row['core_eligible_with_caveat_count']} | {row['sensitivity_only_count']} | {row['quality_fail_count']} |"
        )

    month_table = [
        "",
        "## Month summary preview",
        "| Month | Core eligible | Core with caveat | Sensitivity only | Quality fail |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in month_summary_rows:
        month_table.append(
            f"| {row['month']} | {row['core_eligible_count']} | {row['core_eligible_with_caveat_count']} | {row['sensitivity_only_count']} | {row['quality_fail_count']} |"
        )

    lines.extend(support_table)
    lines.append("")
    lines.extend(month_table)
    lines.append("")

    return "\n".join(lines)


def write_gate_memo(manifest: dict[str, Any]) -> str:
    restrictions = manifest["readiness_restrictions"]
    return "\n".join(
        [
            "# Goal 020 Hydrology-to-Bird-Linkage Gate",
            "",
            f"Decision: `{manifest['goal020_readiness_decision']}`.",
            "",
            "## Scope",
            "Use this hydrology table only for a constrained linkage design. Core analyses should start with `core_eligible` and `core_eligible_with_caveat` support-month rows.",
            "",
            "## Restrictions",
            *[f"- {restriction}" for restriction in restrictions],
            "- Keep all `quality_fail` rows (`23`) for sensitivity-only or reporting contexts.",
            "",
            "## Next goal",
            f"Recommended next goal: `{manifest['recommend_goal']}`.",
        ]
    )


def run(config_path: Path | None = None) -> dict[str, Any]:
    config = load_json(config_path or DEFAULT_CONFIG)
    checks = config.get("checks", {})

    inputs = config["inputs"]
    outputs = config["outputs"]

    goal019_manifest = load_json(REPO / inputs["goal019_manifest_json"])
    series_rows = read_csv(REPO / inputs["goal019_series_csv"])
    item_rows = read_csv(REPO / inputs["goal019_item_sets_csv"])
    summary_rows = read_csv(REPO / inputs["goal019_summary_csv"])
    readiness018_rows = read_csv(REPO / inputs["goal018_readiness_csv"])

    validate_inputs(
        series_rows,
        item_rows,
        summary_rows,
        goal019_manifest,
        {
            "expected_support_count": config["expected_support_count"],
            "expected_month_count": config["expected_month_count"],
            "expected_row_count": config["expected_row_count"],
            "month_window": config["month_window"],
            **checks,
        },
    )

    goal018_lookup = {
        (row.get("support_id", ""), row.get("month", ""))
        for row in readiness018_rows
        if row.get("readiness_class") == "ready_with_legacy_baseline_retired"
    }

    readiness_rows: list[dict[str, Any]] = []
    quality_fail_rows: list[dict[str, Any]] = []
    readiness_counts = collections.Counter()
    quality_fail_reasons = collections.Counter()

    item_lookup = {(row.get("support_id", ""), row.get("month", "")): row for row in item_rows}

    for row in sorted(series_rows, key=lambda row: (row.get("support_id", ""), row.get("month", ""))):
        quality_flag = row.get("quality_flag", "")
        reason = quality_fail_reason(row, checks)
        readiness_class, recommendation, caveats = classify_readiness(
            row,
            reason,
            goal018_lookup,
            checks,
        )
        caveat_code = ";".join(sorted(set(caveats)))

        if quality_flag == "quality_fail":
            quality_fail_rows.append(
                {
                    "support_id": row.get("support_id", ""),
                    "month": row.get("month", ""),
                    "candidate_id": row.get("candidate_id", ""),
                    "support_type": row.get("support_type", ""),
                    "quality_flag": quality_flag,
                    "quality_fail_reason": reason,
                    "bird_linkage_readiness": readiness_class,
                    "recommended_use": recommendation,
                    "caveat_code": caveat_code,
                    "clear_obs_fraction": row.get("clear_obs_fraction", ""),
                    "n_scene_m": row.get("n_scene_m", ""),
                    "support_area_m2": row.get("support_area_m2", ""),
                    "valid_support_area_m2": row.get("valid_support_area_m2", ""),
                    "derived_metric_status": row.get("derived_metric_status", ""),
                    "regional_metric_status": row.get("regional_metric_status", ""),
                }
            )
            quality_fail_reasons[reason] += 1

        readiness_rows.append(
            {
                "support_id": row.get("support_id", ""),
                "month": row.get("month", ""),
                "quality_flag": quality_flag,
                "quality_fail_reason": reason,
                "bird_linkage_readiness": readiness_class,
                "recommended_use": recommendation,
                "caveat_code": caveat_code,
                "row_status": row.get("row_status", ""),
                "item_set_status": item_lookup.get((row.get("support_id", ""), row.get("month", "")), {}).get("row_status", ""),
                "derived_metric_status": row.get("derived_metric_status", ""),
                "regional_metric_status": row.get("regional_metric_status", ""),
            }
        )
        readiness_counts[readiness_class] += 1

    support_summary_rows = build_support_summary(series_rows, readiness_rows)
    month_summary_rows = build_month_summary(series_rows, readiness_rows)

    quality_fail_fieldnames = [
        "support_id",
        "month",
        "candidate_id",
        "support_type",
        "quality_flag",
        "quality_fail_reason",
        "bird_linkage_readiness",
        "recommended_use",
        "caveat_code",
        "clear_obs_fraction",
        "n_scene_m",
        "support_area_m2",
        "valid_support_area_m2",
        "derived_metric_status",
        "regional_metric_status",
    ]
    readiness_fieldnames = [
        "support_id",
        "month",
        "quality_flag",
        "quality_fail_reason",
        "bird_linkage_readiness",
        "recommended_use",
        "caveat_code",
        "row_status",
        "item_set_status",
        "derived_metric_status",
        "regional_metric_status",
    ]
    support_summary_fieldnames = [
        "support_id",
        "row_count",
        "core_eligible_count",
        "core_eligible_with_caveat_count",
        "sensitivity_only_count",
        "exclude_before_bird_linkage_count",
        "blocked_requires_recovery_count",
        "exclude_count",
        "quality_high_count",
        "quality_minimum_count",
        "quality_fail_count",
    ]
    month_summary_fieldnames = [
        "month",
        "row_count",
        "core_eligible_count",
        "core_eligible_with_caveat_count",
        "sensitivity_only_count",
        "exclude_before_bird_linkage_count",
        "blocked_requires_recovery_count",
        "exclude_count",
        "quality_high_count",
        "quality_minimum_count",
        "quality_fail_count",
    ]

    write_csv(REPO / outputs["quality_fail_csv"], quality_fail_rows, quality_fail_fieldnames)
    write_csv(REPO / outputs["readiness_csv"], readiness_rows, readiness_fieldnames)
    write_csv(REPO / outputs["support_summary_csv"], support_summary_rows, support_summary_fieldnames)
    write_csv(REPO / outputs["month_summary_csv"], month_summary_rows, month_summary_fieldnames)

    manifest: dict[str, Any] = {
        "goal": config["goal"],
        "manifest_type": "goal020_hydrology_audit",
        "created_at_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "accessed_date": config["accessed_date"],
        "config_path": repo_relative(config_path or DEFAULT_CONFIG),
        "command": "python3 scripts/audit_direct_s3_full_window_hydrology_020.py",
        "git_head_at_run": git_head(),
        "git_status_at_run": git_status(),
        "host_facts": host_facts(),
        "goal019_manifest": repo_relative(REPO / inputs["goal019_manifest_json"]),
        "goal019_row_count": goal019_manifest.get("row_count", 0),
        "goal019_support_count": goal019_manifest.get("support_count", 0),
        "goal019_month_count": goal019_manifest.get("expected_month_count", 0),
        "goal019_series_csv": repo_relative(REPO / inputs["goal019_series_csv"]),
        "goal019_item_sets_csv": repo_relative(REPO / inputs["goal019_item_sets_csv"]),
        "goal019_summary_csv": repo_relative(REPO / inputs["goal019_summary_csv"]),
        "goal018_readiness_csv": repo_relative(REPO / inputs["goal018_readiness_csv"]),
        "quality_fail_count": len(quality_fail_rows),
        "quality_fail_reasons": dict(quality_fail_reasons),
        "quality_fail_rows": len(quality_fail_rows),
        "readiness_class_counts": dict(readiness_counts),
        "goal019_series_row_count": len(series_rows),
        "goal019_item_set_row_count": len(item_rows),
        "goal019_summary_row_count": len(summary_rows),
        "goal019_status_counts": goal019_manifest.get("status_counts", {}),
        "goal019_quality_counts": goal019_manifest.get("quality_counts", {}),
        "series_row_hash": stable_row_hash(series_rows, ["support_id", "month", "row_status", "quality_flag", "current_wet_area_m2"]),
        "item_set_row_hash": stable_row_hash(item_rows, ["support_id", "month", "row_status", "item_count", "asset_key_hash"]),
        "readiness_row_hash": stable_row_hash(readiness_rows, ["support_id", "month", "bird_linkage_readiness", "quality_fail_reason"]),
        "support_summary_row_hash": stable_row_hash(support_summary_rows, ["support_id", "row_count", "core_eligible_count", "quality_fail_count"]),
        "month_summary_row_hash": stable_row_hash(month_summary_rows, ["month", "row_count", "core_eligible_count", "quality_fail_count"]),
        "readiness_restrictions": config["decision"].get("readiness_restrictions", []),
        "goal020_readiness_decision": config["decision"].get("ready_for_constrained_bird_linkage", "ready_for_constrained_bird_linkage_design"),
        "recommend_goal": config["decision"].get("recommend_goal", "Goal 021"),
        "run_checks": {
            "expected_row_count": config["expected_row_count"],
            "expected_support_count": config["expected_support_count"],
            "expected_month_count": config["expected_month_count"],
            "quality_fail_expected_count": config["quality_fail_expected_count"],
        },
        "outputs": {
            "manifest_json": repo_relative(REPO / outputs["manifest_json"]),
            "audit_report_md": repo_relative(REPO / outputs["audit_report_md"]),
            "gate_memo_md": repo_relative(REPO / outputs["gate_memo_md"]),
            "quality_fail_csv": repo_relative(REPO / outputs["quality_fail_csv"]),
            "readiness_csv": repo_relative(REPO / outputs["readiness_csv"]),
            "support_summary_csv": repo_relative(REPO / outputs["support_summary_csv"]),
            "month_summary_csv": repo_relative(REPO / outputs["month_summary_csv"]),
        },
    }

    manifest_path = REPO / outputs["manifest_json"]
    write_json(manifest_path, manifest)

    report = write_markdown_report(
        manifest,
        readiness_counts,
        quality_fail_reasons,
        quality_fail_rows,
        support_summary_rows,
        month_summary_rows,
    )
    (REPO / outputs["audit_report_md"]).write_text(report, encoding="utf-8")

    gate_memo = write_gate_memo(manifest)
    (REPO / outputs["gate_memo_md"]).write_text(gate_memo, encoding="utf-8")

    return {
        **manifest,
        "quality_fail_rows_list": quality_fail_rows,
        "readiness_rows": readiness_rows,
        "support_summary_rows": support_summary_rows,
        "month_summary_rows": month_summary_rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Goal 020 hydrology output")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Path to goal-020 audit settings JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    run(config_path)


if __name__ == "__main__":
    main()
