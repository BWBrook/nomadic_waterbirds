#!/usr/bin/env python3
"""Goal 006 documented subunit hydrology prototype.

Stages Ramsar component geometry and DEA Waterbodies v3 raw inputs only under
ignored paths, builds a parent-child subunit registry, and computes bounded
monthly DEA Water Observations metrics for selected child supports.
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
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
from osgeo import gdal, ogr, osr

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from official_support_hydrology_005 import (  # noqa: E402
    INVALID_BITS,
    epsg_srs,
    format_value,
    geometry_from_feature,
    month_range,
    rasterize_geometry,
    sha256_bytes,
    sha256_file,
    stac_search,
    summarise_support_month,
    support_grid,
    transform_geometry,
    union_geometries,
    wgs84_srs,
    warp_scene_to_grid,
    write_csv,
    write_json,
)

gdal.UseExceptions()
ogr.UseExceptions()

REPO = SCRIPT_DIR.parents[0]
CONFIG_PATH = REPO / "settings" / "subunit_hydrology_006.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def quiet_git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


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


def ensure_download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as response, path.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def feature_objectid(feature: dict[str, Any]) -> int:
    return int(feature.get("properties", {}).get("OBJECTID", feature.get("id")))


def ramsar_component_id(candidate_id: str, objectid: int) -> str:
    return f"{candidate_id.lower()}_ramsar_component_{objectid}"


def waterbody_subunit_id(candidate_id: str, uid: str) -> str:
    clean_uid = uid.replace("-", "_").replace(".", "_")
    return f"{candidate_id.lower()}_dea_waterbody_{clean_uid}"


def ramsar_component_registry_rows(candidate: dict[str, Any], features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_objectids = {int(value) for value in candidate.get("selected_ramsar_objectids", [])}
    rows: list[dict[str, Any]] = []
    for feature in sorted(features, key=feature_objectid):
        props = feature.get("properties", {})
        objectid = feature_objectid(feature)
        selected = objectid in selected_objectids
        area_m2 = float(props.get("AREA_HA") or 0.0) * 10000.0
        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "candidate_name": candidate["candidate_name"],
                "parent_support_id": candidate["parent_support_id"],
                "parent_support_type": candidate.get("parent_support_type", ""),
                "subunit_id": ramsar_component_id(candidate["candidate_id"], objectid),
                "subunit_name": props.get("WETLAND_NAME") or props.get("RAMSAR_NAME") or "",
                "subunit_type": "ramsar_component",
                "source": "DCCEEW Geospatial Ramsar Wetlands service",
                "source_identifier": f"REFCODE={props.get('REFCODE')};OBJECTID={objectid}",
                "source_url": candidate.get("source_url", ""),
                "component_objectid": objectid,
                "waterbody_uid": "",
                "overlap_rank": "",
                "subunit_area_m2": area_m2,
                "overlap_area_m2": area_m2,
                "overlap_fraction_of_subunit": 1.0 if area_m2 else "",
                "overlap_fraction_of_parent": "",
                "selected_for_hydrology": "yes" if selected else "no",
                "inclusion_status": "included_for_subunit_hydrology" if selected else "retained_for_later",
                "caveat": candidate.get("subunit_caveat", ""),
            }
        )
    return rows


def build_parent_supports(
    config: dict[str, Any], ramsar_subset: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    wgs84 = wgs84_srs()
    albers = epsg_srs(3577)
    features_by_refcode: dict[int, list[dict[str, Any]]] = {}
    for feature in ramsar_subset.get("features", []):
        refcode = int(feature["properties"]["REFCODE"])
        features_by_refcode.setdefault(refcode, []).append(feature)
    parents: dict[str, dict[str, Any]] = {}
    for candidate in config["candidates"]:
        refcode = int(candidate["ramsar_refcode"])
        features = features_by_refcode.get(refcode, [])
        if not features:
            continue
        geoms_wgs84 = [geometry_from_feature(feature) for feature in features]
        union_wgs84 = union_geometries(geoms_wgs84)
        union_albers = transform_geometry(union_wgs84, wgs84, albers)
        parents[candidate["candidate_id"]] = {
            "candidate": candidate,
            "features": features,
            "geom_wgs84": union_wgs84,
            "geom_albers": union_albers,
            "area_m2": float(union_albers.GetArea()),
        }
    return parents, features_by_refcode


def geometry_hash_wkb(geom: ogr.Geometry) -> str:
    return hashlib.sha256(geom.ExportToWkb()).hexdigest()


def feature_geometry_hash(feature: dict[str, Any]) -> str:
    payload = json.dumps(
        {"id": feature.get("id"), "geometry": feature.get("geometry"), "properties": feature.get("properties")},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def waterbodies_layer(zip_path: Path) -> tuple[ogr.DataSource, ogr.Layer]:
    dataset_path = f"/vsizip/{zip_path}/ga_ls_wb_3_v3.shp"
    dataset = ogr.Open(dataset_path)
    if dataset is None:
        raise RuntimeError(f"could not open DEA Waterbodies shapefile from {zip_path}")
    return dataset, dataset.GetLayer(0)


def waterbody_overlap_rows(
    config: dict[str, Any], parents: dict[str, dict[str, Any]], zip_path: Path
) -> tuple[list[dict[str, Any]], dict[str, ogr.Geometry], dict[str, dict[str, Any]]]:
    _dataset, layer = waterbodies_layer(zip_path)
    rows: list[dict[str, Any]] = []
    selected_geoms: dict[str, ogr.Geometry] = {}
    selected_meta: dict[str, dict[str, Any]] = {}
    top_n = int(config["waterbody_registry_top_n_per_parent"])
    for candidate in config["candidates"]:
        parent_record = parents.get(candidate["candidate_id"])
        if not parent_record:
            continue
        parent = parent_record["geom_albers"]
        minx, maxx, miny, maxy = parent.GetEnvelope()
        layer.SetSpatialFilterRect(minx, miny, maxx, maxy)
        overlaps: list[dict[str, Any]] = []
        for feature in layer:
            geom = feature.GetGeometryRef()
            if geom is None or not geom.Intersects(parent):
                continue
            intersection = geom.Intersection(parent)
            if intersection is None or intersection.IsEmpty():
                continue
            overlap_area = float(intersection.GetArea())
            if overlap_area <= 0:
                continue
            uid = feature.GetField("uid")
            waterbody_area = float(feature.GetField("area_m2") or geom.GetArea())
            overlaps.append(
                {
                    "uid": uid,
                    "timeseries": feature.GetField("timeseries"),
                    "area_m2": waterbody_area,
                    "wet_sa_m2": feature.GetField("wet_sa_m2"),
                    "overlap_area_m2": overlap_area,
                    "overlap_fraction_of_subunit": overlap_area / waterbody_area if waterbody_area else None,
                    "overlap_fraction_of_parent": overlap_area / parent_record["area_m2"] if parent_record["area_m2"] else None,
                    "geometry_hash_sha256": geometry_hash_wkb(intersection),
                    "intersection_geom": intersection.Clone(),
                }
            )
        layer.ResetReading()
        layer.SetSpatialFilter(None)
        overlaps.sort(key=lambda item: (-item["overlap_area_m2"], item["uid"]))
        selected_count = int(candidate.get("selected_waterbody_overlap_count", 0))
        for rank, overlap in enumerate(overlaps[:top_n], start=1):
            selected = rank <= selected_count
            subunit_id = waterbody_subunit_id(candidate["candidate_id"], overlap["uid"])
            row = {
                "candidate_id": candidate["candidate_id"],
                "candidate_name": candidate["candidate_name"],
                "parent_support_id": candidate["parent_support_id"],
                "parent_support_type": candidate["parent_support_type"],
                "subunit_id": subunit_id,
                "subunit_name": f"DEA Waterbody {overlap['uid']}",
                "subunit_type": "dea_waterbody_overlap",
                "source": "DEA Waterbodies v3 shapefile",
                "source_identifier": overlap["uid"],
                "source_url": config["dea_waterbodies_zip_url"],
                "component_objectid": "",
                "waterbody_uid": overlap["uid"],
                "overlap_rank": rank,
                "subunit_area_m2": overlap["area_m2"],
                "overlap_area_m2": overlap["overlap_area_m2"],
                "overlap_fraction_of_subunit": overlap["overlap_fraction_of_subunit"],
                "overlap_fraction_of_parent": overlap["overlap_fraction_of_parent"],
                "selected_for_hydrology": "yes" if selected else "no",
                "inclusion_status": "included_for_subunit_hydrology" if selected else "retained_for_later",
                "caveat": "DEA Waterbodies polygon intersected with parent Ramsar support; open-water screening subunit only.",
            }
            rows.append(row)
            if selected:
                selected_geoms[subunit_id] = overlap["intersection_geom"]
                selected_meta[subunit_id] = {**row, "geometry_hash_sha256": overlap["geometry_hash_sha256"]}
    return rows, selected_geoms, selected_meta


def selected_ramsar_geometries(
    config: dict[str, Any], features_by_refcode: dict[int, list[dict[str, Any]]]
) -> tuple[dict[str, ogr.Geometry], dict[str, dict[str, Any]]]:
    wgs84 = wgs84_srs()
    albers = epsg_srs(3577)
    selected_geoms: dict[str, ogr.Geometry] = {}
    selected_meta: dict[str, dict[str, Any]] = {}
    for candidate in config["candidates"]:
        selected_objectids = {int(value) for value in candidate.get("selected_ramsar_objectids", [])}
        for feature in features_by_refcode.get(int(candidate["ramsar_refcode"]), []):
            objectid = feature_objectid(feature)
            if objectid not in selected_objectids:
                continue
            geom_wgs84 = geometry_from_feature(feature)
            geom_albers = transform_geometry(geom_wgs84, wgs84, albers)
            props = feature["properties"]
            subunit_id = ramsar_component_id(candidate["candidate_id"], objectid)
            selected_geoms[subunit_id] = geom_albers
            selected_meta[subunit_id] = {
                "candidate_id": candidate["candidate_id"],
                "candidate_name": candidate["candidate_name"],
                "parent_support_id": candidate["parent_support_id"],
                "parent_support_type": candidate["parent_support_type"],
                "subunit_id": subunit_id,
                "subunit_name": props.get("WETLAND_NAME") or props.get("RAMSAR_NAME") or "",
                "subunit_type": "ramsar_component",
                "source": "DCCEEW Geospatial Ramsar Wetlands service",
                "source_identifier": f"REFCODE={props.get('REFCODE')};OBJECTID={objectid}",
                "source_url": config["ramsar_service_layer_url"],
                "support_area_m2": float(geom_albers.GetArea()),
                "geometry_hash_sha256": feature_geometry_hash(feature),
                "caveat": candidate.get("subunit_caveat", ""),
            }
    return selected_geoms, selected_meta


def bbox_wgs84_from_albers(geom_albers: ogr.Geometry) -> tuple[float, float, float, float]:
    albers = epsg_srs(3577)
    wgs84 = wgs84_srs()
    geom_wgs84 = transform_geometry(geom_albers, albers, wgs84)
    return geom_wgs84.GetEnvelope()


def process_subunit_hydrology(
    config: dict[str, Any], selected_geoms: dict[str, ogr.Geometry], selected_meta: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    gdal.SetConfigOption("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
    albers = epsg_srs(3577)
    rows: list[dict[str, Any]] = []
    manifest_subunits: list[dict[str, Any]] = []
    for subunit_id, geom_albers in sorted(selected_geoms.items()):
        meta = selected_meta[subunit_id]
        record = {
            "candidate_id": meta["candidate_id"],
            "parent_support_id": meta["parent_support_id"],
            "subunit_id": subunit_id,
            "subunit_type": meta["subunit_type"],
            "months": [],
        }
        try:
            bounds, geotransform, xsize, ysize = support_grid(geom_albers, int(config["pixel_size_m"]))
            grid_pixels = xsize * ysize
            if grid_pixels > int(config["max_reference_grid_pixels"]):
                raise RuntimeError(
                    f"reference grid has {grid_pixels} cells, above configured maximum {config['max_reference_grid_pixels']}"
                )
            support_mask = rasterize_geometry(geom_albers, albers, geotransform, xsize, ysize)
            bbox_wgs84 = bbox_wgs84_from_albers(geom_albers)
        except Exception as exc:
            for month in config["months"]:
                rows.append(blocked_hydrology_row(config, meta, month, "blocked_subunit_grid", str(exc)))
                record["months"].append({"month": month["month"], "status": "blocked_subunit_grid", "caveat": str(exc)})
            manifest_subunits.append(record)
            continue
        for month in config["months"]:
            month_name = month["month"]
            scene_arrays: list[np.ndarray] = []
            scene_records: list[dict[str, Any]] = []
            skipped: list[dict[str, str]] = []
            try:
                stac = stac_search(config, bbox_wgs84, month_name)
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
                        scene_arrays.append(warp_scene_to_grid(href, bounds, xsize, ysize, config["reference_crs"]))
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
                status = "computed_subunit_metrics" if scene_arrays else "blocked_no_readable_water_observations_scene"
                row = hydrology_base_row(config, meta, month)
                row.update(
                    {
                        "access_method": "subunit geometry plus DEA STAC and GDAL warp to EPSG:3577 support grid",
                        "status": status,
                        "stac_items_found": len(features),
                        "readable_scene_count": len(scene_records),
                        "skipped_scene_count": len(skipped),
                        **metrics,
                        "failure_or_caveat": meta["caveat"]
                        if scene_arrays
                        else "No readable Water Observations scene could be warped for this subunit/month.",
                    }
                )
                rows.append(row)
                record["months"].append(
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
                rows.append(blocked_hydrology_row(config, meta, month, "blocked_subunit_processing_error", str(exc)))
                record["months"].append(
                    {"month": month_name, "status": "blocked_subunit_processing_error", "caveat": str(exc)}
                )
        record["reference_grid"] = {
            "crs": config["reference_crs"],
            "pixel_size_m": config["pixel_size_m"],
            "xsize": xsize,
            "ysize": ysize,
            "grid_pixels": xsize * ysize,
            "support_mask_pixels": int(support_mask.sum()),
            "bounds": [round(value, 3) for value in bounds],
        }
        manifest_subunits.append(record)
    return rows, manifest_subunits


def hydrology_base_row(config: dict[str, Any], meta: dict[str, Any], month: dict[str, str]) -> dict[str, Any]:
    return {
        "candidate_id": meta["candidate_id"],
        "candidate_name": meta["candidate_name"],
        "parent_support_id": meta["parent_support_id"],
        "parent_support_type": meta["parent_support_type"],
        "subunit_id": meta["subunit_id"],
        "subunit_name": meta["subunit_name"],
        "subunit_type": meta["subunit_type"],
        "month": month["month"],
        "month_rationale": month["rationale"],
        "source_geometry": meta["source"],
        "source_identifier": meta["source_identifier"],
        "source_geometry_caveat": meta["caveat"],
        "support_area_m2": meta["support_area_m2"],
        "geometry_hash_sha256": meta["geometry_hash_sha256"],
        "dea_product": config["source_product"],
        "dea_product_version": config["source_product_version"],
        "metric_spec_version": config["metric_spec_version"],
    }


def blocked_hydrology_row(
    config: dict[str, Any], meta: dict[str, Any], month: dict[str, str], status: str, caveat: str
) -> dict[str, Any]:
    row = hydrology_base_row(config, meta, month)
    row.update(
        {
            "access_method": "blocked before monthly Water Observations metrics",
            "status": status,
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
            "clear_pixel_count": "",
            "clear_pixel_fraction": "",
            "quality_flag": "quality_fail",
            "wet_month_flag": "",
            **{field: "" for field in INVALID_BITS},
            "failure_or_caveat": caveat,
        }
    )
    return row


def registry_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "candidate_name",
        "parent_support_id",
        "parent_support_type",
        "subunit_id",
        "subunit_name",
        "subunit_type",
        "source",
        "source_identifier",
        "source_url",
        "component_objectid",
        "waterbody_uid",
        "overlap_rank",
        "subunit_area_m2",
        "overlap_area_m2",
        "overlap_fraction_of_subunit",
        "overlap_fraction_of_parent",
        "selected_for_hydrology",
        "inclusion_status",
        "caveat",
    ]


def hydrology_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "candidate_name",
        "parent_support_id",
        "parent_support_type",
        "subunit_id",
        "subunit_name",
        "subunit_type",
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


def run() -> int:
    start_time = time.time()
    config = load_json(CONFIG_PATH)
    for relpath in config["scratch_paths"].values():
        (REPO / relpath).mkdir(parents=True, exist_ok=True)

    ramsar_path = REPO / config["staged_files"]["ramsar_subset_geojson"]
    waterbodies_zip = REPO / config["staged_files"]["dea_waterbodies_zip"]
    ramsar_subset, ramsar_query_url = fetch_ramsar_subset(config)
    ramsar_path.parent.mkdir(parents=True, exist_ok=True)
    ramsar_payload = json.dumps(ramsar_subset, indent=2).encode("utf-8")
    ramsar_path.write_bytes(ramsar_payload)
    ensure_download(config["dea_waterbodies_zip_url"], waterbodies_zip)

    parents, features_by_refcode = build_parent_supports(config, ramsar_subset)
    registry_rows: list[dict[str, Any]] = []
    for candidate in config["candidates"]:
        component_features = features_by_refcode.get(int(candidate["ramsar_refcode"]), [])
        registry_rows.extend(ramsar_component_registry_rows(candidate, component_features))

    waterbody_rows, selected_waterbody_geoms, selected_waterbody_meta = waterbody_overlap_rows(
        config, parents, waterbodies_zip
    )
    registry_rows.extend(waterbody_rows)

    selected_ramsar_geoms, selected_ramsar_meta = selected_ramsar_geometries(config, features_by_refcode)
    selected_geoms = {**selected_ramsar_geoms, **selected_waterbody_geoms}
    selected_meta = {**selected_ramsar_meta, **selected_waterbody_meta}
    for subunit_id, row in selected_waterbody_meta.items():
        row["support_area_m2"] = row["overlap_area_m2"]

    hydrology_rows, hydrology_manifest_subunits = process_subunit_hydrology(config, selected_geoms, selected_meta)

    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    write_csv(outputs["registry_csv"], registry_rows, registry_fieldnames())
    write_csv(outputs["hydrology_summary_csv"], hydrology_rows, hydrology_fieldnames())

    ramsar_sha = sha256_file(ramsar_path)
    waterbodies_sha = sha256_file(waterbodies_zip)
    staged_raw_files = [
        {
            "path": str(ramsar_path.relative_to(REPO)),
            "bytes": ramsar_path.stat().st_size,
            "sha256": ramsar_sha,
            "committed": False,
        },
        {
            "path": str(waterbodies_zip.relative_to(REPO)),
            "bytes": waterbodies_zip.stat().st_size,
            "sha256": waterbodies_sha,
            "committed": False,
        },
    ]
    waterbody_counts = {
        candidate["candidate_id"]: sum(
            row["candidate_id"] == candidate["candidate_id"] and row["subunit_type"] == "dea_waterbody_overlap"
            for row in registry_rows
        )
        for candidate in config["candidates"]
    }
    now = dt.datetime.now(dt.UTC).isoformat()
    registry_manifest = {
        "goal": config["goal"],
        "manifest_type": "subunit_support_registry",
        "accessed_at_utc": now,
        "command": "python3 scripts/subunit_hydrology_006.py",
        "config_path": str(CONFIG_PATH.relative_to(REPO)),
        "source_urls": {
            "ramsar_dataset_catalogue": config["ramsar_dataset_catalogue_url"],
            "ramsar_service_layer": config["ramsar_service_layer_url"],
            "ramsar_service_query": ramsar_query_url,
            "dea_waterbodies_product": config["dea_waterbodies_product_url"],
            "dea_waterbodies_zip": config["dea_waterbodies_zip_url"],
            "dea_waterbodies_s3_prefix": config["dea_waterbodies_s3_prefix_url"],
        },
        "staged_raw_files": staged_raw_files,
        "cleanup_status": "raw Ramsar subset and DEA Waterbodies ZIP left only in ignored staging paths; not committed",
        "registry_row_count": len(registry_rows),
        "ramsar_component_rows": sum(row["subunit_type"] == "ramsar_component" for row in registry_rows),
        "dea_waterbody_overlap_rows": sum(row["subunit_type"] == "dea_waterbody_overlap" for row in registry_rows),
        "waterbody_top_n_per_parent": config["waterbody_registry_top_n_per_parent"],
        "waterbody_registry_rows_by_candidate": waterbody_counts,
        "selected_subunit_count": sum(row["selected_for_hydrology"] == "yes" for row in registry_rows),
        "outputs": {
            "registry_csv": str(outputs["registry_csv"].relative_to(REPO)),
            "manifest_json": str(outputs["registry_manifest_json"].relative_to(REPO)),
        },
        "git_commit_at_run": quiet_git_commit(),
    }
    hydrology_manifest = {
        "goal": config["goal"],
        "manifest_type": "subunit_hydrology",
        "metric_spec_version": config["metric_spec_version"],
        "started_at_utc": dt.datetime.fromtimestamp(start_time, tz=dt.UTC).isoformat(),
        "finished_at_utc": now,
        "elapsed_seconds": round(time.time() - start_time, 3),
        "command": "python3 scripts/subunit_hydrology_006.py",
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
            "dea_waterbodies_product": config["dea_waterbodies_product_url"],
            "ramsar_service_layer": config["ramsar_service_layer_url"],
        },
        "scratch_paths": config["scratch_paths"],
        "staged_raw_files": staged_raw_files,
        "staged_file_sizes_bytes": {
            item["path"]: item["bytes"] for item in staged_raw_files
        },
        "cleanup_status": registry_manifest["cleanup_status"],
        "outputs": {
            "summary_csv": str(outputs["hydrology_summary_csv"].relative_to(REPO)),
            "manifest_json": str(outputs["hydrology_manifest_json"].relative_to(REPO)),
        },
        "row_count": len(hydrology_rows),
        "status_counts": {
            status: sum(row["status"] == status for row in hydrology_rows)
            for status in sorted({row["status"] for row in hydrology_rows})
        },
        "subunits": hydrology_manifest_subunits,
        "git_commit_at_run": quiet_git_commit(),
    }
    write_json(outputs["registry_manifest_json"], registry_manifest)
    write_json(outputs["hydrology_manifest_json"], hydrology_manifest)
    print(f"wrote {outputs['registry_csv'].relative_to(REPO)}")
    print(f"wrote {outputs['registry_manifest_json'].relative_to(REPO)}")
    print(f"wrote {outputs['hydrology_summary_csv'].relative_to(REPO)}")
    print(f"wrote {outputs['hydrology_manifest_json'].relative_to(REPO)}")
    print(json.dumps({"registry_rows": len(registry_rows), "hydrology_rows": len(hydrology_rows), "status_counts": hydrology_manifest["status_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
