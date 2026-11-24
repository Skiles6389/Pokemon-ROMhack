PokemonLeague_AaronsRoom_MapScripts::
	.byte 0

PokemonLeague_AaronsRoom_EventScript_Leader::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_ELITE_FOUR_AARON, PokemonLeague_AaronsRoom_EventScript_PostBattle
	playbgm MUS_ENCOUNTER_ELITE_FOUR, FALSE
	msgbox PokemonLeague_AaronsRoom_Text_Intro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_ELITE_FOUR_AARON, PokemonLeague_AaronsRoom_Text_Defeat
	goto PokemonLeague_AaronsRoom_EventScript_Defeated
	end

PokemonLeague_AaronsRoom_EventScript_Defeated::
	setflag FLAG_DEFEATED_ELITE_FOUR_AARON
	msgbox PokemonLeague_AaronsRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_AaronsRoom_EventScript_PostBattle::
	msgbox PokemonLeague_AaronsRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_AaronsRoom_EventScript_DoorGuard::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_ELITE_FOUR_AARON, PokemonLeague_AaronsRoom_EventScript_DoorOpen
	msgbox PokemonLeague_AaronsRoom_Text_DoorClosed, MSGBOX_DEFAULT
	release
	end

PokemonLeague_AaronsRoom_EventScript_DoorOpen::
	msgbox PokemonLeague_AaronsRoom_Text_DoorOpen, MSGBOX_DEFAULT
	release
	end

PokemonLeague_AaronsRoom_Text_Intro:
	.string "I am AARON of the ELITE FOUR.\nBug Pokemon are my pride.\pShow me a battle worth the League!$"

PokemonLeague_AaronsRoom_Text_Defeat:
	.string "My swarm... broken.$"

PokemonLeague_AaronsRoom_Text_After:
	.string "Bertha is next. Her Ground types\nshake the floor itself.$"

PokemonLeague_AaronsRoom_Text_DoorClosed:
	.string "The path ahead stays sealed until you\n"
	.string "defeat the Elite Four member here.$"

PokemonLeague_AaronsRoom_Text_DoorOpen:
	.string "The elevator ahead leads to Bertha.$"
