#!/usr/bin/env python3
"""
Regenerate Floaroma Town from authentic Platinum land-data MAP_033 (north) +
MAP_032 (south). M13 accidentally used MAP_025/029 (Route 207/206 chunks).

Emerald tiles only — same stamp/open_path approach as gen_m13_maps.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_m13_maps import (  # noqa: E402
    PLAT_DATA,
    LAYOUTS,
    attrs_to_metatile_grid,
    load_attrs,
    open_path,
    pack,
    stamp_building,
)


def main() -> int:
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        return 1

    aN, aS = load_attrs(33), load_attrs(32)
    g = []
    for y in range(32):
        g.append([aN[y * 32 + x] for x in range(32)])
    for y in range(32):
        g.append([aS[y * 32 + x] for x in range(32)])
    mt = attrs_to_metatile_grid(g)

    # Connections / corridors before stamping buildings
    open_path(mt, [(x, y) for x in range(14, 20) for y in range(26, 34)])
    open_path(mt, [(x, 63) for x in range(14, 18)])
    open_path(mt, [(31, y) for y in range(50, 55)] + [(30, y) for y in range(50, 55)])
    open_path(mt, [(20, 4), (21, 4), (20, 5), (21, 5)])
    open_path(mt, [(2, 33), (3, 33), (2, 34), (3, 34), (4, 33)])
    for dx, dy in ((16, 58), (24, 49), (20, 43), (24, 58), (11, 46)):
        open_path(mt, [(dx, dy + 1), (dx - 1, dy + 1), (dx + 1, dy + 1)])

    # Platinum world-local door tiles (origin 160,608) — stamp last
    stamp_building(mt, 16, 58, "center")
    stamp_building(mt, 24, 49, "mart")
    stamp_building(mt, 20, 43, "shop")
    stamp_building(mt, 24, 58, "house")
    stamp_building(mt, 11, 46, "house")

    folder = LAYOUTS / "FloaromaTown"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(pack(mt))

    layouts_path = LAYOUTS / "layouts.json"
    layouts = json.loads(layouts_path.read_text())
    layouts["layouts"] = [L for L in layouts["layouts"] if L.get("id") != "LAYOUT_FLOAROMATOWN"]
    for L in layouts["layouts"]:
        if L.get("id") == "LAYOUT_FLOAROMA_TOWN":
            L["width"] = 32
            L["height"] = 64
            L["blockdata_filepath"] = "data/layouts/FloaromaTown/map.bin"
            break
    layouts_path.write_text(json.dumps(layouts, indent=2) + "\n")
    print("FloaromaTown regenerated from MAP_033 + MAP_032")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
