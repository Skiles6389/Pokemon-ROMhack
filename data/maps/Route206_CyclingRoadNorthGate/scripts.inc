Route206_CyclingRoadNorthGate_MapScripts::
	.byte 0

Route206_CyclingRoadNorthGate_EventScript_Clerk::
	msgbox Route206_CyclingRoadNorthGate_Text_Clerk, MSGBOX_NPC
	end

Route206_CyclingRoadNorthGate_EventScript_BikeCheck::
	lockall
	checkitem ITEM_BICYCLE
	goto_if_eq VAR_RESULT, FALSE, Route206_CyclingRoadNorthGate_EventScript_NoBikeOwned
	specialvar VAR_RESULT, GetPlayerAvatarBike
	goto_if_eq VAR_RESULT, 0, Route206_CyclingRoadNorthGate_EventScript_NotRiding
	setflag FLAG_SYS_CYCLING_ROAD
	setvar VAR_TEMP_1, 1
	releaseall
	end

Route206_CyclingRoadNorthGate_EventScript_NoBikeOwned::
	msgbox Route206_CyclingRoadNorthGate_Text_NoBike, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route206_CyclingRoadNorthGate_Movement_PushWest
	waitmovement 0
	releaseall
	end

Route206_CyclingRoadNorthGate_EventScript_NotRiding::
	msgbox Route206_CyclingRoadNorthGate_Text_GetOnBike, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route206_CyclingRoadNorthGate_Movement_PushWest
	waitmovement 0
	releaseall
	end

Route206_CyclingRoadNorthGate_EventScript_ClearCyclingRoad::
	lockall
	clearflag FLAG_SYS_CYCLING_ROAD
	setvar VAR_TEMP_1, 0
	releaseall
	end

Route206_CyclingRoadNorthGate_Movement_PushWest:
	walk_left
	step_end

Route206_CyclingRoadNorthGate_Text_Clerk:
	.string "On CYCLING ROAD, you can go all out\n"
	.string "and cycle as fast as you'd like.\pIt feels great to go that fast, but try\p"
	.string "not to crash into anyone!$"
Route206_CyclingRoadNorthGate_Text_NoBike:
	.string "Sorry, you can't walk on CYCLING\n"
	.string "ROAD. It's too dangerous.\pPlease come back with a BIKE.\p"
	.string "There's a Cycle Shop in Eterna City!$"
Route206_CyclingRoadNorthGate_Text_GetOnBike:
	.string "Please get on your BIKE before\n"
	.string "entering CYCLING ROAD!$"
