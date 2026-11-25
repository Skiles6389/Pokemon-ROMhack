#!/usr/bin/env python3
"""Rebuild Twinleaf Town to Platinum geometry + re-pack water elev on all Sinnoh maps.

Fixes:
- Water elev 3→1 (vanilla Emerald) so ponds are not walkable without Surf
- Twinleaf tree ring uses complete 2x2 trees (no rock/cliff leftovers)
- Paths from Platinum walkway attrs; houses stamped at door warps
- Corner flower beds (tall-grass stand-in) inside tree clearings
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
    LAYOUTS,
    LAYOUTS_JSON,
    MAPS,
    MT_GRASS,
    MT_ROCK,
    MT_TALL,
    MT_TREE,
    MT_WATER,
    WATER_METATILES,
    encode_map_cell,
    grid_from_chunks,
    paint_paths_from_attrs,
    pack,
    load_attrs,
)

# Twinleaf house facade (Emerald Petalburg secondary) — door 0x248
HOUSE = [
    [0x210, 0x211, 0x211, 0x211, 0x212],
    [0x218, 0x219, 0x219, 0x219, 0x21A],
    [0x222, 0x232, 0x230, 0x240, 0x221],
    [0x22A, 0x23A, 0x238, 0x248, 0x229],
]
# Larger player/rival house (5x5-ish using same tiles with extra mid column)
HOUSE_LARGE = [
    [0x210, 0x211, 0x211, 0x211, 0x211, 0x212],
    [0x218, 0x219, 0x219, 0x219, 0x219, 0x21A],
    [0x222, 0x232, 0x230, 0x240, 0x230, 0x221],
    [0x22A, 0x23A, 0x238, 0x248, 0x238, 0x229],
]


def stamp_facade(grid, door_x: int, door_y: int, facade) -> None:
    door_dx = next(i for i, mt in enumerate(facade[-1]) if mt == 0x248)
    top = door_y - (len(facade) - 1)
    left = door_x - door_dx
    for dy, row in enumerate(facade):
        for dx, mt in enumerate(row):
            x, y = left + dx, top + dy
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = mt


def clear_house_footprint(grid, collision, door_x: int, door_y: int, facade) -> None:
    """Grass under facade so trees/rocks don't stick through roofs."""
    door_dx = next(i for i, mt in enumerate(facade[-1]) if mt == 0x248)
    top = door_y - (len(facade) - 1)
    left = door_x - door_dx
    h, w = len(grid), len(grid[0])
    for dy in range(len(facade) + 1):
        for dx in range(len(facade[0])):
            x, y = left + dx, top + dy
            if 0 <= y < h and 0 <= x < w:
                if grid[y][x] in set(MT_TREE) | {MT_ROCK}:
                    grid[y][x] = MT_GRASS
                    collision[y][x] = 0


def repair_incomplete_trees(grid, collision) -> None:
    """Ensure every tree tile belongs to a complete TL/TR/BL/BR quad; else grass."""
    h, w = len(grid), len(grid[0])
    expect = {MT_TREE[0]: (0, 0), MT_TREE[1]: (-1, 0), MT_TREE[2]: (0, -1), MT_TREE[3]: (-1, -1)}
    TREE = set(MT_TREE)

    def is_complete(tlx, tly) -> bool:
        if tlx < 0 or tly < 0 or tlx + 1 >= w or tly + 1 >= h:
            return False
        return (
            grid[tly][tlx] == MT_TREE[0]
            and grid[tly][tlx + 1] == MT_TREE[1]
            and grid[tly + 1][tlx] == MT_TREE[2]
            and grid[tly + 1][tlx + 1] == MT_TREE[3]
        )

    orphans = []
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt not in TREE:
                continue
            dx, dy = expect[mt]
            if not is_complete(x + dx, y + dy):
                orphans.append((x, y))
    for x, y in orphans:
        if grid[y][x] in TREE:
            grid[y][x] = MT_GRASS
            collision[y][x] = 0


def paint_flower_beds(grid, collision) -> None:
    """Emerald tall-grass patches as flower-bed stand-ins in Twinleaf NW/NE clearings."""
    beds = [
        # top-left garden (near player house)
        [(5, 4), (6, 4), (5, 5), (6, 5)],
        # top-right garden
        [(24, 4), (25, 4), (24, 5), (25, 5)],
    ]
    for bed in beds:
        for x, y in bed:
            if grid[y][x] == MT_GRASS:
                grid[y][x] = MT_TALL
                collision[y][x] = 0


