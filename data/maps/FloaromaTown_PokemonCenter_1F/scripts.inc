FloaromaTown_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FloaromaTown_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

FloaromaTown_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_FLOAROMA_TOWN
	end

FloaromaTown_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_FLOAROMA_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

FloaromaTown_PokemonCenter_1F_EventScript_Girl::
	msgbox FloaromaTown_PokemonCenter_1F_Text_Girl, MSGBOX_NPC
	end

FloaromaTown_PokemonCenter_1F_EventScript_OldMan::
	msgbox FloaromaTown_PokemonCenter_1F_Text_OldMan, MSGBOX_NPC
	end

FloaromaTown_PokemonCenter_1F_Text_Girl:
	.string "The flowers outside smell so nice,\n"
	.string "even from in here!$"

FloaromaTown_PokemonCenter_1F_Text_OldMan:
	.string "A quiet town is a gift. Don't rush\n"
	.string "through it like the city folk do.$"
