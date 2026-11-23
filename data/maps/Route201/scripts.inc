.equ LOCALID_ROUTE201_TRAVELER, 1
.equ LOCALID_ROUTE201_BARRY, 2
.equ LOCALID_ROUTE201_ROWAN, 3
.equ LOCALID_ROUTE201_ASSISTANT, 4

.equ BARRY_MON_CHIMCHAR, 0
.equ BARRY_MON_PIPLUP, 1
.equ BARRY_MON_TURTWIG, 2

Route201_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route201_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Route201_OnFrame
	.byte 0

Route201_OnTransition:
	call Route201_EventScript_SetAssistantGfx
	end

Route201_EventScript_SetAssistantGfx::
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, Route201_EventScript_SetDawnGfx
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL
	return

Route201_EventScript_SetDawnGfx::
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_MAY_NORMAL
	return

Route201_OnFrame:
	map_script_2 VAR_ROUTE201_STATE, 2, Route201_EventScript_RowanArrives
	map_script_2 VAR_ROUTE201_STATE, 3, Route201_EventScript_BarryRematch
	.2byte 0

Route201_EventScript_BarryMeet::
	lockall
	getplayerxy VAR_TEMP_0, VAR_TEMP_1
	subvar VAR_TEMP_1, 3
	setobjectxyperm LOCALID_ROUTE201_BARRY, VAR_TEMP_0, VAR_TEMP_1
	clearflag FLAG_HIDE_ROUTE201_BARRY
	addobject LOCALID_ROUTE201_BARRY
	applymovement LOCALID_ROUTE201_BARRY, Route201_Movement_BarryBesidePlayer
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox Route201_Text_BarryMeet, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_ROUTE201_BARRY, Route201_Movement_BarryLeads
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Route201_Movement_PlayerFollows
	waitmovement 0
	removeobject LOCALID_ROUTE201_BARRY
	setflag FLAG_HIDE_ROUTE201_BARRY
	clearflag FLAG_HIDE_LAKE_VERITY_BARRY
	clearflag FLAG_HIDE_LAKE_VERITY_ROWAN
	clearflag FLAG_HIDE_LAKE_VERITY_ASSISTANT
	clearflag FLAG_HIDE_LAKE_VERITY_BRIEFCASE
	setvar VAR_ROUTE201_STATE, 1
	warpsilent MAP_LAKE_VERITY, 46, 20
	waitstate
	releaseall
	end

Route201_EventScript_PlayerStepLeft:
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkLeft
	waitmovement 0
	return

Route201_EventScript_RowanArrives::
	@ State 2: player walked back from Lake Verity; Rowan notes the connection, then Barry battles.
	lockall
	getplayerxy VAR_TEMP_0, VAR_TEMP_1
	@ Place the group east of the player (Sandgem side), then walk them over.
	copyvar VAR_TEMP_2, VAR_TEMP_0
	addvar VAR_TEMP_2, 5
	copyvar VAR_TEMP_3, VAR_TEMP_1
	setobjectxyperm LOCALID_ROUTE201_ROWAN, VAR_TEMP_2, VAR_TEMP_3
	addvar VAR_TEMP_3, 1
	setobjectxyperm LOCALID_ROUTE201_ASSISTANT, VAR_TEMP_2, VAR_TEMP_3
	subvar VAR_TEMP_3, 2
	setobjectxyperm LOCALID_ROUTE201_BARRY, VAR_TEMP_2, VAR_TEMP_3
	clearflag FLAG_HIDE_ROUTE201_ROWAN
	clearflag FLAG_HIDE_ROUTE201_ASSISTANT
	clearflag FLAG_HIDE_ROUTE201_BARRY
	addobject LOCALID_ROUTE201_ROWAN
	addobject LOCALID_ROUTE201_ASSISTANT
	addobject LOCALID_ROUTE201_BARRY
	applymovement LOCALID_ROUTE201_ROWAN, Route201_Movement_RowanApproach
	applymovement LOCALID_ROUTE201_ASSISTANT, Route201_Movement_AssistantApproach
	applymovement LOCALID_ROUTE201_BARRY, Route201_Movement_BarryApproachMeetup
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route201_EventScript_RowanConnectionLucas
	msgbox Route201_Text_RowanConnectionDawn, MSGBOX_DEFAULT
	goto Route201_EventScript_BarryChallenges
	end

Route201_EventScript_RowanConnectionLucas::
	msgbox Route201_Text_RowanConnectionLucas, MSGBOX_DEFAULT
	goto Route201_EventScript_BarryChallenges
	end

