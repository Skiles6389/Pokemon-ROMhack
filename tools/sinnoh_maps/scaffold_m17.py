#!/usr/bin/env python3
"""Scaffold M17 Hearthome City maps, scripts, constants, trainers, heal/music wiring."""
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


def write_map(name: str, data: dict, scripts: str):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("wrote", name)


def outdoor_base(map_id, name, layout, music="MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT", mapsec="MAPSEC_HEARTHOME_CITY", map_type="MAP_TYPE_CITY"):
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


def indoor_base(map_id, name, layout, music, mapsec="MAPSEC_HEARTHOME_CITY", night=None, show_name=False, battle="MAP_BATTLE_SCENE_NORMAL"):
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


# ---------- City overworld ----------
def scaffold_city():
    data = outdoor_base("MAP_HEARTHOME_CITY", "HearthomeCity", "LAYOUT_HEARTHOME_CITY")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_YOUNGSTER", 54, 54, "HearthomeCity_EventScript_Barry", flag="FLAG_HIDE_HEARTHOME_BARRY", local_id="LOCALID_HEARTHOME_BARRY", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_BEAUTY", 51, 26, "HearthomeCity_EventScript_FantinaCameo", flag="FLAG_HIDE_HEARTHOME_FANTINA", movement="MOVEMENT_TYPE_FACE_UP"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 20, 28, "HearthomeCity_EventScript_Woman", movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=2, range_y=2),
        obj("OBJ_EVENT_GFX_MAN_1", 33, 30, "HearthomeCity_EventScript_Man", movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=1, range_y=2),
        obj("OBJ_EVENT_GFX_GIRL_1", 42, 27, "HearthomeCity_EventScript_Girl", movement="MOVEMENT_TYPE_LOOK_AROUND"),
        obj("OBJ_EVENT_GFX_BOY_1", 28, 40, "HearthomeCity_EventScript_Boy", movement="MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT", range_x=2),
        obj("OBJ_EVENT_GFX_OLD_WOMAN", 15, 39, "HearthomeCity_EventScript_OldWoman"),
        obj("OBJ_EVENT_GFX_FAT_MAN", 35, 22, "HearthomeCity_EventScript_FatMan"),
    ]
    # Warp index comments in scripts for interiors
    data["warp_events"] = [
        warp(17, 25, "MAP_HEARTHOME_CITY_POKEMON_CENTER_1F", 0),  # 0
        warp(18, 25, "MAP_HEARTHOME_CITY_POKEMON_CENTER_1F", 1),  # 1
        warp(22, 25, "MAP_HEARTHOME_CITY_BEBES_HOUSE", 0),  # 2
        warp(51, 25, "MAP_HEARTHOME_CITY_GYM", 0),  # 3
        warp(29, 38, "MAP_HEARTHOME_CITY_MART", 0),  # 4
        warp(40, 38, "MAP_HEARTHOME_CITY_POKEMON_FAN_CLUB", 0),  # 5
        warp(12, 37, "MAP_HEARTHOME_CITY_FOREIGN_BUILDING", 0),  # 6
        warp(31, 19, "MAP_HEARTHOME_CITY_CONTEST_LOBBY", 0),  # 7
        warp(10, 11, "MAP_HEARTHOME_CITY_AMITY_SQUARE_WEST_GATE", 0),  # 8
        warp(11, 11, "MAP_HEARTHOME_CITY_AMITY_SQUARE_WEST_GATE", 1),  # 9
        warp(52, 11, "MAP_HEARTHOME_CITY_AMITY_SQUARE_EAST_GATE", 0),  # 10
        warp(53, 11, "MAP_HEARTHOME_CITY_AMITY_SQUARE_EAST_GATE", 1),  # 11
        warp(6, 54, "MAP_ROUTE208_HEARTHOME_GATE", 2),  # 12 west to R208 gate east
        warp(6, 55, "MAP_ROUTE208_HEARTHOME_GATE", 3),  # 13
        warp(57, 54, "MAP_HEARTHOME_CITY_ROUTE209_GATE", 0),  # 14
        warp(57, 55, "MAP_HEARTHOME_CITY_ROUTE209_GATE", 1),  # 15
        warp(10, 57, "MAP_HEARTHOME_CITY_ROUTE212_GATE", 0),  # 16
        warp(11, 57, "MAP_HEARTHOME_CITY_ROUTE212_GATE", 1),  # 17
        warp(24, 38, "MAP_HEARTHOME_CITY_POFFIN_HOUSE", 0),  # 18
    ]
    data["coord_events"] = [
        trigger(53, 54, "HearthomeCity_EventScript_BarryTrigger", "VAR_HEARTHOME_CITY_STATE", "0"),
        trigger(53, 55, "HearthomeCity_EventScript_BarryTrigger", "VAR_HEARTHOME_CITY_STATE", "0"),
        trigger(54, 53, "HearthomeCity_EventScript_BarryTrigger", "VAR_HEARTHOME_CITY_STATE", "0"),
    ]
    data["bg_events"] = [
        sign(51, 26, "HearthomeCity_EventScript_GymSign"),
        sign(19, 27, "HearthomeCity_EventScript_CitySign"),
        sign(32, 20, "HearthomeCity_EventScript_ContestSign"),
    ]
    scripts = r'''HearthomeCity_MapScripts::
	.byte 0

HearthomeCity_EventScript_BarryTrigger::
	lockall
	goto_if_unset FLAG_BADGE03_GET, HearthomeCity_EventScript_NeedRelicBadge
	goto_if_set FLAG_HIDE_HEARTHOME_BARRY, HearthomeCity_EventScript_BarryAlreadyDone
	playse SE_PIN
	applymovement LOCALID_HEARTHOME_BARRY, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_HEARTHOME_BARRY, Common_Movement_FacePlayer
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceRight
	waitmovement 0
	msgbox HearthomeCity_Text_BarryIntro, MSGBOX_DEFAULT
	switch VAR_ROUTE201_BARRY_MON
	case 0, HearthomeCity_EventScript_BattleChimchar
	case 1, HearthomeCity_EventScript_BattlePiplup
	case 2, HearthomeCity_EventScript_BattleTurtwig
	end

HearthomeCity_EventScript_NeedRelicBadge::
	msgbox HearthomeCity_Text_NeedRelicBadge, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Movement_PushWest
	waitmovement 0
	releaseall
	end

HearthomeCity_EventScript_BarryAlreadyDone::
	releaseall
	end

HearthomeCity_EventScript_BattleChimchar::
	trainerbattle LOCALID_HEARTHOME_BARRY, TRAINER_BARRY_3_CHIMCHAR, HearthomeCity_Text_BarryChallenge, HearthomeCity_Text_BarryDefeat, HearthomeCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

HearthomeCity_EventScript_BattlePiplup::
	trainerbattle LOCALID_HEARTHOME_BARRY, TRAINER_BARRY_3_PIPLUP, HearthomeCity_Text_BarryChallenge, HearthomeCity_Text_BarryDefeat, HearthomeCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

HearthomeCity_EventScript_BattleTurtwig::
	trainerbattle LOCALID_HEARTHOME_BARRY, TRAINER_BARRY_3_TURTWIG, HearthomeCity_Text_BarryChallenge, HearthomeCity_Text_BarryDefeat, HearthomeCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

HearthomeCity_EventScript_AfterBarry::
	msgbox HearthomeCity_Text_BarryAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_HEARTHOME_BARRY, HearthomeCity_Movement_BarryLeave
	waitmovement 0
	removeobject LOCALID_HEARTHOME_BARRY
	setflag FLAG_HIDE_HEARTHOME_BARRY
	setvar VAR_HEARTHOME_CITY_STATE, 1
	releaseall
	end

HearthomeCity_EventScript_Barry::
	msgbox HearthomeCity_Text_BarryWait, MSGBOX_NPC
	end

HearthomeCity_Movement_PushWest:
	walk_left
	step_end

HearthomeCity_Movement_BarryLeave:
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

HearthomeCity_EventScript_FantinaCameo::
	msgbox HearthomeCity_Text_FantinaCameo, MSGBOX_NPC
	end

HearthomeCity_EventScript_Woman::
	msgbox HearthomeCity_Text_Woman, MSGBOX_NPC
	end

HearthomeCity_EventScript_Man::
	msgbox HearthomeCity_Text_Man, MSGBOX_NPC
	end

HearthomeCity_EventScript_Girl::
	msgbox HearthomeCity_Text_Girl, MSGBOX_NPC
	end

HearthomeCity_EventScript_Boy::
	msgbox HearthomeCity_Text_Boy, MSGBOX_NPC
	end

HearthomeCity_EventScript_OldWoman::
	msgbox HearthomeCity_Text_OldWoman, MSGBOX_NPC
	end

HearthomeCity_EventScript_FatMan::
	msgbox HearthomeCity_Text_FatMan, MSGBOX_NPC
	end

HearthomeCity_EventScript_GymSign::
	msgbox HearthomeCity_Text_GymSign, MSGBOX_SIGN
	end

HearthomeCity_EventScript_CitySign::
	msgbox HearthomeCity_Text_CitySign, MSGBOX_SIGN
	end

HearthomeCity_EventScript_ContestSign::
	msgbox HearthomeCity_Text_ContestSign, MSGBOX_SIGN
	end

HearthomeCity_Text_NeedRelicBadge:
	.string "The gate to Route 209 is sealed for now.\n"
	.string "Challenge FANTINA for the Relic Badge\l"
	.string "before heading east!$"

HearthomeCity_Text_BarryIntro:
	.string "BARRY: There you are!\p"
	.string "I raced through Hearthome and even\n"
	.string "watched the Contests!\p"
	.string "You're not leaving for Route 209\n"
	.string "without a battle!$"

HearthomeCity_Text_BarryChallenge:
	.string "My team is way tougher than before!\n"
	.string "Let's go!$"

HearthomeCity_Text_BarryDefeat:
	.string "Argh! You're still a step ahead!$"

HearthomeCity_Text_BarryAfter:
	.string "BARRY: Fine! You win this round.\p"
	.string "I'm heading to Solaceon next.\n"
	.string "Don't you dare fall behind!$"

HearthomeCity_Text_BarryWait:
	.string "BARRY: Get that Relic Badge, then\n"
	.string "come battle me here!$"

HearthomeCity_Text_FantinaCameo:
	.string "FANTINA: Ooh la la! Contests and Gym\n"
	.string "battles both shine in Hearthome!\p"
	.string "Visit my Gym when you're ready for a\n"
	.string "ghostly performance!$"

HearthomeCity_Text_Woman:
	.string "Hearthome loves Contests almost as\n"
	.string "much as Gym battles.$"

HearthomeCity_Text_Man:
	.string "Amity Square is a peaceful park.\n"
	.string "They're still tidying the gates.$"

HearthomeCity_Text_Girl:
	.string "Bebe raises the cutest EEVEE!\n"
	.string "Her house is by the POKéMON CENTER.$"

HearthomeCity_Text_Boy:
	.string "The Fan Club chairman talks forever\n"
	.string "about friendship and Poffins.$"

HearthomeCity_Text_OldWoman:
	.string "The Foreign Building is quiet.\n"
	.string "People go there to think.$"

HearthomeCity_Text_FatMan:
	.string "Route 212 to the south is closed for\n"
	.string "now. Try the east gate later!$"

HearthomeCity_Text_GymSign:
	.string "HEARTHOME CITY POKéMON GYM\n"
	.string "LEADER: FANTINA\l"
	.string "The Mystical Dancer!$"

HearthomeCity_Text_CitySign:
	.string "HEARTHOME CITY\n"
	.string "Where soft hearts find a home$"

HearthomeCity_Text_ContestSign:
	.string "HEARTHOME SUPER CONTEST HALL\n"
	.string "Show the world your POKéMON's charm!$"
'''
    write_map("HearthomeCity", data, scripts)


