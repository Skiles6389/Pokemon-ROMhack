HearthomeCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, HearthomeCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

HearthomeCity_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_HEARTHOME_CITY
	end

HearthomeCity_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_HEARTHOME_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

HearthomeCity_PokemonCenter_1F_EventScript_Woman::
	msgbox HearthomeCity_PokemonCenter_1F_Text_Woman, MSGBOX_NPC
	end

HearthomeCity_PokemonCenter_1F_EventScript_Boy::
	msgbox HearthomeCity_PokemonCenter_1F_Text_Boy, MSGBOX_NPC
	end

HearthomeCity_PokemonCenter_1F_Text_Woman:
	.string "White-out returns you here safely.\n"
	.string "Nurse Joy never freezes up on us!$"

HearthomeCity_PokemonCenter_1F_Text_Boy:
	.string "I'm resting before FANTINA's Gym.\n"
	.string "Ghost types give me the shivers!$"