Route201_EventScript_BarryChallenges::
	closemessage
	applymovement LOCALID_ROUTE201_BARRY, Common_Movement_WalkInPlaceFasterLeft
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	msgbox Route201_Text_BarryAdvantage, MSGBOX_DEFAULT
	closemessage
	setvar VAR_ROUTE201_STATE, 3
	goto Route201_EventScript_StartBattle
	end

Route201_EventScript_BarryRematch::
	lockall
	msgbox Route201_Text_BarryRematch, MSGBOX_DEFAULT
	closemessage
	goto Route201_EventScript_StartBattle
	end

Route201_EventScript_StartBattle::
	switch VAR_ROUTE201_BARRY_MON
	case BARRY_MON_CHIMCHAR, Route201_EventScript_BattleChimchar
	case BARRY_MON_PIPLUP, Route201_EventScript_BattlePiplup
	case BARRY_MON_TURTWIG, Route201_EventScript_BattleTurtwig
	end

Route201_EventScript_BattleChimchar::
	trainerbattle LOCALID_ROUTE201_BARRY, TRAINER_BARRY_1_CHIMCHAR, Route201_Text_BarryIntro, Route201_Text_BarryLoss, Route201_EventScript_AfterBattle, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route201_EventScript_BattlePiplup::
	trainerbattle LOCALID_ROUTE201_BARRY, TRAINER_BARRY_1_PIPLUP, Route201_Text_BarryIntro, Route201_Text_BarryLoss, Route201_EventScript_AfterBattle, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route201_EventScript_BattleTurtwig::
	trainerbattle LOCALID_ROUTE201_BARRY, TRAINER_BARRY_1_TURTWIG, Route201_Text_BarryIntro, Route201_Text_BarryLoss, Route201_EventScript_AfterBattle, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route201_EventScript_AfterBattle::
	msgbox Route201_Text_BarryAfter, MSGBOX_DEFAULT
	closemessage
	setvar VAR_ROUTE201_STATE, 4
	setflag FLAG_HIDE_ROUTE201_TRAVELER
	removeobject LOCALID_ROUTE201_TRAVELER
	releaseall
	end

Route201_EventScript_Grass::
	lockall
	msgbox Route201_Text_GrassUnsafe, MSGBOX_DEFAULT
	closemessage
	specialvar VAR_RESULT, GetPlayerFacingDirection
	goto_if_eq VAR_RESULT, DIR_NORTH, Route201_EventScript_GrassStepDown
	goto_if_eq VAR_RESULT, DIR_SOUTH, Route201_EventScript_GrassStepUp
	goto_if_eq VAR_RESULT, DIR_WEST, Route201_EventScript_GrassStepRight
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkLeft
	waitmovement 0
	releaseall
	end

Route201_EventScript_GrassStepDown:
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkDown
	waitmovement 0
	releaseall
	end

Route201_EventScript_GrassStepUp:
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkUp
	waitmovement 0
	releaseall
	end

Route201_EventScript_GrassStepRight:
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkRight
	waitmovement 0
	releaseall
	end

Route201_EventScript_GrassWarning::
	lock
	faceplayer
	goto_if_ge VAR_ROUTE201_STATE, 3, Route201_EventScript_TravelerWaiting
	msgbox Route201_Text_GrassWarning, MSGBOX_DEFAULT
	release
	end

Route201_EventScript_TravelerWaiting::
	msgbox Route201_Text_TravelerWaiting, MSGBOX_DEFAULT
	release
	end

Route201_EventScript_LakeSign::
	msgbox Route201_Text_LakeSign, MSGBOX_SIGN
	end

Route201_EventScript_SandgemSign::
	goto_if_ge VAR_ROUTE201_STATE, 4, Route201_EventScript_SandgemOpen
	msgbox Route201_Text_SandgemSign, MSGBOX_SIGN
	end

Route201_EventScript_SandgemOpen::
	msgbox Route201_Text_SandgemOpen, MSGBOX_SIGN
	end

Route201_EventScript_Barry::
	lock
	faceplayer
	goto_if_ge VAR_ROUTE201_STATE, 4, Route201_EventScript_BarryAfterTalk
	msgbox Route201_Text_BarryBusy, MSGBOX_DEFAULT
	release
	end

Route201_EventScript_BarryAfterTalk::
	msgbox Route201_Text_BarryLater, MSGBOX_DEFAULT
	release
	end

Route201_EventScript_Rowan::
	lock
	faceplayer
	goto_if_ge VAR_ROUTE201_STATE, 4, Route201_EventScript_RowanAfterTalk
	msgbox Route201_Text_RowanBusy, MSGBOX_DEFAULT
	release
	end