def scaffold_center():
    data = indoor_base("MAP_HEARTHOME_CITY_POKEMON_CENTER_1F", "HearthomeCity_PokemonCenter_1F",
                       "LAYOUT_POKEMON_CENTER_1F", "MUS_PL_POKE_CENTER", night="MUS_PL_POKE_CENTER_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_NURSE", 7, 2, "HearthomeCity_PokemonCenter_1F_EventScript_Nurse", local_id="LOCALID_HEARTHOME_NURSE"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 2, 3, "HearthomeCity_PokemonCenter_1F_EventScript_Woman"),
        obj("OBJ_EVENT_GFX_BOY_1", 11, 5, "HearthomeCity_PokemonCenter_1F_EventScript_Boy"),
    ]
    data["warp_events"] = [
        warp(7, 8, "MAP_HEARTHOME_CITY", 0, 3),
        warp(6, 8, "MAP_HEARTHOME_CITY", 0, 3),
        warp(1, 6, "MAP_HEARTHOME_CITY_POKEMON_CENTER_2F", 0, 4),
    ]
    scripts = r'''HearthomeCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, HearthomeCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

HearthomeCity_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_HEARTHOME_CITY
	end

HearthomeCity_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_HEARTHOME_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

HearthomeCity_PokemonCenter_1F_EventScript_Woman::
	msgbox HearthomeCity_PokemonCenter_1F_Text_Woman, MSGBOX_NPC
	end

HearthomeCity_PokemonCenter_1F_EventScript_Boy::
	msgbox HearthomeCity_PokemonCenter_1F_Text_Boy, MSGBOX_NPC
	end

HearthomeCity_PokemonCenter_1F_Text_Woman:
	.string "White-out returns you here safely.\n"
	.string "Nurse Joy never freezes up on us!$"

HearthomeCity_PokemonCenter_1F_Text_Boy:
	.string "I'm resting before FANTINA's Gym.\n"
	.string "Ghost types give me the shivers!$"
'''
    write_map("HearthomeCity_PokemonCenter_1F", data, scripts)

    data2 = indoor_base("MAP_HEARTHOME_CITY_POKEMON_CENTER_2F", "HearthomeCity_PokemonCenter_2F",
                        "LAYOUT_POKEMON_CENTER_2F", "MUS_PL_POKE_CENTER", night="MUS_PL_POKE_CENTER_NIGHT")
    data2["warp_events"] = [warp(1, 6, "MAP_HEARTHOME_CITY_POKEMON_CENTER_1F", 2, 4)]
    scripts2 = "HearthomeCity_PokemonCenter_2F_MapScripts::\n\t.byte 0\n"
    write_map("HearthomeCity_PokemonCenter_2F", data2, scripts2)


