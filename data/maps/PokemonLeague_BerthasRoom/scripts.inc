PokemonLeague_BerthasRoom_MapScripts::
	.byte 0

PokemonLeague_BerthasRoom_EventScript_Leader::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_ELITE_FOUR_BERTHA, PokemonLeague_BerthasRoom_EventScript_PostBattle
	playbgm MUS_ENCOUNTER_ELITE_FOUR, FALSE
	msgbox PokemonLeague_BerthasRoom_Text_Intro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_ELITE_FOUR_BERTHA, PokemonLeague_BerthasRoom_Text_Defeat
	goto PokemonLeague_BerthasRoom_EventScript_Defeated
	end

PokemonLeague_BerthasRoom_EventScript_Defeated::
	setflag FLAG_DEFEATED_ELITE_FOUR_BERTHA
	msgbox PokemonLeague_BerthasRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_BerthasRoom_EventScript_PostBattle::
	msgbox PokemonLeague_BerthasRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_BerthasRoom_EventScript_DoorGuard::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_ELITE_FOUR_BERTHA, PokemonLeague_BerthasRoom_EventScript_DoorOpen
	msgbox PokemonLeague_BerthasRoom_Text_DoorClosed, MSGBOX_DEFAULT
	release
	end

PokemonLeague_BerthasRoom_EventScript_DoorOpen::
	msgbox PokemonLeague_BerthasRoom_Text_DoorOpen, MSGBOX_DEFAULT
	release
	end

PokemonLeague_BerthasRoom_Text_Intro:
	.string "I am BERTHA of the ELITE FOUR.\nGround Pokemon endure every storm.\pCan you stand firm against them?$"

PokemonLeague_BerthasRoom_Text_Defeat:
	.string "So the earth can still shake...$"

PokemonLeague_BerthasRoom_Text_After:
	.string "Flint burns hotter than any forge.\nDo not blink.$"

PokemonLeague_BerthasRoom_Text_DoorClosed:
	.string "The path ahead stays sealed until you\n"
	.string "defeat the Elite Four member here.$"

PokemonLeague_BerthasRoom_Text_DoorOpen:
	.string "The elevator ahead leads to Flint.$"
