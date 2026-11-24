VeilstoneCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VeilstoneCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

VeilstoneCity_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_VEILSTONE_CITY
	end

VeilstoneCity_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_VEILSTONE_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

VeilstoneCity_PokemonCenter_1F_EventScript_BlackBelt::
	msgbox VeilstoneCity_PokemonCenter_1F_Text_BlackBelt, MSGBOX_NPC
	end

VeilstoneCity_PokemonCenter_1F_Text_BlackBelt:
	.string "I train from dawn till dusk, then\n"
	.string "nurse my bruises here.\p"
	.string "The nurse never complains!$"

VeilstoneCity_PokemonCenter_1F_EventScript_Girl::
	msgbox VeilstoneCity_PokemonCenter_1F_Text_Girl, MSGBOX_NPC
	end

VeilstoneCity_PokemonCenter_1F_Text_Girl:
	.string "Veilstone's Gym Leader is a lot\n"
	.string "tougher than she looks!$"