def scaffold_mart():
    data = indoor_base("MAP_HEARTHOME_CITY_MART", "HearthomeCity_Mart", "LAYOUT_MART", "MUS_PL_POKE_MART")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 1, 3, "HearthomeCity_Mart_EventScript_Clerk"),
        obj("OBJ_EVENT_GFX_GIRL_2", 7, 2, "HearthomeCity_Mart_EventScript_Girl"),
    ]
    data["warp_events"] = [
        warp(3, 7, "MAP_HEARTHOME_CITY", 4),
        warp(4, 7, "MAP_HEARTHOME_CITY", 4),
    ]
    scripts = r'''HearthomeCity_Mart_MapScripts::
	.byte 0

HearthomeCity_Mart_EventScript_Clerk::
	lock
	faceplayer
	msgbox HearthomeCity_Mart_Text_ClerkAsk, MSGBOX_DEFAULT
	pokemart HearthomeCity_Mart_Pokemart
	msgbox HearthomeCity_Mart_Text_ClerkFarewell, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Mart_EventScript_Girl::
	msgbox HearthomeCity_Mart_Text_Girl, MSGBOX_NPC
	end

	.align 2
HearthomeCity_Mart_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_NONE
	release
	end

HearthomeCity_Mart_Text_ClerkAsk:
	.string "Welcome to Hearthome Mart!\n"
	.string "May I help you?$"

HearthomeCity_Mart_Text_ClerkFarewell:
	.string "Please come again!$"

HearthomeCity_Mart_Text_Girl:
	.string "Stock up before the Gym.\n"
	.string "Ghost battles get spooky!$"
'''
    write_map("HearthomeCity_Mart", data, scripts)


def scaffold_bebe():
    data = indoor_base("MAP_HEARTHOME_CITY_BEBES_HOUSE", "HearthomeCity_BebesHouse", "LAYOUT_HOUSE1", "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_WOMAN_3", 4, 4, "HearthomeCity_BebesHouse_EventScript_Bebe", local_id="LOCALID_BEBE"),
        obj("OBJ_EVENT_GFX_LITTLE_GIRL", 7, 5, "HearthomeCity_BebesHouse_EventScript_Child"),
    ]
    data["warp_events"] = [
        warp(3, 7, "MAP_HEARTHOME_CITY", 2),
        warp(4, 7, "MAP_HEARTHOME_CITY", 2),
    ]
    scripts = r'''HearthomeCity_BebesHouse_MapScripts::
	.byte 0

HearthomeCity_BebesHouse_EventScript_Bebe::
	lock
	faceplayer
	goto_if_set FLAG_GOT_BEBE_EEVEE, HearthomeCity_BebesHouse_EventScript_BebeAfter
	msgbox HearthomeCity_BebesHouse_Text_BebeIntro, MSGBOX_DEFAULT
	setvar VAR_TEMP_1, SPECIES_EEVEE
	givemon SPECIES_EEVEE, 20
	goto_if_eq VAR_RESULT, 0, HearthomeCity_BebesHouse_EventScript_GetEeveeParty
	goto_if_eq VAR_RESULT, 1, HearthomeCity_BebesHouse_EventScript_GetEeveePC
	goto_if_eq VAR_RESULT, 2, Common_EventScript_NoMoreRoomForPokemon
	release
	end

HearthomeCity_BebesHouse_EventScript_GetEeveeParty::
	playfanfare MUS_OBTAIN_ITEM
	message HearthomeCity_BebesHouse_Text_ReceivedEevee
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_EEVEE
	msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, HearthomeCity_BebesHouse_EventScript_SetGotEevee
	call Common_EventScript_GetGiftMonPartySlot
	call Common_EventScript_NameReceivedPartyMon
	goto HearthomeCity_BebesHouse_EventScript_SetGotEevee
	end

HearthomeCity_BebesHouse_EventScript_GetEeveePC::
	playfanfare MUS_OBTAIN_ITEM
	message HearthomeCity_BebesHouse_Text_ReceivedEevee
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_EEVEE
	msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, HearthomeCity_BebesHouse_EventScript_TransferEevee
	call Common_EventScript_NameReceivedBoxMon
	goto HearthomeCity_BebesHouse_EventScript_TransferEevee
	end

HearthomeCity_BebesHouse_EventScript_TransferEevee::
	call Common_EventScript_TransferredToPC
	goto HearthomeCity_BebesHouse_EventScript_SetGotEevee
	end

HearthomeCity_BebesHouse_EventScript_SetGotEevee::
	setflag FLAG_GOT_BEBE_EEVEE
	msgbox HearthomeCity_BebesHouse_Text_BebeCare, MSGBOX_DEFAULT
	release
	end

HearthomeCity_BebesHouse_EventScript_BebeAfter::
	msgbox HearthomeCity_BebesHouse_Text_BebeAfter, MSGBOX_DEFAULT
	release
	end

HearthomeCity_BebesHouse_EventScript_Child::
	msgbox HearthomeCity_BebesHouse_Text_Child, MSGBOX_NPC
	end

HearthomeCity_BebesHouse_Text_BebeIntro:
	.string "BEBE: Welcome!\p"
	.string "I raise EEVEE with all my heart.\n"
	.string "You look like a kind Trainer...\p"
	.string "Please take this EEVEE!\n"
	.string "Raise it with love!$"

HearthomeCity_BebesHouse_Text_ReceivedEevee:
	.string "{PLAYER} received an EEVEE!$"

HearthomeCity_BebesHouse_Text_BebeCare:
	.string "BEBE: Friendship changes EEVEE's\n"
	.string "future. Take good care of it!$"

HearthomeCity_BebesHouse_Text_BebeAfter:
	.string "BEBE: How is EEVEE doing?\n"
	.string "I hope you're the best of friends!$"

HearthomeCity_BebesHouse_Text_Child:
	.string "Mom's EEVEE is so soft!\n"
	.string "I want one when I grow up!$"
'''
    write_map("HearthomeCity_BebesHouse", data, scripts)


