.equ LOCALID_LAKE_CYRUS, 1
.equ LOCALID_LAKE_BARRY, 2

LakeVerity_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, LakeVerity_OnFrame
	.byte 0

LakeVerity_OnFrame:
	map_script_2 VAR_ROUTE201_STATE, 1, LakeVerity_EventScript_CyrusScene
	.2byte 0

LakeVerity_EventScript_CyrusScene::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, LakeVerity_Movement_PlayerToShore
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_LAKE_BARRY, LakeVerity_Movement_BarryToShore
	applymovement LOCALID_LAKE_CYRUS, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	msgbox LakeVerity_Text_Cyrus, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_LAKE_CYRUS, LakeVerity_Movement_CyrusLeaves
	waitmovement 0
	removeobject LOCALID_LAKE_CYRUS
	setflag FLAG_HIDE_LAKE_VERITY_CYRUS
	msgbox LakeVerity_Text_BarryAfterCyrus, MSGBOX_DEFAULT
	closemessage
	removeobject LOCALID_LAKE_BARRY
	setflag FLAG_HIDE_LAKE_VERITY_BARRY
	setvar VAR_ROUTE201_STATE, 2
	warpsilent MAP_ROUTE201, 8, 11
	waitstate
	releaseall
	end

LakeVerity_EventScript_Cyrus::
	msgbox LakeVerity_Text_CyrusIdle, MSGBOX_NPC
	end

LakeVerity_EventScript_Barry::
	msgbox LakeVerity_Text_BarryIdle, MSGBOX_NPC
	end

LakeVerity_EventScript_Sign::
	msgbox LakeVerity_Text_Sign, MSGBOX_SIGN
	end

LakeVerity_Movement_PlayerToShore:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_up
	step_end

LakeVerity_Movement_BarryToShore:
	walk_fast_up
	face_left
	step_end

LakeVerity_Movement_CyrusLeaves:
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

LakeVerity_Text_Cyrus:
	.string "CYRUS: This lake is perfectly still.\p"
	.string "People drag their noise and their\n"
	.string "wanting wherever they go.\p"
	.string "A complete world would not bother\n"
	.string "with any of that.\p"
	.string "...I'm finished here.$"

LakeVerity_Text_BarryAfterCyrus:
	.string "BARRY: That guy was awful.\n"
	.string "And the Professor isn't even here!\p"
	.string "Back to the route. We must have\n"
	.string "walked right past him!$"

LakeVerity_Text_CyrusIdle:
	.string "CYRUS: The surface doesn't argue.$"

LakeVerity_Text_BarryIdle:
	.string "BARRY: Keep up, {PLAYER}!$"

LakeVerity_Text_Sign:
	.string "LAKE VERITY\n"
	.string "The water keeps its own counsel.$"
