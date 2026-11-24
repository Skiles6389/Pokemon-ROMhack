#!/usr/bin/env python3
"""
M29 Elite Four: Aaron, Bertha, Flint, Lucian (Platinum teams/levels, IVs 0).

Land IDs (Platinum):
  AaronsRoom / BerthasRoom / FlintsRoom / LuciansRoom: 260–263
  Elevator_ToAaron: 306
  Elevators Bertha/Flint/Lucian share land 307 (separate headers)
  Elevator_ToCynthia: 308 (soft-closes Champion for M30)

Also opens League Exterior soft-close and rebuilds CanalaveCity_Gym from land 225.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinnoh_build_lib import (  # noqa: E402
    MAPS,
    clear_plat_walkables,
    ensure_flag,
    ensure_trainer,
    grid_from_chunks,
    obj,
    pack,
    register_maps,
    scrub,
    warp,
    write_layout,
    write_map,
)

AARON, BERTHA, FLINT, LUCIAN = [[260]], [[261]], [[262]], [[263]]
ELEV_AARON, ELEV_BFL, ELEV_CYNTHIA = [[306]], [[307]], [[308]]
CANALAVE_GYM = [[225]]


def stitch_layout(name: str, chunks):
    grid, w, h, coll = grid_from_chunks(chunks)
    clear_plat_walkables(grid, chunks)
    write_layout(name, w, h, "gTileset_Building", "gTileset_Facility", pack(grid, coll))
    return grid, w, h


def e4_scripts(em: str, tid: str, flag: str, next_hint: str, intro: str, defeat: str, after: str) -> str:
    return f"""{em}_MapScripts::
	.byte 0

{em}_EventScript_Leader::
	lock
	faceplayer
	goto_if_set {flag}, {em}_EventScript_PostBattle
	playbgm MUS_ENCOUNTER_ELITE_FOUR, FALSE
	msgbox {em}_Text_Intro, MSGBOX_DEFAULT
	trainerbattle_no_intro {tid}, {em}_Text_Defeat
	goto {em}_EventScript_Defeated
	end

{em}_EventScript_Defeated::
	setflag {flag}
	msgbox {em}_Text_After, MSGBOX_DEFAULT
	release
	end

{em}_EventScript_PostBattle::
	msgbox {em}_Text_After, MSGBOX_DEFAULT
	release
	end

{em}_EventScript_DoorGuard::
	lock
	faceplayer
	goto_if_set {flag}, {em}_EventScript_DoorOpen
	msgbox {em}_Text_DoorClosed, MSGBOX_DEFAULT
	release
	end

{em}_EventScript_DoorOpen::
	msgbox {em}_Text_DoorOpen, MSGBOX_DEFAULT
	release
	end

{em}_Text_Intro:
	.string "{intro}$"

{em}_Text_Defeat:
	.string "{defeat}$"

{em}_Text_After:
	.string "{after}$"

{em}_Text_DoorClosed:
	.string "The path ahead stays sealed until you\\n"
	.string "defeat the Elite Four member here.$"

{em}_Text_DoorOpen:
	.string "{next_hint}$"
