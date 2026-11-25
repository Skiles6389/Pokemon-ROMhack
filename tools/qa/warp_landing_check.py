#!/usr/bin/env python3
"""Fail when warp landings / warp_event tiles are softlock traps.

For Sinnoh maps (default) or --all:
  1) Script warp/warpsilent/setwarp/setescapewarp/setdivewarp with literal
     (MAP, x, y) must land on a walkable cell (coll=0 OR door/cave/warp
     metatile behavior). setdynamicwarp skipped (elevator floor mats).
  2) Flood fill from that landing must reach an exit when the dest map is
     outdoor (connections or map_type route/town/city): another warp_event
     or a walkable connection-edge cell.
  3) Every warp_event tile must be walkable (door behavior OK). On maps with
     connections, every warp_event must be reachable from a connection edge
     or from another warp landing.

Exit 1 on any violation.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data/maps"
LAYOUTS_LIST = json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
LAYOUTS_BY_ID = {L["id"]: L for L in LAYOUTS_LIST}
LAYOUTS_BY_NAME = {L["name"]: L for L in LAYOUTS_LIST}

# Metatile behaviors that are valid warp stand / door tiles (coll may be 1).
WARP_DOOR_BEHAVIORS = {
    0x08,  # MB_CAVE
    0x0D,  # MB_BATTLE_PYRAMID_WARP
    0x0E,  # MB_MOSSDEEP_GYM_WARP
    0x1C,  # MB_SHOAL_CAVE_ENTRANCE
    0x29,  # MB_LAVARIDGE_GYM_B1F_WARP
    0x60,  # MB_NON_ANIMATED_DOOR
    0x62, 0x63, 0x64, 0x65,  # arrow warps
    0x67,  # MB_AQUA_HIDEOUT_WARP
    0x68,  # MB_LAVARIDGE_GYM_1F_WARP
    0x69,  # MB_ANIMATED_DOOR
    0x6C,  # MB_WATER_DOOR
    0x6D, 0x6E,  # water/deep south warp
    0x8C,  # MB_TRICK_HOUSE_PUZZLE_DOOR
    0x8D,  # MB_PETALBURG_GYM_DOOR
    0xEB, 0xEC, 0xED, 0xEE,  # stair warps
}

# Known general-tileset door/cave mouths (behavior lookup fallback)
DOOR_METATILES = {0x061, 0x062, 0x041, 0x042, 0x248, 0x22F, 0x287, 0x021, 0x20E, 0x1CD, 0x09F, 0x0A7}

OUTDOOR_TYPES = {
    "MAP_TYPE_TOWN", "MAP_TYPE_CITY", "MAP_TYPE_ROUTE", "MAP_TYPE_OCEAN_ROUTE",
}

SINNOH_PREFIXES = (
    "Twinleaf", "Sandgem", "Jubilife", "Oreburgh", "Floaroma", "Eterna",
    "Hearthome", "Solaceon", "Veilstone", "Pastoria", "Celestic", "Canalave",
    "Snowpoint", "Sunyshore", "FightArea", "SurvivalArea", "ResortArea",
    "Route2", "Route3",  # 201-230
    "Verity", "LakeVerity", "LakeValor", "LakeAcuity", "ValleyWindworks",
    "RavagedPath", "OreburghGate", "OreburghMine", "Wayward", "MtCoronet",
    "IronIsland", "VictoryRoad", "PokemonLeague_Sinnoh", "SpearPillar",
    "Distortion", "StarkMountain", "Fullmoon", "Newmoon", "Turnback",
    "Sendoff", "SpringPath", "GreatMarsh", "SolaceonRuins", "ManiacTunnel",
    "LostTower", "FuegoIronworks", "OldChateau",
)

MAP_CONST_RE = re.compile(
    r"\b(?P<cmd>warp|warpsilent|setwarp|setescapewarp|setdivewarp)\s+"
    r"(?P<map>MAP_[A-Z0-9_]+)\s*,\s*(?:255\s*,\s*)?(?P<x>\d+)\s*,\s*(?P<y>\d+)",
)

TILESET_ATTR_PATHS = {
    "gTileset_General": "data/tilesets/primary/general/metatile_attributes.bin",
}


def _discover_secondary_attrs() -> None:
    root = REPO / "data/tilesets/secondary"
    if not root.exists():
        return
    for p in root.glob("*/metatile_attributes.bin"):
        name = "gTileset_" + "".join(part.capitalize() for part in p.parent.name.split("_"))
        # Common override: battle_frontier_outside_west → gTileset_BattleFrontierOutsideWest
        parts = p.parent.name.split("_")
        camel = "gTileset_" + "".join(x.capitalize() for x in parts)
        TILESET_ATTR_PATHS[camel] = str(p.relative_to(REPO))


_discover_secondary_attrs()

# Manual aliases used in layouts.json
TILESET_ATTR_PATHS.update({
    "gTileset_Petalburg": "data/tilesets/secondary/petalburg/metatile_attributes.bin",
    "gTileset_Rustboro": "data/tilesets/secondary/rustboro/metatile_attributes.bin",
    "gTileset_Building": "data/tilesets/secondary/building/metatile_attributes.bin",
    "gTileset_Shop": "data/tilesets/secondary/shop/metatile_attributes.bin",
    "gTileset_Cave": "data/tilesets/secondary/cave/metatile_attributes.bin",
    "gTileset_SecretBase": "data/tilesets/secondary/secret_base/metatile_attributes.bin",
})


def behavior_for(layout: dict, mt: int) -> int:
    """Return metatile behavior byte for mt on this layout's tilesets."""
    if mt < 0x200:
        path = REPO / TILESET_ATTR_PATHS.get("gTileset_General", "")
        primary = layout.get("primary_tileset", "gTileset_General")
        path = REPO / TILESET_ATTR_PATHS.get(primary, TILESET_ATTR_PATHS["gTileset_General"])
        idx = mt
    else:
        secondary = layout.get("secondary_tileset", "")
        rel = TILESET_ATTR_PATHS.get(secondary)
        if not rel:
            return -1
        path = REPO / rel
        idx = mt - 0x200
    if not path.exists():
        return -1
    data = path.read_bytes()
    if idx * 4 + 4 > len(data):
        return -1
    return struct.unpack_from("<I", data, idx * 4)[0] & 0xFF


