#!/usr/bin/env python3
"""Scaffold M19 Veilstone City: maps, scripts, constants, trainers, Fly wiring.

Story flow
----------
1. Beat Maylene in the Gym -> Cobble Badge + TM Drain Punch.  The counterpart
   (Dawn/Lucas) is un-hidden (FLAG_HIDE_VEILSTONE_COUNTERPART) and Maylene gets a
   cameo outside the Gym (FLAG_HIDE_VEILSTONE_MAYLENE).  VAR_VEILSTONE_CITY_STATE stays 0.
2. Stepping out of the Gym (coord trigger, state 0, badge owned) -> the counterpart
   explains that Galactic grabbed the prototype Pokedex and runs for the warehouse.
   The object is relocated to the warehouse (setobjectxyperm) and state becomes 1.
3. At the warehouse (coord triggers, state 1) the counterpart teams up with the player
   for a two-trainer battle against the Galactic grunts.  Grunts are hidden, the
   counterpart leaves, state becomes 2.  While state is 0 the same tiles just turn
   the player back.
4. Inside the warehouse the player picks up HM02 Fly (also sets FLAG_RECEIVED_HM_FLY).

Fly wiring
----------
* field_move.c: Fly is unlocked by FLAG_BADGE04_GET (Cobble), Strength by FLAG_BADGE06_GET (Mine).
* region_map.c: sMapHealLocations + GetMapsecType gain entries for the nine Sinnoh towns
  that have a Pokemon Center heal location.  FLAG_VISITED_* flags (0x29B-0x2A4) are set from
  each town's OnTransition script.  The Sinnoh towns share the Hoenn region-map canvas, so
  they are parked on the (otherwise empty) top row, x=17..25, as placeholder fly spots.

All patches are idempotent: running the script twice leaves the tree unchanged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data" / "maps"

CITY = "VeilstoneCity"


# --------------------------------------------------------------------------- helpers
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
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (folder / "scripts.inc").write_text(scripts, encoding="utf-8")
    print("wrote", name)


def outdoor_base(map_id, name, layout, music="MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT", mapsec="MAPSEC_VEILSTONE_CITY", map_type="MAP_TYPE_CITY"):
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


def indoor_base(map_id, name, layout, music, mapsec="MAPSEC_VEILSTONE_CITY", night=None, show_name=False, battle="MAP_BATTLE_SCENE_NORMAL"):
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


def house_base(map_id, name, layout="LAYOUT_HOUSE1"):
    return indoor_base(map_id, name, layout, "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")


def house_warps(city_warp):
    return [warp(3, 7, "MAP_VEILSTONE_CITY", city_warp), warp(4, 7, "MAP_VEILSTONE_CITY", city_warp)]


class Scr:
    """Small builder for scripts.inc content.

    Script bodies are written with 4-space indentation and converted to tabs; the token
    %P% expands to the map prefix.  Text blocks take one string per .string line; the
    final line receives the '$' terminator.
    """

    def __init__(self, prefix: str):
        self.p = prefix
        self.chunks: list[str] = []

    def raw(self, s: str):
        s = s.strip("\n").replace("%P%", self.p)
        s = re.sub(r"(?m)^    ", "\t", s)
        self.chunks.append(s + "\n")

    def text(self, name: str, *lines: str):
        body = "".join(f'\t.string "{ln}"\n' for ln in lines[:-1]) + f'\t.string "{lines[-1]}$"\n'
        self.chunks.append(f"{self.p}_Text_{name}:\n{body}")

    def npc(self, name: str, *lines: str):
        self.chunks.append(f"{self.p}_EventScript_{name}::\n\tmsgbox {self.p}_Text_{name}, MSGBOX_NPC\n\tend\n")
        self.text(name, *lines)

    def sign(self, name: str, *lines: str):
        self.chunks.append(f"{self.p}_EventScript_{name}::\n\tmsgbox {self.p}_Text_{name}, MSGBOX_SIGN\n\tend\n")
        self.text(name, *lines)

    def trainer(self, name: str, trainer: str, intro, defeat, after):
        self.chunks.append(
            f"{self.p}_EventScript_{name}::\n"
            f"\ttrainerbattle_single {trainer}, {self.p}_Text_{name}Intro, {self.p}_Text_{name}Defeat\n"
            f"\tmsgbox {self.p}_Text_{name}After, MSGBOX_AUTOCLOSE\n\tend\n"
        )
        self.text(f"{name}Intro", *intro)
        self.text(f"{name}Defeat", *defeat)
        self.text(f"{name}After", *after)

    def render(self) -> str:
        return "\n".join(self.chunks)


def map_scripts(prefix: str, transition: str | None = None, extra: str = "") -> str:
    lines = [f"{prefix}_MapScripts::"]
    if transition:
        lines.append(f"\tmap_script MAP_SCRIPT_ON_TRANSITION, {transition}")
    if extra:
        lines.append(extra)
    lines.append("\t.byte 0")
    return "\n".join(lines)


# --------------------------------------------------------------------------- Veilstone City
WAREHOUSE_TRIGGER_TILES = [(x, 18) for x in range(25, 35)] + [(x, 16) for x in range(27, 32)]


def scaffold_city():
    p = CITY
    data = outdoor_base("MAP_VEILSTONE_CITY", p, "LAYOUT_VEILSTONE_CITY")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_VAR_1", 14, 36, f"{p}_EventScript_Counterpart", flag="FLAG_HIDE_VEILSTONE_COUNTERPART",
            local_id="LOCALID_VEILSTONE_COUNTERPART", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_MAGMA_MEMBER_M", 28, 17, f"{p}_EventScript_WarehouseGrunt", flag="FLAG_HIDE_VEILSTONE_WAREHOUSE_GRUNTS",
            local_id="LOCALID_VEILSTONE_GRUNT_1", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_MAGMA_MEMBER_M", 30, 17, f"{p}_EventScript_WarehouseGrunt", flag="FLAG_HIDE_VEILSTONE_WAREHOUSE_GRUNTS",
            local_id="LOCALID_VEILSTONE_GRUNT_2", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_LEAF", 10, 37, f"{p}_EventScript_MayleneCameo", flag="FLAG_HIDE_VEILSTONE_MAYLENE",
            movement="MOVEMENT_TYPE_FACE_UP"),
        obj("OBJ_EVENT_GFX_MAGMA_MEMBER_M", 42, 14, f"{p}_EventScript_HQGuard", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_MAGMA_MEMBER_M", 48, 14, f"{p}_EventScript_HQGuard", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 22, 34, f"{p}_EventScript_Woman", movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=2, range_y=1),
        obj("OBJ_EVENT_GFX_MAN_1", 36, 37, f"{p}_EventScript_Man", movement="MOVEMENT_TYPE_LOOK_AROUND"),
        obj("OBJ_EVENT_GFX_BOY_1", 30, 29, f"{p}_EventScript_Boy", movement="MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT", range_x=2),
        obj("OBJ_EVENT_GFX_OLD_MAN", 20, 28, f"{p}_EventScript_OldMan", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_SCIENTIST_1", 53, 40, f"{p}_EventScript_Researcher", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_LITTLE_GIRL", 39, 49, f"{p}_EventScript_LittleGirl", movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=2, range_y=1),
    ]
    data["warp_events"] = [
        warp(45, 35, "MAP_VEILSTONE_CITY_POKEMON_CENTER_1F", 0),  # 0
        warp(46, 35, "MAP_VEILSTONE_CITY_POKEMON_CENTER_1F", 1),  # 1
        warp(12, 35, "MAP_VEILSTONE_CITY_GYM", 0),  # 2
        warp(29, 27, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_1F", 0),  # 3
        warp(29, 15, "MAP_VEILSTONE_CITY_GALACTIC_WAREHOUSE", 0),  # 4
        warp(34, 47, "MAP_VEILSTONE_CITY_GAME_CORNER", 0),  # 5
        warp(44, 47, "MAP_VEILSTONE_CITY_PRIZE_EXCHANGE", 0),  # 6
        warp(18, 47, "MAP_VEILSTONE_CITY_MASSAGE_HOUSE", 0),  # 7
        warp(24, 47, "MAP_VEILSTONE_CITY_SOUTHEAST_HOUSE", 0),  # 8
        warp(39, 26, "MAP_VEILSTONE_CITY_NORTHWEST_HOUSE", 0),  # 9
        warp(45, 26, "MAP_VEILSTONE_CITY_NORTHEAST_HOUSE", 0),  # 10
        warp(6, 22, "MAP_ROUTE215_VEILSTONE_GATE", 2),  # 11
        warp(6, 23, "MAP_ROUTE215_VEILSTONE_GATE", 3),  # 12
        warp(46, 62, "MAP_VEILSTONE_CITY_ROUTE214_GATE", 0),  # 13
        warp(47, 62, "MAP_VEILSTONE_CITY_ROUTE214_GATE", 1),  # 14
    ]
    coords = [
        trigger(12, 36, f"{p}_EventScript_GymExitScene", "VAR_VEILSTONE_CITY_STATE", "0"),
        trigger(12, 37, f"{p}_EventScript_GymExitScene", "VAR_VEILSTONE_CITY_STATE", "0"),
    ]
    for x, y in WAREHOUSE_TRIGGER_TILES:
        coords.append(trigger(x, y, f"{p}_EventScript_WarehouseBlocked", "VAR_VEILSTONE_CITY_STATE", "0"))
    for x, y in WAREHOUSE_TRIGGER_TILES:
        coords.append(trigger(x, y, f"{p}_EventScript_WarehouseTeamUp", "VAR_VEILSTONE_CITY_STATE", "1"))
    data["coord_events"] = coords
    data["bg_events"] = [
        sign(11, 36, f"{p}_EventScript_GymSign"),
        sign(8, 23, f"{p}_EventScript_CitySign"),
        sign(31, 28, f"{p}_EventScript_DeptStoreSign"),
        sign(31, 16, f"{p}_EventScript_WarehouseSign"),
        sign(36, 48, f"{p}_EventScript_GameCornerSign"),
        sign(45, 15, f"{p}_EventScript_HQSign"),
        sign(54, 41, f"{p}_EventScript_CraterSign"),
    ]

    s = Scr(p)
    s.raw(map_scripts(p, f"{p}_OnTransition"))
    s.raw("""
%P%_OnTransition:
    setflag FLAG_VISITED_VEILSTONE_CITY
    call %P%_EventScript_SetCounterpartGfx
    end

%P%_EventScript_SetCounterpartGfx::
    checkplayergender
    goto_if_eq VAR_RESULT, MALE, %P%_EventScript_SetDawnGfx
    setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL
    return

%P%_EventScript_SetDawnGfx::
    setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_MAY_NORMAL
    return

%P%_EventScript_SetCounterpartName::
    checkplayergender
    goto_if_eq VAR_RESULT, MALE, %P%_EventScript_NameDawn
    bufferstring STR_VAR_1, %P%_Text_NameLucas
    return

%P%_EventScript_NameDawn::
    bufferstring STR_VAR_1, %P%_Text_NameDawn
    return
""")
    s.text("NameDawn", "DAWN")
    s.text("NameLucas", "LUCAS")

    s.raw("""