"""


def write_e4_room(
    name: str,
    mid: str,
    layout: str,
    chunks,
    tid: str,
    flag: str,
    gfx: str,
    *,
    south_dest: str,
    south_wid: int,
    north_dest: str,
    north_wid: int,
    intro: str,
    defeat: str,
    after: str,
    next_hint: str,
):
    stitch_layout(name, chunks)
    # Platinum coords: leader (8,5), south warp (8,11), north warp (8,2)
    objects = [
        obj(gfx, 8, 5, f"{name}_EventScript_Leader", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj(
            "OBJ_EVENT_GFX_MAN_2",
            8,
            2,
            f"{name}_EventScript_DoorGuard",
            movement="MOVEMENT_TYPE_FACE_DOWN",
            flag=flag,
        ),
    ]
    warps = [
        warp(8, 11, south_dest, south_wid),  # 0 south
        warp(8, 2, north_dest, north_wid),  # 1 north
    ]
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": layout,
            "music": "MUS_VICTORY_ROAD",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_POKEMON_LEAGUE",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": objects,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        e4_scripts(name, tid, flag, next_hint, intro, defeat, after),
    )


def write_elevator(
    name: str,
    mid: str,
    layout: str,
    chunks,
    *,
    south: tuple[int, int],
    south_dest: str,
    south_wid: int,
    north: tuple[int, int],
    north_dest: str,
    north_wid: int,
    line: str,
    soft_close: bool = False,
):
    stitch_layout(name, chunks)
    objects = []
    if soft_close:
        objects.append(
            obj(
                "OBJ_EVENT_GFX_MAN_2",
                north[0],
                north[1],
                f"{name}_EventScript_Closed",
                movement="MOVEMENT_TYPE_FACE_DOWN",
            )
        )
        scripts = f"""{name}_MapScripts::
	.byte 0

{name}_EventScript_Closed::
	lock
	faceplayer
	goto_if_unset FLAG_DEFEATED_ELITE_FOUR_LUCIAN, {name}_EventScript_NeedLucian
	msgbox {name}_Text_Closed, MSGBOX_DEFAULT
	release
	end

{name}_EventScript_NeedLucian::
	msgbox {name}_Text_NeedLucian, MSGBOX_DEFAULT
	release
	end

{name}_Text_NeedLucian:
	.string "Lucian still waits in his chamber.\\n"
	.string "Defeat him before facing the Champion.$"

{name}_Text_Closed:
	.string "The Champion's chamber opens in the\\n"
	.string "next League build. Rest here for now.$"
"""
    else:
        scripts = f"""{name}_MapScripts::
	.byte 0

{name}_EventScript_Attendant::
	msgbox {name}_Text, MSGBOX_NPC
	end

{name}_Text:
	.string "{line}$"
"""
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": layout,
            "music": "MUS_VICTORY_ROAD",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_POKEMON_LEAGUE",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": objects,
            "warp_events": [
                warp(south[0], south[1], south_dest, south_wid),  # 0
                warp(north[0], north[1], north_dest, north_wid),  # 1
            ],
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )


def open_league_entrance():
    ext_path = MAPS / "PokemonLeague_Exterior" / "map.json"
    ext = json.loads(ext_path.read_text())
    ext["object_events"] = [
        o for o in ext.get("object_events") or [] if o.get("script") != "PokemonLeague_Exterior_EventScript_E4Closed"
    ]
    ext_path.write_text(json.dumps(ext, indent=2) + "\n")
    (MAPS / "PokemonLeague_Exterior" / "scripts.inc").write_text(
        """PokemonLeague_Exterior_MapScripts::
	.byte 0

PokemonLeague_Exterior_EventScript_Npc0::
	msgbox PokemonLeague_Exterior_EventScript_Npc0_Text, MSGBOX_NPC
	end

PokemonLeague_Exterior_EventScript_Npc0_Text:
	.string "The Pokemon League waits at the summit.\\n"
	.string "Only trainers with eight badges pass.$"

PokemonLeague_Exterior_EventScript_Npc1::
	msgbox PokemonLeague_Exterior_EventScript_Npc1_Text, MSGBOX_NPC
	end

PokemonLeague_Exterior_EventScript_Npc1_Text:
	.string "Heal at the north Pokemon Center,\\n"
	.string "then ride the elevator to Aaron.$"
