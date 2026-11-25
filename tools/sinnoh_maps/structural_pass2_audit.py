#!/usr/bin/env python3
"""Pass-2 focused audits: Platinum path coverage gaps, isolated rocks (hard),
wrong-facing ledges clustered, border tree incompleteness on connections.
"""
from __future__ import annotations

import argparse
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
    PLAT_DATA,
    WATER_METATILES,
    is_plat_path_behavior,
    load_attrs,
    map_allows_path_fallback,
    plat_behavior,
    plat_collision,
)
from tools.sinnoh_maps.structural_extra_audit import all_map_names, load_cells, walkable  # noqa: E402

LAYOUTS = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
}
CLIFF_ROCK = {MT_ROCK, 0x07C, 0x091, 0x139}
LEDGE = {0x0D5, 0x0D6}
TREE = set(MT_TREE)


def isolated_rocks(cells) -> int:
    h, w = len(cells), len(cells[0])
    n = 0
    for y in range(h):
        for x in range(w):
            if cells[y][x][0] not in CLIFF_ROCK:
                continue
            nbr = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and cells[ny][nx][0] in CLIFF_ROCK:
                    nbr += 1
            if nbr < 2:
                n += 1
    return n


def path_gap_vs_plat(name: str, cells) -> int | None:
    chunks = LAND_TABLE.get(name)
    if not chunks or not PLAT_DATA.exists() or not map_allows_path_fallback(name):
        return None
    em = sum(1 for row in cells for mt, _, _ in row if mt in PATH_METATILES)
    plat = 0
    try:
        for row in chunks:
            for lid in row:
                if lid is None:
                    continue
                for v in load_attrs(lid):
                    if plat_collision(v):
                        continue
                    if is_plat_path_behavior(plat_behavior(v)):
                        plat += 1
    except FileNotFoundError:
        return None
    if plat < 8:
        return None
    # Gap: Emerald covers < 20% of Platinum path cells
    if em < max(4, plat // 5):
        return plat - em
    return 0


def border_incomplete_trees(cells, w, h) -> int:
    """Tree tiles on map border that aren't complete 2x2."""
    expect = {MT_TREE[0]: (0, 0), MT_TREE[1]: (-1, 0), MT_TREE[2]: (0, -1), MT_TREE[3]: (-1, -1)}

    def complete(tlx, tly):
        if tlx < 0 or tly < 0 or tlx + 1 >= w or tly + 1 >= h:
            return False
        return (
            cells[tly][tlx][0] == MT_TREE[0]
            and cells[tly][tlx + 1][0] == MT_TREE[1]
            and cells[tly + 1][tlx][0] == MT_TREE[2]
            and cells[tly + 1][tlx + 1][0] == MT_TREE[3]
        )

    bad = 0
    for y in range(h):
        for x in range(w):
            if y not in (0, 1, h - 1, h - 2) and x not in (0, 1, w - 1, w - 2):
                continue
            mt = cells[y][x][0]
            if mt not in TREE:
                continue
            dx, dy = expect[mt]
            if not complete(x + dx, y + dy):
                bad += 1
    return bad


def audit_one(name: str) -> dict:
    if name not in LAYOUTS:
        return {"name": name, "status": "SKIP", "issues": []}
    cells, w, h, meta = load_cells(name)
    issues = []
    iso = isolated_rocks(cells)
    # Towns/cities only — routes/caves use sparse rock scatter by design
    settlement = (
        name.endswith("Town") or name.endswith("City") or name.endswith("Area")
        or name == "PokemonLeague_Exterior"
    )
    if settlement and iso > 8:
        issues.append(f"isolated rocks: {iso}")
    gap = path_gap_vs_plat(name, cells) if name in LAND_TABLE else None
    if gap and gap > 0:
        issues.append(f"Platinum path gap: missing ~{gap} path cells")
    if name in LAND_TABLE:
        border_trees = border_incomplete_trees(cells, w, h)
        if border_trees > 8:
            issues.append(f"border incomplete trees: {border_trees}")
    # Ledge without south-jump approach (stricter than pass1)
    bad_ledge = 0
    for y in range(h):
        for x in range(w):
            mt = cells[y][x][0]
            if mt == 0x0D5 and (y == 0 or not walkable(*cells[y - 1][x][:2])):
                bad_ledge += 1
    if bad_ledge:
        issues.append(f"south-ledge no approach: {bad_ledge}")
    status = "FAIL" if issues else "PASS"
    return {"name": name, "status": status, "issues": issues}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "tools/sinnoh_maps/structural_pass2_audit_report.json")
    args = ap.parse_args()
    names = [n for n in all_map_names() if n in LAYOUTS]
    results = [audit_one(n) for n in names]
    fail = sum(1 for r in results if r["status"] == "FAIL")
    passed = sum(1 for r in results if r["status"] == "PASS")
    for r in results:
        if r["status"] == "FAIL":
            print(f"FAIL {r['name']}: {'; '.join(r['issues'])}")
    out = {"fail": fail, "pass": passed, "results": results}
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"=== structural_pass2_audit: {fail} FAIL / {passed} PASS → {args.out} ===")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
