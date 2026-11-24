PokemonLeague_Sinnoh_HallOfFame_MapScripts::
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
