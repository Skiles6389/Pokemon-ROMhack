PokemonLeague_Elevator_ToCynthia_MapScripts::
	.byte 0

PokemonLeague_Elevator_ToCynthia_EventScript_Closed::
	lock
	faceplayer
	goto_if_unset FLAG_DEFEATED_ELITE_FOUR_LUCIAN, PokemonLeague_Elevator_ToCynthia_EventScript_NeedLucian
	msgbox PokemonLeague_Elevator_ToCynthia_Text_Closed, MSGBOX_DEFAULT
	release
	end

PokemonLeague_Elevator_ToCynthia_EventScript_NeedLucian::
	msgbox PokemonLeague_Elevator_ToCynthia_Text_NeedLucian, MSGBOX_DEFAULT
	release
	end

PokemonLeague_Elevator_ToCynthia_Text_NeedLucian:
	.string "Lucian still waits in his chamber.\n"
	.string "Defeat him before facing the Champion.$"

PokemonLeague_Elevator_ToCynthia_Text_Closed:
	.string "The Champion's chamber opens in the\n"
	.string "next League build. Rest here for now.$"
