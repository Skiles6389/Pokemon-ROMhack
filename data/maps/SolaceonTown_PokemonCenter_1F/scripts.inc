SolaceonTown_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SolaceonTown_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

SolaceonTown_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_SOLACEON_TOWN
	end

SolaceonTown_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_SOLACEON_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

SolaceonTown_PokemonCenter_1F_EventScript_Woman::
	msgbox SolaceonTown_PokemonCenter_1F_Text_Woman, MSGBOX_NPC
	end

SolaceonTown_PokemonCenter_1F_EventScript_Boy::
	msgbox SolaceonTown_PokemonCenter_1F_Text_Boy, MSGBOX_NPC
	end

SolaceonTown_PokemonCenter_1F_Text_Woman:
	.string "Day Care drop-offs make me nervous.\n"
	.string "I heal here first, every time.$"

SolaceonTown_PokemonCenter_1F_Text_Boy:
	.string "Lost Tower is creepy, but the\n"
	.string "elders up top are kind.$"
