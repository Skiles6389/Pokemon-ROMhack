HearthomeCity_AmitySquareEastGate_MapScripts::
	.byte 0

HearthomeCity_AmitySquareEastGate_EventScript_Guard::
	msgbox HearthomeCity_AmitySquareEastGate_Text_Guard, MSGBOX_NPC
	end

HearthomeCity_AmitySquareEastGate_EventScript_Closed::
	lockall
	msgbox HearthomeCity_AmitySquareEastGate_Text_Closed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_AmitySquareEastGate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_AmitySquareEastGate_Movement_Push:
	walk_left
	step_end

HearthomeCity_AmitySquareEastGate_Text_Guard:
	.string "Amity Square is a park for Trainers\n"
	.string "and their POKéMON.\p"
	.string "We're still preparing the grounds.$"

HearthomeCity_AmitySquareEastGate_Text_Closed:
	.string "Amity Square is closed for now.\n"
	.string "Please enjoy Hearthome City!$"
