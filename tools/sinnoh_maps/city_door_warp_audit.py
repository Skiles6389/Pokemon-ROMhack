#!/usr/bin/env python3
"""City/town visual + door/warp enterability audit.

Flags:
  (a) Grass-dominant outdoor cities that should be paved (Platinum cities)
  (b) Pokémon Center / Mart / Gym warps that are not enterable
      (warp exists AND door metatile on that cell AND approach tile reachable)
  (c) Buildings assembled from wrong metatiles (trees/cliffs inside facade)
  (d) Every outdoor warp is reachable and enterable (BFS from map edge/connections)

Writes tools/sinnoh_maps/city_door_warp_audit_report.json
Exit 1 on any FAIL.
"""
from __future__ import annotations

import json
import struct
import sys
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    MT_GRASS,
    MT_ROCK,
    MT_TALL,
    MT_TREE,
    PATH_METATILES,
    WATER_METATILES,
)

LAYOUTS = REPO / "data" / "layouts"
MAPS = REPO / "data" / "maps"
LAYOUTS_JSON = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((LAYOUTS / "layouts.json").read_text())["layouts"]
}

# Platinum settlements that are paved cities (not grassy towns)
PAVED_CITIES = {
    "JubilifeCity",
    "OreburghCity",
    "EternaCity",
    "HearthomeCity",
    "VeilstoneCity",
    "PastoriaCity",
    "CanalaveCity",
    "SnowpointCity",
    "SunyshoreCity",
    "FightArea",
    "SurvivalArea",
    "ResortArea",
}

# Emerald door / warp-door metatile IDs (General + common secondaries)
DOOR_METATILES = {
    0x061, 0x062,  # Pokémon Center (single / double door)
    0x041, 0x042,  # Mart
    0x248,  # Petalburg house
    0x22F,  # Rustboro flat/school
    0x287,  # Oldale house
    0x021,  # Petalburg house alt
    0x20E,  # indoor mat / gym stand-in
    0x1CD,  # gym door (common)
    0x209,  # mat
    0x09F, 0x0A7,  # cave mouth
}

# City sidewalk / plaza pavement (secondary tilesets)
CITY_PAVE_METATILES = {
    0x2BB,  # Rustboro sidewalk
    0x2C3,  # Rustboro plaza accent
    0x22B,  # Lilycove plaza
    0x233,  # Lilycove
    0x05E,  # Mauville
    0x108,  # Mauville
} | PATH_METATILES

TREE = set(MT_TREE)
CLIFF_ROCK = {MT_ROCK, 0x07C, 0x091, 0x139}

OUTDOOR_SETTLEMENTS = [
    n for n in LAND_TABLE
    if n.endswith("Town") or n.endswith("City") or n in {
        "FightArea", "SurvivalArea", "ResortArea", "PokemonLeague_Exterior",
    }
]


def load_cells(name: str):
    meta = LAYOUTS_JSON[name]
    w, h = int(meta["width"]), int(meta["height"])
    data = (REPO / meta["blockdata_filepath"]).read_bytes()
    cells = []
    for y in range(h):
        row = []
        for x in range(w):
            raw = struct.unpack_from("<H", data, (y * w + x) * 2)[0]
            row.append((raw & 0x3FF, (raw >> 10) & 3, (raw >> 12) & 0xF))
        cells.append(row)
    return cells, w, h, meta


def is_walkable(mt: int, coll: int) -> bool:
    if mt in WATER_METATILES:
        return False
    if mt in TREE or mt in CLIFF_ROCK:
        return False
    # Door metatiles: treat as enterable even when coll=1 (vanilla Emerald)
    if mt in DOOR_METATILES:
        return True
    return coll == 0


