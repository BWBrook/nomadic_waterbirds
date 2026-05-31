#!/usr/bin/env python3
"""Goal 010 service-stability preflight over Goal 009 blocked rows."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from osgeo import gdal, ogr


SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[0]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from event_window_hydrology_007 import (  # noqa: E402
    build_parent_supports,
    build_support_set,
    fetch_ramsar_subset,
    ensure_download,
)
from official_support_hydrology_005 import (  # noqa: E402
    RetryExhaustedError,
    classify_remote_failure,
    epsg_srs,
    load_json,
    normalise_retry_policy,
    rasterize_geometry,
    reset_retry_audit_log,
    retry_audit_events,
    sha256_file,
    stac_search,
    summarise_support_month,
    support_grid,
    warp_scene_to_grid,
    write_json,
)


GOAL009_SERIES = REPO / "docs" / "event_window_hydrology_series_2018_2024.csv"
DEFAULT_CONFIG = REPO / "settings" / "hydrology_recovery_010.json"
DEFAULT_OUTPUT = REPO / "artifacts" / "hydrology_recovery_010" / "output" / "blocked_row_preflight_010.json"
DEFAULT_SAMPLE_CSV = REPO / "artifacts" / "hydrology_recovery_010" / "output" / "blocked_row_preflight_sample_010.csv"
PERIOD_MONTHS = {
    "early": ("2018-01", "2018-07", "2019-01", "2019-07"),
    "wet_flood": ("2021-11", "2022-03", "2022-11", "2023-01"),
    "recent": ("2023-12", "2024-03", "2024-06", "2024-12"),
}
PERIOD_ORDER = ("early", "wet_flood", "recent")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sample_period(month: str) -> str:
    for period, months in PERIOD_MONTHS.items():
        if month in months:
            return period
    year = int(month[:4])
    if year <= 2019:
        return "early"
    if year in {2021, 2022}:
        return "wet_flood"
    return "recent"


def _blocked_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("status") != "computed_event_window_metrics"]


def _row_sort_key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("support_id", ""), row.get("month", "")


def select_preflight_sample(rows: list[dict[str, str]], target_size: int = 33) -> list[dict[str, Any]]:
    blocked = sorted(_blocked_rows(rows), key=_row_sort_key)
    by_support: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in blocked:
        by_support[row["support_id"]].append(row)

    selected_keys: set[tuple[str, str]] = set()
    selected: list[dict[str, Any]] = []

    def add(candidate: dict[str, str], period: str) -> None:
        key = (candidate["support_id"], candidate["month"])
        if key in selected_keys:
            return
        selected_keys.add(key)
        item = dict(candidate)
        item["sample_period"] = period
        selected.append(item)

    for support_id in sorted(by_support):
        support_rows = by_support[support_id]
        for period in PERIOD_ORDER:
            month_priority = PERIOD_MONTHS[period]
            period_rows = [row for row in support_rows if sample_period(row["month"]) == period]
            if not period_rows:
                continue
            period_rows.sort(
                key=lambda row: (
                    month_priority.index(row["month"]) if row["month"] in month_priority else len(month_priority),
                    row["month"],
                )
            )
            add(period_rows[0], period)

    if len(selected) < target_size:
        remaining = [
            row for row in blocked
            if (row["support_id"], row["month"]) not in selected_keys
        ]
        if remaining:
            stride = max(1, len(remaining) // max(1, target_size - len(selected)))
            for row in remaining[::stride]:
                add(row, sample_period(row["month"]))
                if len(selected) >= target_size:
                    break

    selected = selected[:target_size]
    selected.sort(key=lambda row: (row["support_id"], PERIOD_ORDER.index(row["sample_period"]), row["month"]))
    for index, item in enumerate(selected, start=1):
        item["sample_order"] = index
    return selected


def launch_decision(endpoint_probes: list[dict[str, Any]], row_results: list[dict[str, Any]]) -> dict[str, Any]:
    sample_size = len(row_results)
    computed_count = sum(row.get("status") == "computed_preflight_metrics" for row in row_results)
    computed_fraction = round(computed_count / sample_size, 6) if sample_size else 0.0
    blockers: list[str] = []

    if not endpoint_probes or any(probe.get("endpoint_status") != "available" for probe in endpoint_probes):
        blockers.append("endpoint_probe_unavailable")
    if computed_fraction < 0.8:
        blockers.append("sample_computed_fraction_below_0.8")

    for field, blocker_name in (("support_id", "clustered_support_failures"), ("sample_period", "clustered_period_failures")):
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in row_results:
            grouped[str(row.get(field, ""))].append(row)
        for group_rows in grouped.values():
            if len(group_rows) < 2:
                continue
            group_computed = sum(row.get("status") == "computed_preflight_metrics" for row in group_rows)
            if group_computed / len(group_rows) < 0.5:
                blockers.append(blocker_name)
                break

    decision = "launch_recovery" if not blockers else "stop_service_stability_blocker"
    return {
        "decision": decision,
        "sample_size": sample_size,
        "computed_count": computed_count,
        "blocked_count": sample_size - computed_count,
        "computed_fraction": computed_fraction,
        "blockers": sorted(set(blockers)),
    }


def build_support_lookup(config: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    ramsar_subset, ramsar_query_url = fetch_ramsar_subset(config)
    ramsar_path = REPO / config["staged_files"]["ramsar_subset_geojson"]
    ramsar_path.parent.mkdir(parents=True, exist_ok=True)
    ramsar_path.write_bytes(json.dumps(ramsar_subset, indent=2).encode("utf-8"))
    waterbodies_zip = REPO / config["staged_files"]["dea_waterbodies_zip"]
    seed = REPO / config.get("existing_waterbodies_zip_path", "")
    ensure_download(config["dea_waterbodies_zip_url"], waterbodies_zip, seed_path=seed)
    parents, features_by_refcode = build_parent_supports(config, ramsar_subset)
    supports, _crosswalk_rows, _evidence_checks, _named_geometry_manifest = build_support_set(
        config, parents, features_by_refcode, waterbodies_zip
    )
    source_manifest = {
        "ramsar_query_url": ramsar_query_url,
        "staged_files": [
            {
                "path": str(ramsar_path.relative_to(REPO)),
                "bytes": ramsar_path.stat().st_size,
                "sha256": sha256_file(ramsar_path),
                "committed": False,
            },
            {
                "path": str(waterbodies_zip.relative_to(REPO)),
                "bytes": waterbodies_zip.stat().st_size,
                "sha256": sha256_file(waterbodies_zip),
                "committed": False,
            },
        ],
    }
    return {support["support_id"]: support for support in supports}, source_manifest


def compute_preflight_row(config: dict[str, Any], support: dict[str, Any], sample: dict[str, Any]) -> dict[str, Any]:
    month = sample["month"]
    started = time.time()
    before_events = len(retry_audit_events())
    result: dict[str, Any] = {
        "sample_order": sample["sample_order"],
        "sample_period": sample["sample_period"],
        "support_id": sample["support_id"],
        "month": month,
        "goal009_status": sample.get("status", ""),
        "goal009_failure_or_caveat": sample.get("failure_or_caveat", ""),
    }
    try:
        os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
        gdal.SetConfigOption("AWS_NO_SIGN_REQUEST", "YES")
        gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
        gdal.SetConfigOption("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
        pixel_size = int(config["pixel_size_m"])
        bounds, geotransform, xsize, ysize = support_grid(support["geom_albers"], pixel_size)
        if xsize * ysize > int(config["max_reference_grid_pixels"]):
            raise RuntimeError(f"reference grid has {xsize * ysize} cells, above configured maximum")
        support_mask = rasterize_geometry(support["geom_albers"], epsg_srs(3577), geotransform, xsize, ysize)
        stac = stac_search(config, support["bbox_wgs84"], month)
        features = sorted(
            stac.get("features", []),
            key=lambda feature: feature.get("properties", {}).get("datetime", ""),
        )
        scene_arrays: list[np.ndarray] = []
        skipped: list[dict[str, str]] = []
        for feature in features:
            href = feature.get("assets", {}).get("water", {}).get("href")
            if not href:
                skipped.append({"id": feature.get("id", ""), "reason": "missing water asset"})
                continue
            try:
                scene_arrays.append(warp_scene_to_grid(href, bounds, xsize, ysize, config["reference_crs"], config))
            except Exception as exc:
                skipped.append({"id": feature.get("id", ""), "reason": str(exc)})
        metrics = summarise_support_month(scene_arrays, support_mask)
        if scene_arrays:
            result.update(
                {
                    "status": "computed_preflight_metrics",
                    "failure_class": "",
                    "stac_items_found": len(features),
                    "readable_scene_count": len(scene_arrays),
                    "skipped_scene_count": len(skipped),
                    "quality_flag": metrics["quality_flag"],
                    "current_proportion_wet": metrics["current_proportion_wet"],
                    "failure_or_caveat": support["caveat"],
                }
            )
        else:
            result.update(
                {
                    "status": "blocked_no_readable_water_observations_scene",
                    "failure_class": "no_readable_asset",
                    "stac_items_found": len(features),
                    "readable_scene_count": 0,
                    "skipped_scene_count": len(skipped),
                    "quality_flag": "quality_fail",
                    "current_proportion_wet": "",
                    "failure_or_caveat": "No readable Water Observations scene could be warped for this support/month.",
                }
            )
    except RetryExhaustedError as exc:
        event = exc.event
        result.update(
            {
                "status": "blocked_preflight_processing_error",
                "failure_class": event["failure_class"],
                "stac_items_found": 0,
                "readable_scene_count": 0,
                "skipped_scene_count": 0,
                "quality_flag": "quality_fail",
                "current_proportion_wet": "",
                "failure_or_caveat": str(exc),
            }
        )
    except Exception as exc:
        classification = classify_remote_failure(exc, "preflight_processing")
        result.update(
            {
                "status": "blocked_preflight_processing_error",
                "failure_class": classification["failure_class"],
                "stac_items_found": 0,
                "readable_scene_count": 0,
                "skipped_scene_count": 0,
                "quality_flag": "quality_fail",
                "current_proportion_wet": "",
                "failure_or_caveat": classification["message"],
            }
        )
    result["elapsed_seconds"] = round(time.time() - started, 3)
    new_events = retry_audit_events()[before_events:]
    result["attempt_count"] = max((int(event.get("attempt_count", 1)) for event in new_events), default=1)
    result["retry_events"] = new_events
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:
        return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--goal009-series", default=str(GOAL009_SERIES))
    parser.add_argument("--target-size", type=int, default=33)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--sample-csv", default=str(DEFAULT_SAMPLE_CSV))
    parser.add_argument("--host-label", default=socket.gethostname())
    parser.add_argument("--sample-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start = time.time()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO / config_path
    series_path = Path(args.goal009_series)
    if not series_path.is_absolute():
        series_path = REPO / series_path
    output = Path(args.output)
    if not output.is_absolute():
        output = REPO / output
    sample_csv = Path(args.sample_csv)
    if not sample_csv.is_absolute():
        sample_csv = REPO / sample_csv

    config = load_json(config_path)
    goal009_rows = read_csv_rows(series_path)
    sample = select_preflight_sample(goal009_rows, target_size=args.target_size)
    write_csv(sample_csv, sample)
    row_results: list[dict[str, Any]] = []
    source_manifest: dict[str, Any] = {}
    if not args.sample_only:
        reset_retry_audit_log()
        supports, source_manifest = build_support_lookup(config)
        for item in sample:
            support = supports[item["support_id"]]
            print(f"preflight {item['sample_order']}/{len(sample)} {item['support_id']} {item['month']}", flush=True)
            row_results.append(compute_preflight_row(config, support, item))

    manifest = {
        "goal": "010-hydrology-recovery-resume",
        "manifest_type": "blocked_row_preflight_010",
        "host_label": args.host_label,
        "host_facts": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": sys.version,
            "gdal_version": gdal.VersionInfo("--version"),
            "numpy_version": np.__version__,
        },
        "started_at_utc": dt.datetime.fromtimestamp(start, tz=dt.UTC).isoformat(),
        "finished_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "elapsed_seconds": round(time.time() - start, 3),
        "command": "python3 scripts/stac_recovery_preflight_010.py",
        "config_path": str(config_path.relative_to(REPO)) if config_path.is_relative_to(REPO) else str(config_path),
        "goal009_series_path": str(series_path.relative_to(REPO)) if series_path.is_relative_to(REPO) else str(series_path),
        "sample_target_size": args.target_size,
        "sample_size": len(sample),
        "retry_policy": normalise_retry_policy(config),
        "sample_csv": str(sample_csv.relative_to(REPO)) if sample_csv.is_relative_to(REPO) else str(sample_csv),
        "source_manifest": source_manifest,
        "sample": sample,
        "row_results": row_results,
        "result_status_counts": dict(Counter(row.get("status", "") for row in row_results)),
        "result_failure_class_counts": dict(Counter(row.get("failure_class", "") for row in row_results)),
        "result_quality_counts": dict(Counter(row.get("quality_flag", "") for row in row_results)),
        "retry_audit_events": retry_audit_events(),
        "git_commit_at_run": git_commit(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, manifest)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
