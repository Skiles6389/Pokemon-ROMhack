.equ LOCALID_LAKE_CYRUS, 1
.equ LOCALID_LAKE_BARRY, 2
.equ LOCALID_LAKE_ROWAN, 3
.equ LOCALID_LAKE_ASSISTANT, 4
.equ LOCALID_LAKE_BRIEFCASE, 5

.equ BARRY_MON_CHIMCHAR, 0
.equ BARRY_MON_PIPLUP, 1
.equ BARRY_MON_TURTWIG, 2

LakeVerity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LakeVerity_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, LakeVerity_OnFrame
	.byte 0

LakeVerity_OnTransition:
	call LakeVerity_EventScript_SetAssistantGfx
	end

LakeVerity_EventScript_SetAssistantGfx::
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, LakeVerity_EventScript_SetDawnGfx
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL
	return

LakeVerity_EventScript_SetDawnGfx::
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_MAY_NORMAL
	return

LakeVerity_OnFrame:
	map_script_2 VAR_ROUTE201_STATE, 1, LakeVerity_EventScript_OpeningScene
	.2byte 0

LakeVerity_EventScript_OpeningScene::
	lockall
	call LakeVerity_EventScript_SetAssistantGfx
	goto_if_set FLAG_SYS_POKEMON_GET, LakeVerity_EventScript_ResumeAfterStarter
	applymovement OBJ_EVENT_ID_PLAYER, LakeVerity_Movement_PlayerApproach
	applymovement LOCALID_LAKE_BARRY, LakeVerity_Movement_BarryApproach
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, LakeVerity_EventScript_RowanLucasTalk
	msgbox LakeVerity_Text_RowanDawnTalk, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_RowanLeaves
	end

LakeVerity_EventScript_RowanLucasTalk::
	msgbox LakeVerity_Text_RowanLucasTalk, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_RowanLeaves
	end

LakeVerity_EventScript_RowanLeaves::
	closemessage
	applymovement LOCALID_LAKE_ROWAN, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_LAKE_ASSISTANT, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, LakeVerity_EventScript_RowanLucasNotice
	msgbox LakeVerity_Text_RowanNoticesKids, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_DoLeave
	end

LakeVerity_EventScript_RowanLucasNotice::
	msgbox LakeVerity_Text_RowanNoticesKidsLucas, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_DoLeave
	end

LakeVerity_EventScript_DoLeave::
	closemessage
	applymovement LOCALID_LAKE_ROWAN, LakeVerity_Movement_RowanLeaves
	applymovement LOCALID_LAKE_ASSISTANT, LakeVerity_Movement_AssistantLeaves
	waitmovement 0
	removeobject LOCALID_LAKE_ROWAN
	removeobject LOCALID_LAKE_ASSISTANT
	setflag FLAG_HIDE_LAKE_VERITY_ROWAN
	setflag FLAG_HIDE_LAKE_VERITY_ASSISTANT
	msgbox LakeVerity_Text_BarrySeesCase, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, LakeVerity_Movement_PlayerToCase
	applymovement LOCALID_LAKE_BARRY, LakeVerity_Movement_BarryToCase
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	applymovement LOCALID_LAKE_BARRY, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox LakeVerity_Text_StarlyAttack, MSGBOX_DEFAULT
	closemessage
	msgbox LakeVerity_Text_OpenCase, MSGBOX_DEFAULT
	closemessage
	goto LakeVerity_EventScript_ChooseStarter
	end

LakeVerity_EventScript_ResumeAfterStarter::
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	msgbox LakeVerity_Text_StarlyStillThere, MSGBOX_DEFAULT
	closemessage
	goto LakeVerity_EventScript_BattleStarly
	end

LakeVerity_EventScript_ChooseStarter::
	dynmultichoice 0, 0, TRUE, 3, 0, DYN_MULTICHOICE_CB_NONE, LakeVerity_Text_MenuTurtwig, LakeVerity_Text_MenuChimchar, LakeVerity_Text_MenuPiplup
	switch VAR_RESULT
	case 0, LakeVerity_EventScript_ConfirmTurtwig
	case 1, LakeVerity_EventScript_ConfirmChimchar
	case 2, LakeVerity_EventScript_ConfirmPiplup
	goto LakeVerity_EventScript_ChooseStarter
	end

