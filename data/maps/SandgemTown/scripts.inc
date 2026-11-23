SandgemTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SandgemTown_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SandgemTown_OnFrame
	.byte 0

SandgemTown_OnTransition:
	call SandgemTown_EventScript_SetAssistantGfx
	end

SandgemTown_EventScript_SetAssistantGfx::
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, SandgemTown_EventScript_SetDawnGfx
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL
	return

SandgemTown_EventScript_SetDawnGfx::
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_MAY_NORMAL
	return

SandgemTown_OnFrame:
	map_script_2 VAR_SANDGEM_STATE, 3, SandgemTown_EventScript_Tour
	.2byte 0

SandgemTown_EventScript_AssistantMeet::
	lockall
	call SandgemTown_EventScript_SetAssistantGfx
	applymovement LOCALID_SANDGEM_ASSISTANT, Common_Movement_FacePlayer
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, SandgemTown_EventScript_LucasMeet
	msgbox SandgemTown_Text_DawnMeet, MSGBOX_DEFAULT
	goto SandgemTown_EventScript_AssistantLead
	end

SandgemTown_EventScript_LucasMeet::
	msgbox SandgemTown_Text_LucasMeet, MSGBOX_DEFAULT
	goto SandgemTown_EventScript_AssistantLead
	end

SandgemTown_EventScript_AssistantLead::
	closemessage
	applymovement LOCALID_SANDGEM_ASSISTANT, SandgemTown_Movement_AssistantToLab
	waitmovement 0
	applymovement LOCALID_SANDGEM_ASSISTANT, Common_Movement_FaceUp
	waitmovement 0
	setvar VAR_SANDGEM_STATE, 1
	releaseall
	end

SandgemTown_EventScript_Assistant::
	lock
	faceplayer
	goto_if_ge VAR_SANDGEM_STATE, 4, SandgemTown_EventScript_AssistantFree
	goto_if_eq VAR_SANDGEM_STATE, 1, SandgemTown_EventScript_AssistantWaiting
	msgbox SandgemTown_Text_AssistantBusy, MSGBOX_DEFAULT
	release
	end

SandgemTown_EventScript_AssistantWaiting::
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, SandgemTown_EventScript_LucasWaiting
	msgbox SandgemTown_Text_DawnWaiting, MSGBOX_DEFAULT
	release
	end

SandgemTown_EventScript_LucasWaiting::
	msgbox SandgemTown_Text_LucasWaiting, MSGBOX_DEFAULT
	release
	end

SandgemTown_EventScript_AssistantFree::
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, SandgemTown_EventScript_LucasFree
	msgbox SandgemTown_Text_DawnFree, MSGBOX_DEFAULT
	release
	end

SandgemTown_EventScript_LucasFree::
	msgbox SandgemTown_Text_LucasFree, MSGBOX_DEFAULT
	release
	end

SandgemTown_EventScript_Tour::
	lockall
	call SandgemTown_EventScript_SetAssistantGfx
	setobjectxy LOCALID_SANDGEM_ASSISTANT, 7, 11
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterLeft
	applymovement LOCALID_SANDGEM_ASSISTANT, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, SandgemTown_EventScript_LucasCenter
	msgbox SandgemTown_Text_DawnCenter, MSGBOX_DEFAULT
	goto SandgemTown_EventScript_TourMart
	end

SandgemTown_EventScript_LucasCenter::
	msgbox SandgemTown_Text_LucasCenter, MSGBOX_DEFAULT
	goto SandgemTown_EventScript_TourMart
	end

SandgemTown_EventScript_TourMart::
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, SandgemTown_Movement_ToMart
	applymovement LOCALID_SANDGEM_ASSISTANT, SandgemTown_Movement_ToMart
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, SandgemTown_EventScript_LucasMart
	msgbox SandgemTown_Text_DawnMart, MSGBOX_DEFAULT
	goto SandgemTown_EventScript_BarryBump
	end

SandgemTown_EventScript_LucasMart::
	msgbox SandgemTown_Text_LucasMart, MSGBOX_DEFAULT
	goto SandgemTown_EventScript_BarryBump
	end

SandgemTown_EventScript_BarryBump::
	closemessage
	setobjectxyperm LOCALID_SANDGEM_BARRY, 26, 12
	clearflag FLAG_HIDE_SANDGEM_BARRY
	addobject LOCALID_SANDGEM_BARRY
	applymovement LOCALID_SANDGEM_BARRY, SandgemTown_Movement_BarryIn
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox SandgemTown_Text_BarryBump, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_SANDGEM_BARRY, SandgemTown_Movement_BarryLeave
	waitmovement 0
	removeobject LOCALID_SANDGEM_BARRY
	setflag FLAG_HIDE_SANDGEM_BARRY
	setvar VAR_SANDGEM_STATE, 4
	releaseall
	end

SandgemTown_EventScript_Barry::
	msgbox SandgemTown_Text_BarryLater, MSGBOX_NPC
	end

