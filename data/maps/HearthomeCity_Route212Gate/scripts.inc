HearthomeCity_Route212Gate_MapScripts::
	.byte 0

HearthomeCity_Route212Gate_EventScript_Guard::
	msgbox HearthomeCity_Route212Gate_Text_Guard, MSGBOX_NPC
	end

HearthomeCity_Route212Gate_EventScript_Closed::
	lockall
	msgbox HearthomeCity_Route212Gate_Text_Closed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route212Gate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_Route212Gate_Movement_Push:
	walk_left
	step_end

HearthomeCity_Route212Gate_Text_Guard:
	.string "Route 212 stretches south from here.\n"
	.string "It's not open in this demo yet.$"

HearthomeCity_Route212Gate_Text_Closed:
	.string "Route 212 isn't open yet.\n"
	.string "Please come back another time.$"