def scaffold_fan_club():
    data = indoor_base("MAP_HEARTHOME_CITY_POKEMON_FAN_CLUB", "HearthomeCity_PokemonFanClub",
                       "LAYOUT_SLATEPORT_CITY_POKEMON_FAN_CLUB", "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_GENTLEMAN", 6, 4, "HearthomeCity_PokemonFanClub_EventScript_Chairman"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 2, 6, "HearthomeCity_PokemonFanClub_EventScript_Woman"),
        obj("OBJ_EVENT_GFX_MAN_3", 10, 7, "HearthomeCity_PokemonFanClub_EventScript_Man"),
        obj("OBJ_EVENT_GFX_LITTLE_BOY", 4, 8, "HearthomeCity_PokemonFanClub_EventScript_Boy"),
    ]
    data["warp_events"] = [
        warp(6, 10, "MAP_HEARTHOME_CITY", 5),
        warp(7, 10, "MAP_HEARTHOME_CITY", 5),
    ]
    scripts = r'''HearthomeCity_PokemonFanClub_MapScripts::
	.byte 0

HearthomeCity_PokemonFanClub_EventScript_Chairman::
	msgbox HearthomeCity_PokemonFanClub_Text_Chairman, MSGBOX_NPC
	end

HearthomeCity_PokemonFanClub_EventScript_Woman::
	msgbox HearthomeCity_PokemonFanClub_Text_Woman, MSGBOX_NPC
	end

HearthomeCity_PokemonFanClub_EventScript_Man::
	msgbox HearthomeCity_PokemonFanClub_Text_Man, MSGBOX_NPC
	end

HearthomeCity_PokemonFanClub_EventScript_Boy::
	msgbox HearthomeCity_PokemonFanClub_Text_Boy, MSGBOX_NPC
	end

HearthomeCity_PokemonFanClub_Text_Chairman:
	.string "I'm the Fan Club chairman!\p"
	.string "Friendship and carefully baked Poffins\n"
	.string "make Contests shine!\p"
	.string "Treat your POKéMON kindly and they'll\n"
	.string "answer with dazzling performances!$"

HearthomeCity_PokemonFanClub_Text_Woman:
	.string "I brush my POKéMON every morning.\n"
	.string "Soft coats win Cute Contests!$"

HearthomeCity_PokemonFanClub_Text_Man:
	.string "Poffins boost condition stats.\n"
	.string "Sweet ones are my favorite.$"

HearthomeCity_PokemonFanClub_Text_Boy:
	.string "When my POKéMON likes me a lot,\n"
	.string "it follows me everywhere!$"
'''
    write_map("HearthomeCity_PokemonFanClub", data, scripts)


def scaffold_foreign():
    data = indoor_base("MAP_HEARTHOME_CITY_FOREIGN_BUILDING", "HearthomeCity_ForeignBuilding",
                       "LAYOUT_HOUSE2", "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_EXPERT_M", 5, 4, "HearthomeCity_ForeignBuilding_EventScript_Elder"),
        obj("OBJ_EVENT_GFX_WOMAN_5", 8, 5, "HearthomeCity_ForeignBuilding_EventScript_Woman"),
    ]
    data["warp_events"] = [
        warp(3, 7, "MAP_HEARTHOME_CITY", 6),
        warp(4, 7, "MAP_HEARTHOME_CITY", 6),
    ]
    scripts = r'''HearthomeCity_ForeignBuilding_MapScripts::
	.byte 0

HearthomeCity_ForeignBuilding_EventScript_Elder::
	msgbox HearthomeCity_ForeignBuilding_Text_Elder, MSGBOX_NPC
	end

HearthomeCity_ForeignBuilding_EventScript_Woman::
	msgbox HearthomeCity_ForeignBuilding_Text_Woman, MSGBOX_NPC
	end

HearthomeCity_ForeignBuilding_Text_Elder:
	.string "This hall is for quiet thoughts.\p"
	.string "Sit a while. Let your journey settle\n"
	.string "like dust in a sunbeam.$"

HearthomeCity_ForeignBuilding_Text_Woman:
	.string "I come here when battles grow loud.\n"
	.string "Silence helps me hear my POKéMON.$"
'''
    write_map("HearthomeCity_ForeignBuilding", data, scripts)


def scaffold_contest():
    data = indoor_base("MAP_HEARTHOME_CITY_CONTEST_LOBBY", "HearthomeCity_ContestLobby",
                       "LAYOUT_LILYCOVE_CITY_CONTEST_LOBBY", "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_WOMAN_4", 5, 5, "HearthomeCity_ContestLobby_EventScript_Receptionist"),
        obj("OBJ_EVENT_GFX_BEAUTY", 12, 6, "HearthomeCity_ContestLobby_EventScript_Keira"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 18, 8, "HearthomeCity_ContestLobby_EventScript_Mom"),
        obj("OBJ_EVENT_GFX_MAN_1", 24, 7, "HearthomeCity_ContestLobby_EventScript_Fan"),
    ]
    data["warp_events"] = [
        warp(14, 11, "MAP_HEARTHOME_CITY", 7),
        warp(15, 11, "MAP_HEARTHOME_CITY", 7),
    ]
    scripts = r'''HearthomeCity_ContestLobby_MapScripts::
	.byte 0

HearthomeCity_ContestLobby_EventScript_Receptionist::
	msgbox HearthomeCity_ContestLobby_Text_Receptionist, MSGBOX_NPC
	end

HearthomeCity_ContestLobby_EventScript_Keira::
	msgbox HearthomeCity_ContestLobby_Text_Keira, MSGBOX_NPC
	end

HearthomeCity_ContestLobby_EventScript_Mom::
	msgbox HearthomeCity_ContestLobby_Text_Mom, MSGBOX_NPC
	end

HearthomeCity_ContestLobby_EventScript_Fan::
	msgbox HearthomeCity_ContestLobby_Text_Fan, MSGBOX_NPC
	end

HearthomeCity_ContestLobby_Text_Receptionist:
	.string "Welcome to the Super Contest Hall!\p"
	.string "Full Contest performances aren't open\n"
	.string "yet, but please enjoy the lobby!\p"
	.string "FANTINA often visits--she's both a\n"
	.string "Contest star and our Gym Leader!$"

HearthomeCity_ContestLobby_Text_Keira:
	.string "KEIRA: I'm studying Contest appeals.\p"
	.string "When the stage is ready, I'll teach\n"
	.string "you how to dazzle the judges!$"

HearthomeCity_ContestLobby_Text_Mom:
	.string "My child loves watching Contests.\n"
	.string "Hearthome feels so lively!$"

HearthomeCity_ContestLobby_Text_Fan:
	.string "I hope FANTINA dances on stage again.\n"
	.string "Her Ghost appeals are unforgettable!$"
'''
    write_map("HearthomeCity_ContestLobby", data, scripts)


def scaffold_poffin():
    data = indoor_base("MAP_HEARTHOME_CITY_POFFIN_HOUSE", "HearthomeCity_PoffinHouse", "LAYOUT_HOUSE1",
                       "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_OLD_WOMAN", 4, 4, "HearthomeCity_PoffinHouse_EventScript_Baker"),
    ]
    data["warp_events"] = [
        warp(3, 7, "MAP_HEARTHOME_CITY", 18),
        warp(4, 7, "MAP_HEARTHOME_CITY", 18),
    ]
    scripts = r'''HearthomeCity_PoffinHouse_MapScripts::
	.byte 0

HearthomeCity_PoffinHouse_EventScript_Baker::
	msgbox HearthomeCity_PoffinHouse_Text_Baker, MSGBOX_NPC
	end

HearthomeCity_PoffinHouse_Text_Baker:
	.string "I bake Poffins for Contest hopefuls.\p"
	.string "The ovens aren't ready for guests yet,\n"
	.string "but smell that berry sweetness!$"
'''
    write_map("HearthomeCity_PoffinHouse", data, scripts)


