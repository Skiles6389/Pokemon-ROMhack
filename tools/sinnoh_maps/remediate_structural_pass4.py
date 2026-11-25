#!/usr/bin/env python3
"""Pass-4: nudge corridor-blocking FACE NPCs off the choke point."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.structural_extra_audit import (  # noqa: E402
    LAYOUTS,
    all_map_names,
    load_cells,
    walkable,
)

MAPS = REPO / "data/maps"


def main() -> int:
    nudged = 0
    for name in all_map_names():
        if name not in LAYOUTS:
            continue
        mj_path = MAPS / name / "map.json"
        if not mj_path.exists():
            continue
        cells, w, h, _ = load_cells(name)
        mj = json.loads(mj_path.read_text())
        warps = {(int(wp["x"]), int(wp["y"])) for wp in (mj.get("warp_events") or [])}
        ch = False

        def W(xx, yy):
            return 0 <= xx < w and 0 <= yy < h and walkable(*cells[yy][xx][:2])

        for obj in mj.get("object_events") or []:
            x, y = int(obj["x"]), int(obj["y"])
            mov = obj.get("movement_type") or ""
            if "FACE" not in mov:
                continue
            if (x, y) in warps:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (x + dx, y + dy) not in warps and W(x + dx, y + dy):
                        obj["x"], obj["y"] = x + dx, y + dy
                        nudged += 1
                        ch = True
                        break
                continue
            if not (0 <= x < w and 0 <= y < h):
                continue
            ns = W(x, y - 1) and W(x, y + 1) and not W(x - 1, y) and not W(x + 1, y)
            ew = W(x - 1, y) and W(x + 1, y) and not W(x, y - 1) and not W(x, y + 1)
            if not (ns or ew):
                continue
            # Nudge into a side alcove if any walkable diagonal/side exists nearby
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1)):
                nx, ny = x + dx, y + dy
                if W(nx, ny) and (nx, ny) not in warps:
                    obj["x"], obj["y"] = nx, ny
                    nudged += 1
                    ch = True
                    break
        if ch:
            mj_path.write_text(json.dumps(mj, indent=2) + "\n")
            print(f"{name}: nudged NPCs")
    print(f"=== remediate_structural_pass4: nudged={nudged} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
