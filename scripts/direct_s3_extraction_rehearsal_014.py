#!/usr/bin/env python3
"""Goal 014 bounded direct-S3 Water Observations extraction rehearsal."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from osgeo import gdal


REPO = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from event_window_hydrology_007 import (  # noqa: E402
    base_metric_fields,
    epsg_srs,
    format_value,
    rasterize_geometry,
    reset_retry_audit_log,
    retry_audit_summary,
    summarise_support_month,
    support_grid,
    warp_scene_to_grid,
)
from support_pathrow_metadata_013 import (  # noqa: E402
    direct_s3_item_sets,
    item_set_hashes,
    load_event_window_supports,
    stable_hash,
)


DEFAULT_CONFIG = REPO / "settings" / "direct_s3_extraction_rehearsal_014.json"
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
TIME_HISTORY_FIELDS = [
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
]
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
    "stac_items_found",
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
        "gdal_version": gdal.VersionInfo("--version"),
    }


def stable_row_hash(rows: list[dict[str, Any]], fields: list[str]) -> str:
    payload = [
        {field: str(row.get(field, "")) for field in fields}
        for row in sorted(rows, key=lambda row: tuple(str(row.get(field, "")) for field in fields))
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def is_blocked_raw_extension(path: Path) -> bool:
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
        "direct_s3_items_found",
        "readable_scene_count",
        "skipped_scene_count",
        "path_rows",
        "asset_key_hash",
        "item_id_hash",
        *base_metric_fields(),
        *TIME_HISTORY_FIELDS,
        "failure_or_caveat",
    ]


def comparison_fieldnames() -> list[str]:
    return [
        "month",
        "comparison_target",
        "comparison_status",
        "fields_compared",
        "differing_fields",
        "max_abs_numeric_difference",
        "legacy_bbox_extra_no_data_hint",
        "direct_readable_scene_count",
        "target_readable_scene_count",
        "direct_current_wet_area_m2",
        "target_current_wet_area_m2",
        "direct_current_proportion_wet",
        "target_current_proportion_wet",
        "target_status",
        "recommendation",
    ]


def validate_item_set_rows(
    rows: list[dict[str, Any]],
    support_id: str,
    months: list[str],
    path_rows: list[str],
    expected_month_counts: dict[str, int],
    goal013_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    filtered = [row for row in rows if row.get("support_id") == support_id]
    by_key = {(row.get("month", ""), row.get("path_row", "")): row for row in filtered}
    missing_path_rows: list[str] = []
    count_mismatches: list[str] = []
    hash_mismatches: list[str] = []
    month_counts: dict[str, int] = {}
    for month in months:
        total = 0
        for path_row in path_rows:
            key = (month, path_row)
            row = by_key.get(key)
            if row is None:
                missing_path_rows.append(f"{month}:{path_row}")
                continue
            total += int(row.get("item_count") or 0)
        month_counts[month] = total
        expected = int(expected_month_counts.get(month, -1))
        if expected >= 0 and total != expected:
            count_mismatches.append(f"{month}: expected {expected}, got {total}")

    if goal013_rows is not None:
        goal013_by_key = {
            (row.get("month", ""), row.get("path_row", "")): row
            for row in goal013_rows
            if row.get("support_id") == support_id
        }
        for month in months:
            for path_row in path_rows:
                key = (month, path_row)
                current = by_key.get(key)
                expected = goal013_by_key.get(key)
                if current is None or expected is None:
                    continue
                for field in ("item_count", "item_id_hash", "asset_key_hash"):
                    if str(current.get(field, "")) != str(expected.get(field, "")):
                        hash_mismatches.append(f"{month}:{path_row}:{field}")

    status = (
        "matched_goal013_item_sets"
        if not missing_path_rows and not count_mismatches and not hash_mismatches
        else "item_set_mismatch"
    )
    return {
        "status": status,
        "month_counts": month_counts,
        "path_rows": path_rows,
        "missing_path_rows": missing_path_rows,
        "count_mismatches": count_mismatches,
        "hash_mismatches": hash_mismatches,
    }


def summarise_direct_support_month(scene_values: list[np.ndarray], support_mask: np.ndarray) -> dict[str, Any]:
    return summarise_support_month(scene_values, support_mask)


def compare_metric_rows(
    month: str,
    direct: dict[str, Any],
    target: dict[str, Any],
    tolerances: dict[str, Any],
    fields: list[str] | None = None,
) -> dict[str, Any]:
    compared = fields or DEFAULT_COMPARISON_FIELDS
    differing: list[str] = []
    numeric_differences: dict[str, float] = {}
    for field in compared:
        direct_value = direct.get(field, "")
        target_value = target.get(field, "")
        if field in STRING_FIELDS:
            if normalised_text(direct_value) != normalised_text(target_value):
                differing.append(field)
            continue
        direct_number = to_float(direct_value)
        target_number = to_float(target_value)
        if direct_number is None or target_number is None:
            if normalised_text(direct_value) != normalised_text(target_value):
                differing.append(field)
            continue
        difference = abs(direct_number - target_number)
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


def legacy_bbox_extra_no_data_hint(direct: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    direct_scene_count = int(to_float(direct.get("readable_scene_count")) or 0)
    target_scene_count = int(to_float(target.get("readable_scene_count")) or 0)
    n_pixel = int(to_float(direct.get("n_pixel_u")) or 0)
    direct_no_data = int(to_float(direct.get("no_data_count")) or 0)
    target_no_data = int(to_float(target.get("no_data_count")) or 0)
    extra_scene_count = target_scene_count - direct_scene_count
    expected_extra_no_data = extra_scene_count * n_pixel
    area_difference = abs((to_float(direct.get("current_wet_area_m2")) or 0.0) - (to_float(target.get("current_wet_area_m2")) or 0.0))
    prop_difference = abs(
        (to_float(direct.get("current_proportion_wet")) or 0.0)
        - (to_float(target.get("current_proportion_wet")) or 0.0)
    )
    observed_extra_no_data = target_no_data - direct_no_data
    return {
        "matches_hint": bool(
            extra_scene_count > 0
            and n_pixel > 0
            and observed_extra_no_data == expected_extra_no_data
            and area_difference <= 0.5
            and prop_difference <= 0.000001
        ),
        "extra_scene_count": extra_scene_count,
        "expected_extra_no_data": expected_extra_no_data,
        "observed_extra_no_data": observed_extra_no_data,
    }


def configure_gdal() -> None:
    os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    gdal.SetConfigOption("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")


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


def validate_goal013_evidence(config: dict[str, Any]) -> dict[str, Any]:
    goal013 = config["goal013"]
    crosswalk_rows = read_csv(REPO / goal013["crosswalk_csv"])
    comparator_rows = read_csv(REPO / goal013["comparator_status_csv"])
    manifest = load_json(REPO / goal013["manifest_json"])
    support_id = config["primary_support_id"]
    crosswalk_support = [row for row in crosswalk_rows if row.get("support_id") == support_id]
    path_rows = sorted({row.get("path_row", "") for row in crosswalk_support if row.get("path_row")})
    coverage_statuses = sorted({row.get("coverage_status", "") for row in crosswalk_support})
    final_rows = [row for row in comparator_rows if row.get("comparator") == "final_equivalence_status"]
    final_status = final_rows[0].get("status", "") if final_rows else ""
    stac_status = manifest.get("stac_item_set_comparison", {}).get("status", "")
    expected_path_rows = sorted(config["path_rows"])
    status = "confirmed" if path_rows == expected_path_rows and coverage_statuses == ["complete"] and final_status == "equivalent" else "blocked"
    evidence = {
        "status": status,
        "support_id": support_id,
        "path_rows": path_rows,
        "expected_path_rows": expected_path_rows,
        "coverage_statuses": coverage_statuses,
        "final_equivalence_status": final_status,
        "stac_item_set_comparison_status": stac_status,
        "goal013_git_head_at_run": manifest.get("git_head_at_run", ""),
    }
    if status != "confirmed":
        raise RuntimeError(f"Goal 013 prerequisite evidence did not confirm bounded direct-S3 extraction: {evidence}")
    return evidence


def s3_href(config: dict[str, Any], asset_key: str) -> str:
    return f"s3://{config['s3']['bucket']}/{asset_key}"


def first_item(item_lookup: dict[str, list[dict[str, str]]], months: list[str], path_rows: list[str]) -> dict[str, str]:
    for month in months:
        for path_row in path_rows:
            items = item_lookup.get(f"{month}|{path_row}", [])
            if items:
                return items[0]
    raise RuntimeError("no direct-S3 Water Observations item available for raster-read probe")


def tiny_raster_read_probe(
    config: dict[str, Any],
    item: dict[str, str],
    bounds: tuple[float, float, float, float],
) -> dict[str, Any]:
    started = time.time()
    array = warp_scene_to_grid(s3_href(config, item["asset_key"]), bounds, 1, 1, config["reference_crs"], config=config)
    return {
        "status": "succeeded",
        "asset_key": item["asset_key"],
        "path_row": item.get("path_row", ""),
        "shape": list(array.shape),
        "min": int(np.min(array)),
        "max": int(np.max(array)),
        "elapsed_seconds": round(time.time() - started, 3),
    }


def support_record(config: dict[str, Any], support: dict[str, Any], month: str) -> dict[str, Any]:
    return {
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
        "month_rationale": "Goal 014 bounded direct-S3 extraction rehearsal month",
        "source_geometry": support["source"],
        "source_identifier": support["source_identifier"],
        "source_geometry_caveat": support["caveat"],
        "support_area_m2": support["support_area_m2"],
        "geometry_hash_sha256": support["geometry_hash_sha256"],
        "dea_product": config["source_product"],
        "dea_product_version": config["source_product_version"],
        "metric_spec_version": config["metric_spec_version"],
    }


def blank_time_history_values() -> dict[str, str]:
    return {field: "" for field in TIME_HISTORY_FIELDS}


def formatted_summary_row(row: dict[str, Any]) -> dict[str, Any]:
    formatted = {}
    for key, value in row.items():
        formatted[key] = format_value(value)
    return formatted


def build_support_grid(config: dict[str, Any], support: dict[str, Any]) -> dict[str, Any]:
    pixel_size = int(config["pixel_size_m"])
    bounds, geotransform, xsize, ysize = support_grid(support["geom_albers"], pixel_size)
    grid_pixels = xsize * ysize
    if grid_pixels > int(config["max_reference_grid_pixels"]):
        raise RuntimeError(f"reference grid has {grid_pixels} cells, above configured maximum")
    support_mask = rasterize_geometry(support["geom_albers"], epsg_srs(3577), geotransform, xsize, ysize)
    return {
        "bounds": bounds,
        "geotransform": geotransform,
        "xsize": xsize,
        "ysize": ysize,
        "grid_pixels": grid_pixels,
        "support_mask": support_mask,
        "support_mask_pixels": int(support_mask.sum()),
    }


def extract_direct_s3_metrics(
    config: dict[str, Any],
    support: dict[str, Any],
    grid: dict[str, Any],
    item_lookup: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    read_records: list[dict[str, Any]] = []
    bounds = grid["bounds"]
    support_mask = grid["support_mask"]
    for month in config["months"]:
        items: list[dict[str, str]] = []
        for path_row in config["path_rows"]:
            items.extend(item_lookup.get(f"{month}|{path_row}", []))
        items = sorted(items, key=lambda item: (item.get("asset_key", ""), item.get("item_id", "")))
        scene_arrays: list[np.ndarray] = []
        skipped: list[dict[str, str]] = []
        per_scene: list[dict[str, Any]] = []
        for item in items:
            href = s3_href(config, item["asset_key"])
            started = time.time()
            try:
                array = warp_scene_to_grid(
                    href,
                    bounds,
                    int(grid["xsize"]),
                    int(grid["ysize"]),
                    config["reference_crs"],
                    config=config,
                )
                scene_arrays.append(array)
                per_scene.append(
                    {
                        "item_id": item.get("item_id", ""),
                        "asset_key": item["asset_key"],
                        "path_row": item.get("path_row", ""),
                        "status": "readable",
                        "elapsed_seconds": round(time.time() - started, 3),
                    }
                )
            except Exception as exc:
                skipped.append({"item_id": item.get("item_id", ""), "asset_key": item["asset_key"], "reason": str(exc)})
                per_scene.append(
                    {
                        "item_id": item.get("item_id", ""),
                        "asset_key": item["asset_key"],
                        "path_row": item.get("path_row", ""),
                        "status": "skipped",
                        "reason": str(exc),
                        "elapsed_seconds": round(time.time() - started, 3),
                    }
                )
        metrics = summarise_direct_support_month(scene_arrays, support_mask)
        hashes = item_set_hashes(items)
        row = {
            **support_record(config, support, month),
            "access_method": "support geometry plus direct public S3 path/row COG reads and GDAL warp to EPSG:3577 support grid",
            "status": "computed_direct_s3_metrics" if scene_arrays else "blocked_no_readable_direct_s3_scene",
            "direct_s3_items_found": len(items),
            "readable_scene_count": len(scene_arrays),
            "skipped_scene_count": len(skipped),
            "path_rows": ";".join(config["path_rows"]),
            "asset_key_hash": hashes["asset_key_hash"],
            "item_id_hash": hashes["item_id_hash"],
            **metrics,
            **blank_time_history_values(),
            "failure_or_caveat": support["caveat"]
            if scene_arrays
            else "No direct-S3 Water Observations scene could be warped for this support/month.",
        }
        rows.append(formatted_summary_row(row))
        read_records.append(
            {
                "month": month,
                "direct_s3_item_count": len(items),
                "readable_scene_count": len(scene_arrays),
                "skipped_scene_count": len(skipped),
                "asset_key_hash": hashes["asset_key_hash"],
                "item_id_hash": hashes["item_id_hash"],
                "per_scene": per_scene,
                "skipped": skipped,
            }
        )
    return rows, read_records


def lookup_row(rows: list[dict[str, str]], support_id: str, month: str) -> dict[str, str] | None:
    for row in rows:
        if row.get("support_id") == support_id and row.get("month") == month:
            return row
    return None


def build_comparison_rows(config: dict[str, Any], summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    comparison_config = config["comparison"]
    event_rows = read_csv(REPO / comparison_config["event_window_series_csv"])
    full_window_rows = read_csv(REPO / comparison_config["full_window_status_csv"])
    summary_by_month = {row["month"]: row for row in summary_rows}
    comparison_rows: list[dict[str, Any]] = []
    support_id = config["primary_support_id"]
    for month in config["months"]:
        direct = summary_by_month[month]
        if month == "2018-01":
            target = lookup_row(full_window_rows, support_id, month) or {}
            comparison_rows.append(
                {
                    "month": month,
                    "comparison_target": "goal009_full_window_status_row",
                    "comparison_status": "new_direct_s3_rehearsal_row_for_endpoint_blocked_month"
                    if target.get("status") == "blocked_event_window_processing_error"
                    else "unexpected_full_window_status",
                    "fields_compared": "status_only",
                    "differing_fields": "",
                    "max_abs_numeric_difference": "",
                    "legacy_bbox_extra_no_data_hint": "",
                    "direct_readable_scene_count": direct.get("readable_scene_count", ""),
                    "target_readable_scene_count": target.get("readable_scene_count", ""),
                    "direct_current_wet_area_m2": direct.get("current_wet_area_m2", ""),
                    "target_current_wet_area_m2": target.get("current_wet_area_m2", ""),
                    "direct_current_proportion_wet": direct.get("current_proportion_wet", ""),
                    "target_current_proportion_wet": target.get("current_proportion_wet", ""),
                    "target_status": target.get("status", ""),
                    "recommendation": "record as bounded rehearsal evidence only; not full-window recovery",
                }
            )
            continue
        target = lookup_row(event_rows, support_id, month)
        if target is None:
            raise RuntimeError(f"missing event-window comparison target for {support_id} {month}")
        result = compare_metric_rows(month, direct, target, comparison_config["tolerances"], comparison_config["fields"])
        hint = legacy_bbox_extra_no_data_hint(direct, target)
        recommendation = (
            "eligible_for_larger_direct_s3_rehearsal"
            if result["comparison_status"] == "within_tolerance"
            else "do_not_scale; first build a path-row-filtered STAC or no-data-adjusted comparator baseline"
        )
        comparison_rows.append(
            {
                "month": month,
                "comparison_target": "goal007_event_window_stac_metrics",
                "comparison_status": result["comparison_status"],
                "fields_compared": result["fields_compared"],
                "differing_fields": result["differing_fields"],
                "max_abs_numeric_difference": round(float(result["max_abs_numeric_difference"]), 6),
                "legacy_bbox_extra_no_data_hint": hint,
                "direct_readable_scene_count": direct.get("readable_scene_count", ""),
                "target_readable_scene_count": target.get("readable_scene_count", ""),
                "direct_current_wet_area_m2": direct.get("current_wet_area_m2", ""),
                "target_current_wet_area_m2": target.get("current_wet_area_m2", ""),
                "direct_current_proportion_wet": direct.get("current_proportion_wet", ""),
                "target_current_proportion_wet": target.get("current_proportion_wet", ""),
                "target_status": target.get("status", ""),
                "recommendation": recommendation,
            }
        )
    return comparison_rows


def comparison_summary(comparison_rows: list[dict[str, Any]]) -> dict[str, Any]:
    overlapping = [row for row in comparison_rows if row["comparison_target"] == "goal007_event_window_stac_metrics"]
    mismatches = [row for row in overlapping if row["comparison_status"] != "within_tolerance"]
    status = "overlap_within_tolerance" if not mismatches else "overlap_mismatch_beyond_tolerance"
    return {
        "status": status,
        "overlap_month_count": len(overlapping),
        "overlap_mismatch_count": len(mismatches),
        "mismatch_months": [row["month"] for row in mismatches],
        "recommendation": "do_not_scale; run a comparator-baseline repair goal before full-window direct S3 extraction"
        if mismatches
        else "candidate_for_next_bounded_scale_rehearsal",
    }


def write_report(
    path: Path,
    config: dict[str, Any],
    item_validation: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> None:
    comparison_status = manifest["comparison_summary"]["status"]
    recommendation = manifest["comparison_summary"]["recommendation"]
    summary_table = "\n".join(
        f"| {row['month']} | {row['readable_scene_count']} | {row['clear_obs_count']} | {row['invalid_obs_count']} | {row['current_wet_area_m2']} | {row['current_proportion_wet']} | {row['quality_flag']} |"
        for row in summary_rows
    )
    comparison_table = "\n".join(
        f"| {row['month']} | {row['comparison_target']} | {row['comparison_status']} | {serialise_csv_value(row['differing_fields'])} | {row['recommendation']} |"
        for row in comparison_rows
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Goal 014 Direct S3 Extraction Rehearsal",
                "",
                f"Accessed date: `{config['accessed_date']}`.",
                "",
                "## Scope",
                "",
                "This bounded rehearsal computed base DEA Water Observations metrics for `NWB002` Narran Lake Nature Reserve only, using direct public S3 COG reads for the Goal 013 derived path/rows `092/081`, `093/080`, and `093/081` in `2018-01`, `2022-11`, and `2024-12`.",
                "",
                "No full `2018-01` through `2024-12` extraction, all-support extraction, biodiversity analysis, or derived time-history hydrology metrics were run.",
                "",
                "## Item-Set Validation",
                "",
                f"Item-set status: `{item_validation['status']}`.",
                "",
                "| Month | Direct S3 Water Observations item count |",
                "| --- | ---: |",
                *[f"| {month} | {count} |" for month, count in item_validation["month_counts"].items()],
                "",
                "The direct-S3 item counts and hashes were checked against Goal 013 before raster reads.",
                "",
                "## Direct-S3 Base Metrics",
                "",
                "| Month | Readable scenes | Clear obs | Invalid obs | Wet area m2 | Wet proportion | Quality |",
                "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
                summary_table,
                "",
                "The `2018-01` row is a bounded rehearsal metric for a month previously recorded as endpoint-blocked in Goal 009, not recovery of the full historical window.",
                "",
                "## Comparison",
                "",
                "| Month | Target | Status | Differing fields | Recommendation |",
                "| --- | --- | --- | --- | --- |",
                comparison_table,
                "",
                f"Overall comparison status: `{comparison_status}`.",
                "",
                "For overlapping months, current wet area, current wet proportion, wet observation count, dry observation count, valid support area, and quality flag are the fields that matter most for base wetness equivalence. The strict comparison also includes observation-denominator fields such as readable scene count, invalid observations, and clear-observation fraction.",
                "",
                "Where the strict comparison differs, the manifest records whether the pattern is consistent with legacy STAC bbox-only no-data scenes that are outside the Goal 013 support-derived path/row set.",
                "",
                "## Recommendation For Goal 015",
                "",
                recommendation + ".",
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
            REPO / config["staging_paths"]["raw"] / "probe.tif",
            REPO / config["staging_paths"]["intermediate"] / "probe.npy",
            REPO / config["staging_paths"]["output"] / "probe.json",
        ]
    )
    if ignored_check["status"] != "all_ignored":
        raise RuntimeError(f"Goal 014 staging paths are not all ignored: {ignored_check}")
    configure_gdal()
    reset_retry_audit_log()
    goal013_evidence = validate_goal013_evidence(config)
    supports = load_event_window_supports(config)
    support = next((item for item in supports if item["support_id"] == config["primary_support_id"]), None)
    if support is None:
        raise RuntimeError(f"support not found: {config['primary_support_id']}")
    grid = build_support_grid(config, support)
    primary_candidate = {
        "candidate_id": support["candidate_id"],
        "candidate_name": support["candidate_name"],
        "support_id": support["support_id"],
    }
    item_rows, item_lookup, s3_route_records = direct_s3_item_sets(
        config, primary_candidate, config["path_rows"], reuse_cache
    )
    goal013_item_rows = read_csv(REPO / config["goal013"]["item_sets_csv"])
    item_validation = validate_item_set_rows(
        item_rows,
        support_id=config["primary_support_id"],
        months=config["months"],
        path_rows=config["path_rows"],
        expected_month_counts={month: int(count) for month, count in config["expected_month_item_counts"].items()},
        goal013_rows=goal013_item_rows,
    )
    if item_validation["status"] != "matched_goal013_item_sets":
        raise RuntimeError(f"direct-S3 item sets do not match Goal 013: {item_validation}")
    probe = tiny_raster_read_probe(config, first_item(item_lookup, config["months"], config["path_rows"]), grid["bounds"])
    summary_rows, read_records = extract_direct_s3_metrics(config, support, grid, item_lookup)
    comparison_rows = build_comparison_rows(config, summary_rows)
    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    write_csv(outputs["summary_csv"], summary_rows, summary_fieldnames())
    write_csv(outputs["comparison_csv"], comparison_rows, comparison_fieldnames())
    compact_grid = {
        "crs": config["reference_crs"],
        "pixel_size_m": int(config["pixel_size_m"]),
        "xsize": int(grid["xsize"]),
        "ysize": int(grid["ysize"]),
        "grid_pixels": int(grid["grid_pixels"]),
        "support_mask_pixels": int(grid["support_mask_pixels"]),
        "bounds": [round(float(value), 3) for value in grid["bounds"]],
    }
    manifest = {
        "goal": config["goal"],
        "manifest_type": "direct_s3_extraction_rehearsal_014",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "accessed_date": config["accessed_date"],
        "command": config["run_command"] + (" --reuse-ignored-cache" if reuse_cache else ""),
        "config_path": repo_relative(config_path),
        "reuse_ignored_cache": reuse_cache,
        "git_head_at_run": git_head(),
        "git_status_at_run": git_status(),
        "host_facts": host_facts(),
        "source_urls": config["source_urls"],
        "support": {
            "candidate_id": support["candidate_id"],
            "candidate_name": support["candidate_name"],
            "support_id": support["support_id"],
            "geometry_hash_sha256": support["geometry_hash_sha256"],
            "support_area_m2": support["support_area_m2"],
            "source": support["source"],
            "source_identifier": support["source_identifier"],
            "caveat": support["caveat"],
        },
        "path_rows": config["path_rows"],
        "months": config["months"],
        "goal013_evidence": goal013_evidence,
        "item_set_validation": item_validation,
        "s3_route_records": s3_route_records,
        "support_grid": compact_grid,
        "tiny_raster_read_probe": probe,
        "read_records": read_records,
        "summary_row_count": len(summary_rows),
        "summary_row_hash": stable_row_hash(summary_rows, ["support_id", "month", "status", "asset_key_hash"]),
        "comparison_summary": comparison_summary(comparison_rows),
        "comparison_rows": comparison_rows,
        "retry_audit_summary": retry_audit_summary(),
        "outputs": {key: repo_relative(path) for key, path in outputs.items()},
        "staging_paths": config["staging_paths"],
        "staging_ignored_check": ignored_check,
        "staging_policy": config["commit_policy"],
        "remote_compute_used": False,
        "remote_compute_reason": "Mac mini tiny raster-read probe and bounded three-month extraction completed locally.",
        "elapsed_seconds": round(time.time() - started, 3),
    }
    write_json(outputs["manifest_json"], manifest)
    write_report(outputs["report_md"], config, item_validation, summary_rows, comparison_rows, manifest)
    write_json(REPO / config["staging_paths"]["output"] / "direct_s3_extraction_rehearsal_014_run.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to Goal 014 config JSON")
    parser.add_argument("--reuse-ignored-cache", action="store_true", help="Reuse ignored S3 listing/HEAD caches")
    args = parser.parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    manifest = run(config_path, args.reuse_ignored_cache)
    print(
        json.dumps(
            {
                "status": manifest["comparison_summary"]["status"],
                "summary_rows": manifest["summary_row_count"],
                "elapsed_seconds": manifest["elapsed_seconds"],
                "manifest": manifest["outputs"]["manifest_json"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
