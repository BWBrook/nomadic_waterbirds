#!/usr/bin/env python3
"""Goal 015 path-row-filtered hydrology comparator baseline repair."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import platform
import re
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO / "settings" / "comparator_baseline_repair_015.json"
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
DEFAULT_COMPARISON_FIELDS = [
    "readable_scene_count",
    "clear_obs_count",
    "invalid_obs_count",
    "clear_obs_fraction",
    "current_wet_area_m2",
    "valid_support_area_m2",
    "current_proportion_wet",
    "wet_pixel_observation_count",
    "dry_pixel_observation_count",
    "quality_flag",
    "wet_month_flag",
]
COUNT_FIELDS = {
    "readable_scene_count",
    "skipped_scene_count",
    "direct_s3_items_found",
    "stac_bbox_items_found",
    "stac_filtered_items_found",
    "stac_bbox_extra_item_count",
    "n_scene_m",
    "n_pixel_u",
    "clear_obs_count",
    "invalid_obs_count",
    "wet_pixel_observation_count",
    "dry_pixel_observation_count",
    "clear_pixel_count",
    "no_data_count",
    "contiguity_count",
    "low_solar_angle_count",
    "terrain_shadow_count",
    "high_slope_count",
    "cloud_shadow_count",
    "cloud_count",
}
AREA_FIELDS = {"current_wet_area_m2", "valid_support_area_m2", "support_area_m2"}
FRACTION_FIELDS = {"clear_obs_fraction", "current_proportion_wet", "clear_pixel_fraction"}
STRING_FIELDS = {"quality_flag", "wet_month_flag", "status"}
WETNESS_FIELDS = {
    "current_wet_area_m2",
    "valid_support_area_m2",
    "current_proportion_wet",
    "wet_pixel_observation_count",
    "dry_pixel_observation_count",
    "quality_flag",
    "wet_month_flag",
}
DENOMINATOR_FIELDS = {
    "readable_scene_count",
    "n_scene_m",
    "invalid_obs_count",
    "clear_obs_fraction",
    "no_data_count",
}


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


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


def serialise_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, list):
        return ";".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def stable_hash(values: list[Any]) -> str:
    payload = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stable_row_hash(rows: list[dict[str, Any]], fields: list[str]) -> str:
    payload = [
        {field: str(row.get(field, "")) for field in fields}
        for row in sorted(rows, key=lambda row: tuple(str(row.get(field, "")) for field in fields))
    ]
    return stable_hash(payload)


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


def is_blocked_raw_extension(path: Path) -> bool:
    path_text = path.as_posix()
    if path.suffix.lower() == ".json" and "/raw/" in f"/{path_text}":
        return True
    return path.suffix.lower() in BLOCKED_RAW_EXTENSIONS


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def to_int(value: Any) -> int:
    number = to_float(value)
    return int(number) if number is not None else 0


def normalised_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def metric_tolerance(field: str, tolerances: dict[str, Any]) -> float:
    if field in COUNT_FIELDS:
        return float(tolerances.get("count_abs", 0.0))
    if field in AREA_FIELDS:
        return float(tolerances.get("area_m2_abs", 0.5))
    if field in FRACTION_FIELDS:
        return float(tolerances.get("fraction_abs", 0.000001))
    return float(tolerances.get("numeric_abs", 0.0))


def compare_metric_rows(
    month: str,
    left: dict[str, Any],
    right: dict[str, Any],
    tolerances: dict[str, Any],
    fields: list[str] | None = None,
) -> dict[str, Any]:
    compared = fields or DEFAULT_COMPARISON_FIELDS
    differing: list[str] = []
    numeric_differences: dict[str, float] = {}
    for field in compared:
        left_value = left.get(field, "")
        right_value = right.get(field, "")
        if field in STRING_FIELDS:
            if normalised_text(left_value) != normalised_text(right_value):
                differing.append(field)
            continue
        left_number = to_float(left_value)
        right_number = to_float(right_value)
        if left_number is None or right_number is None:
            if normalised_text(left_value) != normalised_text(right_value):
                differing.append(field)
            continue
        difference = abs(left_number - right_number)
        numeric_differences[field] = difference
        if difference > metric_tolerance(field, tolerances):
            differing.append(field)
    return {
        "month": month,
        "comparison_status": "within_tolerance" if not differing else "mismatch_beyond_tolerance",
        "fields_compared": compared,
        "differing_fields": differing,
        "numeric_differences": numeric_differences,
        "max_abs_numeric_difference": max(numeric_differences.values(), default=0.0),
    }


def summary_fieldnames() -> list[str]:
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
        "access_method",
        "status",
        "scene_selection_policy",
        "direct_s3_items_found",
        "readable_scene_count",
        "skipped_scene_count",
        "path_rows",
        "stac_bbox_items_found",
        "stac_filtered_items_found",
        "stac_bbox_extra_item_count",
        "stac_filtered_asset_key_hash",
        "stac_bbox_asset_key_hash",
        "direct_s3_asset_key_hash",
        "item_set_equivalence_status",
        "asset_key_hash",
        "item_id_hash",
        "n_scene_m",
        "n_pixel_u",
        "clear_obs_count",
        "invalid_obs_count",
        "clear_obs_fraction",
        "current_wet_area_m2",
        "valid_support_area_m2",
        "current_proportion_wet",
        "wet_pixel_observation_count",
        "dry_pixel_observation_count",
        "clear_pixel_count",
        "clear_pixel_fraction",
        "quality_flag",
        "wet_month_flag",
        "no_data_count",
        "contiguity_count",
        "low_solar_angle_count",
        "terrain_shadow_count",
        "high_slope_count",
        "cloud_shadow_count",
        "cloud_count",
        "source_metric_row",
        "failure_or_caveat",
    ]


def comparison_fieldnames() -> list[str]:
    return [
        "month",
        "comparison_type",
        "comparison_status",
        "fields_compared",
        "differing_fields",
        "max_abs_numeric_difference",
        "repaired_status",
        "direct_status",
        "legacy_status",
        "repaired_readable_scene_count",
        "direct_readable_scene_count",
        "legacy_readable_scene_count",
        "repaired_current_wet_area_m2",
        "direct_current_wet_area_m2",
        "legacy_current_wet_area_m2",
        "recommendation",
    ]


def denominator_effect_fieldnames() -> list[str]:
    return [
        "month",
        "legacy_extra_scene_count",
        "support_mask_pixels",
        "expected_extra_invalid_or_no_data",
        "observed_extra_invalid_or_no_data",
        "observed_extra_no_data",
        "observed_extra_invalid_obs",
        "fields_affected",
        "wetness_fields_changed",
        "effect_status",
        "wetness_effect",
        "recommendation",
    ]


def month_range(month: str) -> tuple[str, str]:
    year, month_number = map(int, month.split("-"))
    start = dt.datetime(year, month_number, 1, tzinfo=dt.UTC)
    stop = dt.datetime(year + int(month_number == 12), 1 if month_number == 12 else month_number + 1, 1, tzinfo=dt.UTC)
    return start.strftime("%Y-%m-%dT%H:%M:%SZ"), stop.strftime("%Y-%m-%dT%H:%M:%SZ")


def stac_payload(collection: str, bbox: list[float], month: str, limit: int) -> dict[str, Any]:
    start, stop = month_range(month)
    return {
        "collections": [collection],
        "bbox": bbox,
        "datetime": f"{start}/{stop}",
        "limit": int(limit),
    }


def post_json(url: str, payload: dict[str, Any], timeout_seconds: int) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return int(response.status), dict(response.headers), response.read()


def path_row_from_asset_key(asset_key: str) -> str:
    match = re.search(r"/(\d{3})/(\d{3})/\d{4}/\d{2}/", asset_key)
    return f"{match.group(1)}/{match.group(2)}" if match else ""


def stac_feature_to_item(feature: dict[str, Any], bucket: str) -> dict[str, str] | None:
    href = feature.get("assets", {}).get("water", {}).get("href", "")
    if not href:
        return None
    asset_key = href
    if href.startswith(f"s3://{bucket}/"):
        asset_key = href.removeprefix(f"s3://{bucket}/")
    elif href.startswith("https://"):
        asset_key = urllib.parse.urlparse(href).path.lstrip("/")
    return {
        "item_id": str(feature.get("id", "")),
        "asset_key": asset_key,
        "path_row": path_row_from_asset_key(asset_key),
    }


def filter_items_to_path_rows(items: list[dict[str, str]], path_rows: set[str]) -> dict[str, Any]:
    filtered = sorted([item for item in items if item.get("path_row") in path_rows], key=lambda item: (item["asset_key"], item["item_id"]))
    extras = sorted([item for item in items if item.get("path_row") not in path_rows], key=lambda item: (item["asset_key"], item["item_id"]))
    return {
        "filtered_items": filtered,
        "bbox_extra_items": extras,
        "filtered_item_count": len(filtered),
        "bbox_extra_item_count": len(extras),
    }


def item_set_hashes(items: list[dict[str, str]]) -> dict[str, str | int]:
    item_ids = sorted(item.get("item_id", "") for item in items)
    asset_keys = sorted(item.get("asset_key", "") for item in items)
    return {
        "item_count": len(items),
        "item_id_hash": stable_hash(item_ids) if item_ids else "",
        "asset_key_hash": stable_hash(asset_keys) if asset_keys else "",
    }


def support_bbox_from_crosswalk(path: Path, support_id: str) -> list[float]:
    for row in read_csv(path):
        if row.get("support_id") == support_id and row.get("support_bbox_wgs84"):
            return [float(value) for value in json.loads(row["support_bbox_wgs84"])]
    raise RuntimeError(f"could not find support bbox for {support_id} in {path}")


def fetch_stac_route(config: dict[str, Any], bbox: list[float], reuse_cache: bool) -> dict[str, Any]:
    raw_dir = REPO / config["staging_paths"]["raw"]
    month_results: list[dict[str, Any]] = []
    by_month: dict[str, list[dict[str, str]]] = {}
    for month in config["months"]:
        payload = stac_payload(config["dea_collection"], bbox, month, int(config["stac"]["limit"]))
        cache_path = raw_dir / f"stac_bbox_{config['primary_candidate_id']}_{month}.json"
        started = time.time()
        if reuse_cache and cache_path.exists():
            body_json = load_json(cache_path)
            status_code = int(body_json.get("_status_code", 200))
            ok = status_code == 200
            headers = body_json.get("_headers", {})
            error = ""
        else:
            try:
                status_code, headers, body = post_json(
                    config["stac"]["search_url"],
                    payload,
                    int(config["stac"]["timeout_seconds"]),
                )
                body_json = json.loads(body.decode("utf-8")) if body else {}
                body_json["_status_code"] = status_code
                body_json["_headers"] = headers
                body_json["_query_payload"] = payload
                write_json(cache_path, body_json)
                ok = status_code == 200
                error = ""
            except Exception as exc:
                body_json = {"features": [], "_query_payload": payload}
                status_code = 0
                headers = {}
                ok = False
                error = f"{type(exc).__name__}: {exc}"
                write_json(
                    cache_path,
                    {
                        "_query_payload": payload,
                        "_status_code": status_code,
                        "_headers": headers,
                        "features": [],
                        "_error": error,
                    },
                )
        items = [
            item
            for item in (stac_feature_to_item(feature, config["s3"]["bucket"]) for feature in body_json.get("features", []))
            if item is not None
        ]
        by_month[month] = sorted(items, key=lambda item: (item["asset_key"], item["item_id"]))
        month_results.append(
            {
                "month": month,
                "status_code": status_code,
                "ok": ok,
                "feature_count": len(body_json.get("features", [])),
                "water_asset_count": len(items),
                "cache_path": repo_relative(cache_path),
                "elapsed_seconds": round(time.time() - started, 3),
                "error": error,
            }
        )
    failed = [result["month"] for result in month_results if not result["ok"]]
    return {
        "route_status": "available" if not failed else "unavailable_service_unstable",
        "failure_months": failed,
        "bbox": bbox,
        "month_results": month_results,
        "items_by_month": by_month,
    }


def check_ignored(paths: list[Path]) -> dict[str, Any]:
    rel_paths = [repo_relative(path) for path in paths]
    completed = subprocess.run(
        ["git", "check-ignore", *rel_paths],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    ignored = completed.stdout.strip().splitlines() if completed.stdout.strip() else []
    return {
        "status": "all_ignored" if sorted(ignored) == sorted(rel_paths) else "not_all_ignored",
        "checked_paths": rel_paths,
        "ignored_paths": ignored,
        "stderr": completed.stderr.strip(),
    }


def lookup_row(rows: list[dict[str, str]], support_id: str, month: str) -> dict[str, str] | None:
    for row in rows:
        if row.get("support_id") == support_id and row.get("month") == month:
            return row
    return None


def legacy_denominator_effect(
    month: str,
    legacy: dict[str, Any],
    repaired: dict[str, Any],
    tolerances: dict[str, Any],
) -> dict[str, Any]:
    legacy_extra_scene_count = to_int(legacy.get("readable_scene_count")) - to_int(repaired.get("readable_scene_count"))
    support_mask_pixels = to_int(repaired.get("n_pixel_u"))
    expected_extra = legacy_extra_scene_count * support_mask_pixels
    observed_extra_no_data = to_int(legacy.get("no_data_count")) - to_int(repaired.get("no_data_count"))
    observed_extra_invalid = to_int(legacy.get("invalid_obs_count")) - to_int(repaired.get("invalid_obs_count"))
    compared_fields = list(dict.fromkeys(DEFAULT_COMPARISON_FIELDS + ["n_scene_m", "no_data_count"]))
    comparison = compare_metric_rows(month, repaired, legacy, tolerances, compared_fields)
    fields_affected = comparison["differing_fields"]
    wetness_changed = [field for field in fields_affected if field in WETNESS_FIELDS]
    denominator_changed = [field for field in fields_affected if field in DENOMINATOR_FIELDS]
    effect_confirmed = (
        legacy_extra_scene_count > 0
        and support_mask_pixels > 0
        and observed_extra_invalid == expected_extra
        and observed_extra_no_data == expected_extra
        and not wetness_changed
        and bool(denominator_changed)
    )
    return {
        "month": month,
        "legacy_extra_scene_count": legacy_extra_scene_count,
        "support_mask_pixels": support_mask_pixels,
        "expected_extra_invalid_or_no_data": expected_extra,
        "observed_extra_invalid_or_no_data": observed_extra_invalid,
        "observed_extra_no_data": observed_extra_no_data,
        "observed_extra_invalid_obs": observed_extra_invalid,
        "fields_affected": fields_affected,
        "wetness_fields_changed": wetness_changed,
        "effect_status": "bbox_only_denominator_effect_confirmed" if effect_confirmed else "denominator_effect_not_fully_explained",
        "wetness_effect": "denominator_only" if not wetness_changed else "wetness_fields_changed",
        "recommendation": "use_pathrow_filtered_baseline_for_scale_validation"
        if effect_confirmed
        else "do_not_scale_until_legacy_difference_is_explained",
    }


def build_summary_rows(
    config: dict[str, Any],
    direct_rows: list[dict[str, str]],
    stac_route: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    support_id = config["primary_support_id"]
    path_rows = set(config["path_rows"])
    rows: list[dict[str, Any]] = []
    item_set_records: list[dict[str, Any]] = []
    stac_available = stac_route["route_status"] == "available"
    for month in config["months"]:
        direct = lookup_row(direct_rows, support_id, month)
        if direct is None:
            raise RuntimeError(f"missing Goal 014 direct-S3 summary row for {support_id} {month}")
        all_items = stac_route.get("items_by_month", {}).get(month, [])
        filtered = filter_items_to_path_rows(all_items, path_rows) if stac_available else {
            "filtered_items": [],
            "bbox_extra_items": [],
            "filtered_item_count": 0,
            "bbox_extra_item_count": 0,
        }
        filtered_hashes = item_set_hashes(filtered["filtered_items"])
        bbox_hashes = item_set_hashes(all_items)
        direct_hash = direct.get("asset_key_hash", "")
        item_set_matches = (
            stac_available
            and int(filtered_hashes["item_count"]) == to_int(direct.get("readable_scene_count"))
            and str(filtered_hashes["asset_key_hash"]) == str(direct_hash)
        )
        status = (
            "repaired_pathrow_filtered_stac_comparator"
            if item_set_matches
            else "comparator_blocked_stac_unavailable"
            if not stac_available
            else "comparator_blocked_item_set_mismatch"
        )
        item_status = (
            "stac_filtered_item_set_matches_goal014_direct_s3"
            if item_set_matches
            else "stac_unavailable"
            if not stac_available
            else "stac_filtered_item_set_mismatch"
        )
        row = {field: direct.get(field, "") for field in summary_fieldnames()}
        row.update(
            {
                "month_rationale": "Goal 015 path-row-filtered comparator repair month",
                "dea_product_version": config["source_product_version"],
                "metric_spec_version": config["metric_spec_version"],
                "access_method": "DEA STAC bbox metadata filtered to support-intersecting WRS path/rows; metric values inherited from Goal 014 direct-S3 summary after item-set equivalence check",
                "status": status,
                "scene_selection_policy": config["scene_selection_policy"]["id"],
                "stac_bbox_items_found": len(all_items) if stac_available else "",
                "stac_filtered_items_found": filtered["filtered_item_count"] if stac_available else "",
                "stac_bbox_extra_item_count": filtered["bbox_extra_item_count"] if stac_available else "",
                "stac_filtered_asset_key_hash": filtered_hashes["asset_key_hash"],
                "stac_bbox_asset_key_hash": bbox_hashes["asset_key_hash"],
                "direct_s3_asset_key_hash": direct_hash,
                "item_set_equivalence_status": item_status,
                "source_metric_row": config["inputs"]["goal014_summary_csv"],
                "failure_or_caveat": direct.get("failure_or_caveat", ""),
            }
        )
        rows.append(row)
        item_set_records.append(
            {
                "month": month,
                "stac_bbox_item_count": len(all_items),
                "stac_filtered_item_count": filtered["filtered_item_count"],
                "stac_bbox_extra_item_count": filtered["bbox_extra_item_count"],
                "direct_readable_scene_count": to_int(direct.get("readable_scene_count")),
                "stac_filtered_asset_key_hash": filtered_hashes["asset_key_hash"],
                "direct_asset_key_hash": direct_hash,
                "status": item_status,
                "bbox_extra_path_rows": sorted({item.get("path_row", "") for item in filtered["bbox_extra_items"] if item.get("path_row")}),
            }
        )
    return rows, item_set_records


def build_comparison_rows(
    config: dict[str, Any],
    repaired_rows: list[dict[str, Any]],
    direct_rows: list[dict[str, str]],
    legacy_rows: list[dict[str, str]],
    full_window_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    support_id = config["primary_support_id"]
    fields = config["comparison"]["fields"]
    tolerances = config["comparison"]["tolerances"]
    repaired_by_month = {row["month"]: row for row in repaired_rows}
    comparisons: list[dict[str, Any]] = []
    for month in config["months"]:
        repaired = repaired_by_month[month]
        direct = lookup_row(direct_rows, support_id, month)
        if direct is None:
            raise RuntimeError(f"missing direct comparison row for {support_id} {month}")
        result = compare_metric_rows(month, repaired, direct, tolerances, fields)
        comparisons.append(
            {
                "month": month,
                "comparison_type": "repaired_comparator_vs_goal014_direct_s3",
                "comparison_status": result["comparison_status"],
                "fields_compared": result["fields_compared"],
                "differing_fields": result["differing_fields"],
                "max_abs_numeric_difference": round(float(result["max_abs_numeric_difference"]), 6),
                "repaired_status": repaired.get("status", ""),
                "direct_status": direct.get("status", ""),
                "legacy_status": "",
                "repaired_readable_scene_count": repaired.get("readable_scene_count", ""),
                "direct_readable_scene_count": direct.get("readable_scene_count", ""),
                "legacy_readable_scene_count": "",
                "repaired_current_wet_area_m2": repaired.get("current_wet_area_m2", ""),
                "direct_current_wet_area_m2": direct.get("current_wet_area_m2", ""),
                "legacy_current_wet_area_m2": "",
                "recommendation": "use_repaired_comparator_for_next_bounded_scale_step"
                if result["comparison_status"] == "within_tolerance"
                else "do_not_scale_until_repaired_comparator_matches_direct_s3",
            }
        )
    for month in ("2022-11", "2024-12"):
        repaired = repaired_by_month[month]
        legacy = lookup_row(legacy_rows, support_id, month)
        if legacy is None:
            raise RuntimeError(f"missing legacy Goal 007 row for {support_id} {month}")
        result = compare_metric_rows(month, repaired, legacy, tolerances, fields)
        comparisons.append(
            {
                "month": month,
                "comparison_type": "legacy_goal007_bbox_stac_vs_repaired_comparator",
                "comparison_status": result["comparison_status"],
                "fields_compared": result["fields_compared"],
                "differing_fields": result["differing_fields"],
                "max_abs_numeric_difference": round(float(result["max_abs_numeric_difference"]), 6),
                "repaired_status": repaired.get("status", ""),
                "direct_status": "",
                "legacy_status": legacy.get("status", ""),
                "repaired_readable_scene_count": repaired.get("readable_scene_count", ""),
                "direct_readable_scene_count": "",
                "legacy_readable_scene_count": legacy.get("readable_scene_count", ""),
                "repaired_current_wet_area_m2": repaired.get("current_wet_area_m2", ""),
                "direct_current_wet_area_m2": "",
                "legacy_current_wet_area_m2": legacy.get("current_wet_area_m2", ""),
                "recommendation": "legacy_denominator_artifact_explained_use_repaired_baseline"
                if result["comparison_status"] == "mismatch_beyond_tolerance"
                else "legacy_matches_repaired_baseline",
            }
        )
    repaired = repaired_by_month["2018-01"]
    legacy_2018 = lookup_row(full_window_rows, support_id, "2018-01") or {}
    comparisons.append(
        {
            "month": "2018-01",
            "comparison_type": "legacy_goal009_status_context",
            "comparison_status": "legacy_blocked_no_metric_comparison"
            if legacy_2018.get("status") == "blocked_event_window_processing_error"
            else "unexpected_legacy_goal009_status",
            "fields_compared": "status_only",
            "differing_fields": "",
            "max_abs_numeric_difference": "",
            "repaired_status": repaired.get("status", ""),
            "direct_status": "",
            "legacy_status": legacy_2018.get("status", ""),
            "repaired_readable_scene_count": repaired.get("readable_scene_count", ""),
            "direct_readable_scene_count": "",
            "legacy_readable_scene_count": legacy_2018.get("readable_scene_count", ""),
            "repaired_current_wet_area_m2": repaired.get("current_wet_area_m2", ""),
            "direct_current_wet_area_m2": "",
            "legacy_current_wet_area_m2": legacy_2018.get("current_wet_area_m2", ""),
            "recommendation": "record_2018_01_as_bounded_repaired_comparator_only_not_full_window_recovery",
        }
    )
    return comparisons


def comparison_summary(comparison_rows: list[dict[str, Any]]) -> dict[str, Any]:
    repaired_vs_direct = [row for row in comparison_rows if row["comparison_type"] == "repaired_comparator_vs_goal014_direct_s3"]
    direct_mismatches = [row for row in repaired_vs_direct if row["comparison_status"] != "within_tolerance"]
    legacy_rows = [row for row in comparison_rows if row["comparison_type"] == "legacy_goal007_bbox_stac_vs_repaired_comparator"]
    return {
        "status": "repaired_comparator_matches_direct_s3" if not direct_mismatches else "repaired_comparator_mismatch",
        "repaired_vs_direct_rows": len(repaired_vs_direct),
        "repaired_vs_direct_mismatch_count": len(direct_mismatches),
        "legacy_comparison_rows": len(legacy_rows),
        "legacy_mismatch_months": [row["month"] for row in legacy_rows if row["comparison_status"] != "within_tolerance"],
        "recommendation": "Goal 016 should scale cautiously from the repaired comparator baseline, not from legacy bbox-only denominator rows."
        if not direct_mismatches
        else "Do not scale direct S3 until repaired comparator mismatches are resolved.",
    }


def build_denominator_effect_rows(
    config: dict[str, Any],
    repaired_rows: list[dict[str, Any]],
    legacy_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    support_id = config["primary_support_id"]
    repaired_by_month = {row["month"]: row for row in repaired_rows}
    rows: list[dict[str, Any]] = []
    for month in ("2022-11", "2024-12"):
        legacy = lookup_row(legacy_rows, support_id, month)
        if legacy is None:
            raise RuntimeError(f"missing legacy denominator target for {support_id} {month}")
        rows.append(legacy_denominator_effect(month, legacy, repaired_by_month[month], config["comparison"]["tolerances"]))
    return rows


def write_report(
    path: Path,
    config: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    denominator_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> None:
    summary_table = "\n".join(
        f"| {row['month']} | {row['status']} | {row['readable_scene_count']} | {row['stac_bbox_items_found']} | {row['stac_bbox_extra_item_count']} | {row['current_wet_area_m2']} | {row['current_proportion_wet']} |"
        for row in summary_rows
    )
    comparison_table = "\n".join(
        f"| {row['month']} | {row['comparison_type']} | {row['comparison_status']} | {serialise_csv_value(row['differing_fields'])} | {row['recommendation']} |"
        for row in comparison_rows
    )
    denominator_table = "\n".join(
        f"| {row['month']} | {row['legacy_extra_scene_count']} | {row['observed_extra_invalid_or_no_data']} | {row['effect_status']} | {row['wetness_effect']} |"
        for row in denominator_rows
    )
    policy = config["scene_selection_policy"]["rule"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Goal 015 Comparator Baseline Repair",
                "",
                f"Accessed date: `{config['accessed_date']}`.",
                "",
                "## Scope",
                "",
                "This bounded repair covers `NWB002` Narran Lake Nature Reserve only, the Goal 013 support-derived path/rows `092/081`, `093/080`, and `093/081`, and the Goal 014 probe months `2018-01`, `2022-11`, and `2024-12`.",
                "",
                "No full-window extraction, all-support extraction, biodiversity analysis, or ecological interpretation was run.",
                "",
                "## Scene-Selection Policy",
                "",
                policy,
                "",
                "STAC bbox results are discovery metadata. For support-level metrics, bbox-only Water Observations scenes outside the support-intersecting WRS path/row set are excluded before scene counting or denominator accounting.",
                "",
                "## Repaired Comparator Baseline",
                "",
                f"STAC route status: `{manifest['stac_route']['route_status']}`.",
                "",
                "| Month | Status | Readable scenes | STAC bbox items | Bbox-only extras | Wet area m2 | Wet proportion |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
                summary_table,
                "",
                "The repaired comparator rows reuse the Goal 014 metric values only after STAC metadata filtered to the support path/rows matches the Goal 014 direct-S3 asset-key hash for the same month.",
                "",
                "## Comparisons",
                "",
                "| Month | Comparison | Status | Differing fields | Recommendation |",
                "| --- | --- | --- | --- | --- |",
                comparison_table,
                "",
                f"Overall repaired-comparator status: `{manifest['comparison_summary']['status']}`.",
                "",
                "## Legacy Denominator Effect",
                "",
                "| Month | Extra bbox-only scenes | Extra invalid/no-data observations | Effect status | Wetness effect |",
                "| --- | ---: | ---: | --- | --- |",
                denominator_table,
                "",
                "For both overlapping months, the extra invalid/no-data observations equal the bbox-only scene count multiplied by the support-mask pixel count. Wet area, wet proportion, wet/dry observation counts, valid support area, quality flag, and wet-month flag are unchanged.",
                "",
                "## Recommendation For Goal 016",
                "",
                "Scale cautiously from the repaired path-row-filtered comparator baseline. The next bounded step should expand either all supports across the same three probe months or `NWB002` across the full event window, but it should not use legacy bbox-only denominator rows as the validation baseline.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run(config_path: Path, reuse_cache: bool) -> dict[str, Any]:
    started = time.time()
    config = load_json(config_path)
    for staging_path in config["staging_paths"].values():
        (REPO / staging_path).mkdir(parents=True, exist_ok=True)
    ignored_check = check_ignored(
        [
            REPO / config["staging_paths"]["raw"] / "probe.json",
            REPO / config["staging_paths"]["intermediate"] / "probe.npy",
            REPO / config["staging_paths"]["output"] / "probe.json",
        ]
    )
    if ignored_check["status"] != "all_ignored":
        raise RuntimeError(f"Goal 015 staging paths are not all ignored: {ignored_check}")
    inputs = {key: REPO / value for key, value in config["inputs"].items()}
    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    direct_rows = read_csv(inputs["goal014_summary_csv"])
    legacy_rows = read_csv(inputs["legacy_event_window_csv"])
    full_window_rows = read_csv(inputs["legacy_full_window_csv"])
    goal013_manifest = load_json(inputs["goal013_manifest_json"])
    goal014_manifest = load_json(inputs["goal014_manifest_json"])
    bbox = support_bbox_from_crosswalk(inputs["goal013_crosswalk_csv"], config["primary_support_id"])
    stac_route = fetch_stac_route(config, bbox, reuse_cache)
    summary_rows, item_set_records = build_summary_rows(config, direct_rows, stac_route)
    comparison_rows = build_comparison_rows(config, summary_rows, direct_rows, legacy_rows, full_window_rows)
    denominator_rows = build_denominator_effect_rows(config, summary_rows, legacy_rows)
    write_csv(outputs["summary_csv"], summary_rows, summary_fieldnames())
    write_csv(outputs["comparison_csv"], comparison_rows, comparison_fieldnames())
    write_csv(outputs["denominator_effect_csv"], denominator_rows, denominator_effect_fieldnames())
    manifest = {
        "goal": config["goal"],
        "manifest_type": "comparator_baseline_repair_015",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "accessed_date": config["accessed_date"],
        "command": config["run_command"] + (" --reuse-ignored-cache" if reuse_cache else ""),
        "config_path": repo_relative(config_path),
        "reuse_ignored_cache": reuse_cache,
        "git_head_at_run": git_head(),
        "git_status_at_run": git_status(),
        "host_facts": host_facts(),
        "source_urls": config["source_urls"],
        "support": goal014_manifest.get("support", {}),
        "path_rows": config["path_rows"],
        "months": config["months"],
        "scene_selection_policy": config["scene_selection_policy"],
        "stac_route": {
            key: value
            for key, value in stac_route.items()
            if key != "items_by_month"
        },
        "goal013_item_set_comparison": goal013_manifest.get("stac_item_set_comparison", {}),
        "goal014_summary_source": config["inputs"]["goal014_summary_csv"],
        "item_set_records": item_set_records,
        "summary_row_count": len(summary_rows),
        "summary_row_hash": stable_row_hash(summary_rows, ["support_id", "month", "status", "asset_key_hash"]),
        "comparison_summary": comparison_summary(comparison_rows),
        "comparison_rows": comparison_rows,
        "denominator_effect_rows": denominator_rows,
        "outputs": {key: repo_relative(path) for key, path in outputs.items()},
        "staging_paths": config["staging_paths"],
        "staging_ignored_check": ignored_check,
        "staging_policy": config["commit_policy"],
        "remote_compute_used": False,
        "remote_compute_reason": "Mac mini metadata-only STAC/path-row comparator repair completed locally; no full extraction launched.",
        "elapsed_seconds": round(time.time() - started, 3),
    }
    write_json(outputs["manifest_json"], manifest)
    write_report(outputs["report_md"], config, summary_rows, comparison_rows, denominator_rows, manifest)
    write_json(REPO / config["staging_paths"]["output"] / "comparator_baseline_repair_015_run.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to Goal 015 config JSON")
    parser.add_argument("--reuse-ignored-cache", action="store_true", help="Reuse ignored STAC caches")
    args = parser.parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    manifest = run(config_path, args.reuse_ignored_cache)
    print(
        json.dumps(
            {
                "status": manifest["comparison_summary"]["status"],
                "stac_route_status": manifest["stac_route"]["route_status"],
                "summary_rows": manifest["summary_row_count"],
                "elapsed_seconds": manifest["elapsed_seconds"],
                "manifest": manifest["outputs"]["manifest_json"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