def bfs_reachable(cells, w, h, seeds):
    """4-connected walkability flood fill; doors are absorbing-but-reachable."""
    seen = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()
    for x, y in seeds:
        if 0 <= x < w and 0 <= y < h and is_walkable(*cells[y][x][:2]):
            seen[y][x] = True
            q.append((x, y))
    while q:
        x, y = q.popleft()
        mt = cells[y][x][0]
        # Don't flood through door into building interior (door is destination)
        if mt in DOOR_METATILES:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                if is_walkable(*cells[ny][nx][:2]):
                    seen[ny][nx] = True
                    q.append((nx, ny))
    return seen


def edge_seeds(w, h):
    seeds = []
    for x in range(w):
        seeds.append((x, 0))
        seeds.append((x, h - 1))
    for y in range(h):
        seeds.append((0, y))
        seeds.append((w - 1, y))
    return seeds


def connection_seeds(name: str, w: int, h: int):
    seeds = edge_seeds(w, h)
    mj = MAPS / name / "map.json"
    if not mj.exists():
        return seeds
    data = json.loads(mj.read_text())
    for conn in data.get("connections") or []:
        direction = conn.get("direction")
        offset = int(conn.get("offset") or 0)
        # Approximate entry band along the connected edge
        if direction == "up":
            for x in range(max(0, offset), min(w, offset + 16)):
                seeds.append((x, 0))
        elif direction == "down":
            for x in range(max(0, offset), min(w, offset + 16)):
                seeds.append((x, h - 1))
        elif direction == "left":
            for y in range(max(0, offset), min(h, offset + 16)):
                seeds.append((0, y))
        elif direction == "right":
            for y in range(max(0, offset), min(h, offset + 16)):
                seeds.append((w - 1, y))
    # Also seed from outdoor warp exits that land on this map's south approaches
    for warp in data.get("warp_events") or []:
        x, y = int(warp["x"]), int(warp["y"])
        if 0 <= x < w and 0 <= y + 1 < h:
            seeds.append((x, y + 1))
    return seeds


def grass_dominant(cells, w, h) -> tuple[bool, float, float]:
    """Return (is_grass_heavy, grass_frac, pave_frac) over non-solid outdoor cells."""
    grass = pave = walk = 0
    for y in range(h):
        for x in range(w):
            mt, coll, _ = cells[y][x]
            if mt in TREE or mt in CLIFF_ROCK or mt >= 0x200 and mt not in CITY_PAVE_METATILES | DOOR_METATILES:
                if mt in CITY_PAVE_METATILES:
                    pass
                else:
                    continue
            if coll and mt not in DOOR_METATILES and mt not in CITY_PAVE_METATILES:
                if mt not in (MT_GRASS, MT_TALL) and mt not in CITY_PAVE_METATILES:
                    continue
            if mt in (MT_GRASS, MT_TALL):
                grass += 1
                walk += 1
            elif mt in CITY_PAVE_METATILES:
                pave += 1
                walk += 1
            elif coll == 0:
                walk += 1
    if walk == 0:
        return False, 0.0, 0.0
    return grass / walk >= 0.45 and pave / walk < 0.20, grass / walk, pave / walk


def trees_in_building(cells, door_x, door_y) -> int:
    """Count tree/rock tiles that poke through a building facade.

    Only flags tree/rock cells that have a neighboring secondary facade tile
    (>=0x200 building body). Tree rings beside houses (Twinleaf) are fine.
    """
    h, w = len(cells), len(cells[0])
    bad = 0
    for dy in range(-5, 1):
        for dx in range(-3, 4):
            x, y = door_x + dx, door_y + dy
            if y < 0 or x < 0 or y >= h or x >= w:
                continue
            mt = cells[y][x][0]
            if mt not in TREE and mt not in CLIFF_ROCK:
                continue
            # Truly inside a facade: building tiles on opposite sides (not just
            # adjacent tree-ring next to a house wall — Twinleaf is correct).
            def is_bldg(nx, ny) -> bool:
                if not (0 <= nx < w and 0 <= ny < h):
                    return False
                nmt = cells[ny][nx][0]
                return nmt >= 0x200 and nmt not in {0x201, 0x209}

            inside = (is_bldg(x - 1, y) and is_bldg(x + 1, y)) or (
                is_bldg(x, y - 1) and is_bldg(x, y + 1)
            )
            if inside:
                bad += 1
    return bad


