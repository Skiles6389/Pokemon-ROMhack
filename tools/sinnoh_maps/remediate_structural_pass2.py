#!/usr/bin/env python3
"""Pass-2 remediations: isolated rocks→grass, border tree repair, path paint, bad ledges."""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    MT_GRASS,
    MT_ROCK,
    MT_TREE,
    PATH_METATILES,
    WATER_METATILES,
    pack,
    paint_paths_from_attrs,
    path_metatile_for_neighbors,
    grid_from_chunks,
    load_attrs,
)
from tools.sinnoh_maps.structural_extra_audit import LAYOUTS, walkable  # noqa: E402
from tools.sinnoh_maps.remediate_structural_pass1 import load, save, fix_trees  # noqa: E402

CLIFF_ROCK = {MT_ROCK, 0x07C, 0x091, 0x139}


def clear_isolated_rocks(grid, coll):
    h, w = len(grid), len(grid[0])
    n = 0
    for y in range(h):
        for x in range(w):
            if grid[y][x] not in CLIFF_ROCK:
                continue
            nbr = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in CLIFF_ROCK:
                    nbr += 1
            if nbr < 2:
                grid[y][x] = MT_GRASS
                coll[y][x] = 0
                n += 1
    return n


def clear_bad_ledges(grid, coll):
    h, w = len(grid), len(grid[0])
    n = 0
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt == 0x0D5 and (y == 0 or not walkable(grid[y - 1][x], coll[y - 1][x])):
                grid[y][x] = MT_GRASS
                coll[y][x] = 0
                n += 1
            elif mt == 0x0D6 and (y + 1 >= h or not walkable(grid[y + 1][x], coll[y + 1][x])):
                grid[y][x] = MT_GRASS
                coll[y][x] = 0
                n += 1
    return n


def paint_missing_paths(name, grid, coll):
    if name not in LAND_TABLE:
        return 0
    chunks = LAND_TABLE[name]
    try:
        # Rebuild path overlay from attrs without wiping buildings
        h, w = len(grid), len(grid[0])
        attrs = [[0] * w for _ in range(h)]
        for cy, row in enumerate(chunks):
            for cx, lid in enumerate(row):
                if lid is None:
                    continue
                a = load_attrs(lid)
                for ly in range(32):
                    for lx in range(32):
                        attrs[cy * 32 + ly][cx * 32 + lx] = a[ly * 32 + lx]
        before = sum(1 for row in grid for mt in row if mt in PATH_METATILES)
        # Only paint onto grass
        tmp = [row[:] for row in grid]
        paint_paths_from_attrs(tmp, attrs, map_name=name)
        n = 0
        for y in range(h):
            for x in range(w):
                if tmp[y][x] in PATH_METATILES and grid[y][x] in (MT_GRASS, 0x001, 0x00D):
                    grid[y][x] = tmp[y][x]
                    coll[y][x] = 0
                    n += 1
        return n
    except Exception as e:
        print(f"  path paint skip {name}: {e}")
        return 0


def main() -> int:
    total = {"rocks": 0, "ledges": 0, "trees": 0, "paths": 0}
    # Towns/cities only for rock clear — routes keep sparse cliff scatter
    targets = [
        n for n in LAND_TABLE
        if n.endswith("Town") or n.endswith("City") or n.endswith("Area")
        or n == "PokemonLeague_Exterior"
    ]
    for name in sorted(set(list(LAND_TABLE))):
        if name not in LAYOUTS:
            continue
        grid, coll, elev, w, h, meta = load(name)
        r = clear_isolated_rocks(grid, coll) if name in targets else 0
        l = clear_bad_ledges(grid, coll)
        t = fix_trees(grid, coll)
        # Skip mass path paint (over-paints paved/town maps)
        p = 0
        if r or l or t or p:
            save(grid, coll, elev, meta)
            print(f"{name}: rocks={r} ledges={l} trees={t} paths={p}")
            total["rocks"] += r
            total["ledges"] += l
            total["trees"] += t
            total["paths"] += p
    print(f"=== remediate_structural_pass2: {total} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
