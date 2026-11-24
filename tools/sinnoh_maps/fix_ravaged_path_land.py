#!/usr/bin/env python3
"""
Regenerate Ravaged Path from authentic Platinum dungeon land-data MAP_435 (N) +
MAP_436 (S). M13 used MAP_374 for the south half (wrong chunk).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_m13_maps import (  # noqa: E402
    PLAT_DATA,
    LAYOUTS,
    CAVE_ENTRANCE,
    CAVE_FLOOR,
    attrs_to_metatile_grid,
    load_attrs,
    open_path,
    pack,
)


def main() -> int:
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        return 1

    aN, aS = load_attrs(435), load_attrs(436)
    g = []
    for y in range(32):
        g.append([aN[y * 32 + x] for x in range(32)])
    for y in range(32):
        g.append([aS[y * 32 + x] for x in range(32)])
    mt = attrs_to_metatile_grid(g, cave=True)

    open_path(mt, [(19, 50), (19, 51), (18, 50), (20, 50), (19, 49)], CAVE_FLOOR)
    open_path(mt, [(28, 44), (27, 44), (28, 43), (28, 45), (29, 44)], CAVE_FLOOR)
    mt[50][19] = CAVE_ENTRANCE
    mt[44][28] = CAVE_ENTRANCE
    open_path(mt, [(x, y) for x in range(16, 22) for y in range(30, 35)], CAVE_FLOOR)

    folder = LAYOUTS / "RavagedPath"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(pack(mt))
    print("RavagedPath regenerated from MAP_435 + MAP_436")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
