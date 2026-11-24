#!/usr/bin/env python3
"""
Sunyshore / Volkner (Beacon Badge) — Platinum order after Distortion World.

Land IDs (TownsAndRoutes matrix):
  Route222        [[149, 150, 151]]           96x32 origin (736, 768)
  SunyshoreCity   [[96, 97], [98, 99]]        64x64 origin (832, 736)
  Gym rooms       296 / 297 / 298

Also: Route222 gate + city interiors (PC/Mart/houses) as Emerald indoor stubs.
Soft-closes Route 223 / League approach for M29 Victory Road.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinnoh_build_lib import (  # noqa: E402
    FLAGS,
    GFX_DEFAULT,
    MAPS,
    PLAT_MAPS,
    clear_plat_walkables,
    ensure_flag,
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
)

TMS = Path(__file__).resolve().parents[2] / "include" / "constants" / "tms_hms.h"

ROUTE222 = [[149, 150, 151]]
SUNYSHORE = [[96, 97], [98, 99]]
R222_ORIGIN = (736, 768)
SUNY_ORIGIN = (832, 736)


def ensure_discharge_tm():
    t = TMS.read_text()
    if "F(DISCHARGE)" not in t:
        t = t.replace("F(AVALANCHE)", "F(AVALANCHE) \\\n    F(DISCHARGE)")
        TMS.write_text(t)
        print("added DISCHARGE TM")


def stamp_door(grid, x, y, floor=0x001):
    for dy, row in enumerate([[0x210, 0x211, 0x212], [0x218, 0x219, 0x21A], [0x222, 0x230, 0x221]]):
        for dx, mt in enumerate(row):
            sx, sy = x - 1 + dx, y - 2 + dy
            if 0 <= sy < len(grid) and 0 <= sx < len(grid[0]) and not (sx == x and sy == y):
                grid[sy][sx] = mt
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x] = floor


def densify(em, plat, origin, w, h, level, text_after="Sunyshore's Gym runs on electricity.$"):
    pe = json.loads((PLAT_MAPS / plat / "events.json").read_text())
    ox, oz = origin
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"] - ox), int(po["z"] - oz)
        if not (0 <= lx < w and 0 <= ly < h) or (lx, ly) in occupied:
            continue
        occupied.add((lx, ly))
        tr = po.get("trainer") or {}
        gfx_src = po.get("graphics_id") or ""
        gfx = GFX_DEFAULT.get(gfx_src, "OBJ_EVENT_GFX_MAN_5")
        if "BALL" in gfx_src.upper() or "ITEM" in gfx_src.upper():
            gfx = "OBJ_EVENT_GFX_ITEM_BALL"
        if tr.get("id"):
            tid = tr["id"] if str(tr["id"]).startswith("TRAINER_") else f"TRAINER_{tr['id']}"
            # sanitize unique local trainer ids
            tid = re.sub(r"[^A-Z0-9_]", "_", tid.upper())
            if not tid.startswith("TRAINER_"):
                tid = "TRAINER_" + tid
            ensure_trainer(
                tid,
                level,
                "Youngster",
                "Youngster",
                [("Magnemite", level), ("Pikachu", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title(),
                tag="Sinnoh Sunyshore",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(
                obj(
                    gfx,
                    lx,
                    ly,
                    label,
                    trainer="TRAINER_TYPE_NORMAL",
                    sight=str(tr.get("sight_range") or 2),
                    movement=face(po.get("initial_dir")),
                )
            )
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f'{label}_Intro:\n\t.string "Surf and spark!\\n"\n\t.string "Route 222 trains for Volkner!$"\n\n'
                f'{label}_Defeat:\n\t.string "Shorted out.$"\n\n'
                f'{label}_After:\n\t.string "{text_after}"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "Sunyshore never sleeps.\\n"\n\t.string "The lighthouse keeps the tide honest.$"\n\n'
            )
        n += 1
    warps = []
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or "", pw.get("id") or ""))
    return objs, scripts, warps, pe


def indoor(name, mid, mapsec, exit_map, exit_wid, label, text, gfx="OBJ_EVENT_GFX_OLD_WOMAN"):
    lid, w, h = indoor_room(name, w=10, h=8, north_door=False)
    # rewrite smaller using GenericBuilding like m25
    from sinnoh_build_lib import IN_DOOR, IN_FLOOR, IN_WALL

    grid = [
        [IN_WALL if y in (0, 7) or x in (0, 9) else (IN_DOOR if y == 7 and x in (4, 5) else IN_FLOOR) for x in range(10)]
        for y in range(8)
    ]
    lid = write_layout(name, 10, 8, "gTileset_Building", "gTileset_GenericBuilding", pack(grid))
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": lid,
            "music": "MUS_PL_JUBILIFE",
            "region": "REGION_HOENN",
            "region_map_section": mapsec,
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [obj(gfx, 4, 3, label)],
            "warp_events": [warp(4, 7, exit_map, exit_wid), warp(5, 7, exit_map, exit_wid)],
            "coord_events": [],
            "bg_events": [],
        },
        f"{name}_MapScripts::\n\t.byte 0\n\n{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n{label}_Text:\n\t.string \"{text}\"\n",
    )


def build_gym():
    ensure_flag("FLAG_RECEIVED_SUNYSHORE_GYM_TM", "0x2B5", "Sinnoh Sunyshore Volkner TM")
    # Stitch gym room 1 as approach; Volkner in room 3 land 298
    for name, chunks, mid in [
        ("SunyshoreCity_Gym_Room1", [[296]], "MAP_SUNYSHORE_CITY_GYM_ROOM1"),
        ("SunyshoreCity_Gym_Room2", [[297]], "MAP_SUNYSHORE_CITY_GYM_ROOM2"),
        ("SunyshoreCity_Gym_VolknersRoom", [[298]], "MAP_SUNYSHORE_CITY_GYM_VOLKNERS_ROOM"),
    ]:
        grid, w, h = grid_from_chunks(chunks, cave=False)
        clear_plat_walkables(grid, chunks)
        write_layout(name, w, h, "gTileset_Building", "gTileset_Facility", pack(grid))

    ensure_trainer(
        "TRAINER_LEADER_VOLKNER",
        49,
        "Leader",
        "Leader Wattson",
        [("Raichu", 46), ("Ambipom", 47), ("Octillery", 47), ("Luxray", 49)],
        display_name="Volkner",
        tag="Sinnoh Sunyshore",
    )
    ensure_trainer("TRAINER_GUITARIST_SUNY_A", 44, "Guitarist", "Guitarist", [("Magnemite", 44)], "Jerry", tag="Sinnoh Sunyshore")
    ensure_trainer("TRAINER_GUITARIST_SUNY_B", 45, "Guitarist", "Guitarist", [("Elekid", 45)], "Lonnie", tag="Sinnoh Sunyshore")

    # Room1: from city, up to room2
    write_map(
        "SunyshoreCity_Gym_Room1",
        {
            "id": "MAP_SUNYSHORE_CITY_GYM_ROOM1",
            "name": "SunyshoreCity_Gym_Room1",
            "layout": "LAYOUT_SUNYSHORE_CITY_GYM_ROOM1",
            "music": "MUS_GYM",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": False,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_GYM",
            "connections": None,
            "object_events": [
                obj("OBJ_EVENT_GFX_MAN_2", 8, 14, "SunyshoreCity_Gym_EventScript_Guide"),
                obj(
                    "OBJ_EVENT_GFX_MAN_5",
                    5,
                    8,
                    "SunyshoreCity_Gym_EventScript_Jerry",
                    trainer="TRAINER_TYPE_NORMAL",
                    sight="3",
                ),
            ],
            "warp_events": [
                warp(8, 15, "MAP_SUNYSHORE_CITY", 12),
                warp(9, 15, "MAP_SUNYSHORE_CITY", 12),
                warp(8, 1, "MAP_SUNYSHORE_CITY_GYM_ROOM2", 0),
                warp(9, 1, "MAP_SUNYSHORE_CITY_GYM_ROOM2", 1),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "SunyshoreCity_Gym_Room1_MapScripts::\n\t.byte 0\n\n"
        "SunyshoreCity_Gym_EventScript_Jerry::\n"
        "\ttrainerbattle_single TRAINER_GUITARIST_SUNY_A, SunyshoreCity_Gym_Text_JerryIntro, SunyshoreCity_Gym_Text_JerryDefeat\n"
        "\tmsgbox SunyshoreCity_Gym_Text_JerryAfter, MSGBOX_AUTOCLOSE\n\tend\n\n"
        "SunyshoreCity_Gym_EventScript_Guide::\n"
        "\tlock\n\tfaceplayer\n"
        "\tgoto_if_set FLAG_BADGE08_GET, SunyshoreCity_Gym_EventScript_GuideWon\n"
        "\tmsgbox SunyshoreCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        "SunyshoreCity_Gym_EventScript_GuideWon::\n"
        "\tmsgbox SunyshoreCity_Gym_Text_GuideWon, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        'SunyshoreCity_Gym_Text_JerryIntro:\n\t.string "Feel that bass drop?\\n"\n\t.string "Electric types love the beat!$"\n\n'
        'SunyshoreCity_Gym_Text_JerryDefeat:\n\t.string "Unplugged...$"\n\n'
        'SunyshoreCity_Gym_Text_JerryAfter:\n\t.string "Volkner is upstairs in the last room.$"\n\n'
        'SunyshoreCity_Gym_Text_GuideAdvice:\n\t.string "Volkner thrives on Electric-type pressure.\\n"\n\t.string "Ground moves cut the circuit.$"\n\n'
        'SunyshoreCity_Gym_Text_GuideWon:\n\t.string "Beacon Badge earned!\\n"\n\t.string "Victory Road is next along Route 223.$"\n',
    )

    write_map(
        "SunyshoreCity_Gym_Room2",
        {
            "id": "MAP_SUNYSHORE_CITY_GYM_ROOM2",
            "name": "SunyshoreCity_Gym_Room2",
            "layout": "LAYOUT_SUNYSHORE_CITY_GYM_ROOM2",
            "music": "MUS_GYM",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": False,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_GYM",
            "connections": None,
            "object_events": [
                obj(
                    "OBJ_EVENT_GFX_MAN_5",
                    10,
                    8,
                    "SunyshoreCity_Gym_EventScript_Lonnie",
                    trainer="TRAINER_TYPE_NORMAL",
                    sight="3",
                ),
            ],
            "warp_events": [
                warp(8, 15, "MAP_SUNYSHORE_CITY_GYM_ROOM1", 2),
                warp(9, 15, "MAP_SUNYSHORE_CITY_GYM_ROOM1", 3),
                warp(8, 1, "MAP_SUNYSHORE_CITY_GYM_VOLKNERS_ROOM", 0),
                warp(9, 1, "MAP_SUNYSHORE_CITY_GYM_VOLKNERS_ROOM", 1),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "SunyshoreCity_Gym_Room2_MapScripts::\n\t.byte 0\n\n"
        "SunyshoreCity_Gym_EventScript_Lonnie::\n"
        "\ttrainerbattle_single TRAINER_GUITARIST_SUNY_B, SunyshoreCity_Gym_Text_LonnieIntro, SunyshoreCity_Gym_Text_LonnieDefeat\n"
        "\tmsgbox SunyshoreCity_Gym_Text_LonnieAfter, MSGBOX_AUTOCLOSE\n\tend\n\n"
        'SunyshoreCity_Gym_Text_LonnieIntro:\n\t.string "Amp it up!$"\n\n'
        'SunyshoreCity_Gym_Text_LonnieDefeat:\n\t.string "Blown fuse...$"\n\n'
        'SunyshoreCity_Gym_Text_LonnieAfter:\n\t.string "Volkner is just ahead.$"\n',
    )

    write_map(
        "SunyshoreCity_Gym_VolknersRoom",
        {
            "id": "MAP_SUNYSHORE_CITY_GYM_VOLKNERS_ROOM",
            "name": "SunyshoreCity_Gym_VolknersRoom",
            "layout": "LAYOUT_SUNYSHORE_CITY_GYM_VOLKNERS_ROOM",
            "music": "MUS_GYM",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": False,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_GYM",
            "connections": None,
            "object_events": [
                obj("OBJ_EVENT_GFX_MAN_3", 8, 4, "SunyshoreCity_Gym_EventScript_Volkner"),
            ],
            "warp_events": [
                warp(8, 15, "MAP_SUNYSHORE_CITY_GYM_ROOM2", 2),
                warp(9, 15, "MAP_SUNYSHORE_CITY_GYM_ROOM2", 3),
            ],
            "coord_events": [],
            "bg_events": [
                {
                    "type": "sign",
                    "x": 7,
                    "y": 13,
                    "elevation": 0,
                    "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                    "script": "SunyshoreCity_Gym_EventScript_Statue",
                },
                {
                    "type": "sign",
                    "x": 10,
                    "y": 13,
                    "elevation": 0,
                    "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                    "script": "SunyshoreCity_Gym_EventScript_Statue",
                },
            ],
        },
        r"""SunyshoreCity_Gym_VolknersRoom_MapScripts::
	.byte 0

