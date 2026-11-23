OreburghCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OreburghCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

OreburghCity_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_OREBURGH_CITY
	end

OreburghCity_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_OREBURGH_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

OreburghCity_PokemonCenter_1F_EventScript_Worker::
	msgbox OreburghCity_PokemonCenter_1F_Text_Worker, MSGBOX_NPC
	end

OreburghCity_PokemonCenter_1F_EventScript_Lass::
	msgbox OreburghCity_PokemonCenter_1F_Text_Lass, MSGBOX_NPC
	end

OreburghCity_PokemonCenter_1F_Text_Worker:
	.string "After a long shift, my GEODUDE and\n"
	.string "I come here to rest up.$"

OreburghCity_PokemonCenter_1F_Text_Lass:
	.string "Water and Grass moves hit rock\n"
	.string "POKéMON hard. Just saying!$"
