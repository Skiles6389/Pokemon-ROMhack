TwinleafTown_PlayersHouse_2F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, TwinleafTown_PlayersHouse_2F_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, TwinleafTown_PlayersHouse_2F_OnFrame
	.byte 0

TwinleafTown_PlayersHouse_2F_OnTransition:
	setrespawn HEAL_LOCATION_TWINLEAF_TOWN_PLAYERSHOUSE_2F
	end

TwinleafTown_PlayersHouse_2F_OnFrame:
	map_script_2 VAR_TEMP_0, 0, TwinleafTown_PlayersHouse_2F_EventScript_TryOpeningNews
	.2byte 0

@ Platinum-style opening: first time in the bedroom, the TV is already on with news.
TwinleafTown_PlayersHouse_2F_EventScript_TryOpeningNews::
	setvar VAR_TEMP_0, 1
	goto_if_set FLAG_SYS_TV_START, TwinleafTown_PlayersHouse_2F_EventScript_NewsDone
	lockall
	msgbox TwinleafTown_PlayersHouse_2F_Text_TVNewsStorm, MSGBOX_DEFAULT
	msgbox TwinleafTown_PlayersHouse_2F_Text_TVNewsGyarados, MSGBOX_DEFAULT
	closemessage
	setflag FLAG_SYS_TV_START
	releaseall
	end

TwinleafTown_PlayersHouse_2F_EventScript_NewsDone::
	end

TwinleafTown_PlayersHouse_2F_EventScript_PC::
	lockall
	setvar VAR_0x8004, PC_LOCATION_BRENDANS_HOUSE
	special DoPCTurnOnEffect
	playse SE_PC_ON
	msgbox gText_PlayerHouseBootPC, MSGBOX_DEFAULT
	special BedroomPC
	releaseall
	end

TwinleafTown_PlayersHouse_2F_EventScript_TurnOffPC::
	setvar VAR_0x8004, PC_LOCATION_BRENDANS_HOUSE
	playse SE_PC_OFF
	special DoPCTurnOffEffect
	releaseall
	end

TwinleafTown_PlayersHouse_2F_EventScript_TV::
	lockall
	goto_if_set FLAG_SYS_TV_START, TwinleafTown_PlayersHouse_2F_EventScript_TVReplay
	msgbox TwinleafTown_PlayersHouse_2F_Text_TVNewsStorm, MSGBOX_DEFAULT
	msgbox TwinleafTown_PlayersHouse_2F_Text_TVNewsGyarados, MSGBOX_DEFAULT
	setflag FLAG_SYS_TV_START
	releaseall
	end

TwinleafTown_PlayersHouse_2F_EventScript_TVReplay::
	msgbox TwinleafTown_PlayersHouse_2F_Text_TVReplay, MSGBOX_DEFAULT
	releaseall
	end

TwinleafTown_PlayersHouse_2F_Text_TVNewsStorm:
	.string "A news report is playing.\p"
	.string "“…and a sudden storm rolled over the\n"
	.string "lakes last night, scattering boats\l"
	.string "and knocking out power lines.”$"

TwinleafTown_PlayersHouse_2F_Text_TVNewsGyarados:
	.string "“Witnesses near the shore claim they\n"
	.string "saw a red GYARADOS thrashing in the\l"
	.string "waves before vanishing into the fog.\p"
	.string "Authorities ask travelers to stay\n"
	.string "clear of the water until morning.”\p"
	.string "…The broadcast fades to static.$"

TwinleafTown_PlayersHouse_2F_Text_TVReplay:
	.string "The same news report is looping.\n"
	.string "A red GYARADOS… and a wild storm.$"
