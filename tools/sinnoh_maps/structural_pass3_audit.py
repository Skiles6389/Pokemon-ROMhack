#!/usr/bin/env python3
"""Pass-3 audit: interior stubs still fully open; item access; indoor door warps."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.structural_extra_audit import (  # noqa: E402
    LAYOUTS,
    all_map_names,
    audit_inaccessible_items,
    audit_interior_walls,
    is_indoor,
    load_cells,
    walkable,
)

MAPS = REPO / "data/maps"


def audit_indoor_warps(name, cells, w, h) -> list[str]:
    mj = MAPS / name / "map.json"
    if not mj.exists():
        return []
    bad = 0
    for wp in json.loads(mj.read_text()).get("warp_events") or []:
        x, y = int(wp["x"]), int(wp["y"])
        if not (0 <= x < w and 0 <= y < h):
            bad += 1
            continue
        # Need walkable self or neighbor
        ok = any(
            0 <= x + dx < w and 0 <= y + dy < h and walkable(*cells[y + dy][x + dx][:2])
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
        )
        if not ok:
            bad += 1
    if bad:
        return [f"indoor warps blocked: {bad}"]
    return []


def audit_one(name: str) -> dict:
    if name not in LAYOUTS:
        return {"name": name, "status": "SKIP", "issues": []}
    cells, w, h, meta = load_cells(name)
    issues = []
    if is_indoor(meta, name):
        issues += audit_interior_walls(cells, w, h, meta, name)
        issues += audit_indoor_warps(name, cells, w, h)
    issues += audit_inaccessible_items(name, cells, w, h)
    return {"name": name, "status": "FAIL" if issues else "PASS", "issues": issues}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "tools/sinnoh_maps/structural_pass3_audit_report.json")
    args = ap.parse_args()
    results = [audit_one(n) for n in all_map_names() if n in LAYOUTS]
    fail = sum(1 for r in results if r["status"] == "FAIL")
    passed = sum(1 for r in results if r["status"] == "PASS")
    for r in results:
        if r["status"] == "FAIL":
            print(f"FAIL {r['name']}: {'; '.join(r['issues'])}")
    args.out.write_text(json.dumps({"fail": fail, "pass": passed, "results": results}, indent=2) + "\n")
    print(f"=== structural_pass3_audit: {fail} FAIL / {passed} PASS → {args.out} ===")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
