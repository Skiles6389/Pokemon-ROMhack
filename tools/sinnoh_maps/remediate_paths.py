#!/usr/bin/env python3
"""Paint Emerald dirt-path metatiles from Platinum path behaviors onto Sinnoh maps."""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    PATH_METATILES,
    encode_map_cell,
    paint_paths_from_attrs,
    stitch,
)

LAYOUTS_JSON = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
}


def remediate(name: str) -> dict:
    meta = LAYOUTS_JSON.get(name)
    chunks = LAND_TABLE.get(name)
    if not meta or not chunks:
        return {"name": name, "status": "SKIP"}
    path = REPO / meta["blockdata_filepath"]
    if not path.exists():
        return {"name": name, "status": "SKIP", "reason": "missing"}
    w, h = int(meta["width"]), int(meta["height"])
    try:
        attr = stitch(chunks)
    except FileNotFoundError as e:
        return {"name": name, "status": "FAIL", "reason": str(e)}
    if len(attr) != h or len(attr[0]) != w:
        return {"name": name, "status": "SKIP", "reason": f"size {len(attr[0])}x{len(attr)} != {w}x{h}"}

    data = bytearray(path.read_bytes())
    grid = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            grid[y][x] = struct.unpack_from("<H", data, (y * w + x) * 2)[0] & 0x3FF

    before = sum(1 for row in grid for mt in row if mt in PATH_METATILES)
    snow = "Fallarbor" in (meta.get("secondary_tileset") or "") or name in {
        "SnowpointCity", "Route216", "Route217", "AcuityLakefront", "LakeAcuity",
    }
    painted = paint_paths_from_attrs(grid, attr, snow=snow, map_name=name)

    for y in range(h):
        for x in range(w):
            struct.pack_into("<H", data, (y * w + x) * 2, encode_map_cell(grid[y][x]))
    path.write_bytes(bytes(data))
    after = sum(1 for row in grid for mt in row if mt in PATH_METATILES)
    return {
        "name": name,
        "status": "OK",
        "plat_path_cells": painted,
        "path_metatiles_before": before,
        "path_metatiles_after": after,
    }


def main() -> int:
    results = [remediate(n) for n in sorted(LAND_TABLE)]
    ok = [r for r in results if r["status"] == "OK"]
    total_painted = sum(r.get("plat_path_cells", 0) for r in ok)
    out = REPO / "tools/sinnoh_maps/remediate_paths_report.json"
    out.write_text(json.dumps({"results": results, "painted_cells": total_painted}, indent=2) + "\n")
    for r in ok:
        if r.get("plat_path_cells"):
            print(
                f"OK {r['name']:32s} plat={r['plat_path_cells']:4d} "
                f"path_mt {r['path_metatiles_before']}→{r['path_metatiles_after']}"
            )
    print(f"=== path remediate: {total_painted} Platinum path cells → {out} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
