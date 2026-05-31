#!/usr/bin/env python3
"""Goal 016 bounded all-support direct-S3 Water Observations probe."""

from __future__ import annotations

import argparse
import collections
import copy
import csv
import datetime as dt
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


REPO = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from direct_s3_extraction_rehearsal_014 import (  # noqa: E402
    AREA_FIELDS,
    COUNT_FIELDS,
    DEFAULT_COMPARISON_FIELDS,
    FRACTION_FIELDS,
    STRING_FIELDS,
    build_support_grid,
    check_ignored,
    configure_gdal,
    formatted_summary_row,
    git_head,
    git_status,
    host_facts as gdal_host_facts,
    load_json,
    metric_tolerance,
    normalised_text,
    read_csv,
    repo_relative,
    serialise_csv_value,
    stable_row_hash,
    summarise_direct_support_month,
    to_float,
    write_csv,
    write_json,
)
from event_window_hydrology_007 import (  # noqa: E402
    base_metric_fields,
    blocked_metric_values,
    format_value,
    reset_retry_audit_log,
    retry_audit_summary,
    warp_scene_to_grid,
)
from support_pathrow_metadata_013 import (  # noqa: E402
    direct_s3_item_sets,
    item_set_hashes,
    load_event_window_supports,
)


DEFAULT_CONFIG = REPO / "settings" / "direct_s3_all_support_probe_016.json"
COMPUTED_STATUS = "computed_direct_s3_metrics"
REQUIRED_STATUSES = {
    COMPUTED_STATUS,
    "blocked_no_items_found",
    "blocked_s3_listing_failure",
    "blocked_cog_read_failure",
    "blocked_mask_or_geometry_failure",
    "blocked_remote_or_route_unavailable",
    "blocked_unclassified_failure",
}
STATUS_VOCABULARY = {
    *REQUIRED_STATUSES,
}
COMPARISON_STATUSES = {
    "within_tolerance",
    "wetness_within_tolerance_denominator_diff",
    "wetness_diff",
    "missing_or_blocked_reference",
    "computed_row_blocked",
    "not_compared",
}
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
WETNESS_FIELDS = {
    "current_wet_area_m2",
    "valid_support_area_m2",
    "current_proportion_wet",
    "wet_pixel_observation_count",
    "dry_pixel_observation_count",
}
DENOMINATOR_FIELDS = {
    "readable_scene_count",
    "n_scene_m",
    "clear_obs_count",
    "invalid_obs_count",
    "clear_obs_fraction",
    "no_data_count",
    "quality_flag",
    "wet_month_flag",
}
REFERENCE_COMPUTED_STATUSES = {
    "computed_event_window_metrics",
    "computed_direct_s3_metrics",
    "repaired_pathrow_filtered_stac_comparator",
}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def is_blocked_raw_extension(path: Path) -> bool:
    path_text = path.as_posix()
    if path.suffix.lower() == ".json" and "/raw/" in f"/{path_text}":
        return True
    return path.suffix.lower() in BLOCKED_RAW_EXTENSIONS


def host_facts() -> dict[str, str]:
    facts = gdal_host_facts()
    facts.update(
        {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
        }
    )
    return facts


def expected_support_month_grid(supports: list[dict[str, Any]], months: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for support in sorted(supports, key=lambda row: str(row.get("support_id", ""))):
        for month in sorted(months):
            rows.append({"support_id": support["support_id"], "candidate_id": support.get("candidate_id", ""), "month": month})
    return rows


def path_rows_by_support(crosswalk_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    grouped: dict[str, set[str]] = collections.defaultdict(set)
    for row in crosswalk_rows:
        support_id = str(row.get("support_id", "")).strip()
        path_row = str(row.get("path_row", "")).strip()
        if support_id and path_row:
            grouped[support_id].add(path_row)
    return {support_id: sorted(path_rows) for support_id, path_rows in grouped.items()}


def status_for_failure(stage: str, _exc: Exception | None = None) -> str:
    return {
        "s3_listing": "blocked_s3_listing_failure",
        "cog_read": "blocked_cog_read_failure",
        "mask": "blocked_mask_or_geometry_failure",
        "geometry": "blocked_mask_or_geometry_failure",
        "remote": "blocked_remote_or_route_unavailable",
        "no_items": "blocked_no_items_found",
    }.get(stage, "blocked_unclassified_failure")


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
        "scene_selection_policy",
        "access_method",
        "status",
        "failure_class",
        "direct_s3_items_found",
        "readable_scene_count",
        "skipped_scene_count",
        "path_rows",
        "asset_key_hash",
        "item_id_hash",
        *base_metric_fields(),
        "failure_or_caveat",
    ]


def support_summary_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "candidate_name",
        "support_id",
        "display_name",
        "support_level",
        "support_type",
        "path_rows",
        "expected_month_count",
        "computed_month_count",
        "blocked_month_count",
        "quality_high_count",
        "quality_minimum_count",
        "quality_fail_count",
        "wet_month_count",
        "status_counts",
        "caveat",
    ]