SunyshoreCity_Gym_EventScript_Volkner::
	lock
	faceplayer
	trainerbattle_single TRAINER_LEADER_VOLKNER, SunyshoreCity_Gym_Text_VolknerIntro, SunyshoreCity_Gym_Text_VolknerDefeat, SunyshoreCity_Gym_EventScript_VolknerDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_SUNYSHORE_GYM_TM, SunyshoreCity_Gym_EventScript_GiveTM
	msgbox SunyshoreCity_Gym_Text_VolknerAfter, MSGBOX_DEFAULT
	release
	end

SunyshoreCity_Gym_EventScript_VolknerDefeated::
	message SunyshoreCity_Gym_Text_ReceivedBeaconBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox SunyshoreCity_Gym_Text_BeaconBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE08_GET
	goto SunyshoreCity_Gym_EventScript_GiveTM
	end

SunyshoreCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_DISCHARGE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_SUNYSHORE_GYM_TM
	msgbox SunyshoreCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

SunyshoreCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE08_GET, SunyshoreCity_Gym_EventScript_StatueWon
	msgbox SunyshoreCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

SunyshoreCity_Gym_EventScript_StatueWon::
	msgbox SunyshoreCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

SunyshoreCity_Gym_Text_VolknerIntro:
	.string "I'm VOLKNER, the Sunyshore Gym Leader!\n"
	.string "Electric types never get boring when you\l"
	.string "keep inventing new circuits.\p"
	.string "Let's see if you can short my design!$"

