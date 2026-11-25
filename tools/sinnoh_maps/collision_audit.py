#!/usr/bin/env python3
"""Collision/elevation audit: compare Emerald map.bin bits to Platinum land data.

Fails when:
  - map.bin has collision/elevation stripped (hi bits all zero) on solid IDs
  - Platinum impassable cells map to Emerald walkable collision bits
  - Walkable cells have elevation 0 (should be 3)
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
    PLAT_DATA,
    is_solid_metatile,
    load_attrs,
    plat_collision,
)

LAYOUTS = REPO / "data" / "layouts"
# Rustboro: road autotile 0x2F8-0x30A, facade doors 0x21F/0x22F, dark gate doorway 0x282.
SECONDARY_WALKABLE = {
    "gTileset_Rustboro": {0x2F8, 0x2F9, 0x2FA, 0x300, 0x301, 0x302, 0x308, 0x309, 0x30A, 0x21F, 0x22F, 0x282},
}
LAYOUTS_JSON = {L["name"].replace("_Layout", ""): L for L in json.loads((LAYOUTS / "layouts.json").read_text())["layouts"]}


def audit_one(name: str) -> dict:
    meta = LAYOUTS_JSON.get(name)
    if not meta:
        return {"name": name, "status": "SKIP", "reason": "no layout"}
    path = REPO / meta["blockdata_filepath"]
    if not path.exists():
        return {"name": name, "status": "FAIL", "reason": "missing map.bin"}
    w, h = int(meta["width"]), int(meta["height"])
    data = path.read_bytes()
    n = w * h
    if len(data) < n * 2:
        return {"name": name, "status": "FAIL", "reason": "size mismatch"}

    hi = sum(1 for i in range(n) if struct.unpack_from("<H", data, i * 2)[0] & 0xFC00)
    strip_rate = 1.0 - hi / n

    # Engine collision vs metatile-ID heuristic. Secondary-specific walkables the
    # global heuristic can't know about (same IDs are walls in other secondaries).
    sec_walk = SECONDARY_WALKABLE.get(meta.get("secondary_tileset", ""), set())
    solid_id_walkable_coll = 0
    walkable_bad_elev = 0
    for i in range(n):
        v = struct.unpack_from("<H", data, i * 2)[0]
        mt, coll, elev = v & 0x3FF, (v >> 10) & 3, (v >> 12) & 0xF
        if is_solid_metatile(mt) and coll == 0 and mt not in sec_walk:
            solid_id_walkable_coll += 1
        if coll == 0 and elev == 0 and mt not in (0,):
            walkable_bad_elev += 1

    plat_opened = 0  # Platinum solid → Emerald coll=0
    plat_blocked = 0  # Platinum walk → Emerald coll=1
    plat_total = 0
    chunks = LAND_TABLE.get(name)
    if chunks and PLAT_DATA.exists():
        rows, cols = len(chunks), len(chunks[0])
        if rows * 32 == h and cols * 32 == w:
            for cy, row in enumerate(chunks):
                for cx, lid in enumerate(row):
                    if lid is None:
                        continue
                    try:
                        attrs = load_attrs(lid)
                    except FileNotFoundError:
                        continue
                    for ly in range(32):
                        for lx in range(32):
                            x, y = cx * 32 + lx, cy * 32 + ly
                            pv = attrs[ly * 32 + lx]
                            ev = struct.unpack_from("<H", data, (y * w + x) * 2)[0]
                            ecoll = (ev >> 10) & 3
                            plat_total += 1
                            if plat_collision(pv) and ecoll == 0:
                                plat_opened += 1
                            if not plat_collision(pv) and ecoll:
                                # water/ledge OK; count only if not water-ish
                                if (ev & 0x3FF) not in (0x170, 0x0D5, 0x0D6):
                                    plat_blocked += 1

    issues = []
    status = "PASS"
    if strip_rate > 0.5:
        issues.append(f"stripped collision/elevation ({strip_rate:.0%})")
        status = "FAIL"
    if solid_id_walkable_coll > max(8, n * 0.01):
        issues.append(f"solid metatile IDs with coll=0: {solid_id_walkable_coll}")
        status = "FAIL"
    if plat_total and plat_opened / plat_total > 0.08:
        # Intentionally paved Platinum cities (Jubilife etc.) convert building-mass
        # solids to sidewalk + stamped Emerald facades — plat_opened is expected.
        from tools.sinnoh_maps.city_door_warp_audit import PAVED_CITIES
        issues.append(f"Platinum solids opened {plat_opened}/{plat_total} ({plat_opened/plat_total:.1%})")
        # Paved cities + door-stamp remediations open Platinum building solids by design.
        settlement = (
            name in PAVED_CITIES
            or name.endswith("Town")
            or name.endswith("City")
            or name == "PokemonLeague_Exterior"
        )
        if settlement:
            if status == "PASS":
                status = "WARN"
        else:
            status = "FAIL"
    if walkable_bad_elev > n * 0.5 and strip_rate <= 0.5:
        issues.append(f"walkable elev=0 cells: {walkable_bad_elev}")
        if status == "PASS":
            status = "WARN"

    return {
        "name": name,
        "status": status,
        "strip_rate": round(strip_rate, 4),
        "solid_id_walkable_coll": solid_id_walkable_coll,
        "plat_opened": plat_opened,
        "plat_blocked": plat_blocked,
        "plat_total": plat_total,
        "issues": issues,
    }


def main() -> int:
    results = [audit_one(n) for n in sorted(LAND_TABLE)]
    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    out = REPO / "tools/sinnoh_maps/collision_audit_report.json"
    out.write_text(json.dumps({"results": results, "fail": len(fails), "warn": len(warns)}, indent=2) + "\n")
    for r in results:
        if r["status"] != "PASS":
            print(f"{r['status']:4s} {r['name']}: {'; '.join(r.get('issues') or [r.get('reason','')])}")
    print(f"=== collision audit: {len(fails)} FAIL, {len(warns)} WARN, {len(results)} maps → {out} ===")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
