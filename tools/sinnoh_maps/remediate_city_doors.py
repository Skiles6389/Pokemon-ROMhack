#!/usr/bin/env python3
"""Stamp Emerald PC/Mart/house/civic facades on outdoor settlement warps.

Also converts grass-dominant paved cities to sidewalk/path pavement.
Dedupes adjacent double-door warps (PC often has two cells) so the primary
door metatile lands on the leftmost warp.

Run after rebuild_jubilife_city.py. Idempotent.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.city_door_warp_audit import (  # noqa: E402
    CLIFF_ROCK,
    DOOR_METATILES,
    PAVED_CITIES,
    TREE,
    classify_warp,
    expected_door,
)
from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    MT_GRASS,
    MT_PATH_C,
    MT_ROCK,
    MT_TALL,
    WATER_METATILES,
    pack,
)

LAYOUTS = REPO / "data" / "layouts"
MAPS = REPO / "data" / "maps"
LAYOUTS_JSON = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((LAYOUTS / "layouts.json").read_text())["layouts"]
}

MT_CITY_PAVE = 0x2BB

PC_GENERAL = [
    [0x048, 0x049, 0x04A, 0x04B],
    [0x050, 0x051, 0x052, 0x053],
    [0x058, 0x059, 0x05A, 0x05B],
    [0x060, 0x061, 0x062, 0x063],
]
PC_RUSTBORO = [
    [0x256, 0x25E, 0x25F, 0x257],
    [0x050, 0x051, 0x052, 0x053],
    [0x058, 0x059, 0x05A, 0x05B],
    [0x266, 0x061, 0x062, 0x27E],
]
MART_GENERAL = [
    [0x030, 0x031, 0x032, 0x033],
    [0x038, 0x039, 0x03A, 0x03B],
    [0x060, 0x041, 0x042, 0x043],
]
MART_RUSTBORO = [
    [0x030, 0x031, 0x032, 0x033],
    [0x038, 0x039, 0x03A, 0x03B],
    [0x266, 0x041, 0x042, 0x27F],
]
HOUSE_PETALBURG = [
    [0x210, 0x211, 0x211, 0x211, 0x212],
    [0x218, 0x219, 0x219, 0x219, 0x21A],
    [0x222, 0x232, 0x230, 0x240, 0x221],
    [0x22A, 0x23A, 0x238, 0x248, 0x229],
]
HOUSE_RUSTBORO = [
    [0x220, 0x221, 0x221, 0x221, 0x222],
    [0x228, 0x229, 0x229, 0x229, 0x22A],
    [0x230, 0x231, 0x231, 0x227, 0x233],
    [0x238, 0x23A, 0x23A, 0x23A, 0x23B],
    [0x240, 0x241, 0x241, 0x22F, 0x243],
]
GYM_FACADE = [
    [0x210, 0x211, 0x211, 0x211, 0x212],
    [0x218, 0x219, 0x219, 0x219, 0x21A],
    [0x222, 0x232, 0x230, 0x240, 0x221],
    [0x22A, 0x23A, 0x1CD, 0x248, 0x229],
]
CAVE_MOUTH = [
    [0x09F],
    [0x0A7],
]


def load_grid(name: str):
    meta = LAYOUTS_JSON[name]
    w, h = int(meta["width"]), int(meta["height"])
    path = REPO / meta["blockdata_filepath"]
    data = path.read_bytes()
    grid = [[0] * w for _ in range(h)]
    coll = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            raw = struct.unpack_from("<H", data, (y * w + x) * 2)[0]
            grid[y][x] = raw & 0x3FF
            coll[y][x] = (raw >> 10) & 3
    return grid, coll, w, h, meta, path


def door_dx_for(facade, door_mt: int) -> int:
    return next(i for i, mt in enumerate(facade[-1]) if mt == door_mt)


def stamp(grid, door_x, door_y, facade, door_mt: int) -> None:
    door_dx = door_dx_for(facade, door_mt)
    top = door_y - (len(facade) - 1)
    left = door_x - door_dx
    h, w = len(grid), len(grid[0])
    for dy, row in enumerate(facade):
        for dx, mt in enumerate(row):
            x, y = left + dx, top + dy
            if 0 <= y < h and 0 <= x < w:
                grid[y][x] = mt


def clear_footprint(grid, coll, door_x, door_y, facade, door_mt, fill: int) -> None:
    door_dx = door_dx_for(facade, door_mt)
    top = door_y - (len(facade) - 1) - 1
    left = door_x - door_dx - 1
    h, w = len(grid), len(grid[0])
    for dy in range(len(facade) + 3):
        for dx in range(len(facade[0]) + 2):
            x, y = left + dx, top + dy
            if 0 <= y < h and 0 <= x < w:
                mt = grid[y][x]
                if mt in TREE | CLIFF_ROCK | {MT_GRASS, MT_TALL, MT_ROCK, 0x139}:
                    grid[y][x] = fill
                    coll[y][x] = 0
                elif mt < 0x028 and mt not in WATER_METATILES:
                    grid[y][x] = fill
                    coll[y][x] = 0


def pave_city(grid, coll, meta) -> int:
    sec = meta.get("secondary_tileset") or ""
    fill = MT_CITY_PAVE if "Rustboro" in sec else MT_PATH_C
    n = 0
    h, w = len(grid), len(grid[0])
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt in (MT_GRASS, MT_TALL):
                grid[y][x] = fill
                coll[y][x] = 0
                n += 1
            elif mt in CLIFF_ROCK and x > 1 and y > 1 and x < w - 2 and y < h - 2:
                if not _near_building(grid, x, y):
                    grid[y][x] = fill
                    coll[y][x] = 0
                    n += 1
    return n


def _near_building(grid, x, y) -> bool:
    h, w = len(grid), len(grid[0])
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                mt = grid[ny][nx]
                if mt >= 0x200 or mt in DOOR_METATILES | {0x050, 0x051, 0x058, 0x061, 0x041, 0x048}:
                    return True
    return False


def sync_collision(grid, coll) -> None:
    h, w = len(grid), len(grid[0])
    solid_general = {
        0x048, 0x049, 0x04A, 0x04B, 0x050, 0x051, 0x052, 0x053,
        0x058, 0x059, 0x05A, 0x05B, 0x060, 0x062, 0x063, 0x061,
        0x030, 0x031, 0x032, 0x033, 0x038, 0x039, 0x03A, 0x03B,
        0x041, 0x042, 0x043, 0x1CD, 0x09F, 0x0A7,
    }
    walk = {
        MT_CITY_PAVE, MT_PATH_C, MT_GRASS, MT_TALL,
        0x1D0, 0x1D1, 0x1D2, 0x1D8, 0x1D9, 0x1DA, 0x1E0, 0x1E1, 0x1E2,
        0x1E4, 0x1E5, 0x1E6, 0x1E7, 0x003, 0x004, 0x2C3, 0x22B, 0x233,
    }
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt in WATER_METATILES:
                coll[y][x] = 0
            elif mt in walk:
                coll[y][x] = 0
            elif mt in TREE or mt in CLIFF_ROCK or mt >= 0x200 or mt in solid_general | DOOR_METATILES:
                coll[y][x] = 1


def facade_for(kind: str, dest: str, sec: str):
    rust = "Rustboro" in sec
    d = dest.upper()
    if kind == "center":
        return (PC_RUSTBORO if rust else PC_GENERAL), 0x061
    if kind == "mart":
        return (MART_RUSTBORO if rust else MART_GENERAL), 0x041
    if kind == "gym":
        return GYM_FACADE, 0x1CD
    if kind == "cave" or any(k in d for k in ("CAVE", "MINE", "TEMPLE", "VICTORY_ROAD")):
        return CAVE_MOUTH, 0x0A7
    if rust:
        return HOUSE_RUSTBORO, 0x22F
    return HOUSE_PETALBURG, 0x248


def pick_stamp_warps(warps: list[dict]) -> list[dict]:
    """For nearby same-dest warps, stamp once at the leftmost (primary door)."""
    items = sorted(
        [
            w for w in warps
            if classify_warp(w.get("dest_map") or "") not in (None, "gate", "other")
        ],
        key=lambda w: (w["y"], w["x"]),
    )
    chosen = []
    used = set()
    for w in items:
        key = (w["x"], w["y"])
        if key in used:
            continue
        dest = w.get("dest_map") or ""
        kind = classify_warp(dest)
        if kind in (None, "gate", "other"):
            continue
        # Skip same-dest siblings within 3 tiles horizontally (double/triple doors)
        for o in items:
            if o.get("dest_map") != dest:
                continue
            if o["y"] == w["y"] and w["x"] < o["x"] <= w["x"] + 3:
                used.add((o["x"], o["y"]))
        used.add(key)
        chosen.append(w)
    order = {"center": 0, "mart": 1, "gym": 2, "cave": 3, "building": 4, "other": 5}
    chosen.sort(key=lambda w: (order.get(classify_warp(w.get("dest_map") or ""), 6), w["y"], w["x"]))
    return chosen


def fill_for(meta, name: str) -> int:
    sec = meta.get("secondary_tileset") or ""
    if "Rustboro" in sec:
        return MT_CITY_PAVE
    if name in PAVED_CITIES:
        return MT_PATH_C
    # Grassy towns: scrub with grass, not dirt-path (avoids oversized-path FAIL)
    return MT_GRASS


def needs_stamp(grid, x, y, kind: str) -> bool:
    expect = expected_door(kind)
    if expect is None:
        return grid[y][x] not in DOOR_METATILES and grid[y][x] in TREE | CLIFF_ROCK | {MT_GRASS, MT_TALL}
    return grid[y][x] not in expect


def remediate_one(name: str) -> dict:
    if name not in LAYOUTS_JSON:
        return {"name": name, "status": "SKIP"}
    grid, coll, w, h, meta, path = load_grid(name)
    sec = meta.get("secondary_tileset") or ""
    fill = fill_for(meta, name)

    mj = MAPS / name / "map.json"
    warps = json.loads(mj.read_text()).get("warp_events") or [] if mj.exists() else []

    paved = 0
    if name in PAVED_CITIES:
        paved = pave_city(grid, coll, meta)
        fill = fill_for(meta, name)

    stamped = 0
    cleaned = 0
    # Open outdoor/field warps that landed on solid junk
    for warp in warps:
        kind = classify_warp(warp.get("dest_map") or "")
        if kind not in ("other", "gate"):
            continue
        x, y = int(warp["x"]), int(warp["y"])
        if not (0 <= x < w and 0 <= y < h):
            continue
        if grid[y][x] in TREE | CLIFF_ROCK or (grid[y][x] >= 0x200 and grid[y][x] not in DOOR_METATILES):
            grid[y][x] = fill
            coll[y][x] = 0
            cleaned += 1

    for warp in pick_stamp_warps(warps):
        dest = warp.get("dest_map") or ""
        kind = classify_warp(dest)
        if kind in (None, "gate"):
            continue
        x, y = int(warp["x"]), int(warp["y"])
        if not (0 <= x < w and 0 <= y < h):
            continue
        facade, door_mt = facade_for(kind, dest, sec)

        if needs_stamp(grid, x, y, kind):
            clear_footprint(grid, coll, x, y, facade, door_mt, fill)
            stamp(grid, x, y, facade, door_mt)
            stamped += 1
        else:
            # Door already correct — only scrub trees/rocks that poke through the facade body
            door_dx = door_dx_for(facade, door_mt)
            top = y - (len(facade) - 1)
            left = x - door_dx
            for dy in range(len(facade)):
                for dx in range(len(facade[0])):
                    fx, fy = left + dx, top + dy
                    if 0 <= fy < h and 0 <= fx < w and grid[fy][fx] in TREE | CLIFF_ROCK:
                        grid[fy][fx] = facade[dy][dx]
                        coll[fy][fx] = 1
                        cleaned += 1

        # Force every same-dest warp cell on this row onto a valid door/cave tile
        expect = expected_door(kind) or DOOR_METATILES
        for ow in warps:
            if ow.get("dest_map") != dest or int(ow["y"]) != y:
                continue
            ox = int(ow["x"])
            if not (0 <= ox < w):
                continue
            if abs(ox - x) <= 3 and grid[y][ox] not in expect:
                # Mirror primary door (or adjacent PC/Mart second door tile)
                if kind == "center" and ox == x + 1:
                    grid[y][ox] = 0x062
                elif kind == "mart" and ox == x + 1:
                    grid[y][ox] = 0x042
                else:
                    grid[y][ox] = door_mt
                coll[y][ox] = 1

        # Approach corridor south + side so BFS can reach the door
        expect_set = expected_door(kind) or DOOR_METATILES
        for ay in range(y + 1, min(h, y + 4)):
            for ax in range(max(0, x - 1), min(w, x + 2)):
                mt = grid[ay][ax]
                if mt in expect_set or mt in DOOR_METATILES:
                    continue
                if mt in TREE | CLIFF_ROCK or mt >= 0x200 or mt in {
                    0x048, 0x049, 0x04A, 0x04B, 0x050, 0x051, 0x052, 0x053,
                    0x058, 0x059, 0x05A, 0x05B, 0x060, 0x030, 0x031, 0x038,
                }:
                    grid[ay][ax] = fill
                    coll[ay][ax] = 0
        # Side approach only for cave mouths — never strip PC/Mart/house framing
        if kind == "cave":
            for ax, ay in ((x - 1, y), (x + 1, y)):
                if 0 <= ax < w and 0 <= ay < h:
                    mt = grid[ay][ax]
                    if mt not in expect_set and mt not in DOOR_METATILES and mt >= 0x200:
                        grid[ay][ax] = fill
                        coll[ay][ax] = 0

    # Repair incomplete 2x2 trees left after facade scrubbing
    repaired = _repair_trees(grid, coll, fill)

    sync_collision(grid, coll)
    path.write_bytes(pack(grid, coll))
    return {
        "name": name,
        "status": "OK",
        "paved_cells": paved,
        "stamped": stamped,
        "cleaned_tree_rock": cleaned,
        "trees_repaired": repaired,
    }


def _repair_trees(grid, coll, fill: int) -> int:
    """Orphan tree halves → fill; complete quads kept."""
    from tools.sinnoh_maps.sinnoh_build_lib import MT_TREE as TREE_TUP
    h, w = len(grid), len(grid[0])
    TREE_SET = set(TREE_TUP)
    expect = {TREE_TUP[0]: (0, 0), TREE_TUP[1]: (-1, 0), TREE_TUP[2]: (0, -1), TREE_TUP[3]: (-1, -1)}

    def is_complete(tlx, tly) -> bool:
        if tlx < 0 or tly < 0 or tlx + 1 >= w or tly + 1 >= h:
            return False
        return (
            grid[tly][tlx] == TREE_TUP[0]
            and grid[tly][tlx + 1] == TREE_TUP[1]
            and grid[tly + 1][tlx] == TREE_TUP[2]
            and grid[tly + 1][tlx + 1] == TREE_TUP[3]
        )

    n = 0
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt not in TREE_SET:
                continue
            dx, dy = expect[mt]
            if not is_complete(x + dx, y + dy):
                grid[y][x] = fill
                coll[y][x] = 0
                n += 1
    return n


def main() -> int:
    names = sorted(
        n for n in LAND_TABLE
        if n.endswith("Town") or n.endswith("City") or n in PAVED_CITIES
        or n == "PokemonLeague_Exterior"
    )
    results = []
    for n in names:
        if n not in LAYOUTS_JSON:
            continue
        # Jubilife has a dedicated rebuild — still run scrub/stamp for any misses
        r = remediate_one(n)
        results.append(r)
        if r.get("stamped") or r.get("paved_cells") or r.get("cleaned_tree_rock"):
            print(
                f"{r['name']}: paved={r.get('paved_cells',0)} "
                f"stamped={r.get('stamped',0)} cleaned={r.get('cleaned_tree_rock',0)}"
            )
    out = REPO / "tools/sinnoh_maps/remediate_city_doors_report.json"
    out.write_text(json.dumps({"results": results}, indent=2) + "\n")
    print(f"=== remediate_city_doors: {len(results)} maps → {out} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