@ Fires when the player steps out of the Gym with the Cobble Badge (state 0).
%P%_EventScript_GymExitScene::
    goto_if_unset FLAG_BADGE04_GET, %P%_EventScript_NoScene
    goto_if_set FLAG_HIDE_VEILSTONE_COUNTERPART, %P%_EventScript_NoScene
    lockall
    call %P%_EventScript_SetCounterpartName
    playse SE_PIN
    applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_ExclamationMark
    waitmovement 0
    applymovement LOCALID_VEILSTONE_COUNTERPART, %P%_Movement_CounterpartToPlayer
    waitmovement 0
    applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_FacePlayer
    applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceRight
    waitmovement 0
    msgbox %P%_Text_CounterpartRush, MSGBOX_DEFAULT
    closemessage
    applymovement LOCALID_VEILSTONE_COUNTERPART, %P%_Movement_CounterpartRunOff
    waitmovement 0
    removeobject LOCALID_VEILSTONE_COUNTERPART
    setobjectxyperm LOCALID_VEILSTONE_COUNTERPART, 28, 18
    setobjectmovementtype LOCALID_VEILSTONE_COUNTERPART, MOVEMENT_TYPE_FACE_RIGHT
    addobject LOCALID_VEILSTONE_COUNTERPART
    setvar VAR_VEILSTONE_CITY_STATE, 1
    releaseall
    end

%P%_EventScript_NoScene::
    end

%P%_Movement_CounterpartToPlayer:
    walk_fast_left
    step_end

%P%_Movement_CounterpartRunOff:
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    step_end
""")
    s.text("CounterpartRush",
           r"{STR_VAR_1}: {PLAYER}! Over here!\p",
           r"I watched your match through the\n",
           r"Gym window. Unbelievable!\p",
           r"But there's no time to celebrate.\n",
           r"TEAM GALACTIC hauled crates into\l",
           r"the old warehouse up north.\p",
           r"One of them holds the prototype\n",
           r"POKéDEX Prof. Rowan sent here\l",
           r"for testing!\p",
           r"If they pry it open, it's gone.\p",
           r"I'll scout ahead. Meet me at the\n",
           r"warehouse, and bring your best!")

    s.raw("""
@ Counterpart waiting outside the warehouse (state 1) or idling by the Gym.
%P%_EventScript_Counterpart::
    lock
    faceplayer
    call %P%_EventScript_SetCounterpartName
    goto_if_eq VAR_VEILSTONE_CITY_STATE, 1, %P%_EventScript_CounterpartWaiting
    msgbox %P%_Text_CounterpartIdle, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_CounterpartWaiting::
    msgbox %P%_Text_CounterpartWaiting, MSGBOX_DEFAULT
    release
    end
""")
    s.text("CounterpartIdle",
           r"{STR_VAR_1}: Congratulations on the\n",
           r"COBBLE BADGE, {PLAYER}!")
    s.text("CounterpartWaiting",
           r"{STR_VAR_1}: Two grunts, one door.\p",
           r"Step up to the warehouse and we'll\n",
           r"take them on together!")

    s.raw("""
@ State 0: the warehouse is sealed off.
%P%_EventScript_WarehouseBlocked::
    lockall
    applymovement LOCALID_VEILSTONE_GRUNT_1, Common_Movement_FacePlayer
    applymovement LOCALID_VEILSTONE_GRUNT_2, Common_Movement_FacePlayer
    waitmovement 0
    msgbox %P%_Text_WarehouseBlocked, MSGBOX_DEFAULT
    closemessage
    applymovement OBJ_EVENT_ID_PLAYER, %P%_Movement_PushBack
    waitmovement 0
    releaseall
    end

%P%_Movement_PushBack:
    walk_down
    walk_down
    step_end

@ State 1: the counterpart joins the player against both grunts.
%P%_EventScript_WarehouseTeamUp::
    lockall
    special HasEnoughMonsForDoubleBattle
    goto_if_ne VAR_RESULT, PLAYER_HAS_TWO_USABLE_MONS, %P%_EventScript_NeedTwoMons
    call %P%_EventScript_SetCounterpartName
    playse SE_PIN
    applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_ExclamationMark
    waitmovement 0
    applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_FacePlayer
    waitmovement 0
    msgbox %P%_Text_TeamUp, MSGBOX_DEFAULT
    closemessage
    applymovement LOCALID_VEILSTONE_GRUNT_1, Common_Movement_FacePlayer
    applymovement LOCALID_VEILSTONE_GRUNT_2, Common_Movement_FacePlayer
    waitmovement 0
    msgbox %P%_Text_GruntsWarn, MSGBOX_DEFAULT
    closemessage
    trainerbattle_two_trainers TRAINER_GALACTIC_GRUNT_VEILSTONE_1, %P%_Text_Grunt1Defeat, TRAINER_GALACTIC_GRUNT_VEILSTONE_2, %P%_Text_Grunt2Defeat
    setflag FLAG_DEFEATED_VEILSTONE_WAREHOUSE_GRUNTS
    msgbox %P%_Text_GruntsRetreat, MSGBOX_DEFAULT
    closemessage
    applymovement LOCALID_VEILSTONE_GRUNT_1, %P%_Movement_GruntFleeWest
    applymovement LOCALID_VEILSTONE_GRUNT_2, %P%_Movement_GruntFleeEast
    waitmovement 0
    removeobject LOCALID_VEILSTONE_GRUNT_1
    removeobject LOCALID_VEILSTONE_GRUNT_2
    setflag FLAG_HIDE_VEILSTONE_WAREHOUSE_GRUNTS
    applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_FacePlayer
    waitmovement 0
    msgbox %P%_Text_CounterpartThanks, MSGBOX_DEFAULT
    closemessage
    applymovement LOCALID_VEILSTONE_COUNTERPART, %P%_Movement_CounterpartLeave
    waitmovement 0
    removeobject LOCALID_VEILSTONE_COUNTERPART
    setflag FLAG_HIDE_VEILSTONE_COUNTERPART
    setvar VAR_VEILSTONE_CITY_STATE, 2
    releaseall
    end

%P%_EventScript_NeedTwoMons::
    msgbox %P%_Text_NeedTwoMons, MSGBOX_DEFAULT
    closemessage
    applymovement OBJ_EVENT_ID_PLAYER, %P%_Movement_PushBack
    waitmovement 0
    releaseall
    end

%P%_Movement_GruntFleeWest:
    walk_fast_left
    walk_fast_left
    walk_fast_left
    walk_fast_left
    step_end

%P%_Movement_GruntFleeEast:
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    step_end

%P%_Movement_CounterpartLeave:
    walk_fast_down
    walk_fast_down
    walk_fast_down
    walk_fast_down
    walk_fast_down
    walk_fast_down
    step_end

%P%_EventScript_WarehouseGrunt::
    lock
    faceplayer
    msgbox %P%_Text_WarehouseGrunt, MSGBOX_DEFAULT
    release
    end
""")
    s.text("WarehouseBlocked",
           r"GRUNT: Hold it, kid!\p",
           r"This depot belongs to TEAM GALACTIC\n",
           r"now. Nobody gets through.\p",
           r"Go play somewhere else!")
    s.text("TeamUp",
           r"{STR_VAR_1}: There you are, {PLAYER}!\p",
           r"Two grunts on the door, and they\n",
           r"won't listen to reason.\p",
           r"So let's not ask nicely. We take\n",
           r"them together, side by side!")
    s.text("GruntsWarn",
           r"GRUNT: Two brats for the price of\n",
           r"one? Fine by us!\p",
           r"TEAM GALACTIC doesn't lose to\n",
           r"kids. Get ready!")
    s.text("Grunt1Defeat",
           r"Tch... The Commander will have my\n",
           r"head for this!")
    s.text("Grunt2Defeat",
           r"We were supposed to be the muscle...")
    s.text("GruntsRetreat",
           r"GRUNT: This depot isn't worth the\n",
           r"trouble! Fall back!")
    s.text("CounterpartThanks",
           r"{STR_VAR_1}: That's how it's done,\n",
           r"{PLAYER}! The door's clear.\p",
           r"The crate with the POKéDEX was\n",
           r"already carried out the back way.\p",
           r"There's a sealed door deeper inside\n",
           r"that needs a STORAGE KEY. I'll\l",
           r"track down where they went.\p",
           r"Have a look around in there--they\n",
           r"left a lot behind in a hurry!")
    s.text("NeedTwoMons",
           r"You need at least two POKéMON able\n",
           r"to battle to take on both grunts.")
    s.text("WarehouseGrunt",
           r"Move along. This warehouse is off\n",
           r"limits to civilians.")

    s.raw(f"""
%P%_EventScript_MayleneCameo::
    lock
    faceplayer
    goto_if_eq VAR_VEILSTONE_CITY_STATE, 2, %P%_EventScript_MayleneAfter
    msgbox %P%_Text_MayleneCameo, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_MayleneAfter::
    msgbox %P%_Text_MayleneAfter, MSGBOX_DEFAULT
    release
    end
""")
    s.text("MayleneCameo",
           r"MAYLENE: You fought with heart in\n",
           r"there. I like that!\p",
           r"I heard shouting up near the old\n",
           r"warehouse. Be careful, okay?")
    s.text("MayleneAfter",
           r"MAYLENE: You and your friend cleared\n",
           r"the warehouse? Nicely done!\p",
           r"With the COBBLE BADGE, POKéMON that\n",
           r"know FLY will carry you to any\l",
           r"town you've already visited.")

    s.npc("HQGuard",
          r"Move along.\n",
          r"TEAM GALACTIC's headquarters is\l",
          r"closed to the public.")
    s.npc("Woman",
          r"Veilstone is the city of stone.\n",
          r"Even the streets feel sturdy!\p",
          r"The quarry winds down to the sea\n",
          r"from here.")
    s.npc("Man",
          r"That crater to the east? A giant\n",
          r"meteorite crashed there long ago.\p",
          r"People say it's why the stone in\n",
          r"this city is so tough.")
    s.npc("Boy",
          r"The Department Store has five\n",
          r"floors and an elevator!\p",
          r"I ride it up and down all day.")
    s.npc("OldMan",
          r"That big building to the north is\n",
          r"TEAM GALACTIC's. I never see who\l",
          r"goes in or out.\p",
          r"Something is off about those folks.")
    s.npc("Researcher",
          r"I'm measuring the crater's depth.\p",
          r"Space rock or not, it's a fine\n",
          r"spot to study erosion.")
    s.npc("LittleGirl",
          r"The Game Corner is for grown-ups.\n",
          r"I just like the music from outside!")
    s.sign("GymSign",
           r"VEILSTONE CITY POKéMON GYM\n",
           r"LEADER: MAYLENE\l",
           r"The Iron-Willed Bruiser!")
    s.sign("CitySign",
           r"VEILSTONE CITY\n",
           r"A city carved from stone")
    s.sign("DeptStoreSign",
           r"VEILSTONE DEPARTMENT STORE\n",
           r"Five floors of everything a\l",
           r"Trainer needs!")
    s.sign("WarehouseSign",
           r"NO ENTRY\n",
           r"Property of TEAM GALACTIC")
    s.sign("GameCornerSign",
           r"VEILSTONE GAME CORNER\n",
           r"Fun and prizes for everyone!")
    s.sign("HQSign",
           r"TEAM GALACTIC VEILSTONE HQ\n",
           r"Visitors are not welcome.")
    s.sign("CraterSign",
           r"VEILSTONE METEORITE CRATER\n",
           r"A hollow left by a fallen star.\p",
           r"Please stay off the rim.")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Pokemon Center
def scaffold_center():
    p = "VeilstoneCity_PokemonCenter_1F"
    data = indoor_base("MAP_VEILSTONE_CITY_POKEMON_CENTER_1F", p, "LAYOUT_POKEMON_CENTER_1F",
                       "MUS_PL_POKE_CENTER", night="MUS_PL_POKE_CENTER_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_NURSE", 7, 2, f"{p}_EventScript_Nurse", local_id="LOCALID_VEILSTONE_NURSE"),
        obj("OBJ_EVENT_GFX_BLACK_BELT", 2, 3, f"{p}_EventScript_BlackBelt"),
        obj("OBJ_EVENT_GFX_GIRL_1", 11, 5, f"{p}_EventScript_Girl"),
    ]
    data["warp_events"] = [
        warp(7, 8, "MAP_VEILSTONE_CITY", 0, 3),
        warp(6, 8, "MAP_VEILSTONE_CITY", 1, 3),
        warp(1, 6, "MAP_VEILSTONE_CITY_POKEMON_CENTER_2F", 0, 4),
    ]
    s = Scr(p)
    s.raw(f"""
