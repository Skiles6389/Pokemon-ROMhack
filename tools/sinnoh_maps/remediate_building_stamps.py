#!/usr/bin/env python3
"""Restamp every outdoor-settlement building from complete Emerald stamps.

Uses emerald_building_stamps.py. Idempotent. Run after city door remediations.
Orders stamps so PC/Mart/Gym win conflicts with houses. Aligns double-door
warps onto the primary door metatile. Nudges edge warps when a stamp would OOB.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.city_door_warp_audit import (  # noqa: E402
    OUTDOOR_SETTLEMENTS,
    classify_warp,
)
from tools.sinnoh_maps.emerald_building_stamps import (  # noqa: E402
    CIVIC_RUSTBORO,
    CIVIC_RUSTBORO_WIDE,
    GYM_MAUVILLE,
    HOUSE_OLDALE,
    HOUSE_PETALBURG_A,
    HOUSE_PETALBURG_WIDE,
    HOUSE_RUSTBORO,
    MART_OLDALE,
    MART_RUSTBORO,
    PC_OLDALE,
    PC_RUSTBORO,
    stamp_with_clear,
)
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    LAYOUTS_JSON,
    MAPS,
    MT_GRASS,
    pack,
)

LAYOUTS = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads(LAYOUTS_JSON.read_text())["layouts"]
}

PETALBURG_TOWNS = {
    "TwinleafTown", "SandgemTown", "FloaromaTown", "SolaceonTown",
    "CelesticTown", "SurvivalArea", "ResortArea", "FightArea",
}
RUSTBORO_CITIES = {
    "JubilifeCity", "OreburghCity", "EternaCity", "HearthomeCity",
    "VeilstoneCity", "PastoriaCity", "CanalaveCity", "SnowpointCity",
    "SunyshoreCity", "PokemonLeague_Exterior",
}

MT_CITY_PAVE = 0x2BB
DOOR_MAT = 0x201

# Left-half / right-half of Emerald double doors
LEFT_DOOR_HALF = {0x060, 0x266, 0x062, 0x042}  # also treat right half as sibling
PRIMARY_DOORS = {0x061, 0x041, 0x22F, 0x248, 0x287, 0x1CD}


def pick_stamp(map_name: str, dest: str, kind: str):
    if kind == "center":
        return PC_RUSTBORO if map_name in RUSTBORO_CITIES else PC_OLDALE
    if kind == "mart":
        return MART_RUSTBORO if map_name in RUSTBORO_CITIES else MART_OLDALE
    if kind == "gym":
        return GYM_MAUVILLE
    civic_keys = (
        "TV_", "POKETCH", "SCHOOL", "CONDO", "TERMINAL", "DEPT", "GAME",
        "WAREHOUSE", "HALL", "LAB", "DAY_CARE", "NEWS", "VILLA", "RIBBON",
        "MARKET", "PRIZE", "GALACTIC", "HQ", "LIBRARY", "MUSEUM", "FAN_CLUB",
        "CONTEST", "HARBOR",
    )
    if kind == "civic" or any(k in dest for k in civic_keys):
        if map_name in RUSTBORO_CITIES:
            return CIVIC_RUSTBORO_WIDE if any(
                k in dest for k in ("TV_", "POKETCH", "TERMINAL", "DEPT", "GALACTIC", "HQ")
            ) else CIVIC_RUSTBORO
        return HOUSE_PETALBURG_WIDE if "LAB" in dest else HOUSE_PETALBURG_A
    if map_name in PETALBURG_TOWNS or map_name == "TwinleafTown":
        if any(k in dest for k in ("PLAYERSHOUSE", "RIVALSHOUSE")):
            return HOUSE_PETALBURG_WIDE
        return HOUSE_PETALBURG_A
    return HOUSE_RUSTBORO


def stamp_priority(kind: str, dest: str) -> int:
    """Lower = stamped earlier; PC/Mart/Gym last so they win overlaps."""
    if kind == "gym":
        return 40
    if kind == "center":
        return 30
    if kind == "mart":
        return 30
    if any(k in dest for k in ("TV_", "POKETCH", "TERMINAL", "DEPT", "GALACTIC", "HQ")):
        return 20
    return 10


def load_grid(name: str):
    meta = LAYOUTS[name]
    w, h = int(meta["width"]), int(meta["height"])
    data = bytearray((REPO / meta["blockdata_filepath"]).read_bytes())
    grid = [
        [struct.unpack_from("<H", data, (y * w + x) * 2)[0] & 0x3FF for x in range(w)]
        for y in range(h)
    ]
    coll = [
        [(struct.unpack_from("<H", data, (y * w + x) * 2)[0] >> 10) & 3 for x in range(w)]
        for y in range(h)
    ]
    return grid, coll, w, h, meta


def fill_for(map_name: str) -> int:
    if map_name in RUSTBORO_CITIES:
        return MT_CITY_PAVE
    return MT_GRASS


def fits(stamp, door_x, door_y, w, h) -> bool:
    left = door_x - stamp["door_dx"]
    top = door_y - stamp["door_dy"]
    sw, sh = len(stamp["tiles"][0]), len(stamp["tiles"])
    return left >= 0 and top >= 0 and left + sw <= w and top + sh <= h


def choose_stamp_and_door(map_name, dest, kind, x, y, w, h):
    """Pick a stamp that fits; nudge door coords if near edges."""
    stamp = pick_stamp(map_name, dest, kind)
    if stamp is None:
        return None, x, y
    dx, dy = x, y
    # Prefer primary door; if warp is on right half of double door, use left primary
    # (stamp door_mt is left primary 0x061/0x041)
    if kind in ("center", "mart") and fits(stamp, dx, dy, w, h):
        return stamp, dx, dy

    candidates = [stamp]
    if kind in ("building", "house") and map_name in PETALBURG_TOWNS:
        candidates = [HOUSE_PETALBURG_A, HOUSE_OLDALE, HOUSE_PETALBURG_WIDE]
    elif kind in ("building", "house"):
        candidates = [HOUSE_RUSTBORO, CIVIC_RUSTBORO, HOUSE_PETALBURG_A, HOUSE_OLDALE]

    # Nudge door down/right/left until a candidate fits
    for cand in candidates:
        for ny in range(dy, min(h, dy + 3)):
            for nx in (dx, dx + 1, dx - 1, dx + 2):
                if 0 <= nx < w and fits(cand, nx, ny, w, h):
                    return cand, nx, ny
    # Last resort: Oldale compact house
    if fits(HOUSE_OLDALE, dx, dy, w, h):
        return HOUSE_OLDALE, dx, dy
    for ny in range(dy, min(h, dy + 4)):
        for nx in range(max(0, dx - 2), min(w, dx + 3)):
            if fits(HOUSE_OLDALE, nx, ny, w, h):
                return HOUSE_OLDALE, nx, ny
    return stamp, dx, dy


def remedia_map(name: str) -> dict:
    if name not in LAYOUTS:
        return {"name": name, "stamped": 0}
    if name in ("TwinleafTown", "JubilifeCity"):
        return {"name": name, "stamped": 0, "skipped": True}

    grid, coll, w, h, meta = load_grid(name)
    mj_path = MAPS / name / "map.json"
    mj = json.loads(mj_path.read_text()) if mj_path.exists() else {}
    warps = mj.get("warp_events") or []
    fill = fill_for(name)
    stamped = 0
    warp_nudges = 0

    jobs = []
    for idx, warp in enumerate(warps):
        dest = warp.get("dest_map") or ""
        kind = classify_warp(dest)
        if kind in ("cave", "gate", "other", None):
            if not any(
                k in dest
                for k in (
                    "HOUSE", "CENTER", "MART", "GYM", "SCHOOL", "TV_", "POKETCH",
                    "CONDO", "TERMINAL", "LAB", "DEPT", "GAME", "HALL", "DAY_CARE",
                    "NEWS", "VILLA", "RIBBON", "MARKET", "PRIZE", "WAREHOUSE",
                    "GALACTIC", "HQ", "LIBRARY", "MUSEUM",
                )
            ):
                continue
            if kind in ("other", "cave", "gate"):
                continue
            kind = "building"
        if kind == "unknown":
            kind = "building"
        jobs.append((stamp_priority(kind, dest), idx, warp, kind, dest))

    jobs.sort(key=lambda t: (t[0], t[1]))
    # Deduplicate: only one stamp per unique dest at same door cluster
    seen_dest_xy = set()
    for _prio, idx, warp, kind, dest in jobs:
        x, y = int(warp["x"]), int(warp["y"])
        # Skip secondary half of a double-door pair (same dest, adjacent x)
        key = (dest, y)
        if key in seen_dest_xy and kind in ("center", "mart"):
            # Still nudge this warp onto the primary door after stamping
            continue
        stamp, dx, dy = choose_stamp_and_door(name, dest, kind, x, y, w, h)
        if stamp is None or not stamp.get("door_mt"):
            continue
        if not fits(stamp, dx, dy, w, h):
            continue
        stamp_with_clear(grid, coll, dx, dy, stamp, fill, pad=0)
        if dy + 1 < h and grid[dy + 1][dx] in (fill, MT_GRASS, 0x001, MT_CITY_PAVE):
            grid[dy + 1][dx] = DOOR_MAT
        stamped += 1
        seen_dest_xy.add(key)
        # Nudge warp(s) for this dest onto the door tile
        for widx, w2 in enumerate(warps):
            if w2.get("dest_map") != dest:
                continue
            wx, wy = int(w2["x"]), int(w2["y"])
            # Same door row, within stamp width
            if abs(wy - dy) <= 1 and abs(wx - dx) <= max(2, stamp["door_dx"]):
                if wx != dx or wy != dy:
                    warps[widx]["x"] = dx
                    warps[widx]["y"] = dy
                    warp_nudges += 1

    # Collapse duplicate warps that now share identical coords+dest (keep first)
    deduped = []
    seen = set()
    for w2 in warps:
        k = (w2.get("dest_map"), w2.get("x"), w2.get("y"), w2.get("dest_warp_id"))
        if k in seen:
            continue
        seen.add(k)
        deduped.append(w2)
    if len(deduped) != len(warps):
        mj["warp_events"] = deduped
        warp_nudges += len(warps) - len(deduped)
    else:
        mj["warp_events"] = warps
    if warp_nudges:
        mj_path.write_text(json.dumps(mj, indent=2) + "\n")

    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt in (0x061, 0x062, 0x041, 0x042, 0x22F, 0x248, 0x287, 0x1CD, DOOR_MAT):
                coll[y][x] = 1 if mt != DOOR_MAT else 0
            elif mt >= 0x200 or (0x028 <= mt <= 0x063) or mt in (
                0x256, 0x257, 0x25E, 0x25F, 0x266, 0x27E, 0x27F, 0x325, 0x326, 0x267,
                0x1AA, 0x1AB, 0x1AC, 0x1B2, 0x1B3, 0x1B4, 0x1B8, 0x1B9, 0x1BA, 0x1BB,
                0x1BC, 0x1C0, 0x1C1, 0x1C2, 0x1C3, 0x1C4, 0x1C5, 0x1C8, 0x1C9, 0x1CA,
                0x1CB, 0x1CC,
            ):
                coll[y][x] = 1

    (REPO / meta["blockdata_filepath"]).write_bytes(pack(grid, coll))
    return {"name": name, "stamped": stamped, "warp_nudges": warp_nudges}


def main() -> int:
    results = [remedia_map(n) for n in sorted(OUTDOOR_SETTLEMENTS)]
    total = sum(r["stamped"] for r in results)
    for r in results:
        if r.get("stamped") or r.get("warp_nudges"):
            print(f"{r['name']}: stamped {r.get('stamped', 0)} nudges={r.get('warp_nudges', 0)}")
    print(f"=== remediate_building_stamps: {total} buildings across {len(results)} maps ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
