TwinleafTown_PlayersHouse_2F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, TwinleafTown_PlayersHouse_2F_OnTransition
	.byte 0

TwinleafTown_PlayersHouse_2F_OnTransition:
	setrespawn HEAL_LOCATION_TWINLEAF_TOWN_PLAYERSHOUSE_2F
	end

TwinleafTown_PlayersHouse_2F_EventScript_PC::
	msgbox TwinleafTown_PlayersHouse_2F_Text_PC, MSGBOX_SIGN
	end

TwinleafTown_PlayersHouse_2F_Text_PC:
	.string "It's a PC.$"