"""
    )

    data = json.loads((MAPS / "PokemonLeague_NorthPC" / "map.json").read_text())
    warps = [w for w in data.get("warp_events") or [] if w.get("dest_map") == "MAP_POKEMON_LEAGUE_EXTERIOR"]
    # North into Aaron elevator (arrive on south warp 0)
    warps += [
        {"x": 4, "y": 1, "elevation": 0, "dest_map": "MAP_POKEMON_LEAGUE_ELEVATOR_TO_AARON", "dest_warp_id": "0"},
        {"x": 5, "y": 1, "elevation": 0, "dest_map": "MAP_POKEMON_LEAGUE_ELEVATOR_TO_AARON", "dest_warp_id": "0"},
    ]
    nurse = obj("OBJ_EVENT_GFX_NURSE", 4, 3, "PokemonLeague_NorthPC_EventScript_Nurse")
    nurse["local_id"] = "LOCALID_NURSE"
    data["warp_events"] = warps
    data["object_events"] = [
        nurse,
        obj("OBJ_EVENT_GFX_MAN_2", 7, 4, "PokemonLeague_NorthPC_EventScript_Clerk"),
    ]
    write_map(
        "PokemonLeague_NorthPC",
        data,
        """PokemonLeague_NorthPC_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PokemonLeague_NorthPC_OnTransition
	.byte 0

PokemonLeague_NorthPC_OnTransition::
	setrespawn HEAL_LOCATION_EVER_GRANDE_CITY_POKEMON_LEAGUE
	end

PokemonLeague_NorthPC_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

PokemonLeague_NorthPC_EventScript_Clerk::
	msgbox PokemonLeague_NorthPC_Text_Clerk, MSGBOX_NPC
	end

PokemonLeague_NorthPC_Text_Clerk:
	.string "Welcome to the Pokemon League.\\n"
	.string "Heal up, then take the elevator north.\\p"
	.string "Aaron of the Elite Four is first.$"
""",
    )


def rebuild_canalave_gym():
    name = "CanalaveCity_Gym"
    stitch_layout(name, CANALAVE_GYM)
    scripts = (MAPS / name / "scripts.inc").read_text()
    # Keep M23 Byron scripts; place objects on Platinum coords
    data = {
        "id": "MAP_CANALAVE_CITY_GYM",
        "name": name,
        "layout": "LAYOUT_CANALAVE_CITY_GYM",
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
            obj("OBJ_EVENT_GFX_EXPERT_M", 16, 3, "CanalaveCity_Gym_EventScript_Byron"),
            obj("OBJ_EVENT_GFX_MAN_2", 15, 25, "CanalaveCity_Gym_EventScript_GymGuide"),
            obj("OBJ_EVENT_GFX_MAN_4", 14, 3, "CanalaveCity_Gym_EventScript_WorkerAlan", trainer="TRAINER_TYPE_NORMAL", sight="2"),
            obj("OBJ_EVENT_GFX_MAN_4", 22, 16, "CanalaveCity_Gym_EventScript_WorkerFlavor", movement="MOVEMENT_TYPE_LOOK_AROUND"),
            obj("OBJ_EVENT_GFX_SAILOR", 9, 17, "CanalaveCity_Gym_EventScript_SailorJonah", trainer="TRAINER_TYPE_NORMAL", sight="2"),
            obj("OBJ_EVENT_GFX_BLACK_BELT", 24, 3, "CanalaveCity_Gym_EventScript_BlackBeltFlavor", movement="MOVEMENT_TYPE_FACE_DOWN"),
            obj("OBJ_EVENT_GFX_BLACK_BELT", 27, 25, "CanalaveCity_Gym_EventScript_AceFlavor", movement="MOVEMENT_TYPE_LOOK_AROUND"),
            obj("OBJ_EVENT_GFX_MAN_4", 8, 3, "CanalaveCity_Gym_EventScript_WorkerFlavor2", movement="MOVEMENT_TYPE_FACE_DOWN"),
        ],
        "warp_events": [warp(16, 27, "MAP_CANALAVE_CITY", 0)],
        "coord_events": [],
        "bg_events": [
            {
                "type": "sign",
                "x": 15,
                "y": 26,
                "elevation": 0,
                "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                "script": "CanalaveCity_Gym_EventScript_Statue",
            },
            {
                "type": "sign",
                "x": 17,
                "y": 26,
                "elevation": 0,
                "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                "script": "CanalaveCity_Gym_EventScript_Statue",
            },
        ],
    }
    # Append flavor scripts if missing
    if "WorkerFlavor" not in scripts:
        scripts += """
