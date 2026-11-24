PastoriaCity_GreatMarshGate_MapScripts::
	.byte 0

PastoriaCity_GreatMarshGate_EventScript_Reception::
	lock
	faceplayer
	goto_if_set FLAG_GOT_PASTORIA_HM_DEFOG, PastoriaCity_GreatMarshGate_EventScript_ReceptionAfter
	goto_if_unset FLAG_BADGE05_GET, PastoriaCity_GreatMarshGate_EventScript_ReceptionNoBadge
	msgbox PastoriaCity_GreatMarshGate_Text_OfferDefog, MSGBOX_DEFAULT
	giveitem ITEM_HM_DEFOG
	setflag FLAG_GOT_PASTORIA_HM_DEFOG
	msgbox PastoriaCity_GreatMarshGate_Text_ExplainDefog, MSGBOX_DEFAULT
	release
	end

PastoriaCity_GreatMarshGate_EventScript_ReceptionNoBadge::
	msgbox PastoriaCity_GreatMarshGate_Text_Reception, MSGBOX_DEFAULT
	release
	end

PastoriaCity_GreatMarshGate_EventScript_ReceptionAfter::
	msgbox PastoriaCity_GreatMarshGate_Text_ReceptionAfter, MSGBOX_DEFAULT
	release
	end

PastoriaCity_GreatMarshGate_Text_OfferDefog:
	.string "Fen Badge confirmed. The marsh fog\n"
	.string "bows to a proper gust-take this.$"

PastoriaCity_GreatMarshGate_Text_ExplainDefog:
	.string "HM05 Defog clears fog on the field\n"
	.string "and unsettles foes who hide behind it.$"

PastoriaCity_GreatMarshGate_Text_ReceptionAfter:
	.string "Watch your footing in the reeds.\n"
	.string "Safari work picks up after a clear sky.$"


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
	.string "Safari tours aren't open yet.\n"
	.string "The marsh trails stay closed.$"

PastoriaCity_GreatMarshGate_EventScript_Camper::
	msgbox PastoriaCity_GreatMarshGate_Text_Camper, MSGBOX_NPC
	end

PastoriaCity_GreatMarshGate_Text_Camper:
	.string "I packed binoculars for rare\n"
	.string "sightings. Patience is half the\l"
	.string "adventure!$"

PastoriaCity_GreatMarshGate_EventScript_EnterCheck::
	goto_if_set FLAG_GOT_PASTORIA_HM_DEFOG, PastoriaCity_GreatMarshGate_EventScript_AllowMarsh
	msgbox PastoriaCity_GreatMarshGate_Text_SafariComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, PastoriaCity_GreatMarshGate_Movement_PushSouth
	waitmovement 0
	releaseall
	end

PastoriaCity_GreatMarshGate_EventScript_AllowMarsh::
	releaseall
	end
