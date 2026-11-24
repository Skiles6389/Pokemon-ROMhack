#!/usr/bin/env python3
"""
Postgame M32: Route 224 / 225 + Fight Area (+ VR backside rooms to reach R224).

Land IDs:
  VictoryRoad_Sinnoh_Room1 [[425]]
  VictoryRoad_Sinnoh_Room2 [[421,422],[423,424]]
  VictoryRoad_Sinnoh_Room3 [[426]]
  Route224 [[None,115],[116,117],[118,None]] origin (864,480)
  Route225 [[163,166],[164,None],[165,None]] origin (608,320)
  FightArea [[132,133]] origin (608,416)

Soft-closes Survival Area north of Fight Area / R225.
Fight Area ferry dialogue gated on FLAG_SYS_GAME_CLEAR.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinnoh_build_lib import (  # noqa: E402
    GFX_DEFAULT,
    MAPS,
    PLAT_MAPS,
    clear_plat_walkables,
    ensure_trainer,
    face,
    find_walkable,
    grid_from_chunks,
    indoor_room,
    obj,
    pack,
    register_maps,
    scrub,
    warp,
    write_layout,
    write_map,
    MT_WATER,
)

VR1 = [[425]]
VR2 = [[421, 422], [423, 424]]
VR3 = [[426]]
R224 = [[None, 115], [116, 117], [118, None]]
R225 = [[163, 166], [164, None], [165, None]]
FIGHT = [[132, 133]]
R224_ORIGIN = (27 * 32, 15 * 32)  # 864, 480
R225_ORIGIN = (19 * 32, 10 * 32)  # 608, 320
FIGHT_ORIGIN = (19 * 32, 13 * 32)  # 608, 416


def densify_world(em, plat, origin, w, h, level, flavor="post"):
    pe_path = PLAT_MAPS / plat / "events.json"
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    warps = []
    if not pe_path.exists():
        return objs, scripts, warps
    pe = json.loads(pe_path.read_text())
    ox, oz = origin
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"] - ox), int(po["z"] - oz)
        if not (0 <= lx < w and 0 <= ly < h) or (lx, ly) in occupied:
            continue
        occupied.add((lx, ly))
        tr = po.get("trainer") or {}
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_MAN_5")
        if tr.get("id"):
            tid = tr["id"] if str(tr["id"]).startswith("TRAINER_") else f"TRAINER_{tr['id']}"
            tid = re.sub(r"[^A-Z0-9_]", "_", tid.upper())
            if not tid.startswith("TRAINER_"):
                tid = "TRAINER_" + tid
            if not tid.endswith("_PG"):
                tid = tid + "_PG"
            ensure_trainer(
                tid,
                level,
                "Cooltrainer",
                "Cooltrainer M",
                [("Floatzel", level), ("Luxray", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title(),
                tag="Sinnoh Postgame",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(
                obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2), movement=face(po.get("initial_dir")))
            )
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f'{label}_Intro:\n\t.string "Postgame trainers do not hold back!$"\n\n'
                f'{label}_Defeat:\n\t.string "Outclassed...$"\n\n'
                f'{label}_After:\n\t.string "The Battle Zone is just getting started.$"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "The Fight Area draws champions from every region.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or "", pw.get("id") or ""))
    return objs, scripts, warps


def densify_local(em, plat, w, h, level):
    pe_path = PLAT_MAPS / plat / "events.json"
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    warps = []
    if not pe_path.exists():
        return objs, scripts, warps
    pe = json.loads(pe_path.read_text())
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"]), int(po["z"])
        if not (0 <= lx < w and 0 <= ly < h) or (lx, ly) in occupied:
            continue
        occupied.add((lx, ly))
        tr = po.get("trainer") or {}
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_HIKER")
        if tr.get("id"):
            tid = tr["id"] if str(tr["id"]).startswith("TRAINER_") else f"TRAINER_{tr['id']}"
            tid = re.sub(r"[^A-Z0-9_]", "_", tid.upper())
            if not tid.startswith("TRAINER_"):
                tid = "TRAINER_" + tid
            if not tid.endswith("_PG"):
                tid = tid + "_PG"
            ensure_trainer(
                tid,
                level,
                "Hiker",
                "Hiker",
                [("Onix", level), ("Graveler", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title(),
                tag="Sinnoh Postgame",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2)))
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f'{label}_Intro:\n\t.string "Victory Road still has teeth!$"\n\n'
                f'{label}_Defeat:\n\t.string "Cracked...$"\n\n'
                f'{label}_After:\n\t.string "Route 224 waits beyond these chambers.$"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "These side chambers lead toward Route 224.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or "", pw.get("id") or ""))
    return objs, scripts, warps


def map_outdoor(name, mid, layout, chunks, origin, plat, level, connections, music="MUS_RG_ROUTE1"):
    grid, w, h, coll = grid_from_chunks(chunks)
    clear_plat_walkables(grid, chunks)
    write_layout(name, w, h, "gTileset_General", "gTileset_Petalburg", pack(grid, coll))
    objs, scripts, vwarps = densify_world(name, plat, origin, w, h, level)
    # Resolve warps to known dests where possible
    warps = []
    for lx, ly, dest, wid in vwarps:
        dmap = "MAP_" + name.upper()  # fallback self
        if "ROUTE_224" in dest:
            dmap = "MAP_ROUTE224"
        elif "ROUTE_225" in dest:
            dmap = "MAP_ROUTE225"
        elif "FIGHT_AREA" in dest:
            dmap = "MAP_FIGHT_AREA"
        elif "VICTORY_ROAD_1F_ROOM_3" in dest or "ROOM_3" in dest:
            dmap = "MAP_VICTORY_ROAD_SINNOH_ROOM3"
        elif "VICTORY_ROAD_1F_ROOM_2" in dest or "ROOM_2" in dest:
            dmap = "MAP_VICTORY_ROAD_SINNOH_ROOM2"
        elif "VICTORY_ROAD_1F_ROOM_1" in dest or "ROOM_1" in dest:
            dmap = "MAP_VICTORY_ROAD_SINNOH_ROOM1"
        elif "VICTORY_ROAD_1F" in dest:
            dmap = "MAP_VICTORY_ROAD_SINNOH_1F"
        elif "GATE" in dest:
            continue  # skip unbuilt gates for now
        warps.append(warp(lx, ly, dmap, 0))
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": layout,
            "music": music,
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_ROUTE",
            "allow_cycling": True,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": connections,
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )
    return w, h


def main() -> int:
    indoor = []

    # --- VR backside rooms (replace stub Room1) ---
    for name, chunks, plat, mid, layout in [
        ("VictoryRoad_Sinnoh_Room1", VR1, "victory_road_1f_room_1", "MAP_VICTORY_ROAD_SINNOH_ROOM1", "LAYOUT_VICTORY_ROAD_SINNOH_ROOM1"),
        ("VictoryRoad_Sinnoh_Room2", VR2, "victory_road_1f_room_2", "MAP_VICTORY_ROAD_SINNOH_ROOM2", "LAYOUT_VICTORY_ROAD_SINNOH_ROOM2"),
        ("VictoryRoad_Sinnoh_Room3", VR3, "victory_road_1f_room_3", "MAP_VICTORY_ROAD_SINNOH_ROOM3", "LAYOUT_VICTORY_ROAD_SINNOH_ROOM3"),
    ]:
        grid, w, h, coll = grid_from_chunks(chunks, cave=True)
        clear_plat_walkables(grid, chunks, cave=True)
        write_layout(name, w, h, "gTileset_General", "gTileset_Cave", pack(grid, coll))
        objs, scripts, vwarps = densify_local(name, plat, w, h, 48)
        warps = []
        for lx, ly, dest, wid in vwarps:
            if "ROOM_2" in dest:
                dmap = "MAP_VICTORY_ROAD_SINNOH_ROOM2"
            elif "ROOM_3" in dest:
                dmap = "MAP_VICTORY_ROAD_SINNOH_ROOM3"
            elif "ROOM_1" in dest:
                dmap = "MAP_VICTORY_ROAD_SINNOH_ROOM1"
            elif "ROUTE_224" in dest:
                dmap = "MAP_ROUTE224"
            else:
                dmap = "MAP_VICTORY_ROAD_SINNOH_1F"
            warps.append(warp(lx, ly, dmap, 0))
        if not warps:
            warps = [warp(w // 2, h - 2, "MAP_VICTORY_ROAD_SINNOH_1F", 6)]
        write_map(
            name,
            {
                "id": mid,
                "name": name,
                "layout": layout,
                "music": "MUS_VICTORY_ROAD",
                "region": "REGION_HOENN",
                "region_map_section": "MAPSEC_ROUTE_213",
                "requires_flash": False,
                "weather": "WEATHER_NONE",
                "map_type": "MAP_TYPE_UNDERGROUND",
                "allow_cycling": True,
                "allow_escaping": True,
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
        indoor.append(name)

    # --- Route 224 ---
    map_outdoor(
        "Route224",
        "MAP_ROUTE224",
        "LAYOUT_ROUTE224",
        R224,
        R224_ORIGIN,
        "route_224",
        50,
        connections=[
            {"map": "MAP_ROUTE225", "offset": 0, "direction": "left"},
        ],
        music="MUS_RG_ROUTE1",
    )
    # Soft note NPC if music constant missing - check later

    # --- Route 225 ---
    # Soft-close Survival to the north
    grid, w, h, coll = grid_from_chunks(R225)
    clear_plat_walkables(grid, R225)
    write_layout("Route225", w, h, "gTileset_General", "gTileset_Petalburg", pack(grid, coll))
    objs, scripts, vwarps = densify_world("Route225", "route_225", R225_ORIGIN, w, h, 50)
    # Soft-close north toward Survival
    nx, ny = find_walkable(grid, prefer=(w // 2, 1))
    objs.append(obj("OBJ_EVENT_GFX_MAN_2", nx, ny, "Route225_EventScript_SurvivalClosed", movement="MOVEMENT_TYPE_FACE_DOWN"))
    scripts += """
