#!/usr/bin/env python3
"""Tiny DEA Water Observations smoke test for Goal 004.

This script performs only public STAC metadata queries and tiny GDAL reads from
public DEA Cloud-Optimized GeoTIFFs. It does not download or persist raw source
rasters or biodiversity data.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from osgeo import gdal, osr

gdal.UseExceptions()

REPO = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO / "settings" / "hydrology_smoke_test_004.json"
CROSSWALK_PATH = REPO / "docs" / "prototype_wetland_unit_crosswalk.csv"

INVALID_BITS = {
    "no_data_count": 1,
    "contiguity_count": 2,
    "low_solar_angle_count": 4,
    "terrain_shadow_count": 8,
    "high_slope_count": 16,
    "cloud_shadow_count": 32,
    "cloud_count": 64,
}
WATER_BIT = 128
PIXEL_AREA_M2 = 900


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_crosswalk() -> dict[str, dict[str, str]]:
    with CROSSWALK_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {row["candidate_id"]: row for row in rows}


def month_range(month: str) -> tuple[str, str]:
    year, mon = map(int, month.split("-"))
    start = dt.datetime(year, mon, 1, tzinfo=dt.UTC)
    if mon == 12:
        stop = dt.datetime(year + 1, 1, 1, tzinfo=dt.UTC)
    else:
        stop = dt.datetime(year, mon + 1, 1, tzinfo=dt.UTC)
    return start.isoformat().replace("+00:00", "Z"), stop.isoformat().replace("+00:00", "Z")


def stac_search(config: dict[str, Any], lon: float, lat: float, month: str) -> dict[str, Any]:
    start, stop = month_range(month)
    delta = float(config["probe_bbox_half_width_degrees"])
    payload = {
        "collections": [config["dea_collection"]],
        "bbox": [lon - delta, lat - delta, lon + delta, lat + delta],
        "datetime": f"{start}/{stop}",
        "limit": int(config["stac_limit"]),
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        config["stac_search_url"],
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)
    data["_query_payload"] = payload
    return data


def s3_to_vsi(href: str) -> str:
    if not href.startswith("s3://"):
        return href
    return "/vsis3/" + href.removeprefix("s3://")


def transform_lonlat(dataset: gdal.Dataset, lon: float, lat: float) -> tuple[float, float]:
    projection = dataset.GetProjection()
    if not projection:
        return lon, lat
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    source.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    target = osr.SpatialReference()
    target.ImportFromWkt(projection)
    target.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    transform = osr.CoordinateTransformation(source, target)
    x, y, _ = transform.TransformPoint(lon, lat)
    return x, y


def pixel_window(dataset: gdal.Dataset, lon: float, lat: float, half_window: int) -> tuple[int, int, int, int]:
    x, y = transform_lonlat(dataset, lon, lat)
    gt = dataset.GetGeoTransform()
    inv = gdal.InvGeoTransform(gt)
    px = int(inv[0] + inv[1] * x + inv[2] * y)
    py = int(inv[3] + inv[4] * x + inv[5] * y)
    xoff = max(0, px - half_window)
    yoff = max(0, py - half_window)
    xsize = min(dataset.RasterXSize - xoff, half_window * 2 + 1)
    ysize = min(dataset.RasterYSize - yoff, half_window * 2 + 1)
    if px < 0 or py < 0 or px >= dataset.RasterXSize or py >= dataset.RasterYSize:
        raise ValueError(f"probe point outside raster bounds: pixel=({px}, {py})")
    return xoff, yoff, xsize, ysize


def summarise_values(values: list[int]) -> dict[str, Any]:
    n_pixel = len(values)
    invalid = [value for value in values if value & sum(INVALID_BITS.values())]
    clear_wet = [value for value in values if value == WATER_BIT]
    clear_dry = [value for value in values if value == 0]
    clear = clear_wet + clear_dry
    clear_obs_count = len(clear)
    invalid_obs_count = len(invalid)
    wet_count = len(clear_wet)
    valid_support_area_m2 = clear_obs_count * PIXEL_AREA_M2
    current_wet_area_m2 = wet_count * PIXEL_AREA_M2
    current_proportion_wet = (
        current_wet_area_m2 / valid_support_area_m2 if valid_support_area_m2 else None
    )
    summary: dict[str, Any] = {
        "n_scene_m": 1,
        "n_pixel_u": n_pixel,
        "clear_obs_count": clear_obs_count,
        "invalid_obs_count": invalid_obs_count,
        "clear_obs_fraction": clear_obs_count / n_pixel if n_pixel else None,
        "current_wet_area_m2": current_wet_area_m2,
        "valid_support_area_m2": valid_support_area_m2,
        "current_proportion_wet": current_proportion_wet,
        "wet_pixel_count": wet_count,
        "dry_pixel_count": len(clear_dry),
        "raw_values": ";".join(map(str, values)),
    }
    for field, bit in INVALID_BITS.items():
        summary[field] = sum(1 for value in values if value & bit)
    if clear_obs_count >= 8 and summary["clear_obs_fraction"] >= 0.40:
        summary["quality_flag"] = "quality_high"
    elif clear_obs_count >= 5 and summary["clear_obs_fraction"] >= 0.20:
        summary["quality_flag"] = "quality_minimum"
    else:
        summary["quality_flag"] = "quality_fail"
    summary["wet_month_flag"] = (
        bool(current_proportion_wet is not None and current_proportion_wet >= 0.05)
        if summary["quality_flag"] != "quality_fail"
        else None
    )
    return summary


def read_tiny_window(href: str, lon: float, lat: float, half_window: int) -> tuple[dict[str, Any], str]:
    dataset_path = s3_to_vsi(href)
    gdal.SetConfigOption("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
    dataset = gdal.Open(dataset_path)
    if dataset is None:
        raise RuntimeError(f"GDAL could not open asset: {dataset_path}")
    xoff, yoff, xsize, ysize = pixel_window(dataset, lon, lat, half_window)
    array = dataset.ReadAsArray(xoff, yoff, xsize, ysize)
    if array is None:
        raise RuntimeError("GDAL returned no array for tiny window")
    values = [int(value) for row in array.tolist() for value in row]
    summary = summarise_values(values)
    summary.update({"xoff": xoff, "yoff": yoff, "xsize": xsize, "ysize": ysize})
    return summary, dataset_path


def choose_readable_item(features: list[dict[str, Any]], lon: float, lat: float, half_window: int) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str | None, str | None]:
    last_error = None
    best: tuple[int, int, dict[str, Any], dict[str, Any], str] | None = None
    for feature in features:
        href = feature.get("assets", {}).get("water", {}).get("href")
        if not href:
            continue
        try:
            metrics, dataset_path = read_tiny_window(href, lon, lat, half_window)
            score = (int(metrics["clear_obs_count"]), -int(metrics["invalid_obs_count"]))
            if best is None or score > (best[0], best[1]):
                best = (score[0], score[1], feature, metrics, dataset_path)
        except Exception as exc:  # noqa: BLE001 - we want the access failure in the manifest.
            last_error = str(exc)
    if best is not None:
        return best[2], best[3], best[4], None
    return None, None, None, last_error


def run() -> int:
    start_time = time.time()
    os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
    config = load_json(CONFIG_PATH)
    crosswalk = load_crosswalk()
    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    for path in config["scratch_paths"].values():
        (REPO / path).mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    manifest: dict[str, Any] = {
        "goal": "004-hydrology-extraction-smoke-test",
        "metric_spec_version": config["metric_spec_version"],
        "started_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "command": "python3 scripts/hydrology_smoke_test_004.py",
        "python_version": sys.version,
        "platform": platform.platform(),
        "gdal_version": gdal.VersionInfo("--version"),
        "config_path": str(CONFIG_PATH.relative_to(REPO)),
        "crosswalk_path": str(CROSSWALK_PATH.relative_to(REPO)),
        "source_urls": {
            "stac_search": config["stac_search_url"],
            "dea_water_observations_product": "https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/?tab=overview",
            "dea_waterbodies_product": "https://knowledge.dea.ga.gov.au/data/product/dea-waterbodies-landsat/?tab=details",
        },
        "scratch_paths": config["scratch_paths"],
        "staged_raw_files": [],
        "staged_file_sizes_bytes": {},
        "cleanup_status": "no raw source files were downloaded; ignored scratch directories were created only",
        "candidates": [],
        "outputs": {key: str(path.relative_to(REPO)) for key, path in outputs.items()},
    }
    half_window = int(config["probe_half_window_pixels"])
    for candidate in config["candidates"]:
        candidate_id = candidate["candidate_id"]
        crosswalk_row = crosswalk[candidate_id]
        candidate_record = {
            "candidate_id": candidate_id,
            "candidate_name": crosswalk_row["candidate_name"],
            "probe_lon": candidate["probe_lon"],
            "probe_lat": candidate["probe_lat"],
            "months": [],
        }
        for month in config["months"]:
            row = {
                "candidate_id": candidate_id,
                "candidate_name": crosswalk_row["candidate_name"],
                "support_id": candidate["support_id"],
                "support_type": candidate["support_type"],
                "month": month["month"],
                "month_rationale": month["rationale"],
                "source_product": config["source_product"],
                "source_product_version": config["source_product_version"],
                "access_method": "DEA STAC search plus GDAL /vsis3/ 3x3 window read",
                "status": "",
                "stac_items_found": 0,
                "selected_item_id": "",
                "selected_datetime_utc": "",
                "selected_asset_href": "",
                "dataset_path": "",
                "probe_lon": candidate["probe_lon"],
                "probe_lat": candidate["probe_lat"],
                "support_area_m2": "",
                "n_scene_m": "",
                "n_pixel_u": "",
                "clear_obs_count": "",
                "invalid_obs_count": "",
                "clear_obs_fraction": "",
                "current_wet_area_m2": "",
                "valid_support_area_m2": "",
                "current_proportion_wet": "",
                "wet_pixel_count": "",
                "dry_pixel_count": "",
                "quality_flag": "",
                "wet_month_flag": "",
                "no_data_count": "",
                "contiguity_count": "",
                "low_solar_angle_count": "",
                "terrain_shadow_count": "",
                "high_slope_count": "",
                "cloud_shadow_count": "",
                "cloud_count": "",
                "failure_or_caveat": candidate["probe_caveat"],
            }
            month_record: dict[str, Any] = {"month": month["month"]}
            try:
                search = stac_search(
                    config,
                    float(candidate["probe_lon"]),
                    float(candidate["probe_lat"]),
                    month["month"],
                )
                features = search.get("features", [])
                row["stac_items_found"] = len(features)
                month_record["stac_query_sha256"] = hashlib.sha256(
                    json.dumps(search.get("_query_payload", {}), sort_keys=True).encode("utf-8")
                ).hexdigest()
                month_record["stac_items_found"] = len(features)
                if not features:
                    row["status"] = "stac_no_items"
                    row["failure_or_caveat"] += " STAC returned no Water Observations items."
                else:
                    feature, metrics, dataset_path, error = choose_readable_item(
                        features,
                        float(candidate["probe_lon"]),
                        float(candidate["probe_lat"]),
                        half_window,
                    )
                    if feature is None or metrics is None:
                        row["status"] = "stac_items_but_read_failed"
                        row["failure_or_caveat"] += f" GDAL tiny-window read failed: {error}"
                    else:
                        href = feature["assets"]["water"]["href"]
                        row["status"] = "computed_tiny_probe_metrics"
                        row["selected_item_id"] = feature.get("id", "")
                        row["selected_datetime_utc"] = feature.get("properties", {}).get("datetime", "")
                        row["selected_asset_href"] = href
                        row["dataset_path"] = dataset_path or ""
                        row["support_area_m2"] = metrics["n_pixel_u"] * PIXEL_AREA_M2
                        for key, value in metrics.items():
                            if key in row:
                                row[key] = value
                        month_record.update(
                            {
                                "selected_item_id": row["selected_item_id"],
                                "selected_datetime_utc": row["selected_datetime_utc"],
                                "selected_asset_href": href,
                                "status": row["status"],
                                "quality_flag": row["quality_flag"],
                            }
                        )
            except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError) as exc:
                row["status"] = "access_failed"
                row["failure_or_caveat"] += f" Access failed: {exc}"
                month_record["status"] = row["status"]
                month_record["error"] = str(exc)
            rows.append(row)
            candidate_record["months"].append(month_record)
        manifest["candidates"].append(candidate_record)
    outputs["summary_csv"].parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with outputs["summary_csv"].open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    manifest["finished_at_utc"] = dt.datetime.now(dt.UTC).isoformat()
    manifest["elapsed_seconds"] = round(time.time() - start_time, 3)
    manifest["summary_row_count"] = len(rows)
    manifest["status_counts"] = {}
    for row in rows:
        manifest["status_counts"][row["status"]] = manifest["status_counts"].get(row["status"], 0) + 1
    manifest["git_commit_at_run"] = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], cwd=REPO, text=True
    ).strip()
    outputs["manifest_json"].write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {outputs['summary_csv'].relative_to(REPO)}")
    print(f"wrote {outputs['manifest_json'].relative_to(REPO)}")
    print(json.dumps({"rows": len(rows), "status_counts": manifest["status_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
