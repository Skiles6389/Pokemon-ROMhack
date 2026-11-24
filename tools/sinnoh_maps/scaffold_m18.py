#!/usr/bin/env python3
"""Scaffold M18 Route 209 / Solaceon / Route 210S / Route 215 maps, scripts, constants, trainers, wilds."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data" / "maps"


def obj(gfx, x, y, script, trainer="TRAINER_TYPE_NONE", sight="0", flag="0", movement="MOVEMENT_TYPE_FACE_DOWN", local_id=None, range_x=0, range_y=0):
    o = {
        "graphics_id": gfx,
        "x": x,
        "y": y,
        "elevation": 3,
        "movement_type": movement,
        "movement_range_x": range_x,
        "movement_range_y": range_y,
        "trainer_type": trainer,
        "trainer_sight_or_berry_tree_id": str(sight),
        "script": script,
        "flag": flag,
    }
    if local_id:
        o["local_id"] = local_id
    return o


def warp(x, y, dest, wid, elev=0):
    return {"x": x, "y": y, "elevation": elev, "dest_map": dest, "dest_warp_id": str(wid)}


def trigger(x, y, script, var="VAR_TEMP_0", val="0"):
    return {"type": "trigger", "x": x, "y": y, "elevation": 0, "var": var, "var_value": val, "script": script}


def sign(x, y, script):
    return {"type": "sign", "x": x, "y": y, "elevation": 0, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": script}


def conn(direction, map_id, offset=0):
    return {"map": map_id, "offset": offset, "direction": direction}


def write_map(name: str, data: dict, scripts: str):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("wrote", name)


def outdoor_base(map_id, name, layout, music="MUS_PL_ROUTE203", night="MUS_PL_ROUTE203_NIGHT", mapsec="MAPSEC_ROUTE_209", map_type="MAP_TYPE_ROUTE"):
    return {
        "id": map_id,
        "name": name,
        "layout": layout,
        "music": music,
        "night_music": night,
        "region": "REGION_HOENN",
        "region_map_section": mapsec,
        "requires_flash": False,
        "weather": "WEATHER_SUNNY",
        "map_type": map_type,
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [],
        "object_events": [],
        "warp_events": [],
        "coord_events": [],
        "bg_events": [],
    }


def indoor_base(map_id, name, layout, music, mapsec="MAPSEC_SOLACEON_TOWN", night=None, show_name=False, battle="MAP_BATTLE_SCENE_NORMAL"):
    d = {
        "id": map_id,
        "name": name,
        "layout": layout,
        "music": music,
        "region": "REGION_HOENN",
        "region_map_section": mapsec,
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": False,
        "allow_running": False,
        "show_map_name": show_name,
        "battle_scene": battle,
        "connections": None,
        "object_events": [],
        "warp_events": [],
        "coord_events": [],
        "bg_events": [],
    }
    if night:
        d["night_music"] = night
    return d


def land_entry(map_id, label, mons, rate=30):
    return {
        "map": map_id,
        "base_label": label,
        "land_mons": {
            "encounter_rate": rate,
            "mons": [{"min_level": lv, "max_level": lv, "species": sp} for sp, lv in mons],
        },
    }


# ---------- Outdoor ----------
def scaffold_route209():
    data = outdoor_base("MAP_ROUTE209", "Route209", "LAYOUT_ROUTE209", mapsec="MAPSEC_ROUTE_209")
    data["connections"] = [conn("up", "MAP_SOLACEON_TOWN", 32)]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_YOUNGSTER", 10, 53, "Route209_EventScript_Albert", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_LASS", 42, 39, "Route209_EventScript_Jennifer", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_BEAUTY", 48, 18, "Route209_EventScript_Shelley", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_RUNNING_TRIATHLETE_M", 28, 44, "Route209_EventScript_Richard", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_WALK_SEQUENCE_LEFT_UP_RIGHT_DOWN", range_x=2, range_y=2),
        obj("OBJ_EVENT_GFX_TWIN", 32, 48, "Route209_EventScript_Emma", trainer="TRAINER_TYPE_NORMAL", sight="2", local_id="LOCALID_ROUTE209_EMMA"),
        obj("OBJ_EVENT_GFX_TWIN", 33, 48, "Route209_EventScript_Lil", trainer="TRAINER_TYPE_NORMAL", sight="2", local_id="LOCALID_ROUTE209_LIL"),
        obj("OBJ_EVENT_GFX_BEAUTY", 49, 13, "Route209_EventScript_YoungCoupleF", trainer="TRAINER_TYPE_NORMAL", sight="2", local_id="LOCALID_ROUTE209_COUPLE_F"),
        obj("OBJ_EVENT_GFX_MAN_1", 49, 12, "Route209_EventScript_YoungCoupleM", trainer="TRAINER_TYPE_NORMAL", sight="2", local_id="LOCALID_ROUTE209_COUPLE_M"),
        obj("OBJ_EVENT_GFX_FISHERMAN", 18, 50, "Route209_EventScript_Fisherman", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_OLD_MAN", 40, 30, "Route209_EventScript_Pokefan", movement="MOVEMENT_TYPE_LOOK_AROUND"),
        obj("OBJ_EVENT_GFX_ITEM_BALL", 20, 42, "Route209_EventScript_GreatBall", flag="FLAG_ITEM_ROUTE209_GREAT_BALL"),
        obj("OBJ_EVENT_GFX_ITEM_BALL", 36, 22, "Route209_EventScript_HyperPotion", flag="FLAG_ITEM_ROUTE209_HYPER_POTION"),
        obj("OBJ_EVENT_GFX_ITEM_BALL", 50, 36, "Route209_EventScript_Calcium", flag="FLAG_ITEM_ROUTE209_CALCIUM"),
        obj("OBJ_EVENT_GFX_ITEM_BALL", 12, 28, "Route209_EventScript_Ether", flag="FLAG_ITEM_ROUTE209_ETHER"),
    ]
    data["warp_events"] = [
        warp(0, 54, "MAP_HEARTHOME_CITY_ROUTE209_GATE", 2),
        warp(0, 55, "MAP_HEARTHOME_CITY_ROUTE209_GATE", 3),
        warp(56, 8, "MAP_LOST_TOWER_1F", 0),
    ]
    data["bg_events"] = [
        sign(54, 41, "Route209_EventScript_HallowedTowerSign"),
        sign(55, 41, "Route209_EventScript_HallowedTowerSign"),
        sign(4, 52, "Route209_EventScript_RouteSign"),
    ]
    scripts = r'''Route209_MapScripts::
	.byte 0

Route209_EventScript_Albert::
	trainerbattle_single TRAINER_BREEDER_ALBERT_R209, Route209_Text_AlbertIntro, Route209_Text_AlbertDefeat
	msgbox Route209_Text_AlbertAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Jennifer::
	trainerbattle_single TRAINER_BREEDER_JENNIFER_R209, Route209_Text_JenniferIntro, Route209_Text_JenniferDefeat
	msgbox Route209_Text_JenniferAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Shelley::
	trainerbattle_single TRAINER_COWGIRL_SHELLEY_R209, Route209_Text_ShelleyIntro, Route209_Text_ShelleyDefeat
	msgbox Route209_Text_ShelleyAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Richard::
	trainerbattle_single TRAINER_JOGGER_RICHARD_R209, Route209_Text_RichardIntro, Route209_Text_RichardDefeat
	msgbox Route209_Text_RichardAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Emma::
	trainerbattle_double TRAINER_TWINS_EMMA_LIL_R209, Route209_Text_EmmaIntro, Route209_Text_EmmaDefeat, Route209_Text_EmmaNotEnough
	msgbox Route209_Text_EmmaAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Lil::
	trainerbattle_double TRAINER_TWINS_EMMA_LIL_R209, Route209_Text_LilIntro, Route209_Text_LilDefeat, Route209_Text_LilNotEnough
	msgbox Route209_Text_LilAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_YoungCoupleF::
	trainerbattle_double TRAINER_YOUNG_COUPLE_R209, Route209_Text_CoupleFIntro, Route209_Text_CoupleDefeat, Route209_Text_CoupleNotEnough
	msgbox Route209_Text_CoupleFAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_YoungCoupleM::
	trainerbattle_double TRAINER_YOUNG_COUPLE_R209, Route209_Text_CoupleMIntro, Route209_Text_CoupleDefeat, Route209_Text_CoupleNotEnough
	msgbox Route209_Text_CoupleMAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Fisherman::
	msgbox Route209_Text_Fisherman, MSGBOX_NPC
	end

Route209_EventScript_Pokefan::
	msgbox Route209_Text_Pokefan, MSGBOX_NPC
	end

Route209_EventScript_GreatBall::
	finditem ITEM_GREAT_BALL
	end

Route209_EventScript_HyperPotion::
	finditem ITEM_HYPER_POTION
	end

Route209_EventScript_Calcium::
	finditem ITEM_CALCIUM
	end

Route209_EventScript_Ether::
	finditem ITEM_ETHER
	end

Route209_EventScript_HallowedTowerSign::
	msgbox Route209_Text_HallowedTower, MSGBOX_SIGN
	end

Route209_EventScript_RouteSign::
	msgbox Route209_Text_RouteSign, MSGBOX_SIGN
	end

Route209_Text_AlbertIntro:
	.string "I raise POKéMON with care!\n"
	.string "Let's see your team!$"

Route209_Text_AlbertDefeat:
	.string "They still have growing to do...$"

Route209_Text_AlbertAfter:
	.string "Solaceon Day Care knows true care.$"

Route209_Text_JenniferIntro:
	.string "My cute partners are ready!\n"
	.string "Don't hold back!$"

Route209_Text_JenniferDefeat:
	.string "Aww, that sting...$"

Route209_Text_JenniferAfter:
	.string "Hallowed Tower is spooky at night.$"

Route209_Text_ShelleyIntro:
	.string "Yeehaw! Trail ride's over--\n"
	.string "time for a battle!$"

Route209_Text_ShelleyDefeat:
	.string "Whoa there, partner...$"

Route209_Text_ShelleyAfter:
	.string "Lost Tower sits north of here.\n"
	.string "Spirits like quiet visitors.$"

Route209_Text_RichardIntro:
	.string "I jog this loop every dawn!\n"
	.string "Keep up if you can!$"

Route209_Text_RichardDefeat:
	.string "Outpaced in battle...$"

Route209_Text_RichardAfter:
	.string "Cardio and contests both matter!$"

Route209_Text_EmmaIntro:
	.string "EMMA: Twin power, go!$"

Route209_Text_EmmaDefeat:
	.string "EMMA: We slipped!$"

Route209_Text_EmmaAfter:
	.string "EMMA: Lil, we need more drills.$"

Route209_Text_EmmaNotEnough:
	.string "EMMA: Bring two POKéMON!$"

Route209_Text_LilIntro:
	.string "LIL: We battle as a pair!$"

Route209_Text_LilDefeat:
	.string "LIL: No fair!$"

Route209_Text_LilAfter:
	.string "LIL: Practice makes perfect.$"

Route209_Text_LilNotEnough:
	.string "LIL: You need two partners!$"

Route209_Text_CoupleFIntro:
	.string "We're on a date... and a battle!$"

Route209_Text_CoupleMIntro:
	.string "Two hearts, one battle plan!$"

Route209_Text_CoupleDefeat:
	.string "Our rhythm broke...$"

Route209_Text_CoupleFAfter:
	.string "Romance can wait. Training first!$"

Route209_Text_CoupleMAfter:
	.string "Next stop: Solaceon Town.$"

Route209_Text_CoupleNotEnough:
	.string "Come back with two POKéMON!$"

Route209_Text_Fisherman:
	.string "The brook here is quiet.\n"
	.string "Good place to think and cast.$"

Route209_Text_Pokefan:
	.string "I walk this route for my health.\n"
	.string "My POKéMON enjoy the air, too.$"

Route209_Text_HallowedTower:
	.string "HALLOWED TOWER\n"
	.string "A quiet shrine for wandering souls$"

Route209_Text_RouteSign:
	.string "ROUTE 209\n"
	.string "Hearthome City - Solaceon Town$"
'''
    write_map("Route209", data, scripts)


def scaffold_solaceon_town():
    data = outdoor_base(
        "MAP_SOLACEON_TOWN", "SolaceonTown", "LAYOUT_SOLACEON_TOWN",
        music="MUS_PL_SANDGEM", night="MUS_PL_SANDGEM_NIGHT",
        mapsec="MAPSEC_SOLACEON_TOWN", map_type="MAP_TYPE_TOWN",
    )
    data["connections"] = [
        conn("down", "MAP_ROUTE209", -32),
        conn("up", "MAP_ROUTE210_SOUTH", 0),
    ]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_OLD_MAN", 11, 8, "Route117_EventScript_DaycareMan", movement="MOVEMENT_TYPE_FACE_DOWN", local_id="LOCALID_SOLACEON_DAYCARE_MAN"),
        obj("OBJ_EVENT_GFX_BEAUTY", 18, 20, "SolaceonTown_EventScript_Cowgirl", movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=2, range_y=1),
        obj("OBJ_EVENT_GFX_MAN_1", 30, 18, "SolaceonTown_EventScript_Rancher", movement="MOVEMENT_TYPE_LOOK_AROUND"),
        obj("OBJ_EVENT_GFX_TWIN", 24, 22, "SolaceonTown_EventScript_Twin", movement="MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT", range_x=2),
        obj("OBJ_EVENT_GFX_HIKER", 46, 14, "SolaceonTown_EventScript_RuinManiac", movement="MOVEMENT_TYPE_FACE_UP"),
        obj("OBJ_EVENT_GFX_BOY_1", 33, 24, "SolaceonTown_EventScript_Boy", movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=1, range_y=1),
        obj("OBJ_EVENT_GFX_GIRL_1", 20, 14, "SolaceonTown_EventScript_Girl", movement="MOVEMENT_TYPE_LOOK_AROUND"),
    ]
    data["warp_events"] = [
        warp(9, 5, "MAP_SOLACEON_TOWN_POKEMON_DAY_CARE", 0),   # 0
        warp(22, 16, "MAP_SOLACEON_TOWN_POKEMON_CENTER_1F", 0),  # 1
        warp(27, 25, "MAP_SOLACEON_TOWN_MART", 0),               # 2
        warp(27, 16, "MAP_SOLACEON_TOWN_NEWS_PRESS", 0),         # 3
        warp(21, 6, "MAP_SOLACEON_TOWN_NORTH_HOUSE", 0),         # 4
        warp(35, 8, "MAP_SOLACEON_TOWN_NORTHEAST_HOUSE", 0),     # 5
        warp(37, 16, "MAP_SOLACEON_TOWN_EAST_HOUSE", 0),         # 6
        warp(51, 15, "MAP_SOLACEON_RUINS_EXTERIOR_GATE", 0),     # 7
        warp(53, 12, "MAP_SOLACEON_RUINS_EXTERIOR_GATE", 1),     # 8
    ]
    data["bg_events"] = [
        sign(19, 18, "SolaceonTown_EventScript_TownSign"),
        sign(10, 7, "SolaceonTown_EventScript_DayCareSign"),
        sign(28, 15, "SolaceonTown_EventScript_NewsPressSign"),
        sign(49, 16, "SolaceonTown_EventScript_RuinsSign"),
    ]
    scripts = r'''SolaceonTown_MapScripts::
	.byte 0

SolaceonTown_EventScript_Cowgirl::
	msgbox SolaceonTown_Text_Cowgirl, MSGBOX_NPC
	end

SolaceonTown_EventScript_Rancher::
	msgbox SolaceonTown_Text_Rancher, MSGBOX_NPC
	end

SolaceonTown_EventScript_Twin::
	msgbox SolaceonTown_Text_Twin, MSGBOX_NPC
	end

SolaceonTown_EventScript_RuinManiac::
	msgbox SolaceonTown_Text_RuinManiac, MSGBOX_NPC
	end

SolaceonTown_EventScript_Boy::
	msgbox SolaceonTown_Text_Boy, MSGBOX_NPC
	end

SolaceonTown_EventScript_Girl::
	msgbox SolaceonTown_Text_Girl, MSGBOX_NPC
	end

SolaceonTown_EventScript_TownSign::
	msgbox SolaceonTown_Text_TownSign, MSGBOX_SIGN
	end

SolaceonTown_EventScript_DayCareSign::
	msgbox SolaceonTown_Text_DayCareSign, MSGBOX_SIGN
	end

SolaceonTown_EventScript_NewsPressSign::
	msgbox SolaceonTown_Text_NewsPressSign, MSGBOX_SIGN
	end

SolaceonTown_EventScript_RuinsSign::
	msgbox SolaceonTown_Text_RuinsSign, MSGBOX_SIGN
	end

SolaceonTown_Text_Cowgirl:
	.string "Pastures around Solaceon are wide.\n"
	.string "Great place to raise tough partners!$"

SolaceonTown_Text_Rancher:
	.string "Ranch work starts early.\n"
	.string "POKéMON help with every chore.$"

SolaceonTown_Text_Twin:
	.string "The Day Care Lady is so kind!\n"
	.string "She always remembers my POKéMON.$"

SolaceonTown_Text_RuinManiac:
	.string "Those cliff mouths lead to ruins.\n"
	.string "The interior isn't open yet--patience!$"

SolaceonTown_Text_Boy:
	.string "News Press prints Contest gossip.\n"
	.string "I grab a paper every week!$"

SolaceonTown_Text_Girl:
	.string "Route 210 north is blocked by\n"
	.string "PSYDUCK with headaches. Weird, huh?$"

SolaceonTown_Text_TownSign:
	.string "SOLACEON TOWN\n"
	.string "A town of warm hearts and quiet ruins$"

SolaceonTown_Text_DayCareSign:
	.string "POKéMON DAY CARE\n"
	.string "Let us raise your partners$"

SolaceonTown_Text_NewsPressSign:
	.string "SOLACEON NEWS PRESS\n"
	.string "Fresh headlines daily$"

SolaceonTown_Text_RuinsSign:
	.string "SOLACEON RUINS\n"
	.string "Unown research ongoing$"
'''
    write_map("SolaceonTown", data, scripts)


def scaffold_route210_south():
    data = outdoor_base("MAP_ROUTE210_SOUTH", "Route210_South", "LAYOUT_ROUTE210_SOUTH", mapsec="MAPSEC_ROUTE_210")
    data["connections"] = [
        conn("down", "MAP_SOLACEON_TOWN", 0),
        conn("right", "MAP_ROUTE215", 32),
    ]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_TWIN", 18, 70, "Route210_South_EventScript_Teri", trainer="TRAINER_TYPE_NORMAL", sight="2", local_id="LOCALID_R210_TERI"),
        obj("OBJ_EVENT_GFX_TWIN", 19, 70, "Route210_South_EventScript_Tia", trainer="TRAINER_TYPE_NORMAL", sight="2", local_id="LOCALID_R210_TIA"),
        obj("OBJ_EVENT_GFX_YOUNGSTER", 14, 60, "Route210_South_EventScript_Kahlil", trainer="TRAINER_TYPE_NORMAL", sight="2"),
        obj("OBJ_EVENT_GFX_LASS", 24, 55, "Route210_South_EventScript_Amber", trainer="TRAINER_TYPE_NORMAL", sight="2"),
        obj("OBJ_EVENT_GFX_BEAUTY", 16, 50, "Route210_South_EventScript_Belle", trainer="TRAINER_TYPE_NORMAL", sight="2", local_id="LOCALID_R210_BELLE"),
        obj("OBJ_EVENT_GFX_MAN_1", 17, 50, "Route210_South_EventScript_Pa", trainer="TRAINER_TYPE_NORMAL", sight="2", local_id="LOCALID_R210_PA"),
        obj("OBJ_EVENT_GFX_HIKER", 20, 62, "Route210_South_EventScript_Marco", trainer="TRAINER_TYPE_NORMAL", sight="3"),
        obj("OBJ_EVENT_GFX_RUNNING_TRIATHLETE_M", 12, 75, "Route210_South_EventScript_Wyatt", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_WALK_SEQUENCE_DOWN_RIGHT_UP_LEFT", range_x=2, range_y=2),
        obj("OBJ_EVENT_GFX_BOY_1", 26, 58, "Route210_South_EventScript_GrassBoy", trainer="TRAINER_TYPE_NORMAL", sight="1", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_PSYDUCK", 17, 43, "Route210_South_EventScript_Psyduck", local_id="LOCALID_R210_PSYDUCK_1"),
        obj("OBJ_EVENT_GFX_PSYDUCK", 16, 43, "Route210_South_EventScript_Psyduck", local_id="LOCALID_R210_PSYDUCK_2"),
        obj("OBJ_EVENT_GFX_PSYDUCK", 17, 41, "Route210_South_EventScript_Psyduck", local_id="LOCALID_R210_PSYDUCK_3"),
        obj("OBJ_EVENT_GFX_PSYDUCK", 16, 42, "Route210_South_EventScript_Psyduck", local_id="LOCALID_R210_PSYDUCK_4"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 20, 48, "Route210_South_EventScript_Cynthia", flag="FLAG_HIDE_ROUTE210_CYNTHIA", movement="MOVEMENT_TYPE_FACE_UP", local_id="LOCALID_R210_CYNTHIA"),
        obj("OBJ_EVENT_GFX_ITEM_BALL", 28, 66, "Route210_South_EventScript_ItemHyperPotion", flag="FLAG_ITEM_ROUTE210_HYPER_POTION"),
    ]
    data["warp_events"] = [
        warp(22, 47, "MAP_ROUTE210_CAFE_CABIN", 0),
    ]
    data["coord_events"] = [
        trigger(15, 40, "Route210_South_EventScript_PsyduckBlock", "VAR_ROUTE210_STATE", "0"),
        trigger(16, 40, "Route210_South_EventScript_PsyduckBlock", "VAR_ROUTE210_STATE", "0"),
        trigger(17, 40, "Route210_South_EventScript_PsyduckBlock", "VAR_ROUTE210_STATE", "0"),
        trigger(18, 40, "Route210_South_EventScript_PsyduckBlock", "VAR_ROUTE210_STATE", "0"),
    ]
    data["bg_events"] = [
        sign(22, 48, "Route210_South_EventScript_CafeSign"),
        sign(18, 90, "Route210_South_EventScript_RouteSign"),
    ]
    scripts = r'''Route210_South_MapScripts::
	.byte 0

Route210_South_EventScript_Teri::
	trainerbattle_double TRAINER_TWINS_TERI_TIA_R210, Route210_South_Text_TeriIntro, Route210_South_Text_TeriDefeat, Route210_South_Text_TeriNotEnough
	msgbox Route210_South_Text_TeriAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Tia::
	trainerbattle_double TRAINER_TWINS_TERI_TIA_R210, Route210_South_Text_TiaIntro, Route210_South_Text_TiaDefeat, Route210_South_Text_TiaNotEnough
	msgbox Route210_South_Text_TiaAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Kahlil::
	trainerbattle_single TRAINER_BREEDER_KAHLIL_R210, Route210_South_Text_KahlilIntro, Route210_South_Text_KahlilDefeat
	msgbox Route210_South_Text_KahlilAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Amber::
	trainerbattle_single TRAINER_BREEDER_AMBER_R210, Route210_South_Text_AmberIntro, Route210_South_Text_AmberDefeat
	msgbox Route210_South_Text_AmberAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Belle::
	trainerbattle_double TRAINER_BELLE_AND_PA_R210, Route210_South_Text_BelleIntro, Route210_South_Text_BellePaDefeat, Route210_South_Text_BelleNotEnough
	msgbox Route210_South_Text_BelleAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Pa::
	trainerbattle_double TRAINER_BELLE_AND_PA_R210, Route210_South_Text_PaIntro, Route210_South_Text_BellePaDefeat, Route210_South_Text_PaNotEnough
	msgbox Route210_South_Text_PaAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Marco::
	trainerbattle_single TRAINER_RANCHER_MARCO_R210, Route210_South_Text_MarcoIntro, Route210_South_Text_MarcoDefeat
	msgbox Route210_South_Text_MarcoAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Wyatt::
	trainerbattle_single TRAINER_JOGGER_WYATT_R210, Route210_South_Text_WyattIntro, Route210_South_Text_WyattDefeat
	msgbox Route210_South_Text_WyattAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_GrassBoy::
	trainerbattle_single TRAINER_BOY_GRASS_R210, Route210_South_Text_GrassBoyIntro, Route210_South_Text_GrassBoyDefeat
	msgbox Route210_South_Text_GrassBoyAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Psyduck::
	lock
	faceplayer
	msgbox Route210_South_Text_PsyduckHeadache, MSGBOX_DEFAULT
	release
	end

Route210_South_EventScript_PsyduckBlock::
	lockall
	msgbox Route210_South_Text_PsyduckBlock, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route210_South_Movement_PushSouth
	waitmovement 0
	releaseall
	end

Route210_South_Movement_PushSouth:
	walk_down
	step_end

Route210_South_EventScript_Cynthia::
	msgbox Route210_South_Text_CynthiaHint, MSGBOX_NPC
	end

Route210_South_EventScript_ItemHyperPotion::
	finditem ITEM_HYPER_POTION
	end

Route210_South_EventScript_CafeSign::
	msgbox Route210_South_Text_CafeSign, MSGBOX_SIGN
	end

Route210_South_EventScript_RouteSign::
	msgbox Route210_South_Text_RouteSign, MSGBOX_SIGN
	end

Route210_South_Text_TeriIntro:
	.string "TERI: Ready, Tia? Twin combo!$"

Route210_South_Text_TeriDefeat:
	.string "TERI: We stumbled...$"

Route210_South_Text_TeriAfter:
	.string "TERI: Those PSYDUCK look miserable.$"

Route210_South_Text_TeriNotEnough:
	.string "TERI: Bring two POKéMON!$"

Route210_South_Text_TiaIntro:
	.string "TIA: We never lose together!$"

Route210_South_Text_TiaDefeat:
	.string "TIA: Oh no!$"

Route210_South_Text_TiaAfter:
	.string "TIA: Cafe milk helps headaches...maybe.$"

Route210_South_Text_TiaNotEnough:
	.string "TIA: Two on two, please!$"

Route210_South_Text_KahlilIntro:
	.string "Breeding takes patience.\n"
	.string "Battling builds character!$"

Route210_South_Text_KahlilDefeat:
	.string "Character noted...$"

Route210_South_Text_KahlilAfter:
	.string "Solaceon Day Care taught me a lot.$"

Route210_South_Text_AmberIntro:
	.string "Soft grass, soft hearts?\n"
	.string "Not in my battles!$"

Route210_South_Text_AmberDefeat:
	.string "Too soft after all...$"

Route210_South_Text_AmberAfter:
	.string "Route 215 east gets rainy.$"

Route210_South_Text_BelleIntro:
	.string "BELLE: Pa and I make a team!$"

Route210_South_Text_PaIntro:
	.string "PA: Stick with family, kid!$"

Route210_South_Text_BellePaDefeat:
	.string "Family plan failed...$"

Route210_South_Text_BelleAfter:
	.string "BELLE: Pa still tips the waitress.$"

Route210_South_Text_PaAfter:
	.string "PA: Cafe coffee wakes me up.$"

Route210_South_Text_BelleNotEnough:
	.string "BELLE: Need two POKéMON!$"

Route210_South_Text_PaNotEnough:
	.string "PA: Bring a pair!$"

Route210_South_Text_MarcoIntro:
	.string "Ranch trails toughen you up!\n"
	.string "Show me your grit!$"

Route210_South_Text_MarcoDefeat:
	.string "Tough as nails...$"

Route210_South_Text_MarcoAfter:
	.string "Mind the muddy path in the rain.$"

Route210_South_Text_WyattIntro:
	.string "Mile twenty--and a battle!$"

Route210_South_Text_WyattDefeat:
	.string "Hit the wall...$"

Route210_South_Text_WyattAfter:
	.string "Hydrate. Moomoo Milk works wonders.$"

Route210_South_Text_GrassBoyIntro:
	.string "Surprise from the tall grass!$"

Route210_South_Text_GrassBoyDefeat:
	.string "Spotted too soon...$"

Route210_South_Text_GrassBoyAfter:
	.string "Ninja lessons can wait.$"

Route210_South_Text_PsyduckHeadache:
	.string "PSYDUCK: Psyyaaa...\p"
	.string "It clutches its head.\n"
	.string "A splitting headache!$"

Route210_South_Text_PsyduckBlock:
	.string "The PSYDUCK have splitting headaches\n"
	.string "and won't budge!\p"
	.string "You'll need a SecretPotion later.$"

Route210_South_Text_CynthiaHint:
	.string "Those PSYDUCK need special medicine.\n"
	.string "Keep exploring--help will come.$"

Route210_South_Text_CafeSign:
	.string "CAFE CABIN\n"
	.string "Warm drinks for weary Trainers$"

Route210_South_Text_RouteSign:
	.string "ROUTE 210\n"
	.string "Solaceon Town - Celestic Town$"
'''
    write_map("Route210_South", data, scripts)


def scaffold_route215():
    data = outdoor_base("MAP_ROUTE215", "Route215", "LAYOUT_ROUTE215", mapsec="MAPSEC_ROUTE_215")
    data["weather"] = "WEATHER_RAIN"
    data["connections"] = [conn("left", "MAP_ROUTE210_SOUTH", -32)]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_BLACK_BELT", 20, 20, "Route215_EventScript_Derek", trainer="TRAINER_TYPE_NORMAL", sight="3"),
        obj("OBJ_EVENT_GFX_BLACK_BELT", 40, 24, "Route215_EventScript_Gregory", trainer="TRAINER_TYPE_NORMAL", sight="2"),
        obj("OBJ_EVENT_GFX_BLACK_BELT", 60, 19, "Route215_EventScript_Nathaniel", trainer="TRAINER_TYPE_NORMAL", sight="3"),
        obj("OBJ_EVENT_GFX_HIKER", 48, 22, "Route215_EventScript_Calvin", trainer="TRAINER_TYPE_NORMAL", sight="2"),
        obj("OBJ_EVENT_GFX_RUNNING_TRIATHLETE_M", 28, 21, "Route215_EventScript_Craig", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_WALK_LEFT_AND_RIGHT", range_x=3),
        obj("OBJ_EVENT_GFX_RUNNING_TRIATHLETE_M", 72, 23, "Route215_EventScript_Scott", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_WALK_RIGHT_AND_LEFT", range_x=2),
        obj("OBJ_EVENT_GFX_MAN_3", 55, 20, "Route215_EventScript_Dennis", trainer="TRAINER_TYPE_NORMAL", sight="2"),
        obj("OBJ_EVENT_GFX_WOMAN_3", 80, 22, "Route215_EventScript_Alexia", trainer="TRAINER_TYPE_NORMAL", sight="2"),
        obj("OBJ_EVENT_GFX_MAN_3", 88, 21, "Route215_EventScript_Ernest", trainer="TRAINER_TYPE_NORMAL", sight="3"),
        obj("OBJ_EVENT_GFX_BLACK_BELT", 35, 22, "Route215_EventScript_PaybackGift", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_ITEM_BALL", 45, 18, "Route215_EventScript_ItemEther", flag="FLAG_ITEM_ROUTE215_ETHER"),
        obj("OBJ_EVENT_GFX_ITEM_BALL", 68, 25, "Route215_EventScript_ItemHyperPotion", flag="FLAG_ITEM_ROUTE215_HYPER_POTION"),
    ]
    data["warp_events"] = [
        warp(95, 22, "MAP_ROUTE215_VEILSTONE_GATE", 0),
        warp(95, 23, "MAP_ROUTE215_VEILSTONE_GATE", 1),
    ]
    data["bg_events"] = [
        sign(10, 20, "Route215_EventScript_RouteSign"),
        sign(92, 21, "Route215_EventScript_VeilstoneSign"),
    ]
    scripts = r'''Route215_MapScripts::
	.byte 0

Route215_EventScript_Derek::
	trainerbattle_single TRAINER_BLACK_BELT_DEREK_R215, Route215_Text_DerekIntro, Route215_Text_DerekDefeat
	msgbox Route215_Text_DerekAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Gregory::
	trainerbattle_single TRAINER_BLACK_BELT_GREGORY_R215, Route215_Text_GregoryIntro, Route215_Text_GregoryDefeat
	msgbox Route215_Text_GregoryAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Nathaniel::
	trainerbattle_single TRAINER_BLACK_BELT_NATHANIEL_R215, Route215_Text_NathanielIntro, Route215_Text_NathanielDefeat
	msgbox Route215_Text_NathanielAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Calvin::
	trainerbattle_single TRAINER_RUIN_MANIAC_CALVIN_R215, Route215_Text_CalvinIntro, Route215_Text_CalvinDefeat
	msgbox Route215_Text_CalvinAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Craig::
	trainerbattle_single TRAINER_JOGGER_CRAIG_R215, Route215_Text_CraigIntro, Route215_Text_CraigDefeat
	msgbox Route215_Text_CraigAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Scott::
	trainerbattle_single TRAINER_JOGGER_SCOTT_R215, Route215_Text_ScottIntro, Route215_Text_ScottDefeat
	msgbox Route215_Text_ScottAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Dennis::
	trainerbattle_single TRAINER_ACE_TRAINER_DENNIS_R215, Route215_Text_DennisIntro, Route215_Text_DennisDefeat
	msgbox Route215_Text_DennisAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Alexia::
	trainerbattle_single TRAINER_ACE_TRAINER_ALEXIA_R215, Route215_Text_AlexiaIntro, Route215_Text_AlexiaDefeat
	msgbox Route215_Text_AlexiaAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Ernest::
	trainerbattle_single TRAINER_ACE_TRAINER_ERNEST_R215, Route215_Text_ErnestIntro, Route215_Text_ErnestDefeat
	msgbox Route215_Text_ErnestAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_PaybackGift::
	lock
	faceplayer
	goto_if_set FLAG_GOT_TM_PAYBACK_R215, Route215_EventScript_PaybackAfter
	msgbox Route215_Text_PaybackOffer, MSGBOX_DEFAULT
	giveitem ITEM_TM_PAYBACK
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_TM_PAYBACK_R215
	msgbox Route215_Text_PaybackExplain, MSGBOX_DEFAULT
	release
	end

Route215_EventScript_PaybackAfter::
	msgbox Route215_Text_PaybackAfter, MSGBOX_DEFAULT
	release
	end

Route215_EventScript_ItemEther::
	finditem ITEM_ETHER
	end

Route215_EventScript_ItemHyperPotion::
	finditem ITEM_HYPER_POTION
	end

Route215_EventScript_RouteSign::
	msgbox Route215_Text_RouteSign, MSGBOX_SIGN
	end

Route215_EventScript_VeilstoneSign::
	msgbox Route215_Text_VeilstoneSign, MSGBOX_SIGN
	end

Route215_Text_DerekIntro:
	.string "Rain or shine, my fists train!$"

Route215_Text_DerekDefeat:
	.string "Drenched in defeat...$"

Route215_Text_DerekAfter:
	.string "Mud builds character.$"

Route215_Text_GregoryIntro:
	.string "Karate cuts through the rain!$"

Route215_Text_GregoryDefeat:
	.string "My stance slipped...$"

Route215_Text_GregoryAfter:
	.string "Veilstone Gym waits ahead--soon.$"

Route215_Text_NathanielIntro:
	.string "Power punch! Feel the storm!$"

Route215_Text_NathanielDefeat:
	.string "Thunderous loss...$"

Route215_Text_NathanielAfter:
	.string "Keep your footing on wet roads.$"

Route215_Text_CalvinIntro:
	.string "Ruins whisper even in rainfall.$"

Route215_Text_CalvinDefeat:
	.string "History repeats--I lost.$"

Route215_Text_CalvinAfter:
	.string "Solaceon Ruins still call to me.$"

Route215_Text_CraigIntro:
	.string "Rainy miles make strong legs!$"

Route215_Text_CraigDefeat:
	.string "Splashed out...$"

Route215_Text_CraigAfter:
	.string "Watch for puddles near Veilstone.$"

Route215_Text_ScottIntro:
	.string "I'm warming up for a marathon!$"

Route215_Text_ScottDefeat:
	.string "Pulled a muscle...$"

Route215_Text_ScottAfter:
	.string "Stretch before every battle.$"

Route215_Text_DennisIntro:
	.string "Ace Trainers don't fear weather!$"

Route215_Text_DennisDefeat:
	.string "Your team shines brighter.$"

Route215_Text_DennisAfter:
	.string "Type coverage wins wet battles.$"

Route215_Text_AlexiaIntro:
	.string "Strategy over splash!$"

Route215_Text_AlexiaDefeat:
	.string "Outplayed...$"

Route215_Text_AlexiaAfter:
	.string "Veilstone City isn't open yet.$"

Route215_Text_ErnestIntro:
	.string "Final exam before the gate!$"

Route215_Text_ErnestDefeat:
	.string "You pass with honors.$"

Route215_Text_ErnestAfter:
	.string "Come back when Veilstone opens.$"

Route215_Text_PaybackOffer:
	.string "Took a cheap shot in the rain once.\n"
	.string "Never again!\p"
	.string "Take this TM--PAYBACK hits harder\n"
	.string "when you've already been hurt!$"

Route215_Text_PaybackExplain:
	.string "PAYBACK doubles power if you move\n"
	.string "after your foe. Wait, then strike!$"

Route215_Text_PaybackAfter:
	.string "Remember--patience fuels PAYBACK.$"

Route215_Text_RouteSign:
	.string "ROUTE 215\n"
	.string "Solaceon side - Veilstone side$"

Route215_Text_VeilstoneSign:
	.string "East: VEILSTONE CITY\n"
	.string "Gate ahead$"
'''
    write_map("Route215", data, scripts)


# ---------- Lost Tower ----------
def _lost_tower_floor(floor: int, warps, objects, scripts_body: str, show_name=False):
    name = f"LostTower_{floor}F"
    layout = f"LAYOUT_LOST_TOWER_{floor}_F"
    data = indoor_base(f"MAP_LOST_TOWER_{floor}F", name, layout, "MUS_PL_OREBURGH_GATE",
                       mapsec="MAPSEC_LOST_TOWER", show_name=show_name)
    data["allow_escaping"] = True
    data["allow_running"] = True
    data["object_events"] = objects
    data["warp_events"] = warps
    scripts = f"LostTower_{floor}F_MapScripts::\n\t.byte 0\n\n" + scripts_body
    write_map(name, data, scripts)


def scaffold_lost_tower():
    # 1F
    _lost_tower_floor(
        1,
        [warp(7, 15, "MAP_ROUTE209", 2), warp(8, 15, "MAP_ROUTE209", 2), warp(4, 3, "MAP_LOST_TOWER_2F", 0)],
        [obj("OBJ_EVENT_GFX_CHANNELER", 10, 10, "LostTower_1F_EventScript_Karina", trainer="TRAINER_TYPE_NORMAL", sight="2")],
        r'''LostTower_1F_EventScript_Karina::
	trainerbattle_single TRAINER_CHANNELER_KARINA_LT, LostTower_1F_Text_KarinaIntro, LostTower_1F_Text_KarinaDefeat
	msgbox LostTower_1F_Text_KarinaAfter, MSGBOX_AUTOCLOSE
	end

LostTower_1F_Text_KarinaIntro:
	.string "Spirits linger on every step...$"

LostTower_1F_Text_KarinaDefeat:
	.string "Quieted...$"

LostTower_1F_Text_KarinaAfter:
	.string "Climb with respect.$"
''',
        show_name=True,
    )
    # 2F
    _lost_tower_floor(
        2,
        [warp(10, 3, "MAP_LOST_TOWER_3F", 0), warp(4, 12, "MAP_LOST_TOWER_1F", 2)],
        [
            obj("OBJ_EVENT_GFX_PSYCHIC_M", 6, 8, "LostTower_2F_EventScript_Valerius", trainer="TRAINER_TYPE_NORMAL", sight="2"),
            obj("OBJ_EVENT_GFX_CHANNELER", 12, 9, "LostTower_2F_EventScript_Molly", trainer="TRAINER_TYPE_NORMAL", sight="2"),
        ],
        r'''LostTower_2F_EventScript_Valerius::
	trainerbattle_single TRAINER_PSYCHIC_VALERIUS_LT, LostTower_2F_Text_ValeriusIntro, LostTower_2F_Text_ValeriusDefeat
	msgbox LostTower_2F_Text_ValeriusAfter, MSGBOX_AUTOCLOSE
	end

LostTower_2F_EventScript_Molly::
	trainerbattle_single TRAINER_CHANNELER_MOLLY_LT, LostTower_2F_Text_MollyIntro, LostTower_2F_Text_MollyDefeat
	msgbox LostTower_2F_Text_MollyAfter, MSGBOX_AUTOCLOSE
	end

LostTower_2F_Text_ValeriusIntro:
	.string "I sense your aura... battle!$"

LostTower_2F_Text_ValeriusDefeat:
	.string "Your mind is sharper.$"

LostTower_2F_Text_ValeriusAfter:
	.string "Ghosts answer calm Trainers.$"

LostTower_2F_Text_MollyIntro:
	.string "Boo! Did I startle you?$"

LostTower_2F_Text_MollyDefeat:
	.string "My spirits fled...$"

LostTower_2F_Text_MollyAfter:
	.string "Higher floors feel colder.$"
''',
    )
    # 3F
    _lost_tower_floor(
        3,
        [warp(4, 3, "MAP_LOST_TOWER_4F", 0), warp(10, 12, "MAP_LOST_TOWER_2F", 0)],
        [obj("OBJ_EVENT_GFX_LASS", 8, 7, "LostTower_3F_EventScript_Catherine", trainer="TRAINER_TYPE_NORMAL", sight="2")],
        r'''LostTower_3F_EventScript_Catherine::
	trainerbattle_single TRAINER_LASS_CATHERINE_LT, LostTower_3F_Text_CatherineIntro, LostTower_3F_Text_CatherineDefeat
	msgbox LostTower_3F_Text_CatherineAfter, MSGBOX_AUTOCLOSE
	end

LostTower_3F_Text_CatherineIntro:
	.string "I study Ghost types here!$"

LostTower_3F_Text_CatherineDefeat:
	.string "Lesson learned...$"

LostTower_3F_Text_CatherineAfter:
	.string "Elders wait at the top.$"
''',
    )
    # 4F
    _lost_tower_floor(
        4,
        [warp(10, 3, "MAP_LOST_TOWER_5F", 0), warp(4, 12, "MAP_LOST_TOWER_3F", 0)],
        [
            obj("OBJ_EVENT_GFX_CHANNELER", 5, 8, "LostTower_4F_EventScript_Reina", trainer="TRAINER_TYPE_NORMAL", sight="2"),
            obj("OBJ_EVENT_GFX_PSYCHIC_M", 11, 10, "LostTower_4F_EventScript_Lindsay", trainer="TRAINER_TYPE_NORMAL", sight="2"),
        ],
        r'''LostTower_4F_EventScript_Reina::
	trainerbattle_single TRAINER_CHANNELER_REINA_LT, LostTower_4F_Text_ReinaIntro, LostTower_4F_Text_ReinaDefeat
	msgbox LostTower_4F_Text_ReinaAfter, MSGBOX_AUTOCLOSE
	end

LostTower_4F_EventScript_Lindsay::
	trainerbattle_single TRAINER_PSYCHIC_LINDSAY_LT, LostTower_4F_Text_LindsayIntro, LostTower_4F_Text_LindsayDefeat
	msgbox LostTower_4F_Text_LindsayAfter, MSGBOX_AUTOCLOSE
	end

LostTower_4F_Text_ReinaIntro:
	.string "Whispers guide my team...$"

LostTower_4F_Text_ReinaDefeat:
	.string "Silenced...$"

LostTower_4F_Text_ReinaAfter:
	.string "One more flight of stairs.$"

LostTower_4F_Text_LindsayIntro:
	.string "Focus cuts through fear!$"

LostTower_4F_Text_LindsayDefeat:
	.string "My focus broke...$"

LostTower_4F_Text_LindsayAfter:
	.string "The elders bless kind hearts.$"
''',
    )
    # 5F
    _lost_tower_floor(
        5,
        [warp(10, 3, "MAP_LOST_TOWER_4F", 0)],
        [
            obj("OBJ_EVENT_GFX_OLD_WOMAN", 7, 9, "LostTower_5F_EventScript_ElderCleanse", movement="MOVEMENT_TYPE_FACE_DOWN", local_id="LOCALID_LOST_TOWER_ELDER_L"),
            obj("OBJ_EVENT_GFX_OLD_WOMAN", 8, 9, "LostTower_5F_EventScript_ElderStrength", movement="MOVEMENT_TYPE_FACE_DOWN", local_id="LOCALID_LOST_TOWER_ELDER_R"),
        ],
        r'''LostTower_5F_EventScript_ElderCleanse::
	lock
	faceplayer
	goto_if_set FLAG_GOT_LOST_TOWER_CLEANSE_TAG, LostTower_5F_EventScript_ElderCleanseAfter
	msgbox LostTower_5F_Text_CleanseOffer, MSGBOX_DEFAULT
	giveitem ITEM_CLEANSE_TAG
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_LOST_TOWER_CLEANSE_TAG
	msgbox LostTower_5F_Text_CleanseExplain, MSGBOX_DEFAULT
	release
	end

LostTower_5F_EventScript_ElderCleanseAfter::
	msgbox LostTower_5F_Text_CleanseAfter, MSGBOX_DEFAULT
	release
	end

LostTower_5F_EventScript_ElderStrength::
	lock
	faceplayer
	goto_if_set FLAG_GOT_HM04_STRENGTH_LOST_TOWER, LostTower_5F_EventScript_ElderStrengthAfter
	msgbox LostTower_5F_Text_StrengthOffer, MSGBOX_DEFAULT
	giveitem ITEM_HM_STRENGTH
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_HM04_STRENGTH_LOST_TOWER
	msgbox LostTower_5F_Text_StrengthExplain, MSGBOX_DEFAULT
	release
	end

LostTower_5F_EventScript_ElderStrengthAfter::
	msgbox LostTower_5F_Text_StrengthAfter, MSGBOX_DEFAULT
	release
	end

LostTower_5F_Text_CleanseOffer:
	.string "Welcome, child.\p"
	.string "This tower shelters restless souls.\n"
	.string "Take a CLEANSE TAG for safe travels.$"

LostTower_5F_Text_CleanseExplain:
	.string "Hold it close. Wild spirits keep\n"
	.string "a little more distance.$"

LostTower_5F_Text_CleanseAfter:
	.string "May your path stay peaceful.$"

LostTower_5F_Text_StrengthOffer:
	.string "Strong bodies move heavy stones.\p"
	.string "In this land, we entrust Trainers\n"
	.string "with STRENGTH here in the tower.\p"
	.string "Please accept this HM.$"

LostTower_5F_Text_StrengthExplain:
	.string "Teach STRENGTH to a sturdy partner.\n"
	.string "Boulders on the road will yield.$"

LostTower_5F_Text_StrengthAfter:
	.string "Push onward with steady hearts.$"
''',
    )


# ---------- Solaceon interiors ----------
def scaffold_solaceon_center():
    data = indoor_base(
        "MAP_SOLACEON_TOWN_POKEMON_CENTER_1F", "SolaceonTown_PokemonCenter_1F",
        "LAYOUT_POKEMON_CENTER_1F", "MUS_PL_POKE_CENTER", night="MUS_PL_POKE_CENTER_NIGHT",
    )
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_NURSE", 7, 2, "SolaceonTown_PokemonCenter_1F_EventScript_Nurse", local_id="LOCALID_SOLACEON_NURSE"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 2, 3, "SolaceonTown_PokemonCenter_1F_EventScript_Woman"),
        obj("OBJ_EVENT_GFX_BOY_1", 11, 5, "SolaceonTown_PokemonCenter_1F_EventScript_Boy"),
    ]
    data["warp_events"] = [
        warp(7, 8, "MAP_SOLACEON_TOWN", 1, 3),
        warp(6, 8, "MAP_SOLACEON_TOWN", 1, 3),
        warp(1, 6, "MAP_SOLACEON_TOWN_POKEMON_CENTER_2F", 0, 4),
    ]
    scripts = r'''SolaceonTown_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SolaceonTown_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

SolaceonTown_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_SOLACEON_TOWN
	end

SolaceonTown_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_SOLACEON_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

SolaceonTown_PokemonCenter_1F_EventScript_Woman::
	msgbox SolaceonTown_PokemonCenter_1F_Text_Woman, MSGBOX_NPC
	end

SolaceonTown_PokemonCenter_1F_EventScript_Boy::
	msgbox SolaceonTown_PokemonCenter_1F_Text_Boy, MSGBOX_NPC
	end

SolaceonTown_PokemonCenter_1F_Text_Woman:
	.string "Day Care drop-offs make me nervous.\n"
	.string "I heal here first, every time.$"

SolaceonTown_PokemonCenter_1F_Text_Boy:
	.string "Lost Tower is creepy, but the\n"
	.string "elders up top are kind.$"
'''
    write_map("SolaceonTown_PokemonCenter_1F", data, scripts)

    data2 = indoor_base(
        "MAP_SOLACEON_TOWN_POKEMON_CENTER_2F", "SolaceonTown_PokemonCenter_2F",
        "LAYOUT_POKEMON_CENTER_2F", "MUS_PL_POKE_CENTER", night="MUS_PL_POKE_CENTER_NIGHT",
    )
    data2["warp_events"] = [warp(1, 6, "MAP_SOLACEON_TOWN_POKEMON_CENTER_1F", 2, 4)]
    write_map("SolaceonTown_PokemonCenter_2F", data2, "SolaceonTown_PokemonCenter_2F_MapScripts::\n\t.byte 0\n")


def scaffold_solaceon_mart():
    data = indoor_base("MAP_SOLACEON_TOWN_MART", "SolaceonTown_Mart", "LAYOUT_MART", "MUS_PL_POKE_MART")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 1, 3, "SolaceonTown_Mart_EventScript_Clerk"),
        obj("OBJ_EVENT_GFX_GIRL_1", 7, 2, "SolaceonTown_Mart_EventScript_Girl"),
    ]
    data["warp_events"] = [
        warp(3, 7, "MAP_SOLACEON_TOWN", 2),
        warp(4, 7, "MAP_SOLACEON_TOWN", 2),
    ]
    scripts = r'''SolaceonTown_Mart_MapScripts::
	.byte 0

SolaceonTown_Mart_EventScript_Clerk::
	lock
	faceplayer
	msgbox SolaceonTown_Mart_Text_ClerkAsk, MSGBOX_DEFAULT
	pokemart SolaceonTown_Mart_Pokemart
	msgbox SolaceonTown_Mart_Text_ClerkFarewell, MSGBOX_DEFAULT
	release
	end

SolaceonTown_Mart_EventScript_Girl::
	msgbox SolaceonTown_Mart_Text_Girl, MSGBOX_NPC
	end

	.align 2
SolaceonTown_Mart_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_NONE
	release
	end

SolaceonTown_Mart_Text_ClerkAsk:
	.string "Welcome to Solaceon Mart!\n"
	.string "What can I get you?$"

SolaceonTown_Mart_Text_ClerkFarewell:
	.string "Come again!$"

SolaceonTown_Mart_Text_Girl:
	.string "Stock up before Route 215.\n"
	.string "That rain soaks everything!$"
'''
    write_map("SolaceonTown_Mart", data, scripts)


def scaffold_solaceon_daycare():
    data = indoor_base(
        "MAP_SOLACEON_TOWN_POKEMON_DAY_CARE", "SolaceonTown_PokemonDayCare",
        "LAYOUT_ROUTE117_POKEMON_DAY_CARE", "MUS_PL_SANDGEM", night="MUS_PL_SANDGEM_NIGHT",
    )
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_OLD_WOMAN", 2, 2, "Route117_PokemonDayCare_EventScript_DaycareWoman", local_id="LOCALID_SOLACEON_DAYCARE_LADY"),
    ]
    data["warp_events"] = [
        warp(2, 8, "MAP_SOLACEON_TOWN", 0),
        warp(3, 8, "MAP_SOLACEON_TOWN", 0),
    ]
    write_map("SolaceonTown_PokemonDayCare", data, "SolaceonTown_PokemonDayCare_MapScripts::\n\t.byte 0\n")


def scaffold_solaceon_houses():
    # News Press
    data = indoor_base("MAP_SOLACEON_TOWN_NEWS_PRESS", "SolaceonTown_NewsPress", "LAYOUT_HOUSE1", "MUS_PL_SANDGEM", night="MUS_PL_SANDGEM_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_MAN_1", 4, 4, "SolaceonTown_NewsPress_EventScript_Editor"),
        obj("OBJ_EVENT_GFX_GIRL_1", 7, 5, "SolaceonTown_NewsPress_EventScript_Reporter"),
    ]
    data["warp_events"] = [warp(3, 7, "MAP_SOLACEON_TOWN", 3), warp(4, 7, "MAP_SOLACEON_TOWN", 3)]
    scripts = r'''SolaceonTown_NewsPress_MapScripts::
	.byte 0

SolaceonTown_NewsPress_EventScript_Editor::
	msgbox SolaceonTown_NewsPress_Text_Editor, MSGBOX_NPC
	end

SolaceonTown_NewsPress_EventScript_Reporter::
	msgbox SolaceonTown_NewsPress_Text_Reporter, MSGBOX_NPC
	end

SolaceonTown_NewsPress_Text_Editor:
	.string "We print Contest buzz and town tips.\n"
	.string "Got a scoop? Tell us later!$"

SolaceonTown_NewsPress_Text_Reporter:
	.string "Headline: PSYDUCK jam Route 210!\n"
	.string "Medicine shortage continues.$"
'''
    write_map("SolaceonTown_NewsPress", data, scripts)

    # North house
    data = indoor_base("MAP_SOLACEON_TOWN_NORTH_HOUSE", "SolaceonTown_NorthHouse", "LAYOUT_HOUSE1", "MUS_PL_SANDGEM", night="MUS_PL_SANDGEM_NIGHT")
    data["object_events"] = [obj("OBJ_EVENT_GFX_OLD_WOMAN", 4, 4, "SolaceonTown_NorthHouse_EventScript_Woman")]
    data["warp_events"] = [warp(3, 7, "MAP_SOLACEON_TOWN", 4), warp(4, 7, "MAP_SOLACEON_TOWN", 4)]
    scripts = r'''SolaceonTown_NorthHouse_MapScripts::
	.byte 0

SolaceonTown_NorthHouse_EventScript_Woman::
	msgbox SolaceonTown_NorthHouse_Text_Woman, MSGBOX_NPC
	end

SolaceonTown_NorthHouse_Text_Woman:
	.string "My grandson left for Lost Tower.\n"
	.string "He wanted to meet the elders.$"
'''
    write_map("SolaceonTown_NorthHouse", data, scripts)

    # Northeast house
    data = indoor_base("MAP_SOLACEON_TOWN_NORTHEAST_HOUSE", "SolaceonTown_NortheastHouse", "LAYOUT_HOUSE1", "MUS_PL_SANDGEM", night="MUS_PL_SANDGEM_NIGHT")
    data["object_events"] = [obj("OBJ_EVENT_GFX_MAN_1", 5, 4, "SolaceonTown_NortheastHouse_EventScript_Man")]
    data["warp_events"] = [warp(3, 7, "MAP_SOLACEON_TOWN", 5), warp(4, 7, "MAP_SOLACEON_TOWN", 5)]
    scripts = r'''SolaceonTown_NortheastHouse_MapScripts::
	.byte 0

SolaceonTown_NortheastHouse_EventScript_Man::
	msgbox SolaceonTown_NortheastHouse_Text_Man, MSGBOX_NPC
	end

SolaceonTown_NortheastHouse_Text_Man:
	.string "Unown researchers camp near the\n"
	.string "ruins. I sell them spare rope.$"
'''
    write_map("SolaceonTown_NortheastHouse", data, scripts)

    # East house
    data = indoor_base("MAP_SOLACEON_TOWN_EAST_HOUSE", "SolaceonTown_EastHouse", "LAYOUT_HOUSE1", "MUS_PL_SANDGEM", night="MUS_PL_SANDGEM_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_WOMAN_2", 4, 4, "SolaceonTown_EastHouse_EventScript_Woman"),
        obj("OBJ_EVENT_GFX_BOY_1", 7, 5, "SolaceonTown_EastHouse_EventScript_Boy"),
    ]
    data["warp_events"] = [warp(3, 7, "MAP_SOLACEON_TOWN", 6), warp(4, 7, "MAP_SOLACEON_TOWN", 6)]
    scripts = r'''SolaceonTown_EastHouse_MapScripts::
	.byte 0

SolaceonTown_EastHouse_EventScript_Woman::
	msgbox SolaceonTown_EastHouse_Text_Woman, MSGBOX_NPC
	end

SolaceonTown_EastHouse_EventScript_Boy::
	msgbox SolaceonTown_EastHouse_Text_Boy, MSGBOX_NPC
	end

SolaceonTown_EastHouse_Text_Woman:
	.string "Hearthome Contests are famous, but\n"
	.string "Solaceon stays peacefully quiet.$"

SolaceonTown_EastHouse_Text_Boy:
	.string "I want to read every Unown letter!$"
'''
    write_map("SolaceonTown_EastHouse", data, scripts)


def scaffold_solaceon_ruins_gate():
    data = indoor_base(
        "MAP_SOLACEON_RUINS_EXTERIOR_GATE", "SolaceonRuins_ExteriorGate",
        "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE", "MUS_PL_SANDGEM", night="MUS_PL_SANDGEM_NIGHT",
        mapsec="MAPSEC_SOLACEON_TOWN",
    )
    data["allow_cycling"] = True
    data["allow_running"] = True
    data["object_events"] = [obj("OBJ_EVENT_GFX_HIKER", 7, 2, "SolaceonRuins_ExteriorGate_EventScript_Guard")]
    data["warp_events"] = [
        warp(1, 5, "MAP_SOLACEON_TOWN", 7),
        warp(2, 5, "MAP_SOLACEON_TOWN", 8),
        warp(12, 5, "MAP_SOLACEON_TOWN", 7),
        warp(13, 5, "MAP_SOLACEON_TOWN", 8),
    ]
    data["coord_events"] = [
        trigger(10, 4, "SolaceonRuins_ExteriorGate_EventScript_ComingSoon"),
        trigger(11, 4, "SolaceonRuins_ExteriorGate_EventScript_ComingSoon"),
        trigger(12, 4, "SolaceonRuins_ExteriorGate_EventScript_ComingSoon"),
    ]
    scripts = r'''SolaceonRuins_ExteriorGate_MapScripts::
	.byte 0

SolaceonRuins_ExteriorGate_EventScript_Guard::
	msgbox SolaceonRuins_ExteriorGate_Text_Guard, MSGBOX_NPC
	end

SolaceonRuins_ExteriorGate_EventScript_ComingSoon::
	lockall
	msgbox SolaceonRuins_ExteriorGate_Text_ComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, SolaceonRuins_ExteriorGate_Movement_Push
	waitmovement 0
	releaseall
	end

SolaceonRuins_ExteriorGate_Movement_Push:
	walk_left
	step_end

SolaceonRuins_ExteriorGate_Text_Guard:
	.string "Ruins access is limited.\n"
	.string "Researchers only, for now.$"

SolaceonRuins_ExteriorGate_Text_ComingSoon:
	.string "Solaceon Ruins interior coming in\n"
	.string "a later milestone!$"
'''
    write_map("SolaceonRuins_ExteriorGate", data, scripts)


def scaffold_cafe_cabin():
    data = indoor_base(
        "MAP_ROUTE210_CAFE_CABIN", "Route210_CafeCabin", "LAYOUT_ROUTE210_CAFE_CABIN",
        "MUS_PL_SANDGEM", night="MUS_PL_SANDGEM_NIGHT", mapsec="MAPSEC_ROUTE_210",
    )
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_BEAUTY", 5, 3, "Route210_CafeCabin_EventScript_Waitress"),
        obj("OBJ_EVENT_GFX_MAN_1", 2, 5, "Route210_CafeCabin_EventScript_Patron"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 8, 4, "Route210_CafeCabin_EventScript_Collector", trainer="TRAINER_TYPE_NORMAL", sight="1"),
    ]
    data["warp_events"] = [
        warp(5, 8, "MAP_ROUTE210_SOUTH", 0),
        warp(6, 8, "MAP_ROUTE210_SOUTH", 0),
    ]
    scripts = r'''Route210_CafeCabin_MapScripts::
	.byte 0

Route210_CafeCabin_EventScript_Waitress::
	lock
	faceplayer
	msgbox Route210_CafeCabin_Text_WaitressAsk, MSGBOX_DEFAULT
	pokemart Route210_CafeCabin_Pokemart
	msgbox Route210_CafeCabin_Text_WaitressBye, MSGBOX_DEFAULT
	release
	end

Route210_CafeCabin_EventScript_Patron::
	msgbox Route210_CafeCabin_Text_Patron, MSGBOX_NPC
	end

Route210_CafeCabin_EventScript_Collector::
	trainerbattle_single TRAINER_CAFE_COLLECTOR_R210, Route210_CafeCabin_Text_CollectorIntro, Route210_CafeCabin_Text_CollectorDefeat
	msgbox Route210_CafeCabin_Text_CollectorAfter, MSGBOX_AUTOCLOSE
	end

	.align 2
Route210_CafeCabin_Pokemart:
	.2byte ITEM_MOOMOO_MILK
	.2byte ITEM_NONE
	release
	end

Route210_CafeCabin_Text_WaitressAsk:
	.string "Welcome! Fresh Moomoo Milk today.\n"
	.string "Care for a bottle?$"

Route210_CafeCabin_Text_WaitressBye:
	.string "Come warm up anytime!$"

Route210_CafeCabin_Text_Patron:
	.string "Milk after a rainy walk hits right.\n"
	.string "Those PSYDUCK could use some, too.$"

Route210_CafeCabin_Text_CollectorIntro:
	.string "I collect cafe stickers!\n"
	.string "Battle me for bragging rights!$"

Route210_CafeCabin_Text_CollectorDefeat:
	.string "Stickerless and beaten...$"

Route210_CafeCabin_Text_CollectorAfter:
	.string "Next cafe stop: somewhere sunnier.$"
'''
    write_map("Route210_CafeCabin", data, scripts)


def scaffold_veilstone_gate():
    data = indoor_base(
        "MAP_ROUTE215_VEILSTONE_GATE", "Route215_VeilstoneGate",
        "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE", "MUS_PL_ROUTE203", night="MUS_PL_ROUTE203_NIGHT",
        mapsec="MAPSEC_VEILSTONE_GATE",
    )
    data["allow_cycling"] = True
    data["allow_running"] = True
    data["object_events"] = [obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 7, 2, "Route215_VeilstoneGate_EventScript_Guard")]
    data["warp_events"] = [
        warp(1, 5, "MAP_ROUTE215", 0),
        warp(2, 5, "MAP_ROUTE215", 1),
        warp(12, 5, "MAP_ROUTE215", 0),
        warp(13, 5, "MAP_ROUTE215", 1),
    ]
    data["coord_events"] = [
        trigger(10, 4, "Route215_VeilstoneGate_EventScript_ComingSoon"),
        trigger(11, 4, "Route215_VeilstoneGate_EventScript_ComingSoon"),
        trigger(12, 4, "Route215_VeilstoneGate_EventScript_ComingSoon"),
    ]
    scripts = r'''Route215_VeilstoneGate_MapScripts::
	.byte 0

Route215_VeilstoneGate_EventScript_Guard::
	msgbox Route215_VeilstoneGate_Text_Guard, MSGBOX_NPC
	end

Route215_VeilstoneGate_EventScript_ComingSoon::
	lockall
	msgbox Route215_VeilstoneGate_Text_ComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route215_VeilstoneGate_Movement_Push
	waitmovement 0
	releaseall
	end

Route215_VeilstoneGate_Movement_Push:
	walk_left
	step_end

Route215_VeilstoneGate_Text_Guard:
	.string "Veilstone City is just beyond...\n"
	.string "when the road opens, that is.$"

Route215_VeilstoneGate_Text_ComingSoon:
	.string "Veilstone City coming in the next\n"
	.string "milestone!$"
'''
    write_map("Route215_VeilstoneGate", data, scripts)


# ---------- Patches ----------
def patch_route209_gate():
    gate = MAPS / "HearthomeCity_Route209Gate"
    data = json.loads((gate / "map.json").read_text())
    data["warp_events"][2] = warp(12, 5, "MAP_ROUTE209", 0)
    data["warp_events"][3] = warp(13, 5, "MAP_ROUTE209", 1)
    (gate / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    scripts = r'''HearthomeCity_Route209Gate_MapScripts::
	.byte 0

HearthomeCity_Route209Gate_EventScript_Guard::
	msgbox HearthomeCity_Route209Gate_Text_Guard, MSGBOX_NPC
	end

HearthomeCity_Route209Gate_EventScript_CheckProgress::
	lockall
	goto_if_unset FLAG_BADGE03_GET, HearthomeCity_Route209Gate_EventScript_NeedBadge
	goto_if_unset FLAG_HIDE_HEARTHOME_BARRY, HearthomeCity_Route209Gate_EventScript_NeedBarry
	releaseall
	end

HearthomeCity_Route209Gate_EventScript_NeedBadge::
	msgbox HearthomeCity_Route209Gate_Text_NeedBadge, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route209Gate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_Route209Gate_EventScript_NeedBarry::
	msgbox HearthomeCity_Route209Gate_Text_NeedBarry, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route209Gate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_Route209Gate_Movement_Push:
	walk_left
	step_end

HearthomeCity_Route209Gate_Text_Guard:
	.string "Route 209 leads toward Solaceon Town.\n"
	.string "Beat FANTINA and BARRY first!$"

HearthomeCity_Route209Gate_Text_NeedBadge:
	.string "You need the Relic Badge from FANTINA\n"
	.string "before heading to Route 209.$"

HearthomeCity_Route209Gate_Text_NeedBarry:
	.string "BARRY is waiting just outside!\n"
	.string "You should settle that rivalry first.$"
'''
    (gate / "scripts.inc").write_text(scripts)
    print("patched HearthomeCity_Route209Gate")


def patch_map_groups():
    path = REPO / "data" / "maps" / "map_groups.json"
    groups = json.loads(path.read_text())
    towns = groups["gMapGroup_TownsAndRoutes"]
    for name in ("Route209", "SolaceonTown", "Route210_South", "Route215"):
        if name not in towns:
            if "HearthomeCity" in towns:
                towns.insert(towns.index("HearthomeCity") + 1 + ["Route209", "SolaceonTown", "Route210_South", "Route215"].index(name), name)
            else:
                towns.append(name)
    # Deduplicate while preserving order if re-run scrambled inserts
    seen = set()
    cleaned = []
    for t in towns:
        if t not in seen:
            seen.add(t)
            cleaned.append(t)
    # Ensure M18 outdoor order after HearthomeCity
    for name in ("Route209", "SolaceonTown", "Route210_South", "Route215"):
        if name in cleaned:
            cleaned.remove(name)
    if "HearthomeCity" in cleaned:
        idx = cleaned.index("HearthomeCity") + 1
        for i, name in enumerate(("Route209", "SolaceonTown", "Route210_South", "Route215")):
            cleaned.insert(idx + i, name)
    else:
        cleaned.extend(["Route209", "SolaceonTown", "Route210_South", "Route215"])
    groups["gMapGroup_TownsAndRoutes"] = cleaned

    indoor = [
        "LostTower_1F",
        "LostTower_2F",
        "LostTower_3F",
        "LostTower_4F",
        "LostTower_5F",
        "SolaceonTown_PokemonCenter_1F",
        "SolaceonTown_PokemonCenter_2F",
        "SolaceonTown_Mart",
        "SolaceonTown_PokemonDayCare",
        "SolaceonTown_NewsPress",
        "SolaceonTown_NorthHouse",
        "SolaceonTown_NortheastHouse",
        "SolaceonTown_EastHouse",
        "SolaceonRuins_ExteriorGate",
        "Route210_CafeCabin",
        "Route215_VeilstoneGate",
    ]
    groups["gMapGroup_IndoorM18"] = indoor
    order = groups["group_order"]
    if "gMapGroup_IndoorM18" not in order:
        if "gMapGroup_IndoorHearthome" in order:
            order.insert(order.index("gMapGroup_IndoorHearthome") + 1, "gMapGroup_IndoorM18")
        else:
            order.append("gMapGroup_IndoorM18")
    path.write_text(json.dumps(groups, indent=2) + "\n")
    print("patched map_groups.json")


def patch_region_mapsecs():
    path = REPO / "src" / "data" / "region_map" / "region_map_sections.json"
    text = path.read_text()
    if "MAPSEC_SOLACEON_TOWN" in text:
        print("region_map_sections already has M18")
        return
    text = text.replace(
        '''{
      "id": "MAPSEC_ROUTE_209_GATE",
      "name": "ROUTE 209 GATE"
    }
  ]
}''',
        '''{
      "id": "MAPSEC_ROUTE_209_GATE",
      "name": "ROUTE 209 GATE"
    },
    {
      "id": "MAPSEC_ROUTE_209",
      "name": "ROUTE 209"
    },
    {
      "id": "MAPSEC_LOST_TOWER",
      "name": "LOST TOWER"
    },
    {
      "id": "MAPSEC_SOLACEON_TOWN",
      "name": "SOLACEON TOWN"
    },
    {
      "id": "MAPSEC_ROUTE_210",
      "name": "ROUTE 210"
    },
    {
      "id": "MAPSEC_ROUTE_215",
      "name": "ROUTE 215"
    },
    {
      "id": "MAPSEC_VEILSTONE_GATE",
      "name": "VEILSTONE GATE"
    }
  ]
}'''
    )
    path.write_text(text)
    print("patched region_map_sections.json")


def patch_regions_h():
    path = REPO / "include" / "regions.h"
    text = path.read_text()
    if "MAPSEC_VEILSTONE_GATE" in text:
        print("regions.h already has Veilstone gate bound")
        return
    text = text.replace(
        "sectionId <= MAPSEC_ROUTE_209_GATE;",
        "sectionId <= MAPSEC_VEILSTONE_GATE;",
    )
    path.write_text(text)
    print("patched regions.h")


def patch_map_name_popup():
    path = REPO / "src" / "map_name_popup.c"
    text = path.read_text()
    if "MAPSEC_SOLACEON_TOWN - KANTO_MAPSEC_COUNT" in text:
        print("map_name_popup already has M18")
        return
    additions_wood = (
        "[MAPSEC_ROUTE_209_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,\n"
        "    [MAPSEC_ROUTE_209 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,\n"
        "    [MAPSEC_LOST_TOWER - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,\n"
        "    [MAPSEC_SOLACEON_TOWN - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,\n"
        "    [MAPSEC_ROUTE_210 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,\n"
        "    [MAPSEC_ROUTE_215 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,\n"
        "    [MAPSEC_VEILSTONE_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,"
    )
    additions_bw = (
        "[MAPSEC_ROUTE_209_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,\n"
        "    [MAPSEC_ROUTE_209 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,\n"
        "    [MAPSEC_LOST_TOWER - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,\n"
        "    [MAPSEC_SOLACEON_TOWN - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,\n"
        "    [MAPSEC_ROUTE_210 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,\n"
        "    [MAPSEC_ROUTE_215 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,\n"
        "    [MAPSEC_VEILSTONE_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,"
    )
    text = text.replace(
        "[MAPSEC_ROUTE_209_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,",
        additions_wood,
        1,
    )
    text = text.replace(
        "[MAPSEC_ROUTE_209_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,",
        additions_bw,
        1,
    )
    path.write_text(text)
    print("patched map_name_popup.c")


def patch_heal_locations():
    path = REPO / "src" / "data" / "heal_locations.json"
    data = json.loads(path.read_text())
    locs = data["heal_locations"] if "heal_locations" in data else data
    if any(L.get("id") == "HEAL_LOCATION_SOLACEON_TOWN" for L in locs):
        print("heal_locations already has Solaceon")
        return
    locs.append({
        "id": "HEAL_LOCATION_SOLACEON_TOWN",
        "map": "MAP_SOLACEON_TOWN",
        "x": 22,
        "y": 17,
        "respawn_map": "MAP_SOLACEON_TOWN_POKEMON_CENTER_1F",
        "respawn_npc": "LOCALID_SOLACEON_NURSE",
    })
    if "heal_locations" in data:
        data["heal_locations"] = locs
        path.write_text(json.dumps(data, indent=2) + "\n")
    else:
        path.write_text(json.dumps(locs, indent=2) + "\n")
    print("patched heal_locations.json")


def patch_flags_vars():
    flags = REPO / "include" / "constants" / "flags.h"
    ft = flags.read_text()
    if "FLAG_GOT_LOST_TOWER_CLEANSE_TAG" not in ft:
        ft = ft.replace(
            "#define FLAG_UNUSED_0x28A  0x28A // Unused Flag\n"
            "#define FLAG_UNUSED_0x28B  0x28B // Unused Flag\n"
            "#define FLAG_UNUSED_0x28C  0x28C // Unused Flag\n"
            "#define FLAG_UNUSED_0x28D  0x28D // Unused Flag\n"
            "#define FLAG_UNUSED_0x28E  0x28E // Unused Flag\n"
            "#define FLAG_UNUSED_0x28F  0x28F // Unused Flag\n"
            "#define FLAG_UNUSED_0x290  0x290 // Unused Flag\n"
            "#define FLAG_UNUSED_0x291  0x291 // Unused Flag\n"
            "#define FLAG_UNUSED_0x292  0x292 // Unused Flag\n"
            "#define FLAG_UNUSED_0x293  0x293 // Unused Flag\n"
            "#define FLAG_UNUSED_0x294  0x294 // Unused Flag\n",
            "#define FLAG_GOT_LOST_TOWER_CLEANSE_TAG  0x28A // Sinnoh M18\n"
            "#define FLAG_GOT_HM04_STRENGTH_LOST_TOWER  0x28B // Sinnoh M18\n"
            "#define FLAG_GOT_TM_PAYBACK_R215  0x28C // Sinnoh M18\n"
            "#define FLAG_ITEM_ROUTE209_GREAT_BALL  0x28D // Sinnoh M18\n"
            "#define FLAG_ITEM_ROUTE209_HYPER_POTION  0x28E // Sinnoh M18\n"
            "#define FLAG_ITEM_ROUTE209_CALCIUM  0x28F // Sinnoh M18\n"
            "#define FLAG_ITEM_ROUTE209_ETHER  0x290 // Sinnoh M18\n"
            "#define FLAG_HIDE_ROUTE210_CYNTHIA  0x291 // Sinnoh M18; hidden until story needs her\n"
            "#define FLAG_ITEM_ROUTE210_HYPER_POTION  0x292 // Sinnoh M18\n"
            "#define FLAG_ITEM_ROUTE215_ETHER  0x293 // Sinnoh M18\n"
            "#define FLAG_ITEM_ROUTE215_HYPER_POTION  0x294 // Sinnoh M18\n",
        )
        flags.write_text(ft)
        print("patched flags.h")
    else:
        print("flags.h already has M18")

    vars_path = REPO / "include" / "constants" / "vars.h"
    vt = vars_path.read_text()
    if "VAR_ROUTE210_STATE" not in vt:
        vt = vt.replace(
            "#define VAR_UNUSED_0x40FA                                0x40FA // Unused Var\n",
            "#define VAR_ROUTE210_STATE                               0x40FA // Sinnoh M18: Psyduck blockade (0 blocked)\n",
        )
        vars_path.write_text(vt)
        print("patched vars.h")
    else:
        print("vars.h already has VAR_ROUTE210_STATE")

    ng = REPO / "data" / "scripts" / "new_game.inc"
    nt = ng.read_text()
    if "FLAG_HIDE_ROUTE210_CYNTHIA" not in nt:
        nt = nt.replace(
            "\tsetflag FLAG_HIDE_HEARTHOME_FANTINA\n",
            "\tsetflag FLAG_HIDE_HEARTHOME_FANTINA\n"
            "\tsetflag FLAG_HIDE_ROUTE210_CYNTHIA\n",
        )
        ng.write_text(nt)
        print("patched new_game.inc")
    else:
        print("new_game.inc already has Cynthia hide")


def patch_opponents():
    path = REPO / "include" / "constants" / "opponents.h"
    text = path.read_text()
    if "TRAINER_BREEDER_ALBERT_R209" in text:
        print("opponents.h already has M18")
        return
    replacements = [
        ("#define TRAINER_JEFFREY_3                   229\n",
         "#define TRAINER_BREEDER_ALBERT_R209                   229 // Sinnoh M18: was TRAINER_JEFFREY_3\n"
         "#define TRAINER_JEFFREY_3 TRAINER_BREEDER_ALBERT_R209\n"),
        ("#define TRAINER_JEFFREY_4                   230\n",
         "#define TRAINER_BREEDER_JENNIFER_R209                   230 // Sinnoh M18: was TRAINER_JEFFREY_4\n"
         "#define TRAINER_JEFFREY_4 TRAINER_BREEDER_JENNIFER_R209\n"),
        ("#define TRAINER_JEFFREY_5                   231\n",
         "#define TRAINER_COWGIRL_SHELLEY_R209                   231 // Sinnoh M18: was TRAINER_JEFFREY_5\n"
         "#define TRAINER_JEFFREY_5 TRAINER_COWGIRL_SHELLEY_R209\n"),
        ("#define TRAINER_DALTON_2                    197\n",
         "#define TRAINER_JOGGER_RICHARD_R209                    197 // Sinnoh M18: was TRAINER_DALTON_2\n"
         "#define TRAINER_DALTON_2 TRAINER_JOGGER_RICHARD_R209\n"),
        ("#define TRAINER_DALTON_3                    198\n",
         "#define TRAINER_TWINS_EMMA_LIL_R209                    198 // Sinnoh M18: was TRAINER_DALTON_3\n"
         "#define TRAINER_DALTON_3 TRAINER_TWINS_EMMA_LIL_R209\n"),
        ("#define TRAINER_DALTON_4                    199\n",
         "#define TRAINER_YOUNG_COUPLE_R209                    199 // Sinnoh M18: was TRAINER_DALTON_4\n"
         "#define TRAINER_DALTON_4 TRAINER_YOUNG_COUPLE_R209\n"),
        ("#define TRAINER_DALTON_5                    200\n",
         "#define TRAINER_TWINS_TERI_TIA_R210                    200 // Sinnoh M18: was TRAINER_DALTON_5\n"
         "#define TRAINER_DALTON_5 TRAINER_TWINS_TERI_TIA_R210\n"),
        ("#define TRAINER_BERNIE_2                    207\n",
         "#define TRAINER_BREEDER_KAHLIL_R210                    207 // Sinnoh M18: was TRAINER_BERNIE_2\n"
         "#define TRAINER_BERNIE_2 TRAINER_BREEDER_KAHLIL_R210\n"),
        ("#define TRAINER_BERNIE_3                    208\n",
         "#define TRAINER_BREEDER_AMBER_R210                    208 // Sinnoh M18: was TRAINER_BERNIE_3\n"
         "#define TRAINER_BERNIE_3 TRAINER_BREEDER_AMBER_R210\n"),
        ("#define TRAINER_BERNIE_4                    209\n",
         "#define TRAINER_BELLE_AND_PA_R210                    209 // Sinnoh M18: was TRAINER_BERNIE_4\n"
         "#define TRAINER_BERNIE_4 TRAINER_BELLE_AND_PA_R210\n"),
        ("#define TRAINER_BERNIE_5                    210\n",
         "#define TRAINER_RANCHER_MARCO_R210                    210 // Sinnoh M18: was TRAINER_BERNIE_5\n"
         "#define TRAINER_BERNIE_5 TRAINER_RANCHER_MARCO_R210\n"),
        ("#define TRAINER_CAMERON_2                   239\n",
         "#define TRAINER_JOGGER_WYATT_R210                   239 // Sinnoh M18: was TRAINER_CAMERON_2\n"
         "#define TRAINER_CAMERON_2 TRAINER_JOGGER_WYATT_R210\n"),
        ("#define TRAINER_CAMERON_3                   240\n",
         "#define TRAINER_BOY_GRASS_R210                   240 // Sinnoh M18: was TRAINER_CAMERON_3\n"
         "#define TRAINER_CAMERON_3 TRAINER_BOY_GRASS_R210\n"),
        ("#define TRAINER_CAMERON_4                   241\n",
         "#define TRAINER_BLACK_BELT_DEREK_R215                   241 // Sinnoh M18: was TRAINER_CAMERON_4\n"
         "#define TRAINER_CAMERON_4 TRAINER_BLACK_BELT_DEREK_R215\n"),
        ("#define TRAINER_CAMERON_5                   242\n",
         "#define TRAINER_BLACK_BELT_GREGORY_R215                   242 // Sinnoh M18: was TRAINER_CAMERON_5\n"
         "#define TRAINER_CAMERON_5 TRAINER_BLACK_BELT_GREGORY_R215\n"),
        ("#define TRAINER_JACKI_2                     250\n",
         "#define TRAINER_BLACK_BELT_NATHANIEL_R215                     250 // Sinnoh M18: was TRAINER_JACKI_2\n"
         "#define TRAINER_JACKI_2 TRAINER_BLACK_BELT_NATHANIEL_R215\n"),
        ("#define TRAINER_JACKI_3                     251\n",
         "#define TRAINER_RUIN_MANIAC_CALVIN_R215                     251 // Sinnoh M18: was TRAINER_JACKI_3\n"
         "#define TRAINER_JACKI_3 TRAINER_RUIN_MANIAC_CALVIN_R215\n"),
        ("#define TRAINER_JACKI_4                     252\n",
         "#define TRAINER_JOGGER_CRAIG_R215                     252 // Sinnoh M18: was TRAINER_JACKI_4\n"
         "#define TRAINER_JACKI_4 TRAINER_JOGGER_CRAIG_R215\n"),
        ("#define TRAINER_JACKI_5                     253\n",
         "#define TRAINER_JOGGER_SCOTT_R215                     253 // Sinnoh M18: was TRAINER_JACKI_5\n"
         "#define TRAINER_JACKI_5 TRAINER_JOGGER_SCOTT_R215\n"),
        ("#define TRAINER_WALTER_2                    257\n",
         "#define TRAINER_ACE_TRAINER_DENNIS_R215                    257 // Sinnoh M18: was TRAINER_WALTER_2\n"
         "#define TRAINER_WALTER_2 TRAINER_ACE_TRAINER_DENNIS_R215\n"),
        ("#define TRAINER_WALTER_3                    258\n",
         "#define TRAINER_ACE_TRAINER_ALEXIA_R215                    258 // Sinnoh M18: was TRAINER_WALTER_3\n"
         "#define TRAINER_WALTER_3 TRAINER_ACE_TRAINER_ALEXIA_R215\n"),
        ("#define TRAINER_WALTER_4                    259\n",
         "#define TRAINER_ACE_TRAINER_ERNEST_R215                    259 // Sinnoh M18: was TRAINER_WALTER_4\n"
         "#define TRAINER_WALTER_4 TRAINER_ACE_TRAINER_ERNEST_R215\n"),
        ("#define TRAINER_WALTER_5                    260\n",
         "#define TRAINER_CHANNELER_KARINA_LT                    260 // Sinnoh M18: was TRAINER_WALTER_5\n"
         "#define TRAINER_WALTER_5 TRAINER_CHANNELER_KARINA_LT\n"),
        ("#define TRAINER_BRENT                       223\n",
         "#define TRAINER_PSYCHIC_VALERIUS_LT                       223 // Sinnoh M18: was TRAINER_BRENT\n"
         "#define TRAINER_BRENT TRAINER_PSYCHIC_VALERIUS_LT\n"),
        ("#define TRAINER_DONALD                      224\n",
         "#define TRAINER_CHANNELER_MOLLY_LT                      224 // Sinnoh M18: was TRAINER_DONALD\n"
         "#define TRAINER_DONALD TRAINER_CHANNELER_MOLLY_LT\n"),
        ("#define TRAINER_TAYLOR                      225\n",
         "#define TRAINER_LASS_CATHERINE_LT                      225 // Sinnoh M18: was TRAINER_TAYLOR\n"
         "#define TRAINER_TAYLOR TRAINER_LASS_CATHERINE_LT\n"),
        ("#define TRAINER_DEREK                       227\n",
         "#define TRAINER_CHANNELER_REINA_LT                       227 // Sinnoh M18: was TRAINER_DEREK\n"
         "#define TRAINER_DEREK TRAINER_CHANNELER_REINA_LT\n"),
        ("#define TRAINER_EDWARD                      232\n",
         "#define TRAINER_PSYCHIC_LINDSAY_LT                      232 // Sinnoh M18: was TRAINER_EDWARD\n"
         "#define TRAINER_EDWARD TRAINER_PSYCHIC_LINDSAY_LT\n"),
        ("#define TRAINER_PRESTON                     233\n",
         "#define TRAINER_CAFE_COLLECTOR_R210                     233 // Sinnoh M18: was TRAINER_PRESTON\n"
         "#define TRAINER_PRESTON TRAINER_CAFE_COLLECTOR_R210\n"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
    path.write_text(text)
    print("patched opponents.h")


def _party_block(header_name, name, cls, pic, gender, music, mons, double_battle=False):
    lines = [
        f"=== {header_name} ===",
        f"Name: {name}",
        f"Class: {cls}",
        f"Pic: {pic}",
        f"Gender: {gender}",
        f"Music: {music}",
        f"Double Battle: {'Yes' if double_battle else 'No'}",
        "AI: Basic Trainer",
        "",
    ]
    for mon in mons:
        sp, lv, moves = mon
        lines.append(sp)
        lines.append(f"Level: {lv}")
        lines.append("IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe")
        for mv in moves:
            lines.append(f"- {mv}")
        lines.append("")
    return "\n".join(lines) + "\n"


def patch_trainers_party():
    path = REPO / "src" / "data" / "trainers.party"
    text = path.read_text()
    if "TRAINER_BREEDER_ALBERT_R209" in text:
        print("trainers.party already has M18")
        return

    parties = {
        "TRAINER_JEFFREY_3": _party_block(
            "TRAINER_BREEDER_ALBERT_R209", "ALBERT", "Pkmn Breeder", "Pokemon Breeder M", "Male", "Male",
            [("Bidoof", 16, ["Tackle", "Growl", "Defense Curl", "Rollout"]),
             ("Buizel", 17, ["Aqua Jet", "Growl", "Water Sport", "Quick Attack"])]),
        "TRAINER_JEFFREY_4": _party_block(
            "TRAINER_BREEDER_JENNIFER_R209", "JENNIFER", "Pkmn Breeder", "Pokemon Breeder F", "Female", "Female",
            [("Mime Jr.", 18, ["Confusion", "Barrier", "Copycat", "Tickle"]),
             ("Roselia", 18, ["Absorb", "Stun Spore", "Mega Drain", "Growth"])]),
        "TRAINER_JEFFREY_5": _party_block(
            "TRAINER_COWGIRL_SHELLEY_R209", "SHELLEY", "Beauty", "Beauty", "Female", "Female",
            [("Ponyta", 19, ["Ember", "Stomp", "Tail Whip", "Growl"])]),
        "TRAINER_DALTON_2": _party_block(
            "TRAINER_JOGGER_RICHARD_R209", "RICHARD", "Triathlete", "Running Triathlete M", "Male", "Male",
            [("Staravia", 19, ["Quick Attack", "Wing Attack", "Double Team", "Endeavor"])]),
        "TRAINER_DALTON_3": _party_block(
            "TRAINER_TWINS_EMMA_LIL_R209", "EMMA & LIL", "Twins", "Twins", "Female", "Twins",
            [("Cleffa", 17, ["Pound", "Charm", "Encore", "Sing"]),
             ("Cleffa", 17, ["Pound", "Charm", "Encore", "Sing"])], double_battle=True),
        "TRAINER_DALTON_4": _party_block(
            "TRAINER_YOUNG_COUPLE_R209", "MIKE & NAT", "Young Couple", "Young Couple", "Male", "Girl",
            [("Pikachu", 18, ["Thunder Shock", "Quick Attack", "Tail Whip", "Thunder Wave"]),
             ("Pikachu", 18, ["Thunder Shock", "Quick Attack", "Growl", "Double Team"])], double_battle=True),
        "TRAINER_DALTON_5": _party_block(
            "TRAINER_TWINS_TERI_TIA_R210", "TERI & TIA", "Twins", "Twins", "Female", "Twins",
            [("Pichu", 18, ["Thunder Shock", "Charm", "Tail Whip", "Sweet Kiss"]),
             ("Pichu", 18, ["Thunder Shock", "Charm", "Tail Whip", "Sweet Kiss"])], double_battle=True),
        "TRAINER_BERNIE_2": _party_block(
            "TRAINER_BREEDER_KAHLIL_R210", "KAHLIL", "Pkmn Breeder", "Pokemon Breeder M", "Male", "Male",
            [("Happiny", 19, ["Pound", "Charm", "Copycat", "Refresh"]),
             ("Elekid", 20, ["Thunder Shock", "Quick Attack", "Leer", "Swift"])]),
        "TRAINER_BERNIE_3": _party_block(
            "TRAINER_BREEDER_AMBER_R210", "AMBER", "Pkmn Breeder", "Pokemon Breeder F", "Female", "Female",
            [("Mime Jr.", 20, ["Confusion", "Barrier", "Copycat", "Meditate"]),
             ("Bonsly", 20, ["Rock Throw", "Flail", "Low Kick", "Copycat"])]),
        "TRAINER_BERNIE_4": _party_block(
            "TRAINER_BELLE_AND_PA_R210", "BELLE & PA", "Sr And Jr", "Sr And Jr", "Female", "Girl",
            [("Ponyta", 20, ["Ember", "Stomp", "Tail Whip", "Growl"]),
             ("Marill", 20, ["Bubble Beam", "Defense Curl", "Rollout", "Aqua Jet"])], double_battle=True),
        "TRAINER_BERNIE_5": _party_block(
            "TRAINER_RANCHER_MARCO_R210", "MARCO", "Hiker", "Hiker", "Male", "Hiker",
            [("Stunky", 20, ["Poison Gas", "Scratch", "Focus Energy", "Smokescreen"]),
             ("Ponyta", 21, ["Ember", "Stomp", "Tail Whip", "Growl"])]),
        "TRAINER_CAMERON_2": _party_block(
            "TRAINER_JOGGER_WYATT_R210", "WYATT", "Triathlete", "Running Triathlete M", "Male", "Male",
            [("Machop", 21, ["Low Kick", "Leer", "Focus Energy", "Karate Chop"])]),
        "TRAINER_CAMERON_3": _party_block(
            "TRAINER_BOY_GRASS_R210", "TYLER", "Youngster", "Youngster", "Male", "Male",
            [("Croagunk", 19, ["Poison Sting", "Mud Slap", "Astonish", "Taunt"])]),
        "TRAINER_CAMERON_4": _party_block(
            "TRAINER_BLACK_BELT_DEREK_R215", "DEREK", "Black Belt", "Black Belt", "Male", "Intense",
            [("Machoke", 22, ["Karate Chop", "Low Kick", "Seismic Toss", "Focus Energy"])]),
        "TRAINER_CAMERON_5": _party_block(
            "TRAINER_BLACK_BELT_GREGORY_R215", "GREGORY", "Black Belt", "Black Belt", "Male", "Intense",
            [("Meditite", 22, ["Confusion", "Detect", "Force Palm", "Meditate"]),
             ("Machop", 22, ["Karate Chop", "Seismic Toss", "Foresight", "Revenge"])]),
        "TRAINER_JACKI_2": _party_block(
            "TRAINER_BLACK_BELT_NATHANIEL_R215", "NATHANIEL", "Black Belt", "Black Belt", "Male", "Intense",
            [("Machoke", 23, ["Karate Chop", "Seismic Toss", "Revenge", "Vital Throw"])]),
        "TRAINER_JACKI_3": _party_block(
            "TRAINER_RUIN_MANIAC_CALVIN_R215", "CALVIN", "Hiker", "Hiker", "Male", "Hiker",
            [("Bronzor", 22, ["Confusion", "Confuse Ray", "Extrasensory", "Iron Defense"]),
             ("Geodude", 22, ["Rock Throw", "Magnitude", "Defense Curl", "Rollout"])]),
        "TRAINER_JACKI_4": _party_block(
            "TRAINER_JOGGER_CRAIG_R215", "CRAIG", "Triathlete", "Running Triathlete M", "Male", "Male",
            [("Staravia", 22, ["Wing Attack", "Quick Attack", "Double Team", "Endeavor"])]),
        "TRAINER_JACKI_5": _party_block(
            "TRAINER_JOGGER_SCOTT_R215", "SCOTT", "Triathlete", "Running Triathlete M", "Male", "Male",
            [("Staravia", 23, ["Wing Attack", "Quick Attack", "Endeavor", "Aerial Ace"])]),
        "TRAINER_WALTER_2": _party_block(
            "TRAINER_ACE_TRAINER_DENNIS_R215", "DENNIS", "Cooltrainer", "Cooltrainer M", "Male", "Male",
            [("Gligar", 23, ["Wing Attack", "Sand Attack", "Slash", "Poison Sting"]),
             ("Buizel", 23, ["Aqua Jet", "Pursuit", "Swift", "Sonic Boom"])]),
        "TRAINER_WALTER_3": _party_block(
            "TRAINER_ACE_TRAINER_ALEXIA_R215", "ALEXIA", "Cooltrainer", "Cooltrainer F", "Female", "Female",
            [("Roselia", 23, ["Mega Drain", "Stun Spore", "Magical Leaf", "Growth"]),
             ("Ponyta", 24, ["Ember", "Stomp", "Flame Wheel", "Tail Whip"])]),
        "TRAINER_WALTER_4": _party_block(
            "TRAINER_ACE_TRAINER_ERNEST_R215", "ERNEST", "Cooltrainer", "Cooltrainer M", "Male", "Male",
            [("Machoke", 24, ["Karate Chop", "Seismic Toss", "Revenge", "Vital Throw"]),
             ("Kadabra", 24, ["Confusion", "Disable", "Psybeam", "Reflect"])]),
        "TRAINER_WALTER_5": _party_block(
            "TRAINER_CHANNELER_KARINA_LT", "KARINA", "Hex Maniac", "Hex Maniac", "Female", "Suspicious",
            [("Gastly", 17, ["Lick", "Confuse Ray", "Night Shade", "Hypnosis"])]),
        "TRAINER_BRENT": _party_block(
            "TRAINER_PSYCHIC_VALERIUS_LT", "VALERIUS", "Psychic", "Psychic M", "Male", "Intense",
            [("Abra", 18, ["Teleport"]),
             ("Duskull", 18, ["Astonish", "Disable", "Pursuit", "Confuse Ray"])]),
        "TRAINER_DONALD": _party_block(
            "TRAINER_CHANNELER_MOLLY_LT", "MOLLY", "Hex Maniac", "Hex Maniac", "Female", "Suspicious",
            [("Gastly", 18, ["Lick", "Mean Look", "Curse", "Night Shade"]),
             ("Haunter", 19, ["Night Shade", "Confuse Ray", "Curse", "Shadow Punch"])]),
        "TRAINER_TAYLOR": _party_block(
            "TRAINER_LASS_CATHERINE_LT", "CATHERINE", "Lass", "Lass", "Female", "Female",
            [("Gastly", 19, ["Lick", "Confuse Ray", "Hypnosis", "Night Shade"]),
             ("Drifloon", 19, ["Astonish", "Gust", "Focus Energy", "Payback"])]),
        "TRAINER_DEREK": _party_block(
            "TRAINER_CHANNELER_REINA_LT", "REINA", "Hex Maniac", "Hex Maniac", "Female", "Suspicious",
            [("Haunter", 20, ["Night Shade", "Confuse Ray", "Curse", "Shadow Punch"])]),
        "TRAINER_EDWARD": _party_block(
            "TRAINER_PSYCHIC_LINDSAY_LT", "LINDSAY", "Psychic", "Psychic M", "Male", "Intense",
            [("Chingling", 20, ["Confusion", "Growl", "Astonish", "Yawn"]),
             ("Kadabra", 21, ["Confusion", "Disable", "Psybeam", "Reflect"])]),
        "TRAINER_PRESTON": _party_block(
            "TRAINER_CAFE_COLLECTOR_R210", "JORDAN", "Collector", "Collector", "Male", "Suspicious",
            [("Staravia", 20, ["Wing Attack", "Quick Attack", "Double Team", "Endeavor"]),
             ("Buizel", 20, ["Aqua Jet", "Pursuit", "Sonic Boom", "Growl"])]),
    }

    def replace_party(src: str, old_name: str, new_block: str) -> str:
        pattern = rf"=== {old_name} ===.*?(?=\n=== |\Z)"
        m = re.search(pattern, src, flags=re.S)
        if not m:
            print("WARN: missing", old_name)
            return src
        return src[: m.start()] + new_block + src[m.end():]

    for old, block in parties.items():
        text = replace_party(text, old, block)
    path.write_text(text)
    print("patched trainers.party")


def patch_wilds():
    path = REPO / "src" / "data" / "wild_encounters.json"
    data = json.loads(path.read_text())
    encs = data["wild_encounter_groups"][0]["encounters"]
    drop = {
        "MAP_ROUTE209", "MAP_ROUTE210_SOUTH", "MAP_ROUTE215",
        "MAP_LOST_TOWER_1F", "MAP_LOST_TOWER_2F", "MAP_LOST_TOWER_3F",
        "MAP_LOST_TOWER_4F", "MAP_LOST_TOWER_5F",
    }
    encs[:] = [e for e in encs if e.get("map") not in drop]

    r209 = [
        ("SPECIES_ROSELIA", 17), ("SPECIES_BIBAREL", 17), ("SPECIES_STARAVIA", 18), ("SPECIES_RALTS", 16),
        ("SPECIES_CHANSEY", 16), ("SPECIES_ROSELIA", 18), ("SPECIES_BIBAREL", 18), ("SPECIES_STARAVIA", 19),
        ("SPECIES_RALTS", 17), ("SPECIES_CHANSEY", 17), ("SPECIES_ROSELIA", 19), ("SPECIES_BIBAREL", 19),
    ]
    r209_night = list(r209)
    r209_night[0] = ("SPECIES_ZUBAT", 17)
    r209_night[2] = ("SPECIES_DUSKULL", 18)
    r209_night[4] = ("SPECIES_ZUBAT", 16)

    r210 = [
        ("SPECIES_STARAVIA", 18), ("SPECIES_GEODUDE", 17), ("SPECIES_SCYTHER", 19), ("SPECIES_PONYTA", 18),
        ("SPECIES_ROSELIA", 18), ("SPECIES_CHANSEY", 17), ("SPECIES_STARAVIA", 19), ("SPECIES_GEODUDE", 18),
        ("SPECIES_SCYTHER", 20), ("SPECIES_PONYTA", 19), ("SPECIES_ROSELIA", 19), ("SPECIES_CHANSEY", 18),
    ]
    r210_night = list(r210)
    r210_night[1] = ("SPECIES_ZUBAT", 17)
    r210_night[5] = ("SPECIES_DUSKULL", 17)

    r215 = [
        ("SPECIES_STARAVIA", 19), ("SPECIES_MARILL", 18), ("SPECIES_SCYTHER", 20), ("SPECIES_LICKITUNG", 19),
        ("SPECIES_ABRA", 18), ("SPECIES_KADABRA", 20), ("SPECIES_STARAVIA", 20), ("SPECIES_MARILL", 19),
        ("SPECIES_SCYTHER", 21), ("SPECIES_LICKITUNG", 20), ("SPECIES_ABRA", 19), ("SPECIES_KADABRA", 21),
    ]
    r215_night = list(r215)
    r215_night[0] = ("SPECIES_ZUBAT", 19)
    r215_night[4] = ("SPECIES_ZUBAT", 18)

    lt = [
        ("SPECIES_GASTLY", 16), ("SPECIES_ZUBAT", 16), ("SPECIES_DUSKULL", 17), ("SPECIES_GASTLY", 17),
        ("SPECIES_GOLBAT", 18), ("SPECIES_DUSKULL", 18), ("SPECIES_GASTLY", 18), ("SPECIES_ZUBAT", 17),
        ("SPECIES_GOLBAT", 19), ("SPECIES_DUSKULL", 19), ("SPECIES_GASTLY", 19), ("SPECIES_ZUBAT", 18),
    ]

    new_entries = []
    for mid, label, day, night, rate in [
        ("MAP_ROUTE209", "gRoute209", r209, r209_night, 30),
        ("MAP_ROUTE210_SOUTH", "gRoute210South", r210, r210_night, 30),
        ("MAP_ROUTE215", "gRoute215", r215, r215_night, 30),
        ("MAP_LOST_TOWER_1F", "gLostTower1F", lt, lt, 10),
        ("MAP_LOST_TOWER_2F", "gLostTower2F", lt, lt, 10),
        ("MAP_LOST_TOWER_3F", "gLostTower3F", lt, lt, 10),
        ("MAP_LOST_TOWER_4F", "gLostTower4F", lt, lt, 10),
        ("MAP_LOST_TOWER_5F", "gLostTower5F", lt, lt, 10),
    ]:
        new_entries.append(land_entry(mid, label, day, rate))
        new_entries.append(land_entry(mid, label + "_Day", day, rate))
        new_entries.append(land_entry(mid, label + "_Night", night, rate))

    insert_at = len(encs)
    for i, e in enumerate(encs):
        if "BATTLE_PYRAMID" in e.get("map", "") or "BattlePyramid" in e.get("base_label", ""):
            insert_at = i
            break
    for j, e in enumerate(new_entries):
        encs.insert(insert_at + j, e)
    path.write_text(json.dumps(data, indent=2) + "\n")
    print("patched wild_encounters.json")


def patch_tms_hms():
    path = REPO / "include" / "constants" / "tms_hms.h"
    text = path.read_text()
    if "F(PAYBACK)" in text:
        print("tms_hms.h already has PAYBACK")
        return
    text = text.replace(
        "    F(OVERHEAT)\n",
        "    F(OVERHEAT) \\\n    F(PAYBACK)\n",
    )
    path.write_text(text)
    print("patched tms_hms.h")


def patch_items_payback():
    path = REPO / "src" / "data" / "items.h"
    text = path.read_text()
    if "[ITEM_TM_PAYBACK]" in text:
        print("items.h already has ITEM_TM_PAYBACK")
        return
    # Prefer replacing placeholder TM51 (same enum index once FOREACH adds PAYBACK)
    old = '''    [ITEM_TM51] =
    {
        .name = ITEM_NAME("TM51"),
        .price = 3000,
        .description = COMPOUND_STRING("?????"), // Todo
        .importance = I_REUSABLE_TMS,
        .pocket = POCKET_TM_HM,
        .type = ITEM_USE_PARTY_MENU,
        .fieldUseFunc = ItemUseOutOfBattle_TMHM,
    },'''
    new = '''    [ITEM_TM_PAYBACK] =
    {
        .name = ITEM_NAME("TM66"),
        .price = 3000,
        .description = COMPOUND_STRING(
            "An attack that is\n"
            "boosted if user is\n"
            "hit first."),
        .importance = I_REUSABLE_TMS,
        .pocket = POCKET_TM_HM,
        .type = ITEM_USE_PARTY_MENU,
        .fieldUseFunc = ItemUseOutOfBattle_TMHM,
    },'''
    if old in text:
        text = text.replace(old, new, 1)
    else:
        # Fallback: insert after OVERHEAT
        anchor = '''    [ITEM_TM_OVERHEAT] =
    {
        .name = ITEM_NAME("TM50"),
        .price = 3000,
        .description = COMPOUND_STRING(
            "Enables full-power\n"
            "attack, but harshly\n"
            "lowers Sp. Atk."),
        .importance = I_REUSABLE_TMS,
        .pocket = POCKET_TM_HM,
        .type = ITEM_USE_PARTY_MENU,
        .fieldUseFunc = ItemUseOutOfBattle_TMHM,
    },'''
        text = text.replace(anchor, anchor + "\n\n" + new, 1)
    path.write_text(text)
    print("patched items.h for PAYBACK TM")



def patch_event_scripts():
    path = REPO / "data" / "event_scripts.s"
    text = path.read_text()
    marker = '\t.include "data/maps/HearthomeCity_Route212Gate/scripts.inc"\n'
    block = marker + """\t.include "data/maps/Route209/scripts.inc"