Route225_EventScript_SurvivalClosed::
	lock
	faceplayer
	msgbox Route225_Text_SurvivalClosed, MSGBOX_DEFAULT
	release
	end

Route225_Text_SurvivalClosed:
	.string "Survival Area opens in a later postgame\\n"
	.string "build. Train in the Fight Area for now.$"
"""
    warps = []
    for lx, ly, dest, wid in vwarps:
        if "FIGHT" in dest:
            warps.append(warp(lx, ly, "MAP_FIGHT_AREA", 0))
        elif "GATE" in dest:
            warps.append(warp(lx, ly, "MAP_FIGHT_AREA", 0))
        elif "HOUSE" in dest:
            continue
        elif "224" in dest:
            warps.append(warp(lx, ly, "MAP_ROUTE224", 0))
    write_map(
        "Route225",
        {
            "id": "MAP_ROUTE225",
            "name": "Route225",
            "layout": "LAYOUT_ROUTE225",
            "music": "MUS_RG_ROUTE1",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_ROUTE",
            "allow_cycling": True,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": [
                {"map": "MAP_FIGHT_AREA", "offset": 0, "direction": "down"},
                {"map": "MAP_ROUTE224", "offset": 0, "direction": "right"},
            ],
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # --- Fight Area ---
    grid, w, h, coll = grid_from_chunks(FIGHT)
    clear_plat_walkables(grid, FIGHT)
    write_layout("FightArea", w, h, "gTileset_General", "gTileset_Petalburg", pack(grid, coll))
    objs, scripts, vwarps = densify_world("FightArea", "fight_area", FIGHT_ORIGIN, w, h, 50)
    # Game-clear gated sailor / clerk
    sx, sy = find_walkable(grid, prefer=(w // 2, h - 3))
    objs.append(obj("OBJ_EVENT_GFX_SAILOR", sx, sy, "FightArea_EventScript_PostgameClerk"))
    scripts += """
