PokemonLeague_NorthPC_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PokemonLeague_NorthPC_OnTransition
	.byte 0

PokemonLeague_NorthPC_OnTransition::
	setrespawn HEAL_LOCATION_EVER_GRANDE_CITY_POKEMON_LEAGUE
	end

PokemonLeague_NorthPC_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

PokemonLeague_NorthPC_EventScript_Clerk::
	msgbox PokemonLeague_NorthPC_Text_Clerk, MSGBOX_NPC
	end

PokemonLeague_NorthPC_Text_Clerk:
	.string "Welcome to the Pokemon League.\n"
	.string "Heal up, then take the elevator north.\p"
	.string "Aaron of the Elite Four is first.$"