def comparison_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "support_id",
        "month",
        "reference_source",
        "comparison_status",
        "fields_compared",
        "differing_fields",
        "wetness_differing_fields",
        "denominator_differing_fields",
        "max_abs_numeric_difference",
        "computed_status",
        "reference_status",
        "computed_readable_scene_count",
        "reference_readable_scene_count",
        "computed_current_wet_area_m2",
        "reference_current_wet_area_m2",
        "computed_current_proportion_wet",
        "reference_current_proportion_wet",
        "recommendation",
    ]


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
        "month_rationale": "Goal 016 bounded all-support direct-S3 probe month",
        "source_geometry": support["source"],
        "source_identifier": support["source_identifier"],
        "source_geometry_caveat": support["caveat"],
        "support_area_m2": support["support_area_m2"],
        "geometry_hash_sha256": support["geometry_hash_sha256"],
        "dea_product": config["source_product"],
        "dea_product_version": config["source_product_version"],
        "metric_spec_version": config["metric_spec_version"],
        "scene_selection_policy": config["scene_selection_policy"]["id"],
    }


def blocked_summary_row(
    config: dict[str, Any],
    support: dict[str, Any],
    month: str,
    path_rows: list[str],
    status: str,
    failure_class: str,
    caveat: str,
    items: list[dict[str, str]] | None = None,
    skipped_count: int = 0,
) -> dict[str, Any]:
    hashes = item_set_hashes(items or [])
    row = {
        **support_record(config, support, month),
        "access_method": "direct public S3 path/row COG reads blocked before complete base metrics",
        "status": status,
        "failure_class": failure_class,
        "direct_s3_items_found": hashes["item_count"],
        "readable_scene_count": 0,
        "skipped_scene_count": skipped_count,
        "path_rows": ";".join(path_rows),
        "asset_key_hash": hashes["asset_key_hash"],
        "item_id_hash": hashes["item_id_hash"],
        **blocked_metric_values(),
        "failure_or_caveat": caveat,
    }
    return formatted_summary_row(row)


def metric_difference(
    computed: dict[str, Any],
    reference: dict[str, Any],
    tolerances: dict[str, Any],
    fields: list[str],
) -> dict[str, Any]:
    differing: list[str] = []
    wetness_differing: list[str] = []
    denominator_differing: list[str] = []
    numeric_differences: dict[str, float] = {}
    for field in fields:
        left = computed.get(field, "")
        right = reference.get(field, "")
        if field in STRING_FIELDS:
            differs = normalised_text(left) != normalised_text(right)
        else:
            left_number = to_float(left)
            right_number = to_float(right)
            if left_number is None or right_number is None:
                differs = normalised_text(left) != normalised_text(right)
            else:
                difference = abs(left_number - right_number)
                numeric_differences[field] = difference
                differs = difference > metric_tolerance(field, tolerances)
        if differs:
            differing.append(field)
            if field in WETNESS_FIELDS:
                wetness_differing.append(field)
            if field in DENOMINATOR_FIELDS or field in COUNT_FIELDS or field in FRACTION_FIELDS:
                denominator_differing.append(field)
    return {
        "fields_compared": fields,
        "differing_fields": differing,
        "wetness_differing_fields": wetness_differing,
        "denominator_differing_fields": denominator_differing,
        "max_abs_numeric_difference": max(numeric_differences.values(), default=0.0),
    }


def classify_comparison(
    computed: dict[str, Any],
    reference: dict[str, Any],
    tolerances: dict[str, Any],
    fields: list[str] | None = None,
) -> dict[str, Any]:
    compared_fields = fields or DEFAULT_COMPARISON_FIELDS
    computed_status = str(computed.get("status", ""))
    reference_status = str(reference.get("status", ""))
    if computed_status != COMPUTED_STATUS:
        return {
            "comparison_status": "computed_row_blocked",
            "fields_compared": compared_fields,
            "differing_fields": [],
            "wetness_differing_fields": [],
            "denominator_differing_fields": [],
            "max_abs_numeric_difference": "",
        }
    if not reference or reference_status not in REFERENCE_COMPUTED_STATUSES:
        return {
            "comparison_status": "missing_or_blocked_reference",
            "fields_compared": compared_fields,
            "differing_fields": [],
            "wetness_differing_fields": [],
            "denominator_differing_fields": [],
            "max_abs_numeric_difference": "",
        }
    diff = metric_difference(computed, reference, tolerances, compared_fields)
    if not diff["differing_fields"]:
        status = "within_tolerance"
    elif not diff["wetness_differing_fields"]:
        status = "wetness_within_tolerance_denominator_diff"
    else:
        status = "wetness_diff"
    return {"comparison_status": status, **diff}


