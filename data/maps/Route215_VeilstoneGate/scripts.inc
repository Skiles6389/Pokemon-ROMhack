Route215_VeilstoneGate_MapScripts::
	.byte 0

Route215_VeilstoneGate_EventScript_Guard::
	msgbox Route215_VeilstoneGate_Text_Guard, MSGBOX_NPC
	end

Route215_VeilstoneGate_EventScript_ComingSoon::
	lockall
	msgbox Route215_VeilstoneGate_Text_ComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route215_VeilstoneGate_Movement_Push
	waitmovement 0
	releaseall
	end

Route215_VeilstoneGate_Movement_Push:
	walk_left
	step_end

Route215_VeilstoneGate_Text_Guard:
	.string "Veilstone City is just beyond...\n"
	.string "when the road opens, that is.$"

Route215_VeilstoneGate_Text_ComingSoon:
	.string "Veilstone City coming in the next\n"
	.string "milestone!$"
