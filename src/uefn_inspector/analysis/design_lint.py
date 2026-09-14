"""Design lint — measurable "is this level designed or just boxed?" checks.

Runs on the offline level inventory (no editor) and answers, per check,
ok / fail / unverified with the measured value, the threshold and evidence.
It is meant to run MID-loop (after the skeleton ticket and after the visual
ticket), not only at review time, so a session cannot drift into a flat plane
of untextured primitives without noticing.

Thresholds are defaults for a first pass; a game fixes its own in
`spec/GDD.md §0` and passes them as `profile`.
"""
from __future__ import annotations

import math
from collections import Counter

from ..level import Level, PlacedActor

DEFAULT_PROFILE: dict = {
    "graybox_share_max": 0.20,      # GrayBox_* / S_Cube / WorldGridMaterial actors
    "mesh_variety_min": 8,          # distinct mesh assets referenced
    "material_variety_min": 6,      # distinct material assets referenced
    "gallery_sources_min": 1,       # asset folders outside the greybox/device cubes
    "dominant_mesh_share_max": 0.50,
    "z_bands_min": 2,               # distinct height bands (band = z_band_cm)
    "z_band_cm": 200.0,
    "z_range_min_cm": 300.0,
    "flat_prop_share_max": 0.30,    # scale with one axis <= flat_ratio * largest axis
    "flat_ratio": 0.10,
    "off_grid_rotation_share_min": 0.10,   # yaw not a multiple of 90
    "occupancy_min": 0.15,          # occupied / bounding cells (cell = occupancy_cell_cm)
    "occupancy_max": 0.75,
    "occupancy_cell_cm": 500.0,
    "required_class_substrings": ["Spawn"],
    "light_class_substrings": ["Light"],
}

_GREYBOX_MARKERS = ("GrayBox_", "/S_Cube", "WorldGridMaterial", "M_Basic_Wall", "M_Basic_Floor")
_MESH_PREFIXES = ("SM_", "S_", "SK_")
_MAT_PREFIXES = ("M_", "MI_", "MF_", "MM_")


def _leaf(ref: str) -> str:
    return ref.rsplit("/", 1)[-1]


def _is_mesh(ref: str) -> bool:
    return "/Meshes/" in ref or _leaf(ref).startswith(_MESH_PREFIXES)


def _is_material(ref: str) -> bool:
    return "/Materials/" in ref or _leaf(ref).startswith(_MAT_PREFIXES)


def _is_greybox(a: PlacedActor) -> bool:
    if a.device_class.startswith("GrayBox_"):
        return True
    return any(m in r for r in a.asset_refs for m in _GREYBOX_MARKERS[1:])


def _source_folder(ref: str) -> str:
    parts = [p for p in ref.split("/") if p]
    return "/" + "/".join(parts[:3])


def _check(cid, title, status, value, threshold, evidence=""):
    return {"id": cid, "title": title, "status": status, "value": value,
            "threshold": threshold, "evidence": evidence}


