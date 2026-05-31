#!/usr/bin/env python3
"""Goal 005 official-support hydrology prototype.

The workflow stages a small DCCEEW Ramsar geometry subset in ignored paths and
computes bounded monthly DEA Water Observations metrics over official support
geometry. Raw geometry and raster data are not committed.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import os
import platform
import random
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

import numpy as np
from osgeo import gdal, ogr, osr

gdal.UseExceptions()
ogr.UseExceptions()

REPO = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO / "settings" / "official_support_hydrology_005.json"

INVALID_BITS = {
    "no_data_count": 1,
    "contiguity_count": 2,
    "low_solar_angle_count": 4,
    "terrain_shadow_count": 8,
    "high_slope_count": 16,
    "cloud_shadow_count": 32,
    "cloud_count": 64,
}
INVALID_MASK = sum(INVALID_BITS.values())
WATER_BIT = 128
TRANSIENT_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}
DETERMINISTIC_HTTP_STATUS_CODES = {400, 401, 403, 404}
DEFAULT_RETRY_POLICY = {
    "max_attempts": 3,
    "initial_delay_seconds": 2.0,
    "backoff_multiplier": 2.0,
    "max_delay_seconds": 30.0,
    "jitter_fraction": 0.1,
}
RETRY_AUDIT_LOG: list[dict[str, Any]] = []


class RetryExhaustedError(RuntimeError):
    """Raised when a transient remote failure persists after bounded retry."""

    def __init__(self, event: dict[str, Any]):
        self.event = event
        context = event.get("context", {})
        message = (
            f"{event.get('failure_class')}: {event.get('operation')} failed after "
            f"{event.get('attempt_count')}/{event.get('max_attempts')} attempts; "
            f"context={context}; last_error={event.get('last_error')}"
        )
        super().__init__(message)


def normalise_retry_policy(config: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = dict(DEFAULT_RETRY_POLICY)
    if config and isinstance(config.get("retry_policy"), dict):
        policy.update(config["retry_policy"])
    policy["max_attempts"] = max(1, int(policy["max_attempts"]))
    policy["initial_delay_seconds"] = max(0.0, float(policy["initial_delay_seconds"]))
    policy["backoff_multiplier"] = max(1.0, float(policy["backoff_multiplier"]))
    policy["max_delay_seconds"] = max(0.0, float(policy["max_delay_seconds"]))
    policy["jitter_fraction"] = max(0.0, float(policy["jitter_fraction"]))
    return policy


def reset_retry_audit_log() -> None:
    RETRY_AUDIT_LOG.clear()


def retry_audit_events() -> list[dict[str, Any]]:
    return [dict(event) for event in RETRY_AUDIT_LOG]


def retry_audit_summary(max_events: int = 200) -> dict[str, Any]:
    events = retry_audit_events()
    status_counts: dict[str, int] = {}
    failure_class_counts: dict[str, int] = {}
    for event in events:
        status = str(event.get("final_status", "unknown"))
        failure_class = str(event.get("failure_class", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
        failure_class_counts[failure_class] = failure_class_counts.get(failure_class, 0) + 1
    if len(events) <= max_events:
        retained_events = events
        truncated_count = 0
    else:
        head = max_events // 2
        tail = max_events - head
        retained_events = events[:head] + events[-tail:]
        truncated_count = len(events) - len(retained_events)
    return {
        "event_count": len(events),
        "events_truncated_count": truncated_count,
        "status_counts": status_counts,
        "failure_class_counts": failure_class_counts,
        "max_attempt_count": max((int(event.get("attempt_count", 0)) for event in events), default=0),
        "events": retained_events,
    }


def _failure_domain(operation: str) -> str:
    lowered = operation.lower()
    if "cog" in lowered or "asset" in lowered or "gdal" in lowered or "read" in lowered:
        return "asset"
    return "endpoint"


def _status_code_from_message(message: str) -> int | None:
    for code in sorted(TRANSIENT_HTTP_STATUS_CODES | DETERMINISTIC_HTTP_STATUS_CODES):
        needles = (
            f"HTTP {code}",
            f"HTTP response code: {code}",
            f"status {code}",
            f"code {code}",
            f": {code}",
        )
        if any(needle in message for needle in needles):
            return code
    return None


def classify_remote_failure(exc: BaseException, operation: str) -> dict[str, Any]:
    domain = _failure_domain(operation)
    message = str(exc)
    status_code: int | None = None
    transient = False

    if isinstance(exc, urllib.error.HTTPError):
        status_code = int(exc.code)
        transient = status_code in TRANSIENT_HTTP_STATUS_CODES
    elif isinstance(exc, (TimeoutError, socket.timeout)):
        transient = True
    elif isinstance(exc, urllib.error.URLError):
        transient = True
    else:
        status_code = _status_code_from_message(message)
        transient_tokens = (
            "timed out",
            "timeout",
            "temporarily unavailable",
            "connection reset",
            "connection refused",
            "curl error",
            "server returned nothing",
        )
        transient = (status_code in TRANSIENT_HTTP_STATUS_CODES) or any(
            token in message.lower() for token in transient_tokens
        )

    if transient:
        failure_class = "transient_asset_read_failure" if domain == "asset" else "transient_endpoint_failure"
    else:
        failure_class = "deterministic_asset_read_failure" if domain == "asset" else "deterministic_endpoint_failure"
    if isinstance(exc, urllib.error.HTTPError):
        try:
            exc.close()
        except Exception:
            pass
    return {
        "operation": operation,
        "transient": transient,
        "failure_class": failure_class,
        "status_code": status_code,
        "exception_type": type(exc).__name__,
        "message": message,
    }


def _retry_delay_seconds(
    policy: dict[str, Any], attempt_number: int, random_func: Callable[[], float]
) -> float:
    base = policy["initial_delay_seconds"] * (policy["backoff_multiplier"] ** max(0, attempt_number - 1))
    delay = min(policy["max_delay_seconds"], base)
    if delay and policy["jitter_fraction"]:
        jitter = delay * policy["jitter_fraction"] * ((random_func() * 2.0) - 1.0)
        delay = max(0.0, delay + jitter)
    return delay


def retry_remote_operation(
    operation: str,
    context: dict[str, Any],
    config: dict[str, Any] | None,
    action: Callable[[], Any],
    sleep_func: Callable[[float], None] = time.sleep,
    random_func: Callable[[], float] = random.random,
) -> Any:
    policy = normalise_retry_policy(config)
    last_classification: dict[str, Any] | None = None
    for attempt in range(1, policy["max_attempts"] + 1):
        try:
            result = action()
        except Exception as exc:
            classification = classify_remote_failure(exc, operation)
            last_classification = classification
            can_retry = classification["transient"] and attempt < policy["max_attempts"]
            if can_retry:
                sleep_func(_retry_delay_seconds(policy, attempt, random_func))
                continue
            event = {
                "operation": operation,
                "context": context,
                "attempt_count": attempt,
                "max_attempts": policy["max_attempts"],
                "final_status": "exhausted_transient_failure"
                if classification["transient"]
                else "deterministic_failure",
                "failure_class": classification["failure_class"],
                "status_code": classification["status_code"],
                "exception_type": classification["exception_type"],
                "last_error": classification["message"],
            }
            RETRY_AUDIT_LOG.append(event)
            if classification["transient"]:
                raise RetryExhaustedError(event) from exc
            raise
        else:
            if attempt > 1:
                event = {
                    "operation": operation,
                    "context": context,
                    "attempt_count": attempt,
                    "max_attempts": policy["max_attempts"],
                    "final_status": "success_after_retry",
                    "failure_class": last_classification["failure_class"] if last_classification else "",
                    "status_code": last_classification["status_code"] if last_classification else None,
                    "exception_type": last_classification["exception_type"] if last_classification else "",
                    "last_error": last_classification["message"] if last_classification else "",
                }
                RETRY_AUDIT_LOG.append(event)
            return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def month_range(month: str) -> tuple[str, str]:
    year, mon = map(int, month.split("-"))
    start = dt.datetime(year, mon, 1, tzinfo=dt.UTC)
    stop = dt.datetime(year + (mon == 12), 1 if mon == 12 else mon + 1, 1, tzinfo=dt.UTC)
    return start.isoformat().replace("+00:00", "Z"), stop.isoformat().replace("+00:00", "Z")


def post_json(url: str, payload: dict[str, Any], timeout: int = 90) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def fetch_ramsar_subset(config: dict[str, Any]) -> tuple[dict[str, Any], str]:
    refcodes = ",".join(str(candidate["ramsar_refcode"]) for candidate in config["candidates"])
    params = {
        "where": f"REFCODE IN ({refcodes})",
        "outFields": (
            "OBJECTID,REFCODE,STATE,AREA_HA,TOTAL_SITE_AREA_HA,SOURCE,RAMSAR_NAME,"
            "WETLAND_NAME,JURISDICTION,GAZETTED_AREA_HA,WETLANDSDB_URL,METADATA_URL"
        ),
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    url = f"{config['ramsar_service_layer_url']}/query?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=90) as response:
        payload = response.read()
    return json.loads(payload), url


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def s3_to_vsi(href: str) -> str:
    if href.startswith("s3://"):
        return "/vsis3/" + href.removeprefix("s3://")
    return href


def wgs84_srs() -> osr.SpatialReference:
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return srs


def epsg_srs(epsg: int) -> osr.SpatialReference:
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return srs


def transform_geometry(
    geom: ogr.Geometry, source_srs: osr.SpatialReference, target_srs: osr.SpatialReference
) -> ogr.Geometry:
    clone = geom.Clone()
    transform = osr.CoordinateTransformation(source_srs, target_srs)
    clone.Transform(transform)
    return clone


def geometry_from_feature(feature: dict[str, Any]) -> ogr.Geometry:
    return ogr.CreateGeometryFromJson(json.dumps(feature["geometry"]))


def union_geometries(geometries: list[ogr.Geometry]) -> ogr.Geometry:
    if not geometries:
        raise ValueError("cannot union an empty geometry list")
    union = geometries[0].Clone()
    for geom in geometries[1:]:
        union = union.Union(geom)
    return union


def geometry_hash(features: list[dict[str, Any]]) -> str:
    selected = [
        {
            "id": feature.get("id"),
            "properties": feature.get("properties", {}),
            "geometry": feature.get("geometry", {}),
        }
        for feature in sorted(features, key=lambda item: item.get("id"))
    ]
    payload = json.dumps(selected, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def support_grid(
    geom_albers: ogr.Geometry, pixel_size: int
) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float, float, float], int, int]:
    minx, maxx, miny, maxy = geom_albers.GetEnvelope()
    minx = math.floor(minx / pixel_size) * pixel_size
    maxx = math.ceil(maxx / pixel_size) * pixel_size
    miny = math.floor(miny / pixel_size) * pixel_size
    maxy = math.ceil(maxy / pixel_size) * pixel_size
    xsize = int(round((maxx - minx) / pixel_size))
    ysize = int(round((maxy - miny) / pixel_size))
    if xsize <= 0 or ysize <= 0:
        raise ValueError("support grid has zero width or height")
    geotransform = (minx, pixel_size, 0.0, maxy, 0.0, -pixel_size)
    return (minx, miny, maxx, maxy), geotransform, xsize, ysize


def rasterize_geometry(
    geom: ogr.Geometry,
    srs: osr.SpatialReference,
    geotransform: tuple[float, float, float, float, float, float],
    xsize: int,
    ysize: int,
) -> np.ndarray:
    raster = gdal.GetDriverByName("MEM").Create("", xsize, ysize, 1, gdal.GDT_Byte)
    raster.SetGeoTransform(geotransform)
    raster.SetProjection(srs.ExportToWkt())
    band = raster.GetRasterBand(1)
    band.Fill(0)
    vector = memory_vector_driver().CreateDataSource("")
    layer = vector.CreateLayer("support", srs=srs, geom_type=ogr.wkbMultiPolygon)
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetGeometry(geom.Clone())
    layer.CreateFeature(feature)
    gdal.RasterizeLayer(raster, [1], layer, burn_values=[1])
    return band.ReadAsArray().astype(bool)


def memory_vector_driver():
    driver = ogr.GetDriverByName("MEM")
    if driver is not None:
        return driver
    driver = ogr.GetDriverByName("Memory")
    if driver is None:
        raise RuntimeError("No in-memory OGR vector driver is available")
    return driver


def summarise_support_month(scene_values: list[np.ndarray], support_mask: np.ndarray) -> dict[str, Any]:
    n_scene = len(scene_values)
    n_pixel = int(support_mask.sum())
    pixel_area_m2 = 900
    empty = {
        "n_scene_m": n_scene,
        "n_pixel_u": n_pixel,
        "clear_obs_count": 0,
        "invalid_obs_count": 0,
        "clear_obs_fraction": None,
        "current_wet_area_m2": None,
        "valid_support_area_m2": 0,
        "current_proportion_wet": None,
        "wet_pixel_observation_count": 0,
        "dry_pixel_observation_count": 0,
        "clear_pixel_count": 0,
        "quality_flag": "quality_fail",
        "wet_month_flag": None,
    }
    empty.update({field: 0 for field in INVALID_BITS})
    if n_scene == 0 or n_pixel == 0:
        return empty

    clear_per_pixel = np.zeros(support_mask.shape, dtype=np.uint16)
    wet_per_pixel = np.zeros(support_mask.shape, dtype=np.uint16)
    invalid_obs_count = 0
    invalid_bit_counts = {field: 0 for field in INVALID_BITS}
    clear_obs_count = 0
    wet_obs_count = 0
    dry_obs_count = 0

    for values in scene_values:
        support_values = values[support_mask]
        invalid = (support_values & INVALID_MASK) != 0
        clear = (support_values == 0) | (support_values == WATER_BIT)
        wet = support_values == WATER_BIT
        dry = support_values == 0
        invalid_obs_count += int(invalid.sum())
        clear_obs_count += int(clear.sum())
        wet_obs_count += int(wet.sum())
        dry_obs_count += int(dry.sum())
        for field, bit in INVALID_BITS.items():
            invalid_bit_counts[field] += int(((support_values & bit) != 0).sum())
        scene_clear = np.zeros(support_mask.shape, dtype=np.uint8)
        scene_wet = np.zeros(support_mask.shape, dtype=np.uint8)
        scene_clear[support_mask] = clear.astype(np.uint8)
        scene_wet[support_mask] = wet.astype(np.uint8)
        clear_per_pixel += scene_clear
        wet_per_pixel += scene_wet

    valid_pixels = clear_per_pixel > 0
    valid_pixel_count = int(valid_pixels.sum())
    pixel_wet_fraction = np.zeros(support_mask.shape, dtype=np.float32)
    pixel_wet_fraction[valid_pixels] = wet_per_pixel[valid_pixels] / clear_per_pixel[valid_pixels]
    current_wet_area_m2 = float(pixel_wet_fraction[valid_pixels].sum() * pixel_area_m2)
    valid_support_area_m2 = valid_pixel_count * pixel_area_m2
    clear_obs_fraction = clear_obs_count / (n_scene * n_pixel)
    clear_pixel_fraction = valid_pixel_count / n_pixel if n_pixel else 0.0
    current_proportion_wet = (
        current_wet_area_m2 / valid_support_area_m2 if valid_support_area_m2 else None
    )
    if n_scene >= 2 and clear_pixel_fraction >= 0.80 and clear_obs_fraction >= 0.40:
        quality_flag = "quality_high"
    elif n_scene >= 1 and clear_pixel_fraction >= 0.50 and clear_obs_fraction >= 0.20:
        quality_flag = "quality_minimum"
    else:
        quality_flag = "quality_fail"
    wet_month_flag = (
        bool(current_proportion_wet is not None and current_proportion_wet >= 0.05)
        if quality_flag != "quality_fail"
        else None
    )
    result = {
        "n_scene_m": n_scene,
        "n_pixel_u": n_pixel,
        "clear_obs_count": clear_obs_count,
        "invalid_obs_count": invalid_obs_count,
        "clear_obs_fraction": clear_obs_fraction,
        "current_wet_area_m2": current_wet_area_m2,
        "valid_support_area_m2": valid_support_area_m2,
        "current_proportion_wet": current_proportion_wet,
        "wet_pixel_observation_count": wet_obs_count,
        "dry_pixel_observation_count": dry_obs_count,
        "clear_pixel_count": valid_pixel_count,
        "clear_pixel_fraction": clear_pixel_fraction,
        "quality_flag": quality_flag,
        "wet_month_flag": wet_month_flag,
    }
    result.update(invalid_bit_counts)
    return result


def stac_search(config: dict[str, Any], bbox: tuple[float, float, float, float], month: str) -> dict[str, Any]:
    start, stop = month_range(month)
    minx, maxx, miny, maxy = bbox
    payload = {
        "collections": [config["dea_collection"]],
        "bbox": [minx, miny, maxx, maxy],
        "datetime": f"{start}/{stop}",
        "limit": int(config["stac_limit"]),
    }
    data = retry_remote_operation(
        "dea_stac_search",
        {"month": month, "bbox": [minx, miny, maxx, maxy]},
        config,
        lambda: post_json(config["dea_stac_search_url"], payload),
    )
    data["_query_payload"] = payload
    return data


def warp_scene_to_grid(
    href: str,
    bounds: tuple[float, float, float, float],
    xsize: int,
    ysize: int,
    dst_srs: str,
    config: dict[str, Any] | None = None,
) -> np.ndarray:
    def read_scene() -> np.ndarray:
        dataset = gdal.Open(s3_to_vsi(href))
        if dataset is None:
            raise RuntimeError(f"GDAL could not open {href}")
        warped = gdal.Warp(
            "",
            dataset,
            format="MEM",
            dstSRS=dst_srs,
            outputBounds=bounds,
            width=xsize,
            height=ysize,
            resampleAlg="near",
            outputType=gdal.GDT_Byte,
            dstNodata=1,
            errorThreshold=0.0,
        )
        if warped is None:
            raise RuntimeError(f"GDAL warp returned no dataset for {href}")
        array = warped.ReadAsArray()
        if array is None:
            raise RuntimeError(f"GDAL warp returned no array for {href}")
        return array.astype(np.uint8, copy=False)

    return retry_remote_operation(
        "remote_cog_read",
        {"href": href, "xsize": xsize, "ysize": ysize},
        config,
        read_scene,
    )


def format_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float):
        return round(value, 6)
    return value


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field, "")) for field in fieldnames})


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def build_supports(
    config: dict[str, Any], subset_geojson: dict[str, Any], raw_path: Path, raw_sha: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    wgs84 = wgs84_srs()
    albers = epsg_srs(3577)
    features = subset_geojson.get("features", [])
    geometry_rows: list[dict[str, Any]] = []
    supports: list[dict[str, Any]] = []
    for candidate in config["candidates"]:
        refcode = candidate["ramsar_refcode"]
        selected = [feature for feature in features if feature["properties"].get("REFCODE") == refcode]
        if not selected:
            geometry_rows.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "candidate_name": candidate["candidate_name"],
                    "support_id": candidate["support_id"],
                    "support_type": candidate["support_type"],
                    "source": "DCCEEW Geospatial Ramsar Wetlands service",
                    "source_id_or_url": config["ramsar_service_layer_url"],
                    "source_feature_refcode": refcode,
                    "source_objectids": "",
                    "component_count": 0,
                    "staged_path_class": "blocked_no_feature",
                    "geometry_area_m2": "",
                    "geometry_area_ha": "",
                    "geometry_hash_sha256": "",
                    "source_hash_sha256": raw_sha,
                    "inclusion_status": "blocked_no_official_support_feature",
                    "caveat": "No Ramsar feature matched the configured REFCODE.",
                }
            )
            continue
        geometries = [geometry_from_feature(feature) for feature in selected]
        union_wgs84 = union_geometries(geometries)
        union_albers = transform_geometry(union_wgs84, wgs84, albers)
        area_m2 = float(union_albers.GetArea())
        objectids = [str(feature.get("id")) for feature in selected]
        ramsar_names = sorted({feature["properties"].get("RAMSAR_NAME", "") for feature in selected})
        wetland_names = sorted({feature["properties"].get("WETLAND_NAME", "") for feature in selected})
        row = {
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["candidate_name"],
            "support_id": candidate["support_id"],
            "support_type": candidate["support_type"],
            "source": "DCCEEW Geospatial Ramsar Wetlands service",
            "source_id_or_url": config["ramsar_service_layer_url"],
            "source_feature_refcode": refcode,
            "source_objectids": ";".join(objectids),
            "component_count": len(selected),
            "staged_path_class": "ignored_raw_geojson_subset",
            "geometry_area_m2": area_m2,
            "geometry_area_ha": area_m2 / 10000,
            "geometry_hash_sha256": geometry_hash(selected),
            "source_hash_sha256": raw_sha,
            "inclusion_status": "included_for_real_support_hydrology",
            "caveat": candidate["source_geometry_caveat"],
        }
        geometry_rows.append(row)
        minx, maxx, miny, maxy = union_wgs84.GetEnvelope()
        supports.append(
            {
                "candidate": candidate,
                "features": selected,
                "feature_count": len(selected),
                "objectids": objectids,
                "ramsar_names": ramsar_names,
                "wetland_names": wetland_names,
                "geom_wgs84": union_wgs84,
                "geom_albers": union_albers,
                "bbox_wgs84": (minx, maxx, miny, maxy),
                "area_m2": area_m2,
                "raw_path": str(raw_path.relative_to(REPO)),
                "geometry_hash_sha256": row["geometry_hash_sha256"],
            }
        )
    return geometry_rows, supports


def process_hydrology(config: dict[str, Any], supports: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    gdal.SetConfigOption("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
    albers = epsg_srs(3577)
    pixel_size = int(config["pixel_size_m"])
    max_grid_pixels = int(config["max_reference_grid_pixels"])
    hydrology_rows: list[dict[str, Any]] = []
    manifest_supports: list[dict[str, Any]] = []
    for support in supports:
        candidate = support["candidate"]
        base_row = {
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["candidate_name"],
            "support_id": candidate["support_id"],
            "support_type": candidate["support_type"],
            "source_geometry": "DCCEEW Geospatial Ramsar Wetlands service",
            "source_geometry_caveat": candidate["source_geometry_caveat"],
            "support_area_m2": support["area_m2"],
            "geometry_hash_sha256": support["geometry_hash_sha256"],
            "dea_product": config["source_product"],
            "dea_product_version": config["source_product_version"],
            "metric_spec_version": config["metric_spec_version"],
        }
        support_record = {
            "candidate_id": candidate["candidate_id"],
            "support_id": candidate["support_id"],
            "support_area_m2": round(support["area_m2"], 3),
            "component_count": support["feature_count"],
            "months": [],
        }
        try:
            bounds, geotransform, xsize, ysize = support_grid(support["geom_albers"], pixel_size)
            grid_pixels = xsize * ysize
            if grid_pixels > max_grid_pixels:
                raise RuntimeError(
                    f"reference grid has {grid_pixels} cells, above configured maximum {max_grid_pixels}"
                )
            support_mask = rasterize_geometry(support["geom_albers"], albers, geotransform, xsize, ysize)
        except Exception as exc:
            for month in config["months"]:
                row = dict(base_row)
                row.update(
                    {
                        "month": month["month"],
                        "month_rationale": month["rationale"],
                        "access_method": "blocked before Water Observations read",
                        "status": "blocked_support_grid",
                        "stac_items_found": 0,
                        "readable_scene_count": 0,
                        "skipped_scene_count": 0,
                        "n_scene_m": 0,
                        "n_pixel_u": "",
                        "clear_obs_count": "",
                        "invalid_obs_count": "",
                        "clear_obs_fraction": "",
                        "current_wet_area_m2": "",
                        "valid_support_area_m2": "",
                        "current_proportion_wet": "",
                        "wet_pixel_observation_count": "",
                        "dry_pixel_observation_count": "",
                        "quality_flag": "quality_fail",
                        "wet_month_flag": "",
                        **{field: "" for field in INVALID_BITS},
                        "failure_or_caveat": str(exc),
                    }
                )
                hydrology_rows.append(row)
                support_record["months"].append({"month": month["month"], "status": row["status"], "caveat": str(exc)})
            manifest_supports.append(support_record)
            continue
        for month in config["months"]:
            month_name = month["month"]
            row = dict(base_row)
            row.update({"month": month_name, "month_rationale": month["rationale"]})
            scene_arrays: list[np.ndarray] = []
            scene_records: list[dict[str, Any]] = []
            skipped: list[dict[str, str]] = []
            try:
                stac = stac_search(config, support["bbox_wgs84"], month_name)
                features = sorted(
                    stac.get("features", []),
                    key=lambda feature: feature.get("properties", {}).get("datetime", ""),
                )
                for feature in features:
                    href = feature.get("assets", {}).get("water", {}).get("href")
                    if not href:
                        skipped.append({"id": feature.get("id", ""), "reason": "missing water asset"})
                        continue
                    try:
                        array = warp_scene_to_grid(href, bounds, xsize, ysize, config["reference_crs"])
                        scene_arrays.append(array)
                        scene_records.append(
                            {
                                "id": feature.get("id", ""),
                                "datetime": feature.get("properties", {}).get("datetime", ""),
                                "href": href,
                            }
                        )
                    except Exception as exc:
                        skipped.append({"id": feature.get("id", ""), "reason": str(exc)})
                metrics = summarise_support_month(scene_arrays, support_mask)
                status = "computed_real_support_metrics" if scene_arrays else "blocked_no_readable_water_observations_scene"
                row.update(
                    {
                        "access_method": "DCCEEW Ramsar geometry plus DEA STAC and GDAL warp to EPSG:3577 support grid",
                        "status": status,
                        "stac_items_found": len(features),
                        "readable_scene_count": len(scene_records),
                        "skipped_scene_count": len(skipped),
                        **metrics,
                        "failure_or_caveat": candidate["source_geometry_caveat"]
                        if scene_arrays
                        else "No readable Water Observations scene could be warped for this support/month.",
                    }
                )
                support_record["months"].append(
                    {
                        "month": month_name,
                        "status": status,
                        "stac_items_found": len(features),
                        "readable_scene_count": len(scene_records),
                        "skipped_scene_count": len(skipped),
                        "scene_ids": [scene["id"] for scene in scene_records],
                        "skipped": skipped[:10],
                    }
                )
            except Exception as exc:
                row.update(
                    {
                        "access_method": "DCCEEW Ramsar geometry plus DEA STAC and GDAL warp to EPSG:3577 support grid",
                        "status": "blocked_hydrology_processing_error",
                        "stac_items_found": 0,
                        "readable_scene_count": 0,
                        "skipped_scene_count": 0,
                        "n_scene_m": 0,
                        "n_pixel_u": int(support_mask.sum()),
                        "clear_obs_count": "",
                        "invalid_obs_count": "",
                        "clear_obs_fraction": "",
                        "current_wet_area_m2": "",
                        "valid_support_area_m2": "",
                        "current_proportion_wet": "",
                        "wet_pixel_observation_count": "",
                        "dry_pixel_observation_count": "",
                        "quality_flag": "quality_fail",
                        "wet_month_flag": "",
                        **{field: "" for field in INVALID_BITS},
                        "failure_or_caveat": str(exc),
                    }
                )
                support_record["months"].append({"month": month_name, "status": row["status"], "caveat": str(exc)})
            hydrology_rows.append(row)
        support_record["reference_grid"] = {
            "crs": config["reference_crs"],
            "pixel_size_m": pixel_size,
            "xsize": xsize,
            "ysize": ysize,
            "grid_pixels": xsize * ysize,
            "support_mask_pixels": int(support_mask.sum()),
            "bounds": [round(value, 3) for value in bounds],
        }
        manifest_supports.append(support_record)
    return hydrology_rows, manifest_supports


def run() -> int:
    start_time = time.time()
    config = load_json(CONFIG_PATH)
    for relpath in config["scratch_paths"].values():
        (REPO / relpath).mkdir(parents=True, exist_ok=True)
    raw_geojson_path = REPO / config["staged_files"]["ramsar_subset_geojson"]
    subset_geojson, service_query_url = fetch_ramsar_subset(config)
    raw_geojson_path.parent.mkdir(parents=True, exist_ok=True)
    raw_payload = json.dumps(subset_geojson, indent=2).encode("utf-8")
    raw_geojson_path.write_bytes(raw_payload)
    raw_sha = sha256_file(raw_geojson_path)
    geometry_rows, supports = build_supports(config, subset_geojson, raw_geojson_path, raw_sha)
    hydrology_rows, hydrology_support_manifest = process_hydrology(config, supports)

    outputs = {name: REPO / relpath for name, relpath in config["outputs"].items()}
    geometry_fields = [
        "candidate_id",
        "candidate_name",
        "support_id",
        "support_type",
        "source",
        "source_id_or_url",
        "source_feature_refcode",
        "source_objectids",
        "component_count",
        "staged_path_class",
        "geometry_area_m2",
        "geometry_area_ha",
        "geometry_hash_sha256",
        "source_hash_sha256",
        "inclusion_status",
        "caveat",
    ]
    hydrology_fields = [
        "candidate_id",
        "candidate_name",
        "support_id",
        "support_type",
        "month",
        "month_rationale",
        "source_geometry",
        "source_geometry_caveat",
        "support_area_m2",
        "geometry_hash_sha256",
        "dea_product",
        "dea_product_version",
        "metric_spec_version",
        "access_method",
        "status",
        "stac_items_found",
        "readable_scene_count",
        "skipped_scene_count",
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
        *INVALID_BITS.keys(),
        "failure_or_caveat",
    ]
    write_csv(outputs["geometry_summary_csv"], geometry_rows, geometry_fields)
    write_csv(outputs["hydrology_summary_csv"], hydrology_rows, hydrology_fields)

    now = dt.datetime.now(dt.UTC).isoformat()
    staged_size = raw_geojson_path.stat().st_size
    geometry_manifest = {
        "goal": config["goal"],
        "manifest_type": "official_support_geometry",
        "accessed_at_utc": now,
        "command": "python3 scripts/official_support_hydrology_005.py",
        "config_path": str(CONFIG_PATH.relative_to(REPO)),
        "source_urls": {
            "ramsar_dataset_catalogue": config["ramsar_dataset_catalogue_url"],
            "ramsar_service_layer": config["ramsar_service_layer_url"],
            "ramsar_service_query": service_query_url,
        },
        "staged_raw_files": [
            {
                "path": str(raw_geojson_path.relative_to(REPO)),
                "bytes": staged_size,
                "sha256": raw_sha,
                "committed": False,
            }
        ],
        "cleanup_status": "raw Ramsar subset left only in ignored staging path for reproducibility; not committed",
        "candidate_count": len(config["candidates"]),
        "support_rows": len(geometry_rows),
        "supports": [
            {
                "candidate_id": row["candidate_id"],
                "support_id": row["support_id"],
                "support_type": row["support_type"],
                "source_feature_refcode": row["source_feature_refcode"],
                "source_objectids": row["source_objectids"],
                "component_count": row["component_count"],
                "geometry_area_m2": round(row["geometry_area_m2"], 3) if row["geometry_area_m2"] else "",
                "inclusion_status": row["inclusion_status"],
                "caveat": row["caveat"],
            }
            for row in geometry_rows
        ],
        "outputs": {
            "summary_csv": str(outputs["geometry_summary_csv"].relative_to(REPO)),
            "manifest_json": str(outputs["geometry_manifest_json"].relative_to(REPO)),
        },
        "git_commit_at_run": git_commit(),
    }
    hydrology_manifest = {
        "goal": config["goal"],
        "manifest_type": "real_support_hydrology",
        "metric_spec_version": config["metric_spec_version"],
        "started_at_utc": dt.datetime.fromtimestamp(start_time, tz=dt.UTC).isoformat(),
        "finished_at_utc": now,
        "elapsed_seconds": round(time.time() - start_time, 3),
        "command": "python3 scripts/official_support_hydrology_005.py",
        "python_version": sys.version,
        "platform": platform.platform(),
        "gdal_version": gdal.VersionInfo("--version"),
        "numpy_version": np.__version__,
        "config_path": str(CONFIG_PATH.relative_to(REPO)),
        "months": config["months"],
        "source_products": {
            "dea_stac_search": config["dea_stac_search_url"],
            "dea_collection": config["dea_collection"],
            "dea_water_observations_product": "https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/?tab=overview",
            "ramsar_service_layer": config["ramsar_service_layer_url"],
        },
        "scratch_paths": config["scratch_paths"],
        "staged_raw_files": geometry_manifest["staged_raw_files"],
        "staged_file_sizes_bytes": {
            str(raw_geojson_path.relative_to(REPO)): staged_size,
        },
        "cleanup_status": geometry_manifest["cleanup_status"],
        "outputs": {
            "summary_csv": str(outputs["hydrology_summary_csv"].relative_to(REPO)),
            "manifest_json": str(outputs["hydrology_manifest_json"].relative_to(REPO)),
        },
        "row_count": len(hydrology_rows),
        "status_counts": {
            status: sum(row["status"] == status for row in hydrology_rows)
            for status in sorted({row["status"] for row in hydrology_rows})
        },
        "supports": hydrology_support_manifest,
        "git_commit_at_run": git_commit(),
    }
    write_json(outputs["geometry_manifest_json"], geometry_manifest)
    write_json(outputs["hydrology_manifest_json"], hydrology_manifest)
    print(f"wrote {outputs['geometry_summary_csv'].relative_to(REPO)}")
    print(f"wrote {outputs['geometry_manifest_json'].relative_to(REPO)}")
    print(f"wrote {outputs['hydrology_summary_csv'].relative_to(REPO)}")
    print(f"wrote {outputs['hydrology_manifest_json'].relative_to(REPO)}")
    print(json.dumps({"hydrology_rows": len(hydrology_rows), "status_counts": hydrology_manifest["status_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
