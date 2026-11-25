#!/usr/bin/env python3
"""FAIL maps that place metatiles rendering >50% transparent/near-black, or OOB.

Common cause: Rustboro civic/pave IDs (0x2BB, 0x22F, …) on a Petalburg secondary
tileset that has only 144 metas / empty slots at those indices.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.city_door_warp_audit import OUTDOOR_SETTLEMENTS  # noqa: E402
from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.render_map_preview import (  # noqa: E402
    NUM_METATILES_IN_PRIMARY,
    load_tilesets,
    render_metatile,
)
from tools.sinnoh_maps.structural_extra_audit import all_map_names  # noqa: E402

LAYOUTS = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
}

BLACK_FRAC = 0.50


@lru_cache(maxsize=8)
def tilesets(primary: str, secondary: str):
    return load_tilesets(primary, secondary)


@lru_cache(maxsize=4096)
def metatile_black_frac(primary: str, secondary: str, mt_id: int) -> float:
    prim, sec = tilesets(primary, secondary)
    # OOB secondary
    if mt_id >= NUM_METATILES_IN_PRIMARY:
        local = mt_id - NUM_METATILES_IN_PRIMARY
        if local >= len(sec["metas"]):
            return 1.0
    elif mt_id >= len(prim["metas"]):
        return 1.0
    img = render_metatile(prim, sec, mt_id)
    px = list(img.getdata())
    if not px:
        return 1.0
    bad = sum(1 for r, g, b, a in px if a < 8 or (r + g + b) < 24)
    return bad / len(px)


def audit_map(name: str) -> dict:
    if name not in LAYOUTS:
        return {"name": name, "status": "SKIP", "issues": []}
    meta = LAYOUTS[name]
    primary = meta.get("primary_tileset") or "gTileset_General"
    secondary = meta.get("secondary_tileset") or "gTileset_Petalburg"
    # Indoor Building/Facility stubs use 0x001 as solid black filler — out of scope.
    if primary in ("gTileset_Building", "gTileset_SecretBase", "gTileset_BattleFrontier"):
        return {"name": name, "status": "SKIP", "issues": ["indoor primary skipped"], "secondary": secondary}
    w, h = int(meta["width"]), int(meta["height"])
    data = (REPO / meta["blockdata_filepath"]).read_bytes()
    bad_cells = 0
    bad_ids: dict[int, int] = {}
    samples = []
    for y in range(h):
        for x in range(w):
            mt = struct.unpack_from("<H", data, (y * w + x) * 2)[0] & 0x3FF
            frac = metatile_black_frac(primary, secondary, mt)
            if frac > BLACK_FRAC:
                bad_cells += 1
                bad_ids[mt] = bad_ids.get(mt, 0) + 1
                if len(samples) < 8:
                    samples.append({"x": x, "y": y, "mt": f"0x{mt:03X}", "black_frac": round(frac, 2)})
    issues = []
    if bad_cells:
        top = sorted(bad_ids.items(), key=lambda kv: -kv[1])[:8]
        issues.append(
            f"black/void cells: {bad_cells} "
            f"(ids {', '.join(f'0x{m:03X}×{c}' for m,c in top)}; "
            f"tileset {secondary})"
        )
    status = "FAIL" if issues else "PASS"
    return {
        "name": name,
        "status": status,
        "issues": issues,
        "bad_cells": bad_cells,
        "bad_ids": {f"0x{m:03X}": c for m, c in bad_ids.items()},
        "secondary": secondary,
        "samples": samples,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "tools/sinnoh_maps/black_metatile_audit_report.json")
    ap.add_argument("--maps", nargs="*")
    ap.add_argument("--outdoor-only", action="store_true")
    args = ap.parse_args()
    if args.maps:
        names = args.maps
    elif args.outdoor_only:
        # Settlements + General-primary land routes (exclude indoor League stubs in LAND_TABLE)
        names = sorted(
            set(OUTDOOR_SETTLEMENTS)
            | {
                n for n in LAND_TABLE
                if n in LAYOUTS
                and (LAYOUTS[n].get("primary_tileset") or "gTileset_General") == "gTileset_General"
            }
        )
    else:
        names = all_map_names()
    names = [n for n in names if n in LAYOUTS]
    results = [audit_map(n) for n in names]
    fail = sum(1 for r in results if r["status"] == "FAIL")
    passed = sum(1 for r in results if r["status"] == "PASS")
    for r in results:
        if r["status"] == "FAIL":
            print(f"FAIL {r['name']}: {r['issues'][0]}")
    out = {"fail": fail, "pass": passed, "results": results, "threshold": BLACK_FRAC}
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"=== black_metatile_audit: {fail} FAIL / {passed} PASS → {args.out} ===")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
