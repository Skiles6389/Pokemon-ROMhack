#!/usr/bin/env python3
"""Pass-4: NPCs blocking single-tile corridors; connection reverse mismatches."""
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
    audit_connection_seams,
    audit_npc_on_warps,
    load_cells,
    walkable,
)

MAPS = REPO / "data/maps"


def npc_blocks_corridor(name, cells, w, h) -> list[str]:
    mj = MAPS / name / "map.json"
    if not mj.exists():
        return []
    data = json.loads(mj.read_text())
    blocked = 0
    for obj in data.get("object_events") or []:
        x, y = int(obj["x"]), int(obj["y"])
        mov = obj.get("movement_type") or ""
        if "FACE" not in mov:
            continue
        if not (0 <= x < w and 0 <= y < h):
            continue
        # Corridor: walkable N-S or E-W but sides blocked
        def W(xx, yy):
            return 0 <= xx < w and 0 <= yy < h and walkable(*cells[yy][xx][:2])

        ns = W(x, y - 1) and W(x, y + 1) and not W(x - 1, y) and not W(x + 1, y)
        ew = W(x - 1, y) and W(x + 1, y) and not W(x, y - 1) and not W(x, y + 1)
        if ns or ew:
            blocked += 1
    if blocked:
        return [f"stationary NPCs in single-tile corridors: {blocked}"]
    return []


def audit_one(name: str) -> dict:
    if name not in LAYOUTS:
        return {"name": name, "status": "SKIP", "issues": []}
    cells, w, h, meta = load_cells(name)
    issues = []
    issues += audit_npc_on_warps(name, cells, w, h)
    issues += npc_blocks_corridor(name, cells, w, h)
    issues += audit_connection_seams(name, cells, w, h)
    return {"name": name, "status": "FAIL" if issues else "PASS", "issues": issues}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "tools/sinnoh_maps/structural_pass4_audit_report.json")
    args = ap.parse_args()
    results = [audit_one(n) for n in all_map_names() if n in LAYOUTS]
    fail = sum(1 for r in results if r["status"] == "FAIL")
    passed = sum(1 for r in results if r["status"] == "PASS")
    for r in results:
        if r["status"] == "FAIL":
            print(f"FAIL {r['name']}: {'; '.join(r['issues'])}")
    args.out.write_text(json.dumps({"fail": fail, "pass": passed, "results": results}, indent=2) + "\n")
    print(f"=== structural_pass4_audit: {fail} FAIL / {passed} PASS → {args.out} ===")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
