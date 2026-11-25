#!/usr/bin/env python3
"""Visual + object audits for Sinnoh outdoor maps.

Checks:
- Incomplete Emerald 2x2 trees (orphan halves at any alignment)
- Isolated cliff/rock tiles not in a contiguous rock cluster
- Oversized path blobs vs Platinum path attrs
- Passable water (wrong elev/collision — must be elev=1, coll=0 for Surf)
- Fence inventions / stray ledges (legacy)
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    MT_ROCK,
    MT_SAND,
    MT_TREE_BL,
    MT_TREE_BR,
    MT_TREE_TL,
    MT_TREE_TR,
    MT_WATER,
    PATH_METATILES,
    PLAT_DATA,
    PLAT_SNOW_PATH_BEHAVIORS,
    WATER_METATILES,
    is_plat_path_behavior,
    load_attrs,
    map_allows_path_fallback,
    plat_behavior,
    plat_collision,
)

LAYOUTS = REPO / "data" / "layouts"
MAPS = REPO / "data" / "maps"
LAYOUTS_JSON = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((LAYOUTS / "layouts.json").read_text())["layouts"]
}
# Emerald General 2x2 tree family: dense quad plus the vanilla edge variants
# (open side / open below / water above) that Emerald routes use at forest edges.
TREE_TL = {MT_TREE_TL, 0x1D6, 0x1FC}
TREE_TR = {MT_TREE_TR, 0x1D7, 0x1FD}
TREE_BL = {MT_TREE_BL, 0x1DE, 0x1E4, 0x1E6}
TREE_BR = {MT_TREE_BR, 0x1DF, 0x1E5, 0x1E7}
# Only the dense quad ids are audited as "tree tiles" (unchanged coverage);
# a quad counts as complete when its corners are any member of the family.
TREE = {MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR}
TREE_EXPECT = {
    MT_TREE_TL: (0, 0),
    MT_TREE_TR: (-1, 0),
    MT_TREE_BL: (0, -1),
    MT_TREE_BR: (-1, -1),
}
COMPLETE = [MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR]
LEDGE = {0x0D5, 0x0D6}
FENCE_LIKE = {0x00A, 0x00B, 0x00C}
CLIFF_ROCK = {MT_ROCK, 0x07C, 0x091, 0x139}


def load_cells(name: str):
    meta = LAYOUTS_JSON[name]
    w, h = int(meta["width"]), int(meta["height"])
    data = (REPO / meta["blockdata_filepath"]).read_bytes()
    cells = []
    for y in range(h):
        row = []
        for x in range(w):
            raw = struct.unpack_from("<H", data, (y * w + x) * 2)[0]
            row.append((raw & 0x3FF, (raw >> 10) & 3, (raw >> 12) & 0xF))
        cells.append(row)
    return cells, w, h, meta


def incomplete_trees(cells) -> int:
    """Count tree tiles that are not part of a correct TL/TR/BL/BR quad."""
    h, w = len(cells), len(cells[0])

    def is_complete(tlx, tly) -> bool:
        if tlx < 0 or tly < 0 or tlx + 1 >= w or tly + 1 >= h:
            return False
        return (
            cells[tly][tlx][0] in TREE_TL
            and cells[tly][tlx + 1][0] in TREE_TR
            and cells[tly + 1][tlx][0] in TREE_BL
            and cells[tly + 1][tlx + 1][0] in TREE_BR
        )

    bad = 0
    for y in range(h):
        for x in range(w):
            mt = cells[y][x][0]
            if mt not in TREE:
                continue
            dx, dy = TREE_EXPECT[mt]
            if not is_complete(x + dx, y + dy):
                bad += 1
    return bad


def building_stamp_cells(cells) -> set[tuple[int, int]]:
    """Cells covered by an exact Emerald building stamp (General house roofs and
    walls reuse 0x00A-0x00C, which are not fences there)."""
    from tools.sinnoh_maps.emerald_building_stamps import ALL_STAMPS

    h, w = len(cells), len(cells[0])
    covered: set[tuple[int, int]] = set()
    for st in ALL_STAMPS:
        t = st["tiles"]
        th, tw = len(t), len(t[0])
        for y in range(h - th + 1):
            for x in range(w - tw + 1):
                if cells[y][x][0] != t[0][0]:
                    continue
                if all(cells[y + a][x + b][0] == t[a][b] for a in range(th) for b in range(tw)):
                    covered.update((x + b, y + a) for a in range(th) for b in range(tw))
    return covered


def isolated_rocks(cells) -> int:
    """Rock/cliff tiles with <2 rock/cliff neighbors (4-connected) → isolated."""
    h, w = len(cells), len(cells[0])
    isolated = 0
    for y in range(h):
        for x in range(w):
            if cells[y][x][0] not in CLIFF_ROCK:
                continue
            n = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and cells[ny][nx][0] in CLIFF_ROCK:
                    n += 1
            if n < 2:
                isolated += 1
    return isolated


def passable_water(cells) -> int:
    """Water that is walkable: wrong elev (must be 1) or collision set."""
    bad = 0
    for row in cells:
        for mt, coll, elev in row:
            if mt not in WATER_METATILES:
                continue
            # Vanilla Emerald: coll=0, elev=1 → elevation mismatch vs player elev 3
            if coll != 0 or elev != 1:
                bad += 1
    return bad


def plat_ledge_count(chunks) -> int:
    n = 0
    for row in chunks:
        for lid in row:
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for v in attrs:
                if plat_behavior(v) == 0x3B:
                    n += 1
    return n


def plat_path_count(chunks, *, snow: bool = False) -> int:
    n = 0
    for row in chunks:
        for lid in row:
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for v in attrs:
                if plat_collision(v):
                    continue
                beh = plat_behavior(v)
                if is_plat_path_behavior(beh) or (snow and beh in PLAT_SNOW_PATH_BEHAVIORS):
                    n += 1
    return n


def is_snow_layout(meta: dict, name: str) -> bool:
    sec = meta.get("secondary_tileset") or ""
    if "Fallarbor" in sec:
        return True
    return name in {
        "SnowpointCity", "Route216", "Route217", "AcuityLakefront", "LakeAcuity",
    }


def audit_one(name: str) -> dict:
    if name not in LAYOUTS_JSON:
        return {"name": name, "status": "SKIP"}
    cells, w, h, meta = load_cells(name)
    incomplete = incomplete_trees(cells)
    isolated = isolated_rocks(cells)
    bad_water = passable_water(cells)
    em_ledges = sum(1 for row in cells for mt, _, _ in row if mt in LEDGE)
    in_stamp = building_stamp_cells(cells)
    em_fences = sum(
        1 for y, row in enumerate(cells) for x, (mt, _, _) in enumerate(row)
        if mt in FENCE_LIKE and (x, y) not in in_stamp
    )
    snow = is_snow_layout(meta, name)
    em_paths = sum(1 for row in cells for mt, _, _ in row if mt in PATH_METATILES)
    em_sand = sum(1 for row in cells for mt, _, _ in row if mt == MT_SAND)
    em_water = sum(1 for row in cells for mt, _, _ in row if mt in WATER_METATILES)

    plat_ledges = 0
    plat_paths = 0
    stray_ledges = 0
    chunks = LAND_TABLE.get(name)
    if chunks and PLAT_DATA.exists():
        try:
            plat_ledges = plat_ledge_count(chunks)
            plat_paths = plat_path_count(chunks, snow=snow)
        except FileNotFoundError:
            plat_ledges = -1
            plat_paths = -1
        if plat_ledges >= 0 and em_ledges > plat_ledges + 16:
            stray_ledges = em_ledges - plat_ledges

    signs = 0
    mj = MAPS / name / "map.json"
    warps = []
    if mj.exists():
        data = json.loads(mj.read_text())
        for bg in data.get("bg_events") or []:
            if bg.get("type") == "sign":
                signs += 1
        warps = data.get("warp_events") or []

    issues = []
    status = "PASS"

    # Paved-city grass dominance + trees-inside-buildings (city visual checks)
    from tools.sinnoh_maps.city_door_warp_audit import (  # local import avoids cycle at load
        PAVED_CITIES,
        TREE as _TREE,
        CLIFF_ROCK as _CLIFF,
        grass_dominant,
        trees_in_building,
        classify_warp,
    )

    if name in PAVED_CITIES:
        heavy, gfrac, pfrac = grass_dominant(cells, w, h)
        if heavy:
            issues.append(
                f"grass-dominant paved city: grass={gfrac:.0%} pave={pfrac:.0%}"
            )
            status = "FAIL"
        bad_bldg = 0
        for warp in warps:
            kind = classify_warp(warp.get("dest_map") or "")
            if kind in ("center", "mart", "gym", "building"):
                bad_bldg += trees_in_building(cells, int(warp["x"]), int(warp["y"]))
        if bad_bldg:
            issues.append(f"trees/cliffs inside building facades: {bad_bldg}")
            status = "FAIL"
    if incomplete > 0:
        issues.append(f"incomplete 2x2 trees: {incomplete}")
        status = "FAIL"
    # Flag sparse rock leftovers. Twinleaf must be cliff-free (Chris playtest).
    # Other maps WARN — converting rocks to grass opens Platinum solids.
    if isolated > 0:
        issues.append(f"isolated cliff/rock tiles: {isolated}")
        if name == "TwinleafTown":
            status = "FAIL"
        elif status == "PASS":
            status = "WARN"
    if bad_water > 0:
        issues.append(f"passable/wrong-pack water cells: {bad_water}")
        status = "FAIL"
    if em_fences:
        issues.append(f"fence metatiles with no Platinum fence mapping: {em_fences}")
        status = "FAIL"
    if stray_ledges > 32:
        issues.append(f"extra ledge metatiles vs Platinum: +{stray_ledges}")
        if status == "PASS":
            status = "WARN"

    path_coverage = None
    outdoor = "Building" not in (meta.get("primary_tileset") or "") and "Cave" not in (
        meta.get("secondary_tileset") or ""
    )
    if plat_paths and plat_paths > 0:
        covered = (em_sand + em_paths) if snow else em_paths
        path_coverage = covered / plat_paths
        # Require at least 25% coverage, but don't demand a flat 8 tiles when
        # Platinum only has a handful of walkway cells (e.g. Celestic=1).
        min_required = max(1, min(8, plat_paths // 4)) if plat_paths >= 8 else max(1, plat_paths)
        if covered < min_required:
            issues.append(
                f"missing paths: Platinum {plat_paths} path cells → Emerald "
                f"path/sand {covered} ({path_coverage:.0%})"
            )
            status = "FAIL"
        # Oversized path blob: Emerald paths >> Platinum (town sand rectangles etc.)
        # Paved Platinum cities intentionally use sidewalk/path for most walkables.
        if not snow and covered > max(plat_paths * 3, plat_paths + 48):
            issues.append(
                f"oversized paths: Emerald {covered} vs Platinum {plat_paths} "
                f"({path_coverage:.1f}x)"
            )
            if name in PAVED_CITIES:
                if status == "PASS":
                    status = "WARN"
            elif covered > max(plat_paths * 5, plat_paths + 120):
                status = "FAIL"
            elif status == "PASS":
                status = "WARN"
    elif (
        outdoor
        and not snow
        and chunks
        and PLAT_DATA.exists()
        and plat_paths == 0
        and map_allows_path_fallback(name)
    ):
        plain = 0
        try:
            for row in chunks:
                for lid in row:
                    if lid is None:
                        continue
                    for v in load_attrs(lid):
                        if plat_collision(v):
                            continue
                        if plat_behavior(v) == 0:
                            plain += 1
        except FileNotFoundError:
            plain = 0
        if plain >= 40 and em_paths < max(8, plain // 8):
            issues.append(
                f"missing paths: Platinum plain-ground fallback {plain} cells → "
                f"Emerald path {em_paths}"
            )
            status = "FAIL"

    return {
        "name": name,
        "status": status,
        "incomplete_trees": incomplete,
        "isolated_rocks": isolated,
        "passable_water": bad_water,
        "em_water": em_water,
        "em_ledges": em_ledges,
        "plat_ledges": plat_ledges,
        "em_fences": em_fences,
        "em_paths": em_paths,
        "em_sand": em_sand,
        "plat_paths": plat_paths,
        "path_coverage": None if path_coverage is None else round(path_coverage, 3),
        "signs": signs,
        "issues": issues,
    }


def main() -> int:
    results = [audit_one(n) for n in sorted(LAND_TABLE)]
    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    out = REPO / "tools/sinnoh_maps/visual_object_audit_report.json"
    out.write_text(
        json.dumps(
            {
                "results": results,
                "fail": len(fails),
                "warn": len(warns),
                "pass": sum(1 for r in results if r["status"] == "PASS"),
            },
            indent=2,
        )
        + "\n"
    )
    for r in results:
        if r["status"] != "PASS":
            print(f"{r['status']:4s} {r['name']}: {'; '.join(r['issues'])}")
    print(
        f"=== visual/object audit: {len(fails)} FAIL / {len(warns)} WARN / "
        f"{len(results)} → {out} ==="
    )
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
