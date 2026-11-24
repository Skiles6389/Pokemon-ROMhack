SolaceonRuins_ExteriorGate_MapScripts::
	.byte 0

SolaceonRuins_ExteriorGate_EventScript_Guard::
	msgbox SolaceonRuins_ExteriorGate_Text_Guard, MSGBOX_NPC
	end

SolaceonRuins_ExteriorGate_EventScript_ComingSoon::
	lockall
	msgbox SolaceonRuins_ExteriorGate_Text_ComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, SolaceonRuins_ExteriorGate_Movement_Push
	waitmovement 0
	releaseall
	end

SolaceonRuins_ExteriorGate_Movement_Push:
	walk_left
	step_end

SolaceonRuins_ExteriorGate_Text_Guard:
	.string "Ruins access is limited.\n"
	.string "Researchers only, for now.$"

SolaceonRuins_ExteriorGate_Text_ComingSoon:
	.string "The ruins are closed to visitors\n"
	.string "for now.$"