LakeVerity_EventScript_ConfirmTurtwig::
	showmonpic SPECIES_TURTWIG, 10, 3
	msgbox LakeVerity_Text_ConfirmTurtwig, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, LakeVerity_EventScript_DeclineStarter
	hidemonpic
	bufferspeciesname STR_VAR_1, SPECIES_TURTWIG
	givemon SPECIES_TURTWIG, 5, ITEM_NONE
	setvar VAR_ROUTE201_BARRY_MON, BARRY_MON_CHIMCHAR
	goto LakeVerity_EventScript_GotStarter
	end

LakeVerity_EventScript_ConfirmChimchar::
	showmonpic SPECIES_CHIMCHAR, 10, 3
	msgbox LakeVerity_Text_ConfirmChimchar, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, LakeVerity_EventScript_DeclineStarter
	hidemonpic
	bufferspeciesname STR_VAR_1, SPECIES_CHIMCHAR
	givemon SPECIES_CHIMCHAR, 5, ITEM_NONE
	setvar VAR_ROUTE201_BARRY_MON, BARRY_MON_PIPLUP
	goto LakeVerity_EventScript_GotStarter
	end

LakeVerity_EventScript_ConfirmPiplup::
	showmonpic SPECIES_PIPLUP, 10, 3
	msgbox LakeVerity_Text_ConfirmPiplup, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, LakeVerity_EventScript_DeclineStarter
	hidemonpic
	bufferspeciesname STR_VAR_1, SPECIES_PIPLUP
	givemon SPECIES_PIPLUP, 5, ITEM_NONE
	setvar VAR_ROUTE201_BARRY_MON, BARRY_MON_TURTWIG
	goto LakeVerity_EventScript_GotStarter
	end

LakeVerity_EventScript_DeclineStarter::
	hidemonpic
	msgbox LakeVerity_Text_TakeYourTime, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_ChooseStarter
	end

LakeVerity_EventScript_GotStarter::
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PARTY, LakeVerity_EventScript_StarterInParty
	goto Common_EventScript_NoMoreRoomForPokemon
	end

LakeVerity_EventScript_StarterInParty::
	setflag FLAG_SYS_POKEMON_GET
	setvar VAR_ROUTE201_GRASS, 1
	playfanfare MUS_OBTAIN_ITEM
	message LakeVerity_Text_ReceivedMon
	waitmessage
	waitfanfare
	msgbox LakeVerity_Text_BarryGrabsOther, MSGBOX_DEFAULT
	closemessage
	goto LakeVerity_EventScript_BattleStarly
	end

LakeVerity_EventScript_BattleStarly::
	playmoncry SPECIES_STARLY, CRY_MODE_ENCOUNTER
	delay 40
	waitmoncry
	setwildbattle SPECIES_STARLY, 2
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_LOST, LakeVerity_EventScript_LostToStarly
	goto LakeVerity_EventScript_AfterStarly
	end

LakeVerity_EventScript_LostToStarly::
	@ Blackout handles heal; OnFrame resumes via FLAG_SYS_POKEMON_GET.
	releaseall
	end

LakeVerity_EventScript_AfterStarly::
	msgbox LakeVerity_Text_BarryAfterStarly, MSGBOX_DEFAULT
	closemessage
	setobjectxyperm LOCALID_LAKE_ASSISTANT, 47, 21
	clearflag FLAG_HIDE_LAKE_VERITY_ASSISTANT
	addobject LOCALID_LAKE_ASSISTANT
	applymovement LOCALID_LAKE_ASSISTANT, LakeVerity_Movement_AssistantReturns
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_LAKE_BARRY, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, LakeVerity_EventScript_LucasReturns
	msgbox LakeVerity_Text_DawnReturns, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_TakeBriefcase
	end

LakeVerity_EventScript_LucasReturns::
	msgbox LakeVerity_Text_LucasReturns, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_TakeBriefcase
	end

LakeVerity_EventScript_TakeBriefcase::
	closemessage
	applymovement LOCALID_LAKE_ASSISTANT, LakeVerity_Movement_AssistantToCase
	waitmovement 0
	removeobject LOCALID_LAKE_BRIEFCASE
	setflag FLAG_HIDE_LAKE_VERITY_BRIEFCASE
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, LakeVerity_EventScript_LucasLabHint
	msgbox LakeVerity_Text_DawnLabHint, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_AssistantLeavesAgain
	end