FightArea_EventScript_PostgameClerk::
	lock
	faceplayer
	goto_if_unset FLAG_SYS_GAME_CLEAR, FightArea_EventScript_NotChampion
	msgbox FightArea_Text_WelcomeChamp, MSGBOX_DEFAULT
	release
	end

FightArea_EventScript_NotChampion::
	msgbox FightArea_Text_NotChampion, MSGBOX_DEFAULT
	release
	end

FightArea_Text_WelcomeChamp:
	.string "Welcome to the Fight Area, Champion!\\n"
	.string "Survival and Resort Areas open soon.$"

FightArea_Text_NotChampion:
	.string "The Battle Zone is for League Champions.\\n"
	.string "Defeat Cynthia, then sail back here.$"
"""
    # Soft-close Battle Frontier / Survival stubs
    fx, fy = find_walkable(grid, prefer=(2, 2))
    objs.append(obj("OBJ_EVENT_GFX_MAN_2", fx, fy, "FightArea_EventScript_FrontierClosed", movement="MOVEMENT_TYPE_FACE_DOWN"))
    scripts += """
FightArea_EventScript_FrontierClosed::
	msgbox FightArea_Text_FrontierClosed, MSGBOX_NPC
	end

FightArea_Text_FrontierClosed:
	.string "The Battle Frontier gate is still sealed.\\n"
	.string "A later build will open the Battle Zone.$"
