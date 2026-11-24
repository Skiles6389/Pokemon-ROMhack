PokemonLeague_Exterior_MapScripts::
	.byte 0

PokemonLeague_Exterior_EventScript_Npc0::
	msgbox PokemonLeague_Exterior_EventScript_Npc0_Text, MSGBOX_NPC
	end

PokemonLeague_Exterior_EventScript_Npc0_Text:
	.string "The Pokemon League waits at the summit.\n"
	.string "Only trainers with eight badges pass.$"

PokemonLeague_Exterior_EventScript_Npc1::
	msgbox PokemonLeague_Exterior_EventScript_Npc1_Text, MSGBOX_NPC
	end

PokemonLeague_Exterior_EventScript_Npc1_Text:
	.string "The Pokemon League waits at the summit.\n"
	.string "Only trainers with eight badges pass.$"

PokemonLeague_Exterior_EventScript_E4Closed::
	lock
	faceplayer
	setflag FLAG_REACHED_POKEMON_LEAGUE_DOOR
	msgbox PokemonLeague_Exterior_Text_E4Closed, MSGBOX_DEFAULT
	release
	end

PokemonLeague_Exterior_Text_E4Closed:
	.string "The Elite Four hall is sealed for now.\n"
	.string "You have reached the League door -\l"
	.string "the challenge opens in a later chapter.$"

