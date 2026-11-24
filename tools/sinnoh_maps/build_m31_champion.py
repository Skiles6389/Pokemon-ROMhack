#!/usr/bin/env python3
"""
M30 Champion Cynthia + Hall of Fame + credits + ending flag.

Land IDs:
  PokemonLeague_Sinnoh_CynthiasRoom [[264]]
  PokemonLeague_Sinnoh_HallOfFame   [[265]]
  PokemonLeague_Sinnoh_HallwayToHoF [[309]]

Opens Elevator_ToCynthia north warp into Cynthia's room.
Sets FLAG_DEFEATED_CHAMPION_CYNTHIA + FLAG_SYS_GAME_CLEAR via Hall of Fame / GameClear.
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

CYNTHIA = [[264]]
HOF = [[265]]
HALLWAY = [[309]]


def stitch(name, chunks):
    grid, w, h = grid_from_chunks(chunks)
    clear_plat_walkables(grid, chunks)
    write_layout(name, w, h, "gTileset_Building", "gTileset_Facility", pack(grid))
    return w, h


def open_cynthia_elevator():
    path = MAPS / "PokemonLeague_Elevator_ToCynthia" / "map.json"
    data = json.loads(path.read_text())
    # Remove soft-close NPC; north warp → Cynthia room south (warp 0)
    data["object_events"] = []
    data["warp_events"] = [
        {"x": 4, "y": 23, "elevation": 0, "dest_map": "MAP_POKEMON_LEAGUE_LUCIANS_ROOM", "dest_warp_id": "1"},
        {"x": 4, "y": 2, "elevation": 0, "dest_map": "MAP_POKEMON_LEAGUE_SINNOH_CYNTHIAS_ROOM", "dest_warp_id": "0"},
    ]
    path.write_text(json.dumps(data, indent=2) + "\n")
    (MAPS / "PokemonLeague_Elevator_ToCynthia" / "scripts.inc").write_text(
        """PokemonLeague_Elevator_ToCynthia_MapScripts::
	.byte 0

PokemonLeague_Elevator_ToCynthia_EventScript_Attendant::
	msgbox PokemonLeague_Elevator_ToCynthia_Text, MSGBOX_NPC
	end

PokemonLeague_Elevator_ToCynthia_Text:
	.string "The Champion awaits.\\n"
	.string "Steel yourself.$"
"""
    )


def main() -> int:
    ensure_flag("FLAG_DEFEATED_CHAMPION_CYNTHIA", "0x2BB", "Sinnoh M30 Champion Cynthia")

    ensure_trainer(
        "TRAINER_CHAMPION_CYNTHIA",
        62,
        "Champion",
        "Champion Wallace",
        [
            ("Spiritomb", 58),
            ("Roserade", 58),
            ("Gastrodon", 60),
            ("Lucario", 60),
            ("Milotic", 58),
            ("Garchomp", 62),
        ],
        display_name="Cynthia",
        gender="Female",
        tag="Sinnoh Champion",
    )

    open_cynthia_elevator()

    # Cynthia's room — Platinum coords: south (8,18), north (8,2), Cynthia (8,11)
    stitch("PokemonLeague_Sinnoh_CynthiasRoom", CYNTHIA)
    write_map(
        "PokemonLeague_Sinnoh_CynthiasRoom",
        {
            "id": "MAP_POKEMON_LEAGUE_SINNOH_CYNTHIAS_ROOM",
            "name": "PokemonLeague_Sinnoh_CynthiasRoom",
            "layout": "LAYOUT_POKEMON_LEAGUE_SINNOH_CYNTHIAS_ROOM",
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
            "object_events": [
                obj("OBJ_EVENT_GFX_WALLACE", 8, 11, "PokemonLeague_Sinnoh_CynthiasRoom_EventScript_Cynthia", movement="MOVEMENT_TYPE_FACE_DOWN"),
            ],
            "warp_events": [
                warp(8, 18, "MAP_POKEMON_LEAGUE_ELEVATOR_TO_CYNTHIA", 1),  # 0 south
                warp(8, 2, "MAP_POKEMON_LEAGUE_SINNOH_HALLWAY_TO_HO_F", 0),  # 1 north (post-win)
            ],
            "coord_events": [],
            "bg_events": [],
        },
        r"""PokemonLeague_Sinnoh_CynthiasRoom_MapScripts::
	.byte 0