SunyshoreCity_Gym_Text_VolknerDefeat:
	.string "You overcharged my plans...$"

SunyshoreCity_Gym_Text_VolknerAfter:
	.string "Take Route 223 north when you're ready.\n"
	.string "Victory Road waits beyond the surf.$"

SunyshoreCity_Gym_Text_ReceivedBeaconBadge:
	.string "{PLAYER} received the BEACON BADGE\n"
	.string "from VOLKNER.$"

SunyshoreCity_Gym_Text_BeaconBadgeInfo:
	.string "With the BEACON BADGE, every machine\n"
	.string "recognizes your team's full voltage.$"

SunyshoreCity_Gym_Text_ExplainTM:
	.string "That's TM Discharge.\n"
	.string "It shocks everything around the user.$"

SunyshoreCity_Gym_Text_Statue:
	.string "Sunyshore City Pokemon Gym$"

SunyshoreCity_Gym_Text_StatueWon:
	.string "Sunyshore City Pokemon Gym\n"
	.string "Certified Trainer: {PLAYER}$"
""",
    )


def main():
    ensure_discharge_tm()
    ensure_flag("FLAG_RECEIVED_SUNYSHORE_GYM_TM", "0x2B5", "Sinnoh Sunyshore Volkner TM")

    # --- Route 222 ---
    grid, w, h = grid_from_chunks(ROUTE222)
    clear_plat_walkables(grid, ROUTE222)
    objs, scripts, plat_warps, _ = densify("Route222", "route_222", R222_ORIGIN, w, h, 42)
    warps = []
    # Map platinum warps to interiors / gate
    # We'll create gate + 2 houses; align warp indices carefully
    # After creating indoors, set dests:
    # For now collect positions; stamp doors
    for lx, ly, dest, wid in plat_warps:
        stamp_door(grid, lx, ly)
    write_layout("Route222", w, h, "gTileset_General", "gTileset_Dewford", pack(grid))

    # Soft-close NPC toward water / league for later
    sx, sy = find_walkable(grid, prefer=(w - 3, h // 2))
    objs.append(obj("OBJ_EVENT_GFX_SAILOR", sx, sy, "Route222_EventScript_SoftClose"))
    scripts += (
        "Route222_EventScript_SoftClose::\n"
        "\tmsgbox Route222_Text_SoftClose, MSGBOX_NPC\n\tend\n\n"
        'Route222_Text_SoftClose:\n\t.string "Sunyshore is through the east gate.\\n"\n'
        '\t.string "Route 223 stays closed until Volkner falls.$"\n\n'
    )

    # Place warps: gate (2), west house, east house — match first 4 plat warps order from earlier dump
    # plat order: gate, gate, east house, west house at (89,22),(89,23),(65,16),(59,16)
    gate_map = "MAP_ROUTE222_GATE_TO_SUNYSHORE"
    warps = [
        warp(89, 22, gate_map, 0),
        warp(89, 23, gate_map, 1),
        warp(65, 16, "MAP_ROUTE222_EAST_HOUSE", 0),
        warp(59, 16, "MAP_ROUTE222_WEST_HOUSE", 0),
    ]
    write_map(
        "Route222",
        {
            "id": "MAP_ROUTE222",
            "name": "Route222",
            "layout": "LAYOUT_ROUTE222",
            "music": "MUS_ROUTE110",
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
                {"map": "MAP_VALOR_LAKEFRONT", "offset": -32, "direction": "left"},
                {"map": "MAP_SUNYSHORE_CITY", "offset": -32, "direction": "right"},
            ],
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    indoor(
        "Route222_WestHouse",
        "MAP_ROUTE222_WEST_HOUSE",
        "MAPSEC_ROUTE_213",
        "MAP_ROUTE222",
        3,
        "Route222_WestHouse_EventScript_Resident",
        "Fishers trade stories about Route 223's current.\\nVolkner surfs that water for fun.$",
    )
    indoor(
        "Route222_EastHouse",
        "MAP_ROUTE222_EAST_HOUSE",
        "MAPSEC_ROUTE_213",
        "MAP_ROUTE222",
        2,
        "Route222_EastHouse_EventScript_Resident",
        "The gate ahead leads straight into Sunyshore.$",
    )

    # Gate stub
    lid, _, _ = indoor_room("Route222_Gate_ToSunyshore", w=10, h=10, north_door=False)
    from sinnoh_build_lib import IN_DOOR, IN_FLOOR, IN_WALL

    ggrid = [
        [
            IN_WALL
            if y in (0, 9) or x in (0, 9)
            else (
                IN_DOOR
                if (y == 9 and x in (4, 5)) or (y == 0 and x in (4, 5)) or (x == 9 and y in (4, 5))
                else IN_FLOOR
            )
            for x in range(10)
        ]
        for y in range(10)
    ]
    write_layout("Route222_Gate_ToSunyshore", 10, 10, "gTileset_Building", "gTileset_Facility", pack(ggrid))
    write_map(
        "Route222_Gate_ToSunyshore",
        {
            "id": "MAP_ROUTE222_GATE_TO_SUNYSHORE",
            "name": "Route222_Gate_ToSunyshore",
            "layout": "LAYOUT_ROUTE222_GATE_TO_SUNYSHORE",
            "music": "MUS_PL_JUBILIFE",
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
            "object_events": [obj("OBJ_EVENT_GFX_MAN_2", 5, 5, "Route222_Gate_EventScript_Guard")],
            "warp_events": [
                warp(4, 9, "MAP_ROUTE222", 0),
                warp(5, 9, "MAP_ROUTE222", 1),
                warp(9, 4, "MAP_SUNYSHORE_CITY", 3),
                warp(9, 5, "MAP_SUNYSHORE_CITY", 6),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "Route222_Gate_ToSunyshore_MapScripts::\n\t.byte 0\n\n"
        "Route222_Gate_EventScript_Guard::\n\tmsgbox Route222_Gate_Text, MSGBOX_NPC\n\tend\n\n"
        'Route222_Gate_Text:\n\t.string "Welcome to Sunyshore.\\n"\n\t.string "Volkner keeps the Gym lights blazing.$"\n',
    )

    # --- Sunyshore City ---
    grid, w, h = grid_from_chunks(SUNYSHORE)
    clear_plat_walkables(grid, SUNYSHORE)
    objs, scripts, plat_warps, pe = densify("SunyshoreCity", "sunyshore_city", SUNY_ORIGIN, w, h, 44)
    for lx, ly, dest, wid in plat_warps:
        stamp_door(grid, lx, ly)

    # Soft-close Route 223 (north water) with NPC
    objs.append(obj("OBJ_EVENT_GFX_SAILOR", 40, 2, "SunyshoreCity_EventScript_Route223Closed"))
    scripts += (
        "SunyshoreCity_EventScript_Route223Closed::\n"
        "\tlock\n\tfaceplayer\n"
        "\tgoto_if_set FLAG_BADGE08_GET, SunyshoreCity_EventScript_Route223Hint\n"
        "\tmsgbox SunyshoreCity_Text_NeedBadge, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        "SunyshoreCity_EventScript_Route223Hint::\n"
        "\tmsgbox SunyshoreCity_Text_OpenSoon, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        'SunyshoreCity_Text_NeedBadge:\n\t.string "Route 223\'s current is rough.\\n"\n'
        '\t.string "Earn the Beacon Badge before surfing north.$"\n\n'
        'SunyshoreCity_Text_OpenSoon:\n\t.string "With the Beacon Badge, Victory Road\\n"\n'
        '\t.string "opens past Route 223. Pack plenty of Repels.$"\n\n'
    )

    write_layout("SunyshoreCity", w, h, "gTileset_General", "gTileset_Dewford", pack(grid))

    # Build interiors matching warp count; index warps to match plat order
    # From earlier: market, NE house, west house, gate, NW house, mart, gate, unused1, unused2, east house, lighthouse, PC, gym, market
    indoor_specs = [
        ("SunyshoreCity_Market", "MAP_SUNYSHORE_CITY_MARKET", "Market stalls sell fresh water Pokemon food.\\nThe Gym is northwest of the plaza.$"),
        ("SunyshoreCity_NortheastHouse", "MAP_SUNYSHORE_CITY_NORTHEAST_HOUSE", "Volkner invents new puzzles when he gets bored.\\nThat is most days.$"),
        ("SunyshoreCity_WestHouse", "MAP_SUNYSHORE_CITY_WEST_HOUSE", "Bring Ground types if you challenge the Gym.$"),
        None,  # gate handled separately - warp to Route222 gate
        ("SunyshoreCity_NorthwestHouse", "MAP_SUNYSHORE_CITY_NORTHWEST_HOUSE", "The lighthouse elevator is east of town.$"),
        ("SunyshoreCity_Mart", "MAP_SUNYSHORE_CITY_MART", "Stock up before Victory Road.$", "OBJ_EVENT_GFX_MART_EMPLOYEE"),
        None,  # second gate warp
        ("SunyshoreCity_UnusedHouse1", "MAP_SUNYSHORE_CITY_UNUSED_HOUSE1", "An empty cottage overlooking the bay.$"),
        ("SunyshoreCity_UnusedHouse2", "MAP_SUNYSHORE_CITY_UNUSED_HOUSE2", "Curtains drawn. Come back later.$"),
        ("SunyshoreCity_EastHouse", "MAP_SUNYSHORE_CITY_EAST_HOUSE", "Surf north after the Beacon Badge.$"),
        ("SunyshoreCity_LighthouseElevator", "MAP_SUNYSHORE_CITY_LIGHTHOUSE_ELEVATOR", "Vista Lighthouse elevator. Closed for polish.$"),
        ("SunyshoreCity_PokemonCenter_1F", "MAP_SUNYSHORE_CITY_POKEMON_CENTER_1F", "Welcome to the Sunyshore Pokemon Center!$", "OBJ_EVENT_GFX_NURSE"),
        None,  # gym
        ("SunyshoreCity_MarketB", "MAP_SUNYSHORE_CITY_MARKET_B", "Second market door. Same plaza chatter.$"),
    ]

    city_warps = []
    indoor_names = []
    for i, (lx, ly, dest, wid) in enumerate(plat_warps):
        spec = indoor_specs[i] if i < len(indoor_specs) else None
        if dest and "GATE" in dest:
            city_warps.append(warp(lx, ly, "MAP_ROUTE222_GATE_TO_SUNYSHORE", 2 if i == 3 else 3))
        elif dest and "GYM" in dest:
            city_warps.append(warp(lx, ly, "MAP_SUNYSHORE_CITY_GYM_ROOM1", 0))
        elif spec is None:
            # fallback NPC door to west house
            city_warps.append(warp(lx, ly, "MAP_SUNYSHORE_CITY_WEST_HOUSE", 0))
        else:
            name, mid, text = spec[0], spec[1], spec[2]
            gfx = spec[3] if len(spec) > 3 else "OBJ_EVENT_GFX_OLD_WOMAN"
            # exit warp id = index in city_warps we'll assign
            exit_wid = len(city_warps)
            indoor(name, mid, "MAPSEC_ROUTE_213", "MAP_SUNYSHORE_CITY", exit_wid, f"{name}_EventScript_Npc", text, gfx=gfx)
            indoor_names.append(name)
            city_warps.append(warp(lx, ly, mid, 0))

    write_map(
        "SunyshoreCity",
        {
            "id": "MAP_SUNYSHORE_CITY",
            "name": "SunyshoreCity",
            "layout": "LAYOUT_SUNYSHORE_CITY",
            "music": "MUS_PL_JUBILIFE",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_CITY",
            "allow_cycling": True,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": [
                {"map": "MAP_ROUTE222", "offset": 32, "direction": "left"},
            ],
            "object_events": objs,
            "warp_events": city_warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    build_gym()

    # Link ValorLakefront east -> Route222
    vl = json.loads((MAPS / "ValorLakefront" / "map.json").read_text())
    conns = vl.get("connections") or []
    if not any(c.get("map") == "MAP_ROUTE222" for c in conns):
        conns.append({"map": "MAP_ROUTE222", "offset": 32, "direction": "right"})
    vl["connections"] = conns
    (MAPS / "ValorLakefront" / "map.json").write_text(json.dumps(vl, indent=2) + "\n")

    outdoor = ["Route222", "SunyshoreCity"]
    indoor_all = indoor_names + [
        "Route222_WestHouse",
        "Route222_EastHouse",
        "Route222_Gate_ToSunyshore",
        "SunyshoreCity_Gym_Room1",
        "SunyshoreCity_Gym_Room2",
        "SunyshoreCity_Gym_VolknersRoom",
    ]
    register_maps(outdoor, indoor_all, "gMapGroup_IndoorM28Sunyshore")
    scrub(outdoor + indoor_all)
    print("Sunyshore / Volkner build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
