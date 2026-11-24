HearthomeCity_Route209Gate_MapScripts::
	.byte 0

HearthomeCity_Route209Gate_EventScript_Guard::
	msgbox HearthomeCity_Route209Gate_Text_Guard, MSGBOX_NPC
	end

HearthomeCity_Route209Gate_EventScript_CheckProgress::
	lockall
	goto_if_unset FLAG_BADGE03_GET, HearthomeCity_Route209Gate_EventScript_NeedBadge
	goto_if_unset FLAG_HIDE_HEARTHOME_BARRY, HearthomeCity_Route209Gate_EventScript_NeedBarry
	msgbox HearthomeCity_Route209Gate_Text_ComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route209Gate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_Route209Gate_EventScript_NeedBadge::
	msgbox HearthomeCity_Route209Gate_Text_NeedBadge, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route209Gate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_Route209Gate_EventScript_NeedBarry::
	msgbox HearthomeCity_Route209Gate_Text_NeedBarry, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Route209Gate_Movement_Push
	waitmovement 0
	releaseall
	end

HearthomeCity_Route209Gate_Movement_Push:
	walk_left
	step_end

HearthomeCity_Route209Gate_Text_Guard:
	.string "Route 209 leads toward Solaceon Town.\n"
	.string "Beat FANTINA and BARRY first!$"

HearthomeCity_Route209Gate_Text_NeedBadge:
	.string "You need the Relic Badge from FANTINA\n"
	.string "before heading to Route 209.$"

HearthomeCity_Route209Gate_Text_NeedBarry:
	.string "BARRY is waiting just outside!\n"
	.string "You should settle that rivalry first.$"

HearthomeCity_Route209Gate_Text_ComingSoon:
	.string "Route 209 and Solaceon Town coming\n"
	.string "in the next milestone!$"
