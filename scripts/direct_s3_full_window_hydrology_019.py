#!/usr/bin/env python3
"""Goal 019 restartable full-window direct-S3 hydrology production workflow."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import math
import platform
import socket
import sys
import time
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from direct_s3_all_support_probe_016 import (  # noqa: E402
    extract_rows as goal016_extract_rows,
    selected_supports as goal016_selected_supports,
)
from direct_s3_extraction_rehearsal_014 import (  # noqa: E402
    check_ignored,
    configure_gdal,
    git_head,
    git_status,
    load_json,
    read_csv,
    repo_relative,
    serialise_csv_value,
    write_csv,
    write_json,
)
from event_window_hydrology_007 import (  # noqa: E402
    base_metric_fields,
    blocked_metric_values,
    reset_retry_audit_log,
    retry_audit_summary,
)


DEFAULT_CONFIG = REPO / "settings" / "direct_s3_full_window_hydrology_019.json"
COMPUTED_STATUS = "computed_direct_s3_metrics"
REQUIRED_ROW_STATUSES = {
    COMPUTED_STATUS,
    "blocked_direct_s3_listing_failure",
    "blocked_direct_s3_read_failure",
    "blocked_geometry_or_mask_failure",
    "blocked_metric_computation_failure",
}
ROW_STATUS_VOCABULARY = {
    *REQUIRED_ROW_STATUSES,
    "blocked_direct_s3_no_items_found",
    "blocked_remote_or_route_unavailable",
}
GOAL016_STATUS_MAP = {
    "computed_direct_s3_metrics": COMPUTED_STATUS,
    "blocked_no_items_found": "blocked_direct_s3_no_items_found",
    "blocked_s3_listing_failure": "blocked_direct_s3_listing_failure",
    "blocked_cog_read_failure": "blocked_direct_s3_read_failure",
    "blocked_mask_or_geometry_failure": "blocked_geometry_or_mask_failure",
    "blocked_remote_or_route_unavailable": "blocked_remote_or_route_unavailable",
    "blocked_unclassified_failure": "blocked_metric_computation_failure",
}
QUALITY_PASS = {"quality_high", "quality_minimum"}
DERIVED_FIELDS = [
    "wet_area_lag_1m",
    "wet_prop_lag_1m",
    "wet_area_lag_3m",
    "wet_prop_lag_3m",
    "wet_prop_trailing_3m",
    "wetting_delta_1m",
    "wetting_delta_3m",
    "novel_after_dry_flag",
    "dry_spell_length_prior",
    "cumulative_wet_months_12m",
    "consecutive_wet_months",
    "consecutive_dry_months_prior",
    "drying_velocity_1m",
    "drying_velocity_3m",
    "rapid_drying_flag",
    "derived_metric_status",
]
REGIONAL_FIELDS = [
    "regional_wet_area_m2",
    "regional_valid_area_m2",
    "regional_proportion_wet",
    "regional_support_count",
    "regional_scarcity_index",
    "regional_metric_status",
]
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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def month_shift(month_name: str, offset: int) -> str:
    year, month = [int(part) for part in month_name.split("-")]
    index = year * 12 + month - 1 + offset
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def expected_support_month_grid(supports: list[dict[str, Any]], months: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for support in sorted(supports, key=lambda row: str(row.get("support_id", ""))):
        for month in sorted(months):
            rows.append({"support_id": support["support_id"], "candidate_id": support.get("candidate_id", ""), "month": month})
    return rows


def preflight_coverage(targets: list[dict[str, Any]], pathrow_map: dict[str, list[str]]) -> dict[str, Any]:
    months = {target["month"] for target in targets}
    support_ids = {target["support_id"] for target in targets}
    pathrow_lengths = [len(pathrow_map.get(target["support_id"], [])) for target in targets]
    coverage = {
        "has_single_pathrow": any(length == 1 for length in pathrow_lengths),
        "has_multi_pathrow": any(length > 1 for length in pathrow_lengths),
        "has_kerang_discrepancy_cluster": bool(
            support_ids & {"nwb004_ramsar_component_369", "nwb004_ramsar_ref265"}
        ),
        "has_early_window_month": "2018-01" in months,
        "has_flood_window_month": "2022-11" in months,
        "has_recent_month": "2024-12" in months,
    }
    coverage["passes"] = all(bool(value) for value in coverage.values())
    return coverage


def row_status_for_failure(stage: str, _exc: Exception | None = None) -> str:
    return {
        "s3_listing": "blocked_direct_s3_listing_failure",
        "no_items": "blocked_direct_s3_no_items_found",
        "cog_read": "blocked_direct_s3_read_failure",
        "mask": "blocked_geometry_or_mask_failure",
        "geometry": "blocked_geometry_or_mask_failure",
        "remote": "blocked_remote_or_route_unavailable",
        "metric": "blocked_metric_computation_failure",
    }.get(stage, "blocked_metric_computation_failure")


def is_blocked_raw_extension(path: Path) -> bool:
    path_text = path.as_posix()
    if path.suffix.lower() == ".json" and "/raw/" in f"/{path_text}":
        return True
    return path.suffix.lower() in BLOCKED_RAW_EXTENSIONS


def series_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "candidate_name",
        "parent_support_id",
        "support_id",
        "subunit_id",
        "display_name",
        "support_level",
        "support_type",
        "evidence_status",
        "month",
        "month_rationale",
        "source_geometry",
        "source_identifier",
        "source_geometry_caveat",
        "support_area_m2",
        "geometry_hash_sha256",
        "dea_product",
        "dea_product_version",
        "metric_spec_version",
        "scene_selection_policy",
        "access_method",
        "row_status",
        "failure_class",
        "item_count",
        "readable_scene_count",
        "skipped_scene_count",
        "path_rows",
        "asset_key_hash",
        "item_id_hash",
        *base_metric_fields(),
        *DERIVED_FIELDS,
        *REGIONAL_FIELDS,
        "failure_or_caveat",
    ]


def item_set_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "path_rows",
        "item_count",
        "asset_key_hash",
        "item_id_hash",
        "route_status",
        "row_status",
        "readable_scene_count",
        "skipped_scene_count",
        "failure_class",
    ]


def summary_fieldnames() -> list[str]:
    return [
        "summary_level",
        "support_id",
        "month",
        "path_rows",
        "row_count",
        "computed_count",
        "blocked_count",
        "quality_high_count",
        "quality_minimum_count",
        "quality_fail_count",
        "wet_month_count",
        "status_counts",
        "quality_counts",
        "row_hash",
    ]


def parse_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value in ("", None):
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def format_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def quality_passes(row: dict[str, Any]) -> bool:
    return row.get("row_status") == COMPUTED_STATUS and row.get("quality_flag") in QUALITY_PASS


def stable_grid_hash(rows: list[dict[str, Any]], fields: list[str]) -> str:
    payload = [
        {field: serialise_csv_value(row.get(field, "")) for field in fields}
        for row in sorted(rows, key=lambda item: (str(item.get("support_id", "")), str(item.get("month", ""))))
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def host_facts() -> dict[str, str]:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
    }


def work_items_for_mode(config: dict[str, Any], supports: list[dict[str, Any]], mode: str) -> dict[str, list[str]]:
    months = month_sequence(config["month_window"]["start"], config["month_window"]["end"])
    support_ids = {support["support_id"] for support in supports}
    if mode == "production":
        return {support_id: list(months) for support_id in sorted(support_ids)}
    work_items: dict[str, set[str]] = collections.defaultdict(set)
    for target in config["preflight_targets"]:
        support_id = target["support_id"]
        month = target["month"]
        if support_id not in support_ids:
            raise RuntimeError(f"preflight support is outside current support set: {support_id}")
        if month not in months:
            raise RuntimeError(f"preflight month is outside configured production window: {month}")
        work_items[support_id].add(month)
    return {support_id: sorted(months_for_support) for support_id, months_for_support in sorted(work_items.items())}


def grid_for_work_items(supports: list[dict[str, Any]], work_items: dict[str, list[str]]) -> list[dict[str, Any]]:
    support_lookup = {support["support_id"]: support for support in supports}
    rows: list[dict[str, Any]] = []
    for support_id in sorted(work_items):
        support = support_lookup[support_id]
        for month in sorted(work_items[support_id]):
            rows.append({"support_id": support_id, "candidate_id": support.get("candidate_id", ""), "month": month})
    return rows


def shard_path(config: dict[str, Any], mode: str, kind: str, support_id: str, month: str) -> Path:
    key = "series_shard_dir" if kind == "series" else "item_set_shard_dir"
    safe_name = f"{support_id}__{month}.json"
    return REPO / config["sharding"][key] / mode / safe_name


def load_shard(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_shard(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def map_goal016_status(status: str) -> str:
    return GOAL016_STATUS_MAP.get(status, "blocked_metric_computation_failure")


def normalise_extracted_row(config: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    normalised = dict(row)
    normalised["row_status"] = map_goal016_status(str(row.get("status", "")))
    normalised["item_count"] = row.get("direct_s3_items_found", "")
    normalised["month_rationale"] = "Goal 019 full-window direct-S3 production month"
    normalised["dea_product"] = config["source_product"]
    normalised["dea_product_version"] = config["source_product_version"]
    normalised["metric_spec_version"] = config["metric_spec_version"]
    normalised["scene_selection_policy"] = config["scene_selection_policy"]["id"]
    normalised.setdefault("failure_class", "")
    normalised.setdefault("failure_or_caveat", "")
    if normalised["row_status"] != COMPUTED_STATUS and not normalised.get("quality_flag"):
        normalised["quality_flag"] = "quality_fail"
    return {key: format_scalar(value) for key, value in normalised.items()}


def blocked_series_row(
    config: dict[str, Any],
    support: dict[str, Any],
    month: str,
    path_rows: list[str],
    row_status: str,
    failure_class: str,
    caveat: str,
) -> dict[str, Any]:
    row = {
        "candidate_id": support["candidate_id"],
        "candidate_name": support["candidate_name"],
        "parent_support_id": support["parent_support_id"],
        "support_id": support["support_id"],
        "subunit_id": support.get("subunit_id", ""),
        "display_name": support["display_name"],
        "support_level": support["support_level"],
        "support_type": support["support_type"],
        "evidence_status": support["evidence_status"],
        "month": month,
        "month_rationale": "Goal 019 full-window direct-S3 production month",
        "source_geometry": support["source"],
        "source_identifier": support["source_identifier"],
        "source_geometry_caveat": support["caveat"],
        "support_area_m2": support["support_area_m2"],
        "geometry_hash_sha256": support["geometry_hash_sha256"],
        "dea_product": config["source_product"],
        "dea_product_version": config["source_product_version"],
        "metric_spec_version": config["metric_spec_version"],
        "scene_selection_policy": config["scene_selection_policy"]["id"],
        "access_method": "direct public S3 path/row COG reads blocked before complete metrics",
        "row_status": row_status,
        "failure_class": failure_class,
        "item_count": 0,
        "readable_scene_count": 0,
        "skipped_scene_count": 0,
        "path_rows": ";".join(path_rows),
        "asset_key_hash": "",
        "item_id_hash": "",
        **blocked_metric_values(),
        "failure_or_caveat": caveat,
    }
    return {key: format_scalar(value) for key, value in row.items()}


def item_row_from_series(row: dict[str, Any]) -> dict[str, Any]:
    row_status = row.get("row_status", "")
    if row_status == COMPUTED_STATUS:
        route_status = "direct_s3_metrics_computed"
    elif row_status == "blocked_direct_s3_read_failure" and row.get("item_count") not in {"", "0", 0}:
        route_status = "direct_s3_items_listed_read_blocked"
    else:
        route_status = row_status
    return {
        "candidate_id": row.get("candidate_id", ""),
        "support_id": row.get("support_id", ""),
        "month": row.get("month", ""),
        "path_rows": row.get("path_rows", ""),
        "item_count": row.get("item_count", ""),
        "asset_key_hash": row.get("asset_key_hash", ""),
        "item_id_hash": row.get("item_id_hash", ""),
        "route_status": route_status,
        "row_status": row_status,
        "readable_scene_count": row.get("readable_scene_count", ""),
        "skipped_scene_count": row.get("skipped_scene_count", ""),
        "failure_class": row.get("failure_class", ""),
    }


def add_derived_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        grouped[str(row["support_id"])].append(dict(row))
    enriched: list[dict[str, Any]] = []
    for support_id in sorted(grouped):
        support_rows = sorted(grouped[support_id], key=lambda row: row["month"])
        by_month = {row["month"]: row for row in support_rows}
        for row in support_rows:
            row.update({field: "" for field in DERIVED_FIELDS})
            if row.get("row_status") != COMPUTED_STATUS:
                row["derived_metric_status"] = "not_derived_row_blocked"
                enriched.append(row)
                continue
            if not quality_passes(row):
                row["derived_metric_status"] = "not_derived_quality_fail"
                enriched.append(row)
                continue
            month = row["month"]
            current_prop = parse_float(row.get("current_proportion_wet"))
            current_wet = parse_bool(row.get("wet_month_flag")) is True
            lag1 = by_month.get(month_shift(month, -1))
            lag3 = by_month.get(month_shift(month, -3))
            lag1_prop = parse_float(lag1.get("current_proportion_wet")) if lag1 and quality_passes(lag1) else None
            lag1_area = parse_float(lag1.get("current_wet_area_m2")) if lag1 and quality_passes(lag1) else None
            lag3_prop = parse_float(lag3.get("current_proportion_wet")) if lag3 and quality_passes(lag3) else None
            lag3_area = parse_float(lag3.get("current_wet_area_m2")) if lag3 and quality_passes(lag3) else None
            trailing_values: list[float] = []
            for offset in (-1, -2, -3):
                prior = by_month.get(month_shift(month, offset))
                value = parse_float(prior.get("current_proportion_wet")) if prior and quality_passes(prior) else None
                if value is not None:
                    trailing_values.append(value)
            trailing3 = sum(trailing_values) / len(trailing_values) if trailing_values else None

            prior_month = by_month.get(month_shift(month, -1))
            dry_prior: int | None
            if prior_month is None:
                dry_prior = None
            elif not quality_passes(prior_month):
                dry_prior = None
            else:
                dry_prior = 0
                offset = -1
                while True:
                    prior = by_month.get(month_shift(month, offset))
                    if prior is None or not quality_passes(prior):
                        break
                    if parse_bool(prior.get("wet_month_flag")) is not False:
                        break
                    dry_prior += 1
                    offset -= 1

            consecutive_wet = 0
            if current_wet:
                offset = 0
                while True:
                    prior = by_month.get(month_shift(month, offset))
                    if prior is None or not quality_passes(prior) or parse_bool(prior.get("wet_month_flag")) is not True:
                        break
                    consecutive_wet += 1
                    offset -= 1

            cumulative_wet = 0
            for offset in range(-11, 1):
                prior = by_month.get(month_shift(month, offset))
                if prior and quality_passes(prior) and parse_bool(prior.get("wet_month_flag")) is True:
                    cumulative_wet += 1

            wetting_delta_1m = current_prop - lag1_prop if current_prop is not None and lag1_prop is not None else None
            wetting_delta_3m = current_prop - trailing3 if current_prop is not None and trailing3 is not None else None
            drying_velocity_1m = lag1_prop - current_prop if current_prop is not None and lag1_prop is not None else None
            drying_velocity_3m = trailing3 - current_prop if current_prop is not None and trailing3 is not None else None
            partial = any(value is None for value in [lag1_prop, lag3_prop, trailing3, dry_prior])
            row.update(
                {
                    "wet_area_lag_1m": lag1_area,
                    "wet_prop_lag_1m": lag1_prop,
                    "wet_area_lag_3m": lag3_area,
                    "wet_prop_lag_3m": lag3_prop,
                    "wet_prop_trailing_3m": trailing3,
                    "wetting_delta_1m": wetting_delta_1m,
                    "wetting_delta_3m": wetting_delta_3m,
                    "novel_after_dry_flag": None if dry_prior is None else bool(current_wet and dry_prior >= 2),
                    "dry_spell_length_prior": dry_prior,
                    "cumulative_wet_months_12m": cumulative_wet,
                    "consecutive_wet_months": consecutive_wet,
                    "consecutive_dry_months_prior": dry_prior,
                    "drying_velocity_1m": drying_velocity_1m,
                    "drying_velocity_3m": drying_velocity_3m,
                    "rapid_drying_flag": None if drying_velocity_1m is None else bool(drying_velocity_1m >= 0.10),
                    "derived_metric_status": "derived_partial_history" if partial else "derived_with_available_history",
                }
            )
            enriched.append({key: format_scalar(value) for key, value in row.items()})
    return enriched


def add_regional_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_month: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        by_month[str(row["month"])].append(row)
    enriched: list[dict[str, Any]] = []
    for row in rows:
        row = dict(row)
        row.update({field: "" for field in REGIONAL_FIELDS})
        if not quality_passes(row):
            row["regional_metric_status"] = "not_computed_row_blocked_or_quality_fail"
            enriched.append(row)
            continue
        peer_rows = [
            peer
            for peer in by_month[row["month"]]
            if peer.get("support_id") != row.get("support_id") and quality_passes(peer)
        ]
        wet_area = sum(parse_float(peer.get("current_wet_area_m2")) or 0.0 for peer in peer_rows)
        valid_area = sum(parse_float(peer.get("valid_support_area_m2")) or 0.0 for peer in peer_rows)
        if not peer_rows or valid_area <= 0:
            row["regional_metric_status"] = "not_computed_no_quality_passing_peers"
            enriched.append(row)
            continue
        regional_prop = wet_area / valid_area
        row.update(
            {
                "regional_wet_area_m2": wet_area,
                "regional_valid_area_m2": valid_area,
                "regional_proportion_wet": regional_prop,
                "regional_support_count": len(peer_rows),
                "regional_scarcity_index": 1.0 - regional_prop,
                "regional_metric_status": "computed_all_current_supports_excluding_focal",
            }
        )
        enriched.append({key: format_scalar(value) for key, value in row.items()})
    return enriched


def complete_grid(
    config: dict[str, Any],
    rows: list[dict[str, Any]],
    item_rows: list[dict[str, Any]],
    expected_grid: list[dict[str, Any]],
    support_lookup: dict[str, dict[str, Any]],
    pathrow_map: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    row_lookup = {(row["support_id"], row["month"]): row for row in rows}
    item_lookup = {(row["support_id"], row["month"]): row for row in item_rows}
    filled_rows: list[dict[str, Any]] = []
    filled_items: list[dict[str, Any]] = []
    inserted: list[dict[str, str]] = []
    for expected in expected_grid:
        key = (expected["support_id"], expected["month"])
        row = row_lookup.get(key)
        if row is None:
            support = support_lookup[expected["support_id"]]
            row = blocked_series_row(
                config,
                support,
                expected["month"],
                pathrow_map.get(expected["support_id"], []),
                "blocked_metric_computation_failure",
                "missing_shard_after_extraction",
                "Workflow inserted a classified row because extraction returned no row for this support/month.",
            )
            inserted.append({"support_id": expected["support_id"], "month": expected["month"]})
        item = item_lookup.get(key) or item_row_from_series(row)
        filled_rows.append(row)
        filled_items.append(item)
    return filled_rows, filled_items, inserted


def build_summary_rows(rows: list[dict[str, Any]], pathrow_map: dict[str, list[str]]) -> list[dict[str, Any]]:
    summary_rows: list[dict[str, Any]] = []

    def summarise(level: str, group_rows: list[dict[str, Any]], support_id: str = "", month: str = "") -> dict[str, Any]:
        status_counts = dict(sorted(collections.Counter(row.get("row_status", "") for row in group_rows).items()))
        quality_counts = dict(sorted(collections.Counter(row.get("quality_flag", "") for row in group_rows).items()))
        return {
            "summary_level": level,
            "support_id": support_id,
            "month": month,
            "path_rows": ";".join(pathrow_map.get(support_id, [])) if support_id else "",
            "row_count": len(group_rows),
            "computed_count": status_counts.get(COMPUTED_STATUS, 0),
            "blocked_count": len(group_rows) - status_counts.get(COMPUTED_STATUS, 0),
            "quality_high_count": quality_counts.get("quality_high", 0),
            "quality_minimum_count": quality_counts.get("quality_minimum", 0),
            "quality_fail_count": quality_counts.get("quality_fail", 0),
            "wet_month_count": sum(row.get("wet_month_flag") == "True" for row in group_rows),
            "status_counts": status_counts,
            "quality_counts": quality_counts,
            "row_hash": stable_grid_hash(group_rows, ["support_id", "month", "row_status", "asset_key_hash", "item_id_hash"]),
        }

    summary_rows.append(summarise("overall", rows))
    by_support: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    by_month: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        by_support[row["support_id"]].append(row)
        by_month[row["month"]].append(row)
    for support_id in sorted(by_support):
        summary_rows.append(summarise("support", by_support[support_id], support_id=support_id))
    for month in sorted(by_month):
        summary_rows.append(summarise("month", by_month[month], month=month))
    return summary_rows


def run_ignored_check(config: dict[str, Any]) -> dict[str, Any]:
    for staging_path in config["staging_paths"].values():
        (REPO / staging_path).mkdir(parents=True, exist_ok=True)
    probes = [
        REPO / config["staging_paths"]["raw"] / "probe.json",
        REPO / config["staging_paths"]["intermediate"] / "probe.npy",
        REPO / config["staging_paths"]["output"] / "probe.csv",
        REPO / config["sharding"]["series_shard_dir"] / "probe.json",
        REPO / config["sharding"]["item_set_shard_dir"] / "probe.json",
    ]
    return check_ignored(probes)


def execute_mode(
    config: dict[str, Any],
    mode: str,
    resume: bool,
    reuse_cache: bool,
    run_host_label: str,
    remote_workdir: str,
) -> dict[str, Any]:
    started = time.time()
    configure_gdal()
    reset_retry_audit_log()
    ignored_check = run_ignored_check(config)
    if ignored_check["status"] != "all_ignored":
        raise RuntimeError(f"Goal 019 staging paths are not all ignored: {ignored_check}")
    supports, support_source_rows, pathrow_map = goal016_selected_supports(config, None)
    support_lookup = {support["support_id"]: support for support in supports}
    work_items = work_items_for_mode(config, supports, mode)
    expected_grid = grid_for_work_items(supports, work_items)
    rows: list[dict[str, Any]] = []
    item_rows: list[dict[str, Any]] = []
    shard_events: list[dict[str, Any]] = []
    for support_id in sorted(work_items):
        support = support_lookup[support_id]
        months = sorted(work_items[support_id])
        existing_months: list[str] = []
        missing_months: list[str] = []
        for month in months:
            series_shard = shard_path(config, mode, "series", support_id, month)
            item_shard = shard_path(config, mode, "item_set", support_id, month)
            if resume and series_shard.exists() and item_shard.exists():
                rows.append(load_shard(series_shard))
                item_rows.append(load_shard(item_shard))
                existing_months.append(month)
            else:
                missing_months.append(month)
        if missing_months:
            try:
                extracted_rows, _records = goal016_extract_rows(
                    config,
                    [support],
                    missing_months,
                    pathrow_map,
                    reuse_cache or resume,
                )
                normalised_rows = [normalise_extracted_row(config, row) for row in extracted_rows]
            except Exception as exc:
                normalised_rows = [
                    blocked_series_row(
                        config,
                        support,
                        month,
                        pathrow_map.get(support_id, []),
                        row_status_for_failure("metric", exc),
                        "unexpected_support_month_extraction_error",
                        f"{type(exc).__name__}: {exc}",
                    )
                    for month in missing_months
                ]
            for row in normalised_rows:
                item_row = item_row_from_series(row)
                write_shard(shard_path(config, mode, "series", row["support_id"], row["month"]), row)
                write_shard(shard_path(config, mode, "item_set", row["support_id"], row["month"]), item_row)
                rows.append(row)
                item_rows.append(item_row)
        shard_events.append(
            {
                "support_id": support_id,
                "loaded_existing_months": len(existing_months),
                "extracted_months": len(missing_months),
            }
        )

    rows, item_rows, inserted_rows = complete_grid(config, rows, item_rows, expected_grid, support_lookup, pathrow_map)
    rows = add_regional_metrics(add_derived_metrics(rows))
    rows.sort(key=lambda row: (row["support_id"], row["month"]))
    item_rows.sort(key=lambda row: (row["support_id"], row["month"]))
    summary_rows = build_summary_rows(rows, pathrow_map)
    output_dir = REPO / config["staging_paths"]["output"]
    if mode == "preflight":
        write_csv(output_dir / "direct_s3_full_window_hydrology_019_preflight_series.csv", rows, series_fieldnames())
        write_csv(output_dir / "direct_s3_full_window_hydrology_019_preflight_item_sets.csv", item_rows, item_set_fieldnames())
        write_csv(output_dir / "direct_s3_full_window_hydrology_019_preflight_summary.csv", summary_rows, summary_fieldnames())
    result = {
        "mode": mode,
        "resume": resume,
        "reuse_cache": reuse_cache,
        "run_host_label": run_host_label,
        "remote_workdir": remote_workdir,
        "host_facts": host_facts(),
        "support_count": len({row["support_id"] for row in rows}),
        "support_source_row_count": len(support_source_rows),
        "support_ids": sorted({row["support_id"] for row in rows}),
        "months": sorted({row["month"] for row in rows}),
        "expected_row_count": len(expected_grid),
        "row_count": len(rows),
        "rows": rows,
        "item_rows": item_rows,
        "summary_rows": summary_rows,
        "status_counts": dict(sorted(collections.Counter(row["row_status"] for row in rows).items())),
        "quality_counts": dict(sorted(collections.Counter(row.get("quality_flag", "") for row in rows).items())),
        "series_row_hash": stable_grid_hash(
            rows,
            ["support_id", "month", "row_status", "asset_key_hash", "item_id_hash", "current_wet_area_m2", "current_proportion_wet"],
        ),
        "item_set_row_hash": stable_grid_hash(
            item_rows,
            ["support_id", "month", "route_status", "item_count", "asset_key_hash", "item_id_hash"],
        ),
        "summary_row_hash": stable_grid_hash(summary_rows, ["summary_level", "support_id", "month", "row_hash"]),
        "computed_item_hash_blank_count": sum(
            1
            for row in rows
            if row["row_status"] == COMPUTED_STATUS and (not row.get("asset_key_hash") or not row.get("item_id_hash"))
        ),
        "computed_nonfinite_base_count": sum(
            1
            for row in rows
            if row["row_status"] == COMPUTED_STATUS
            and (
                parse_float(row.get("current_wet_area_m2")) is None
                or parse_float(row.get("current_proportion_wet")) is None
            )
        ),
        "inserted_missing_grid_rows": inserted_rows,
        "shard_events": shard_events,
        "ignored_check": ignored_check,
        "retry_audit_summary": retry_audit_summary(),
        "elapsed_seconds": round(time.time() - started, 3),
    }
    return result


def resume_check(initial: dict[str, Any], rerun: dict[str, Any]) -> dict[str, Any]:
    return {
        "series_row_hash_initial": initial["series_row_hash"],
        "series_row_hash_resume": rerun["series_row_hash"],
        "item_set_row_hash_initial": initial["item_set_row_hash"],
        "item_set_row_hash_resume": rerun["item_set_row_hash"],
        "summary_row_hash_initial": initial["summary_row_hash"],
        "summary_row_hash_resume": rerun["summary_row_hash"],
        "stable": initial["series_row_hash"] == rerun["series_row_hash"]
        and initial["item_set_row_hash"] == rerun["item_set_row_hash"]
        and initial["summary_row_hash"] == rerun["summary_row_hash"],
        "initial_elapsed_seconds": initial["elapsed_seconds"],
        "resume_elapsed_seconds": rerun["elapsed_seconds"],
    }


def preflight_pass_status(config: dict[str, Any], result: dict[str, Any], check: dict[str, Any] | None) -> dict[str, Any]:
    supports, _source_rows, pathrow_map = goal016_selected_supports(config, None)
    coverage = preflight_coverage(config["preflight_targets"], pathrow_map)
    all_rows_computed = result["status_counts"] == {COMPUTED_STATUS: result["row_count"]}
    passed = (
        coverage["passes"]
        and result["row_count"] == result["expected_row_count"]
        and all_rows_computed
        and result["computed_item_hash_blank_count"] == 0
        and result["computed_nonfinite_base_count"] == 0
        and result["ignored_check"]["status"] == "all_ignored"
        and (check is None or check["stable"])
    )
    return {
        "passed": passed,
        "coverage": coverage,
        "all_rows_computed": all_rows_computed,
        "expected_row_count": result["expected_row_count"],
        "row_count": result["row_count"],
        "status_counts": result["status_counts"],
        "quality_counts": result["quality_counts"],
        "computed_item_hash_blank_count": result["computed_item_hash_blank_count"],
        "computed_nonfinite_base_count": result["computed_nonfinite_base_count"],
        "ignored_check_status": result["ignored_check"]["status"],
        "support_count_in_context": len(supports),
    }


def write_preflight_file(
    config_path: Path,
    config: dict[str, Any],
    initial: dict[str, Any],
    rerun: dict[str, Any] | None,
    check: dict[str, Any] | None,
) -> dict[str, Any]:
    final = rerun or initial
    pass_status = preflight_pass_status(config, final, check)
    payload = {
        "goal": config["goal"],
        "manifest_type": "direct_s3_full_window_hydrology_019_preflight",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "config_path": repo_relative(config_path),
        "command": config["run_command"] + " --mode preflight" + (" --verify-resume" if check else ""),
        "run_host_label": final["run_host_label"],
        "remote_workdir": final["remote_workdir"],
        "host_facts": final["host_facts"],
        "preflight_targets": config["preflight_targets"],
        "preflight_pass_status": pass_status,
        "resume_check": check or {},
        "series_row_hash": final["series_row_hash"],
        "item_set_row_hash": final["item_set_row_hash"],
        "summary_row_hash": final["summary_row_hash"],
        "shard_events": final["shard_events"],
        "ignored_check": final["ignored_check"],
        "status_vocabulary": sorted(ROW_STATUS_VOCABULARY),
        "outputs": {
            "preflight_json": config["outputs"]["preflight_json"],
            "ignored_preflight_series_csv": str(Path(config["staging_paths"]["output"]) / "direct_s3_full_window_hydrology_019_preflight_series.csv"),
            "ignored_preflight_item_sets_csv": str(Path(config["staging_paths"]["output"]) / "direct_s3_full_window_hydrology_019_preflight_item_sets.csv"),
            "ignored_preflight_summary_csv": str(Path(config["staging_paths"]["output"]) / "direct_s3_full_window_hydrology_019_preflight_summary.csv"),
        },
        "elapsed_seconds": final["elapsed_seconds"],
    }
    write_json(REPO / config["outputs"]["preflight_json"], payload)
    return payload


def write_report(path: Path, config: dict[str, Any], manifest: dict[str, Any]) -> None:
    status_counts = manifest["status_counts"]
    quality_counts = manifest["quality_counts"]
    resume = manifest.get("resume_check", {})
    blocked_count = manifest["row_count"] - status_counts.get(COMPUTED_STATUS, 0)
    status_lines = [f"| {status} | {count} |" for status, count in sorted(status_counts.items())]
    quality_lines = [f"| {status} | {count} |" for status, count in sorted(quality_counts.items())]
    write_text(
        path,
        "\n".join(
            [
                "# Goal 019 Full-Window Direct-S3 Hydrology Production",
                "",
                f"Accessed date: `{config['accessed_date']}`.",
                "",
                "## Scope",
                "",
                "This hydrology-only production package used direct public S3 COG reads with the support-intersecting WRS path-row scene-selection policy. It does not use STAC as a production dependency and does not make biodiversity or ecological-response claims.",
                "",
                "## Remote Route",
                "",
                f"Run host label: `{manifest['run_host_label']}`.",
                f"Remote working path: `{manifest['remote_workdir']}`.",
                f"Remote compute used: `{manifest['remote_compute_used']}`.",
                "",
                "## Preflight",
                "",
                f"Preflight passed: `{manifest.get('preflight_passed', False)}`.",
                f"Preflight file: `{config['outputs']['preflight_json']}`.",
                "",
                "## Production Grid",
                "",
                f"Expected rows: `{manifest['expected_row_count']}`.",
                f"Observed rows: `{manifest['row_count']}`.",
                f"Expected grid complete: `{manifest['expected_grid_complete']}`.",
                f"Computed rows: `{status_counts.get(COMPUTED_STATUS, 0)}`.",
                f"Blocked rows: `{blocked_count}`.",
                "",
                "| Row status | Rows |",
                "| --- | ---: |",
                *status_lines,
                "",
                "| Quality flag | Rows |",
                "| --- | ---: |",
                *quality_lines,
                "",
                "## Restartability",
                "",
                f"Resume/rerun stable: `{resume.get('stable', False)}`.",
                f"Initial series hash: `{resume.get('series_row_hash_initial', '')}`.",
                f"Resume series hash: `{resume.get('series_row_hash_resume', '')}`.",
                "",
                "## Compact Outputs",
                "",
                f"- Series: `{config['outputs']['series_csv']}`.",
                f"- Item sets: `{config['outputs']['item_sets_csv']}`.",
                f"- Summary: `{config['outputs']['summary_csv']}`.",
                f"- Manifest: `{config['outputs']['manifest_json']}`.",
                "",
                "## Recommendation For Goal 020",
                "",
                manifest["recommendation_for_goal020"],
            ]
        )
        + "\n",
    )


def recommendation_for_goal020(manifest: dict[str, Any]) -> str:
    if manifest["row_count"] != manifest["expected_row_count"] or not manifest["expected_grid_complete"]:
        return "Open a recovery goal to repair missing support-month rows before any biodiversity linkage."
    blocked_count = manifest["row_count"] - manifest["status_counts"].get(COMPUTED_STATUS, 0)
    if blocked_count:
        return "Open a targeted recovery goal for the classified blocked support-month rows before using the series as a complete hydrology covariate layer."
    return "Use Goal 020 to audit the production hydrology table, document any metric caveats, and prepare the next hydrology-to-bird-data design gate."


def write_production_package(
    config_path: Path,
    config: dict[str, Any],
    result: dict[str, Any],
    check: dict[str, Any] | None,
) -> dict[str, Any]:
    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    write_csv(outputs["series_csv"], result["rows"], series_fieldnames())
    write_csv(outputs["item_sets_csv"], result["item_rows"], item_set_fieldnames())
    write_csv(outputs["summary_csv"], result["summary_rows"], summary_fieldnames())
    expected_complete = (
        result["row_count"] == result["expected_row_count"]
        and not result["inserted_missing_grid_rows"]
        and len(result["support_ids"]) == config["expected_support_count"]
        and len(result["months"]) == config["expected_month_count"]
    )
    preflight_payload = {}
    preflight_path = outputs["preflight_json"]
    if preflight_path.exists():
        preflight_payload = load_json(preflight_path)
    manifest = {
        "goal": config["goal"],
        "manifest_type": "direct_s3_full_window_hydrology_019",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "accessed_date": config["accessed_date"],
        "command": config["run_command"] + " --mode production" + (" --verify-resume" if check else ""),
        "config_path": repo_relative(config_path),
        "git_head_at_run": git_head(),
        "git_status_at_run": git_status(),
        "host_facts": result["host_facts"],
        "run_host_label": result["run_host_label"],
        "remote_compute_used": result["run_host_label"] not in {"local", "local_mac_mini"},
        "remote_workdir": result["remote_workdir"],
        "source_urls": config["source_urls"],
        "scene_selection_policy": config["scene_selection_policy"],
        "support_count": len(result["support_ids"]),
        "support_ids": result["support_ids"],
        "month_window": config["month_window"],
        "months": result["months"],
        "expected_support_count": config["expected_support_count"],
        "expected_month_count": config["expected_month_count"],
        "expected_row_count": result["expected_row_count"],
        "row_count": result["row_count"],
        "expected_grid_complete": expected_complete,
        "status_counts": result["status_counts"],
        "quality_counts": result["quality_counts"],
        "series_row_hash": result["series_row_hash"],
        "item_set_row_hash": result["item_set_row_hash"],
        "summary_row_hash": result["summary_row_hash"],
        "computed_item_hash_blank_count": result["computed_item_hash_blank_count"],
        "computed_nonfinite_base_count": result["computed_nonfinite_base_count"],
        "inserted_missing_grid_rows": result["inserted_missing_grid_rows"],
        "resume_check": check or {},
        "preflight_passed": bool(preflight_payload.get("preflight_pass_status", {}).get("passed", False)),
        "preflight": preflight_payload,
        "sharding": config["sharding"],
        "shard_events": result["shard_events"],
        "retry_audit_summary": result["retry_audit_summary"],
        "outputs": {key: repo_relative(path) for key, path in outputs.items()},
        "staging_paths": config["staging_paths"],
        "staging_ignored_check": result["ignored_check"],
        "staging_policy": config["commit_policy"],
        "status_vocabulary": sorted(ROW_STATUS_VOCABULARY),
        "validation_outcomes": {},
        "recommendation_for_goal020": "",
        "elapsed_seconds": result["elapsed_seconds"],
    }
    manifest["recommendation_for_goal020"] = recommendation_for_goal020(manifest)
    write_json(outputs["manifest_json"], manifest)
    write_report(outputs["report_md"], config, manifest)
    return manifest


def run(
    config_path: Path,
    mode: str,
    resume: bool,
    verify_resume: bool,
    reuse_cache: bool,
    run_host_label: str,
    remote_workdir: str,
) -> dict[str, Any]:
    config = load_json(config_path)
    remote_workdir = remote_workdir or config["compute"]["remote_workdir"]
    if verify_resume:
        initial = execute_mode(config, mode, resume=False, reuse_cache=reuse_cache, run_host_label=run_host_label, remote_workdir=remote_workdir)
        rerun = execute_mode(config, mode, resume=True, reuse_cache=True, run_host_label=run_host_label, remote_workdir=remote_workdir)
        check = resume_check(initial, rerun)
        if mode == "preflight":
            return write_preflight_file(config_path, config, initial, rerun, check)
        return write_production_package(config_path, config, rerun, check)
    result = execute_mode(config, mode, resume=resume, reuse_cache=reuse_cache, run_host_label=run_host_label, remote_workdir=remote_workdir)
    if mode == "preflight":
        return write_preflight_file(config_path, config, result, None, None)
    return write_production_package(config_path, config, result, None)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to Goal 019 config JSON")
    parser.add_argument("--mode", choices=["preflight", "production"], default="preflight")
    parser.add_argument("--resume", action="store_true", help="Reuse existing per-support-month shards when present")
    parser.add_argument("--verify-resume", action="store_true", help="Run once fresh and once with resume, then compare hashes")
    parser.add_argument("--reuse-ignored-cache", action="store_true", help="Reuse ignored direct-S3 listing caches")
    parser.add_argument("--run-host-label", default="local_mac_mini")
    parser.add_argument("--remote-workdir", default="")
    args = parser.parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    payload = run(
        config_path=config_path,
        mode=args.mode,
        resume=args.resume,
        verify_resume=args.verify_resume,
        reuse_cache=args.reuse_ignored_cache,
        run_host_label=args.run_host_label,
        remote_workdir=args.remote_workdir,
    )
    print(
        json.dumps(
            {
                "mode": args.mode,
                "passed": payload.get("preflight_pass_status", {}).get("passed", payload.get("expected_grid_complete", "")),
                "row_count": payload.get("row_count", payload.get("preflight_pass_status", {}).get("row_count", "")),
                "status_counts": payload.get("status_counts", payload.get("preflight_pass_status", {}).get("status_counts", {})),
                "manifest_type": payload.get("manifest_type", ""),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