PokemonLeague_Sinnoh_CynthiasRoom_EventScript_Cynthia::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_CHAMPION_CYNTHIA, PokemonLeague_Sinnoh_CynthiasRoom_EventScript_PostBattle
	playbgm MUS_ENCOUNTER_CHAMPION, FALSE
	msgbox PokemonLeague_Sinnoh_CynthiasRoom_Text_Intro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_CHAMPION_CYNTHIA, PokemonLeague_Sinnoh_CynthiasRoom_Text_Defeat
	goto PokemonLeague_Sinnoh_CynthiasRoom_EventScript_Defeated
	end

PokemonLeague_Sinnoh_CynthiasRoom_EventScript_Defeated::
	setflag FLAG_DEFEATED_CHAMPION_CYNTHIA
	msgbox PokemonLeague_Sinnoh_CynthiasRoom_Text_After, MSGBOX_DEFAULT
	closemessage
	warp MAP_POKEMON_LEAGUE_SINNOH_HALLWAY_TO_HO_F, 5, 22
	waitstate
	release
	end

PokemonLeague_Sinnoh_CynthiasRoom_EventScript_PostBattle::
	msgbox PokemonLeague_Sinnoh_CynthiasRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_Sinnoh_CynthiasRoom_Text_Intro:
	.string "I am CYNTHIA, the Pokemon League\n"
	.string "Champion of Sinnoh.\p"
	.string "I have longed for a challenger who\n"
	.string "could share this stage with me.\p"
	.string "Come. Show me the bonds you forged\n"
	.string "on your journey.$"

PokemonLeague_Sinnoh_CynthiasRoom_Text_Defeat:
	.string "That was splendid...\n"
	.string "Truly splendid.$"

PokemonLeague_Sinnoh_CynthiasRoom_Text_After:
	.string "You are a worthy Champion.\n"
	.string "Walk with me to the Hall of Fame.$"
""",
    )

    # Hallway — Platinum: south (5,23) from champ, north (5,2) to HoF
    stitch("PokemonLeague_Sinnoh_HallwayToHoF", HALLWAY)
    write_map(
        "PokemonLeague_Sinnoh_HallwayToHoF",
        {
            "id": "MAP_POKEMON_LEAGUE_SINNOH_HALLWAY_TO_HO_F",
            "name": "PokemonLeague_Sinnoh_HallwayToHoF",
            "layout": "LAYOUT_POKEMON_LEAGUE_SINNOH_HALLWAY_TO_HO_F",
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
            "object_events": [
                obj("OBJ_EVENT_GFX_WALLACE", 5, 20, "PokemonLeague_Sinnoh_HallwayToHoF_EventScript_Cynthia", movement="MOVEMENT_TYPE_FACE_UP"),
            ],
            "warp_events": [
                warp(5, 23, "MAP_POKEMON_LEAGUE_SINNOH_CYNTHIAS_ROOM", 1),  # 0
                warp(5, 2, "MAP_POKEMON_LEAGUE_SINNOH_HALL_OF_FAME", 0),  # 1
            ],
            "coord_events": [],
            "bg_events": [],
        },
        r"""PokemonLeague_Sinnoh_HallwayToHoF_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, PokemonLeague_Sinnoh_HallwayToHoF_OnFrame
	.byte 0

PokemonLeague_Sinnoh_HallwayToHoF_OnFrame:
	map_script_2 VAR_TEMP_1, 0, PokemonLeague_Sinnoh_HallwayToHoF_EventScript_LeadIn
	.2byte 0

PokemonLeague_Sinnoh_HallwayToHoF_EventScript_LeadIn::
	lockall
	setvar VAR_TEMP_1, 1
	applymovement LOCALID_PLAYER, PokemonLeague_Sinnoh_HallwayToHoF_Movement_WalkNorth
	waitmovement 0
	msgbox PokemonLeague_Sinnoh_HallwayToHoF_Text_Lead, MSGBOX_DEFAULT
	closemessage
	warp MAP_POKEMON_LEAGUE_SINNOH_HALL_OF_FAME, 8, 14
	waitstate
	releaseall
	end

PokemonLeague_Sinnoh_HallwayToHoF_EventScript_Cynthia::
	msgbox PokemonLeague_Sinnoh_HallwayToHoF_Text_Lead, MSGBOX_NPC
	end

PokemonLeague_Sinnoh_HallwayToHoF_Movement_WalkNorth:
	walk_up
	walk_up
	walk_up
	step_end

PokemonLeague_Sinnoh_HallwayToHoF_Text_Lead:
	.string "This hall honors every Champion who\n"
	.string "stood where you stand now.\p"
	.string "Come. The Hall of Fame awaits.$"