def classify_warp(dest: str) -> str | None:
    d = dest.upper()
    if "GATE" in d:
        return "gate"
    # Outdoor field links — just need a walkable cell, not a building door
    if any(k in d for k in ("MEADOW", "LAKEFRONT", "ROUTE", "UNDERGROUND")):
        return "other"
    if "POKEMON_CENTER" in d or d.endswith("_CENTER_1F") or "POKEMONCENTER" in d or d.endswith("_SOUTH_PC"):
        return "center"
    if "MART" in d or "MARKET" in d:
        return "mart"
    if "GYM" in d:
        return "gym"
    if any(k in d for k in ("CAVE", "MINE", "TEMPLE", "VICTORY_ROAD")):
        return "cave"
    if any(k in d for k in (
        "HOUSE", "CONDO", "SCHOOL", "LAB", "MUSEUM", "TV_", "POKETCH",
        "TERMINAL", "DEPT", "FAN_CLUB", "CONTEST", "HALL", "LIBRARY",
        "APARTMENT", "FLAT", "SHOP", "CENTER", "HARBOR", "INN",
        "VILLA", "DAY_CARE", "DAYCARE", "NEWS", "GALACTIC",
        "PRIZE", "EXCHANGE", "BUILDING", "HQ",
    )):
        return "building"
    # Any other MAP_* indoor dest still needs an enterable cell
    if d.startswith("MAP_") and "ROUTE" not in d:
        return "building"
    return "other"


def expected_door(kind: str) -> set[int] | None:
    if kind == "center":
        return {0x061, 0x062}
    if kind == "mart":
        return {0x041, 0x042}
    if kind == "gym":
        return {0x1CD, 0x20E, 0x061, 0x22F, 0x248}
    if kind == "cave":
        return {0x09F, 0x0A7} | DOOR_METATILES  # cave mouth or any door stand-in
    if kind in ("building", "house"):
        return DOOR_METATILES
    return None  # gates/other: any walkable OK