def design_lint(level: Level, profile: dict | None = None) -> dict:
    P = {**DEFAULT_PROFILE, **(profile or {})}
    actors = level.actors
    n = len(actors)
    checks: list[dict] = []
    if n == 0:
        return {"level": level.name, "actors": 0, "checks": [], "fail": [], "unverified": [],
                "summary": "no actors"}

    # ---- assets: are we pulling anything in, or boxing? ----------------------
    grey = [a for a in actors if _is_greybox(a)]
    share = len(grey) / n
    checks.append(_check("graybox_share", "그레이박스 비율", "ok" if share <= P["graybox_share_max"] else "fail",
                         round(share, 2), f"<= {P['graybox_share_max']}",
                         f"{len(grey)}/{n} actors are GrayBox_/S_Cube/basic-material"))

    meshes = Counter(); mats = set(); mesh_actors = 0
    for a in actors:
        ms = {r for r in a.asset_refs if _is_mesh(r)}
        mats |= {r for r in a.asset_refs if _is_material(r)}
        if ms:
            mesh_actors += 1
        for m in ms:
            meshes[m] += 1
    checks.append(_check("mesh_variety", "고유 메시 수", "ok" if len(meshes) >= P["mesh_variety_min"] else "fail",
                         len(meshes), f">= {P['mesh_variety_min']}", ", ".join(sorted(map(_leaf, meshes))[:8])))
    checks.append(_check("material_variety", "고유 머티리얼 수", "ok" if len(mats) >= P["material_variety_min"] else "fail",
                         len(mats), f">= {P['material_variety_min']}", ", ".join(sorted(map(_leaf, mats))[:8])))
    sources = {_source_folder(m) for m in meshes if not any(k in m for k in _GREYBOX_MARKERS)}
    checks.append(_check("gallery_sources", "불러다 쓴 자산 출처(폴더) 수",
                         "ok" if len(sources) >= P["gallery_sources_min"] else "fail",
                         len(sources), f">= {P['gallery_sources_min']}", ", ".join(sorted(sources))))
    if meshes:
        top, cnt = meshes.most_common(1)[0]
        dom = cnt / mesh_actors
        checks.append(_check("dominant_mesh", "한 메시의 점유율", "ok" if dom <= P["dominant_mesh_share_max"] else "fail",
                             round(dom, 2), f"<= {P['dominant_mesh_share_max']}", f"{_leaf(top)} x{cnt}"))
    else:
        checks.append(_check("dominant_mesh", "한 메시의 점유율", "unverified", None, "", "no mesh refs decoded"))

    # ---- space: flat plane or a place? --------------------------------------
    locs = [a.location for a in actors if a.location]
    if locs:
        zs = [l[2] for l in locs]
        bands = {math.floor(z / P["z_band_cm"]) for z in zs}
        zr = max(zs) - min(zs)
        ok = len(bands) >= P["z_bands_min"] and zr >= P["z_range_min_cm"]
        checks.append(_check("verticality", "높이 층 수 / z 범위", "ok" if ok else "fail",
                             {"bands": len(bands), "z_range": round(zr)},
                             f"bands >= {P['z_bands_min']}, z_range >= {P['z_range_min_cm']}",
                             "all actors on one height band = flat plane" if len(bands) < 2 else ""))
        cell = P["occupancy_cell_cm"]
        xs, ys = [l[0] for l in locs], [l[1] for l in locs]
        occupied = {(math.floor(x / cell), math.floor(y / cell)) for x, y in zip(xs, ys)}
        cols = math.floor(max(xs) / cell) - math.floor(min(xs) / cell) + 1
        rows = math.floor(max(ys) / cell) - math.floor(min(ys) / cell) + 1
        occ = len(occupied) / (cols * rows)
        ok = P["occupancy_min"] <= occ <= P["occupancy_max"]
        checks.append(_check("occupancy", "공간 점유율(셀 기준)", "ok" if ok else "fail", round(occ, 2),
                             f"{P['occupancy_min']} .. {P['occupancy_max']}",
                             f"{len(occupied)} of {cols * rows} cells ({cell:g} cm)"
                             + (" — too sparse" if occ < P["occupancy_min"] else " — crammed" if occ > P["occupancy_max"] else "")))
    else:
        checks.append(_check("verticality", "높이 층 수 / z 범위", "unverified", None, "", "no locations decoded"))
        checks.append(_check("occupancy", "공간 점유율(셀 기준)", "unverified", None, "", "no locations decoded"))

    scaled = [a.scale for a in actors if a.scale]
    if scaled:
        flat = [s for s in scaled if min(map(abs, s)) <= P["flat_ratio"] * max(map(abs, s))]
        fs = len(flat) / len(scaled)
        checks.append(_check("flat_props", "판(한 축이 납작한 스케일) 비율", "ok" if fs <= P["flat_prop_share_max"] else "fail",
                             round(fs, 2), f"<= {P['flat_prop_share_max']}", f"{len(flat)}/{len(scaled)} scaled actors"))
    else:
        checks.append(_check("flat_props", "판(한 축이 납작한 스케일) 비율", "unverified", None, "", "no RelativeScale3D decoded"))

    rots = [a.rotation for a in actors if a.rotation]
    if rots:
        off = [r for r in rots if abs((r[2] % 90.0 + 90.0) % 90.0) > 1.0]
        os_ = len(off) / len(rots)
        checks.append(_check("rotation_variety", "축에서 벗어난 회전(yaw) 비율", "ok" if os_ >= P["off_grid_rotation_share_min"] else "fail",
                             round(os_, 2), f">= {P['off_grid_rotation_share_min']}",
                             "everything axis-aligned reads as a grid of boxes" if os_ == 0 else ""))
    else:
        checks.append(_check("rotation_variety", "축에서 벗어난 회전(yaw) 비율", "unverified", None, "", "no RelativeRotation decoded"))

    # ---- function & light ----------------------------------------------------
    classes = [a.device_class for a in actors]
    missing = [s for s in P["required_class_substrings"] if not any(s in c for c in classes)]
    checks.append(_check("function_elements", "필수 기능 요소 존재", "ok" if not missing else "fail",
                         [s for s in P["required_class_substrings"] if s not in missing],
                         f"all of {P['required_class_substrings']}", f"missing: {missing}" if missing else ""))
    lights = [c for c in classes if any(s in c for s in P["light_class_substrings"])]
    checks.append(_check("lighting", "광원 액터 수", "ok" if lights else "fail", len(lights), ">= 1",
                         ", ".join(sorted(set(lights))[:4])))

    fail = [c["id"] for c in checks if c["status"] == "fail"]
    unv = [c["id"] for c in checks if c["status"] == "unverified"]
    okn = sum(c["status"] == "ok" for c in checks)
    return {"level": level.name, "actors": n, "checks": checks, "fail": fail, "unverified": unv,
            "profile": P, "summary": f"{okn}/{len(checks)} ok, {len(fail)} fail, {len(unv)} unverified"}
