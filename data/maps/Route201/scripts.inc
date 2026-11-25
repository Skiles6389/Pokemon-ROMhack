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
	.2byte 0

@ Fired from east-path coord triggers only (var gate = state 2).
Route201_EventScript_RowanArrivesTrigger::
	goto Route201_EventScript_RowanArrives
	end

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
	@ Lead onto the clear west corridor (x→0,y=22), then land on the matching
	@ VerityLakefront east-path tile (seamless Route201 connection twin). Never
	@ warp into trees — lakefront grass path opens to the Lake Verity gap.
	fadescreen FADE_TO_BLACK
	@ Barry stands one tile ahead (west) of the player so he really leads.
	setobjectxy OBJ_EVENT_ID_PLAYER, 4, 22
	setobjectxyperm LOCALID_ROUTE201_BARRY, 3, 22
	setobjectxy LOCALID_ROUTE201_BARRY, 3, 22
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceLeft
	applymovement LOCALID_ROUTE201_BARRY, Common_Movement_FaceLeft
	waitmovement 0
	fadescreen FADE_FROM_BLACK
	applymovement LOCALID_ROUTE201_BARRY, Route201_Movement_BarryLeadsWest
	applymovement OBJ_EVENT_ID_PLAYER, Route201_Movement_PlayerFollowsWest
	waitmovement 0
	removeobject LOCALID_ROUTE201_BARRY
	setflag FLAG_HIDE_ROUTE201_BARRY
	clearflag FLAG_HIDE_LAKE_VERITY_BARRY
	clearflag FLAG_HIDE_LAKE_VERITY_ROWAN
	clearflag FLAG_HIDE_LAKE_VERITY_ASSISTANT
	clearflag FLAG_HIDE_LAKE_VERITY_BRIEFCASE
	setvar VAR_ROUTE201_STATE, 1
	@ Route201 (0,22) connects to VerityLakefront (19,14) (left connection, offset 8);
	@ land one tile in on the lakefront's lower grass clearing.
	warpsilent MAP_VERITY_LAKEFRONT, 18, 14
	waitstate
	releaseall
	end

Route201_EventScript_PlayerStepLeft:
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkLeft
	waitmovement 0
	return

Route201_EventScript_RowanArrives::
	@ State 2: east-path meetup. Fixed clear corridor (y=12, x=42+) — never through trees.
	lockall
	fadescreen FADE_TO_BLACK
	@ Snap the player onto the clear path tile in front of the group.
	setobjectxy OBJ_EVENT_ID_PLAYER, 42, 12
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceRight
	waitmovement 0
	@ Spawn on grass/path east of the player (coll=0 the whole way to the map edge).
	setobjectxyperm LOCALID_ROUTE201_ROWAN, 47, 12
	setobjectxyperm LOCALID_ROUTE201_ASSISTANT, 48, 12
	setobjectxyperm LOCALID_ROUTE201_BARRY, 49, 12
	clearflag FLAG_HIDE_ROUTE201_ROWAN
	clearflag FLAG_HIDE_ROUTE201_ASSISTANT
	clearflag FLAG_HIDE_ROUTE201_BARRY
	addobject LOCALID_ROUTE201_ROWAN
	addobject LOCALID_ROUTE201_ASSISTANT
	addobject LOCALID_ROUTE201_BARRY
	fadescreen FADE_FROM_BLACK
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
	msgbox Route201_Text_BarryIntro, MSGBOX_DEFAULT
	closemessage
	@ Advance off OnFrame state 2 before battle so a return never re-runs RowanArrives.
	@ Platinum: win OR lose continues the same post-battle script (no rematch / no whiteout).
	setvar VAR_ROUTE201_STATE, 3
	goto Route201_EventScript_StartBattle
	end

Route201_EventScript_StartBattle::
	@ FLAG_TEMP_5 == B_FLAG_NO_WHITEOUT → continue script after loss (cleared on map transition).
	setflag FLAG_TEMP_5
	switch VAR_ROUTE201_BARRY_MON
	case BARRY_MON_CHIMCHAR, Route201_EventScript_BattleChimchar
	case BARRY_MON_PIPLUP, Route201_EventScript_BattlePiplup
	case BARRY_MON_TURTWIG, Route201_EventScript_BattleTurtwig
	end

Route201_EventScript_BattleChimchar::
	trainerbattle_no_intro TRAINER_BARRY_1_CHIMCHAR, Route201_Text_BarryLoss
	goto Route201_EventScript_AfterBattle
	end

Route201_EventScript_BattlePiplup::
	trainerbattle_no_intro TRAINER_BARRY_1_PIPLUP, Route201_Text_BarryLoss
	goto Route201_EventScript_AfterBattle
	end