def audit_one(name: str) -> dict:
    if name not in LAYOUTS_JSON:
        return {"name": name, "status": "SKIP", "issues": ["no layout"]}
    cells, w, h, meta = load_cells(name)
    mj_path = MAPS / name / "map.json"
    warps = []
    if mj_path.exists():
        warps = json.loads(mj_path.read_text()).get("warp_events") or []

    issues = []
    status = "PASS"
    details: dict = {
        "warps": [],
        "grass_frac": None,
        "pave_frac": None,
        "bad_building_tiles": 0,
        "unreachable_warps": 0,
        "non_enterable_doors": 0,
    }

    # (a) grass-dominant paved cities
    if name in PAVED_CITIES:
        heavy, gfrac, pfrac = grass_dominant(cells, w, h)
        details["grass_frac"] = round(gfrac, 3)
        details["pave_frac"] = round(pfrac, 3)
        if heavy:
            issues.append(
                f"grass-dominant paved city: grass={gfrac:.0%} pave={pfrac:.0%} "
                "(Platinum city should be pavement, not grass)"
            )
            status = "FAIL"

    seeds = connection_seeds(name, w, h)
    reachable = bfs_reachable(cells, w, h, seeds)

    for warp in warps:
        x, y = int(warp["x"]), int(warp["y"])
        dest = warp.get("dest_map") or ""
        kind = classify_warp(dest)
        entry = {
            "x": x, "y": y, "dest": dest, "kind": kind,
            "mt": None, "coll": None, "reachable": False, "enterable": False, "issues": [],
        }
        if not (0 <= x < w and 0 <= y < h):
            entry["issues"].append("warp OOB")
            issues.append(f"warp OOB ({x},{y}) → {dest}")
            status = "FAIL"
            details["warps"].append(entry)
            details["non_enterable_doors"] += 1
            continue

        mt, coll, elev = cells[y][x]
        entry["mt"] = f"0x{mt:03X}"
        entry["coll"] = coll
        entry["reachable"] = bool(reachable[y][x])

        # Approach tile south of door should be walkable + reachable for south-facing doors
        approach_ok = False
        for ax, ay in ((x, y + 1), (x, y - 1), (x - 1, y), (x + 1, y)):
            if 0 <= ax < w and 0 <= ay < h and reachable[ay][ax] and cells[ay][ax][1] == 0:
                approach_ok = True
                break
        # Edge warps (gates) may themselves be the approach
        if kind == "gate" and (x == 0 or y == 0 or x == w - 1 or y == h - 1):
            approach_ok = True
            entry["reachable"] = True

        expect = expected_door(kind)
        door_ok = True
        if expect is not None:
            if mt not in expect:
                # Double-door sibling: adjacent cell may hold the real door tile
                sibling_door = False
                for ax, ay in ((x - 1, y), (x + 1, y)):
                    if 0 <= ax < w and 0 <= ay < h and cells[ay][ax][0] in expect:
                        sibling_door = True
                        break
                if sibling_door and approach_ok:
                    door_ok = True
                elif kind == "cave" and coll == 0 and approach_ok:
                    # Walkable path into a cave/mine mouth is acceptable
                    door_ok = True
                else:
                    door_ok = False
                    entry["issues"].append(
                        f"expected door metatile in {{{', '.join(f'0x{m:03X}' for m in sorted(expect))}}}, "
                        f"got 0x{mt:03X}"
                    )
        else:
            # non-building: just need walkable or door
            if not is_walkable(mt, coll) and mt not in DOOR_METATILES:
                door_ok = False
                entry["issues"].append(f"non-walkable warp cell 0x{mt:03X} coll={coll}")

        enterable = door_ok and (entry["reachable"] or approach_ok)
        # Prefer approach: door may be coll=1 and only marked reachable if flood hits it
        if door_ok and approach_ok:
            enterable = True
            entry["reachable"] = True
        entry["enterable"] = enterable

        if kind in ("center", "mart", "gym") and not enterable:
            details["non_enterable_doors"] += 1
            issues.append(
                f"{kind} not enterable at ({x},{y}): " + "; ".join(entry["issues"] or ["unreachable"])
            )
            status = "FAIL"
        elif not enterable and kind != "gate":
            details["unreachable_warps"] += 1
            issues.append(
                f"warp not enterable/reachable at ({x},{y}) → {dest}: "
                + "; ".join(entry["issues"] or ["no approach"])
            )
            status = "FAIL"

        # (c) trees/cliffs inside building facade near important warps
        if kind in ("center", "mart", "gym", "building"):
            bad = trees_in_building(cells, x, y)
            if bad > 0:
                details["bad_building_tiles"] += bad
                entry["issues"].append(f"trees/cliffs in facade: {bad}")
                issues.append(f"bad building tiles near ({x},{y}) {kind}: {bad} tree/rock cells")
                status = "FAIL"

        details["warps"].append(entry)

    return {
        "name": name,
        "status": status,
        "issues": issues,
        **{k: v for k, v in details.items() if k != "warps"},
        "warp_count": len(warps),
        "warps": details["warps"],
    }


def main() -> int:
    names = sorted(n for n in OUTDOOR_SETTLEMENTS if n in LAYOUTS_JSON)
    results = [audit_one(n) for n in names]
    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    out = REPO / "tools/sinnoh_maps/city_door_warp_audit_report.json"
    out.write_text(
        json.dumps(
            {
                "results": results,
                "fail": len(fails),
                "warn": len(warns),
                "pass": sum(1 for r in results if r["status"] == "PASS"),
            },
            indent=2,
        )
        + "\n"
    )
    for r in results:
        if r["status"] != "PASS":
            print(f"{r['status']:4s} {r['name']}: {'; '.join(r['issues'][:4])}")
    print(
        f"=== city/door/warp audit: {len(fails)} FAIL / {len(warns)} WARN / "
        f"{len(results)} → {out} ==="
    )
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