LakeVerity_EventScript_LucasLabHint::
	msgbox LakeVerity_Text_LucasLabHint, MSGBOX_DEFAULT
	goto LakeVerity_EventScript_AssistantLeavesAgain
	end

LakeVerity_EventScript_AssistantLeavesAgain::
	closemessage
	applymovement LOCALID_LAKE_ASSISTANT, LakeVerity_Movement_AssistantLeavesFinal
	waitmovement 0
	removeobject LOCALID_LAKE_ASSISTANT
	setflag FLAG_HIDE_LAKE_VERITY_ASSISTANT
	goto LakeVerity_EventScript_CyrusScene
	end

LakeVerity_EventScript_CyrusScene::
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	applymovement LOCALID_LAKE_BARRY, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	applymovement LOCALID_LAKE_BARRY, Common_Movement_ExclamationMark
	waitmovement 0
	setobjectxyperm LOCALID_LAKE_CYRUS, 45, 13
	clearflag FLAG_HIDE_LAKE_VERITY_CYRUS
	addobject LOCALID_LAKE_CYRUS
	applymovement LOCALID_LAKE_CYRUS, LakeVerity_Movement_CyrusStepsIn
	waitmovement 0
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
	warpsilent MAP_ROUTE201, 14, 22
	waitstate
	releaseall
	end

LakeVerity_EventScript_Cyrus::
	msgbox LakeVerity_Text_CyrusIdle, MSGBOX_NPC
	end

LakeVerity_EventScript_Barry::
	msgbox LakeVerity_Text_BarryIdle, MSGBOX_NPC
	end

LakeVerity_EventScript_Rowan::
	msgbox LakeVerity_Text_RowanIdle, MSGBOX_NPC
	end

LakeVerity_EventScript_Assistant::
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, LakeVerity_EventScript_LucasIdle
	msgbox LakeVerity_Text_DawnIdle, MSGBOX_NPC
	end

LakeVerity_EventScript_LucasIdle::
	msgbox LakeVerity_Text_LucasIdle, MSGBOX_NPC
	end

LakeVerity_EventScript_Briefcase::
	msgbox LakeVerity_Text_BriefcaseIdle, MSGBOX_SIGN
	end

LakeVerity_EventScript_Sign::
	msgbox LakeVerity_Text_Sign, MSGBOX_SIGN
	end

LakeVerity_Movement_PlayerApproach:
	walk_up
	walk_up
	walk_up
	face_up
	step_end

LakeVerity_Movement_BarryApproach:
	walk_up
	walk_up
	face_left
	step_end

LakeVerity_Movement_RowanLeaves:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

LakeVerity_Movement_AssistantLeaves:
	delay_8
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

LakeVerity_Movement_PlayerToCase:
	walk_up
	face_up
	step_end

LakeVerity_Movement_BarryToCase:
	walk_left
	walk_up
	face_up
	step_end

LakeVerity_Movement_AssistantReturns:
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	face_up
	step_end

LakeVerity_Movement_AssistantToCase:
	walk_up
	face_up
	step_end

LakeVerity_Movement_AssistantLeavesFinal:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

LakeVerity_Movement_CyrusStepsIn:
	walk_down
	step_end

LakeVerity_Movement_CyrusLeaves:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

LakeVerity_Text_RowanDawnTalk:
	.string "ROWAN: The lake is quieter than\n"
	.string "the reports suggested.\p"
	.string "DAWN: Professor, if nothing shows\n"
	.string "itself, should we head back?\p"
	.string "ROWAN: In a moment. I want one more\n"
	.string "look at the water.$"

LakeVerity_Text_RowanLucasTalk:
	.string "ROWAN: The lake is quieter than\n"
	.string "the reports suggested.\p"
	.string "LUCAS: Professor, if nothing shows\n"
	.string "itself, should we head back?\p"
	.string "ROWAN: In a moment. I want one more\n"
	.string "look at the water.$"

LakeVerity_Text_RowanNoticesKids:
	.string "ROWAN: ...Hm. Visitors.\p"
	.string "DAWN: Professor, the case--\p"
	.string "ROWAN: Leave it. We will return\n"
	.string "shortly. Come, Dawn.$"

LakeVerity_Text_RowanNoticesKidsLucas:
	.string "ROWAN: ...Hm. Visitors.\p"
	.string "LUCAS: Professor, the case--\p"
	.string "ROWAN: Leave it. We will return\n"
	.string "shortly. Come, Lucas.$"

