VeilstoneCity_Route214Gate_MapScripts::
	.byte 0

VeilstoneCity_Route214Gate_EventScript_Guard::
	msgbox VeilstoneCity_Route214Gate_Text_Guard, MSGBOX_NPC
	end

VeilstoneCity_Route214Gate_EventScript_ComingSoon::
	lockall
	msgbox VeilstoneCity_Route214Gate_Text_ComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, VeilstoneCity_Route214Gate_Movement_Push
	waitmovement 0
	releaseall
	end

VeilstoneCity_Route214Gate_Movement_Push:
	walk_left
	step_end

VeilstoneCity_Route214Gate_Text_Guard:
	.string "Route 214 runs south along the\n"
	.string "marsh toward Pastoria City.\p"
	.string "The road isn't ready for travelers\n"
	.string "just yet.$"

VeilstoneCity_Route214Gate_Text_ComingSoon:
	.string "Route 214 and Pastoria City coming\n"
	.string "in the next milestone!$"
