#!/usr/bin/env python3
"""Goal 007 named-subunit evidence and event-window hydrology series."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
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
    normalise_retry_policy,
    rasterize_geometry,
    reset_retry_audit_log,
    retry_audit_summary,
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
QUALITY_PASS = {"quality_high", "quality_minimum"}


def configured_event_path() -> Path:
    raw = os.environ.get("NOMADIC_WATERBIRDS_EVENT_CONFIG")
    if not raw:
        return REPO / "settings" / "event_window_hydrology_007.json"
    path = Path(raw)
    return path if path.is_absolute() else REPO / path


CONFIG_PATH = configured_event_path()


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


def iter_months(start_month: str, end_month: str, rationale: str = "Goal 007 bounded event-window month") -> list[dict[str, str]]:
    start_year, start_mon = map(int, start_month.split("-"))
    end_year, end_mon = map(int, end_month.split("-"))
    current = dt.date(start_year, start_mon, 1)
    end = dt.date(end_year, end_mon, 1)
    months: list[dict[str, str]] = []
    while current <= end:
        months.append(
            {
                "month": f"{current.year:04d}-{current.month:02d}",
                "rationale": rationale,
            }
        )
        year = current.year + (current.month == 12)
        month = 1 if current.month == 12 else current.month + 1
        current = dt.date(year, month, 1)
    return months


def month_shift(month_name: str, offset: int) -> str:
    year, month = map(int, month_name.split("-"))
    index = year * 12 + (month - 1) + offset
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


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


def ensure_download(url: str, path: Path, seed_path: Path | None = None) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if seed_path is not None and seed_path.exists() and seed_path.stat().st_size > 0:
        shutil.copyfile(seed_path, path)
        return
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


def waterbody_support_id(candidate_id: str, uid: str) -> str:
    clean_uid = uid.replace("-", "_").replace(".", "_")
    return f"{candidate_id.lower()}_dea_waterbody_{clean_uid}"


def geometry_hash_wkb(geom: ogr.Geometry) -> str:
    return hashlib.sha256(geom.ExportToWkb()).hexdigest()


def feature_geometry_hash(feature: dict[str, Any]) -> str:
    payload = json.dumps(
        {"id": feature.get("id"), "geometry": feature.get("geometry"), "properties": feature.get("properties")},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def build_parent_supports(
    config: dict[str, Any], ramsar_subset: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    wgs84 = wgs84_srs()
    albers = epsg_srs(3577)
    features_by_refcode: dict[int, list[dict[str, Any]]] = {}
    for feature in ramsar_subset.get("features", []):
        features_by_refcode.setdefault(int(feature["properties"]["REFCODE"]), []).append(feature)
    parents: dict[str, dict[str, Any]] = {}
    for candidate in config["candidates"]:
        features = features_by_refcode.get(int(candidate["ramsar_refcode"]), [])
        if not features:
            continue
        geoms_wgs84 = [geometry_from_feature(feature) for feature in features]
        union_wgs84 = union_geometries(geoms_wgs84)
        union_albers = transform_geometry(union_wgs84, wgs84, albers)
        minx, maxx, miny, maxy = union_wgs84.GetEnvelope()
        objectids = ";".join(str(feature_objectid(feature)) for feature in sorted(features, key=feature_objectid))
        parents[candidate["candidate_id"]] = {
            "candidate": candidate,
            "features": features,
            "geom_wgs84": union_wgs84,
            "geom_albers": union_albers,
            "bbox_wgs84": (minx, maxx, miny, maxy),
            "area_m2": float(union_albers.GetArea()),
            "objectids": objectids,
            "geometry_hash_sha256": hashlib.sha256(
                json.dumps(
                    [
                        {
                            "id": feature.get("id"),
                            "geometry": feature.get("geometry", {}),
                            "properties": feature.get("properties", {}),
                        }
                        for feature in sorted(features, key=feature_objectid)
                    ],
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
        }
    return parents, features_by_refcode


def kmz_geometry(path: Path) -> ogr.Geometry:
    dataset = ogr.Open(str(path))
    if dataset is None:
        raise RuntimeError(f"could not open named geometry source {path}")
    albers = epsg_srs(3577)
    union: ogr.Geometry | None = None
    for layer_index in range(dataset.GetLayerCount()):
        layer = dataset.GetLayer(layer_index)
        source_srs = layer.GetSpatialRef()
        if source_srs is not None:
            source_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        for feature in layer:
            geom = feature.GetGeometryRef()
            if geom is None:
                continue
            clone = geom.Clone()
            if source_srs is not None:
                clone.Transform(osr.CoordinateTransformation(source_srs, albers))
            union = clone if union is None else union.Union(clone)
    if union is None:
        raise RuntimeError(f"named geometry source had no readable geometry: {path}")
    return union


def bbox_wgs84_from_albers(geom_albers: ogr.Geometry) -> tuple[float, float, float, float]:
    geom_wgs84 = transform_geometry(geom_albers, epsg_srs(3577), wgs84_srs())
    return geom_wgs84.GetEnvelope()


def waterbodies_layer(zip_path: Path) -> tuple[ogr.DataSource, ogr.Layer]:
    dataset = ogr.Open(f"/vsizip/{zip_path}/ga_ls_wb_3_v3.shp")
    if dataset is None:
        raise RuntimeError(f"could not open DEA Waterbodies shapefile from {zip_path}")
    return dataset, dataset.GetLayer(0)


def waterbody_overlap_lookup(zip_path: Path, geom_albers: ogr.Geometry, uid_filter: str | None = None) -> list[dict[str, Any]]:
    dataset, layer = waterbodies_layer(zip_path)
    _keepalive = dataset
    minx, maxx, miny, maxy = geom_albers.GetEnvelope()
    layer.SetSpatialFilterRect(minx, miny, maxx, maxy)
    overlaps: list[dict[str, Any]] = []
    for feature in layer:
        uid = feature.GetField("uid")
        if uid_filter and uid != uid_filter:
            continue
        geom = feature.GetGeometryRef()
        if geom is None or not geom.Intersects(geom_albers):
            continue
        intersection = geom.Intersection(geom_albers)
        if intersection is None or intersection.IsEmpty():
            continue
        overlap_area = float(intersection.GetArea())
        if overlap_area <= 0:
            continue
        waterbody_area = float(feature.GetField("area_m2") or geom.GetArea())
        overlaps.append(
            {
                "uid": uid,
                "timeseries": feature.GetField("timeseries"),
                "area_m2": waterbody_area,
                "overlap_area_m2": overlap_area,
                "overlap_fraction_of_support": overlap_area / geom_albers.GetArea() if geom_albers.GetArea() else None,
                "overlap_fraction_of_waterbody": overlap_area / waterbody_area if waterbody_area else None,
                "intersection_geom": intersection.Clone(),
                "geometry_hash_sha256": geometry_hash_wkb(intersection),
            }
        )
    layer.SetSpatialFilter(None)
    overlaps.sort(key=lambda item: (-item["overlap_area_m2"], item["uid"]))
    return overlaps


def blank_crosswalk_row(config: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": row.get("candidate_id", ""),
        "candidate_name": row.get("candidate_name", ""),
        "parent_support_id": row.get("parent_support_id", ""),
        "support_id": row.get("support_id", ""),
        "subunit_id": row.get("subunit_id", ""),
        "display_name": row.get("display_name", ""),
        "support_level": row.get("support_level", ""),
        "support_type": row.get("support_type", ""),
        "source": row.get("source", ""),
        "source_identifier": row.get("source_identifier", ""),
        "source_url": row.get("source_url", ""),
        "evidence_status": row.get("evidence_status", ""),
        "name_evidence": row.get("name_evidence", ""),
        "location_evidence": row.get("location_evidence", ""),
        "geometry_evidence": row.get("geometry_evidence", ""),
        "dea_uid_relationship": row.get("dea_uid_relationship", ""),
        "ramsar_component_relationship": row.get("ramsar_component_relationship", ""),
        "related_dea_waterbody_uid": row.get("related_dea_waterbody_uid", ""),
        "support_area_m2": row.get("support_area_m2", ""),
        "overlap_area_m2": row.get("overlap_area_m2", ""),
        "overlap_fraction_of_support": row.get("overlap_fraction_of_support", ""),
        "overlap_fraction_of_dea_waterbody": row.get("overlap_fraction_of_dea_waterbody", ""),
        "included_in_event_window": row.get("included_in_event_window", "no"),
        "inclusion_decision": row.get("inclusion_decision", ""),
        "event_window": f"{config['event_window']['start_month']}:{config['event_window']['end_month']}",
        "caveat": row.get("caveat", ""),
    }


def add_support(
    supports: list[dict[str, Any]],
    crosswalk_rows: list[dict[str, Any]],
    config: dict[str, Any],
    row: dict[str, Any],
    geom_albers: ogr.Geometry,
    geometry_hash: str,
) -> None:
    row = blank_crosswalk_row(config, row)
    row["included_in_event_window"] = "yes"
    row["inclusion_decision"] = row.get("inclusion_decision") or "included_for_event_window_hydrology"
    row["support_area_m2"] = row.get("support_area_m2") or float(geom_albers.GetArea())
    crosswalk_rows.append(row)
    supports.append(
        {
            **row,
            "geom_albers": geom_albers,
            "bbox_wgs84": bbox_wgs84_from_albers(geom_albers),
            "geometry_hash_sha256": geometry_hash,
        }
    )


def build_support_set(
    config: dict[str, Any],
    parents: dict[str, dict[str, Any]],
    features_by_refcode: dict[int, list[dict[str, Any]]],
    waterbodies_zip: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    albers = epsg_srs(3577)
    wgs84 = wgs84_srs()
    supports: list[dict[str, Any]] = []
    crosswalk_rows: list[dict[str, Any]] = []
    evidence_checks: list[dict[str, Any]] = []
    named_geometry_manifest: list[dict[str, Any]] = []

    for candidate in config["candidates"]:
        parent = parents[candidate["candidate_id"]]
        add_support(
            supports,
            crosswalk_rows,
            config,
            {
                "candidate_id": candidate["candidate_id"],
                "candidate_name": candidate["candidate_name"],
                "parent_support_id": candidate["parent_support_id"],
                "support_id": candidate["parent_support_id"],
                "display_name": candidate["candidate_name"],
                "support_level": "parent",
                "support_type": candidate["parent_support_type"],
                "source": "DCCEEW Geospatial Ramsar Wetlands service",
                "source_identifier": f"REFCODE={candidate['ramsar_refcode']};OBJECTID={parent['objectids']}",
                "source_url": config["ramsar_service_layer_url"],
                "evidence_status": "official_parent_ramsar_support",
                "name_evidence": "official Ramsar site name",
                "location_evidence": "official Ramsar polygon service",
                "geometry_evidence": "official Ramsar polygon union",
                "ramsar_component_relationship": "parent support",
                "caveat": candidate["parent_caveat"],
            },
            parent["geom_albers"],
            parent["geometry_hash_sha256"],
        )

    for candidate in config["candidates"]:
        selected_objectids = {int(value) for value in candidate.get("included_ramsar_objectids", [])}
        for feature in features_by_refcode.get(int(candidate["ramsar_refcode"]), []):
            objectid = feature_objectid(feature)
            if objectid not in selected_objectids:
                continue
            props = feature["properties"]
            geom = transform_geometry(geometry_from_feature(feature), wgs84, albers)
            support_id = ramsar_component_id(candidate["candidate_id"], objectid)
            add_support(
                supports,
                crosswalk_rows,
                config,
                {
                    "candidate_id": candidate["candidate_id"],
                    "candidate_name": candidate["candidate_name"],
                    "parent_support_id": candidate["parent_support_id"],
                    "support_id": support_id,
                    "subunit_id": support_id,
                    "display_name": props.get("WETLAND_NAME") or props.get("RAMSAR_NAME") or support_id,
                    "support_level": "subunit",
                    "support_type": "ramsar_component",
                    "source": "DCCEEW Geospatial Ramsar Wetlands service",
                    "source_identifier": f"REFCODE={props.get('REFCODE')};OBJECTID={objectid}",
                    "source_url": config["ramsar_service_layer_url"],
                    "evidence_status": "official_named_ramsar_component",
                    "name_evidence": "official Ramsar component wetland name",
                    "location_evidence": "official Ramsar component polygon",
                    "geometry_evidence": "official Ramsar component geometry",
                    "ramsar_component_relationship": f"OBJECTID={objectid}",
                    "caveat": candidate["subunit_caveat"],
                },
                geom,
                feature_geometry_hash(feature),
            )

    for candidate in config["candidates"]:
        parent = parents[candidate["candidate_id"]]
        for uid in candidate.get("included_waterbody_uids", []):
            overlap = waterbody_overlap_lookup(waterbodies_zip, parent["geom_albers"], uid_filter=uid)
            if not overlap:
                crosswalk_rows.append(
                    blank_crosswalk_row(
                        config,
                        {
                            "candidate_id": candidate["candidate_id"],
                            "candidate_name": candidate["candidate_name"],
                            "parent_support_id": candidate["parent_support_id"],
                            "support_id": waterbody_support_id(candidate["candidate_id"], uid),
                            "subunit_id": waterbody_support_id(candidate["candidate_id"], uid),
                            "display_name": f"DEA Waterbody {uid}",
                            "support_level": "subunit",
                            "support_type": "dea_waterbody_overlap",
                            "source": "DEA Waterbodies v3 shapefile",
                            "source_identifier": uid,
                            "source_url": config["dea_waterbodies_zip_url"],
                            "evidence_status": "blocked_no_parent_overlap",
                            "included_in_event_window": "no",
                            "inclusion_decision": "blocked_no_parent_overlap",
                            "caveat": f"No overlap found for configured DEA Waterbody UID {uid}.",
                        },
                    )
                )
                continue
            item = overlap[0]
            support_id = waterbody_support_id(candidate["candidate_id"], uid)
            add_support(
                supports,
                crosswalk_rows,
                config,
                {
                    "candidate_id": candidate["candidate_id"],
                    "candidate_name": candidate["candidate_name"],
                    "parent_support_id": candidate["parent_support_id"],
                    "support_id": support_id,
                    "subunit_id": support_id,
                    "display_name": f"DEA Waterbody {uid}",
                    "support_level": "subunit",
                    "support_type": "dea_waterbody_overlap",
                    "source": "DEA Waterbodies v3 shapefile",
                    "source_identifier": uid,
                    "source_url": config["dea_waterbodies_zip_url"],
                    "evidence_status": "open_water_screen_link_pending_named_geometry",
                    "name_evidence": "DEA Waterbody geohash UID only",
                    "location_evidence": "DEA Waterbodies polygon intersects parent Ramsar support",
                    "geometry_evidence": "DEA Waterbodies polygon clipped to parent Ramsar support",
                    "dea_uid_relationship": "support geometry is clipped from configured DEA Waterbody UID",
                    "related_dea_waterbody_uid": uid,
                    "overlap_area_m2": item["overlap_area_m2"],
                    "overlap_fraction_of_support": 1.0,
                    "overlap_fraction_of_dea_waterbody": item["overlap_fraction_of_waterbody"],
                    "caveat": candidate["subunit_caveat"],
                },
                item["intersection_geom"],
                item["geometry_hash_sha256"],
            )

    for source in config["named_geometry_sources"]:
        staged_path = REPO / source["staged_path"]
        ensure_download(source["download_url"], staged_path)
        size = staged_path.stat().st_size
        sha = sha256_file(staged_path)
        geom = kmz_geometry(staged_path)
        overlaps = waterbody_overlap_lookup(waterbodies_zip, geom)
        top = overlaps[0] if overlaps else {}
        expected = source.get("expected_related_dea_uid", "")
        expected_match = next((item for item in overlaps if item["uid"] == expected), None) if expected else None
        named_geometry_manifest.append(
            {
                "support_id": source["support_id"],
                "path": str(staged_path.relative_to(REPO)),
                "bytes": size,
                "sha256": sha,
                "area_m2": round(float(geom.GetArea()), 3),
                "source_url": source["source_url"],
                "download_url": source["download_url"],
                "top_dea_waterbody_uid": top.get("uid", ""),
                "top_overlap_area_m2": round(top.get("overlap_area_m2", 0.0), 3) if top else "",
                "expected_related_dea_uid": expected,
                "expected_uid_overlap_area_m2": round(expected_match["overlap_area_m2"], 3) if expected_match else "",
                "expected_uid_overlap_fraction_of_named_support": round(
                    expected_match["overlap_fraction_of_support"], 6
                )
                if expected_match
                else "",
                "expected_uid_overlap_fraction_of_dea_waterbody": round(
                    expected_match["overlap_fraction_of_waterbody"], 6
                )
                if expected_match
                else "",
                "committed": False,
            }
        )
        proves_uid = bool(expected_match)
        evidence_status = "official_named_geometry_linked_to_dea_waterbody" if proves_uid else "official_named_geometry"
        evidence_checks.append(
            {
                "support_id": source["support_id"],
                "display_name": source["display_name"],
                "source_url": source["source_url"],
                "proves_name": True,
                "proves_approx_location": True,
                "proves_geometry": True,
                "proves_dea_uid_relationship": proves_uid,
                "related_dea_waterbody_uid": expected if proves_uid else "",
                "evidence_status": evidence_status,
                "unresolved": ""
                if proves_uid
                else "No configured DEA Waterbody UID relationship was required or proved.",
            }
        )
        if proves_uid:
            for row in crosswalk_rows:
                if row.get("related_dea_waterbody_uid") == expected:
                    row["evidence_status"] = "open_water_screen_linked_to_diwa_named_geometry"
                    row["name_evidence"] = f"overlaps WetlandInfo DIWA named geometry for {source['display_name']}"
                    row["dea_uid_relationship"] = (
                        f"DEA UID {expected} overlaps {source['display_name']} by "
                        f"{expected_match['overlap_fraction_of_waterbody']:.3f} of the DEA polygon and "
                        f"{expected_match['overlap_fraction_of_support']:.3f} of the named support"
                    )
        if source["support_type"] == "wetlandinfo_ramsar_boundary_check":
            continue
        if not source.get("include_in_event_window", True):
            crosswalk_rows.append(
                blank_crosswalk_row(
                    config,
                    {
                        "candidate_id": source["candidate_id"],
                        "candidate_name": source["candidate_name"],
                        "parent_support_id": source["parent_support_id"],
                        "support_id": source["support_id"],
                        "subunit_id": source["support_id"],
                        "display_name": source["display_name"],
                        "support_level": "subunit",
                        "support_type": source["support_type"],
                        "source": "Queensland WetlandInfo DIWA facts and maps KMZ",
                        "source_identifier": Path(source["download_url"]).name,
                        "source_url": source["source_url"],
                        "evidence_status": evidence_status,
                        "name_evidence": "official Queensland WetlandInfo DIWA name",
                        "location_evidence": "WetlandInfo facts and maps location context",
                        "geometry_evidence": "WetlandInfo boundary KMZ geometry",
                        "dea_uid_relationship": f"overlaps configured DEA Waterbody {expected}" if proves_uid else "",
                        "related_dea_waterbody_uid": expected if proves_uid else "",
                        "overlap_area_m2": expected_match["overlap_area_m2"] if expected_match else "",
                        "overlap_fraction_of_support": expected_match["overlap_fraction_of_support"]
                        if expected_match
                        else "",
                        "overlap_fraction_of_dea_waterbody": expected_match["overlap_fraction_of_waterbody"]
                        if expected_match
                        else "",
                        "included_in_event_window": "no",
                        "inclusion_decision": "retained_as_named_evidence_not_in_fallback_event_window",
                        "caveat": source["caveat"],
                    },
                )
            )
            continue
        add_support(
            supports,
            crosswalk_rows,
            config,
            {
                "candidate_id": source["candidate_id"],
                "candidate_name": source["candidate_name"],
                "parent_support_id": source["parent_support_id"],
                "support_id": source["support_id"],
                "subunit_id": source["support_id"],
                "display_name": source["display_name"],
                "support_level": "subunit",
                "support_type": source["support_type"],
                "source": "Queensland WetlandInfo DIWA facts and maps KMZ",
                "source_identifier": Path(source["download_url"]).name,
                "source_url": source["source_url"],
                "evidence_status": evidence_status,
                "name_evidence": "official Queensland WetlandInfo DIWA name",
                "location_evidence": "WetlandInfo facts and maps location context",
                "geometry_evidence": "WetlandInfo boundary KMZ geometry",
                "dea_uid_relationship": f"overlaps configured DEA Waterbody {expected}" if proves_uid else "",
                "related_dea_waterbody_uid": expected if proves_uid else "",
                "overlap_area_m2": expected_match["overlap_area_m2"] if expected_match else "",
                "overlap_fraction_of_support": expected_match["overlap_fraction_of_support"] if expected_match else "",
                "overlap_fraction_of_dea_waterbody": expected_match["overlap_fraction_of_waterbody"]
                if expected_match
                else "",
                "caveat": source["caveat"],
            },
            geom,
            geometry_hash_wkb(geom),
        )

    for unresolved in config["unresolved_named_supports"]:
        crosswalk_rows.append(
            blank_crosswalk_row(
                config,
                {
                    **unresolved,
                    "subunit_id": unresolved["support_id"],
                    "support_level": "subunit",
                    "source": "DCCEEW Ramsar site page",
                    "name_evidence": "official page names the support feature within the Ramsar site",
                    "location_evidence": "within parent Ramsar site only",
                    "geometry_evidence": "not verified",
                    "dea_uid_relationship": "not verified",
                    "ramsar_component_relationship": "not exposed as separate Ramsar component geometry",
                    "included_in_event_window": "no",
                    "inclusion_decision": "retained_unresolved_no_event_window_hydrology",
                },
            )
        )
        evidence_checks.append(
            {
                "support_id": unresolved["support_id"],
                "display_name": unresolved["display_name"],
                "source_url": unresolved["source_url"],
                "proves_name": True,
                "proves_approx_location": True,
                "proves_geometry": False,
                "proves_dea_uid_relationship": False,
                "related_dea_waterbody_uid": "",
                "evidence_status": unresolved["evidence_status"],
                "unresolved": unresolved["caveat"],
            }
        )

    return supports, crosswalk_rows, evidence_checks, named_geometry_manifest


def to_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def wet_flag(value: Any) -> bool | None:
    if value in ("", None):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "yes", "1"}:
            return True
        if text in {"false", "no", "0"}:
            return False
    return None


def quality_passes(row: dict[str, Any]) -> bool:
    return row.get("quality_flag") in QUALITY_PASS


def count_unresolved_named_supports(rows: list[dict[str, Any]]) -> int:
    return sum(
        row.get("included_in_event_window") != "yes"
        and (
            "unresolved" in row.get("support_type", "")
            or "no_geometry" in row.get("evidence_status", "")
            or row.get("geometry_evidence") == "not verified"
        )
        for row in rows
    )


def add_time_history_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["support_id"], []).append(dict(row))
    enriched: list[dict[str, Any]] = []
    for support_id in sorted(grouped):
        support_rows = sorted(grouped[support_id], key=lambda row: row["month"])
        by_month = {row["month"]: row for row in support_rows}
        for row in support_rows:
            month = row["month"]
            current_prop = to_float(row.get("current_proportion_wet"))
            current_area = to_float(row.get("current_wet_area_m2"))
            lag1 = by_month.get(month_shift(month, -1))
            lag3 = by_month.get(month_shift(month, -3))
            lag1_prop = to_float(lag1.get("current_proportion_wet")) if lag1 else None
            lag1_area = to_float(lag1.get("current_wet_area_m2")) if lag1 else None
            lag3_prop = to_float(lag3.get("current_proportion_wet")) if lag3 else None
            lag3_area = to_float(lag3.get("current_wet_area_m2")) if lag3 else None
            trailing_values = []
            for offset in (-1, -2, -3):
                prior = by_month.get(month_shift(month, offset))
                if prior and quality_passes(prior):
                    value = to_float(prior.get("current_proportion_wet"))
                    if value is not None:
                        trailing_values.append(value)
            trailing3 = sum(trailing_values) / len(trailing_values) if trailing_values else None

            dry_prior = 0
            offset = -1
            while True:
                prior = by_month.get(month_shift(month, offset))
                if not prior or not quality_passes(prior) or wet_flag(prior.get("wet_month_flag")) is not False:
                    break
                dry_prior += 1
                offset -= 1

            current_wet = quality_passes(row) and wet_flag(row.get("wet_month_flag")) is True
            consecutive_wet = 0
            if current_wet:
                offset = 0
                while True:
                    prior = by_month.get(month_shift(month, offset))
                    if not prior or not quality_passes(prior) or wet_flag(prior.get("wet_month_flag")) is not True:
                        break
                    consecutive_wet += 1
                    offset -= 1

            cumulative_wet = 0
            for offset in range(-11, 1):
                prior = by_month.get(month_shift(month, offset))
                if prior and quality_passes(prior) and wet_flag(prior.get("wet_month_flag")) is True:
                    cumulative_wet += 1

            novel_after_dry = bool(current_wet and dry_prior >= 2)
            wetting_delta_1m = current_prop - lag1_prop if current_prop is not None and lag1_prop is not None else None
            wetting_delta_3m = current_prop - trailing3 if current_prop is not None and trailing3 is not None else None
            drying_velocity_1m = lag1_prop - current_prop if current_prop is not None and lag1_prop is not None else None
            drying_velocity_3m = trailing3 - current_prop if current_prop is not None and trailing3 is not None else None
            row.update(
                {
                    "wet_area_lag_1m": lag1_area,
                    "wet_prop_lag_1m": lag1_prop,
                    "wet_area_lag_3m": lag3_area,
                    "wet_prop_lag_3m": lag3_prop,
                    "wet_prop_trailing_3m": trailing3,
                    "wetting_delta_1m": wetting_delta_1m,
                    "wetting_delta_3m": wetting_delta_3m,
                    "novel_after_dry_flag": novel_after_dry,
                    "dry_spell_length_prior": dry_prior,
                    "cumulative_wet_months_12m": cumulative_wet,
                    "consecutive_wet_months": consecutive_wet,
                    "consecutive_dry_months_prior": dry_prior,
                    "drying_velocity_1m": drying_velocity_1m,
                    "drying_velocity_3m": drying_velocity_3m,
                }
            )
            enriched.append(row)
    return enriched


def base_metric_fields() -> list[str]:
    return [
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
    ]


def blocked_metric_values(quality_flag: str = "quality_fail") -> dict[str, Any]:
    values = {
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
        "quality_flag": quality_flag,
        "wet_month_flag": "",
    }
    values.update({field: "" for field in INVALID_BITS})
    return values


def process_event_window(
    config: dict[str, Any], supports: list[dict[str, Any]], months: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("AWS_NO_SIGN_REQUEST", "YES")
    gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    gdal.SetConfigOption("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
    albers = epsg_srs(3577)
    pixel_size = int(config["pixel_size_m"])
    max_grid_pixels = int(config["max_reference_grid_pixels"])
    rows: list[dict[str, Any]] = []
    support_manifest: list[dict[str, Any]] = []
    for index, support in enumerate(supports, start=1):
        print(f"processing support {index}/{len(supports)} {support['support_id']}", flush=True)
        record = {
            "candidate_id": support["candidate_id"],
            "support_id": support["support_id"],
            "support_type": support["support_type"],
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
            for month in months:
                row = event_base_row(config, support, month)
                row.update(
                    {
                        "access_method": "blocked before monthly Water Observations metrics",
                        "status": "blocked_support_grid",
                        "stac_items_found": 0,
                        "readable_scene_count": 0,
                        "skipped_scene_count": 0,
                        **blocked_metric_values(),
                        "failure_or_caveat": str(exc),
                    }
                )
                rows.append(row)
                record["months"].append({"month": month["month"], "status": "blocked_support_grid"})
            support_manifest.append(record)
            continue
        record["reference_grid"] = {
            "crs": config["reference_crs"],
            "pixel_size_m": pixel_size,
            "xsize": xsize,
            "ysize": ysize,
            "grid_pixels": xsize * ysize,
            "support_mask_pixels": int(support_mask.sum()),
            "bounds": [round(value, 3) for value in bounds],
        }
        for month in months:
            row = event_base_row(config, support, month)
            month_name = month["month"]
            scene_arrays: list[np.ndarray] = []
            skipped: list[dict[str, str]] = []
            try:
                stac = stac_search(config, support["bbox_wgs84"], month_name)
                features = sorted(
                    stac.get("features", []),
                    key=lambda feature: feature.get("properties", {}).get("datetime", ""),
                )
                readable_count = 0
                for feature in features:
                    href = feature.get("assets", {}).get("water", {}).get("href")
                    if not href:
                        skipped.append({"id": feature.get("id", ""), "reason": "missing water asset"})
                        continue
                    try:
                        scene_arrays.append(
                            warp_scene_to_grid(href, bounds, xsize, ysize, config["reference_crs"], config=config)
                        )
                        readable_count += 1
                    except Exception as exc:
                        skipped.append({"id": feature.get("id", ""), "reason": str(exc)})
                metrics = summarise_support_month(scene_arrays, support_mask)
                status = "computed_event_window_metrics" if scene_arrays else "blocked_no_readable_water_observations_scene"
                row.update(
                    {
                        "access_method": "support geometry plus DEA STAC and GDAL warp to EPSG:3577 support grid",
                        "status": status,
                        "stac_items_found": len(features),
                        "readable_scene_count": readable_count,
                        "skipped_scene_count": len(skipped),
                        **metrics,
                        "failure_or_caveat": support["caveat"]
                        if scene_arrays
                        else "No readable Water Observations scene could be warped for this support/month.",
                    }
                )
                record["months"].append(
                    {
                        "month": month_name,
                        "status": status,
                        "stac_items_found": len(features),
                        "readable_scene_count": readable_count,
                        "skipped_scene_count": len(skipped),
                    }
                )
            except Exception as exc:
                row.update(
                    {
                        "access_method": "blocked during monthly Water Observations processing",
                        "status": "blocked_event_window_processing_error",
                        "stac_items_found": 0,
                        "readable_scene_count": 0,
                        "skipped_scene_count": 0,
                        **blocked_metric_values(),
                        "failure_or_caveat": str(exc),
                    }
                )
                record["months"].append({"month": month_name, "status": row["status"], "caveat": str(exc)})
            rows.append(row)
        support_manifest.append(record)
    return add_time_history_metrics(rows), support_manifest


def event_base_row(config: dict[str, Any], support: dict[str, Any], month: dict[str, str]) -> dict[str, Any]:
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
        "month": month["month"],
        "month_rationale": month["rationale"],
        "source_geometry": support["source"],
        "source_identifier": support["source_identifier"],
        "source_geometry_caveat": support["caveat"],
        "support_area_m2": support["support_area_m2"],
        "geometry_hash_sha256": support["geometry_hash_sha256"],
        "dea_product": config["source_product"],
        "dea_product_version": config["source_product_version"],
        "metric_spec_version": config["metric_spec_version"],
    }


def event_series_fieldnames() -> list[str]:
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
        "stac_items_found",
        "readable_scene_count",
        "skipped_scene_count",
        *base_metric_fields(),
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
        "failure_or_caveat",
    ]


def crosswalk_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "candidate_name",
        "parent_support_id",
        "support_id",
        "subunit_id",
        "display_name",
        "support_level",
        "support_type",
        "source",
        "source_identifier",
        "source_url",
        "evidence_status",
        "name_evidence",
        "location_evidence",
        "geometry_evidence",
        "dea_uid_relationship",
        "ramsar_component_relationship",
        "related_dea_waterbody_uid",
        "support_area_m2",
        "overlap_area_m2",
        "overlap_fraction_of_support",
        "overlap_fraction_of_dea_waterbody",
        "included_in_event_window",
        "inclusion_decision",
        "event_window",
        "caveat",
    ]


def summary_rows(series_rows: list[dict[str, Any]], crosswalk_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    included_lookup = {row["support_id"]: row for row in crosswalk_rows if row["included_in_event_window"] == "yes"}
    rows: list[dict[str, Any]] = []
    for support_id in sorted(included_lookup):
        support_rows = [row for row in series_rows if row["support_id"] == support_id]
        quality_rows = [row for row in support_rows if quality_passes(row)]
        numeric_props = [
            (row["month"], to_float(row.get("current_proportion_wet")))
            for row in quality_rows
            if to_float(row.get("current_proportion_wet")) is not None
        ]
        max_month = ""
        max_prop: float | None = None
        if numeric_props:
            max_month, max_prop = max(numeric_props, key=lambda item: item[1])
        wet_months = [
            row["month"] for row in support_rows if quality_passes(row) and wet_flag(row.get("wet_month_flag")) is True
        ]
        mean_prop = (
            sum(value for _, value in numeric_props) / len(numeric_props)
            if numeric_props
            else None
        )
        crosswalk = included_lookup[support_id]
        rows.append(
            {
                "candidate_id": crosswalk["candidate_id"],
                "candidate_name": crosswalk["candidate_name"],
                "parent_support_id": crosswalk["parent_support_id"],
                "support_id": support_id,
                "display_name": crosswalk["display_name"],
                "support_level": crosswalk["support_level"],
                "support_type": crosswalk["support_type"],
                "evidence_status": crosswalk["evidence_status"],
                "months_expected": len(support_rows),
                "computed_month_count": sum(row["status"] == "computed_event_window_metrics" for row in support_rows),
                "blocked_or_missing_month_count": sum(row["status"] != "computed_event_window_metrics" for row in support_rows),
                "quality_high_count": sum(row["quality_flag"] == "quality_high" for row in support_rows),
                "quality_minimum_count": sum(row["quality_flag"] == "quality_minimum" for row in support_rows),
                "quality_fail_count": sum(row["quality_flag"] == "quality_fail" for row in support_rows),
                "wet_month_count": len(wet_months),
                "first_wet_month": wet_months[0] if wet_months else "",
                "last_wet_month": wet_months[-1] if wet_months else "",
                "max_current_proportion_wet": max_prop,
                "max_wet_month": max_month,
                "mean_current_proportion_wet_quality_months": mean_prop,
                "novel_after_dry_count": sum(wet_flag(row.get("novel_after_dry_flag")) is True for row in support_rows),
                "max_consecutive_wet_months": max(
                    (int(row.get("consecutive_wet_months") or 0) for row in support_rows),
                    default=0,
                ),
                "max_consecutive_dry_months_prior": max(
                    (int(row.get("consecutive_dry_months_prior") or 0) for row in support_rows),
                    default=0,
                ),
                "caveat": crosswalk["caveat"],
            }
        )
    return rows


def summary_fieldnames() -> list[str]:
    return [
        "candidate_id",
        "candidate_name",
        "parent_support_id",
        "support_id",
        "display_name",
        "support_level",
        "support_type",
        "evidence_status",
        "months_expected",
        "computed_month_count",
        "blocked_or_missing_month_count",
        "quality_high_count",
        "quality_minimum_count",
        "quality_fail_count",
        "wet_month_count",
        "first_wet_month",
        "last_wet_month",
        "max_current_proportion_wet",
        "max_wet_month",
        "mean_current_proportion_wet_quality_months",
        "novel_after_dry_count",
        "max_consecutive_wet_months",
        "max_consecutive_dry_months_prior",
        "caveat",
    ]


def run() -> int:
    start_time = time.time()
    config = load_json(CONFIG_PATH)
    reset_retry_audit_log()
    for relpath in config["scratch_paths"].values():
        (REPO / relpath).mkdir(parents=True, exist_ok=True)
    months = iter_months(
        config["event_window"]["start_month"],
        config["event_window"]["end_month"],
        config["event_window"].get("month_rationale", "Goal 007 bounded event-window month"),
    )

    ramsar_path = REPO / config["staged_files"]["ramsar_subset_geojson"]
    waterbodies_zip = REPO / config["staged_files"]["dea_waterbodies_zip"]
    ramsar_subset, ramsar_query_url = fetch_ramsar_subset(config)
    ramsar_path.parent.mkdir(parents=True, exist_ok=True)
    ramsar_path.write_bytes(json.dumps(ramsar_subset, indent=2).encode("utf-8"))
    seed = REPO / config["existing_waterbodies_zip_path"]
    ensure_download(config["dea_waterbodies_zip_url"], waterbodies_zip, seed_path=seed)

    parents, features_by_refcode = build_parent_supports(config, ramsar_subset)
    supports, crosswalk_rows, evidence_checks, named_geometry_manifest = build_support_set(
        config, parents, features_by_refcode, waterbodies_zip
    )
    outputs = {key: REPO / value for key, value in config["outputs"].items()}
    write_csv(outputs["named_crosswalk_csv"], crosswalk_rows, crosswalk_fieldnames())

    series_rows, support_manifest = process_event_window(config, supports, months)
    write_csv(outputs["event_series_csv"], series_rows, event_series_fieldnames())
    write_csv(outputs["event_summary_csv"], summary_rows(series_rows, crosswalk_rows), summary_fieldnames())

    now = dt.datetime.now(dt.UTC).isoformat()
    staged_raw_files = [
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
        *[
            {
                "path": item["path"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
                "committed": False,
            }
            for item in named_geometry_manifest
        ],
    ]
    named_manifest = {
        "goal": config["goal"],
        "manifest_type": "named_subunit_evidence",
        "accessed_at_utc": now,
        "command": config.get("run_command", "python3 scripts/event_window_hydrology_007.py"),
        "config_path": str(CONFIG_PATH.relative_to(REPO)),
        "source_urls": {
            "ramsar_service_layer": config["ramsar_service_layer_url"],
            "ramsar_service_query": ramsar_query_url,
            "dea_waterbodies_product": config["dea_waterbodies_product_url"],
            "dea_waterbodies_zip": config["dea_waterbodies_zip_url"],
            "narran_dcceew_page": config["unresolved_named_supports"][0]["source_url"],
            "currawinya_named_geometry_pages": [
                source["source_url"] for source in config["named_geometry_sources"]
            ],
        },
        "staged_raw_files": staged_raw_files,
        "named_geometry_sources": named_geometry_manifest,
        "source_checks": evidence_checks,
        "crosswalk_rows": len(crosswalk_rows),
        "included_support_count": sum(row["included_in_event_window"] == "yes" for row in crosswalk_rows),
        "unresolved_named_support_count": count_unresolved_named_supports(crosswalk_rows),
        "cleanup_status": "raw Ramsar subset, DEA Waterbodies ZIP, and WetlandInfo KMZ files left only in ignored staging paths; not committed",
        "outputs": {
            "crosswalk_csv": str(outputs["named_crosswalk_csv"].relative_to(REPO)),
            "manifest_json": str(outputs["named_manifest_json"].relative_to(REPO)),
        },
        "git_commit_at_run": quiet_git_commit(),
    }
    status_counts = {
        status: sum(row["status"] == status for row in series_rows)
        for status in sorted({row["status"] for row in series_rows})
    }
    hydrology_manifest = {
        "goal": config["goal"],
        "manifest_type": "event_window_hydrology_series",
        "metric_spec_version": config["metric_spec_version"],
        "started_at_utc": dt.datetime.fromtimestamp(start_time, tz=dt.UTC).isoformat(),
        "finished_at_utc": now,
        "elapsed_seconds": round(time.time() - start_time, 3),
        "command": config.get("run_command", "python3 scripts/event_window_hydrology_007.py"),
        "python_version": sys.version,
        "platform": platform.platform(),
        "gdal_version": gdal.VersionInfo("--version"),
        "numpy_version": np.__version__,
        "config_path": str(CONFIG_PATH.relative_to(REPO)),
        "event_window": config["event_window"],
        "months": [month["month"] for month in months],
        "retry_policy": normalise_retry_policy(config),
        "retry_audit_summary": retry_audit_summary(),
        "source_products": {
            "dea_stac_search": config["dea_stac_search_url"],
            "dea_collection": config["dea_collection"],
            "dea_water_observations_product": "https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/?tab=overview",
            "dea_waterbodies_product": config["dea_waterbodies_product_url"],
            "ramsar_service_layer": config["ramsar_service_layer_url"],
        },
        "scratch_paths": config["scratch_paths"],
        "staged_raw_files": staged_raw_files,
        "cleanup_status": named_manifest["cleanup_status"],
        "outputs": {
            "series_csv": str(outputs["event_series_csv"].relative_to(REPO)),
            "summary_csv": str(outputs["event_summary_csv"].relative_to(REPO)),
            "manifest_json": str(outputs["event_manifest_json"].relative_to(REPO)),
        },
        "support_count": len(supports),
        "row_count": len(series_rows),
        "status_counts": status_counts,
        "derived_metrics": [
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
        ],
        "supports": support_manifest,
        "git_commit_at_run": quiet_git_commit(),
    }
    write_json(outputs["named_manifest_json"], named_manifest)
    write_json(outputs["event_manifest_json"], hydrology_manifest)
    print(f"wrote {outputs['named_crosswalk_csv'].relative_to(REPO)}")
    print(f"wrote {outputs['named_manifest_json'].relative_to(REPO)}")
    print(f"wrote {outputs['event_series_csv'].relative_to(REPO)}")
    print(f"wrote {outputs['event_summary_csv'].relative_to(REPO)}")
    print(f"wrote {outputs['event_manifest_json'].relative_to(REPO)}")
    print(
        json.dumps(
            {
                "supports": len(supports),
                "months": len(months),
                "event_rows": len(series_rows),
                "status_counts": status_counts,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
