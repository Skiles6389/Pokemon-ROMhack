PastoriaCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PastoriaCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

PastoriaCity_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_PASTORIA_CITY
	end

PastoriaCity_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_PASTORIA_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

PastoriaCity_PokemonCenter_1F_EventScript_Fisherman::
	msgbox PastoriaCity_PokemonCenter_1F_Text_Fisherman, MSGBOX_NPC
	end

PastoriaCity_PokemonCenter_1F_Text_Fisherman:
	.string "I healed my team after a marsh\n"
	.string "mud bath. The nurse didn't blink.$"

PastoriaCity_PokemonCenter_1F_EventScript_Girl::
	msgbox PastoriaCity_PokemonCenter_1F_Text_Girl, MSGBOX_NPC
	end

PastoriaCity_PokemonCenter_1F_Text_Girl:
	.string "CRASHER WAKE's Gym is soaked!\n"
	.string "Pack towels and Thunderbolts.$"