LakeVerity_Text_BarrySeesCase:
	.string "BARRY: They left that case behind!\n"
	.string "What if it has POKéMON in it?\p"
	.string "Come on, {PLAYER}. Just a look!$"

LakeVerity_Text_StarlyAttack:
	.string "A wild STARLY swoops down from\n"
	.string "the grass!$"

LakeVerity_Text_OpenCase:
	.string "BARRY: No POKéMON of our own--\n"
	.string "open the case! Hurry!$"

LakeVerity_Text_StarlyStillThere:
	.string "BARRY: That STARLY is still here!\n"
	.string "Use your POKéMON!$"

LakeVerity_Text_MenuTurtwig:
	.string "TURTWIG$"

LakeVerity_Text_MenuChimchar:
	.string "CHIMCHAR$"

LakeVerity_Text_MenuPiplup:
	.string "PIPLUP$"

LakeVerity_Text_ConfirmTurtwig:
	.string "The Grass-type TURTWIG looks ready.\n"
	.string "Take this one?$"

LakeVerity_Text_ConfirmChimchar:
	.string "The Fire-type CHIMCHAR won't stay\n"
	.string "still. Take this one?$"

LakeVerity_Text_ConfirmPiplup:
	.string "The Water-type PIPLUP stands proud.\n"
	.string "Take this one?$"

LakeVerity_Text_TakeYourTime:
	.string "BARRY: Pick one already!\n"
	.string "That bird isn't waiting!$"

LakeVerity_Text_ReceivedMon:
	.string "{PLAYER} received {STR_VAR_1}!$"

LakeVerity_Text_BarryGrabsOther:
	.string "BARRY: Then this one's mine!\n"
	.string "Now fight that STARLY!$"

LakeVerity_Text_BarryAfterStarly:
	.string "BARRY: Ha! That's what you get!\p"
	.string "Wait--someone's coming back!$"

LakeVerity_Text_DawnReturns:
	.string "DAWN: Oh no--the Professor's case!\p"
	.string "You two... you had to open it?\n"
	.string "A wild POKéMON attacked?\p"
	.string "Then keep the one you used.\n"
	.string "I'll explain everything at the lab\l"
	.string "in Sandgem Town.$"

LakeVerity_Text_LucasReturns:
	.string "LUCAS: Oh no--the Professor's case!\p"
	.string "You two... you had to open it?\n"
	.string "A wild POKéMON attacked?\p"
	.string "Then keep the one you used.\n"
	.string "I'll explain everything at the lab\l"
	.string "in Sandgem Town.$"

LakeVerity_Text_DawnLabHint:
	.string "DAWN: I'll take the case.\n"
	.string "Please visit the lab when you can.$"

LakeVerity_Text_LucasLabHint:
	.string "LUCAS: I'll take the case.\n"
	.string "Please visit the lab when you can.$"

LakeVerity_Text_Cyrus:
	.string "CYRUS: This lake is perfectly still.\p"
	.string "People drag their noise and their\n"
	.string "wanting wherever they go.\p"
	.string "A complete world would not bother\n"
	.string "with any of that.\p"
	.string "...I'm finished here.$"

LakeVerity_Text_BarryAfterCyrus:
	.string "BARRY: That guy gave me the creeps.\p"
	.string "Anyway--Sandgem is east of the\n"
	.string "route. Race you once we get back!\p"
	.string "And don't think you're skipping\n"
	.string "a battle with me!$"

LakeVerity_Text_CyrusIdle:
	.string "CYRUS: The surface doesn't argue.$"

LakeVerity_Text_BarryIdle:
	.string "BARRY: Keep up, {PLAYER}!$"

LakeVerity_Text_RowanIdle:
	.string "ROWAN: The water keeps its secrets.$"

LakeVerity_Text_DawnIdle:
	.string "DAWN: Stay quiet. The Professor is\n"
	.string "listening to the lake.$"

LakeVerity_Text_LucasIdle:
	.string "LUCAS: Stay quiet. The Professor is\n"
	.string "listening to the lake.$"

LakeVerity_Text_BriefcaseIdle:
	.string "A sturdy briefcase sits in the grass.\n"
	.string "Something inside shifts faintly.$"

LakeVerity_Text_Sign:
	.string "LAKE VERITY\n"
	.string "The water keeps its own counsel.$"
