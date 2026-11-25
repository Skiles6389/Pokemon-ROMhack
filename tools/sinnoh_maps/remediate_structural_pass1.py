#!/usr/bin/env python3
"""Pass-1 structural remediations for known audit FAILs.

- Door mats (0x201) walkable (coll=0)
- Building facade tiles impassable (coll=1)
- Nudge double-door warps onto primary door metatile
- Move meadow/route field warps off building walls onto grass
- Incomplete 2x2 tree repair (via remediate_visual_water logic)
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
    MT_GRASS,
    MT_TREE,
    WATER_METATILES,
    is_solid_metatile,
    pack,
)

LAYOUTS = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
}
MAPS = REPO / "data/maps"
DOOR_MAT = 0x201
DOOR_PRIMARY = {0x061, 0x041, 0x22F, 0x248, 0x287, 0x1CD}
DOOR_LEFT = {0x060, 0x266}
TREE = set(MT_TREE)
TREE_EXPECT = {MT_TREE[0]: (0, 0), MT_TREE[1]: (-1, 0), MT_TREE[2]: (0, -1), MT_TREE[3]: (-1, -1)}


def load(name):
    meta = LAYOUTS[name]
    w, h = int(meta["width"]), int(meta["height"])
    path = REPO / meta["blockdata_filepath"]
    data = bytearray(path.read_bytes())
    grid = [[struct.unpack_from("<H", data, (y * w + x) * 2)[0] & 0x3FF for x in range(w)] for y in range(h)]
    coll = [[(struct.unpack_from("<H", data, (y * w + x) * 2)[0] >> 10) & 3 for x in range(w)] for y in range(h)]
    elev = [[(struct.unpack_from("<H", data, (y * w + x) * 2)[0] >> 12) & 0xF for x in range(w)] for y in range(h)]
    return grid, coll, elev, w, h, meta


def save(grid, coll, elev, meta):
    # pack() uses coll grid + default elev; for water elev=1 we set after
    blob = pack(grid, coll)
    # Fix water elev to 1
    w, h = len(grid[0]), len(grid)
    data = bytearray(blob)
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            c = coll[y][x]
            e = 1 if mt in WATER_METATILES else (elev[y][x] if elev[y][x] else 3)
            if c == 0 and e == 0:
                e = 3
            raw = (mt & 0x3FF) | ((c & 3) << 10) | ((e & 0xF) << 12)
            struct.pack_into("<H", data, (y * w + x) * 2, raw)
    (REPO / meta["blockdata_filepath"]).write_bytes(bytes(data))


# Walkable secondary tiles (pave / plaza / mats / flowers) — never force coll=1
WALKABLE_SECONDARY = {
    DOOR_MAT, 0x2BB, 0x2C3, 0x2C4, 0x2BD,  # Rustboro pave/plaza
    0x00D, 0x001, 0x003, 0x004,  # grass / mailbox / flowers
}


def fix_collision(grid, coll, elev):
    h, w = len(grid), len(grid[0])
    n = 0
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt in WALKABLE_SECONDARY or mt in (0x2BB, 0x2C3):
                if coll[y][x] != 0:
                    coll[y][x] = 0
                    n += 1
                if elev[y][x] == 0:
                    elev[y][x] = 3
            elif mt == DOOR_MAT:
                if coll[y][x] != 0:
                    coll[y][x] = 0
                    n += 1
                elev[y][x] = 3
            elif mt in WATER_METATILES:
                coll[y][x] = 0
                elev[y][x] = 1
            elif mt in TREE or (0x028 <= mt <= 0x063) or (
                mt >= 0x200 and mt not in WALKABLE_SECONDARY and mt not in DOOR_PRIMARY
            ) or (is_solid_metatile(mt) and mt < 0x200):
                # Building facades / trees / PC-Mart body — impassable
                # Keep door tiles as-is (engine treats them enterable)
                if mt not in DOOR_PRIMARY:
                    if coll[y][x] == 0:
                        coll[y][x] = 1
                        n += 1
            elif coll[y][x] == 0 and elev[y][x] == 0:
                elev[y][x] = 3
                n += 1
    return n


def fix_trees(grid, coll):
    h, w = len(grid), len(grid[0])

    def complete(tlx, tly):
        if tlx < 0 or tly < 0 or tlx + 1 >= w or tly + 1 >= h:
            return False
        return (
            grid[tly][tlx] == MT_TREE[0]
            and grid[tly][tlx + 1] == MT_TREE[1]
            and grid[tly + 1][tlx] == MT_TREE[2]
            and grid[tly + 1][tlx + 1] == MT_TREE[3]
        )

    fixed = 0
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt not in TREE:
                continue
            dx, dy = TREE_EXPECT[mt]
            if not complete(x + dx, y + dy):
                grid[y][x] = MT_GRASS
                coll[y][x] = 0
                fixed += 1
    return fixed


def nudge_warps(name):
    mj_path = MAPS / name / "map.json"
    if not mj_path.exists() or name not in LAYOUTS:
        return 0
    grid, coll, elev, w, h, meta = load(name)
    mj = json.loads(mj_path.read_text())
    warps = mj.get("warp_events") or []
    changed = 0
    for wp in warps:
        dest = wp.get("dest_map") or ""
        x, y = int(wp["x"]), int(wp["y"])
        if not (0 <= x < w and 0 <= y < h):
            continue
        mt = grid[y][x]
        # Double-door: move left-half onto primary
        if mt in DOOR_LEFT or mt in (0x062, 0x042):
            for nx in (x + 1, x - 1, x + 2):
                if 0 <= nx < w and grid[y][nx] in DOOR_PRIMARY:
                    wp["x"] = nx
                    changed += 1
                    break
        # Field warps (meadow/route) on building walls → move south onto grass
        if any(k in dest for k in ("MEADOW", "ROUTE", "LAKEFRONT")) and (
            mt >= 0x200 or is_solid_metatile(mt)
        ):
            for ny in range(y + 1, min(h, y + 6)):
                if grid[ny][x] in (MT_GRASS, 0x001, 0x00D) or coll[ny][x] == 0 and grid[ny][x] < 0x028:
                    if grid[ny][x] not in TREE and grid[ny][x] not in WATER_METATILES:
                        wp["y"] = ny
                        # Ensure walkable
                        if grid[ny][x] >= 0x200:
                            grid[ny][x] = MT_GRASS
                        coll[ny][x] = 0
                        changed += 1
                        break
    if changed:
        mj["warp_events"] = warps
        mj_path.write_text(json.dumps(mj, indent=2) + "\n")
        save(grid, coll, elev, meta)
    return changed


def main() -> int:
    total_coll = total_trees = total_warps = 0
    for name in sorted(LAND_TABLE):
        if name not in LAYOUTS:
            continue
        grid, coll, elev, w, h, meta = load(name)
        n = fix_collision(grid, coll, elev)
        t = fix_trees(grid, coll)
        if n or t:
            save(grid, coll, elev, meta)
            total_coll += n
            total_trees += t
            print(f"{name}: coll_fixes={n} tree_fixes={t}")
        wfix = nudge_warps(name)
        if wfix:
            total_warps += wfix
            print(f"{name}: warp_nudges={wfix}")
    # Also rebuild Jubilife/Twinleaf for door-mat coll after stamp
    print(f"=== remediate_structural_pass1: coll={total_coll} trees={total_trees} warps={total_warps} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
