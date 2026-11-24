PokemonLeague_LuciansRoom_MapScripts::
	.byte 0

PokemonLeague_LuciansRoom_EventScript_Leader::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_ELITE_FOUR_LUCIAN, PokemonLeague_LuciansRoom_EventScript_PostBattle
	playbgm MUS_ENCOUNTER_ELITE_FOUR, FALSE
	msgbox PokemonLeague_LuciansRoom_Text_Intro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_ELITE_FOUR_LUCIAN, PokemonLeague_LuciansRoom_Text_Defeat
	goto PokemonLeague_LuciansRoom_EventScript_Defeated
	end

PokemonLeague_LuciansRoom_EventScript_Defeated::
	setflag FLAG_DEFEATED_ELITE_FOUR_LUCIAN
	msgbox PokemonLeague_LuciansRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_LuciansRoom_EventScript_PostBattle::
	msgbox PokemonLeague_LuciansRoom_Text_After, MSGBOX_DEFAULT
	release
	end

PokemonLeague_LuciansRoom_EventScript_DoorGuard::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_ELITE_FOUR_LUCIAN, PokemonLeague_LuciansRoom_EventScript_DoorOpen
	msgbox PokemonLeague_LuciansRoom_Text_DoorClosed, MSGBOX_DEFAULT
	release
	end

PokemonLeague_LuciansRoom_EventScript_DoorOpen::
	msgbox PokemonLeague_LuciansRoom_Text_DoorOpen, MSGBOX_DEFAULT
	release
	end

PokemonLeague_LuciansRoom_Text_Intro:
	.string "I am LUCIAN of the ELITE FOUR.\nPsychic Pokemon read every move.\pShall we begin a battle of minds?$"

PokemonLeague_LuciansRoom_Text_Defeat:
	.string "Your spirit outpaces my reading...$"

PokemonLeague_LuciansRoom_Text_After:
	.string "Beyond lies the Champion's chamber.\nWin there, and the Hall of Fame awaits.$"

PokemonLeague_LuciansRoom_Text_DoorClosed:
	.string "The path ahead stays sealed until you\n"
	.string "defeat the Elite Four member here.$"

PokemonLeague_LuciansRoom_Text_DoorOpen:
	.string "The final elevator leads toward the Champion.$"
