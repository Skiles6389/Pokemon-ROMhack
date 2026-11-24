EternaCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, EternaCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

EternaCity_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_ETERNA_CITY
	end

EternaCity_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_ETERNA_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

EternaCity_PokemonCenter_1F_EventScript_Woman::
	msgbox EternaCity_PokemonCenter_1F_Text_Woman, MSGBOX_NPC
	end

EternaCity_PokemonCenter_1F_EventScript_Man::
	msgbox EternaCity_PokemonCenter_1F_Text_Man, MSGBOX_NPC
	end

EternaCity_PokemonCenter_1F_Text_Woman:
	.string "Eterna's so green and peaceful.\n"
	.string "Perfect for raising Pokémon.$"

EternaCity_PokemonCenter_1F_Text_Man:
	.string "The underground man nearby trades\n"
	.string "funny spheres and stat boosts.$"