%P%_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, %P%_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

%P%_OnTransition:
    setrespawn HEAL_LOCATION_VEILSTONE_CITY
    end

%P%_EventScript_Nurse::
    setvar VAR_0x800B, LOCALID_VEILSTONE_NURSE
    call Common_EventScript_PkmnCenterNurse
    waitmessage
    waitbuttonpress
    release
    end
""")
    s.npc("BlackBelt",
          r"I train from dawn till dusk, then\n",
          r"nurse my bruises here.\p",
          r"The nurse never complains!")
    s.npc("Girl",
          r"Veilstone's Gym Leader is a lot\n",
          r"tougher than she looks!")
    write_map(p, data, s.render())

    p2 = "VeilstoneCity_PokemonCenter_2F"
    data2 = indoor_base("MAP_VEILSTONE_CITY_POKEMON_CENTER_2F", p2, "LAYOUT_POKEMON_CENTER_2F",
                        "MUS_PL_POKE_CENTER", night="MUS_PL_POKE_CENTER_NIGHT")
    data2["warp_events"] = [warp(1, 6, "MAP_VEILSTONE_CITY_POKEMON_CENTER_1F", 2, 4)]
    write_map(p2, data2, f"{p2}_MapScripts::\n\t.byte 0\n")


# --------------------------------------------------------------------------- Gym
def scaffold_gym():
    p = "VeilstoneCity_Gym"
    data = indoor_base("MAP_VEILSTONE_CITY_GYM", p, "LAYOUT_VEILSTONE_CITY_GYM", "MUS_PL_GYM",
                       mapsec="MAPSEC_VEILSTONE_GYM", show_name=True, battle="MAP_BATTLE_SCENE_GYM")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_LEAF", 12, 4, f"{p}_EventScript_Maylene", local_id="LOCALID_VEILSTONE_GYM_MAYLENE"),
        obj("OBJ_EVENT_GFX_BLACK_BELT", 7, 10, f"{p}_EventScript_Colby", trainer="TRAINER_TYPE_NORMAL", sight="4", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_BLACK_BELT", 16, 10, f"{p}_EventScript_Darren", trainer="TRAINER_TYPE_NORMAL", sight="4", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_BLACK_BELT", 7, 16, f"{p}_EventScript_Jeffery", trainer="TRAINER_TYPE_NORMAL", sight="4", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_BLACK_BELT", 16, 16, f"{p}_EventScript_Rafael", trainer="TRAINER_TYPE_NORMAL", sight="4", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_MAN_4", 8, 28, f"{p}_EventScript_GymGuide"),
    ]
    data["warp_events"] = [
        warp(11, 31, "MAP_VEILSTONE_CITY", 2),
        warp(12, 31, "MAP_VEILSTONE_CITY", 2),
    ]
    data["bg_events"] = [
        sign(10, 29, f"{p}_EventScript_Statue"),
        sign(13, 29, f"{p}_EventScript_Statue"),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_Maylene::
    trainerbattle_single TRAINER_LEADER_MAYLENE, %P%_Text_MayleneIntro, %P%_Text_MayleneDefeat, %P%_EventScript_MayleneDefeated, NO_MUSIC
    goto_if_unset FLAG_RECEIVED_VEILSTONE_GYM_TM, %P%_EventScript_GiveTM
    msgbox %P%_Text_MayleneAfter, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_MayleneDefeated::
    message %P%_Text_ReceivedCobbleBadge
    waitmessage
    call Common_EventScript_PlayGymBadgeFanfare
    msgbox %P%_Text_CobbleBadgeInfo, MSGBOX_DEFAULT
    setflag FLAG_BADGE04_GET
    setvar VAR_VEILSTONE_CITY_STATE, 0
    clearflag FLAG_HIDE_VEILSTONE_MAYLENE
    clearflag FLAG_HIDE_VEILSTONE_COUNTERPART
    goto %P%_EventScript_GiveTM
    end

%P%_EventScript_GiveTM::
    giveitem ITEM_TM_DRAIN_PUNCH
    goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
    setflag FLAG_RECEIVED_VEILSTONE_GYM_TM
    msgbox %P%_Text_ExplainTM, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_GymGuide::
    lock
    faceplayer
    goto_if_set FLAG_BADGE04_GET, %P%_EventScript_GuideVictory
    msgbox %P%_Text_GuideAdvice, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_GuideVictory::
    msgbox %P%_Text_GuideVictory, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_Statue::
    lockall
    goto_if_set FLAG_BADGE04_GET, %P%_EventScript_StatueWon
    msgbox %P%_Text_Statue, MSGBOX_DEFAULT
    releaseall
    end

%P%_EventScript_StatueWon::
    msgbox %P%_Text_StatueWon, MSGBOX_DEFAULT
    releaseall
    end
""")
    s.trainer("Colby", "TRAINER_BLACK_BELT_COLBY_VEILSTONE",
              [r"Hrrah! Warm-ups are over!\n", r"Show me how you take a punch!"],
              [r"Oof! Your guard held firm..."],
              [r"Strong legs, strong core.\n", r"That's the whole secret."])
    s.trainer("Darren", "TRAINER_BLACK_BELT_DARREN_VEILSTONE",
              [r"I've been waiting for a worthy\n", r"sparring partner!"],
              [r"Ha! That one rattled my teeth!"],
              [r"MAYLENE trains harder than all of\n", r"us put together."])
    s.trainer("Jeffery", "TRAINER_BLACK_BELT_JEFFERY_VEILSTONE",
              [r"Silence your mind. Focus your\n", r"fists. Now, fight!"],
              [r"My focus broke... well fought."],
              [r"Stay calm in a tight spot and the\n", r"win comes to you."])
    s.trainer("Rafael", "TRAINER_BLACK_BELT_RAFAEL_VEILSTONE",
              [r"Few trainers make it past my\n", r"corner of the Gym!"],
              [r"You hit like a boulder..."],
              [r"Go on. MAYLENE is waiting at the\n", r"far end of the hall."])
    s.text("GuideAdvice",
           r"Yo! Challenger in the making!\p",
           r"MAYLENE leads with Fighting-type\n",
           r"POKéMON. Flying and Psychic moves\l",
           r"hit them hard!\p",
           r"Black Belts guard the side rooms.\n",
           r"Meet their eyes and they'll rush\l",
           r"you, so choose your moment!")
    s.text("GuideVictory",
           r"That was a knockout, champ!\p",
           r"I hear TEAM GALACTIC has been\n",
           r"busy around the old warehouse.\p",
           r"Take care out there!")
    s.text("Statue",
           r"VEILSTONE CITY POKéMON GYM\n",
           r"LEADER: MAYLENE")
    s.text("StatueWon",
           r"VEILSTONE CITY POKéMON GYM\n",
           r"LEADER: MAYLENE\p",
           r"Certified Trainers:\n",
           r"{PLAYER}")
    s.text("MayleneIntro",
           r"MAYLENE: I'm MAYLENE, Veilstone's\n",
           r"Gym Leader!\p",
           r"I train with my POKéMON every day,\n",
           r"bruises and all.\p",
           r"Strength isn't only muscle. It's\n",
           r"trust and timing.\p",
           r"Show me how you fight! I won't\n",
           r"hold anything back!")
    s.text("MayleneDefeat",
           r"Oh...that was a clean finish.\n",
           r"You've earned this!")
    s.text("ReceivedCobbleBadge",
           r"{PLAYER} received the COBBLE BADGE\n",
           r"from MAYLENE!")
    s.text("CobbleBadgeInfo",
           r"The COBBLE BADGE lets POKéMON that\n",
           r"know FLY soar to towns you've\l",
           r"already visited.\p",
           r"Here, take this too. It's one of\n",
           r"my favorite moves!")
    s.text("ExplainTM",
           r"That TM contains DRAIN PUNCH.\p",
           r"It hurts the foe and restores part\n",
           r"of the damage to the user's HP.\p",
           r"Fight smart and stay on your feet!")
    s.text("MayleneAfter",
           r"MAYLENE: Keep that fighting spirit!\p",
           r"Something odd is going on around\n",
           r"the warehouse. Watch your back.")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Department Store
