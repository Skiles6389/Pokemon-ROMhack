#!/usr/bin/env python3
"""Rebuild Jubilife City: Platinum street layout + COMPLETE Emerald building stamps.

- Walkable Platinum cells → Rustboro sidewalk 0x2BB
- Edge solids only → complete 2×2 trees (few trees, borders only)
- Interior solids → sidewalk (plaza/streets; buildings stamped on top)
- Every building is a full contiguous stamp from Rustboro/Oldale (see
  emerald_building_stamps.py) with door warp on the door metatile
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.emerald_building_stamps import (  # noqa: E402
    CIVIC_RUSTBORO,
    CIVIC_RUSTBORO_WIDE,
    HOUSE_RUSTBORO,
    MAILBOX,
    MART_RUSTBORO,
    PC_RUSTBORO,
    stamp_with_clear,
)
from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    LAYOUTS,
    LAYOUTS_JSON,
    MAPS,
    MT_ROCK,
    MT_TREE,
    WATER_METATILES,
    pack,
    place_complete_trees,
    plat_collision,
    stitch,
)

MT_CITY_PAVE = 0x2BB
MT_CITY_PLAZA = 0x2C3  # accent plaza squares
DOOR_METATILES = {0x061, 0x041, 0x22F, 0x248, 0x20E, 0x287, 0x062, 0x042}

BUILDING_KIND = [
    ("POKEMON_CENTER", "center"),
    ("MART", "mart"),
    ("POKETCH", "civic_wide"),
    ("TRAINERS_SCHOOL", "civic"),
    ("TV_", "civic_wide"),
    ("CONDO", "civic"),
    ("GLOBAL_TERMINAL", "civic_wide"),
    ("HOUSE", "house"),
]


def kind_for_dest(dest: str) -> str | None:
    for sub, kind in BUILDING_KIND:
        if sub in dest:
            return kind
    if "GATE" in dest:
        return None
    return "house"


def facade_for(kind: str):
    return {
        "center": PC_RUSTBORO,
        "mart": MART_RUSTBORO,
        "civic": CIVIC_RUSTBORO,
        "civic_wide": CIVIC_RUSTBORO_WIDE,
        "house": HOUSE_RUSTBORO,
    }[kind]


def sync_collision(grid, collision) -> None:
    TREE = set(MT_TREE)
    h, w = len(grid), len(grid[0])
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt in WATER_METATILES or mt in (MT_CITY_PAVE, MT_CITY_PLAZA):
                collision[y][x] = 0
            elif mt in TREE or mt == MT_ROCK or mt == 0x139:
                collision[y][x] = 1
            elif mt == 0x201:  # door mat — must be walkable for approach
                collision[y][x] = 0
            elif mt >= 0x200:
                collision[y][x] = 1
            elif mt in DOOR_METATILES or (0x028 <= mt <= 0x063) or mt in (
                0x256, 0x257, 0x25E, 0x25F, 0x266, 0x27E, 0x27F, 0x325, 0x326, 0x267,
            ):
                collision[y][x] = 1
            else:
                collision[y][x] = 0


def rebuild() -> None:
    chunks = LAND_TABLE["JubilifeCity"]
    attr = stitch(chunks)
    h, w = len(attr), len(attr[0])
    assert (w, h) == (64, 64), (w, h)

    solid = [[bool(plat_collision(attr[y][x])) for x in range(w)] for y in range(h)]
    # Trees ONLY on outer margin (Chris: few trees, borders only)
    edge = [[False] * w for _ in range(h)]
    margin = 2
    for y in range(h):
        for x in range(w):
            if solid[y][x] and (x < margin or y < margin or x >= w - margin or y >= h - margin):
                edge[y][x] = True
    tree_grid = place_complete_trees([row[:] for row in edge])

    # Entire interior (walkable + former building solids) → pavement so streets read
    grid = [[MT_CITY_PAVE for _ in range(w)] for _ in range(h)]
    collision = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if edge[y][x] and tree_grid[y][x] in set(MT_TREE) | {MT_ROCK}:
                grid[y][x] = tree_grid[y][x]
                collision[y][x] = 1

    # Cross-street sidewalk accents (Platinum avenue feel) before buildings
    for y in range(20, 44):
        for x in (31, 32):
            if grid[y][x] == MT_CITY_PAVE:
                grid[y][x] = MT_CITY_PLAZA
    for x in range(20, 44):
        for y in (31, 32):
            if grid[y][x] == MT_CITY_PAVE:
                grid[y][x] = MT_CITY_PLAZA

    mj_path = MAPS / "JubilifeCity" / "map.json"
    mj = json.loads(mj_path.read_text())
    warps = [
        wp for wp in (mj.get("warp_events") or [])
        if not (wp["x"] <= 1 and wp["y"] <= 1 and "CONDO" in wp.get("dest_map", ""))
    ]
    # Dedupe Pokétch double door — keep leftmost
    seen_poketch = False
    filtered = []
    for wp in sorted(warps, key=lambda z: (z["y"], z["x"])):
        dest = wp.get("dest_map", "")
        if "POKETCH" in dest:
            if seen_poketch:
                continue
            seen_poketch = True
        filtered.append(wp)
    warps = filtered

    ordered = sorted(
        warps,
        key=lambda wp: (
            0 if kind_for_dest(wp.get("dest_map", "")) in ("civic_wide", "civic") else
            1 if kind_for_dest(wp.get("dest_map", "")) in ("center", "mart") else 2
        ),
    )
    stamped = 0
    for warp in ordered:
        kind = kind_for_dest(warp.get("dest_map", ""))
        if kind is None:
            continue
        stamp = facade_for(kind)
        stamp_with_clear(grid, collision, warp["x"], warp["y"], stamp, MT_CITY_PAVE, pad=1)
        stamped += 1

    # Ensure gate corridors open
    for x in range(44, 48):
        for y in range(0, 3):
            grid[y][x] = MT_CITY_PAVE
            collision[y][x] = 0
    for y in range(20, 26):
        for x in range(0, 3):
            grid[y][x] = MT_CITY_PAVE
            collision[y][x] = 0

    # Central plaza + fountain (after stamps so civic pads don't wipe it)
    for y in range(26, 38):
        for x in range(26, 38):
            if grid[y][x] in (MT_CITY_PAVE, MT_CITY_PLAZA):
                grid[y][x] = MT_CITY_PLAZA
                collision[y][x] = 0
    for y in range(30, 34):
        for x in range(30, 34):
            # Fountain rim uses plaza; keep center walkable accent
            grid[y][x] = MT_CITY_PLAZA if (x in (30, 33) or y in (30, 33)) else 0x2C3
            collision[y][x] = 0

    # Emerald city decor: flower patches + lamp/sign posts (general tileset)
    FLOWER = 0x004  # pink flower bed
    BUSH = 0x00D
    SHRUB = 0x00E
    for left, top in (
        (22, 24), (38, 24), (22, 38), (38, 38), (24, 30), (36, 30),
        (28, 22), (34, 22), (28, 40), (34, 40), (18, 31), (44, 31),
    ):
        for dy in range(2):
            for dx in range(2):
                x, y = left + dx, top + dy
                if 0 <= x < w and 0 <= y < h and grid[y][x] in (MT_CITY_PAVE, MT_CITY_PLAZA):
                    grid[y][x] = (FLOWER, BUSH, SHRUB, FLOWER)[(dx + 2 * dy) % 4]
                    collision[y][x] = 0
    # Sidewalk strips from plaza toward each stamped door
    for warp in warps:
        kind = kind_for_dest(warp.get("dest_map", ""))
        if kind is None:
            continue
        dx, dy = int(warp["x"]), int(warp["y"])
        # Walk south from door toward plaza row if north of plaza
        if dy < 30:
            for y in range(dy + 2, min(31, dy + 8)):
                for ox in (0, 1):
                    x = dx + ox
                    if 0 <= x < w and grid[y][x] == MT_CITY_PAVE:
                        grid[y][x] = MT_CITY_PLAZA
        elif dy > 34:
            for y in range(max(33, dy - 8), dy):
                for ox in (0, 1):
                    x = dx + ox
                    if 0 <= x < w and grid[y][x] == MT_CITY_PAVE:
                        grid[y][x] = MT_CITY_PLAZA
        # Lamp/sign posts near major doors
        if kind in ("civic", "civic_wide", "center", "mart"):
            for mx, my in ((dx + 3, dy + 1), (dx - 3, dy + 1), (dx + 4, dy + 2)):
                if 0 <= mx < w and 0 <= my < h and grid[my][mx] in (MT_CITY_PAVE, MT_CITY_PLAZA):
                    grid[my][mx] = MAILBOX
                    collision[my][mx] = 1
                    break
    # Avenue lamp posts along plaza cross
    for x in (24, 28, 35, 39):
        for y in (31, 32):
            if grid[y][x] in (MT_CITY_PAVE, MT_CITY_PLAZA):
                grid[y][x] = MAILBOX
                collision[y][x] = 1
    for y in (24, 28, 35, 39):
        for x in (31, 32):
            if grid[y][x] in (MT_CITY_PAVE, MT_CITY_PLAZA):
                grid[y][x] = MAILBOX
                collision[y][x] = 1

    # Scrub any orphan tree halves on the border
    TREE = set(MT_TREE)
    expect = {MT_TREE[0]: (0, 0), MT_TREE[1]: (-1, 0), MT_TREE[2]: (0, -1), MT_TREE[3]: (-1, -1)}

    def complete(tlx, tly):
        if tlx < 0 or tly < 0 or tlx + 1 >= w or tly + 1 >= h:
            return False
        return (
            grid[tly][tlx] == MT_TREE[0]
            and grid[tly][tlx + 1] == MT_TREE[1]
            and grid[tly + 1][tlx] == MT_TREE[2]
            and grid[tly + 1][tlx + 1] == MT_TREE[3]
        )

    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt == MT_ROCK:
                grid[y][x] = MT_CITY_PAVE
                collision[y][x] = 0
            elif mt in TREE:
                dx, dy = expect[mt]
                if not complete(x + dx, y + dy):
                    grid[y][x] = MT_CITY_PAVE
                    collision[y][x] = 0

    sync_collision(grid, collision)
    (LAYOUTS / "JubilifeCity" / "map.bin").write_bytes(pack(grid, collision))

    layouts = json.loads(LAYOUTS_JSON.read_text())
    for L in layouts["layouts"]:
        if L.get("id") == "LAYOUT_JUBILIFE_CITY":
            L["primary_tileset"] = "gTileset_General"
            L["secondary_tileset"] = "gTileset_Rustboro"
            break
    LAYOUTS_JSON.write_text(json.dumps(layouts, indent=2) + "\n")

    mj["warp_events"] = warps
    mj_path.write_text(json.dumps(mj, indent=2) + "\n")

    doors = sum(1 for y in range(h) for x in range(w) if grid[y][x] in DOOR_METATILES)
    trees = sum(1 for y in range(h) for x in range(w) if grid[y][x] in TREE)
    pave = sum(1 for y in range(h) for x in range(w) if grid[y][x] in (MT_CITY_PAVE, MT_CITY_PLAZA))
    print(f"Jubilife rebuilt: {stamped} complete stamps, {doors} doors, {pave} pave, {trees} tree tiles")


if __name__ == "__main__":
    rebuild()