def scaffold_amity_gates():
    for side, mid, wid in (
        ("West", "MAP_HEARTHOME_CITY_AMITY_SQUARE_WEST_GATE", 8),
        ("East", "MAP_HEARTHOME_CITY_AMITY_SQUARE_EAST_GATE", 10),
    ):
        name = f"HearthomeCity_AmitySquare{side}Gate"
        data = indoor_base(mid, name, "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE",
                           "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
        data["allow_cycling"] = True
        data["allow_running"] = True
        data["object_events"] = [
            obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 7, 2, f"{name}_EventScript_Guard"),
        ]
        data["warp_events"] = [
            warp(1, 5, "MAP_HEARTHOME_CITY", wid),
            warp(2, 5, "MAP_HEARTHOME_CITY", wid),
            warp(12, 5, "MAP_HEARTHOME_CITY", wid),
            warp(13, 5, "MAP_HEARTHOME_CITY", wid),
        ]
        data["coord_events"] = [
            trigger(10, 4, f"{name}_EventScript_Closed"),
            trigger(11, 4, f"{name}_EventScript_Closed"),
            trigger(12, 4, f"{name}_EventScript_Closed"),
        ]
        scripts = f'''{name}_MapScripts::
	.byte 0

{name}_EventScript_Guard::
	msgbox {name}_Text_Guard, MSGBOX_NPC
	end

{name}_EventScript_Closed::
	lockall
	msgbox {name}_Text_Closed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, {name}_Movement_Push
	waitmovement 0
	releaseall
	end

{name}_Movement_Push:
	walk_left
	step_end

{name}_Text_Guard:
	.string "Amity Square is a park for Trainers\n"
	.string "and their POKéMON.\p"
	.string "We're still preparing the grounds.$"

{name}_Text_Closed:
	.string "Amity Square is closed for now.\n"
	.string "Please enjoy Hearthome City!$"
'''
        write_map(name, data, scripts)


def scaffold_route212_gate():
    data = indoor_base("MAP_HEARTHOME_CITY_ROUTE212_GATE", "HearthomeCity_Route212Gate",
                       "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE", "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["allow_cycling"] = True
    data["allow_running"] = True
    data["object_events"] = [obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 7, 2, "HearthomeCity_Route212Gate_EventScript_Guard")]
    data["warp_events"] = [
        warp(1, 5, "MAP_HEARTHOME_CITY", 16),
        warp(2, 5, "MAP_HEARTHOME_CITY", 16),
        warp(12, 5, "MAP_HEARTHOME_CITY", 16),
        warp(13, 5, "MAP_HEARTHOME_CITY", 16),
    ]
    data["coord_events"] = [
        trigger(10, 4, "HearthomeCity_Route212Gate_EventScript_Closed"),
        trigger(11, 4, "HearthomeCity_Route212Gate_EventScript_Closed"),
        trigger(12, 4, "HearthomeCity_Route212Gate_EventScript_Closed"),
    ]
    scripts = r'''HearthomeCity_Route212Gate_MapScripts::
	.byte 0

HearthomeCity_Route212Gate_EventScript_Guard::
	msgbox HearthomeCity_Route212Gate_Text_Guard, MSGBOX_NPC
	end

HearthomeCity_Route212Gate_EventScript_Closed::
	lockall
	msgbox HearthomeCity_Route212Gate_Text_Closed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route212Gate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_Route212Gate_Movement_Push:
	walk_left
	step_end

HearthomeCity_Route212Gate_Text_Guard:
	.string "Route 212 stretches south from here.\n"
	.string "It's not open in this demo yet.$"

HearthomeCity_Route212Gate_Text_Closed:
	.string "Route 212 is coming in a later\n"
	.string "milestone!$"
'''
    write_map("HearthomeCity_Route212Gate", data, scripts)


def scaffold_route209_gate():
    data = indoor_base("MAP_HEARTHOME_CITY_ROUTE209_GATE", "HearthomeCity_Route209Gate",
                       "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE", "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["allow_cycling"] = True
    data["allow_running"] = True
    data["object_events"] = [obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 7, 2, "HearthomeCity_Route209Gate_EventScript_Guard")]
    data["warp_events"] = [
        warp(1, 5, "MAP_HEARTHOME_CITY", 14),
        warp(2, 5, "MAP_HEARTHOME_CITY", 14),
        # East side loops for now — progression gated by coord trigger
        warp(12, 5, "MAP_HEARTHOME_CITY", 14),
        warp(13, 5, "MAP_HEARTHOME_CITY", 14),
    ]
    data["coord_events"] = [
        trigger(10, 4, "HearthomeCity_Route209Gate_EventScript_CheckProgress"),
        trigger(11, 4, "HearthomeCity_Route209Gate_EventScript_CheckProgress"),
        trigger(12, 4, "HearthomeCity_Route209Gate_EventScript_CheckProgress"),
    ]
    scripts = r'''HearthomeCity_Route209Gate_MapScripts::
	.byte 0

HearthomeCity_Route209Gate_EventScript_Guard::
	msgbox HearthomeCity_Route209Gate_Text_Guard, MSGBOX_NPC
	end

HearthomeCity_Route209Gate_EventScript_CheckProgress::
	lockall
	goto_if_unset FLAG_BADGE03_GET, HearthomeCity_Route209Gate_EventScript_NeedBadge
	goto_if_unset FLAG_HIDE_HEARTHOME_BARRY, HearthomeCity_Route209Gate_EventScript_NeedBarry
	msgbox HearthomeCity_Route209Gate_Text_ComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route209Gate_Movement_Push
	waitmovement 0
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

HearthomeCity_Route209Gate_Text_ComingSoon:
	.string "Route 209 and Solaceon Town coming\n"
	.string "in the next milestone!$"
'''
    write_map("HearthomeCity_Route209Gate", data, scripts)