Route201_EventScript_RowanAfterTalk::
	msgbox Route201_Text_RowanLater, MSGBOX_DEFAULT
	release
	end

Route201_EventScript_Assistant::
	lock
	faceplayer
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route201_EventScript_LucasTalk
	msgbox Route201_Text_DawnLater, MSGBOX_DEFAULT
	release
	end

Route201_EventScript_LucasTalk::
	msgbox Route201_Text_LucasLater, MSGBOX_DEFAULT
	release
	end

Route201_Movement_BarryBesidePlayer:
	walk_fast_down
	walk_fast_down
	face_down
	step_end

Route201_Movement_BarryLeads:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

Route201_Movement_PlayerFollows:
	walk_fast_up
	walk_fast_up
	step_end

Route201_Movement_Approach:
	walk_right
	walk_right
	face_right
	step_end

Route201_Movement_RowanApproach:
	walk_left
	walk_left
	walk_left
	face_left
	step_end

Route201_Movement_AssistantApproach:
	delay_8
	walk_left
	walk_left
	walk_left
	face_left
	step_end

Route201_Movement_BarryApproachMeetup:
	delay_16
	walk_left
	walk_left
	walk_left
	face_left
	step_end

Route201_Text_BarryMeet:
	.string "BARRY: {PLAYER}! You made it!\p"
	.string "The lake is just west of here.\n"
	.string "I saw the Professor go that way.\p"
	.string "Come on, I'll go with you.\n"
	.string "Don't fall behind!$"

Route201_Text_RowanConnectionDawn:
	.string "ROWAN: Ah, {PLAYER}.\p"
	.string "Dawn told me what happened at the\n"
	.string "lake--and about the POKéMON you chose.\p"
	.string "That POKéMON already has a strong\n"
	.string "connection with you.\p"
	.string "Come see me at my lab in Sandgem Town.\n"
	.string "There is more I would like to ask.$"

Route201_Text_RowanConnectionLucas:
	.string "ROWAN: Ah, {PLAYER}.\p"
	.string "Lucas told me what happened at the\n"
	.string "lake--and about the POKéMON you chose.\p"
	.string "That POKéMON already has a strong\n"
	.string "connection with you.\p"
	.string "Come see me at my lab in Sandgem Town.\n"
	.string "There is more I would like to ask.$"

Route201_Text_BarryAdvantage:
	.string "BARRY: Alright--no more waiting!\p"
	.string "My POKéMON has the advantage.\n"
	.string "We're battling, right now!$"

Route201_Text_BarryIntro:
	.string "BARRY: Don't blink!$"

Route201_Text_BarryLoss:
	.string "BARRY: What? I lost already?$"

Route201_Text_BarryRematch:
	.string "BARRY: You're back! I still haven't\n"
	.string "lost for real. One more time!$"

Route201_Text_BarryAfter:
	.string "BARRY: Augh! Fine! Next time I'll\n"
	.string "be way stronger.\p"
	.string "Sandgem is east of here.\n"
	.string "Visit the lab--and race you there!$"

Route201_Text_GrassUnsafe:
	.string "The tall grass rustles.\p"
	.string "You don't have a POKéMON yet,\n"
	.string "so you step back out.$"

Route201_Text_GrassWarning:
	.string "Hold on a second!\p"
	.string "The tall grass, and the road past\n"
	.string "me, are no place without a POKéMON.$"

Route201_Text_TravelerWaiting:
	.string "Finish your business on the road.\n"
	.string "I'm not stepping aside yet.$"

Route201_Text_LakeSign:
	.string "WEST: LAKE VERITY\n"
	.string "A quiet lake at the end of the path.$"

Route201_Text_SandgemSign:
	.string "EAST: SANDGEM TOWN\n"
	.string "The road is still unfinished.$"

Route201_Text_SandgemOpen:
	.string "EAST: SANDGEM TOWN\n"
	.string "A quiet town and a professor's lab.$"

Route201_Text_BarryBusy:
	.string "BARRY: Quit stalling--battle me!$"

Route201_Text_BarryLater:
	.string "BARRY: Sandgem's east. Don't you\n"
	.string "dare get there before I do!$"

Route201_Text_RowanBusy:
	.string "ROWAN: ...$"

Route201_Text_RowanLater:
	.string "ROWAN: I'll be at the lab in\n"
	.string "Sandgem Town.$"

Route201_Text_DawnLater:
	.string "DAWN: The lab is east of here.\n"
	.string "The Professor is expecting you.$"

Route201_Text_LucasLater:
	.string "LUCAS: The lab is east of here.\n"
	.string "The Professor is expecting you.$"