\t.include "data/maps/LostTower_1F/scripts.inc"
\t.include "data/maps/LostTower_2F/scripts.inc"
\t.include "data/maps/LostTower_3F/scripts.inc"
\t.include "data/maps/LostTower_4F/scripts.inc"
\t.include "data/maps/LostTower_5F/scripts.inc"
\t.include "data/maps/SolaceonTown/scripts.inc"
\t.include "data/maps/SolaceonTown_PokemonCenter_1F/scripts.inc"
\t.include "data/maps/SolaceonTown_PokemonCenter_2F/scripts.inc"
\t.include "data/maps/SolaceonTown_Mart/scripts.inc"
\t.include "data/maps/SolaceonTown_PokemonDayCare/scripts.inc"
\t.include "data/maps/SolaceonTown_NewsPress/scripts.inc"
\t.include "data/maps/SolaceonTown_NorthHouse/scripts.inc"
\t.include "data/maps/SolaceonTown_NortheastHouse/scripts.inc"
\t.include "data/maps/SolaceonTown_EastHouse/scripts.inc"
\t.include "data/maps/SolaceonRuins_ExteriorGate/scripts.inc"
\t.include "data/maps/Route210_South/scripts.inc"
\t.include "data/maps/Route210_CafeCabin/scripts.inc"
\t.include "data/maps/Route215/scripts.inc"
\t.include "data/maps/Route215_VeilstoneGate/scripts.inc"
"""
    if 'data/maps/Route209/scripts.inc' not in text and marker in text:
        text = text.replace(marker, block, 1)
        path.write_text(text)
        print("patched event_scripts.s")
    else:
        print("event_scripts.s already has M18 includes or marker missing")


def main():
    scaffold_route209()
    scaffold_solaceon_town()
    scaffold_route210_south()
    scaffold_route215()
    scaffold_lost_tower()
    scaffold_solaceon_center()
    scaffold_solaceon_mart()
    scaffold_solaceon_daycare()
    scaffold_solaceon_houses()
    scaffold_solaceon_ruins_gate()
    scaffold_cafe_cabin()
    scaffold_veilstone_gate()
    patch_route209_gate()
    patch_map_groups()
    patch_region_mapsecs()
    patch_regions_h()
    patch_map_name_popup()
    patch_heal_locations()
    patch_flags_vars()
    patch_opponents()
    patch_trainers_party()
    patch_wilds()
    patch_tms_hms()
    patch_items_payback()
    print("M18 scaffold complete.")


if __name__ == "__main__":
    main()
