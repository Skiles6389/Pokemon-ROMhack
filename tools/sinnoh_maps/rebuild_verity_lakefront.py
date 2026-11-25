#!/usr/bin/env python3
"""Rebuild VerityLakefront as a dense Emerald forest approach (Platinum-style).

Layout (32×18, General + Petalburg):
  - Dense 2×2 trees everywhere
  - East: 3-tile grass path from Route201 into a ~12×5 clearing (middle-left)
  - North side of clearing (west end): 2-tile forest GAP (not a cave) with warps
  - Sign + sand tile just right/below the gap
  - East clearing: fenced flower patch (fence W+S) + white flowers + lone trees
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
W, H = 32, 18

MT_GRASS, MT_TALL = 0x001, 0x00D
MT_FLOWER = 0x004  # pink/white flower bed (General)
MT_SHRUB = 0x00E
MT_SIGN = 0x003
MT_SAND = 0x121
MT_PATH = 0x1D9
MT_TREE = (0x1D4, 0x1D5, 0x1DC, 0x1DD)  # TL TR BL BR
# Brown rock ledge (General) — west/south border of the flower patch
LEDGE = 0x079


def cell(mt: int, coll: int, elev: int = 3) -> int:
    return (mt & 0x3FF) | ((coll & 3) << 10) | ((elev & 0xF) << 12)


def setc(grid, x, y, mt, coll, elev=3):
    if 0 <= x < W and 0 <= y < H:
        grid[y][x] = cell(mt, coll, elev)


def tree_quad(grid, tx, ty):
    if tx < 0 or ty < 0 or tx + 1 >= W or ty + 1 >= H:
        return
    setc(grid, tx, ty, MT_TREE[0], 1)
    setc(grid, tx + 1, ty, MT_TREE[1], 1)
    setc(grid, tx, ty + 1, MT_TREE[2], 1)
    setc(grid, tx + 1, ty + 1, MT_TREE[3], 1)


def is_tree(v: int) -> bool:
    return (v & 0x3FF) in MT_TREE


def main() -> None:
    # Start as solid tree cover on even grid
    grid = [[cell(MT_GRASS, 0) for _ in range(W)] for _ in range(H)]
    for y in range(0, H - 1, 2):
        for x in range(0, W - 1, 2):
            tree_quad(grid, x, y)

    # --- Walkable carve ---
    # East approach path: 3 tiles tall (y=10,11,12), x=16..31
    PATH_Y = (10, 11, 12)
    for y in PATH_Y:
        for x in range(16, W):
            setc(grid, x, y, MT_GRASS, 0)

    # Clearing ~12×5 at middle-left: x=4..15, y=8..12
    CLR_X0, CLR_X1 = 4, 15
    CLR_Y0, CLR_Y1 = 8, 12
    for y in range(CLR_Y0, CLR_Y1 + 1):
        for x in range(CLR_X0, CLR_X1 + 1):
            setc(grid, x, y, MT_GRASS, 0)

    # Connect path into clearing (x=16 already open; ensure x=14-15 open)
    for y in PATH_Y:
        for x in range(14, 17):
            setc(grid, x, y, MT_GRASS, 0)

    # North forest GAP (2 tiles) at west end of clearing — shaded tall grass, NOT cave.
    # Gap sits in the tree line just above the clearing: (5,6)/(6,6) and (5,7)/(6,7).
    GAP = [(5, 6), (6, 6), (5, 7), (6, 7)]
    for x, y in GAP:
        setc(grid, x, y, MT_TALL, 0)  # shaded opening

    # Warp stand tiles just south of the dark gap (return landing).
    WARP = [(5, 8), (6, 8)]
    for x, y in WARP:
        setc(grid, x, y, MT_GRASS, 0)

    # One sandy/dirt tile + sign just right/below the gap
    setc(grid, 7, 8, MT_SAND, 0)
    setc(grid, 8, 8, MT_SIGN, 1)  # signpost (solid)

    # Flower tufts on clearing grass
    for x, y in [(7, 10), (9, 9), (10, 12), (12, 10), (5, 11), (13, 9)]:
        setc(grid, x, y, MT_FLOWER, 0)

    # East-half raised flower patch: interior x=11..14, y=9..11
    # Brown ledge on west (x=10) and south (y=12) sides
    for y in range(9, 12):
        setc(grid, 10, y, LEDGE, 1)
    for x in range(10, 15):
        setc(grid, x, 12, LEDGE, 1)
    # Interior flowers + grass
    for y in range(9, 12):
        for x in range(11, 15):
            setc(grid, x, y, MT_FLOWER if (x + y) % 2 == 0 else MT_GRASS, 0)
    # A couple of lone trees inside clearing on the right (must be 2×2 aligned)
    tree_quad(grid, 14, 8)  # top-right of clearing — overlays corner
    # Re-open path tiles that tree may have blocked on the approach
    for y in PATH_Y:
        for x in range(16, W):
            setc(grid, x, y, MT_GRASS, 0)
    # Keep clearing walkable around the lone tree; second lone tree further right edge of clear
    # Place smaller shrub accents instead of second full tree if space tight
    setc(grid, 13, 11, MT_SHRUB, 0)

    # Ensure east edge connection rows stay open (Route201 offset 11 → y=3,4,7,9..12)
    for y in (3, 4, 7, 9, 10, 11, 12):
        for x in range(28, W):
            # only open if we're on/near the path band; keep forest above/below dense
            if y in PATH_Y or y in (9,):
                setc(grid, x, y, MT_GRASS, 0)
    # Force full east path band
    for y in PATH_Y:
        for x in range(16, W):
            setc(grid, x, y, MT_GRASS, 0)

    # Re-plant dense trees above gap (y=0..5) except the gap column
    for y in range(0, 6, 2):
        for x in range(0, W - 1, 2):
            if x in (4, 6) and y >= 4:
                continue  # leave gap columns
            tree_quad(grid, x, y)
    # Punch gap again after re-plant
    for x, y in GAP:
        setc(grid, x, y, MT_TALL, 0)
    for x, y in WARP:
        setc(grid, x, y, MT_GRASS, 0)
    setc(grid, 7, 8, MT_SAND, 0)
    setc(grid, 8, 8, MT_SIGN, 1)

    # Dense trees south of path
    for y in range(14, H - 1, 2):
        for x in range(0, W - 1, 2):
            tree_quad(grid, x, y)

    # Dense trees west of clearing
    for y in range(8, 14, 2):
        for x in range(0, 4, 2):
            tree_quad(grid, x, y)

    # Write map.bin
    out = REPO / "data/layouts/VerityLakefront/map.bin"
    buf = bytearray()
    for y in range(H):
        for x in range(W):
            buf += struct.pack("<H", grid[y][x])
    out.write_bytes(buf)

    # Update layouts.json dimensions
    layouts_path = REPO / "data/layouts/layouts.json"
    layouts = json.loads(layouts_path.read_text())
    for L in layouts["layouts"]:
        if L["id"] == "LAYOUT_VERITY_LAKEFRONT":
            L["width"] = W
            L["height"] = H
            L["primary_tileset"] = "gTileset_General"
            L["secondary_tileset"] = "gTileset_Petalburg"
            break
    layouts_path.write_text(json.dumps(layouts, indent=2) + "\n")

    # Update map.json warps + sign
    mj_path = REPO / "data/maps/VerityLakefront/map.json"
    meta = json.loads(mj_path.read_text())
    meta["warp_events"] = [
        {
            "x": 5,
            "y": 8,
            "elevation": 0,
            "dest_map": "MAP_LAKE_VERITY",
            "dest_warp_id": "0",
        },
        {
            "x": 6,
            "y": 8,
            "elevation": 0,
            "dest_map": "MAP_LAKE_VERITY",
            "dest_warp_id": "1",
        },
    ]
    meta["bg_events"] = [
        {
            "type": "sign",
            "x": 8,
            "y": 8,
            "elevation": 0,
            "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
            "script": "VerityLakefront_EventScript_Sign",
        }
    ]
    # Keep east connection to Route201; offset -11 pairs with Route201 left offset 11
    # (R201 y=22 → VL y=11 on the path band)
    meta["connections"] = [
        {"map": "MAP_ROUTE201", "offset": -11, "direction": "right"}
    ]
    mj_path.write_text(json.dumps(meta, indent=2) + "\n")

    # Dump collision preview
    def coll(v):
        return (v >> 10) & 3

    def mt(v):
        return v & 0x3FF

    print(f"wrote {out} ({W}x{H})")
    for y in range(H):
        row = []
        for x in range(W):
            v = grid[y][x]
            m = mt(v)
            if m in MT_TREE:
                row.append("#")
            elif m in (LEDGE, MT_SIGN):
                row.append("=")
            elif m == MT_TALL:
                row.append("~")
            elif m == MT_FLOWER:
                row.append("*")
            elif m == MT_SAND or m == MT_PATH:
                row.append(":")
            elif coll(v) == 0:
                row.append(".")
            else:
                row.append("X")
        print(f"y{y:02d}: {''.join(row)}")
    print("warps", WARP, "gap", GAP)


if __name__ == "__main__":
    main()