def is_sinnoh(name: str) -> bool:
    if "_Frlg" in name or name.endswith("Frlg"):
        return False
    if name.startswith("Route"):
        digits = "".join(c for c in name[5:] if c.isdigit())
        try:
            if digits and 201 <= int(digits) <= 230:
                return True
        except ValueError:
            pass
        return False
    return any(name.startswith(p) for p in SINNOH_PREFIXES)


def load_map(name: str) -> dict | None:
    p = MAPS / name / "map.json"
    return json.loads(p.read_text()) if p.exists() else None


def load_cells(name: str):
    meta = load_map(name)
    if not meta:
        return None
    L = LAYOUTS_BY_ID.get(meta["layout"]) or LAYOUTS_BY_NAME.get(meta["layout"])
    if not L:
        return None
    w, h = int(L["width"]), int(L["height"])
    path = REPO / L["blockdata_filepath"]
    if not path.exists():
        return None
    data = path.read_bytes()
    cells = []
    for y in range(h):
        row = []
        for x in range(w):
            raw = struct.unpack_from("<H", data, (y * w + x) * 2)[0]
            row.append((raw & 0x3FF, (raw >> 10) & 3, (raw >> 12) & 0xF))
        cells.append(row)
    return cells, w, h, meta, L


def is_walkable(layout: dict, mt: int, coll: int) -> bool:
    if mt in DOOR_METATILES:
        return True
    beh = behavior_for(layout, mt)
    if beh in WARP_DOOR_BEHAVIORS:
        return True
    return coll == 0


def connection_edge_seeds(meta, w, h, cells, layout) -> list[tuple[int, int]]:
    seeds = []
    for conn in meta.get("connections") or []:
        direction = conn.get("direction")
        if direction == "left":
            for y in range(h):
                if is_walkable(layout, *cells[y][0][:2]):
                    seeds.append((0, y))
        elif direction == "right":
            for y in range(h):
                if is_walkable(layout, *cells[y][w - 1][:2]):
                    seeds.append((w - 1, y))
        elif direction == "up":
            for x in range(w):
                if is_walkable(layout, *cells[0][x][:2]):
                    seeds.append((x, 0))
        elif direction == "down":
            for x in range(w):
                if is_walkable(layout, *cells[h - 1][x][:2]):
                    seeds.append((x, h - 1))
    return seeds


def bfs(cells, w, h, layout, seeds):
    seen: set[tuple[int, int]] = set()
    q: deque[tuple[int, int]] = deque()
    for x, y in seeds:
        if 0 <= x < w and 0 <= y < h and is_walkable(layout, *cells[y][x][:2]):
            if (x, y) not in seen:
                seen.add((x, y))
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen:
                if is_walkable(layout, *cells[ny][nx][:2]):
                    seen.add((nx, ny))
                    q.append((nx, ny))
    return seen


def is_outdoor(meta: dict) -> bool:
    if meta.get("connections"):
        return True
    return meta.get("map_type") in OUTDOOR_TYPES


def has_exit(meta, cells, w, h, layout, reachable, origin) -> bool:
    warps = [(int(e["x"]), int(e["y"])) for e in meta.get("warp_events") or []]
    for t in warps:
        if t in reachable:
            return True
    for s in connection_edge_seeds(meta, w, h, cells, layout):
        if s in reachable:
            return True
    return False