DEPT_FLOORS = {
    1: dict(
        layout="LAYOUT_LILYCOVE_CITY_DEPARTMENT_STORE_1F",
        warps=[
            warp(8, 7, "MAP_VEILSTONE_CITY", 3),
            warp(9, 7, "MAP_VEILSTONE_CITY", 3),
            warp(16, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_2F", 0),
            warp(2, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_ELEVATOR", 0),
        ],
        objects=[
            ("BEAUTY", 8, 2, "FACE_DOWN", "Greeter"),
            ("WOMAN_3", 10, 2, "FACE_DOWN", "ClerkBalls"),
            ("POKEFAN_F", 14, 5, "WANDER_AROUND", "PokefanF"),
            ("LITTLE_GIRL", 4, 4, "WANDER_AROUND", "LittleGirl"),
            ("POKEFAN_M", 3, 6, "LOOK_AROUND", "PokefanM"),
        ],
    ),
    2: dict(
        layout="LAYOUT_LILYCOVE_CITY_DEPARTMENT_STORE_2F",
        warps=[
            warp(16, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_1F", 2),
            warp(13, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_3F", 0),
            warp(2, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_ELEVATOR", 0),
        ],
        objects=[
            ("COOK", 8, 2, "FACE_DOWN", "Cook"),
            ("POKEFAN_F", 0, 5, "WANDER_AROUND", "PokefanF"),
            ("SAILOR", 13, 5, "WANDER_AROUND", "Sailor"),
            ("WOMAN_3", 10, 6, "FACE_UP", "ClerkPotions"),
            ("WOMAN_3", 7, 6, "FACE_UP", "ClerkStatus"),
        ],
    ),
    3: dict(
        layout="LAYOUT_LILYCOVE_CITY_DEPARTMENT_STORE_3F",
        warps=[
            warp(13, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_2F", 1),
            warp(16, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_4F", 0),
            warp(2, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_ELEVATOR", 0),
        ],
        objects=[
            ("RUNNING_TRIATHLETE_M", 0, 5, "WANDER_AROUND", "Triathlete"),
            ("POKEFAN_M", 7, 7, "WANDER_AROUND", "PokefanM"),
            ("WOMAN_5", 13, 5, "WANDER_AROUND", "Woman"),
            ("WOMAN_3", 8, 2, "FACE_DOWN", "ClerkFighting"),
            ("WOMAN_3", 10, 2, "FACE_DOWN", "ClerkUtility"),
        ],
    ),
    4: dict(
        layout="LAYOUT_LILYCOVE_CITY_DEPARTMENT_STORE_4F",
        warps=[
            warp(16, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_3F", 1),
            warp(13, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_5F", 0),
            warp(2, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_ELEVATOR", 0),
        ],
        objects=[
            ("GENTLEMAN", 0, 2, "WANDER_AROUND", "Gentleman"),
            ("WOMAN_2", 6, 2, "WANDER_AROUND", "Woman"),
            ("YOUNGSTER", 13, 4, "WANDER_AROUND", "Youngster"),
            ("WOMAN_3", 7, 6, "FACE_UP", "ClerkBattle"),
            ("WOMAN_3", 9, 6, "FACE_UP", "ClerkEscape"),
        ],
    ),
    5: dict(
        layout="LAYOUT_LILYCOVE_CITY_DEPARTMENT_STORE_5F",
        warps=[
            warp(13, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_4F", 1),
            warp(2, 1, "MAP_VEILSTONE_CITY_DEPARTMENT_STORE_ELEVATOR", 0),
        ],
        objects=[
            ("LITTLE_GIRL", 1, 6, "WANDER_AROUND", "LittleGirl"),
            ("POKEFAN_F", 7, 7, "FACE_DOWN_AND_LEFT", "PokefanF"),
            ("WOMAN_3", 7, 2, "FACE_DOWN", "ClerkVitamins"),
            ("WOMAN_3", 9, 2, "FACE_DOWN", "ClerkSupplies"),
            ("WOMAN_2", 9, 5, "FACE_RIGHT", "Woman"),
        ],
    ),
}

DEPT_MARTS = {
    "ClerkBalls": ["ITEM_POKE_BALL", "ITEM_GREAT_BALL", "ITEM_ULTRA_BALL", "ITEM_NET_BALL", "ITEM_NEST_BALL",
                   "ITEM_REPEAT_BALL", "ITEM_TIMER_BALL", "ITEM_LUXURY_BALL"],
    "ClerkStatus": ["ITEM_ANTIDOTE", "ITEM_PARALYZE_HEAL", "ITEM_AWAKENING", "ITEM_BURN_HEAL", "ITEM_ICE_HEAL", "ITEM_FULL_HEAL"],
    "ClerkPotions": ["ITEM_POTION", "ITEM_SUPER_POTION", "ITEM_HYPER_POTION", "ITEM_MAX_POTION", "ITEM_REVIVE", "ITEM_ETHER"],
    "ClerkFighting": ["ITEM_TM_BRICK_BREAK", "ITEM_TM_BULK_UP", "ITEM_TM_FOCUS_PUNCH"],
    "ClerkUtility": ["ITEM_TM_ROCK_TOMB", "ITEM_TM_DOUBLE_TEAM", "ITEM_TM_REST"],
    "ClerkBattle": ["ITEM_X_ATTACK", "ITEM_X_DEFENSE", "ITEM_X_SPEED", "ITEM_X_ACCURACY", "ITEM_DIRE_HIT", "ITEM_GUARD_SPEC"],
    "ClerkEscape": ["ITEM_REPEL", "ITEM_SUPER_REPEL", "ITEM_MAX_REPEL", "ITEM_ESCAPE_ROPE", "ITEM_FLUFFY_TAIL"],
    "ClerkVitamins": ["ITEM_HP_UP", "ITEM_PROTEIN", "ITEM_IRON", "ITEM_CALCIUM", "ITEM_ZINC", "ITEM_CARBOS"],
    "ClerkSupplies": ["ITEM_PP_UP", "ITEM_ELIXIR", "ITEM_MAX_REVIVE", "ITEM_FULL_HEAL"],
}

DEPT_TEXT = {
    (1, "Greeter"): [r"Welcome to the VEILSTONE\n", r"DEPARTMENT STORE!\p",
                     r"1F: POKé BALLS\n", r"2F: MEDICINE\l", r"3F: TECHNICAL MACHINES\l",
                     r"4F: BATTLE ITEMS\l", r"5F: VITAMINS AND EXTRAS\p",
                     r"The elevator is by the west stairs."],
    (1, "PokefanF"): [r"I always buy my POKé BALLS here.\n", r"The selection is wonderful!"],
    (1, "LittleGirl"): [r"I'm not allowed to ride the\n", r"elevator by myself yet!"],
    (1, "PokefanM"): [r"Five whole floors! You could get\n", r"lost in here for a day."],
    (2, "Cook"): [r"Stock up on medicine before the\n", r"next Gym. It's just smart."],
    (2, "PokefanF"): [r"A fine potion for a fine partner!"],
    (2, "Sailor"): [r"Long trips need plenty of\n", r"healing items. Trust me."],
    (3, "Triathlete"): [r"The TMs on this floor are a good\n", r"fit for any fighter."],
    (3, "PokefanM"): [r"Brick Break shatters walls,\n", r"and Bulk Up builds a champion."],
    (3, "Woman"): [r"A TM can be used over and over.\n", r"What a great invention!"],
    (4, "Gentleman"): [r"X items give a short boost in\n", r"battle. A clever trainer's trick."],
    (4, "Woman"): [r"Repels keep wild POKéMON away.\n", r"Perfect for a long walk!"],
    (4, "Youngster"): [r"I save my allowance for DIRE HITs!"],
    (5, "LittleGirl"): [r"Mommy says vitamins make POKéMON\n", r"grow big and strong."],
    (5, "PokefanF"): [r"The rooftop is closed for\n", r"repairs. What a shame!"],
    (5, "Woman"): [r"Vitamins are pricey, but your\n", r"POKéMON will thank you."],
}


def _dept_floor_name(n: int) -> str:
    return f"VeilstoneCity_DepartmentStore_{n}F"


def scaffold_department_store():
    for n, spec in DEPT_FLOORS.items():
        p = _dept_floor_name(n)
        data = indoor_base(f"MAP_VEILSTONE_CITY_DEPARTMENT_STORE_{n}F", p, spec["layout"], "MUS_PL_POKE_MART")
        data["object_events"] = [
            obj(f"OBJ_EVENT_GFX_{g}", x, y, f"{p}_EventScript_{sc}", movement=f"MOVEMENT_TYPE_{mv}",
                range_x=1 if mv.startswith("WANDER") else 0, range_y=1 if mv.startswith("WANDER") else 0)
            for g, x, y, mv, sc in spec["objects"]
        ]
        data["warp_events"] = spec["warps"]
        if n == 5:
            data["coord_events"] = [trigger(16, 1, f"{p}_EventScript_RooftopClosed")]

        s = Scr(p)
        s.raw(map_scripts(p, f"{p}_OnTransition"))
        s.raw(f"""
%P%_OnTransition:
    setvar VAR_DEPT_STORE_FLOOR, DEPT_STORE_FLOORNUM_{n}F
    setdynamicwarp MAP_VEILSTONE_CITY_DEPARTMENT_STORE_{n}F, 2, 1
    end
""")
        for g, x, y, mv, sc in spec["objects"]:
            if sc in DEPT_MARTS:
                items = "\n".join(f"    .2byte {it}" for it in DEPT_MARTS[sc])
                s.raw(f"""
%P%_EventScript_{sc}::
    lock
    faceplayer
    message gText_HowMayIServeYou
    waitmessage
    pokemart %P%_Pokemart_{sc}
    msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
    release
    end

    .align 2
%P%_Pokemart_{sc}:
{items}
    pokemartlistend
""")
            else:
                s.npc(sc, *DEPT_TEXT[(n, sc)])
        if n == 5:
            s.raw("""
%P%_EventScript_RooftopClosed::
    lockall
    msgbox %P%_Text_RooftopClosed, MSGBOX_DEFAULT
    closemessage
    applymovement OBJ_EVENT_ID_PLAYER, %P%_Movement_StepBack
    waitmovement 0
    releaseall
    end

%P%_Movement_StepBack:
    walk_down
    step_end
""")
            s.text("RooftopClosed",
                   r"The rooftop is closed for repairs.\n",
                   r"Please use the stairs or elevator.")
        write_map(p, data, s.render())

    scaffold_elevator()


def scaffold_elevator():
    p = "VeilstoneCity_DepartmentStore_Elevator"
    data = indoor_base("MAP_VEILSTONE_CITY_DEPARTMENT_STORE_ELEVATOR", p,
                       "LAYOUT_LILYCOVE_CITY_DEPARTMENT_STORE_ELEVATOR", "MUS_PL_POKE_MART")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_TEALA", 0, 5, f"{p}_EventScript_Attendant"),
    ]
    data["warp_events"] = [
        warp(1, 5, "MAP_DYNAMIC", "WARP_ID_DYNAMIC", 3),
        warp(2, 5, "MAP_DYNAMIC", "WARP_ID_DYNAMIC", 3),
    ]
    order = [5, 4, 3, 2, 1]  # MULTI_FLOORS list order (cursor index 0..4), index 5 = Exit
    s = Scr(p)
    s.raw(map_scripts(p))
    cases = "\n".join(f"    case DEPT_STORE_FLOORNUM_{n}F, %P%_EventScript_ChooseFrom{n}F" for n in order)
    s.raw(f"""
%P%_EventScript_Attendant::
    lock
    faceplayer
    message gText_WhichFloorWouldYouLike
    waitmessage
    switch VAR_DEPT_STORE_FLOOR
{cases}
    goto %P%_EventScript_ChooseFrom1F
    end
""")
    for idx, n in enumerate(order):
        s.raw(f"""
%P%_EventScript_ChooseFrom{n}F::
    multichoicedefault 0, 0, MULTI_FLOORS, {idx}, FALSE
    goto %P%_EventScript_ChooseFloor
    end
""")
    choose = "\n".join(f"    case {idx}, %P%_EventScript_Go{n}F" for idx, n in enumerate(order))
    s.raw(f"""
%P%_EventScript_ChooseFloor::
    switch VAR_RESULT
{choose}
    case 5, %P%_EventScript_ExitFloorSelect
    case MULTI_B_PRESSED, %P%_EventScript_ExitFloorSelect
    end
""")
    for n in order:
        s.raw(f"""
%P%_EventScript_Go{n}F::
    setvar VAR_0x8006, DEPT_STORE_FLOORNUM_{n}F
    setdynamicwarp MAP_VEILSTONE_CITY_DEPARTMENT_STORE_{n}F, 2, 1
    goto_if_eq VAR_DEPT_STORE_FLOOR, DEPT_STORE_FLOORNUM_{n}F, %P%_EventScript_ExitFloorSelect
    call %P%_EventScript_MoveElevator
    setvar VAR_DEPT_STORE_FLOOR, DEPT_STORE_FLOORNUM_{n}F
    goto %P%_EventScript_ExitFloorSelect
    end
""")
    s.raw("""
%P%_EventScript_ExitFloorSelect::
    release
    end

%P%_EventScript_MoveElevator::
    closemessage
    applymovement VAR_LAST_TALKED, Common_Movement_WalkInPlaceFasterDown
    waitmovement 0
    waitse
    copyvar VAR_0x8005, VAR_DEPT_STORE_FLOOR
    special MoveElevator
    return
""")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Massage House
def scaffold_massage_house():
    p = "VeilstoneCity_MassageHouse"
    data = house_base("MAP_VEILSTONE_CITY_MASSAGE_HOUSE", p)
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_WOMAN_3", 4, 4, f"{p}_EventScript_Masseuse", movement="MOVEMENT_TYPE_FACE_DOWN",
            local_id="LOCALID_VEILSTONE_MASSEUSE"),
        obj("OBJ_EVENT_GFX_LITTLE_BOY", 7, 5, f"{p}_EventScript_Boy"),
    ]
    data["warp_events"] = house_warps(7)
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_Masseuse::
    lock
    faceplayer
    goto_if_lt VAR_MASSAGE_COOLDOWN_STEP_COUNTER, 500, %P%_EventScript_RateMonFriendship
    msgbox %P%_Text_OfferMassage, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, %P%_EventScript_DeclineMassage
    msgbox %P%_Text_WhichMon
    special ChoosePartyMon
    lock
    faceplayer
    goto_if_ge VAR_0x8004, PARTY_SIZE, %P%_EventScript_DeclineMassage
    specialvar VAR_RESULT, ScriptGetPartyMonSpecies
    goto_if_eq VAR_RESULT, SPECIES_EGG, %P%_EventScript_CantMassageEgg
    msgbox %P%_Text_SettleIn
    closemessage
    fadescreen FADE_TO_BLACK
    playfanfare MUS_HEAL
    waitfanfare
    special DaisyMassageServices
    fadescreen FADE_FROM_BLACK
    special BufferMonNickname
    msgbox %P%_Text_AllDone
    release
    end

%P%_EventScript_CantMassageEgg::
    msgbox %P%_Text_CantMassageEgg
    release
    end

%P%_EventScript_DeclineMassage::
    msgbox %P%_Text_DeclineMassage
    release
    end

%P%_EventScript_RateMonFriendship::
    msgbox %P%_Text_LetMeSeeFirstMon
    specialvar VAR_RESULT, GetLeadMonFriendship
    switch VAR_RESULT
    case 0, %P%_EventScript_Friendship0
    case 1, %P%_EventScript_Friendship1
    case 2, %P%_EventScript_Friendship2
    case 3, %P%_EventScript_Friendship3
    case 4, %P%_EventScript_Friendship4
    case 5, %P%_EventScript_Friendship5
    case 6, %P%_EventScript_Friendship6
    end

%P%_EventScript_Friendship0::
    msgbox %P%_Text_Friendship0
    release
    end

%P%_EventScript_Friendship1::
    msgbox %P%_Text_Friendship1
    release
    end

%P%_EventScript_Friendship2::
    msgbox %P%_Text_Friendship2
    release
    end

%P%_EventScript_Friendship3::
    msgbox %P%_Text_Friendship3
    release
    end

%P%_EventScript_Friendship4::
    msgbox %P%_Text_Friendship4
    release
    end

%P%_EventScript_Friendship5::
    msgbox %P%_Text_Friendship5
    release
    end

%P%_EventScript_Friendship6::
    msgbox %P%_Text_Friendship6
    release
    end
""")
    s.npc("Boy",
          r"Mom's hands are magic. My\n",
          r"POKéMON falls asleep every time!")
    s.text("OfferMassage",
           r"Welcome to my little parlor.\p",
           r"A good massage melts away stress\n",
           r"and brings POKéMON closer to\l",
           r"their Trainers.\p",
           r"Would you like me to knead out the\n",
           r"knots in one of yours?")
    s.text("WhichMon", r"Which POKéMON needs a rubdown?")
    s.text("SettleIn",
           r"Wonderful! Let your POKéMON settle\n",
           r"in. This won't take long.")
    s.text("AllDone",
           r"There! {STR_VAR_1} looks relaxed and\n",
           r"very happy.\p",
           r"Come back after you've walked a\n",
           r"good while together.")
    s.text("CantMassageEgg",
           r"Oh, that's an Egg! I can't massage\n",
           r"something so delicate.")
    s.text("DeclineMassage",
           r"No rubdown today? Perfectly fine.\n",
           r"Drop by whenever you like.")
    s.text("LetMeSeeFirstMon",
           r"Your POKéMON should rest a while\n",
           r"before another massage.\p",
           r"In the meantime, may I see the\n",
           r"first POKéMON in your party?")
    s.text("Friendship0",
           r"Oh dear. It hardly trusts you at\n",
           r"all.\p",
           r"Be gentle with it, and be patient.")
    s.text("Friendship1",
           r"It stays guarded around you.\n",
           r"Spend more time together.")
    s.text("Friendship2",
           r"It doesn't know you well yet.\n",
           r"Walk with it, battle with it.")
    s.text("Friendship3",
           r"I can tell it's warming up to you.\n",
           r"Keep it up!")
    s.text("Friendship4",
           r"It's quite fond of you. Look how\n",
           r"it leans toward you!")
    s.text("Friendship5",
           r"What a happy face! It adores you.")
    s.text("Friendship6",
           r"It couldn't love you more!\n",
           r"You two are inseparable.")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Plain houses
def scaffold_houses():
    # Southeast house
    p = "VeilstoneCity_SoutheastHouse"
    data = house_base("MAP_VEILSTONE_CITY_SOUTHEAST_HOUSE", p)
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_OLD_MAN", 4, 4, f"{p}_EventScript_OldMan"),
        obj("OBJ_EVENT_GFX_LITTLE_BOY", 7, 5, f"{p}_EventScript_Boy", movement="MOVEMENT_TYPE_LOOK_AROUND"),
    ]
    data["warp_events"] = house_warps(8)
    s = Scr(p)
    s.raw(map_scripts(p))
    s.npc("OldMan",
          r"I carved stone in this city for\n",
          r"fifty years.\p",
          r"Veilstone rock is hard, but it\n",
          r"yields to patience.")
    s.npc("Boy",
          r"Grandpa lets me hammer the\n",
          r"small stones. It's so loud!")
    write_map(p, data, s.render())

    # Northwest house
    p = "VeilstoneCity_NorthwestHouse"
    data = house_base("MAP_VEILSTONE_CITY_NORTHWEST_HOUSE", p)
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_WOMAN_2", 4, 4, f"{p}_EventScript_Woman"),
        obj("OBJ_EVENT_GFX_BUG_CATCHER", 7, 5, f"{p}_EventScript_Collector", movement="MOVEMENT_TYPE_FACE_LEFT"),
    ]
    data["warp_events"] = house_warps(9)
    s = Scr(p)
    s.raw(map_scripts(p))
    s.npc("Woman",
          r"Have you seen TEAM GALACTIC's\n",
          r"building? It's huge and silent.\p",
          r"I keep the curtains drawn now.")
    s.npc("Collector",
          r"I collect pebbles from every\n",
          r"route I visit.\p",
          r"Veilstone pebbles are the heaviest\n",
          r"in my collection.")
    write_map(p, data, s.render())

    # Northeast house: Porygon gift
    p = "VeilstoneCity_NortheastHouse"
    data = house_base("MAP_VEILSTONE_CITY_NORTHEAST_HOUSE", p)
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_SCIENTIST_1", 4, 4, f"{p}_EventScript_Programmer", local_id="LOCALID_VEILSTONE_PROGRAMMER"),
        obj("OBJ_EVENT_GFX_LITTLE_GIRL", 7, 5, f"{p}_EventScript_Girl", movement="MOVEMENT_TYPE_LOOK_AROUND"),
    ]
    data["warp_events"] = house_warps(10)
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_Programmer::
    lock
    faceplayer
    goto_if_set FLAG_GOT_VEILSTONE_PORYGON, %P%_EventScript_ProgrammerAfter
    msgbox %P%_Text_ProgrammerIntro, MSGBOX_DEFAULT
    setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_PORYGON
    givemon SPECIES_PORYGON, 25
    goto_if_eq VAR_RESULT, 0, %P%_EventScript_GetPorygonParty
    goto_if_eq VAR_RESULT, 1, %P%_EventScript_GetPorygonPC
    goto_if_eq VAR_RESULT, 2, Common_EventScript_NoMoreRoomForPokemon
    release
    end

%P%_EventScript_GetPorygonParty::
    playfanfare MUS_OBTAIN_ITEM
    message %P%_Text_ReceivedPorygon
    waitmessage
    waitfanfare
    bufferspeciesname STR_VAR_1, SPECIES_PORYGON
    msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, %P%_EventScript_SetGotPorygon
    call Common_EventScript_GetGiftMonPartySlot
    call Common_EventScript_NameReceivedPartyMon
    goto %P%_EventScript_SetGotPorygon
    end

%P%_EventScript_GetPorygonPC::
    playfanfare MUS_OBTAIN_ITEM
    message %P%_Text_ReceivedPorygon
    waitmessage
    waitfanfare
    bufferspeciesname STR_VAR_1, SPECIES_PORYGON
    msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, %P%_EventScript_TransferPorygon
    call Common_EventScript_NameReceivedBoxMon
    goto %P%_EventScript_TransferPorygon
    end

%P%_EventScript_TransferPorygon::
    call Common_EventScript_TransferredToPC
    goto %P%_EventScript_SetGotPorygon
    end

%P%_EventScript_SetGotPorygon::
    setflag FLAG_GOT_VEILSTONE_PORYGON
    msgbox %P%_Text_ProgrammerExplain, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_ProgrammerAfter::
    msgbox %P%_Text_ProgrammerAfter, MSGBOX_DEFAULT
    release
    end
""")
    s.npc("Girl",
          r"Daddy built a POKéMON out of\n",
          r"numbers! Isn't that silly?")
    s.text("ProgrammerIntro",
           r"Ah, a visitor! Perfect timing.\p",
           r"I write programs for a living, and\n",
           r"my latest project grew a little\l",
           r"too clever for my apartment.\p",
           r"Would you take it off my hands?\n",
           r"It's a digital POKéMON called\l",
           r"PORYGON. Please treat it kindly!")
    s.text("ReceivedPorygon", r"{PLAYER} received PORYGON!")
    s.text("ProgrammerExplain",
           r"PORYGON can copy itself into\n",
           r"just about any data.\p",
           r"It's a little odd, but it's loyal.\n",
           r"Look after it for me!")
    s.text("ProgrammerAfter",
           r"How's PORYGON doing? I hope it\n",
           r"isn't getting lonely in there.")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Game Corner / Prize Exchange
GAME_CORNER_MACHINES = [
    (2, 6), (2, 8), (2, 9), (3, 7), (3, 8), (3, 9), (7, 6), (7, 7), (7, 9), (8, 6), (8, 7), (8, 9),
    (14, 6), (15, 6), (14, 7), (15, 7), (14, 8), (15, 8), (18, 6), (19, 6), (18, 7), (19, 7), (18, 8), (19, 8),
]


def scaffold_game_corner():
    p = "VeilstoneCity_GameCorner"
    data = indoor_base("MAP_VEILSTONE_CITY_GAME_CORNER", p, "LAYOUT_MAUVILLE_CITY_GAME_CORNER",
                       "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_BEAUTY", 12, 2, f"{p}_EventScript_Receptionist"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 12, 7, f"{p}_EventScript_Woman", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_GENTLEMAN", 16, 5, f"{p}_EventScript_Gentleman", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_GIRL_2", 7, 3, f"{p}_EventScript_Girl", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_OLD_MAN", 20, 8, f"{p}_EventScript_OldMan", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_MANIAC", 9, 8, f"{p}_EventScript_Maniac", movement="MOVEMENT_TYPE_FACE_UP"),
        obj("OBJ_EVENT_GFX_MAN_3", 1, 7, f"{p}_EventScript_Man", movement="MOVEMENT_TYPE_FACE_RIGHT"),
    ]
    data["warp_events"] = [
        warp(11, 10, "MAP_VEILSTONE_CITY", 5),
        warp(12, 10, "MAP_VEILSTONE_CITY", 5),
    ]
    data["bg_events"] = [sign(x, y, f"{p}_EventScript_OutOfOrder") for x, y in GAME_CORNER_MACHINES]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.npc("Receptionist",
          r"Welcome to the VEILSTONE GAME\n",
          r"CORNER!\p",
          r"The machines are being serviced,\n",
          r"so we can't offer any games yet.\p",
          r"Feel free to look around!")
    s.npc("Woman",
          r"I used to play here every\n",
          r"evening. Now I just keep the\l",
          r"seat warm.")
    s.npc("Gentleman",
          r"These machines were rattling long\n",
          r"before the crews arrived. I\l",
          r"wonder what's wrong with them.")
    s.npc("Girl",
          r"I'm saving up Coins for the\n",
          r"Prize Exchange next door!")
    s.npc("OldMan",
          r"In my day we flipped a coin\n",
          r"and called it fate.")
    s.npc("Maniac",
          r"They say TEAM GALACTIC stored\n",
          r"crates in the warehouse near the\l",
          r"plaza. Strange place for a prize!")
    s.npc("Man",
          r"No games today, and I still came.\n",
          r"The jingle music is too good.")
    s.sign("OutOfOrder",
           r"This machine is switched off for\n",
           r"servicing.")
    write_map(p, data, s.render())


def scaffold_prize_exchange():
    p = "VeilstoneCity_PrizeExchange"
    data = house_base("MAP_VEILSTONE_CITY_PRIZE_EXCHANGE", p)
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 4, 4, f"{p}_EventScript_Clerk"),
        obj("OBJ_EVENT_GFX_WOMAN_5", 7, 5, f"{p}_EventScript_Woman", movement="MOVEMENT_TYPE_FACE_LEFT"),
    ]
    data["warp_events"] = house_warps(6)
    s = Scr(p)
    s.raw(map_scripts(p))
    s.npc("Clerk",
          r"Welcome to the PRIZE EXCHANGE!\p",
          r"We're waiting on a fresh shipment\n",
          r"of prizes, so the counter is\l",
          r"closed for the time being.\p",
          r"Please check back later!")
    s.npc("Woman",
          r"I'm just here to admire the\n",
          r"prize shelves. Pretty, aren't they?")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Galactic Warehouse
def scaffold_warehouse():
    p = "VeilstoneCity_GalacticWarehouse"
    data = indoor_base("MAP_VEILSTONE_CITY_GALACTIC_WAREHOUSE", p, "LAYOUT_VEILSTONE_CITY_GALACTIC_WAREHOUSE",
                       "MUS_PL_ENCOUNTER_GALACTIC", mapsec="MAPSEC_GALACTIC_WAREHOUSE", show_name=True)
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_ITEM_BALL", 4, 7, f"{p}_EventScript_ItemHMFly", flag="FLAG_GOT_HM_FLY_VEILSTONE"),
        obj("OBJ_EVENT_GFX_SCIENTIST_1", 11, 6, f"{p}_EventScript_Scientist", movement="MOVEMENT_TYPE_FACE_LEFT"),
    ]
    data["warp_events"] = [
        warp(7, 13, "MAP_VEILSTONE_CITY", 4),
        warp(8, 13, "MAP_VEILSTONE_CITY", 4),
    ]
    data["coord_events"] = [
        trigger(7, 3, f"{p}_EventScript_LockedDoor"),
        trigger(8, 3, f"{p}_EventScript_LockedDoor"),
    ]
    data["bg_events"] = [
        sign(3, 4, f"{p}_EventScript_Crates"),
        sign(12, 4, f"{p}_EventScript_Crates"),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_ItemHMFly::
    lock
    giveitem ITEM_HM_FLY
    goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
    removeobject VAR_LAST_TALKED
    setflag FLAG_GOT_HM_FLY_VEILSTONE
    setflag FLAG_RECEIVED_HM_FLY
    msgbox %P%_Text_ExplainFly, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_LockedDoor::
    lockall
    msgbox %P%_Text_LockedDoor, MSGBOX_DEFAULT
    closemessage
    applymovement OBJ_EVENT_ID_PLAYER, %P%_Movement_StepBack
    waitmovement 0
    releaseall
    end

%P%_Movement_StepBack:
    walk_down
    step_end

%P%_EventScript_Scientist::
    lock
    faceplayer
    msgbox %P%_Text_Scientist, MSGBOX_DEFAULT
    release
    end
""")
    s.text("ExplainFly",
           r"HM02 contains FLY!\p",
           r"A POKéMON that learns it can carry\n",
           r"you to any town you've visited.\p",
           r"You'll need the COBBLE BADGE to use\n",
           r"it outside of battle.")
    s.text("LockedDoor",
           r"The door is locked tight.\p",
           r"A card reader beside it reads:\n",
           r"“STORAGE KEY REQUIRED.”")
    s.text("Scientist",
           r"Eek! Please don't hurt me!\p",
           r"I just catalog crates for TEAM\n",
           r"GALACTIC. The rest of the crew\l",
           r"left in a rush.\p",
           r"The real storage is behind that\n",
           r"locked door. Only the Commander\l",
           r"carries the STORAGE KEY.")
    s.sign("Crates",
           r"Stacked crates marked with the\n",
           r"TEAM GALACTIC logo. All empty.")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Route 214 gate
def scaffold_route214_gate():
    p = "VeilstoneCity_Route214Gate"
    data = indoor_base("MAP_VEILSTONE_CITY_ROUTE214_GATE", p, "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE",
                       "MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT")
    data["allow_cycling"] = True
    data["allow_running"] = True
    data["object_events"] = [obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 7, 2, f"{p}_EventScript_Guard")]
    data["warp_events"] = [
        warp(1, 5, "MAP_VEILSTONE_CITY", 13),
        warp(2, 5, "MAP_VEILSTONE_CITY", 14),
        warp(12, 5, "MAP_VEILSTONE_CITY", 13),
        warp(13, 5, "MAP_VEILSTONE_CITY", 14),
    ]
    data["coord_events"] = [
        trigger(10, 4, f"{p}_EventScript_ComingSoon"),
        trigger(11, 4, f"{p}_EventScript_ComingSoon"),
        trigger(12, 4, f"{p}_EventScript_ComingSoon"),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_Guard::
    msgbox %P%_Text_Guard, MSGBOX_NPC
    end

%P%_EventScript_ComingSoon::
    lockall
    msgbox %P%_Text_ComingSoon, MSGBOX_DEFAULT
    closemessage
    applymovement OBJ_EVENT_ID_PLAYER, %P%_Movement_Push
    waitmovement 0
    releaseall
    end

%P%_Movement_Push:
    walk_left
    step_end
""")
    s.text("Guard",
           r"Route 214 runs south along the\n",
           r"marsh toward Pastoria City.\p",
           r"The road isn't ready for travelers\n",
           r"just yet.")
    s.text("ComingSoon",
           r"Route 214 and Pastoria City coming\n",
           r"in the next milestone!")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Patches: Route 215 gate
def patch_route215_gate():
    gate = MAPS / "Route215_VeilstoneGate"
    path = gate / "map.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["warp_events"][2] = warp(12, 5, "MAP_VEILSTONE_CITY", 11)
    data["warp_events"][3] = warp(13, 5, "MAP_VEILSTONE_CITY", 12)
    data["coord_events"] = []
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    s = Scr("Route215_VeilstoneGate")
    s.raw(map_scripts("Route215_VeilstoneGate"))
    s.raw("""
%P%_EventScript_Guard::
    msgbox %P%_Text_Guard, MSGBOX_NPC
    end
""")
    s.text("Guard",
           r"Veilstone City is just beyond\n",
           r"this gate. It's open now!\p",
           r"Mind the TEAM GALACTIC folks near\n",
           r"the warehouse, though.")
    (gate / "scripts.inc").write_text(s.render(), encoding="utf-8")
    print("patched Route215_VeilstoneGate")


# --------------------------------------------------------------------------- Patches: map groups
M19_INDOOR = [
    "VeilstoneCity_PokemonCenter_1F",
    "VeilstoneCity_PokemonCenter_2F",
    "VeilstoneCity_Gym",
    "VeilstoneCity_DepartmentStore_1F",
    "VeilstoneCity_DepartmentStore_2F",
    "VeilstoneCity_DepartmentStore_3F",
    "VeilstoneCity_DepartmentStore_4F",
    "VeilstoneCity_DepartmentStore_5F",
    "VeilstoneCity_DepartmentStore_Elevator",
    "VeilstoneCity_MassageHouse",
    "VeilstoneCity_SoutheastHouse",
    "VeilstoneCity_NorthwestHouse",
    "VeilstoneCity_NortheastHouse",
    "VeilstoneCity_GameCorner",
    "VeilstoneCity_PrizeExchange",
    "VeilstoneCity_GalacticWarehouse",
    "VeilstoneCity_Route214Gate",
]


def patch_map_groups():
    path = MAPS / "map_groups.json"
    groups = json.loads(path.read_text(encoding="utf-8"))
    towns = groups["gMapGroup_TownsAndRoutes"]
    if CITY not in towns:
        towns.insert(towns.index("Route215") + 1 if "Route215" in towns else len(towns), CITY)
    groups["gMapGroup_IndoorVeilstone"] = M19_INDOOR
    order = groups["group_order"]
    if "gMapGroup_IndoorVeilstone" not in order:
        anchor = "gMapGroup_IndoorM18"
        order.insert(order.index(anchor) + 1 if anchor in order else len(order), "gMapGroup_IndoorVeilstone")
    path.write_text(json.dumps(groups, indent=2) + "\n", encoding="utf-8")
    print("patched map_groups.json")


# --------------------------------------------------------------------------- Patches: region map sections
FLY_TOWNS = [
    # mapsec, map, heal location, visited flag, placeholder x (row y=0 of the region map)
    ("MAPSEC_TWINLEAF_TOWN", "MAP_TWINLEAF_TOWN", "HEAL_LOCATION_TWINLEAF_TOWN_PLAYERSHOUSE_2F", "FLAG_VISITED_TWINLEAF_TOWN", 17),
    ("MAPSEC_SANDGEM_TOWN", "MAP_SANDGEM_TOWN", "HEAL_LOCATION_SANDGEM_TOWN", "FLAG_VISITED_SANDGEM_TOWN", 18),
    ("MAPSEC_JUBILIFE_CITY", "MAP_JUBILIFE_CITY", "HEAL_LOCATION_JUBILIFE_CITY", "FLAG_VISITED_JUBILIFE_CITY", 19),
    ("MAPSEC_OREBURGH_CITY", "MAP_OREBURGH_CITY", "HEAL_LOCATION_OREBURGH_CITY", "FLAG_VISITED_OREBURGH_CITY", 20),
    ("MAPSEC_FLOAROMA_TOWN", "MAP_FLOAROMA_TOWN", "HEAL_LOCATION_FLOAROMA_TOWN", "FLAG_VISITED_FLOAROMA_TOWN", 21),
    ("MAPSEC_ETERNA_CITY", "MAP_ETERNA_CITY", "HEAL_LOCATION_ETERNA_CITY", "FLAG_VISITED_ETERNA_CITY", 22),
    ("MAPSEC_HEARTHOME_CITY", "MAP_HEARTHOME_CITY", "HEAL_LOCATION_HEARTHOME_CITY", "FLAG_VISITED_HEARTHOME_CITY", 23),
    ("MAPSEC_SOLACEON_TOWN", "MAP_SOLACEON_TOWN", "HEAL_LOCATION_SOLACEON_TOWN", "FLAG_VISITED_SOLACEON_TOWN", 24),
    ("MAPSEC_VEILSTONE_CITY", "MAP_VEILSTONE_CITY", "HEAL_LOCATION_VEILSTONE_CITY", "FLAG_VISITED_VEILSTONE_CITY", 25),
]

NEW_MAPSECS = [
    ("MAPSEC_VEILSTONE_CITY", "VEILSTONE CITY"),
    ("MAPSEC_VEILSTONE_GYM", "VEILSTONE GYM"),
    ("MAPSEC_GALACTIC_WAREHOUSE", "GALACTIC WAREHOUSE"),
]
LAST_SINNOH_MAPSEC = "MAPSEC_GALACTIC_WAREHOUSE"


def patch_region_mapsecs():
    path = REPO / "src" / "data" / "region_map" / "region_map_sections.json"
    text = path.read_text(encoding="utf-8")

    missing = [(i, n) for i, n in NEW_MAPSECS if f'"id": "{i}"' not in text]
    if missing:
        tail = '''{
      "id": "MAPSEC_VEILSTONE_GATE",
      "name": "VEILSTONE GATE"
    }
  ]
}'''
        if tail not in text:
            raise SystemExit("region_map_sections.json: MAPSEC_VEILSTONE_GATE tail not found")
        extra = "".join(
            ',\n    {\n      "id": "%s",\n      "name": "%s"\n    }' % (i, n) for i, n in missing
        )
        text = text.replace(
            tail,
            '{\n      "id": "MAPSEC_VEILSTONE_GATE",\n      "name": "VEILSTONE GATE"\n    }' + extra + "\n  ]\n}",
        )
        print("patched region_map_sections.json (new sections)")
    else:
        print("region_map_sections already has Veilstone sections")

    for mapsec, _map, _heal, _flag, x in FLY_TOWNS:
        pat = re.compile(r'("id": "%s",\n\s+"name": "[^"]*")(\n(\s+)\})' % mapsec)
        m = pat.search(text)
        if not m:
            if re.search(r'"id": "%s",\n\s+"name": "[^"]*",\n\s+"x":' % mapsec, text):
                continue
            raise SystemExit(f"region_map_sections.json: {mapsec} block not found")
        ind = m.group(3) + "  "
        coords = f',\n{ind}"x": {x},\n{ind}"y": 0,\n{ind}"width": 1,\n{ind}"height": 1'
        text = text[: m.end(1)] + coords + text[m.end(1):]
        print(f"  placed {mapsec} at ({x}, 0)")
    path.write_text(text, encoding="utf-8")


def patch_regions_h():
    path = REPO / "include" / "regions.h"
    text = path.read_text(encoding="utf-8")
    if f"sectionId <= {LAST_SINNOH_MAPSEC};" in text:
        print("regions.h already extended")
        return
    new = re.sub(r"sectionId <= MAPSEC_\w+;", f"sectionId <= {LAST_SINNOH_MAPSEC};", text, count=1)
    if new == text:
        raise SystemExit("regions.h: IsSinnohMapSec bound not found")
    path.write_text(new, encoding="utf-8")
    print("patched regions.h")


def patch_map_name_popup():
    path = REPO / "src" / "map_name_popup.c"
    text = path.read_text(encoding="utf-8")
    if "MAPSEC_VEILSTONE_CITY - KANTO_MAPSEC_COUNT" in text:
        print("map_name_popup already has M19")
        return
    for theme in ("MAPPOPUP_THEME_WOOD", "MAPPOPUP_THEME_BW_DEFAULT"):
        anchor = f"[MAPSEC_VEILSTONE_GATE - KANTO_MAPSEC_COUNT] = {theme},"
        if text.count(anchor) != 1:
            raise SystemExit(f"map_name_popup.c: anchor for {theme} not unique ({text.count(anchor)})")
        extra = "".join(f"\n    [{i} - KANTO_MAPSEC_COUNT] = {theme}," for i, _ in NEW_MAPSECS)
        text = text.replace(anchor, anchor + extra)
    path.write_text(text, encoding="utf-8")
    print("patched map_name_popup.c")


def patch_heal_locations():
    path = REPO / "src" / "data" / "heal_locations.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    locs = data["heal_locations"] if isinstance(data, dict) else data
    if any(L.get("id") == "HEAL_LOCATION_VEILSTONE_CITY" for L in locs):
        print("heal_locations already has Veilstone")
        return
    locs.append({
        "id": "HEAL_LOCATION_VEILSTONE_CITY",
        "map": "MAP_VEILSTONE_CITY",
        "x": 45,
        "y": 36,
        "respawn_map": "MAP_VEILSTONE_CITY_POKEMON_CENTER_1F",
        "respawn_npc": "LOCALID_VEILSTONE_NURSE",
    })
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("patched heal_locations.json")


# --------------------------------------------------------------------------- Patches: flags / vars / new game
M19_FLAGS = [
    (0x295, "FLAG_RECEIVED_VEILSTONE_GYM_TM", "Sinnoh M19"),
    (0x296, "FLAG_HIDE_VEILSTONE_MAYLENE", "Sinnoh M19; cameo outside the Gym, cleared after badge"),
    (0x297, "FLAG_HIDE_VEILSTONE_COUNTERPART", "Sinnoh M19; Dawn/Lucas, cleared after badge"),
    (0x298, "FLAG_HIDE_VEILSTONE_WAREHOUSE_GRUNTS", "Sinnoh M19; set once the grunts are beaten"),
    (0x299, "FLAG_GOT_HM_FLY_VEILSTONE", "Sinnoh M19; HM02 item ball in the Galactic Warehouse"),
    (0x29A, "FLAG_GOT_VEILSTONE_PORYGON", "Sinnoh M19"),
    (0x29B, "FLAG_VISITED_VEILSTONE_CITY", "Sinnoh M19; Fly"),
    (0x29C, "FLAG_DEFEATED_VEILSTONE_WAREHOUSE_GRUNTS", "Sinnoh M19"),
    (0x29D, "FLAG_VISITED_TWINLEAF_TOWN", "Sinnoh M19; Fly"),
    (0x29E, "FLAG_VISITED_SANDGEM_TOWN", "Sinnoh M19; Fly"),
    (0x29F, "FLAG_VISITED_JUBILIFE_CITY", "Sinnoh M19; Fly"),
    (0x2A0, "FLAG_VISITED_OREBURGH_CITY", "Sinnoh M19; Fly"),
    (0x2A1, "FLAG_VISITED_FLOAROMA_TOWN", "Sinnoh M19; Fly"),
    (0x2A2, "FLAG_VISITED_ETERNA_CITY", "Sinnoh M19; Fly"),
    (0x2A3, "FLAG_VISITED_HEARTHOME_CITY", "Sinnoh M19; Fly"),
    (0x2A4, "FLAG_VISITED_SOLACEON_TOWN", "Sinnoh M19; Fly"),
]


def patch_flags_vars():
    flags = REPO / "include" / "constants" / "flags.h"
    ft = flags.read_text(encoding="utf-8")
    changed = False
    for value, name, note in M19_FLAGS:
        if re.search(rf"^#define {name}\b", ft, re.M):
            continue
        old = f"#define FLAG_UNUSED_0x{value:X}  0x{value:X} // Unused Flag\n"
        if old not in ft:
            raise SystemExit(f"flags.h: expected placeholder for 0x{value:X} not found")
        ft = ft.replace(old, f"#define {name}  0x{value:X} // {note}\n")
        changed = True
    if changed:
        flags.write_text(ft, encoding="utf-8")
        print("patched flags.h")
    else:
        print("flags.h already has M19")

    vars_path = REPO / "include" / "constants" / "vars.h"
    vt = vars_path.read_text(encoding="utf-8")
    if "VAR_VEILSTONE_CITY_STATE" not in vt:
        old = "#define VAR_UNUSED_0x40FB                                0x40FB // Unused Var\n"
        if old not in vt:
            raise SystemExit("vars.h: VAR_UNUSED_0x40FB placeholder not found")
        vt = vt.replace(
            old,
            "#define VAR_VEILSTONE_CITY_STATE                         0x40FB // Sinnoh M19: 0 counterpart pending, 1 warehouse standoff, 2 grunts beaten\n",
        )
        vars_path.write_text(vt, encoding="utf-8")
        print("patched vars.h")
    else:
        print("vars.h already has VAR_VEILSTONE_CITY_STATE")

    ng = REPO / "data" / "scripts" / "new_game.inc"
    nt = ng.read_text(encoding="utf-8")
    if "FLAG_HIDE_VEILSTONE_MAYLENE" not in nt:
        anchor = "\tsetflag FLAG_HIDE_ROUTE210_CYNTHIA\n"
        if anchor not in nt:
            raise SystemExit("new_game.inc: FLAG_HIDE_ROUTE210_CYNTHIA anchor not found")
        nt = nt.replace(
            anchor,
            anchor + "\tsetflag FLAG_HIDE_VEILSTONE_MAYLENE\n\tsetflag FLAG_HIDE_VEILSTONE_COUNTERPART\n",
            1,
        )
        ng.write_text(nt, encoding="utf-8")
        print("patched new_game.inc")
    else:
        print("new_game.inc already hides Veilstone cameos")


# --------------------------------------------------------------------------- Patches: trainers
M19_TRAINERS = [
    # old alias, new constant, name, class, pic, gender, music, mons
    ("TRAINER_JERRY_2", "TRAINER_LEADER_MAYLENE", "MAYLENE", "Leader", "Leaf", "Female", "Female", [
        ("Meditite (F)", 28, ["Force Palm", "Detect", "Confusion", "Mach Punch"]),
        ("Machoke (M)", 29, ["Karate Chop", "Low Kick", "Seismic Toss", "Revenge"]),
        ("Lucario (M) @ Sitrus Berry", 32, ["Aura Sphere", "Force Palm", "Bone Rush", "Quick Attack"]),
    ]),
    ("TRAINER_JERRY_3", "TRAINER_BLACK_BELT_COLBY_VEILSTONE", "COLBY", "Black Belt", "Black Belt", "Male", "Intense", [
        ("Machop", 25, ["Karate Chop", "Low Kick", "Foresight", "Seismic Toss"]),
        ("Meditite", 26, ["Force Palm", "Detect", "Confusion", "Meditate"]),
    ]),
    ("TRAINER_JERRY_4", "TRAINER_BLACK_BELT_DARREN_VEILSTONE", "DARREN", "Black Belt", "Black Belt", "Male", "Intense", [
        ("Machoke", 27, ["Karate Chop", "Low Kick", "Seismic Toss", "Revenge"]),
    ]),
    ("TRAINER_JERRY_5", "TRAINER_BLACK_BELT_JEFFERY_VEILSTONE", "JEFFERY", "Black Belt", "Black Belt", "Male", "Intense", [
        ("Meditite", 26, ["Force Palm", "Detect", "Mach Punch", "Meditate"]),
        ("Machop", 26, ["Karate Chop", "Low Kick", "Vital Throw", "Foresight"]),
    ]),
    ("TRAINER_KAREN_2", "TRAINER_BLACK_BELT_RAFAEL_VEILSTONE", "RAFAEL", "Black Belt", "Black Belt", "Male", "Intense", [
        ("Machoke", 26, ["Karate Chop", "Low Kick", "Seismic Toss", "Revenge"]),
        ("Meditite", 27, ["Force Palm", "Detect", "Confusion", "Meditate"]),
    ]),
    ("TRAINER_KAREN_3", "TRAINER_GALACTIC_GRUNT_VEILSTONE_1", "GRUNT", "Team Galactic", "Magma Grunt M", "Male", "Male", [
        ("Stunky", 25, ["Poison Gas", "Scratch", "Smokescreen", "Bite"]),
        ("Zubat", 26, ["Bite", "Supersonic", "Wing Attack", "Leech Life"]),
    ]),
    ("TRAINER_KAREN_4", "TRAINER_GALACTIC_GRUNT_VEILSTONE_2", "GRUNT", "Team Galactic", "Magma Grunt M", "Male", "Male", [
        ("Croagunk", 26, ["Poison Sting", "Mud Slap", "Astonish", "Taunt"]),
        ("Glameow (F)", 27, ["Fake Out", "Scratch", "Hypnosis", "Fury Swipes"]),
    ]),
]


def _party_block(header, name, cls, pic, gender, music, mons):
    lines = [
        f"=== {header} ===",
        f"Name: {name}",
        f"Class: {cls}",
        f"Pic: {pic}",
        f"Gender: {gender}",
        f"Music: {music}",
        "Double Battle: No",
        "AI: Basic Trainer",
        "",
    ]
    for species, level, moves in mons:
        lines.append(species)
        lines.append(f"Level: {level}")
        lines.append("IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe")
        lines.extend(f"- {mv}" for mv in moves)
        lines.append("")
    return "\n".join(lines) + "\n"


def patch_opponents():
    path = REPO / "include" / "constants" / "opponents.h"
    text = path.read_text(encoding="utf-8")
    changed = False
    for old, new, *_ in M19_TRAINERS:
        if re.search(rf"^#define {new}\b", text, re.M):
            continue
        m = re.search(rf"^#define {old}(\s+)(\d+)[ \t]*\n", text, re.M)
        if not m:
            raise SystemExit(f"opponents.h: {old} not found")
        num = m.group(2)
        repl = (
            f"#define {new}                       {num} // Sinnoh M19: was {old}\n"
            f"#define {old} {new}\n"
        )
        text = text[: m.start()] + repl + text[m.end():]
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
        print("patched opponents.h")
    else:
        print("opponents.h already has M19")


def patch_trainers_party():
    path = REPO / "src" / "data" / "trainers.party"
    text = path.read_text(encoding="utf-8")
    changed = False
    for old, new, name, cls, pic, gender, music, mons in M19_TRAINERS:
        if f"=== {new} ===" in text:
            continue
        pattern = rf"=== {old} ===.*?(?=\n=== |\Z)"
        m = re.search(pattern, text, flags=re.S)
        if not m:
            raise SystemExit(f"trainers.party: {old} not found")
        block = _party_block(new, name, cls, pic, gender, music, mons)
        text = text[: m.start()] + block + text[m.end():]
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
        print("patched trainers.party")
    else:
        print("trainers.party already has M19")


# --------------------------------------------------------------------------- Patches: TM Drain Punch
def patch_tms_hms():
    path = REPO / "include" / "constants" / "tms_hms.h"
    text = path.read_text(encoding="utf-8")
    if "F(DRAIN_PUNCH)" in text:
        print("tms_hms.h already has DRAIN_PUNCH")
        return
    if "    F(PAYBACK)\n" not in text:
        raise SystemExit("tms_hms.h: F(PAYBACK) anchor not found")
    text = text.replace("    F(PAYBACK)\n", "    F(PAYBACK) \\\n    F(DRAIN_PUNCH)\n", 1)
    path.write_text(text, encoding="utf-8")
    print("patched tms_hms.h")


def patch_items_drain_punch():
    path = REPO / "src" / "data" / "items.h"
    text = path.read_text(encoding="utf-8")
    if "[ITEM_TM_DRAIN_PUNCH]" in text:
        print("items.h already has ITEM_TM_DRAIN_PUNCH")
        return
    new = '''    [ITEM_TM_DRAIN_PUNCH] =
    {
        .name = ITEM_NAME("TM60"),
        .price = 3000,
        .description = COMPOUND_STRING(
            "A punch that drains\\n"
            "half the damage it\\n"
            "inflicts to heal HP."),
        .importance = I_REUSABLE_TMS,
        .pocket = POCKET_TM_HM,
        .type = ITEM_USE_PARTY_MENU,
        .fieldUseFunc = ItemUseOutOfBattle_TMHM,
    },'''
    pattern = re.compile(r"    \[ITEM_TM52\] =\n    \{\n(?:        .*\n)*?    \},")
    m = pattern.search(text)
    if not m:
        raise SystemExit("items.h: [ITEM_TM52] placeholder not found")
    text = text[: m.start()] + new + text[m.end():]
    path.write_text(text, encoding="utf-8")
    print("patched items.h for DRAIN_PUNCH TM")


# --------------------------------------------------------------------------- Patches: field moves
def _replace_in_block(text: str, block_name: str, old: str, new: str) -> str:
    start = text.index(f"[{block_name}] =")
    end = text.index("    },", start)
    block = text[start:end]
    if new in block:
        return text
    if old not in block:
        raise SystemExit(f"field_move.c: expected line not found in {block_name}")
    return text[:start] + block.replace(old, new, 1) + text[end:]


def patch_field_move():
    path = REPO / "src" / "field_move.c"
    text = path.read_text(encoding="utf-8")
    orig = text
    text = _replace_in_block(
        text, "FIELD_MOVE_FLY",
        "        .arg = IS_FRLG ? FLAG_TO_BADGE(FLAG_BADGE03_GET) : FLAG_TO_BADGE(FLAG_BADGE06_GET),",
        "        .arg = IS_FRLG ? FLAG_TO_BADGE(FLAG_BADGE03_GET) : FLAG_TO_BADGE(FLAG_BADGE04_GET), // Sinnoh: Cobble Badge unlocks Fly",
    )
    text = _replace_in_block(
        text, "FIELD_MOVE_STRENGTH",
        "        .arg = FLAG_TO_BADGE(FLAG_BADGE04_GET),",
        "        .arg = FLAG_TO_BADGE(FLAG_BADGE06_GET), // Sinnoh: Mine Badge unlocks Strength",
    )
    if text != orig:
        path.write_text(text, encoding="utf-8")
        print("patched field_move.c")
    else:
        print("field_move.c already patched")


# --------------------------------------------------------------------------- Patches: Sinnoh Fly (region_map.c)
def patch_region_map_fly():
    path = REPO / "src" / "region_map.c"
    text = path.read_text(encoding="utf-8")
    orig = text

    if "[MAPSEC_VEILSTONE_CITY] = {" not in text:
        entries = "".join(
            f"    [{sec}] = {{MAP_GROUP({mp}), MAP_NUM({mp}), {heal}}},\n"
            for sec, mp, heal, _flag, _x in FLY_TOWNS
        )
        start = text.index("static const u8 sMapHealLocations[][3] =")
        end = text.index("\n};\n", start) + 1
        text = text[:end] + entries + text[end:]

    if "case MAPSEC_VEILSTONE_CITY:" not in text:
        cases = "".join(
            f"    case {sec}:\n"
            f"        return FlagGet({flag}) ? MAPSECTYPE_CITY_CANFLY : MAPSECTYPE_CITY_CANTFLY;\n"
            for sec, _mp, _heal, flag, _x in FLY_TOWNS
        )
        anchor = "    case MAPSEC_BATTLE_FRONTIER:\n        return FlagGet(FLAG_LANDMARK_BATTLE_FRONTIER)"
        start = text.index("static u8 GetMapsecType(mapsec_u16_t mapSecId)\n{")
        idx = text.index(anchor, start)
        text = text[:idx] + cases + text[idx:]

    if text != orig:
        path.write_text(text, encoding="utf-8")
        print("patched region_map.c (Sinnoh heal locations + fly flags)")
    else:
        print("region_map.c already has Sinnoh fly wiring")

    layout = REPO / "src" / "data" / "region_map" / "region_map_layout.h"
    lt = layout.read_text(encoding="utf-8")
    lines = lt.split("\n")
    row_idx = next(i for i, ln in enumerate(lines) if ln.lstrip().startswith("{MAPSEC_"))
    tokens = re.findall(r"MAPSEC_\w+", lines[row_idx])
    dirty = False
    for sec, _mp, _heal, _flag, x in FLY_TOWNS:
        if tokens[x] == sec:
            continue
        if tokens[x] != "MAPSEC_NONE":
            raise SystemExit(f"region_map_layout.h: cell ({x}, 0) already used by {tokens[x]}")
        tokens[x] = sec
        dirty = True
    if dirty:
        lines[row_idx] = "    {" + ", ".join(tokens) + "},"
        layout.write_text("\n".join(lines), encoding="utf-8")
        print("patched region_map_layout.h (Sinnoh fly spots on the top row)")
    else:
        print("region_map_layout.h already has Sinnoh fly spots")


# --------------------------------------------------------------------------- Patches: visited flags
VISITED_TOWN_MAPS = [
    ("TwinleafTown", "FLAG_VISITED_TWINLEAF_TOWN"),
    ("SandgemTown", "FLAG_VISITED_SANDGEM_TOWN"),
    ("JubilifeCity", "FLAG_VISITED_JUBILIFE_CITY"),
    ("OreburghCity", "FLAG_VISITED_OREBURGH_CITY"),
    ("FloaromaTown", "FLAG_VISITED_FLOAROMA_TOWN"),
    ("EternaCity", "FLAG_VISITED_ETERNA_CITY"),
    ("HearthomeCity", "FLAG_VISITED_HEARTHOME_CITY"),
    ("SolaceonTown", "FLAG_VISITED_SOLACEON_TOWN"),
]


def patch_visited_flags():
    for name, flag in VISITED_TOWN_MAPS:
        path = MAPS / name / "scripts.inc"
        text = path.read_text(encoding="utf-8")
        if f"setflag {flag}\n" in text:
            print(f"{name}: {flag} already set on transition")
            continue
        m = re.search(r"map_script MAP_SCRIPT_ON_TRANSITION, (\w+)", text)
        if m:
            label = m.group(1)
            lm = re.search(rf"^{label}::?\n", text, re.M)
            if not lm:
                raise SystemExit(f"{name}: OnTransition label {label} not defined")
            text = text[: lm.end()] + f"\tsetflag {flag}\n" + text[lm.end():]
        else:
            header = f"{name}_MapScripts::\n\t.byte 0\n"
            if not text.startswith(header):
                raise SystemExit(f"{name}: unexpected MapScripts header")
            label = f"{name}_OnTransition"
            text = (
                f"{name}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, {label}\n\t.byte 0\n\n"
                f"{label}:\n\tsetflag {flag}\n\tend\n" + text[len(header):]
            )
        path.write_text(text, encoding="utf-8")
        print(f"patched {name} to set {flag}")


# --------------------------------------------------------------------------- Patches: event_scripts.s
def patch_event_scripts():
    path = REPO / "data" / "event_scripts.s"
    text = path.read_text(encoding="utf-8")
    marker = '\t.include "data/maps/Route215_VeilstoneGate/scripts.inc"\n'
    names = [CITY] + M19_INDOOR
    block = "".join(f'\t.include "data/maps/{n}/scripts.inc"\n' for n in names)
    if f'data/maps/{CITY}/scripts.inc' in text:
        print("event_scripts.s already has M19 includes")
        return
    if marker not in text:
        raise SystemExit("event_scripts.s: Route215_VeilstoneGate include not found")
    path.write_text(text.replace(marker, marker + block, 1), encoding="utf-8")
    print("patched event_scripts.s")


# --------------------------------------------------------------------------- main
def main():
    scaffold_city()
    scaffold_center()
    scaffold_gym()
    scaffold_department_store()
    scaffold_massage_house()
    scaffold_houses()
    scaffold_game_corner()
    scaffold_prize_exchange()
    scaffold_warehouse()
    scaffold_route214_gate()
    patch_route215_gate()
    patch_map_groups()
    patch_region_mapsecs()
    patch_regions_h()
    patch_map_name_popup()
    patch_heal_locations()
    patch_flags_vars()
    patch_opponents()
    patch_trainers_party()
    patch_tms_hms()
    patch_items_drain_punch()
    patch_field_move()
    patch_region_map_fly()
    patch_visited_flags()
    patch_event_scripts()
    print("M19 scaffold complete.")


if __name__ == "__main__":
    main()