def lookup_row(rows: list[dict[str, str]], support_id: str, month: str) -> dict[str, str] | None:
    for row in rows:
        if row.get("support_id") == support_id and row.get("month") == month:
            return row
    return None


def comparison_recommendation(status: str, reference_source: str) -> str:
    if status == "within_tolerance":
        return "use_as_bounded_validation_evidence"
    if status == "wetness_within_tolerance_denominator_diff":
        return "record_denominator_only_scene_selection_difference"
    if status == "wetness_diff":
        return "review_before_scale_up"
    if status == "computed_row_blocked":
        return "resolve_computed_row_blocker_before_using_reference"
    if status == "missing_or_blocked_reference" and reference_source == "goal009_full_window_context":
        return "record_as_context_only_not_full_window_recovery"
    if status == "missing_or_blocked_reference":
        return "record_missing_or_blocked_reference"
    return "not_compared"


def comparison_row(
    computed: dict[str, Any],
    reference: dict[str, Any],
    reference_source: str,
    tolerances: dict[str, Any],
    fields: list[str],
) -> dict[str, Any]:
    result = classify_comparison(computed, reference, tolerances, fields)
    status = result["comparison_status"]
    return {
        "candidate_id": computed.get("candidate_id", ""),
        "support_id": computed.get("support_id", ""),
        "month": computed.get("month", ""),
        "reference_source": reference_source,
        "comparison_status": status,
        "fields_compared": result["fields_compared"],
        "differing_fields": result["differing_fields"],
        "wetness_differing_fields": result["wetness_differing_fields"],
        "denominator_differing_fields": result["denominator_differing_fields"],
        "max_abs_numeric_difference": result["max_abs_numeric_difference"],
        "computed_status": computed.get("status", ""),
        "reference_status": reference.get("status", ""),
        "computed_readable_scene_count": computed.get("readable_scene_count", ""),
        "reference_readable_scene_count": reference.get("readable_scene_count", ""),
        "computed_current_wet_area_m2": computed.get("current_wet_area_m2", ""),
        "reference_current_wet_area_m2": reference.get("current_wet_area_m2", ""),
        "computed_current_proportion_wet": computed.get("current_proportion_wet", ""),
        "reference_current_proportion_wet": reference.get("current_proportion_wet", ""),
        "recommendation": comparison_recommendation(status, reference_source),
    }


def load_route_evidence(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    route_path = path if path.is_absolute() else REPO / path
    if not route_path.exists():
        return {"status": "missing_route_evidence_file", "path": repo_relative(route_path)}
    return load_json(route_path)


def selected_months(config: dict[str, Any], month_filter: str | None) -> list[str]:
    if month_filter:
        if month_filter not in config["months"]:
            raise RuntimeError(f"month filter is outside configured Goal 016 months: {month_filter}")
        return [month_filter]
    return list(config["months"])


def selected_supports(
    config: dict[str, Any],
    support_filter: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, list[str]]]:
    summary_rows = read_csv(REPO / config["inputs"]["event_window_summary_csv"])
    expected_support_ids = [row["support_id"] for row in summary_rows]
    supports = load_event_window_supports(config)
    support_lookup = {support["support_id"]: support for support in supports}
    missing = sorted(set(expected_support_ids) - set(support_lookup))
    if missing:
        raise RuntimeError(f"event-window supports missing from rebuilt support set: {missing}")
    selected_ids = [support_filter] if support_filter else expected_support_ids
    if support_filter and support_filter not in expected_support_ids:
        raise RuntimeError(f"support filter is outside current event-window support set: {support_filter}")
    selected = [support_lookup[support_id] for support_id in selected_ids]
    crosswalk_rows = read_csv(REPO / config["inputs"]["support_pathrow_crosswalk_csv"])
    pathrow_map = path_rows_by_support(crosswalk_rows)
    missing_pathrows = sorted(support["support_id"] for support in selected if support["support_id"] not in pathrow_map)
    if missing_pathrows:
        raise RuntimeError(f"selected supports missing Goal 013 path-row coverage: {missing_pathrows}")
    return selected, summary_rows, pathrow_map


def config_for_months(config: dict[str, Any], months: list[str]) -> dict[str, Any]:
    run_config = copy.deepcopy(config)
    run_config["months"] = months
    return run_config


def s3_href(config: dict[str, Any], asset_key: str) -> str:
    return f"s3://{config['s3']['bucket']}/{asset_key}"


