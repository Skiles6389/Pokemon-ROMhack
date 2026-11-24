PokemonLeague_Sinnoh_CynthiasRoom_MapScripts::
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
