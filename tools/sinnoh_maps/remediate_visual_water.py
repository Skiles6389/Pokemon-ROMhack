#!/usr/bin/env python3
"""Fix passable water, incomplete trees, and isolated rocks across Sinnoh maps.

Priority early-game maps get a fuller tree repair pass. Water elev is re-packed
to vanilla Emerald (coll=0, elev=1) everywhere.
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
    MT_GRASS,
    MT_ROCK,
    MT_TREE,
    WATER_METATILES,
    encode_map_cell,
)

LAYOUTS_JSON = json.loads((LAYOUTS / "layouts.json").read_text())["layouts"]
PRIORITY = {
    "TwinleafTown", "Route201", "SandgemTown", "Route202", "JubilifeCity",
    "Route203", "OreburghCity", "OreburghMine_B1F", "OreburghMine_B2F",
}
TREE = set(MT_TREE)
TREE_EXPECT = {MT_TREE[0]: (0, 0), MT_TREE[1]: (-1, 0), MT_TREE[2]: (0, -1), MT_TREE[3]: (-1, -1)}
CLIFF = {MT_ROCK, 0x07C, 0x091, 0x139}


def layout_meta(name: str):
    for L in LAYOUTS_JSON:
        if L["name"].replace("_Layout", "") == name or name in L["name"]:
            return L
    return None


def load(name: str):
    meta = layout_meta(name)
    if not meta:
        return None
    path = REPO / meta["blockdata_filepath"]
    if not path.exists():
        return None
    w, h = int(meta["width"]), int(meta["height"])
    raw = bytearray(path.read_bytes())
    return meta, path, raw, w, h


def get_cell(raw, w, x, y):
    return struct.unpack_from("<H", raw, (y * w + x) * 2)[0]


def set_cell(raw, w, x, y, cell):
    struct.pack_into("<H", raw, (y * w + x) * 2, cell)


def mt_of(cell):
    return cell & 0x3FF


def repair_water(raw, w, h) -> int:
    n = 0
    for y in range(h):
        for x in range(w):
            cell = get_cell(raw, w, x, y)
            mt = mt_of(cell)
            if mt not in WATER_METATILES:
                continue
            new = encode_map_cell(mt, collision=0)
            if new != cell:
                set_cell(raw, w, x, y, new)
                n += 1
    return n


def is_complete_tree(raw, w, h, tlx, tly) -> bool:
    if tlx < 0 or tly < 0 or tlx + 1 >= w or tly + 1 >= h:
        return False
    return (
        mt_of(get_cell(raw, w, tlx, tly)) == MT_TREE[0]
        and mt_of(get_cell(raw, w, tlx + 1, tly)) == MT_TREE[1]
        and mt_of(get_cell(raw, w, tlx, tly + 1)) == MT_TREE[2]
        and mt_of(get_cell(raw, w, tlx + 1, tly + 1)) == MT_TREE[3]
    )


def repair_trees(raw, w, h) -> int:
    n = 0
    for y in range(h):
        for x in range(w):
            mt = mt_of(get_cell(raw, w, x, y))
            if mt not in TREE:
                continue
            dx, dy = TREE_EXPECT[mt]
            if is_complete_tree(raw, w, h, x + dx, y + dy):
                continue
            set_cell(raw, w, x, y, encode_map_cell(MT_GRASS, collision=0))
            n += 1
    return n


def repair_isolated_rocks(raw, w, h, *, aggressive: bool, min_neighbors: int = 2) -> int:
    """Convert sparse rocks to grass. Keep only clusters with ≥min_neighbors links."""
    n = 0
    # Multi-pass: removing rocks can isolate neighbors
    for _ in range(6 if aggressive else 2):
        rocks = []
        for y in range(h):
            for x in range(w):
                if mt_of(get_cell(raw, w, x, y)) in CLIFF:
                    rocks.append((x, y))
        removed = 0
        for x, y in rocks:
            neigh = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and mt_of(get_cell(raw, w, nx, ny)) in CLIFF:
                    neigh += 1
            if neigh < min_neighbors:
                set_cell(raw, w, x, y, encode_map_cell(MT_GRASS, collision=0))
                removed += 1
        n += removed
        if removed == 0:
            break
    return n


def remediate(name: str) -> dict:
    loaded = load(name)
    if not loaded:
        return {"name": name, "status": "SKIP"}
    meta, path, raw, w, h = loaded
    water = repair_water(raw, w, h)
    trees = repair_trees(raw, w, h)
    # Strip sparse rock leftovers (tree-ring orphans). Keep only contiguous cliffs.
    rocks = repair_isolated_rocks(
        raw, w, h, aggressive=True, min_neighbors=3 if name in PRIORITY else 2
    )
    path.write_bytes(bytes(raw))
    return {
        "name": name,
        "status": "OK",
        "water_fixed": water,
        "trees_fixed": trees,
        "rocks_fixed": rocks,
    }


def main() -> int:
    # Priority first, then the rest
    names = [n for n in PRIORITY if n in LAND_TABLE] + [
        n for n in sorted(LAND_TABLE) if n not in PRIORITY
    ]
    results = [remediate(n) for n in names]
    out = REPO / "tools/sinnoh_maps/remediate_visual_water_report.json"
    out.write_text(json.dumps({"results": results}, indent=2) + "\n")
    tw = sum(r.get("water_fixed", 0) for r in results)
    tt = sum(r.get("trees_fixed", 0) for r in results)
    tr = sum(r.get("rocks_fixed", 0) for r in results)
    print(f"remediated water={tw} orphan_trees={tt} isolated_rocks={tr} → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
