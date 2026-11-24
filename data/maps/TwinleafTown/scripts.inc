TwinleafTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, TwinleafTown_OnTransition
	.byte 0

TwinleafTown_OnTransition:
	setflag FLAG_VISITED_TWINLEAF_TOWN
	end

TwinleafTown_EventScript_Boy::
	msgbox TwinleafTown_Text_Boy, MSGBOX_NPC
	end

TwinleafTown_EventScript_Girl::
	msgbox TwinleafTown_Text_Girl, MSGBOX_NPC
	end

TwinleafTown_EventScript_Woman::
	msgbox TwinleafTown_Text_Woman, MSGBOX_NPC
	end

TwinleafTown_EventScript_TownSign::
	msgbox TwinleafTown_Text_TownSign, MSGBOX_SIGN
	end

TwinleafTown_EventScript_PlayersHouseSign::
	msgbox TwinleafTown_Text_PlayersHouseSign, MSGBOX_SIGN
	end

TwinleafTown_EventScript_RivalsHouseSign::
	msgbox TwinleafTown_Text_RivalsHouseSign, MSGBOX_SIGN
	end

TwinleafTown_Text_Boy:
	.string "ROUTE 201 starts just north of here.\n"
	.string "It runs west toward the lake.$"

TwinleafTown_Text_Girl:
	.string "The water south of town is deep.\n"
	.string "Nobody goes in.$"

TwinleafTown_Text_Woman:
	.string "Welcome to TWINLEAF TOWN.\n"
	.string "It's small, but the breeze is nice.$"

TwinleafTown_Text_TownSign:
	.string "TWINLEAF TOWN\n"
	.string "A quiet start under an open sky.$"

TwinleafTown_Text_PlayersHouseSign:
	.string "{PLAYER}'s house$"

TwinleafTown_Text_RivalsHouseSign:
	.string "A neighbor's house$"
