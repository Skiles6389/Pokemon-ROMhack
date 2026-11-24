#!/usr/bin/env python3
"""Visual + object audits for Sinnoh outdoor maps.

Visual: incomplete Emerald 2x2 tree neighborhoods (orphaned halves).
Object: fence / ledge / sign bg-events or metatiles with no Platinum counterpart
        (ledge behavior 0x3B / rock 0x38-3A; fences are converter inventions).
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
    MT_TREE_BL,
    MT_TREE_BR,
    MT_TREE_TL,
    MT_TREE_TR,
    PLAT_DATA,
    load_attrs,
    plat_behavior,
    plat_collision,
)

LAYOUTS = REPO / "data" / "layouts"
MAPS = REPO / "data" / "maps"
LAYOUTS_JSON = {L["name"].replace("_Layout", ""): L for L in json.loads((LAYOUTS / "layouts.json").read_text())["layouts"]}
TREE = {MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR}
COMPLETE = [MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR]
LEDGE = {0x0D5, 0x0D6}
FENCE_LIKE = {0x00A, 0x00B, 0x00C}  # Emerald fence metatiles if ever used


def load_grid(name: str):
    meta = LAYOUTS_JSON[name]
    w, h = int(meta["width"]), int(meta["height"])
    data = (REPO / meta["blockdata_filepath"]).read_bytes()
    grid = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            grid[y][x] = struct.unpack_from("<H", data, (y * w + x) * 2)[0] & 0x3FF
    return grid, w, h


def incomplete_trees(grid) -> int:
    h, w = len(grid), len(grid[0])
    seen = set()
    bad = 0
    for y in range(h):
        for x in range(w):
            if grid[y][x] not in TREE:
                continue
            ox, oy = x - (x & 1), y - (y & 1)
            key = (ox, oy)
            if key in seen:
                continue
            seen.add(key)
            if ox + 1 >= w or oy + 1 >= h:
                bad += 1
                continue
            cells = [grid[oy][ox], grid[oy][ox + 1], grid[oy + 1][ox], grid[oy + 1][ox + 1]]
            if cells != COMPLETE:
                bad += 1
    return bad


def plat_ledge_count(chunks) -> int:
    n = 0
    for row in chunks:
        for lid in row:
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for v in attrs:
                if plat_behavior(v) == 0x3B:
                    n += 1
    return n


def audit_one(name: str) -> dict:
    if name not in LAYOUTS_JSON:
        return {"name": name, "status": "SKIP"}
    grid, w, h = load_grid(name)
    incomplete = incomplete_trees(grid)
    em_ledges = sum(1 for row in grid for mt in row if mt in LEDGE)
    em_fences = sum(1 for row in grid for mt in row if mt in FENCE_LIKE)

    plat_ledges = 0
    stray_ledges = 0
    chunks = LAND_TABLE.get(name)
    if chunks and PLAT_DATA.exists():
        try:
            plat_ledges = plat_ledge_count(chunks)
        except FileNotFoundError:
            plat_ledges = -1
        if plat_ledges >= 0 and em_ledges > plat_ledges + 16:
            stray_ledges = em_ledges - plat_ledges

    # Sign/bg events without platinum is soft — count map.json signs
    signs = 0
    mj = MAPS / name / "map.json"
    if mj.exists():
        data = json.loads(mj.read_text())
        for bg in data.get("bg_events") or []:
            if bg.get("type") == "sign":
                signs += 1

    issues = []
    status = "PASS"
    if incomplete > 0:
        issues.append(f"incomplete 2x2 trees: {incomplete}")
        status = "FAIL"
    if em_fences:
        issues.append(f"fence metatiles with no Platinum fence mapping: {em_fences}")
        status = "FAIL"
    if stray_ledges > 32:
        issues.append(f"extra ledge metatiles vs Platinum: +{stray_ledges}")
        if status == "PASS":
            status = "WARN"

    return {
        "name": name,
        "status": status,
        "incomplete_trees": incomplete,
        "em_ledges": em_ledges,
        "plat_ledges": plat_ledges,
        "em_fences": em_fences,
        "signs": signs,
        "issues": issues,
    }


def main() -> int:
    results = [audit_one(n) for n in sorted(LAND_TABLE)]
    fails = [r for r in results if r["status"] == "FAIL"]
    out = REPO / "tools/sinnoh_maps/visual_object_audit_report.json"
    out.write_text(json.dumps({"results": results, "fail": len(fails)}, indent=2) + "\n")
    for r in results:
        if r["status"] != "PASS":
            print(f"{r['status']:4s} {r['name']}: {'; '.join(r['issues'])}")
    print(f"=== visual/object audit: {len(fails)} FAIL / {len(results)} → {out} ===")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
