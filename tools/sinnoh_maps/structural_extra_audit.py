#!/usr/bin/env python3
"""Extra structural audits for multi-pass QA.

Categories (pass-focused):
  - map connection / border seam mismatches
  - ledge direction consistency (0x0D5 south vs 0x0D6)
  - elevation mismatches on walkable cells
  - interior wall gaps (indoor maps: open walls / missing border)
  - inaccessible bg_event items (no walkable neighbor)
  - NPCs sitting on warps / door mats
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    MT_GRASS,
    MT_TREE,
    WATER_METATILES,
    is_solid_metatile,
)

LAYOUTS = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
}
MAPS = REPO / "data/maps"
MAP_GROUPS = json.loads((MAPS / "map_groups.json").read_text())

LEDGE_S = 0x0D5  # jump south
LEDGE_N = 0x0D6  # jump other
DOOR_MAT = 0x201
TREE = set(MT_TREE)


def all_map_names() -> list[str]:
    """Sinnoh LAND_TABLE outdoor/caves + interiors whose name starts with a Sinnoh root."""
    names = set(LAND_TABLE)
    roots = tuple(LAND_TABLE) + (
        "LakeVerity", "VerityLakefront", "Jubilife", "Sandgem", "Twinleaf",
        "Oreburgh", "Floaroma", "Eterna", "Hearthome", "Solaceon", "Veilstone",
        "Pastoria", "Celestic", "Canalave", "Snowpoint", "Sunyshore",
        "FightArea", "SurvivalArea", "ResortArea", "PokemonLeague",
        "Route201", "Route202", "Route203", "Route204", "Route205", "Route206",
        "Route207", "Route208", "Route209", "Route210", "Route211", "Route212",
        "Route213", "Route214", "Route215", "Route216", "Route217", "Route218",
        "Route219", "Route220", "Route221", "Route222", "Route223", "Route224",
        "Route225", "Route226", "Route227", "Route228", "Route229", "Route230",
        "MtCoronet", "VictoryRoad_Sinnoh", "StarkMountain", "IronIsland",
        "WaywardCave", "LostTower", "OldChateau", "GreatMarsh", "SendoffSpring",
        "TurnbackCave", "DistortionWorld", "SpearPillar", "Acuity", "Valor",
        "SolaceonRuins", "ManiacTunnel", "FuegoIronworks", "ValleyWindworks",
        "RavagedPath", "OreburghGate", "OreburghMine", "AmitySquare",
    )
    for maps in MAP_GROUPS.values():
        if not isinstance(maps, list):
            continue
        for m in maps:
            if any(m == r or m.startswith(r + "_") for r in roots):
                names.add(m)
    return sorted(n for n in names if n in LAYOUTS)


def load_cells(name: str):
    meta = LAYOUTS[name]
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


def is_indoor(meta: dict, name: str) -> bool:
    prim = meta.get("primary_tileset") or ""
    return "Building" in prim or name.endswith(("_1F", "_2F", "_3F", "_B1F", "_B2F")) or "Gym" in name


def walkable(mt: int, coll: int) -> bool:
    if mt in WATER_METATILES or mt in TREE:
        return False
    if is_solid_metatile(mt) and coll != 0:
        return False
    if coll != 0 and mt not in (DOOR_MAT, 0x061, 0x062, 0x041, 0x042, 0x22F, 0x248, 0x287, 0x1CD):
        # doors often coll=1 but enterable
        if mt < 0x028:
            return False
    return coll == 0 or mt in (0x061, 0x062, 0x041, 0x042, 0x22F, 0x248, 0x287, 0x1CD, DOOR_MAT)


def audit_ledges(cells, w, h) -> list[str]:
    """Ledge tiles should have walkable cell on the jump-from side."""
    issues = []
    bad = 0
    for y in range(h):
        for x in range(w):
            mt, coll, elev = cells[y][x]
            if mt == LEDGE_S:
                # Jump from north onto south — cell above should be walkable
                if y == 0 or not walkable(*cells[y - 1][x][:2]):
                    bad += 1
            elif mt == LEDGE_N:
                if y + 1 >= h or not walkable(*cells[y + 1][x][:2]):
                    bad += 1
    if bad:
        issues.append(f"ledge approach gaps: {bad}")
    return issues


def audit_elevation(cells) -> list[str]:
    bad_water = 0
    bad_walk = 0
    for row in cells:
        for mt, coll, elev in row:
            if mt in WATER_METATILES:
                if elev != 1:
                    bad_water += 1
            elif coll == 0 and elev == 0 and mt not in (0,):
                bad_walk += 1
    issues = []
    # Water elev is a hard FAIL; walk elev=0 only FAILs when widespread
    if bad_water:
        issues.append(f"water elev!=1: {bad_water}")
    if bad_walk > 64:
        issues.append(f"walkable elev=0: {bad_walk}")
    return issues


def audit_connection_seams(name: str, cells, w, h) -> list[str]:
    mj = MAPS / name / "map.json"
    if not mj.exists():
        return []
    data = json.loads(mj.read_text())
    conns = data.get("connections") or []
    issues = []
    for conn in conns:
        direction = conn.get("direction")
        other = (conn.get("map") or "").replace("MAP_", "").replace("_", "")
        # Resolve dest layout name
        dest_name = None
        dest_map = conn.get("map") or ""
        # MAP_ROUTE_201 → Route201 via map.json id lookup
        for folder in MAPS.iterdir():
            if not folder.is_dir():
                continue
            try:
                mid = json.loads((folder / "map.json").read_text()).get("id")
            except Exception:
                continue
            if mid == dest_map:
                dest_name = folder.name
                break
        if not dest_name or dest_name not in LAYOUTS:
            continue
        try:
            dcells, dw, dh, _ = load_cells(dest_name)
        except Exception:
            continue
        offset = int(conn.get("offset") or 0)
        # Overlap on THIS map: when offset is negative, dest hangs off our origin.
        open_cells = 0
        checked = 0
        if direction in ("up", "down"):
            lo = max(0, offset)
            hi = min(w, offset + dw) if offset >= 0 else min(w, dw + offset)
            if offset < 0:
                lo, hi = 0, min(w, dw + offset) if dw + offset > 0 else min(w, dw)
                # dest wider/shifted: our [0, min(w,dw)] still connects
                lo, hi = 0, min(w, dw)
            y = 0 if direction == "up" else h - 1
            for x in range(lo, hi):
                checked += 1
                mt, coll, _ = cells[y][x]
                if walkable(mt, coll) or mt in WATER_METATILES:
                    open_cells += 1
        elif direction in ("left", "right"):
            lo = max(0, offset)
            hi = min(h, offset + dh) if offset >= 0 else 0
            if offset < 0:
                lo, hi = 0, min(h, dh)
            x = 0 if direction == "left" else w - 1
            for y in range(lo, hi):
                checked += 1
                mt, coll, _ = cells[y][x]
                if walkable(mt, coll) or mt in WATER_METATILES:
                    open_cells += 1
        if checked and open_cells == 0:
            issues.append(f"sealed connection {direction}→{dest_name}")
    return issues


def audit_interior_walls(cells, w, h, meta, name) -> list[str]:
    if not is_indoor(meta, name):
        return []
    # Stub interiors (almost no solid tiles) are placeholder maps — skip
    solid = sum(1 for row in cells for mt, coll, _ in row if coll != 0 or is_solid_metatile(mt))
    if solid < max(8, (w * h) // 20):
        return []
    border_open = 0
    border_total = 0
    for x in range(w):
        for y in (0, h - 1):
            border_total += 1
            mt, coll, _ = cells[y][x]
            if walkable(mt, coll) and mt not in (DOOR_MAT, 0x001):
                border_open += 1
    for y in range(1, h - 1):
        for x in (0, w - 1):
            border_total += 1
            mt, coll, _ = cells[y][x]
            if walkable(mt, coll) and mt not in (DOOR_MAT, 0x001):
                border_open += 1
    # Fully-open perimeter = stub placeholder (no walls painted yet)
    if border_total and border_open == border_total:
        return []
    if border_total and border_open / border_total > 0.7:
        return [f"interior wall gaps: {border_open}/{border_total} border open"]
    return []


def audit_inaccessible_items(name: str, cells, w, h) -> list[str]:
    mj = MAPS / name / "map.json"
    if not mj.exists():
        return []
    data = json.loads(mj.read_text())
    bad = 0
    for bg in data.get("bg_events") or []:
        if bg.get("type") not in ("hidden_item", "item", "sign"):
            # still check hidden_item and script items
            if bg.get("type") != "hidden_item" and "item" not in (bg.get("type") or ""):
                if bg.get("type") not in ("hidden_item",):
                    continue
        x, y = int(bg["x"]), int(bg["y"])
        if not (0 <= x < w and 0 <= y < h):
            bad += 1
            continue
        # Need at least one walkable 4-neighbor (or self if walkable)
        ok = False
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and walkable(*cells[ny][nx][:2]):
                ok = True
                break
        if not ok:
            bad += 1
    # Also object_events that are item balls
    for obj in data.get("object_events") or []:
        gfx = obj.get("graphics_id") or ""
        if "ITEM_BALL" not in gfx and "NURIEL" not in gfx:
            continue
        x, y = int(obj["x"]), int(obj["y"])
        ok = False
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and walkable(*cells[ny][nx][:2]):
                ok = True
                break
        if not ok:
            bad += 1
    if bad:
        return [f"inaccessible items/signs: {bad}"]
    return []


def audit_npc_on_warps(name: str, cells, w, h) -> list[str]:
    mj = MAPS / name / "map.json"
    if not mj.exists():
        return []
    data = json.loads(mj.read_text())
    warps = {(int(wp["x"]), int(wp["y"])) for wp in (data.get("warp_events") or [])}
    blocked = 0
    for obj in data.get("object_events") or []:
        x, y = int(obj["x"]), int(obj["y"])
        mov = obj.get("movement_type") or ""
        # Stationary NPC exactly on a warp tile blocks entry
        if (x, y) in warps and "FACE" in mov:
            blocked += 1
    if blocked:
        return [f"stationary NPCs on warps: {blocked}"]
    return []


def audit_map(name: str, *, focus: str = "all") -> dict:
    if name not in LAYOUTS:
        return {"name": name, "status": "SKIP", "issues": ["no layout"]}
    cells, w, h, meta = load_cells(name)
    issues: list[str] = []
    if focus in ("all", "ledges", "pass2"):
        issues += audit_ledges(cells, w, h)
    if focus in ("all", "elevation", "pass2"):
        issues += audit_elevation(cells)
    if focus in ("all", "connections", "pass2", "pass4"):
        issues += audit_connection_seams(name, cells, w, h)
    if focus in ("all", "interiors", "pass3"):
        issues += audit_interior_walls(cells, w, h, meta, name)
    if focus in ("all", "items", "pass3"):
        issues += audit_inaccessible_items(name, cells, w, h)
    if focus in ("all", "npcs", "pass4"):
        issues += audit_npc_on_warps(name, cells, w, h)
    status = "FAIL" if issues else "PASS"
    return {"name": name, "status": status, "issues": issues, "indoor": is_indoor(meta, name)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--focus", default="all")
    ap.add_argument("--out", type=Path, default=REPO / "tools/sinnoh_maps/structural_extra_audit_report.json")
    ap.add_argument("--maps", nargs="*")
    args = ap.parse_args()
    names = args.maps or all_map_names()
    results = [audit_map(n, focus=args.focus) for n in names]
    fail = sum(1 for r in results if r["status"] == "FAIL")
    passed = sum(1 for r in results if r["status"] == "PASS")
    for r in results:
        if r["status"] == "FAIL":
            print(f"FAIL {r['name']}: {'; '.join(r['issues'][:4])}")
    out = {"fail": fail, "pass": passed, "focus": args.focus, "results": results}
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"=== structural_extra_audit ({args.focus}): {fail} FAIL / {passed} PASS → {args.out} ===")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