SandgemTown_EventScript_Boy::
	msgbox SandgemTown_Text_Boy, MSGBOX_NPC
	end

SandgemTown_EventScript_Woman::
	msgbox SandgemTown_Text_Woman, MSGBOX_NPC
	end

SandgemTown_EventScript_CenterSign::
	msgbox SandgemTown_Text_CenterSign, MSGBOX_SIGN
	end

SandgemTown_EventScript_MartSign::
	msgbox SandgemTown_Text_MartSign, MSGBOX_SIGN
	end

SandgemTown_EventScript_LabSign::
	msgbox SandgemTown_Text_LabSign, MSGBOX_SIGN
	end

SandgemTown_EventScript_Route202Sign::
	msgbox SandgemTown_Text_Route202Sign, MSGBOX_SIGN
	end

SandgemTown_EventScript_Route219Sign::
	msgbox SandgemTown_Text_Route219Sign, MSGBOX_SIGN
	end

SandgemTown_Movement_AssistantToLab:
	walk_fast_right
	walk_fast_up
	walk_fast_up
	step_end

SandgemTown_Movement_ToMart:
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

SandgemTown_Movement_BarryIn:
	walk_fast_right
	face_up
	step_end

SandgemTown_Movement_BarryLeave:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

SandgemTown_Text_DawnMeet:
	.string "DAWN: {PLAYER}! You found the town.\p"
	.string "PROFESSOR ROWAN is in the lab, the\n"
	.string "big building to the east.\p"
	.string "Come on. I'll take you to the door.$"

SandgemTown_Text_LucasMeet:
	.string "LUCAS: {PLAYER}! You found the town.\p"
	.string "PROFESSOR ROWAN is in the lab, the\n"
	.string "big building to the east.\p"
	.string "Come on. I'll take you to the door.$"

SandgemTown_Text_DawnWaiting:
	.string "DAWN: The lab door is right here.\n"
	.string "PROFESSOR ROWAN is inside.$"

SandgemTown_Text_LucasWaiting:
	.string "LUCAS: The lab door is right here.\n"
	.string "PROFESSOR ROWAN is inside.$"

SandgemTown_Text_AssistantBusy:
	.string "The lab is the large building\n"
	.string "on the east side of town.$"

SandgemTown_Text_DawnCenter:
	.string "DAWN: This red-roofed building is\n"
	.string "the POKéMON CENTER.\p"
	.string "The nurse inside will heal your\n"
	.string "team. It never costs anything.$"

SandgemTown_Text_LucasCenter:
	.string "LUCAS: This red-roofed building is\n"
	.string "the POKéMON CENTER.\p"
	.string "The nurse inside will heal your\n"
	.string "team. It never costs anything.$"

SandgemTown_Text_DawnMart:
	.string "DAWN: And this is the POKé MART.\p"
	.string "Buy POKé BALLS when you want to\n"
	.string "catch something, and POTIONS\l"
	.string "when a battle leaves you hurt.$"

SandgemTown_Text_LucasMart:
	.string "LUCAS: And this is the POKé MART.\p"
	.string "Buy POKé BALLS when you want to\n"
	.string "catch something, and POTIONS\l"
	.string "when a battle leaves you hurt.$"

SandgemTown_Text_BarryBump:
	.string "BARRY: Whoa! {PLAYER}!\p"
	.string "I'm heading up ROUTE 202. The city\n"
	.string "past it is still shut.\p"
	.string "Don't get comfortable. Next time\n"
	.string "I see you, we're battling again!$"

SandgemTown_Text_BarryLater:
	.string "BARRY: Route 202. I'm taking it.$"

SandgemTown_Text_DawnFree:
	.string "DAWN: I'll be around the lab.\n"
	.string "The Center and the Mart are yours.$"

SandgemTown_Text_LucasFree:
	.string "LUCAS: I'll be around the lab.\n"
	.string "The Center and the Mart are yours.$"

SandgemTown_Text_Boy:
	.string "Everybody in town ends up at the\n"
	.string "lab sooner or later.$"

SandgemTown_Text_Woman:
	.string "The north road is ROUTE 202.\n"
	.string "It runs toward the next city.$"

SandgemTown_Text_CenterSign:
	.string "SANDGEM TOWN POKéMON CENTER\n"
	.string "Heal your team, as often as you like.$"

SandgemTown_Text_MartSign:
	.string "SANDGEM TOWN POKé MART\n"
	.string "POKé BALLS and POTIONS are in stock.$"

SandgemTown_Text_LabSign:
	.string "ROWAN POKéMON LAB\n"
	.string "Ask the questions. Record the answers.$"

SandgemTown_Text_Route202Sign:
	.string "NORTH: ROUTE 202\n"
	.string "A short path toward the next city.$"

SandgemTown_Text_Route219Sign:
	.string "SOUTH: ROUTE 219\n"
	.string "The beach path is closed for now.$"
