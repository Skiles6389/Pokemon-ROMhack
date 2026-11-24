#!/usr/bin/env python3
"""M42 remediator: fix stripped collision/elevation + unfinished tree halves.

Root cause:
  pack() historically wrote `mt & 0x3FF`, wiping Emerald collision (bits 10-11)
  and elevation (bits 12-15). The engine blocks movement from those bits, not
  metatile attributes — so tree/wall IDs looked solid in audits but were
  walk-through in-game. Tree solids were also parity-tiled per cell, producing
  orphan TL/TR/BL/BR halves.

This script:
  1) Re-encodes every Sinnoh LAND_TABLE map.bin with proper coll/elev
  2) Rebuilds tree solids into complete 2x2 Emerald trees (rocks for leftovers)
  3) Preserves building facade metatiles (>=0x200 secondary stamps)
  4) Optionally full-regenerates ground from Platinum attrs when --regen-plat
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    MT_GRASS,
    MT_ROCK,
    MT_TREE,
    MT_TREE_BL,
    MT_TREE_BR,
    MT_TREE_TL,
    MT_TREE_TR,
    encode_map_cell,
    grid_from_chunks,
    is_solid_metatile,
    pack,
    place_complete_trees,
)
from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402

LAYOUTS = REPO / "data" / "layouts"
LAYOUTS_JSON = json.loads((LAYOUTS / "layouts.json").read_text())["layouts"]
LAYOUT_BY_NAME = {L["name"].replace("_Layout", ""): L for L in LAYOUTS_JSON}

TREE_SET = set(MT_TREE)


def load_grid(path: Path, w: int, h: int) -> list[list[int]]:
    data = path.read_bytes()
    expect = w * h * 2
    if len(data) < expect:
        raise SystemExit(f"{path}: size {len(data)} < {expect}")
    grid = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            grid[y][x] = struct.unpack_from("<H", data, (y * w + x) * 2)[0]
    return grid


def write_grid(path: Path, grid: list[list[int]], collision=None) -> None:
    path.write_bytes(pack([[c & 0x3FF for c in row] for row in grid], collision))


def is_building(mt: int) -> bool:
    mt &= 0x3FF
    return mt >= 0x200 and mt not in (0x201, 0x209, 0x20E)  # floor / mat / door


def fix_trees_preserve_buildings(grid: list[list[int]]) -> tuple[list[list[int]], int]:
    """Replace incomplete tree neighborhoods; keep building stamps."""
    h, w = len(grid), len(grid[0])
    solid = [[False] * w for _ in range(h)]
    building = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            mt = grid[y][x] & 0x3FF
            if is_building(mt):
                building[y][x] = True
            elif mt in TREE_SET or mt == MT_ROCK or mt == 0x139:
                solid[y][x] = True

    new_trees = place_complete_trees(solid, cave=False, indoor=False)
    changed = 0
    out = [row[:] for row in grid]
    for y in range(h):
        for x in range(w):
            if building[y][x]:
                continue
            if solid[y][x]:
                new_mt = new_trees[y][x] & 0x3FF
                old_mt = out[y][x] & 0x3FF
                if new_mt != old_mt:
                    out[y][x] = new_mt
                    changed += 1
            elif (out[y][x] & 0x3FF) in TREE_SET:
                # Orphan tree on non-solid mask — shouldn't happen
                out[y][x] = MT_GRASS
                changed += 1
    return out, changed


def count_incomplete_trees(grid: list[list[int]]) -> int:
    h, w = len(grid), len(grid[0])
    incomplete = 0
    for y in range(h):
        for x in range(w):
            mt = grid[y][x] & 0x3FF
            if mt not in TREE_SET:
                continue
            # Find 2x2 origin
            ox, oy = x - (x & 1), y - (y & 1)
            if ox + 1 >= w or oy + 1 >= h:
                incomplete += 1
                continue
            cells = [
                grid[oy][ox] & 0x3FF,
                grid[oy][ox + 1] & 0x3FF,
                grid[oy + 1][ox] & 0x3FF,
                grid[oy + 1][ox + 1] & 0x3FF,
            ]
            if cells != [MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR]:
                incomplete += 1
    return incomplete


def stripped_ratio(path: Path) -> float:
    data = path.read_bytes()
    n = len(data) // 2
    if n == 0:
        return 0.0
    hi = sum(1 for i in range(n) if struct.unpack_from("<H", data, i * 2)[0] & 0xFC00)
    return 1.0 - hi / n


def is_outdoor_layout(meta: dict) -> bool:
    prim = meta.get("primary_tileset") or ""
    sec = meta.get("secondary_tileset") or ""
    if "Cave" in sec or "Building" in prim or "Facility" in sec:
        return False
    return True


def remediate_one(name: str, *, fix_trees: bool, regen_plat: bool) -> dict:
    meta = LAYOUT_BY_NAME.get(name)
    if not meta:
        return {"name": name, "status": "SKIP", "reason": "no layout"}
    path = REPO / meta["blockdata_filepath"]
    if not path.exists():
        return {"name": name, "status": "SKIP", "reason": "missing map.bin"}
    w, h = int(meta["width"]), int(meta["height"])
    before_strip = stripped_ratio(path)
    grid = load_grid(path, w, h)
    before_incomplete = count_incomplete_trees(grid)
    tree_changed = 0
    coll = None
    outdoor = is_outdoor_layout(meta)
    if fix_trees and not outdoor:
        fix_trees = False  # never rewrite cave/indoor solids into outdoor trees

    if regen_plat and name in LAND_TABLE and outdoor:
        chunks = LAND_TABLE[name]
        # Preserve building cells from current grid
        building_mask = [[is_building(grid[y][x]) for x in range(w)] for y in range(h)]
        building_cells = [[grid[y][x] & 0x3FF for x in range(w)] for y in range(h)]
        try:
            new_grid, gw, gh, coll = grid_from_chunks(chunks)
        except FileNotFoundError as e:
            return {"name": name, "status": "FAIL", "reason": str(e)}
        if gw != w or gh != h:
            # Size mismatch — only re-encode collision
            regen_plat = False
        else:
            for y in range(h):
                for x in range(w):
                    if building_mask[y][x]:
                        new_grid[y][x] = building_cells[y][x]
                        if coll is not None:
                            coll[y][x] = 1 if is_solid_metatile(building_cells[y][x]) else 0
            grid = new_grid
            tree_changed = -1  # full regen

    if fix_trees and tree_changed != -1:
        grid, tree_changed = fix_trees_preserve_buildings(grid)

    # Encode collision: prefer Platinum-derived coll if we have it; else infer
    write_grid(path, grid, coll)
    after_strip = stripped_ratio(path)
    after_incomplete = count_incomplete_trees(load_grid(path, w, h))
    return {
        "name": name,
        "status": "OK",
        "before_strip": round(before_strip, 3),
        "after_strip": round(after_strip, 3),
        "before_incomplete_trees": before_incomplete,
        "after_incomplete_trees": after_incomplete,
        "tree_cells_changed": tree_changed,
        "regen_plat": bool(regen_plat and name in LAND_TABLE),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fix-trees", action="store_true", default=True)
    ap.add_argument("--no-fix-trees", action="store_true")
    ap.add_argument("--regen-plat", action="store_true", help="Rebuild ground from Platinum attrs")
    ap.add_argument("--only", nargs="*", help="Subset of map names")
    ap.add_argument("--json-out", type=Path, default=REPO / "tools/sinnoh_maps/remediate_m42_report.json")
    args = ap.parse_args()
    fix_trees = not args.no_fix_trees
    names = args.only or sorted(LAND_TABLE.keys())
    results = []
    for name in names:
        r = remediate_one(name, fix_trees=fix_trees, regen_plat=args.regen_plat)
        results.append(r)
        print(
            f"{r['status']:4s} {name:32s} strip {r.get('before_strip','?'):>5}→{r.get('after_strip','?'):>5} "
            f"trees_incomplete {r.get('before_incomplete_trees','?'):>5}→{r.get('after_incomplete_trees','?'):>5} "
            f"chg={r.get('tree_cells_changed','?')}"
        )
    args.json_out.write_text(json.dumps({"results": results}, indent=2) + "\n")
    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"=== remediated {ok}/{len(results)} → {args.json_out} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