def scaffold_gym():
    data = indoor_base("MAP_HEARTHOME_CITY_GYM", "HearthomeCity_Gym", "LAYOUT_HEARTHOME_CITY_GYM",
                       "MUS_PL_GYM", show_name=True, battle="MAP_BATTLE_SCENE_GYM")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_BEAUTY", 9, 3, "HearthomeCity_Gym_EventScript_Fantina", local_id="LOCALID_HEARTHOME_GYM_FANTINA"),
        obj("OBJ_EVENT_GFX_LASS", 4, 10, "HearthomeCity_Gym_EventScript_Molly", trainer="TRAINER_TYPE_NORMAL", sight="3"),
        obj("OBJ_EVENT_GFX_YOUNGSTER", 15, 16, "HearthomeCity_Gym_EventScript_Karina", trainer="TRAINER_TYPE_NORMAL", sight="3"),
        obj("OBJ_EVENT_GFX_MAN_3", 4, 22, "HearthomeCity_Gym_EventScript_Bryce", trainer="TRAINER_TYPE_NORMAL", sight="3"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 3, 26, "HearthomeCity_Gym_EventScript_GymGuide"),
    ]
    data["warp_events"] = [
        warp(9, 29, "MAP_HEARTHOME_CITY", 3),
        warp(10, 29, "MAP_HEARTHOME_CITY", 3),
    ]
    data["bg_events"] = [
        sign(8, 28, "HearthomeCity_Gym_EventScript_Statue"),
        sign(11, 28, "HearthomeCity_Gym_EventScript_Statue"),
    ]
    scripts = r'''HearthomeCity_Gym_MapScripts::
	.byte 0

HearthomeCity_Gym_EventScript_Fantina::
	trainerbattle_single TRAINER_LEADER_FANTINA, HearthomeCity_Gym_Text_FantinaIntro, HearthomeCity_Gym_Text_FantinaDefeat, HearthomeCity_Gym_EventScript_FantinaDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_HEARTHOME_GYM_TM, HearthomeCity_Gym_EventScript_GiveTM
	msgbox HearthomeCity_Gym_Text_FantinaPost, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Gym_EventScript_FantinaDefeated::
	message HearthomeCity_Gym_Text_ReceivedRelicBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox HearthomeCity_Gym_Text_RelicBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE03_GET
	setvar VAR_HEARTHOME_CITY_STATE, 0
	clearflag FLAG_HIDE_HEARTHOME_FANTINA
	goto HearthomeCity_Gym_EventScript_GiveTM
	end

HearthomeCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_SHADOW_BALL
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_HEARTHOME_GYM_TM
	msgbox HearthomeCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Gym_EventScript_Molly::
	trainerbattle_single TRAINER_LASS_MOLLY_HEARTHOME, HearthomeCity_Gym_Text_MollyIntro, HearthomeCity_Gym_Text_MollyDefeat
	msgbox HearthomeCity_Gym_Text_MollyAfter, MSGBOX_AUTOCLOSE
	end

HearthomeCity_Gym_EventScript_Karina::
	trainerbattle_single TRAINER_SCHOOL_KID_KARINA_HEARTHOME, HearthomeCity_Gym_Text_KarinaIntro, HearthomeCity_Gym_Text_KarinaDefeat
	msgbox HearthomeCity_Gym_Text_KarinaAfter, MSGBOX_AUTOCLOSE
	end

HearthomeCity_Gym_EventScript_Bryce::
	trainerbattle_single TRAINER_ACE_TRAINER_BRYCE_HEARTHOME, HearthomeCity_Gym_Text_BryceIntro, HearthomeCity_Gym_Text_BryceDefeat
	msgbox HearthomeCity_Gym_Text_BryceAfter, MSGBOX_AUTOCLOSE
	end

HearthomeCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE03_GET, HearthomeCity_Gym_EventScript_GuideVictory
	msgbox HearthomeCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Gym_EventScript_GuideVictory::
	msgbox HearthomeCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE03_GET, HearthomeCity_Gym_EventScript_StatueWon
	msgbox HearthomeCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

HearthomeCity_Gym_EventScript_StatueWon::
	msgbox HearthomeCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

HearthomeCity_Gym_Text_GuideAdvice:
	.string "Yo! Champ-to-be!\p"
	.string "FANTINA uses Ghost-type POKéMON.\n"
	.string "Dark and Ghost moves hit hard here.\p"
	.string "Torchlit side rooms hide Trainers.\n"
	.string "Clear them, then face the Leader!$"

HearthomeCity_Gym_Text_GuideVictory:
	.string "That Relic Badge looks great on you!\n"
	.string "BARRY is pacing near the east gate.$"

HearthomeCity_Gym_Text_Statue:
	.string "HEARTHOME CITY POKéMON GYM\p"
	.string "LEADER: FANTINA$"

HearthomeCity_Gym_Text_StatueWon:
	.string "HEARTHOME CITY POKéMON GYM\p"
	.string "LEADER: FANTINA\p"
	.string "Certified Trainers:\n"
	.string "{PLAYER}$"

HearthomeCity_Gym_Text_MollyIntro:
	.string "Boo! Did I scare you?$"

HearthomeCity_Gym_Text_MollyDefeat:
	.string "My ghosts floated away...$"

HearthomeCity_Gym_Text_MollyAfter:
	.string "FANTINA's dance is even spookier.$"

HearthomeCity_Gym_Text_KarinaIntro:
	.string "I studied every Ghost type!\n"
	.string "Pop quiz--battle!$"

HearthomeCity_Gym_Text_KarinaDefeat:
	.string "I need more homework...$"

HearthomeCity_Gym_Text_KarinaAfter:
	.string "Dark-type moves ignore immunities.\n"
	.string "Keep that in mind!$"

HearthomeCity_Gym_Text_BryceIntro:
	.string "Only the calm reach FANTINA.\n"
	.string "Prove your nerve!$"

HearthomeCity_Gym_Text_BryceDefeat:
	.string "Chilling composure...$"

HearthomeCity_Gym_Text_BryceAfter:
	.string "The Leader awaits on the dais.$"

HearthomeCity_Gym_Text_FantinaIntro:
	.string "I am FANTINA, the Gym Leader!\p"
	.string "I adore Contests, but battling lets\n"
	.string "Ghost POKéMON truly shine!\p"
	.string "Can you keep your feet in this dark\n"
	.string "dance hall? Ooh la la--let us begin!$"

HearthomeCity_Gym_Text_FantinaDefeat:
	.string "Magnifique! You outshone my ghosts!$"

HearthomeCity_Gym_Text_ReceivedRelicBadge:
	.string "{PLAYER} received the RELIC BADGE\n"
	.string "from FANTINA!$"

HearthomeCity_Gym_Text_RelicBadgeInfo:
	.string "With the RELIC BADGE, your journey\n"
	.string "through Sinnoh presses onward.\p"
	.string "And take this--my favorite TM!$"

HearthomeCity_Gym_Text_ExplainTM:
	.string "That TM contains SHADOW BALL.\p"
	.string "It may also lower Sp. Def!\n"
	.string "A dramatic flourish for any team!$"

HearthomeCity_Gym_Text_FantinaPost:
	.string "FANTINA: Contests and Gym battles\n"
	.string "both reward passion!\p"
	.string "Visit the Contest Hall anytime--\n"
	.string "even if the stage is still warming up!$"
'''
    write_map("HearthomeCity_Gym", data, scripts)


