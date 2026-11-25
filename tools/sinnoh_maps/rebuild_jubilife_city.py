#!/usr/bin/env python3
"""Rebuild Jubilife City as a paved Platinum-style city with Emerald PC/Mart doors.

Chris's playtest: Jubilife was dirt-path + tree fragments, mangled PC (no enterable
door). Platinum Jubilife is grey pavement with TV / Pokétch / School / Center /
Mart / condos.

Uses land chunks [[18,16],[17,15]] (64×64). Emerald tiles only (Rustboro secondary
already wired on LAYOUT_JUBILIFE_CITY):
  - Walkable → Rustboro sidewalk 0x2BB
  - Edge solids → complete 2×2 trees
  - Warps get authentic Rustboro PC/Mart/house/civic facades (door 0x061/0x041/0x22F)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

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

# Rustboro city sidewalk (walkable secondary) — Jubilife uses gTileset_Rustboro
MT_CITY_PAVE = 0x2BB
# Authentic Rustboro Pokémon Center (door 0x061) — from RustboroCity map.bin
PC_FACADE = [
    [0x256, 0x25E, 0x25F, 0x257],
    [0x050, 0x051, 0x052, 0x053],
    [0x058, 0x059, 0x05A, 0x05B],
    [0x266, 0x061, 0x062, 0x27E],
]
PC_DOOR_DX = 1
# Authentic Rustboro Mart (door 0x041)
MART_FACADE = [
    [0x030, 0x031, 0x032, 0x033],
    [0x038, 0x039, 0x03A, 0x03B],
    [0x266, 0x041, 0x042, 0x27F],
]
MART_DOOR_DX = 1
# Rustboro school / flat style (door 0x22F on bottom row only)
HOUSE_FACADE = [
    [0x220, 0x221, 0x221, 0x221, 0x222],
    [0x228, 0x229, 0x229, 0x229, 0x22A],
    [0x230, 0x231, 0x231, 0x227, 0x233],
    [0x238, 0x23A, 0x23A, 0x23A, 0x23B],
    [0x240, 0x241, 0x241, 0x22F, 0x243],
]
HOUSE_DOOR_DX = 3
# Wider civic (TV / Pokétch / Condo / Terminal / School)
CIVIC_FACADE = [
    [0x220, 0x221, 0x221, 0x221, 0x221, 0x222],
    [0x228, 0x229, 0x229, 0x229, 0x229, 0x22A],
    [0x230, 0x231, 0x231, 0x227, 0x231, 0x233],
    [0x238, 0x23A, 0x23A, 0x23A, 0x23A, 0x23B],
    [0x240, 0x241, 0x241, 0x22F, 0x241, 0x243],
]
CIVIC_DOOR_DX = 3

DOOR_METATILES = {0x061, 0x041, 0x22F, 0x248, 0x20E, 0x287}

# Building stamp classification by dest_map substring
BUILDING_KIND = [
    ("POKEMON_CENTER", "center"),
    ("MART", "mart"),
    ("POKETCH", "civic"),
    ("TRAINERS_SCHOOL", "civic"),
    ("TV_", "civic"),
    ("CONDO", "civic"),
    ("GLOBAL_TERMINAL", "civic"),
    ("HOUSE", "house"),
]


def stamp(grid, door_x: int, door_y: int, facade, door_dx: int) -> None:
    top = door_y - (len(facade) - 1)
    left = door_x - door_dx
    h, w = len(grid), len(grid[0])
    for dy, row in enumerate(facade):
        for dx, mt in enumerate(row):
            x, y = left + dx, top + dy
            if 0 <= y < h and 0 <= x < w:
                grid[y][x] = mt


def clear_footprint(grid, collision, door_x, door_y, facade, door_dx, pad=1) -> None:
    top = door_y - (len(facade) - 1) - pad
    left = door_x - door_dx - pad
    h, w = len(grid), len(grid[0])
    fh, fw = len(facade) + pad * 2 + 1, len(facade[0]) + pad * 2
    for dy in range(fh):
        for dx in range(fw):
            x, y = left + dx, top + dy
            if 0 <= y < h and 0 <= x < w:
                grid[y][x] = MT_CITY_PAVE
                collision[y][x] = 0


def kind_for_dest(dest: str) -> str | None:
    for sub, kind in BUILDING_KIND:
        if sub in dest:
            return kind
    if "GATE" in dest:
        return None
    return "house"


def facade_for(kind: str):
    if kind == "center":
        return PC_FACADE, PC_DOOR_DX
    if kind == "mart":
        return MART_FACADE, MART_DOOR_DX
    if kind == "civic":
        return CIVIC_FACADE, CIVIC_DOOR_DX
    return HOUSE_FACADE, HOUSE_DOOR_DX


def sync_collision(grid, collision) -> None:
    """Match Twinleaf/vanilla: buildings+trees solid; doors keep solid bit (engine
    warp-door behavior); pavement/water walkable.
    """
    h, w = len(grid), len(grid[0])
    TREE = set(MT_TREE)
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt in WATER_METATILES:
                collision[y][x] = 0
            elif mt == MT_CITY_PAVE:
                collision[y][x] = 0
            elif mt in TREE or mt == MT_ROCK or mt == 0x139:
                collision[y][x] = 1
            elif mt >= 0x200:
                # Secondary facade body (incl. door 0x22F) — solid like vanilla Rustboro
                collision[y][x] = 1
            elif mt in (0x061, 0x041, 0x050, 0x051, 0x052, 0x053, 0x058, 0x059, 0x05A, 0x05B,
                        0x060, 0x062, 0x063, 0x030, 0x031, 0x032, 0x033, 0x038, 0x039, 0x03A, 0x03B,
                        0x048, 0x049, 0x04A, 0x04B):
                # General PC/Mart body + door — solid like vanilla (warp-door MB)
                collision[y][x] = 1
            else:
                collision[y][x] = 0


def rebuild() -> None:
    chunks = LAND_TABLE["JubilifeCity"]
    attr = stitch(chunks)
    h, w = len(attr), len(attr[0])
    assert (w, h) == (64, 64), (w, h)

    solid = [[bool(plat_collision(attr[y][x])) for x in range(w)] for y in range(h)]
    # Trees only for edge-ring solids; interior solids become pavement (buildings stamped later)
    edge = [[False] * w for _ in range(h)]
    margin = 2
    for y in range(h):
        for x in range(w):
            if solid[y][x] and (x < margin or y < margin or x >= w - margin or y >= h - margin):
                edge[y][x] = True
    tree_grid = place_complete_trees([row[:] for row in edge])

    grid = [[MT_CITY_PAVE for _ in range(w)] for _ in range(h)]
    collision = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if edge[y][x] and tree_grid[y][x] in set(MT_TREE) | {MT_ROCK}:
                grid[y][x] = tree_grid[y][x]
                collision[y][x] = 1

    mj_path = MAPS / "JubilifeCity" / "map.json"
    mj = json.loads(mj_path.read_text())
    warps = mj.get("warp_events") or []

    # Drop bogus corner warps (0,0)/(1,0) condo duplicates
    warps = [
        w for w in warps
        if not (w["x"] <= 1 and w["y"] <= 1 and "CONDO" in w.get("dest_map", ""))
    ]

    # Ensure approach tiles south of each door are walkable pavement
    for warp in warps:
        if "GATE" in warp.get("dest_map", ""):
            continue
        x, y = warp["x"], warp["y"]
        for ay in range(y, min(h, y + 3)):
            for ax in range(max(0, x - 2), min(w, x + 3)):
                if grid[ay][ax] in set(MT_TREE) | {MT_ROCK}:
                    grid[ay][ax] = MT_CITY_PAVE
                    collision[ay][ax] = 0

    # Stamp larger civics first so smaller houses can overwrite overlaps cleanly
    ordered = sorted(
        warps,
        key=lambda w: (
            0 if kind_for_dest(w.get("dest_map", "")) == "civic" else
            1 if kind_for_dest(w.get("dest_map", "")) in ("center", "mart") else 2
        ),
    )
    stamped = 0
    for warp in ordered:
        dest = warp.get("dest_map", "")
        kind = kind_for_dest(dest)
        if kind is None:
            continue
        facade, door_dx = facade_for(kind)
        clear_footprint(grid, collision, warp["x"], warp["y"], facade, door_dx)
        stamp(grid, warp["x"], warp["y"], facade, door_dx)
        stamped += 1

    # Open north exit (Route 204) and west gate corridor
    for x in range(44, 48):
        for y in range(0, 3):
            grid[y][x] = MT_CITY_PAVE
            collision[y][x] = 0
    for y in range(20, 26):
        for x in range(0, 3):
            grid[y][x] = MT_CITY_PAVE
            collision[y][x] = 0

    sync_collision(grid, collision)

    blob = pack(grid, collision)
    (LAYOUTS / "JubilifeCity" / "map.bin").write_bytes(blob)

    # Keep layout tilesets: General + Rustboro
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
    pave = sum(1 for y in range(h) for x in range(w) if grid[y][x] == MT_CITY_PAVE)
    print(f"Jubilife rebuilt: {stamped} buildings stamped, {doors} door tiles, {pave} pavement cells")


if __name__ == "__main__":
    rebuild()
