PokemonLeague_FlintsRoom_MapScripts::
	.byte 0

PokemonLeague_FlintsRoom_EventScript_Leader::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_ELITE_FOUR_FLINT, PokemonLeague_FlintsRoom_EventScript_PostBattle
	playbgm MUS_ENCOUNTER_ELITE_FOUR, FALSE
	msgbox PokemonLeague_FlintsRoom_Text_Intro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_ELITE_FOUR_FLINT, PokemonLeague_FlintsRoom_Text_Defeat
	goto PokemonLeague_FlintsRoom_EventScript_Defeated
	end

PokemonLeague_FlintsRoom_EventScript_Defeated::
	setflag FLAG_DEFEATED_ELITE_FOUR_FLINT
	msgbox PokemonLeague_FlintsRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_FlintsRoom_EventScript_PostBattle::
	msgbox PokemonLeague_FlintsRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_FlintsRoom_EventScript_DoorGuard::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_ELITE_FOUR_FLINT, PokemonLeague_FlintsRoom_EventScript_DoorOpen
	msgbox PokemonLeague_FlintsRoom_Text_DoorClosed, MSGBOX_DEFAULT
	release
	end

PokemonLeague_FlintsRoom_EventScript_DoorOpen::
	msgbox PokemonLeague_FlintsRoom_Text_DoorOpen, MSGBOX_DEFAULT
	release
	end

PokemonLeague_FlintsRoom_Text_Intro:
	.string "I am FLINT of the ELITE FOUR!\nFire Pokemon torch every doubt!\pLet's see if you can take the heat!$"

PokemonLeague_FlintsRoom_Text_Defeat:
	.string "My flame... snuffed out.$"

PokemonLeague_FlintsRoom_Text_After:
	.string "Lucian waits with a calm mind.\nPsychic pressure ahead.$"

PokemonLeague_FlintsRoom_Text_DoorClosed:
	.string "The path ahead stays sealed until you\n"
	.string "defeat the Elite Four member here.$"

PokemonLeague_FlintsRoom_Text_DoorOpen:
	.string "The elevator ahead leads to Lucian.$"
