VerityLakefront_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VerityLakefront_OnTransition
	.byte 0

@ m51: Barry waits in the lake-entrance corridor only between the Route 201
@ talk (state 1) and the meetup. Driven from vars, so older saves stay correct.
VerityLakefront_OnTransition:
	setflag FLAG_HIDE_VERITY_LAKEFRONT_BARRY
	goto_if_ne VAR_ROUTE201_STATE, 1, VerityLakefront_EventScript_End
	goto_if_set FLAG_VERITY_LAKEFRONT_BARRY_MET, VerityLakefront_EventScript_End
	clearflag FLAG_HIDE_VERITY_LAKEFRONT_BARRY
VerityLakefront_EventScript_End::
	end

VerityLakefront_EventScript_Sign::
	msgbox VerityLakefront_Text_Sign, MSGBOX_SIGN
	end

@ Entrance corridor is 2 wide (x4-5, rows 3-5); every way in crosses (4,6)/(5,6).
VerityLakefront_EventScript_LakeEntrance::
	goto_if_set FLAG_VERITY_LAKEFRONT_BARRY_MET, VerityLakefront_EventScript_End
	lockall
	applymovement LOCALID_VERITY_LAKEFRONT_BARRY, Common_Movement_FacePlayer
	waitmovement 0
	playse SE_PIN
	applymovement LOCALID_VERITY_LAKEFRONT_BARRY, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox VerityLakefront_Text_LakeEntrance, MSGBOX_DEFAULT
	closemessage
	goto VerityLakefront_EventScript_BarryEnters
	end

VerityLakefront_EventScript_Barry::
	lock
	faceplayer
	msgbox VerityLakefront_Text_LakeEntrance, MSGBOX_DEFAULT
	closemessage
	goto VerityLakefront_EventScript_BarryEnters
	end

VerityLakefront_EventScript_BarryEnters::
	applymovement LOCALID_VERITY_LAKEFRONT_BARRY, VerityLakefront_Movement_BarryEnters
	waitmovement 0
	removeobject LOCALID_VERITY_LAKEFRONT_BARRY
	setflag FLAG_HIDE_VERITY_LAKEFRONT_BARRY
	setflag FLAG_VERITY_LAKEFRONT_BARRY_MET
	releaseall
	end

VerityLakefront_Movement_BarryEnters:
	walk_fast_up
	walk_fast_up
	step_end

VerityLakefront_Text_Sign:
	.string "Lake Verity ahead.$"

VerityLakefront_Text_LakeEntrance:
	.string "BARRY: {PLAYER}! What took you?\p"
	.string "The lake's right through here.\n"
	.string "Come on, let's go!$"
