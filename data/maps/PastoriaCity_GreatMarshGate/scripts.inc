PastoriaCity_GreatMarshGate_MapScripts::
	.byte 0

PastoriaCity_GreatMarshGate_EventScript_Reception::
	lock
	faceplayer
	msgbox PastoriaCity_GreatMarshGate_Text_Reception, MSGBOX_DEFAULT
	release
	end

PastoriaCity_GreatMarshGate_EventScript_SafariComingSoon::
	lockall
	msgbox PastoriaCity_GreatMarshGate_Text_SafariComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, PastoriaCity_GreatMarshGate_Movement_PushSouth
	waitmovement 0
	releaseall
	end

PastoriaCity_GreatMarshGate_Movement_PushSouth:
	walk_down
	step_end

PastoriaCity_GreatMarshGate_Text_Reception:
	.string "Welcome to the Great Marsh desk!\p"
	.string "Safari tours aren't running yet,\n"
	.string "but grab a map and dream big.\p"
	.string "When the board opens, we'll hand\n"
	.string "out trail tips--and maybe a tidy\l"
	.string "field move for clearing fog.$"

PastoriaCity_GreatMarshGate_Text_SafariComingSoon:
	.string "Safari coming later!\n"
	.string "The marsh trails stay closed.$"

PastoriaCity_GreatMarshGate_EventScript_Camper::
	msgbox PastoriaCity_GreatMarshGate_Text_Camper, MSGBOX_NPC
	end

PastoriaCity_GreatMarshGate_Text_Camper:
	.string "I packed binoculars for rare\n"
	.string "sightings. Patience is half the\l"
	.string "adventure!$"
