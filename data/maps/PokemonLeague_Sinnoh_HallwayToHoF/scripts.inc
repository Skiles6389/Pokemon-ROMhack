PokemonLeague_Sinnoh_HallwayToHoF_MapScripts::
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
