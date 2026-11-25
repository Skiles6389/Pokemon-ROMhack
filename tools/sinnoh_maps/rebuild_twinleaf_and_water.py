#!/usr/bin/env python3
"""Rebuild Twinleaf Town with COMPLETE Emerald house stamps + fenced gardens.

- Houses: exact Littleroot stamps (roof ridge through door row)
- Gardens: Petalburg fence ring + tall-grass flowers (not roof slabs)
- Paths: Platinum walkways + spine between doors; no path adjacent to water
- Water elev re-pack on all Sinnoh maps
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.emerald_building_stamps import (  # noqa: E402
    DOOR_MAT,
    GARDEN_FENCED,
    HOUSE_PETALBURG_A,
    HOUSE_PETALBURG_WIDE,
    MAILBOX,
    stamp_at,
    stamp_with_clear,
)
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
    load_attrs,
    pack,
    paint_paths_from_attrs,
)


def repair_incomplete_trees(grid, collision) -> None:
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

    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt not in TREE:
                continue
            dx, dy = expect[mt]
            if not is_complete(x + dx, y + dy):
                grid[y][x] = MT_GRASS
                collision[y][x] = 0


def scrub_rocks_to_trees_or_grass(grid, collision) -> None:
    h, w = len(grid), len(grid[0])
    TREE = set(MT_TREE)
    PATH = {
        0x1D0, 0x1D1, 0x1D2, 0x1D8, 0x1D9, 0x1DA, 0x1E0, 0x1E1, 0x1E2,
        0x1E4, 0x1E5, 0x1E6, 0x1E7,
    }

    def try_tree(tx, ty) -> bool:
        if tx < 0 or ty < 0 or tx + 1 >= w or ty + 1 >= h:
            return False
        cells = [(tx, ty), (tx + 1, ty), (tx, ty + 1), (tx + 1, ty + 1)]
        for cx, cy in cells:
            mt = grid[cy][cx]
            if mt in TREE or mt == MT_WATER or mt >= 0x200 or mt in PATH:
                return False
            if mt not in (MT_ROCK, MT_GRASS, MT_TALL):
                return False
        if not any(grid[cy][cx] == MT_ROCK for cx, cy in cells):
            return False
        grid[ty][tx] = MT_TREE[0]
        grid[ty][tx + 1] = MT_TREE[1]
        grid[ty + 1][tx] = MT_TREE[2]
        grid[ty + 1][tx + 1] = MT_TREE[3]
        for cx, cy in cells:
            collision[cy][cx] = 1
        return True

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
    for y in range(h):
        for x in range(w):
            if grid[y][x] == MT_ROCK:
                grid[y][x] = MT_GRASS
                collision[y][x] = 0


def paint_fenced_gardens(grid, collision) -> None:
    """Fenced flower beds in NW/NE clearings — fence + flowers, never a roof slab."""
    # Place so gardens sit in grass clearings inside the tree ring
    # Keep clear of house roofs (rival wide roof starts ~y=7,x=6; house1 at x=17)
    # Garden is 5×4 — stay clear of rival wide roof (~y=7,x=6)
    spots = [(1, 2), (26, 2)]
    for left, top in spots:
        # Clear footprint to grass first (wipe old roof-slab gardens + trees)
        sh, sw = len(GARDEN_FENCED["tiles"]), len(GARDEN_FENCED["tiles"][0])
        for dy in range(sh + 1):
            for dx in range(sw + 1):
                x, y = left + dx, top + dy
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    mt = grid[y][x]
                    if mt in set(MT_TREE) | {MT_ROCK} or mt >= 0x200:
                        grid[y][x] = MT_GRASS
                        collision[y][x] = 0
        stamp_at(grid, left, top, {**GARDEN_FENCED, "door_dx": 0, "door_dy": 0}, fill_mat=False)
        # Signposts solid; flowers/grass/shrubs walkable
        for dy, row in enumerate(GARDEN_FENCED["tiles"]):
            for dx, mt in enumerate(row):
                x, y = left + dx, top + dy
                if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
                    continue
                collision[y][x] = 1 if mt == MAILBOX else 0


# Emerald General sand-on-grass autotiles ( visibly tan, not green dirt 0x1D0 )
SAND_TABLE = (
    (0x118, 0x119, 0x11A),
    (0x120, 0x121, 0x122),
    (0x128, 0x129, 0x12A),
)
SAND_IDS = {mt for row in SAND_TABLE for mt in row}
OLD_PATH = {
    0x1CE, 0x1CF, 0x1D0, 0x1D1, 0x1D2, 0x1D8, 0x1D9, 0x1DA,
    0x1E0, 0x1E1, 0x1E2, 0x1E4, 0x1E5, 0x1E6, 0x1E7,
}


def sand_metatile_for_neighbors(n: bool, s: bool, w: bool, e: bool) -> int:
    if not n and not s:
        row = 1
    elif not n:
        row = 0
    elif not s:
        row = 2
    else:
        row = 1
    if not w and not e:
        col = 1
    elif not w:
        col = 0
    elif not e:
        col = 2
    else:
        col = 1
    return SAND_TABLE[row][col]


def connect_house_paths(grid, warps) -> None:
    """Cross-shaped Emerald sand paths (0x118–0x12A) between houses."""
    h, w = len(grid), len(grid[0])
    # Clear old green dirt / faint path so sand rebuilds cleanly
    for y in range(h):
        for x in range(w):
            if grid[y][x] in OLD_PATH | SAND_IDS:
                grid[y][x] = MT_GRASS

    path_cells: set[tuple[int, int]] = set()
    spine_y = 13
    for warp in warps:
        dx, dy = int(warp["x"]), int(warp["y"])
        y0, y1 = sorted((min(h - 1, dy + 2), spine_y))
        for y in range(y0, y1 + 1):
            for ox in (0, 1):
                xx = dx + ox
                if 0 <= xx < w and grid[y][xx] in {MT_GRASS, MT_TALL} | SAND_IDS | OLD_PATH:
                    path_cells.add((xx, y))
        path_cells.add((dx, spine_y))
        if dx + 1 < w:
            path_cells.add((dx + 1, spine_y))
    xs = [int(w_["x"]) for w_ in warps]
    if xs:
        for x in range(min(xs), max(xs) + 1):
            for oy in (0, 1):
                yy = spine_y + oy
                if yy < h and grid[yy][x] in {MT_GRASS, MT_TALL} | SAND_IDS | OLD_PATH:
                    path_cells.add((x, yy))

    def near_water(x, y) -> bool:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in WATER_METATILES:
                    return True
        return False

    for x, y in list(path_cells):
        if not (0 <= x < w and 0 <= y < h):
            continue
        if near_water(x, y):
            if grid[y][x] in SAND_IDS | OLD_PATH | {0x121}:
                grid[y][x] = MT_GRASS
            continue
        if grid[y][x] >= 0x200 or grid[y][x] == MT_WATER or grid[y][x] in set(MT_TREE):
            continue
        if grid[y][x] in (DOOR_MAT, MAILBOX):
            continue
        n = (x, y - 1) in path_cells and not near_water(x, y - 1)
        s = (x, y + 1) in path_cells and not near_water(x, y + 1)
        ww = (x - 1, y) in path_cells and not near_water(x - 1, y)
        e = (x + 1, y) in path_cells and not near_water(x + 1, y)
        grid[y][x] = sand_metatile_for_neighbors(n, s, ww, e)

    for y in range(h):
        for x in range(w):
            if grid[y][x] in SAND_IDS | {0x121} and near_water(x, y):
                grid[y][x] = MT_GRASS


def rebuild_twinleaf() -> None:
    chunks = LAND_TABLE["TwinleafTown"]
    grid, width, height, collision = grid_from_chunks(chunks)
    attrs = [[load_attrs(chunks[0][0])[y * 32 + x] for x in range(32)] for y in range(32)]
    paint_paths_from_attrs(grid, attrs, map_name="TwinleafTown")

    mj = json.loads((MAPS / "TwinleafTown" / "map.json").read_text())
    warps = mj.get("warp_events") or []
    for warp in warps:
        dx, dy = int(warp["x"]), int(warp["y"])
        dest = warp.get("dest_map") or ""
        large = "PLAYERSHOUSE" in dest or "RIVALSHOUSE" in dest
        stamp = HOUSE_PETALBURG_WIDE if large else HOUSE_PETALBURG_A
        stamp_with_clear(grid, collision, dx, dy, stamp, MT_GRASS, pad=1)

    scrub_rocks_to_trees_or_grass(grid, collision)
    repair_incomplete_trees(grid, collision)
    for y in range(height):
        for x in range(width):
            if grid[y][x] == MT_WATER:
                collision[y][x] = 0

    paint_fenced_gardens(grid, collision)
    connect_house_paths(grid, warps)
    # Re-assert door mats
    for warp in warps:
        dx, dy = int(warp["x"]), int(warp["y"])
        if dy + 1 < height and grid[dy + 1][dx] not in set(MT_TREE) and grid[dy + 1][dx] < 0x208:
            grid[dy + 1][dx] = DOOR_MAT
        # Mailbox beside door on grass
        for mx in (dx + 1, dx - 1):
            if 0 <= mx < width and grid[dy][mx] == MT_GRASS:
                grid[dy][mx] = MAILBOX
                break

    repair_incomplete_trees(grid, collision)

    FENCE = {0x214, 0x215, 0x216, 0x21C, 0x21D, 0x21E}
    for y in range(height):
        for x in range(width):
            mt = grid[y][x]
            if mt in WATER_METATILES or mt in (DOOR_MAT, MAILBOX) or mt in (MT_TALL, 0x00D):
                collision[y][x] = 0
            elif mt >= 0x200 or mt in set(MT_TREE) or mt == MT_ROCK or mt in FENCE:
                collision[y][x] = 1

    blob = pack(grid, collision)
    folder = LAYOUTS / "TwinleafTown"
    (folder / "map.bin").write_bytes(blob)
    border = bytearray(8)
    for i, mt in enumerate(MT_TREE):
        struct.pack_into("<H", border, i * 2, encode_map_cell(mt, collision=1))
    (folder / "border.bin").write_bytes(bytes(border))
    rocks = sum(1 for row in grid for mt in row if mt == MT_ROCK)
    water = sum(1 for row in grid for mt in row if mt == MT_WATER)
    trees = sum(1 for row in grid for mt in row if mt in set(MT_TREE))
    print(f"TwinleafTown rebuilt: rocks={rocks} water={water} tree_tiles={trees} size={width}x{height}")


def reencode_water_all_sinnoh() -> int:
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
    rebuild_twinleaf()
    reencode_water_all_sinnoh()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
