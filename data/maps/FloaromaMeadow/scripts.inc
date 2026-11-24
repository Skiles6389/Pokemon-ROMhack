FloaromaMeadow_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FloaromaMeadow_OnTransition
	.byte 0

FloaromaMeadow_OnTransition:
	call_if_set FLAG_HIDE_FLOAROMA_MEADOW_GRUNTS, FloaromaMeadow_EventScript_HideGrunts
	end

FloaromaMeadow_EventScript_HideGrunts::
	setobjectxyperm LOCALID_FLOAROMA_HONEY_MAN, 12, 47
	return

FloaromaMeadow_EventScript_GruntTrigger::
	lockall
	playbgm MUS_PL_ENCOUNTER_GALACTIC, FALSE
	applymovement LOCALID_FLOAROMA_GRUNT_WEST, Common_Movement_ExclamationMark
	applymovement LOCALID_FLOAROMA_GRUNT_EAST, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox FloaromaMeadow_Text_HandOverHoney, MSGBOX_DEFAULT
	msgbox FloaromaMeadow_Text_DoAsWeSay, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_FLOAROMA_GRUNT_WEST, Common_Movement_FacePlayer
	applymovement LOCALID_FLOAROMA_GRUNT_EAST, Common_Movement_FacePlayer
	waitmovement 0
	msgbox FloaromaMeadow_Text_WhatllWeDo, MSGBOX_DEFAULT
	msgbox FloaromaMeadow_Text_KeepBratQuiet, MSGBOX_DEFAULT
	closemessage
	trainerbattle_no_intro TRAINER_GALACTIC_GRUNT_FLOAROMA_1, FloaromaMeadow_Text_Grunt1Defeat
	applymovement LOCALID_FLOAROMA_GRUNT_WEST, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	msgbox FloaromaMeadow_Text_ThisIsLame, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_FLOAROMA_GRUNT_WEST, Common_Movement_FacePlayer
	waitmovement 0
	msgbox FloaromaMeadow_Text_ImUpNext, MSGBOX_DEFAULT
	closemessage
	trainerbattle_no_intro TRAINER_GALACTIC_GRUNT_FLOAROMA_2, FloaromaMeadow_Text_Grunt2Defeat
	msgbox FloaromaMeadow_Text_BackToWindworks, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_FLOAROMA_GRUNT_WEST
	removeobject LOCALID_FLOAROMA_GRUNT_EAST
	setflag FLAG_HIDE_FLOAROMA_MEADOW_GRUNTS
	setvar VAR_FLOAROMA_MEADOW_STATE, 1
	clearflag FLAG_HIDE_FLOAROMA_MEADOW_WORKS_KEY
	addobject LOCALID_FLOAROMA_WORKS_KEY
	fadescreen FADE_FROM_BLACK
	fadedefaultbgm
	applymovement LOCALID_FLOAROMA_HONEY_MAN, FloaromaMeadow_Movement_HoneyManApproach
	waitmovement 0
	msgbox FloaromaMeadow_Text_KeyForWindworks, MSGBOX_DEFAULT
	giveitem ITEM_WORKS_KEY
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	removeobject LOCALID_FLOAROMA_WORKS_KEY
	setflag FLAG_HIDE_FLOAROMA_MEADOW_WORKS_KEY
	setflag FLAG_GOT_WORKS_KEY
	msgbox FloaromaMeadow_Text_ThankYouHoney, MSGBOX_DEFAULT
	giveitem ITEM_HONEY, 10
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_FLOAROMA_HONEY
	msgbox FloaromaMeadow_Text_SlatherHoney, MSGBOX_DEFAULT
	closemessage
	releaseall
	end

FloaromaMeadow_Movement_HoneyManApproach:
	walk_down
	step_end

FloaromaMeadow_EventScript_GruntWest::
	msgbox FloaromaMeadow_Text_GruntIdle, MSGBOX_NPC
	end

FloaromaMeadow_EventScript_GruntEast::
	msgbox FloaromaMeadow_Text_GruntIdle, MSGBOX_NPC
	end

FloaromaMeadow_EventScript_HoneyMan::
	goto_if_set FLAG_GOT_WORKS_KEY, FloaromaMeadow_EventScript_HoneyManAfter
	msgbox FloaromaMeadow_Text_HoneyManHelp, MSGBOX_NPC
	end

FloaromaMeadow_EventScript_HoneyManAfter::
	goto_if_unset FLAG_GOT_FLOAROMA_HONEY, FloaromaMeadow_EventScript_RetryHoney
	msgbox FloaromaMeadow_Text_HoneyManAfter, MSGBOX_NPC
	end

FloaromaMeadow_EventScript_RetryHoney::
	lock
	faceplayer
	msgbox FloaromaMeadow_Text_ThankYouHoney, MSGBOX_DEFAULT
	giveitem ITEM_HONEY, 10
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_FLOAROMA_HONEY
	msgbox FloaromaMeadow_Text_SlatherHoney, MSGBOX_DEFAULT
	release
	end

FloaromaMeadow_EventScript_WorksKey::
	finditem ITEM_WORKS_KEY
	goto_if_eq VAR_0x8007, FALSE, FloaromaMeadow_EventScript_WorksKeyDone
	setflag FLAG_GOT_WORKS_KEY
FloaromaMeadow_EventScript_WorksKeyDone::
	end

FloaromaMeadow_Text_HandOverHoney:
	.string "GRUNT: Hand over that Honey already!\n"
	.string "Team Galactic doesn't ask twice!$"

FloaromaMeadow_Text_DoAsWeSay:
	.string "HONEY MAN: P-please... I only gather\n"
	.string "it for the meadow POKéMON...$"

FloaromaMeadow_Text_WhatllWeDo:
	.string "GRUNT: Huh? A kid walked in on us?$"

FloaromaMeadow_Text_KeepBratQuiet:
	.string "GRUNT: Then we make sure the brat\n"
	.string "stays quiet!$"

FloaromaMeadow_Text_Grunt1Defeat:
	.string "Tch... this job keeps getting worse.$"

FloaromaMeadow_Text_ThisIsLame:
	.string "GRUNT: This is so lame...$"

FloaromaMeadow_Text_ImUpNext:
	.string "GRUNT: I'm up next. Heh heh...$"

FloaromaMeadow_Text_Grunt2Defeat:
	.string "...I want a promotion so I can get\n"
	.string "tougher POKéMON...$"

FloaromaMeadow_Text_BackToWindworks:
	.string "GRUNT: Forget it. Back to the\n"
	.string "Windworks before the boss notices.$"

FloaromaMeadow_Text_KeyForWindworks:
	.string "HONEY MAN: They dropped this key!\n"
	.string "It must open Valley Windworks.\p"
	.string "Please, take it. You've earned it.$"

FloaromaMeadow_Text_ThankYouHoney:
	.string "And take some Honey for the road.\n"
	.string "The meadow owes you.$"

FloaromaMeadow_Text_SlatherHoney:
	.string "Slather Honey on a honey tree and\n"
	.string "wait. Something curious may visit.$"

FloaromaMeadow_Text_GruntIdle:
	.string "Buzz off, kid.$"

FloaromaMeadow_Text_HoneyManHelp:
	.string "They're after my Honey...\n"
	.string "Please, help me!$"

FloaromaMeadow_Text_HoneyManAfter:
	.string "Thank you again. The meadow feels\n"
	.string "lighter already.$"
