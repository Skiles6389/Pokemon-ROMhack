#!/usr/bin/env python3
"""Force collision=1 on Emerald south-ledge metatiles (0x0D5 / 0x0D6).

Walkable ledge collision was incorrectly forced to 0 by the Sinnoh converter,
letting the player walk sideways/up onto ledges. JumpSouth needs coll=1.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.sinnoh_build_lib import MT_LEDGE_A, MT_LEDGE_B  # noqa: E402

LAYOUTS = json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
LEDGES = {MT_LEDGE_A, MT_LEDGE_B}


def fix_layout(meta: dict) -> int:
    path = REPO / meta["blockdata_filepath"]
    if not path.exists():
        return 0
    w, h = int(meta["width"]), int(meta["height"])
    data = bytearray(path.read_bytes())
    n = 0
    for i in range(w * h):
        v = struct.unpack_from("<H", data, i * 2)[0]
        mt = v & 0x3FF
        coll = (v >> 10) & 3
        elev = (v >> 12) & 0xF
        if mt in LEDGES and coll == 0:
            struct.pack_into("<H", data, i * 2, (mt & 0x3FF) | (1 << 10) | (elev << 12))
            n += 1
    if n:
        path.write_bytes(bytes(data))
    return n


def main() -> int:
    total = maps = 0
    for L in LAYOUTS:
        name = L["name"].replace("_Layout", "")
        n = fix_layout(L)
        if n:
            print(f"{name}: fixed {n} ledge cells")
            total += n
            maps += 1
    print(f"=== remediate_ledge_collision: {total} cells across {maps} maps ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