CanalaveCity_Gym_EventScript_WorkerFlavor::
	msgbox CanalaveCity_Gym_Text_WorkerFlavor, MSGBOX_NPC
	end

CanalaveCity_Gym_EventScript_WorkerFlavor2::
	msgbox CanalaveCity_Gym_Text_WorkerFlavor, MSGBOX_NPC
	end

CanalaveCity_Gym_EventScript_BlackBeltFlavor::
	msgbox CanalaveCity_Gym_Text_BlackBeltFlavor, MSGBOX_NPC
	end

CanalaveCity_Gym_EventScript_AceFlavor::
	msgbox CanalaveCity_Gym_Text_AceFlavor, MSGBOX_NPC
	end

CanalaveCity_Gym_Text_WorkerFlavor:
	.string "Steel floors, steel wills.\\n"
	.string "Byron forged this gym himself.$"

CanalaveCity_Gym_Text_BlackBeltFlavor:
	.string "Hit the beams hard enough and they\\n"
	.string "still do not bend.$"

CanalaveCity_Gym_Text_AceFlavor:
	.string "Canalave's ore ships out daily.\\n"
	.string "Trainers ship out after Byron.$"
"""
    write_map(name, data, scripts)
    print("Canalave gym rebuilt from land 225 (Platinum coords)")


def main() -> int:
    ensure_flag("FLAG_DEFEATED_ELITE_FOUR_AARON", "0x2B7", "Sinnoh M29 Elite Four Aaron")
    ensure_flag("FLAG_DEFEATED_ELITE_FOUR_BERTHA", "0x2B8", "Sinnoh M29 Elite Four Bertha")
    ensure_flag("FLAG_DEFEATED_ELITE_FOUR_FLINT", "0x2B9", "Sinnoh M29 Elite Four Flint")
    ensure_flag("FLAG_DEFEATED_ELITE_FOUR_LUCIAN", "0x2BA", "Sinnoh M29 Elite Four Lucian")

    ensure_trainer(
        "TRAINER_ELITE_FOUR_AARON",
        53,
        "Elite Four",
        "Elite Four Sidney",
        [("Dustox", 49), ("Beautifly", 49), ("Vespiquen", 50), ("Heracross", 51), ("Drapion", 53)],
        display_name="Aaron",
        gender="Male",
        tag="Sinnoh E4",
    )
    ensure_trainer(
        "TRAINER_ELITE_FOUR_BERTHA",
        55,
        "Elite Four",
        "Elite Four Phoebe",
        [("Quagsire", 50), ("Sudowoodo", 53), ("Golem", 52), ("Whiscash", 52), ("Hippowdon", 55)],
        display_name="Bertha",
        gender="Female",
        tag="Sinnoh E4",
    )
    ensure_trainer(
        "TRAINER_ELITE_FOUR_FLINT",
        57,
        "Elite Four",
        "Elite Four Drake",
        [("Houndoom", 53), ("Flareon", 57), ("Rapidash", 55), ("Infernape", 57), ("Magmortar", 55)],
        display_name="Flint",
        gender="Male",
        tag="Sinnoh E4",
    )
    ensure_trainer(
        "TRAINER_ELITE_FOUR_LUCIAN",
        59,
        "Elite Four",
        "Elite Four Sidney",
        [("Mr. Mime", 53), ("Girafarig", 55), ("Medicham", 54), ("Alakazam", 56), ("Bronzong", 59)],
        display_name="Lucian",
        gender="Male",
        tag="Sinnoh E4",
    )

    open_league_entrance()

    # Platinum elevator chain (shared land 307 for B/F/L elevators)
    write_elevator(
        "PokemonLeague_Elevator_ToAaron",
        "MAP_POKEMON_LEAGUE_ELEVATOR_TO_AARON",
        "LAYOUT_POKEMON_LEAGUE_ELEVATOR_TO_AARON",
        ELEV_AARON,
        south=(4, 15),
        south_dest="MAP_POKEMON_LEAGUE_NORTH_PC",
        south_wid=0,
        north=(4, 2),
        north_dest="MAP_POKEMON_LEAGUE_AARONS_ROOM",
        north_wid=0,
        line="Aaron of the Elite Four waits upstairs.\\nBug types lead his charge.",
    )

    write_e4_room(
        "PokemonLeague_AaronsRoom",
        "MAP_POKEMON_LEAGUE_AARONS_ROOM",
        "LAYOUT_POKEMON_LEAGUE_AARONS_ROOM",
        AARON,
        "TRAINER_ELITE_FOUR_AARON",
        "FLAG_DEFEATED_ELITE_FOUR_AARON",
        "OBJ_EVENT_GFX_SIDNEY",
        south_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_AARON",
        south_wid=1,
        north_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_BERTHA",
        north_wid=0,
        intro="I am AARON of the ELITE FOUR.\\nBug Pokemon are my pride.\\pShow me a battle worth the League!",
        defeat="My swarm... broken.",
        after="Bertha is next. Her Ground types\\nshake the floor itself.",
        next_hint="The elevator ahead leads to Bertha.",
    )

    write_elevator(
        "PokemonLeague_Elevator_ToBertha",
        "MAP_POKEMON_LEAGUE_ELEVATOR_TO_BERTHA",
        "LAYOUT_POKEMON_LEAGUE_ELEVATOR_TO_BERTHA",
        ELEV_BFL,
        south=(4, 15),
        south_dest="MAP_POKEMON_LEAGUE_AARONS_ROOM",
        south_wid=1,
        north=(4, 2),
        north_dest="MAP_POKEMON_LEAGUE_BERTHAS_ROOM",
        north_wid=0,
        line="Bertha's chamber is above.\\nGround types wait.",
    )

    write_e4_room(
        "PokemonLeague_BerthasRoom",
        "MAP_POKEMON_LEAGUE_BERTHAS_ROOM",
        "LAYOUT_POKEMON_LEAGUE_BERTHAS_ROOM",
        BERTHA,
        "TRAINER_ELITE_FOUR_BERTHA",
        "FLAG_DEFEATED_ELITE_FOUR_BERTHA",
        "OBJ_EVENT_GFX_EXPERT_F",
        south_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_BERTHA",
        south_wid=1,
        north_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_FLINT",
        north_wid=0,
        intro="I am BERTHA of the ELITE FOUR.\\nGround Pokemon endure every storm.\\pCan you stand firm against them?",
        defeat="So the earth can still shake...",
        after="Flint burns hotter than any forge.\\nDo not blink.",
        next_hint="The elevator ahead leads to Flint.",
    )

    write_elevator(
        "PokemonLeague_Elevator_ToFlint",
        "MAP_POKEMON_LEAGUE_ELEVATOR_TO_FLINT",
        "LAYOUT_POKEMON_LEAGUE_ELEVATOR_TO_FLINT",
        ELEV_BFL,
        south=(4, 15),
        south_dest="MAP_POKEMON_LEAGUE_BERTHAS_ROOM",
        south_wid=1,
        north=(4, 2),
        north_dest="MAP_POKEMON_LEAGUE_FLINTS_ROOM",
        north_wid=0,
        line="Flint's fire is next.\\nKeep your Water types ready.",
    )

    write_e4_room(
        "PokemonLeague_FlintsRoom",
        "MAP_POKEMON_LEAGUE_FLINTS_ROOM",
        "LAYOUT_POKEMON_LEAGUE_FLINTS_ROOM",
        FLINT,
        "TRAINER_ELITE_FOUR_FLINT",
        "FLAG_DEFEATED_ELITE_FOUR_FLINT",
        "OBJ_EVENT_GFX_MAN_3",
        south_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_FLINT",
        south_wid=1,
        north_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_LUCIAN",
        north_wid=0,
        intro="I am FLINT of the ELITE FOUR!\\nFire Pokemon torch every doubt!\\pLet's see if you can take the heat!",
        defeat="My flame... snuffed out.",
        after="Lucian waits with a calm mind.\\nPsychic pressure ahead.",
        next_hint="The elevator ahead leads to Lucian.",
    )

    write_elevator(
        "PokemonLeague_Elevator_ToLucian",
        "MAP_POKEMON_LEAGUE_ELEVATOR_TO_LUCIAN",
        "LAYOUT_POKEMON_LEAGUE_ELEVATOR_TO_LUCIAN",
        ELEV_BFL,
        south=(4, 15),
        south_dest="MAP_POKEMON_LEAGUE_FLINTS_ROOM",
        south_wid=1,
        north=(4, 2),
        north_dest="MAP_POKEMON_LEAGUE_LUCIANS_ROOM",
        north_wid=0,
        line="Lucian's psychic pressure waits above.",
    )

    write_e4_room(
        "PokemonLeague_LuciansRoom",
        "MAP_POKEMON_LEAGUE_LUCIANS_ROOM",
        "LAYOUT_POKEMON_LEAGUE_LUCIANS_ROOM",
        LUCIAN,
        "TRAINER_ELITE_FOUR_LUCIAN",
        "FLAG_DEFEATED_ELITE_FOUR_LUCIAN",
        "OBJ_EVENT_GFX_GENTLEMAN",
        south_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_LUCIAN",
        south_wid=1,
        north_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_CYNTHIA",
        north_wid=0,
        intro="I am LUCIAN of the ELITE FOUR.\\nPsychic Pokemon read every move.\\pShall we begin a battle of minds?",
        defeat="Your spirit outpaces my reading...",
        after="Beyond lies the Champion's chamber.\\nWin there, and the Hall of Fame awaits.",
        next_hint="The final elevator leads toward the Champion.",
    )

    write_elevator(
        "PokemonLeague_Elevator_ToCynthia",
        "MAP_POKEMON_LEAGUE_ELEVATOR_TO_CYNTHIA",
        "LAYOUT_POKEMON_LEAGUE_ELEVATOR_TO_CYNTHIA",
        ELEV_CYNTHIA,
        south=(4, 23),
        south_dest="MAP_POKEMON_LEAGUE_LUCIANS_ROOM",
        south_wid=1,
        north=(4, 2),
        north_dest="MAP_POKEMON_LEAGUE_ELEVATOR_TO_CYNTHIA",
        north_wid=0,  # self until M30
        line="",
        soft_close=True,
    )

    rebuild_canalave_gym()

    indoor = [
        "PokemonLeague_Elevator_ToAaron",
        "PokemonLeague_AaronsRoom",
        "PokemonLeague_Elevator_ToBertha",
        "PokemonLeague_BerthasRoom",
        "PokemonLeague_Elevator_ToFlint",
        "PokemonLeague_FlintsRoom",
        "PokemonLeague_Elevator_ToLucian",
        "PokemonLeague_LuciansRoom",
        "PokemonLeague_Elevator_ToCynthia",
    ]
    # Drop old shared elev name from prior builder run if present
    old = MAPS / "PokemonLeague_Elevator_ToBerthaFlintLucian"
    if old.exists():
        import shutil

        shutil.rmtree(old, ignore_errors=True)
        # layouts leftover OK; map_groups cleaned via register overwrite below

    register_maps([], indoor, "gMapGroup_IndoorM30EliteFour")
    # Ensure group list is exactly the indoor set (replace prior shared-elev entry)
    groups = json.loads((MAPS / "map_groups.json").read_text())
    groups["gMapGroup_IndoorM30EliteFour"] = indoor
    (MAPS / "map_groups.json").write_text(json.dumps(groups, indent=2) + "\n")

    scrub(indoor + ["PokemonLeague_NorthPC", "PokemonLeague_Exterior", "CanalaveCity_Gym"])
    print("M29 Elite Four build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