def extract_rows(
    config: dict[str, Any],
    supports: list[dict[str, Any]],
    months: list[str],
    pathrow_map: dict[str, list[str]],
    reuse_cache: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    read_records: list[dict[str, Any]] = []
    item_set_records: list[dict[str, Any]] = []
    route_records: list[dict[str, Any]] = []
    grid_records: list[dict[str, Any]] = []
    run_config = config_for_months(config, months)
    for index, support in enumerate(sorted(supports, key=lambda item: item["support_id"]), start=1):
        support_id = support["support_id"]
        path_rows = pathrow_map[support_id]
        print(f"processing support {index}/{len(supports)} {support_id}", flush=True)
        try:
            grid = build_support_grid(config, support)
            grid_records.append(
                {
                    "support_id": support_id,
                    "crs": config["reference_crs"],
                    "pixel_size_m": int(config["pixel_size_m"]),
                    "xsize": int(grid["xsize"]),
                    "ysize": int(grid["ysize"]),
                    "grid_pixels": int(grid["grid_pixels"]),
                    "support_mask_pixels": int(grid["support_mask_pixels"]),
                    "bounds": [round(float(value), 3) for value in grid["bounds"]],
                }
            )
        except Exception as exc:
            status = status_for_failure("mask", exc)
            for month in months:
                rows.append(
                    blocked_summary_row(
                        config,
                        support,
                        month,
                        path_rows,
                        status,
                        "support_grid_or_mask",
                        f"{type(exc).__name__}: {exc}",
                    )
                )
            continue

        candidate = {
            "candidate_id": support["candidate_id"],
            "candidate_name": support["candidate_name"],
            "support_id": support_id,
        }
        try:
            item_rows, item_lookup, support_route_records = direct_s3_item_sets(run_config, candidate, path_rows, reuse_cache)
            item_set_records.extend(item_rows)
            route_records.extend({**record, "support_id": support_id} for record in support_route_records)
        except Exception as exc:
            status = status_for_failure("s3_listing", exc)
            for month in months:
                rows.append(
                    blocked_summary_row(
                        config,
                        support,
                        month,
                        path_rows,
                        status,
                        "direct_s3_listing",
                        f"{type(exc).__name__}: {exc}",
                    )
                )
            continue

        bounds = grid["bounds"]
        support_mask = grid["support_mask"]
        for month in months:
            items: list[dict[str, str]] = []
            for path_row in path_rows:
                items.extend(item_lookup.get(f"{month}|{path_row}", []))
            items = sorted(items, key=lambda item: (item.get("asset_key", ""), item.get("item_id", "")))
            hashes = item_set_hashes(items)
            if not items:
                rows.append(
                    blocked_summary_row(
                        config,
                        support,
                        month,
                        path_rows,
                        "blocked_no_items_found",
                        "direct_s3_no_items",
                        "No direct-S3 Water Observations COGs were found for this support/month path-row set.",
                        items=[],
                    )
                )
                read_records.append(
                    {
                        "support_id": support_id,
                        "month": month,
                        "direct_s3_item_count": 0,
                        "readable_scene_count": 0,
                        "skipped_scene_count": 0,
                        "status": "blocked_no_items_found",
                    }
                )
                continue

            scene_arrays: list[np.ndarray] = []
            skipped: list[dict[str, str]] = []
            for item in items:
                try:
                    scene_arrays.append(
                        warp_scene_to_grid(
                            s3_href(config, item["asset_key"]),
                            bounds,
                            int(grid["xsize"]),
                            int(grid["ysize"]),
                            config["reference_crs"],
                            config=config,
                        )
                    )
                except Exception as exc:
                    skipped.append(
                        {
                            "item_id": item.get("item_id", ""),
                            "asset_key": item.get("asset_key", ""),
                            "path_row": item.get("path_row", ""),
                            "reason": f"{type(exc).__name__}: {exc}",
                        }
                    )
            if not scene_arrays:
                rows.append(
                    blocked_summary_row(
                        config,
                        support,
                        month,
                        path_rows,
                        "blocked_cog_read_failure",
                        "direct_s3_cog_read",
                        "No direct-S3 Water Observations COG could be warped for this support/month.",
                        items=items,
                        skipped_count=len(skipped),
                    )
                )
                read_records.append(
                    {
                        "support_id": support_id,
                        "month": month,
                        "direct_s3_item_count": len(items),
                        "readable_scene_count": 0,
                        "skipped_scene_count": len(skipped),
                        "status": "blocked_cog_read_failure",
                        "skipped_sample": skipped[:5],
                    }
                )
                continue

            metrics = summarise_direct_support_month(scene_arrays, support_mask)
            caveat = support["caveat"]
            failure_class = ""
            if skipped:
                failure_class = "partial_direct_s3_cog_read"
                caveat = caveat + f" Partial read: {len(skipped)} of {len(items)} scenes skipped."
            row = {
                **support_record(config, support, month),
                "access_method": "support geometry plus direct public S3 path/row COG reads and GDAL warp to EPSG:3577 support grid",
                "status": COMPUTED_STATUS,
                "failure_class": failure_class,
                "direct_s3_items_found": len(items),
                "readable_scene_count": len(scene_arrays),
                "skipped_scene_count": len(skipped),
                "path_rows": ";".join(path_rows),
                "asset_key_hash": hashes["asset_key_hash"],
                "item_id_hash": hashes["item_id_hash"],
                **metrics,
                "failure_or_caveat": caveat,
            }
            rows.append(formatted_summary_row(row))
            read_records.append(
                {
                    "support_id": support_id,
                    "month": month,
                    "direct_s3_item_count": len(items),
                    "readable_scene_count": len(scene_arrays),
                    "skipped_scene_count": len(skipped),
                    "asset_key_hash": hashes["asset_key_hash"],
                    "item_id_hash": hashes["item_id_hash"],
                    "status": COMPUTED_STATUS,
                    "skipped_sample": skipped[:5],
                }
            )
    rows.sort(key=lambda row: (str(row.get("support_id", "")), str(row.get("month", ""))))
    return rows, {
        "read_records": read_records,
        "item_set_records": item_set_records,
        "s3_route_records": route_records,
        "support_grids": grid_records,
    }


def build_support_summary(rows: list[dict[str, Any]], pathrow_map: dict[str, list[str]]) -> list[dict[str, Any]]:
    by_support: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        by_support[str(row.get("support_id", ""))].append(row)
    summaries: list[dict[str, Any]] = []
    for support_id in sorted(by_support):
        support_rows = by_support[support_id]
        first = support_rows[0]
        status_counts = collections.Counter(row.get("status", "") for row in support_rows)
        summaries.append(
            {
                "candidate_id": first.get("candidate_id", ""),
                "candidate_name": first.get("candidate_name", ""),
                "support_id": support_id,
                "display_name": first.get("display_name", ""),
                "support_level": first.get("support_level", ""),
                "support_type": first.get("support_type", ""),
                "path_rows": ";".join(pathrow_map.get(support_id, [])),
                "expected_month_count": len(support_rows),
                "computed_month_count": status_counts.get(COMPUTED_STATUS, 0),
                "blocked_month_count": len(support_rows) - status_counts.get(COMPUTED_STATUS, 0),
                "quality_high_count": sum(row.get("quality_flag") == "quality_high" for row in support_rows),
                "quality_minimum_count": sum(row.get("quality_flag") == "quality_minimum" for row in support_rows),
                "quality_fail_count": sum(row.get("quality_flag") == "quality_fail" for row in support_rows),
                "wet_month_count": sum(row.get("wet_month_flag") == "True" for row in support_rows),
                "status_counts": dict(status_counts),
                "caveat": first.get("failure_or_caveat", ""),
            }
        )
    return summaries


def build_comparison_rows(config: dict[str, Any], summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    comparison_config = config["comparison"]
    fields = comparison_config["fields"]
    tolerances = comparison_config["tolerances"]
    goal015_rows = read_csv(REPO / comparison_config["goal015_repaired_summary_csv"])
    goal014_rows = read_csv(REPO / comparison_config["goal014_direct_s3_summary_csv"])
    goal007_rows = read_csv(REPO / comparison_config["legacy_event_window_csv"])
    goal009_rows = read_csv(REPO / comparison_config["legacy_full_window_csv"])
    comparison_rows: list[dict[str, Any]] = []
    summary_by_key = {(row["support_id"], row["month"]): row for row in summary_rows}
    primary_support_id = config["primary_support_id_for_comparison"]
    for month in config["months"]:
        computed = summary_by_key.get((primary_support_id, month))
        if computed:
            comparison_rows.append(
                comparison_row(
                    computed,
                    lookup_row(goal015_rows, primary_support_id, month) or {},
                    "goal015_repaired_comparator",
                    tolerances,
                    fields,
                )
            )
            comparison_rows.append(
                comparison_row(
                    computed,
                    lookup_row(goal014_rows, primary_support_id, month) or {},
                    "goal014_direct_s3",
                    tolerances,
                    fields,
                )
            )
    for row in summary_rows:
        month = row["month"]
        support_id = row["support_id"]
        if month in {"2022-11", "2024-12"}:
            comparison_rows.append(
                comparison_row(
                    row,
                    lookup_row(goal007_rows, support_id, month) or {},
                    "goal007_legacy_event_window",
                    tolerances,
                    fields,
                )
            )
        if month == "2018-01":
            comparison_rows.append(
                comparison_row(
                    row,
                    lookup_row(goal009_rows, support_id, month) or {},
                    "goal009_full_window_context",
                    tolerances,
                    fields,
                )
            )
    return comparison_rows


def comparison_summary(comparison_rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = collections.Counter(row["comparison_status"] for row in comparison_rows)
    nwb002_required = [
        row
        for row in comparison_rows
        if row["support_id"] == "nwb002_ramsar_ref1291"
        and row["reference_source"] in {"goal015_repaired_comparator", "goal014_direct_s3"}
    ]
    return {
        "row_count": len(comparison_rows),
        "status_counts": dict(sorted(counts.items())),
        "nwb002_goal015_goal014_statuses": [row["comparison_status"] for row in nwb002_required],
        "nwb002_goal015_goal014_all_within_tolerance": bool(nwb002_required)
        and all(row["comparison_status"] == "within_tolerance" for row in nwb002_required),
        "legacy_denominator_only_count": counts.get("wetness_within_tolerance_denominator_diff", 0),
        "legacy_wetness_diff_count": counts.get("wetness_diff", 0),
    }


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(collections.Counter(row.get("status", "") for row in rows).items()))


def write_report(
    path: Path,
    config: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    support_summary_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> None:
    counts = status_counts(summary_rows)
    support_table = "\n".join(
        f"| {row['support_id']} | {row['path_rows']} | {row['computed_month_count']} | {row['blocked_month_count']} | {row['quality_high_count']} | {row['wet_month_count']} |"
        for row in support_summary_rows
    )
    comparison_counts = collections.Counter(row["comparison_status"] for row in comparison_rows)
    comparison_table = "\n".join(f"| {status} | {count} |" for status, count in sorted(comparison_counts.items()))
    wetness_diff_rows = [row for row in comparison_rows if row["comparison_status"] == "wetness_diff"]
    wetness_diff_table = "\n".join(
        f"| {row['support_id']} | {row['month']} | {row['reference_source']} | {row['wetness_differing_fields']} |"
        for row in wetness_diff_rows
    )
    host_label = manifest.get("run_host_label", "")
    remote_path = manifest.get("remote_workdir", "")
    area_tolerance = config["comparison"]["tolerances"]["area_m2_abs"]
    write_text(
        path,
        "\n".join(
            [
                "# Goal 016 Direct S3 All-Support Probe",
                "",
                f"Accessed date: `{config['accessed_date']}`.",
                "",
                "## Scope",
                "",
                "This bounded rehearsal computed base DEA Water Observations metrics across the current event-window support set for `2018-01`, `2022-11`, and `2024-12` using direct public S3 COG reads and the Goal 015 support-intersecting WRS path/row scene-selection policy.",
                "",
                "No full event-window extraction, lag metrics, time-history metrics, biodiversity analysis, or ecological interpretation was run.",
                "",
                "## Compute Route",
                "",
                f"Run host label: `{host_label}`.",
                f"Remote working path: `{remote_path}`." if remote_path else "Remote working path: not recorded.",
                f"Remote compute used: `{manifest['remote_compute_used']}`.",
                "",
                "## Row Status",
                "",
                f"Expected rows: `{manifest['expected_summary_row_count']}`.",
                f"Observed rows: `{manifest['summary_row_count']}`.",
                "",
                "| Status | Rows |",
                "| --- | ---: |",
                *[f"| {status} | {count} |" for status, count in counts.items()],
                "",
                "## Support Summary",
                "",
                "| Support | Path rows | Computed months | Blocked months | Quality-high months | Wet months |",
                "| --- | --- | ---: | ---: | ---: | ---: |",
                support_table,
                "",
                "## Comparison Summary",
                "",
                "| Comparison status | Rows |",
                "| --- | ---: |",
                comparison_table,
                "",
                f"`NWB002` Goal 015/014 comparisons all within tolerance: `{manifest['comparison_summary']['nwb002_goal015_goal014_all_within_tolerance']}`.",
                f"Area comparisons use a predeclared `{area_tolerance}` m2 absolute tolerance to allow cross-host floating-point summation differences while preserving exact count and proportion tolerances.",
                "",
                "Legacy comparisons are validation context. Denominator-only differences are separated from wetness-field differences in the comparison CSV.",
                "",
                "Wetness-field legacy differences are:",
                "",
                "| Support | Month | Reference | Wetness differing fields |",
                "| --- | --- | --- | --- |",
                wetness_diff_table if wetness_diff_table else "| none |  |  |  |",
                "",
                "## Recommendation For Goal 017",
                "",
                manifest["recommendation_for_goal017"],
            ]
        )
        + "\n",
    )


def write_compute_memo(path: Path, config: dict[str, Any], manifest: dict[str, Any]) -> None:
    route = manifest.get("compute_route_evidence", {})
    probe_status = route.get("status", "not_recorded")
    smoke_status = route.get("remote_smoke_status", "not_recorded")
    probe = route.get("probe", {})
    tests = route.get("remote_focused_tests", {})
    smoke = route.get("remote_smoke", {})
    write_text(
        path,
        "\n".join(
            [
                "# Goal 016 Compute Routing Memo",
                "",
                "## Decision",
                "",
                f"Preferred target: `{config['compute']['preferred_host']}`.",
                f"Final run host label: `{manifest['run_host_label']}`.",
                f"Remote compute used: `{manifest['remote_compute_used']}`.",
                f"Remote working path: `{manifest.get('remote_workdir', '')}`.",
                "",
                "## Target Probe",
                "",
                f"Probe status: `{probe_status}`.",
                f"Route evidence source: `{manifest.get('route_evidence_source', '')}`.",
                f"Hostname: `{probe.get('hostname', '')}`.",
                f"CPU count: `{probe.get('cpu_count', '')}`.",
                f"Memory total: `{probe.get('memory_total', '')}`.",
                f"`/data` available: `{probe.get('disk_data_available', '')}`.",
                f"Python: `{probe.get('python_version', '')}`.",
                f"GDAL: `{probe.get('gdal_version', '')}`.",
                f"Git: `{probe.get('git_version', '')}`.",
                f"S3 route: `{probe.get('s3_head_status', '')}`.",
                f"Python bindings: NumPy `{probe.get('numpy_version', '')}`, GDAL/OGR/OSR `{probe.get('osgeo_python_bindings', '')}`.",
                "",
                "## Target Tests",
                "",
                f"Focused test command: `{tests.get('command', '')}`.",
                f"Focused test status: `{tests.get('status', '')}` with `{tests.get('tests_run', '')}` tests.",
                "",
                "## Smoke Test",
                "",
                f"Remote smoke status: `{smoke_status}`.",
                "Preferred smoke support/month: `NWB002` / `2022-11`.",
                f"Smoke elapsed seconds: `{smoke.get('elapsed_seconds', '')}`.",
                f"Smoke status counts: `{json.dumps(smoke.get('status_counts', {}), sort_keys=True)}`.",
                f"Smoke Goal 015/014 hash/count status: `{smoke.get('goal015_goal014_hash_count_status', '')}`.",
                f"Area difference vs Goal 015/014: `{smoke.get('area_difference_m2_vs_goal015_goal014', '')}` m2; full-run area tolerance: `{smoke.get('area_tolerance_m2_for_full_run', '')}` m2.",
                "",
                "## Final Run",
                "",
                f"Summary row count: `{manifest['summary_row_count']}`.",
                f"Status counts: `{json.dumps(manifest['status_counts'], sort_keys=True)}`.",
                "",
                "## Fallback Rules",
                "",
                "If `deep-server-ts` is unavailable or fails the project-native smoke test, the support grid must not be reduced. A local full run is acceptable only when a local smoke shows the 33-row workload is comfortably bounded; otherwise the package should record a blocker.",
            ]
        )
        + "\n",
    )


def recommendation_for_goal017(summary_rows: list[dict[str, Any]], comparison: dict[str, Any]) -> str:
    all_computed = all(row.get("status") == COMPUTED_STATUS for row in summary_rows)
    nwb_ok = comparison.get("nwb002_goal015_goal014_all_within_tolerance") is True
    wetness_diff_count = int(comparison.get("legacy_wetness_diff_count") or 0)
    if all_computed and nwb_ok and wetness_diff_count == 0:
        return "Proceed to a reviewed Goal 017 design for direct-S3 scale-up, retaining the support-intersecting WRS path/row policy and keeping any full-window launch separate from this bounded probe."
    if not all_computed:
        return "Resolve the classified blocked support/month rows before any direct-S3 scale-up."
    if not nwb_ok:
        return "Resolve the `NWB002` repaired-comparator regression before any direct-S3 scale-up."
    return "Review legacy wetness-field differences before any direct-S3 scale-up."


def run(
    config_path: Path,
    reuse_cache: bool,
    support_filter: str | None = None,
    month_filter: str | None = None,
    run_host_label: str = "local_mac_mini",
    remote_workdir: str = "",
    route_evidence_json: Path | None = None,
) -> dict[str, Any]:
    started = time.time()
    config = load_json(config_path)
    months = selected_months(config, month_filter)
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
        raise RuntimeError(f"Goal 016 staging paths are not all ignored: {ignored_check}")
    configure_gdal()
    reset_retry_audit_log()
    supports, support_summary_source_rows, pathrow_map = selected_supports(config, support_filter)
    expected_grid = expected_support_month_grid(supports, months)
    summary_rows, extraction_records = extract_rows(config, supports, months, pathrow_map, reuse_cache)
    support_summary_rows = build_support_summary(summary_rows, pathrow_map)
    comparison_rows = build_comparison_rows(config, summary_rows) if not support_filter and not month_filter else []
    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    write_csv(outputs["summary_csv"], summary_rows, summary_fieldnames())
    write_csv(outputs["support_summary_csv"], support_summary_rows, support_summary_fieldnames())
    write_csv(outputs["comparison_csv"], comparison_rows, comparison_fieldnames())
    comparison = comparison_summary(comparison_rows) if comparison_rows else {
        "row_count": 0,
        "status_counts": {},
        "nwb002_goal015_goal014_statuses": [],
        "nwb002_goal015_goal014_all_within_tolerance": False,
        "legacy_denominator_only_count": 0,
        "legacy_wetness_diff_count": 0,
    }
    route_evidence = load_route_evidence(route_evidence_json)
    recommendation = recommendation_for_goal017(summary_rows, comparison)
    manifest = {
        "goal": config["goal"],
        "manifest_type": "direct_s3_all_support_probe_016",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "accessed_date": config["accessed_date"],
        "command": config["run_command"]
        + (" --reuse-ignored-cache" if reuse_cache else "")
        + (f" --support-id {support_filter}" if support_filter else "")
        + (f" --month {month_filter}" if month_filter else ""),
        "config_path": repo_relative(config_path),
        "reuse_ignored_cache": reuse_cache,
        "git_head_at_run": git_head(),
        "git_status_at_run": git_status(),
        "host_facts": host_facts(),
        "run_host_label": run_host_label,
        "remote_compute_used": run_host_label not in {"local", "local_mac_mini"},
        "remote_workdir": remote_workdir,
        "route_evidence_source": repo_relative(route_evidence_json) if route_evidence_json else "",
        "compute_route_evidence": route_evidence,
        "source_urls": config["source_urls"],
        "scene_selection_policy": config["scene_selection_policy"],
        "support_count": len(supports),
        "support_source_row_count": len(support_summary_source_rows),
        "support_ids": [support["support_id"] for support in sorted(supports, key=lambda item: item["support_id"])],
        "support_path_rows": {support_id: pathrow_map[support_id] for support_id in sorted(pathrow_map)},
        "months": months,
        "expected_summary_row_count": len(expected_grid),
        "summary_row_count": len(summary_rows),
        "status_counts": status_counts(summary_rows),
        "summary_row_hash": stable_row_hash(summary_rows, ["support_id", "month", "status", "asset_key_hash"]),
        "support_summary_row_count": len(support_summary_rows),
        "comparison_summary": comparison,
        "extraction_records": extraction_records,
        "retry_audit_summary": retry_audit_summary(),
        "outputs": {key: repo_relative(path) for key, path in outputs.items()},
        "staging_paths": config["staging_paths"],
        "staging_ignored_check": ignored_check,
        "staging_policy": config["commit_policy"],
        "status_vocabulary": sorted(STATUS_VOCABULARY),
        "comparison_status_vocabulary": sorted(COMPARISON_STATUSES),
        "recommendation_for_goal017": recommendation,
        "elapsed_seconds": round(time.time() - started, 3),
    }
    write_json(outputs["manifest_json"], manifest)
    write_report(outputs["report_md"], config, summary_rows, support_summary_rows, comparison_rows, manifest)
    write_compute_memo(outputs["compute_memo_md"], config, manifest)
    write_json(REPO / config["staging_paths"]["output"] / "direct_s3_all_support_probe_016_run.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to Goal 016 config JSON")
    parser.add_argument("--reuse-ignored-cache", action="store_true", help="Reuse ignored S3 listing/HEAD caches")
    parser.add_argument("--support-id", default=None, help="Optional support-id filter for target smoke runs")
    parser.add_argument("--month", default=None, help="Optional month filter for target smoke runs")
    parser.add_argument("--run-host-label", default="local_mac_mini", help="Host label to record in manifest")
    parser.add_argument("--remote-workdir", default="", help="Remote working directory to record in manifest")
    parser.add_argument("--route-evidence-json", default=None, help="Optional ignored route-evidence JSON to embed")
    args = parser.parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    route_evidence = Path(args.route_evidence_json) if args.route_evidence_json else None
    manifest = run(
        config_path,
        args.reuse_ignored_cache,
        support_filter=args.support_id,
        month_filter=args.month,
        run_host_label=args.run_host_label,
        remote_workdir=args.remote_workdir,
        route_evidence_json=route_evidence,
    )
    print(
        json.dumps(
            {
                "status_counts": manifest["status_counts"],
                "summary_rows": manifest["summary_row_count"],
                "elapsed_seconds": manifest["elapsed_seconds"],
                "manifest": manifest["outputs"]["manifest_json"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