def collect_script_warps():
    out = []
    paths = list(MAPS.glob("*/scripts.inc")) + list((REPO / "data/scripts").glob("*.inc"))
    for scripts in paths:
        text = scripts.read_text(errors="replace")
        for m in MAP_CONST_RE.finditer(text):
            out.append((
                str(scripts.relative_to(REPO)),
                m.group("cmd"),
                m.group("map"),
                int(m.group("x")),
                int(m.group("y")),
            ))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    id_to_name = {}
    for d in MAPS.iterdir():
        mj = d / "map.json"
        if mj.exists():
            meta = json.loads(mj.read_text())
            id_to_name[meta["id"]] = meta["name"]

    fails: list[str] = []
    checked = 0

    for src, cmd, map_id, x, y in collect_script_warps():
        name = id_to_name.get(map_id)
        if not name:
            continue
        if not args.all and not is_sinnoh(name):
            continue
        pack = load_cells(name)
        if not pack:
            fails.append(f"{src}: {cmd} {map_id},{x},{y} → missing layout {name}")
            continue
        cells, w, h, meta, layout = pack
        checked += 1
        if not (0 <= x < w and 0 <= y < h):
            fails.append(f"{src}: {cmd} → {name}({x},{y}) OOB {w}x{h}")
            continue
        mt, coll, _ = cells[y][x]
        if not is_walkable(layout, mt, coll):
            fails.append(
                f"{src}: {cmd} → {name}({x},{y}) NOT walkable "
                f"mt=0x{mt:03X} coll={coll} beh=0x{behavior_for(layout, mt):02X}"
            )
            continue
        if is_outdoor(meta):
            reach = bfs(cells, w, h, layout, [(x, y)])
            if not has_exit(meta, cells, w, h, layout, reach, (x, y)):
                fails.append(
                    f"{src}: {cmd} → {name}({x},{y}) walkable but no exit reachable"
                )

    for d in sorted(MAPS.iterdir()):
        if not args.all and not is_sinnoh(d.name):
            continue
        pack = load_cells(d.name)
        if not pack:
            continue
        cells, w, h, meta, layout = pack
        warps = meta.get("warp_events") or []
        if not warps:
            continue

        edge = connection_edge_seeds(meta, w, h, cells, layout)
        seeds = list(edge)
        for ev in warps:
            wx, wy = int(ev["x"]), int(ev["y"])
            if 0 <= wx < w and 0 <= wy < h and is_walkable(layout, *cells[wy][wx][:2]):
                seeds.append((wx, wy))
        reach = bfs(cells, w, h, layout, seeds) if seeds else set()

        for ev in warps:
            wx, wy = int(ev["x"]), int(ev["y"])
            checked += 1
            if not (0 <= wx < w and 0 <= wy < h):
                fails.append(f"{d.name}: warp_event ({wx},{wy}) OOB")
                continue
            mt, coll, _ = cells[wy][wx]
            if not is_walkable(layout, mt, coll):
                fails.append(
                    f"{d.name}: warp_event ({wx},{wy}) → {ev.get('dest_map')} "
                    f"NOT walkable mt=0x{mt:03X} coll={coll} "
                    f"beh=0x{behavior_for(layout, mt):02X}"
                )
                continue
            if edge and (wx, wy) not in reach:
                fails.append(
                    f"{d.name}: warp_event ({wx},{wy}) unreachable from "
                    f"connections/other warps"
                )

            # Dest landing on the other map
            dest_map = ev.get("dest_map")
            try:
                dest_idx = int(str(ev.get("dest_warp_id", "0")), 0)
            except ValueError:
                dest_idx = 0
            dest_name = id_to_name.get(dest_map or "")
            if not dest_name:
                continue
            dpack = load_cells(dest_name)
            if not dpack:
                continue
            dcells, dw, dh, dmeta, dlayout = dpack
            dwarps = dmeta.get("warp_events") or []
            if dest_idx >= len(dwarps):
                # Some stubs point at missing warps — flag it
                fails.append(
                    f"{d.name}: warp→{dest_name}[{dest_idx}] missing warp_event"
                )
                continue
            dx, dy = int(dwarps[dest_idx]["x"]), int(dwarps[dest_idx]["y"])
            checked += 1
            if not (0 <= dx < dw and 0 <= dy < dh):
                fails.append(f"{d.name}: warp→{dest_name}[{dest_idx}] ({dx},{dy}) OOB")
                continue
            dmt, dcoll, _ = dcells[dy][dx]
            if not is_walkable(dlayout, dmt, dcoll):
                fails.append(
                    f"{d.name}: warp→{dest_name}[{dest_idx}] ({dx},{dy}) "
                    f"NOT walkable mt=0x{dmt:03X} coll={dcoll} "
                    f"beh=0x{behavior_for(dlayout, dmt):02X}"
                )

    if fails:
        seen: set[str] = set()
        uniq = []
        for f in fails:
            if f not in seen:
                seen.add(f)
                uniq.append(f)
        print(f"FAIL ({len(uniq)} issues, checked={checked}):")
        for f in uniq[:80]:
            print(" -", f)
        if len(uniq) > 80:
            print(f" ... +{len(uniq) - 80} more")
        return 1
    print(f"=== warp_landing_check: PASS (checked={checked}) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