def patch_route208_gate():
    gate = MAPS / "Route208_HearthomeGate"
    data = json.loads((gate / "map.json").read_text())
    # East warps -> Hearthome west entrance
    data["warp_events"][2] = warp(12, 5, "MAP_HEARTHOME_CITY", 12)
    data["warp_events"][3] = warp(13, 5, "MAP_HEARTHOME_CITY", 13)
    data["coord_events"] = []  # open the gate
    (gate / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    scripts = r'''Route208_HearthomeGate_MapScripts::
	.byte 0

Route208_HearthomeGate_EventScript_Guard::
	msgbox Route208_HearthomeGate_Text_Guard, MSGBOX_NPC
	end

Route208_HearthomeGate_Text_Guard:
	.string "Hearthome City is just ahead.\n"
	.string "Enjoy the Contests and the Gym!$"
'''
    (gate / "scripts.inc").write_text(scripts)
    print("patched Route208_HearthomeGate")


def patch_map_groups():
    path = REPO / "data" / "maps" / "map_groups.json"
    groups = json.loads(path.read_text())
    towns = groups["gMapGroup_TownsAndRoutes"]
    if "HearthomeCity" not in towns:
        # insert after Route208
        if "Route208" in towns:
            towns.insert(towns.index("Route208") + 1, "HearthomeCity")
        else:
            towns.append("HearthomeCity")
    indoor = [
        "HearthomeCity_PokemonCenter_1F",
        "HearthomeCity_PokemonCenter_2F",
        "HearthomeCity_Mart",
        "HearthomeCity_BebesHouse",
        "HearthomeCity_PokemonFanClub",
        "HearthomeCity_ForeignBuilding",
        "HearthomeCity_ContestLobby",
        "HearthomeCity_PoffinHouse",
        "HearthomeCity_Gym",
        "HearthomeCity_AmitySquareWestGate",
        "HearthomeCity_AmitySquareEastGate",
        "HearthomeCity_Route209Gate",
        "HearthomeCity_Route212Gate",
    ]
    groups["gMapGroup_IndoorHearthome"] = indoor
    if "gMapGroup_IndoorHearthome" not in groups["group_order"]:
        # after IndoorM16
        order = groups["group_order"]
        if "gMapGroup_IndoorM16" in order:
            order.insert(order.index("gMapGroup_IndoorM16") + 1, "gMapGroup_IndoorHearthome")
        else:
            order.append("gMapGroup_IndoorHearthome")
    path.write_text(json.dumps(groups, indent=2) + "\n")
    print("patched map_groups.json")


def patch_region_mapsecs():
    path = REPO / "src" / "data" / "region_map" / "region_map_sections.json"
    text = path.read_text()
    if '"MAPSEC_HEARTHOME_CITY"' not in text:
        text = text.replace(
            '''{
      "id": "MAPSEC_HEARTHOME_GATE",
      "name": "HEARTHOME GATE"
    }
  ]
}''',
            '''{
      "id": "MAPSEC_HEARTHOME_GATE",
      "name": "HEARTHOME GATE"
    },
    {
      "id": "MAPSEC_HEARTHOME_CITY",
      "name": "HEARTHOME CITY"
    },
    {
      "id": "MAPSEC_ROUTE_209_GATE",
      "name": "ROUTE 209 GATE"
    }
  ]
}'''
        )
        path.write_text(text)
        print("patched region_map_sections.json")
    else:
        print("region_map_sections already has Hearthome")


def patch_regions_h():
    path = REPO / "include" / "regions.h"
    text = path.read_text()
    text = text.replace(
        "sectionId <= MAPSEC_HEARTHOME_GATE;",
        "sectionId <= MAPSEC_ROUTE_209_GATE;",
    )
    path.write_text(text)
    print("patched regions.h")


def patch_map_name_popup():
    path = REPO / "src" / "map_name_popup.c"
    text = path.read_text()
    for theme_block in (
        ("[MAPSEC_HEARTHOME_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,",
         "[MAPSEC_HEARTHOME_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,\n"
         "    [MAPSEC_HEARTHOME_CITY - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,\n"
         "    [MAPSEC_ROUTE_209_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,"),
        ("[MAPSEC_HEARTHOME_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,",
         "[MAPSEC_HEARTHOME_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,\n"
         "    [MAPSEC_HEARTHOME_CITY - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,\n"
         "    [MAPSEC_ROUTE_209_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,"),
    ):
        if "MAPSEC_HEARTHOME_CITY - KANTO_MAPSEC_COUNT" not in text:
            text = text.replace(theme_block[0], theme_block[1], 1)
    path.write_text(text)
    print("patched map_name_popup.c")


def patch_heal_locations():
    path = REPO / "src" / "data" / "heal_locations.json"
    data = json.loads(path.read_text())
    locs = data["heal_locations"] if "heal_locations" in data else data
    if not any(L.get("id") == "HEAL_LOCATION_HEARTHOME_CITY" for L in locs):
        locs.append({
            "id": "HEAL_LOCATION_HEARTHOME_CITY",
            "map": "MAP_HEARTHOME_CITY",
            "x": 17,
            "y": 26,
            "respawn_map": "MAP_HEARTHOME_CITY_POKEMON_CENTER_1F",
            "respawn_npc": "LOCALID_HEARTHOME_NURSE",
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
    if "FLAG_GOT_BEBE_EEVEE" not in ft:
        ft = ft.replace(
            "#define FLAG_ITEM_MT_CORONET_PROTEIN  0x285 // Sinnoh M16\n",
            "#define FLAG_ITEM_MT_CORONET_PROTEIN  0x285 // Sinnoh M16\n"
            "#define FLAG_GOT_BEBE_EEVEE  0x286 // Sinnoh M17\n"
            "#define FLAG_RECEIVED_HEARTHOME_GYM_TM  0x287 // Sinnoh M17\n"
            "#define FLAG_HIDE_HEARTHOME_BARRY  0x288 // Sinnoh M17; set after rival battle\n"
            "#define FLAG_HIDE_HEARTHOME_FANTINA  0x289 // Sinnoh M17; cleared after badge (cameo)\n",
        )
        flags.write_text(ft)
        print("patched flags.h")

    vars_path = REPO / "include" / "constants" / "vars.h"
    vt = vars_path.read_text()
    if "VAR_HEARTHOME_CITY_STATE" not in vt:
        vt = vt.replace(
            "#define VAR_UNUSED_0x40F9                                0x40F9 // Unused Var\n",
            "#define VAR_HEARTHOME_CITY_STATE                         0x40F9 // Sinnoh M17: 0 Barry pending, 1 Barry done\n",
        )
        vars_path.write_text(vt)
        print("patched vars.h")

    # Fantina cameo starts hidden until badge
    ng = REPO / "data" / "scripts" / "new_game.inc"
    nt = ng.read_text()
    if "FLAG_HIDE_HEARTHOME_FANTINA" not in nt:
        nt = nt.replace(
            "\tsetflag FLAG_HIDE_ETERNA_BUILDING_RICKSHAW\n",
            "\tsetflag FLAG_HIDE_ETERNA_BUILDING_RICKSHAW\n"
            "\tsetflag FLAG_HIDE_HEARTHOME_FANTINA\n",
        )
        ng.write_text(nt)
        print("patched new_game.inc")


def patch_opponents():
    path = REPO / "include" / "constants" / "opponents.h"
    text = path.read_text()
    replacements = [
        ("#define TRAINER_NOB_4                       186\n",
         "#define TRAINER_LEADER_FANTINA                       186 // Sinnoh M17: was TRAINER_NOB_4\n"
         "#define TRAINER_NOB_4 TRAINER_LEADER_FANTINA\n"),
        ("#define TRAINER_NOB_5                       187\n",
         "#define TRAINER_LASS_MOLLY_HEARTHOME                       187 // Sinnoh M17: was TRAINER_NOB_5\n"
         "#define TRAINER_NOB_5 TRAINER_LASS_MOLLY_HEARTHOME\n"),
        ("#define TRAINER_ETHAN_2                     219\n",
         "#define TRAINER_SCHOOL_KID_KARINA_HEARTHOME                     219 // Sinnoh M17: was TRAINER_ETHAN_2\n"
         "#define TRAINER_ETHAN_2 TRAINER_SCHOOL_KID_KARINA_HEARTHOME\n"),
        ("#define TRAINER_ETHAN_3                     220\n",
         "#define TRAINER_ACE_TRAINER_BRYCE_HEARTHOME                     220 // Sinnoh M17: was TRAINER_ETHAN_3\n"
         "#define TRAINER_ETHAN_3 TRAINER_ACE_TRAINER_BRYCE_HEARTHOME\n"),
        ("#define TRAINER_ETHAN_4                     221\n",
         "#define TRAINER_BARRY_3_CHIMCHAR                     221 // Sinnoh M17: was TRAINER_ETHAN_4\n"
         "#define TRAINER_ETHAN_4 TRAINER_BARRY_3_CHIMCHAR\n"),
        ("#define TRAINER_ETHAN_5                     222\n",
         "#define TRAINER_BARRY_3_PIPLUP                     222 // Sinnoh M17: was TRAINER_ETHAN_5\n"
         "#define TRAINER_ETHAN_5 TRAINER_BARRY_3_PIPLUP\n"),
        ("#define TRAINER_JEFFREY_2                   228\n",
         "#define TRAINER_BARRY_3_TURTWIG                   228 // Sinnoh M17: was TRAINER_JEFFREY_2\n"
         "#define TRAINER_JEFFREY_2 TRAINER_BARRY_3_TURTWIG\n"),
    ]
    for old, new in replacements:
        if old in text and "TRAINER_LEADER_FANTINA" not in text or (old in text and "Sinnoh M17" not in text[text.find(old):text.find(old)+80]):
            if new.split()[1] not in text:
                text = text.replace(old, new, 1)
    # safer: only if Fantina missing
    if "TRAINER_LEADER_FANTINA" not in text:
        for old, new in replacements:
            text = text.replace(old, new, 1)
        path.write_text(text)
        print("patched opponents.h")
    else:
        print("opponents.h already has Fantina")


def patch_trainers_party():
    path = REPO / "src" / "data" / "trainers.party"
    text = path.read_text()

    parties = {
        "TRAINER_NOB_4": '''=== TRAINER_LEADER_FANTINA ===
Name: FANTINA
Class: Leader
Pic: Leaf
Gender: Female
Music: Female
Double Battle: No
AI: Basic Trainer

Duskull (M)
Level: 24
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Astonish
- Confuse Ray
- Pursuit
- Will-O-Wisp

Haunter (M)
Level: 24
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Shadow Punch
- Confuse Ray
- Curse
- Night Shade

Mismagius (F) @ Sitrus Berry
Level: 26
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Shadow Ball
- Confuse Ray
- Magical Leaf
- Psywave

''',
        "TRAINER_NOB_5": '''=== TRAINER_LASS_MOLLY_HEARTHOME ===
Name: MOLLY
Class: Lass
Pic: Lass
Gender: Female
Music: Female
Double Battle: No
AI: Basic Trainer

Gastly
Level: 21
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Lick
- Confuse Ray
- Night Shade
- Hypnosis

''',
        "TRAINER_ETHAN_2": '''=== TRAINER_SCHOOL_KID_KARINA_HEARTHOME ===
Name: KARINA
Class: School Kid
Pic: School Kid F
Gender: Female
Music: Female
Double Battle: No
AI: Basic Trainer

Duskull
Level: 22
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Astonish
- Disable
- Pursuit
- Confuse Ray

''',
        "TRAINER_ETHAN_3": '''=== TRAINER_ACE_TRAINER_BRYCE_HEARTHOME ===
Name: BRYCE
Class: Cooltrainer
Pic: Cooltrainer M
Gender: Male
Music: Male
Double Battle: No
AI: Basic Trainer

Haunter
Level: 23
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Night Shade
- Confuse Ray
- Curse
- Shadow Punch

''',
        "TRAINER_ETHAN_4": '''=== TRAINER_BARRY_3_CHIMCHAR ===
Name: BARRY
Class: Rival
Pic: Youngster
Gender: Male
Music: Male
Double Battle: No
AI: Basic Trainer

Staravia (M)
Level: 25
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Quick Attack
- Wing Attack
- Double Team
- Endeavor

Roselia (F)
Level: 23
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Mega Drain
- Stun Spore
- Magical Leaf
- Growth

Monferno (M)
Level: 27
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Mach Punch
- Flame Wheel
- Fury Swipes
- Torment

''',
        "TRAINER_ETHAN_5": '''=== TRAINER_BARRY_3_PIPLUP ===
Name: BARRY
Class: Rival
Pic: Youngster
Gender: Male
Music: Male
Double Battle: No
AI: Basic Trainer

Staravia (M)
Level: 25
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Quick Attack
- Wing Attack
- Double Team
- Endeavor

Buizel (M)
Level: 23
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Aqua Jet
- Pursuit
- Sonic Boom
- Quick Attack

Prinplup (M)
Level: 27
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Bubble Beam
- Metal Claw
- Peck
- Growl

''',
        "TRAINER_JEFFREY_2": '''=== TRAINER_BARRY_3_TURTWIG ===
Name: BARRY
Class: Rival
Pic: Youngster
Gender: Male
Music: Male
Double Battle: No
AI: Basic Trainer

Staravia (M)
Level: 25
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Quick Attack
- Wing Attack
- Double Team
- Endeavor

Ponyta (F)
Level: 23
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Ember
- Stomp
- Tail Whip
- Growl

Grotle (M)
Level: 27
IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe
- Razor Leaf
- Bite
- Mega Drain
- Withdraw

''',
    }

    def replace_party(src: str, old_name: str, new_block: str) -> str:
        pattern = rf"=== {old_name} ===.*?(?=\n=== |\Z)"
        m = re.search(pattern, src, flags=re.S)
        if not m:
            print("WARN: missing", old_name)
            return src
        return src[: m.start()] + new_block + src[m.end():]

    if "TRAINER_LEADER_FANTINA" not in text:
        for old, block in parties.items():
            text = replace_party(text, old, block)
        path.write_text(text)
        print("patched trainers.party")
    else:
        print("trainers.party already has Fantina")


def main():
    scaffold_city()
    scaffold_center()
    scaffold_mart()
    scaffold_bebe()
    scaffold_fan_club()
    scaffold_foreign()
    scaffold_contest()
    scaffold_poffin()
    scaffold_amity_gates()
    scaffold_route212_gate()
    scaffold_route209_gate()
    scaffold_gym()
    patch_route208_gate()
    patch_map_groups()
    patch_region_mapsecs()
    patch_regions_h()
    patch_map_name_popup()
    patch_heal_locations()
    patch_flags_vars()
    patch_opponents()
    patch_trainers_party()
    print("M17 scaffold complete.")


if __name__ == "__main__":
    main()