"""
    warps = []
    for lx, ly, dest, wid in vwarps:
        if "POKECENTER" in dest or "MART" in dest or "HOUSE" in dest:
            continue
        if "225" in dest or "GATE" in dest:
            warps.append(warp(lx, ly, "MAP_ROUTE225", 0))
        elif "FRONTIER" in dest or "BATTLE" in dest:
            continue
    # Minimal PC stub
    lid, _, _ = indoor_room("FightArea_PokemonCenter_1F", w=10, h=8)
    indoor.append("FightArea_PokemonCenter_1F")
    pc_x, pc_y = find_walkable(grid, prefer=(w // 2, h // 2))
    warps.append(warp(pc_x, pc_y, "MAP_FIGHT_AREA_POKEMON_CENTER_1F", 0))
    write_map(
        "FightArea_PokemonCenter_1F",
        {
            "id": "MAP_FIGHT_AREA_POKEMON_CENTER_1F",
            "name": "FightArea_PokemonCenter_1F",
            "layout": "LAYOUT_FIGHT_AREA_POKEMON_CENTER_1_F",
            "music": "MUS_POKE_CENTER",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [
                {**obj("OBJ_EVENT_GFX_NURSE", 4, 3, "FightArea_PokemonCenter_1F_EventScript_Nurse"), "local_id": "LOCALID_NURSE"},
            ],
            "warp_events": [
                warp(4, 7, "MAP_FIGHT_AREA", 0),
                warp(5, 7, "MAP_FIGHT_AREA", 0),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        """FightArea_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FightArea_PokemonCenter_1F_OnTransition
	.byte 0

FightArea_PokemonCenter_1F_OnTransition::
	setrespawn HEAL_LOCATION_EVER_GRANDE_CITY
	end

FightArea_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end
""",
    )

    write_map(
        "FightArea",
        {
            "id": "MAP_FIGHT_AREA",
            "name": "FightArea",
            "layout": "LAYOUT_FIGHT_AREA",
            "music": "MUS_RG_PEWTER",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_TOWN",
            "allow_cycling": True,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": [
                {"map": "MAP_ROUTE225", "offset": 0, "direction": "up"},
            ],
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    outdoor = ["Route224", "Route225", "FightArea"]
    # Room1 already registered by M28/M29; only register new rooms + PC
    indoor_new = [n for n in indoor if n != "VictoryRoad_Sinnoh_Room1"]
    register_maps(outdoor, indoor_new, "gMapGroup_IndoorM32PostgameFight")
    scrub(outdoor + indoor)
    print("Postgame Fight Area build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
