#!/usr/bin/env python3
"""Pass-3: stub interior wall frames + inaccessible item neighbor clears."""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.structural_extra_audit import (  # noqa: E402
    LAYOUTS,
    all_map_names,
    is_indoor,
    load_cells,
    walkable,
)
from tools.sinnoh_maps.sinnoh_build_lib import pack, is_solid_metatile  # noqa: E402

# Simple indoor wall/floor from Emerald Building tileset (generic)
WALL = 0x01B  # common indoor wall
FLOOR = 0x001  # or building floor 0x20E style — use 0x279 if present; keep 0x20E
DOOR = 0x20E  # indoor door mat-ish


def paint_stub_walls(name: str) -> int:
    if name not in LAYOUTS:
        return 0
    meta = LAYOUTS[name]
    if not is_indoor(meta, name):
        return 0
    cells, w, h, _ = load_cells(name)
    solid = sum(1 for row in cells for mt, coll, _ in row if coll != 0 or is_solid_metatile(mt))
    # Only paint fully-open stubs
    border_open = 0
    border_total = 0
    for x in range(w):
        for y in (0, h - 1):
            border_total += 1
            if walkable(*cells[y][x][:2]):
                border_open += 1
    for y in range(1, h - 1):
        for x in (0, w - 1):
            border_total += 1
            if walkable(*cells[y][x][:2]):
                border_open += 1
    if not border_total or border_open < border_total:
        return 0  # already has some walls / not stub
    if solid > max(8, w * h // 10):
        return 0

    grid = [[mt for mt, _, _ in row] for row in cells]
    coll = [[c for _, c, _ in row] for row in cells]
    # Floor fill + wall ring
    for y in range(h):
        for x in range(w):
            grid[y][x] = FLOOR
            coll[y][x] = 0
    for x in range(w):
        grid[0][x] = WALL
        coll[0][x] = 1
        grid[h - 1][x] = WALL
        coll[h - 1][x] = 1
    for y in range(h):
        grid[y][0] = WALL
        coll[y][0] = 1
        grid[y][w - 1] = WALL
        coll[y][w - 1] = 1
    # Door gap at bottom center
    dx = w // 2
    grid[h - 1][dx] = DOOR
    coll[h - 1][dx] = 0
    if h > 2:
        grid[h - 2][dx] = FLOOR
        coll[h - 2][dx] = 0
    (REPO / meta["blockdata_filepath"]).write_bytes(pack(grid, coll))
    return 1


def fix_items(name: str) -> int:
    mj_path = REPO / "data/maps" / name / "map.json"
    if not mj_path.exists() or name not in LAYOUTS:
        return 0
    cells, w, h, meta = load_cells(name)
    grid = [[mt for mt, _, _ in row] for row in cells]
    coll = [[c for _, c, _ in row] for row in cells]
    mj = json.loads(mj_path.read_text())
    n = 0
    for bg in mj.get("bg_events") or []:
        typ = bg.get("type") or ""
        if typ not in ("sign", "hidden_item") and "item" not in typ:
            continue
        x, y = int(bg["x"]), int(bg["y"])
        ok = any(
            0 <= x + dx < w and 0 <= y + dy < h and walkable(grid[y + dy][x + dx], coll[y + dy][x + dx])
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
        )
        if not ok and 0 <= x < w and 0 <= y < h:
            for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    grid[ny][nx] = FLOOR
                    coll[ny][nx] = 0
                    n += 1
                    break
    for obj in mj.get("object_events") or []:
        if "ITEM_BALL" not in (obj.get("graphics_id") or ""):
            continue
        x, y = int(obj["x"]), int(obj["y"])
        ok = any(
            0 <= x + dx < w and 0 <= y + dy < h and walkable(grid[y + dy][x + dx], coll[y + dy][x + dx])
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
        )
        if not ok:
            ny = min(h - 1, y + 1)
            if 0 <= x < w:
                grid[ny][x] = FLOOR
                coll[ny][x] = 0
                n += 1
    if n:
        (REPO / meta["blockdata_filepath"]).write_bytes(pack(grid, coll))
    return n


def main() -> int:
    walls = items = 0
    for name in all_map_names():
        walls += paint_stub_walls(name)
        items += fix_items(name)
    print(f"=== remediate_structural_pass3: stub_walls={walls} item_clears={items} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
