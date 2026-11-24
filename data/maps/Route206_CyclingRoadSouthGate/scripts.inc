Route206_CyclingRoadSouthGate_MapScripts::
	.byte 0

Route206_CyclingRoadSouthGate_EventScript_Clerk::
	msgbox Route206_CyclingRoadSouthGate_Text_Clerk, MSGBOX_NPC
	end

Route206_CyclingRoadSouthGate_EventScript_BikeCheck::
	lockall
	checkitem ITEM_BICYCLE
	goto_if_eq VAR_RESULT, FALSE, Route206_CyclingRoadSouthGate_EventScript_NoBike
	specialvar VAR_RESULT, GetPlayerAvatarBike
	goto_if_eq VAR_RESULT, 0, Route206_CyclingRoadSouthGate_EventScript_NoBike
	setflag FLAG_SYS_CYCLING_ROAD
	setvar VAR_TEMP_1, 1
	releaseall
	end

Route206_CyclingRoadSouthGate_EventScript_NoBike::
	msgbox Route206_CyclingRoadSouthGate_Text_NoBike, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route206_CyclingRoadSouthGate_Movement_PushWest
	waitmovement 0
	releaseall
	end

Route206_CyclingRoadSouthGate_EventScript_ClearCyclingRoad::
	lockall
	clearflag FLAG_SYS_CYCLING_ROAD
	setvar VAR_TEMP_1, 0
	releaseall
	end

Route206_CyclingRoadSouthGate_Movement_PushWest:
	walk_left
	step_end

Route206_CyclingRoadSouthGate_Text_Clerk:
	.string "You're almost at Route 207.\n"
	.string "Watch your speed on the slope!$"
Route206_CyclingRoadSouthGate_Text_NoBike:
	.string "Sorry, you can't walk on CYCLING\n"
	.string "ROAD. Please come back with a BIKE.$"
