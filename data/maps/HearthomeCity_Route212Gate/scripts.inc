HearthomeCity_Route212Gate_MapScripts::
	.byte 0

HearthomeCity_Route212Gate_EventScript_Guard::
	goto_if_set FLAG_BADGE05_GET, HearthomeCity_Route212Gate_EventScript_GuardOpen
	msgbox HearthomeCity_Route212Gate_Text_Guard, MSGBOX_NPC
	end

HearthomeCity_Route212Gate_EventScript_GuardOpen::
	msgbox HearthomeCity_Route212Gate_Text_GuardOpen, MSGBOX_NPC
	end

HearthomeCity_Route212Gate_EventScript_NeedFen::
	goto_if_set FLAG_BADGE05_GET, HearthomeCity_Route212Gate_EventScript_Open
HearthomeCity_Route212Gate_EventScript_Closed::
	lockall
	msgbox HearthomeCity_Route212Gate_Text_Closed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route212Gate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_Route212Gate_EventScript_Open::
	releaseall
	end

HearthomeCity_Route212Gate_Movement_Push:
	walk_left
	step_end

HearthomeCity_Route212Gate_Text_Guard:
	.string "Route 212 stretches south from here.\n"
	.string "Bring a Fen Badge before you try it.$"

HearthomeCity_Route212Gate_Text_GuardOpen:
	.string "Fen Badge, hm? The marsh road is\n"
	.string "yours to walk.$"

HearthomeCity_Route212Gate_Text_Closed:
	.string "Hold it. Marsh country is no place\n"
	.string "for trainers without a Fen Badge.$"