Route201_EventScript_BattleTurtwig::
	trainerbattle_no_intro TRAINER_BARRY_1_TURTWIG, Route201_Text_BarryLoss
	goto Route201_EventScript_AfterBattle
	end

Route201_EventScript_AfterBattle::
	@ Story continues on win OR loss; dialogue must match the real outcome.
	clearflag FLAG_TEMP_5
	special HealPlayerParty
	fadescreen FADE_FROM_BLACK
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route201_EventScript_AfterBattleWon
	goto_if_eq VAR_RESULT, B_OUTCOME_LOST, Route201_EventScript_AfterBattleLost
	@ Drew / other — keep story moving with the loss-side line.
	goto Route201_EventScript_AfterBattleLost
	end

Route201_EventScript_AfterBattleWon::
	msgbox Route201_Text_BarryAfterWin, MSGBOX_DEFAULT
	goto Route201_EventScript_AfterBattleContinue
	end

Route201_EventScript_AfterBattleLost::
	msgbox Route201_Text_BarryAfterLoss, MSGBOX_DEFAULT
	goto Route201_EventScript_AfterBattleContinue
	end

Route201_EventScript_AfterBattleContinue::
	closemessage
	applymovement LOCALID_ROUTE201_BARRY, Route201_Movement_PartyLeavesEast
	applymovement LOCALID_ROUTE201_ASSISTANT, Route201_Movement_PartyLeavesEast
	applymovement LOCALID_ROUTE201_ROWAN, Route201_Movement_PartyLeavesEast
	waitmovement 0
	removeobject LOCALID_ROUTE201_BARRY
	removeobject LOCALID_ROUTE201_ASSISTANT
	removeobject LOCALID_ROUTE201_ROWAN
	setflag FLAG_HIDE_ROUTE201_BARRY
	setflag FLAG_HIDE_ROUTE201_ASSISTANT
	setflag FLAG_HIDE_ROUTE201_ROWAN
	settrainerflag TRAINER_BARRY_1_CHIMCHAR
	settrainerflag TRAINER_BARRY_1_PIPLUP
	settrainerflag TRAINER_BARRY_1_TURTWIG
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

@ From (3,22)/(4,22) on the clear west corridor → walk to the map edge.
Route201_Movement_BarryLeadsWest:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	face_left
	step_end

@ Player follows one tile behind Barry: (4,22) -> (0,22); Barry (3,22) walks off the edge.
Route201_Movement_PlayerFollowsWest:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

Route201_Movement_Approach:
	walk_right
	walk_right
	face_right
	step_end

@ Approach: (47/48/49,12) → three steps west on open path toward player at (42,12).
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

@ Leave east along y=12 clear corridor (x=42..63 open) — enough steps to exit the map.
Route201_Movement_PartyLeavesEast:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

Route201_Text_BarryMeet:
	.string "BARRY: {PLAYER}! You made it!\p"
	.string "The lake is just west of here.\n"
	.string "I saw the Professor go that way.\p"
	.string "We'll cut across the lakefront and\n"
	.string "head straight in. Don't fall behind!$"

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

Route201_Text_BarryAfterWin:
	.string "BARRY: Augh! Fine! Next time I'll\n"
	.string "be way stronger.\p"
	.string "Sandgem is east of here.\n"
	.string "Visit the lab--and race you there!$"

Route201_Text_BarryAfterLoss:
	.string "BARRY: Hah! Told you I had the\n"
	.string "advantage!\p"
	.string "Don't look so sour. Sandgem is east.\n"
	.string "Visit the lab--I'll still race you!$"

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

Route201_EventScript_PlatNpc0::
	msgbox Route201_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

Route201_EventScript_PlatNpc0_Text:
	.string "Wild POKéMON love the tall grass.\n"
	.string "Step around it if you're in a hurry.$"

Route201_EventScript_PlatNpc1::
	msgbox Route201_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

Route201_EventScript_PlatNpc1_Text:
	.string "I come out here every morning.\n"
	.string "The grass smells best after dew.$"

Route201_EventScript_PlatNpc2::
	msgbox Route201_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

Route201_EventScript_PlatNpc2_Text:
	.string "Sandgem's just past the trees.\n"
	.string "You can smell the sea from here!$"

Route201_EventScript_PlatNpc3::
	msgbox Route201_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

Route201_EventScript_PlatNpc3_Text:
	.string "I keep pacing because I can't decide\n"
	.string "which way to go first!$"

Route201_EventScript_TrainerTips::
	msgbox Route201_Text_TrainerTips, MSGBOX_SIGN
	end

Route201_Text_TrainerTips:
	.string "TRAINER TIPS\p"
	.string "Jump down a ledge to take a shortcut.\n"
	.string "You can't climb back up the same way!$"
