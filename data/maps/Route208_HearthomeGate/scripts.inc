Route208_HearthomeGate_MapScripts::
	.byte 0

Route208_HearthomeGate_EventScript_Guard::
	msgbox Route208_HearthomeGate_Text_Guard, MSGBOX_NPC
	end

Route208_HearthomeGate_EventScript_HearthomeClosed::
	lockall
	msgbox Route208_HearthomeGate_Text_Closed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route208_HearthomeGate_Movement_PushWest
	waitmovement 0
	releaseall
	end

Route208_HearthomeGate_Movement_PushWest:
	walk_left
	step_end

Route208_HearthomeGate_Text_Guard:
	.string "Hearthome City is just ahead.\n"
	.string "Come back soon!$"
Route208_HearthomeGate_Text_Closed:
	.string "Hearthome City coming in the next\n"
	.string "milestone!$"
