#!/usr/bin/env python3
"""
M38: Battle Zone / Frontier gate stub (Fight Area ↔ Frontier entrance).

Land ID: battle_frontier_gate_to_fight_area = MAP_319
Full Battle Frontier outdoor is out of budget — gate is a stub lobby that
loops messages and warps back to Fight Area.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinnoh_build_lib import (  # noqa: E402
    GFX_DEFAULT,
    MAPS,
    PLAT_MAPS,
    face,
    find_walkable,
    grid_from_chunks,
    obj,
    pack,
    register_maps,
    scrub,
    warp,
    write_layout,
    write_map,
)

GATE = ("BattleFrontier_Gate_Sinnoh", [[319]], "battle_frontier_gate_to_fight_area", "MAP_BATTLE_FRONTIER_GATE_SINNOH", "LAYOUT_BATTLE_FRONTIER_GATE_SINNOH")
FA_ORIGIN = (608, 416)  # FightArea documented origin


def densify_gate(em, plat, w, h):
    pe = json.loads((PLAT_MAPS / plat / "events.json").read_text())
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    warps = []
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"]), int(po["z"])
        if not (0 <= lx < w and 0 <= ly < h) or (lx, ly) in occupied:
            continue
        occupied.add((lx, ly))
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_MAN_3")
        label = f"{em}_EventScript_Npc{n}"
        objs.append(obj(gfx, lx, ly, label, movement=face(po.get("initial_dir"))))
        scripts += (
            f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
            f'{label}_Text:\n\t.string "The Battle Frontier is still under\\n"\n'
            f'\t.string "construction in this demo. Come back later!$"\n\n'
        )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        if not (0 <= lx < w and 0 <= ly < h):
            continue
        dest = (pw.get("dest_header_id") or "").upper()
        if "FIGHT_AREA" in dest:
            warps.append(warp(lx, ly, "MAP_FIGHT_AREA", 0))
        else:
            # Frontier outdoor → stay in gate (stub loop) via south exit
            warps.append(warp(lx, ly, "MAP_FIGHT_AREA", 0))
    return objs, scripts, warps


def main() -> int:
    name, chunks, plat, mid, layout = GATE
    grid, w, h = grid_from_chunks(chunks, cave=False)
    write_layout(name, w, h, "gTileset_Building", "gTileset_Facility", pack(grid), lid=layout)
    objs, scripts, warps = densify_gate(name, plat, w, h)
    if not warps:
        sx, sy = find_walkable(grid, prefer=(w // 2, h - 2))
        warps = [warp(sx, sy, "MAP_FIGHT_AREA", 0)]
    # Receptionist notice
    if not any("FrontierClosed" in (o.get("script") or "") for o in objs):
        rx, ry = find_walkable(grid, prefer=(w // 2, 4))
        objs.append(obj("OBJ_EVENT_GFX_TEALA", rx, ry, f"{name}_EventScript_Clerk"))
        scripts += f"""
{name}_EventScript_Clerk::
	msgbox {name}_Text_Clerk, MSGBOX_NPC
	end

{name}_Text_Clerk:
	.string "Welcome to the Battle Frontier gate.\\n"
	.string "The facilities open after further work.$"
"""
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": layout,
            "music": "MUS_B_TOWER_RS",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_BATTLE_FRONTIER",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # Wire Fight Area Platinum frontier-gate warps
    fa = json.loads((MAPS / "FightArea" / "map.json").read_text())
    pe = json.loads((PLAT_MAPS / "fight_area" / "events.json").read_text())
    ox, oz = FA_ORIGIN
    existing = {(w["x"], w["y"]) for w in fa.get("warp_events") or []}
    for pw in pe.get("warp_events") or []:
        dest = (pw.get("dest_header_id") or "").upper()
        if "FRONTIER" not in dest and "BATTLE_FRONTIER_GATE" not in dest:
            continue
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if not (0 <= lx < 64 and 0 <= ly < 32):
            continue
        if (lx, ly) in existing:
            for w in fa["warp_events"]:
                if w["x"] == lx and w["y"] == ly:
                    w["dest_map"] = mid
                    w["dest_warp_id"] = "3"  # south exit cluster ~index 3
            continue
        fa.setdefault("warp_events", []).append(warp(lx, ly, mid, 3))
        existing.add((lx, ly))
    # Fix gate south warps to land on Fight Area frontier door tiles
    gate = json.loads((MAPS / name / "map.json").read_text())
    # Find FA local coords of frontier door
    fa_door = None
    for pw in pe.get("warp_events") or []:
        if "FRONTIER" in (pw.get("dest_header_id") or "").upper():
            fa_door = (int(pw["x"] - ox), int(pw["z"] - oz))
            break
    # After writing FA, find warp index of first frontier door
    (MAPS / "FightArea" / "map.json").write_text(json.dumps(fa, indent=2) + "\n")
    fa = json.loads((MAPS / "FightArea" / "map.json").read_text())
    door_idx = 0
    for i, w in enumerate(fa.get("warp_events") or []):
        if w.get("dest_map") == mid:
            door_idx = i
            break
    for w in gate.get("warp_events") or []:
        if w.get("dest_map") == "MAP_FIGHT_AREA":
            w["dest_warp_id"] = str(door_idx)
    (MAPS / name / "map.json").write_text(json.dumps(gate, indent=2) + "\n")

    register_maps([], [name], "gMapGroup_IndoorM38FrontierGate")
    scrub([name, "FightArea"])
    print("M38 Battle Frontier gate stub build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