def scrub_rocks_to_trees_or_grass(grid, collision) -> None:
    """Replace outdoor rock leftovers with non-overlapping 2x2 trees, else grass.

    Never overwrite an existing tree tile — overlapping stamps caused orphan halves.
    """
    h, w = len(grid), len(grid[0])
    TREE = set(MT_TREE)

    def try_tree(tx, ty) -> bool:
        if tx < 0 or ty < 0 or tx + 1 >= w or ty + 1 >= h:
            return False
        cells = [(tx, ty), (tx + 1, ty), (tx, ty + 1), (tx + 1, ty + 1)]
        for cx, cy in cells:
            mt = grid[cy][cx]
            if mt in TREE or mt == MT_WATER or mt >= 0x200:
                return False
            # Only convert rock/grass/tall — not paths
            if mt not in (MT_ROCK, MT_GRASS, MT_TALL) and mt not in TREE:
                if mt in (0x1D0, 0x1D1, 0x1D2, 0x1D8, 0x1D9, 0x1DA, 0x1E0, 0x1E1, 0x1E2, 0x1E4, 0x1E5, 0x1E6, 0x1E7):
                    return False
        # Prefer quads that still contain at least one rock leftover
        if not any(grid[cy][cx] == MT_ROCK for cx, cy in cells):
            return False
        grid[ty][tx] = MT_TREE[0]
        grid[ty][tx + 1] = MT_TREE[1]
        grid[ty + 1][tx] = MT_TREE[2]
        grid[ty + 1][tx + 1] = MT_TREE[3]
        for cx, cy in cells:
            collision[cy][cx] = 1
        return True

    # Multi-pass greedy on remaining rocks only
    for _ in range(8):
        rocks = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == MT_ROCK]
        if not rocks:
            break
        progressed = False
        for x, y in rocks:
            if grid[y][x] != MT_ROCK:
                continue
            for tx, ty in ((x & ~1, y & ~1), (x, y), (x - 1, y), (x, y - 1), (x - 1, y - 1)):
                if try_tree(tx, ty):
                    progressed = True
                    break
        if not progressed:
            break
    # Any rock still left → grass (slightly opens Platinum solid; no cliff tiles)
    for y in range(h):
        for x in range(w):
            if grid[y][x] == MT_ROCK:
                grid[y][x] = MT_GRASS
                collision[y][x] = 0


def rebuild_twinleaf() -> None:
    chunks = LAND_TABLE["TwinleafTown"]
    grid, width, height, collision = grid_from_chunks(chunks)
    attrs = [[load_attrs(chunks[0][0])[y * 32 + x] for x in range(32)] for y in range(32)]
    paint_paths_from_attrs(grid, attrs, map_name="TwinleafTown")

    mj = json.loads((MAPS / "TwinleafTown" / "map.json").read_text())
    warps = mj.get("warp_events") or []
    # Platinum: large houses = player + rival; two small NPC houses
    for warp in warps:
        dx, dy = int(warp["x"]), int(warp["y"])
        dest = warp.get("dest_map") or ""
        large = "PLAYERSHOUSE" in dest or "RIVALSHOUSE" in dest
        facade = HOUSE_LARGE if large else HOUSE
        clear_house_footprint(grid, collision, dx, dy, facade)
        stamp_facade(grid, dx, dy, facade)

    scrub_rocks_to_trees_or_grass(grid, collision)
    repair_incomplete_trees(grid, collision)
    # Re-assert water cells from Platinum (pond)
    for y in range(height):
        for x in range(width):
            if grid[y][x] == MT_WATER:
                collision[y][x] = 0

    paint_flower_beds(grid, collision)

    # Sync collision for buildings
    for y in range(height):
        for x in range(width):
            mt = grid[y][x]
            if mt in WATER_METATILES:
                collision[y][x] = 0
            elif mt >= 0x200 or mt in set(MT_TREE) or mt == MT_ROCK:
                collision[y][x] = 1

    blob = pack(grid, collision)
    folder = LAYOUTS / "TwinleafTown"
    (folder / "map.bin").write_bytes(blob)
    # Tree-border border.bin
    border = bytearray(8)
    for i, mt in enumerate(MT_TREE):
        struct.pack_into("<H", border, i * 2, encode_map_cell(mt, collision=1))
    (folder / "border.bin").write_bytes(bytes(border))
    rocks = sum(1 for row in grid for mt in row if mt == MT_ROCK)
    water = sum(1 for row in grid for mt in row if mt == MT_WATER)
    trees = sum(1 for row in grid for mt in row if mt in set(MT_TREE))
    print(f"TwinleafTown rebuilt: rocks={rocks} water={water} tree_tiles={trees} size={width}x{height}")


def reencode_water_all_sinnoh() -> int:
    """Re-pack every Sinnoh layout cell so water uses elev=1."""
    layouts = json.loads(LAYOUTS_JSON.read_text())["layouts"]
    fixed = 0
    for name in sorted(LAND_TABLE):
        meta = next((L for L in layouts if L["name"].replace("_Layout", "") == name or name in L["name"]), None)
        if not meta:
            continue
        path = REPO / meta["blockdata_filepath"]
        if not path.exists():
            continue
        raw = bytearray(path.read_bytes())
        changed = False
        for i in range(0, len(raw), 2):
            cell = struct.unpack_from("<H", raw, i)[0]
            mt = cell & 0x3FF
            if mt not in WATER_METATILES:
                continue
            new = encode_map_cell(mt, collision=0)
            if new != cell:
                struct.pack_into("<H", raw, i, new)
                changed = True
        if changed:
            path.write_bytes(bytes(raw))
            fixed += 1
    print(f"re-encoded water elev on {fixed} Sinnoh layouts")
    return fixed


def main() -> int:
    if not (REPO / "tools/sinnoh_maps").exists():
        return 1
    rebuild_twinleaf()
    reencode_water_all_sinnoh()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