""",
    )

    # Hall of Fame — Platinum south warp (8,15); triggers GameClear / credits
    stitch("PokemonLeague_Sinnoh_HallOfFame", HOF)
    write_map(
        "PokemonLeague_Sinnoh_HallOfFame",
        {
            "id": "MAP_POKEMON_LEAGUE_SINNOH_HALL_OF_FAME",
            "name": "PokemonLeague_Sinnoh_HallOfFame",
            "layout": "LAYOUT_POKEMON_LEAGUE_SINNOH_HALL_OF_FAME",
            "music": "MUS_HALL_OF_FAME",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_POKEMON_LEAGUE",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": False,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [
                obj("OBJ_EVENT_GFX_WALLACE", 9, 6, "PokemonLeague_Sinnoh_HallOfFame_EventScript_Cynthia", movement="MOVEMENT_TYPE_FACE_DOWN"),
                obj("OBJ_EVENT_GFX_PROF_BIRCH", 7, 6, "PokemonLeague_Sinnoh_HallOfFame_EventScript_Rowan", movement="MOVEMENT_TYPE_FACE_DOWN"),
            ],
            "warp_events": [
                warp(8, 15, "MAP_POKEMON_LEAGUE_SINNOH_HALLWAY_TO_HO_F", 1),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        r"""PokemonLeague_Sinnoh_HallOfFame_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, PokemonLeague_Sinnoh_HallOfFame_OnFrame
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, PokemonLeague_Sinnoh_HallOfFame_OnWarp
	.byte 0

PokemonLeague_Sinnoh_HallOfFame_OnWarp:
	map_script_2 VAR_TEMP_1, 0, PokemonLeague_Sinnoh_HallOfFame_EventScript_FaceNorth
	.2byte 0

PokemonLeague_Sinnoh_HallOfFame_EventScript_FaceNorth::
	turnobject LOCALID_PLAYER, DIR_NORTH
	end

PokemonLeague_Sinnoh_HallOfFame_OnFrame:
	map_script_2 VAR_TEMP_1, 0, PokemonLeague_Sinnoh_HallOfFame_EventScript_Enter
	.2byte 0

PokemonLeague_Sinnoh_HallOfFame_EventScript_Enter::
	lockall
	applymovement LOCALID_PLAYER, PokemonLeague_Sinnoh_HallOfFame_Movement_Approach
	waitmovement 0
	msgbox PokemonLeague_Sinnoh_HallOfFame_Text_Honor, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	delay 20
	dofieldeffect FLDEFF_HALL_OF_FAME_RECORD
	waitfieldeffect FLDEFF_HALL_OF_FAME_RECORD
	delay 40
	setvar VAR_TEMP_1, 1
	setflag FLAG_DEFEATED_CHAMPION_CYNTHIA
	setflag FLAG_SYS_GAME_CLEAR
	call EverGrandeCity_HallOfFame_EventScript_SetGameClearFlags
	msgbox PokemonLeague_Sinnoh_HallOfFame_Text_Recorded, MSGBOX_DEFAULT
	closemessage
	fadescreenspeed FADE_TO_BLACK, 24
	special GameClear
	releaseall
	end

PokemonLeague_Sinnoh_HallOfFame_EventScript_Cynthia::
	msgbox PokemonLeague_Sinnoh_HallOfFame_Text_Honor, MSGBOX_NPC
	end

PokemonLeague_Sinnoh_HallOfFame_EventScript_Rowan::
	msgbox PokemonLeague_Sinnoh_HallOfFame_Text_Rowan, MSGBOX_NPC
	end

PokemonLeague_Sinnoh_HallOfFame_Movement_Approach:
	walk_up
	walk_up
	walk_up
	walk_up
	step_end

PokemonLeague_Sinnoh_HallOfFame_Text_Honor:
	.string "Here we honor League Champions and\n"
	.string "the Pokemon who walked beside them.$"

PokemonLeague_Sinnoh_HallOfFame_Text_Recorded:
	.string "Your names are recorded forever.\n"
	.string "Congratulations, Champion.$"

PokemonLeague_Sinnoh_HallOfFame_Text_Rowan:
	.string "Fascinating... Your journey will shape\n"
	.string "Sinnoh's next chapter of research.$"
""",
    )

    indoor = [
        "PokemonLeague_Sinnoh_CynthiasRoom",
        "PokemonLeague_Sinnoh_HallwayToHoF",
        "PokemonLeague_Sinnoh_HallOfFame",
    ]
    register_maps([], indoor, "gMapGroup_IndoorM31Champion")
    scrub(indoor + ["PokemonLeague_Elevator_ToCynthia"])
    print("M30 Champion / Hall of Fame build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
