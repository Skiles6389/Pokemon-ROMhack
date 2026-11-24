PastoriaCity_MoveReminderHouse_MapScripts::
	.byte 0

PastoriaCity_MoveReminderHouse_EventScript_MoveReminder::
	lock
	faceplayer
	msgbox PastoriaCity_MoveReminderHouse_Text_MoveReminderIntro, MSGBOX_DEFAULT
	goto Common_EventScript_MoveRelearner

PastoriaCity_MoveReminderHouse_Text_MoveReminderIntro:
	.string "I help POKéMON remember moves\n"
	.string "they've grown past.\p"
	.string "Pick a partner and we'll dig\n"
	.string "through their memories!$"

PastoriaCity_MoveReminderHouse_EventScript_Child::
	msgbox PastoriaCity_MoveReminderHouse_Text_Child, MSGBOX_NPC
	end

PastoriaCity_MoveReminderHouse_Text_Child:
	.string "Grandpa's stories are longer than\n"
	.string "the marsh boardwalk!$"
