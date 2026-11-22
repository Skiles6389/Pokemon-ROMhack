.equ BARRY_MON_CHIMCHAR, 0
.equ BARRY_MON_PIPLUP, 1
.equ BARRY_MON_TURTWIG, 2

Route203_MapScripts::
	.byte 0

@ Barry waits just past the Jubilife exit, as in Platinum, and battles with
@ the starter that beats the player's (VAR_ROUTE201_BARRY_MON, set on Route 201).
Route203_EventScript_BarryTrigger::
	lockall
	playse SE_PIN
	applymovement LOCALID_ROUTE203_BARRY, Common_Movement_ExclamationMark
	waitmovement 0
	getplayerxy VAR_TEMP_0, VAR_TEMP_1
	goto_if_eq VAR_TEMP_1, 15, Route203_EventScript_BarryApproachLow
	applymovement LOCALID_ROUTE203_BARRY, Route203_Movement_BarryApproach
	waitmovement 0
	goto Route203_EventScript_BarryTalk
	end

Route203_EventScript_BarryApproachLow::
	applymovement LOCALID_ROUTE203_BARRY, Route203_Movement_BarryApproachLow
	waitmovement 0
	goto Route203_EventScript_BarryTalk
	end

Route203_EventScript_BarryTalk::
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceRight
	waitmovement 0
	msgbox Route203_Text_BarryIntro, MSGBOX_DEFAULT
	switch VAR_ROUTE201_BARRY_MON
	case BARRY_MON_CHIMCHAR, Route203_EventScript_BattleChimchar
	case BARRY_MON_PIPLUP, Route203_EventScript_BattlePiplup
	case BARRY_MON_TURTWIG, Route203_EventScript_BattleTurtwig
	end

Route203_EventScript_BattleChimchar::
	trainerbattle LOCALID_ROUTE203_BARRY, TRAINER_BARRY_2_CHIMCHAR, Route203_Text_BarryChallenge, Route203_Text_BarryDefeat, Route203_EventScript_AfterBattle, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route203_EventScript_BattlePiplup::
	trainerbattle LOCALID_ROUTE203_BARRY, TRAINER_BARRY_2_PIPLUP, Route203_Text_BarryChallenge, Route203_Text_BarryDefeat, Route203_EventScript_AfterBattle, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route203_EventScript_BattleTurtwig::
	trainerbattle LOCALID_ROUTE203_BARRY, TRAINER_BARRY_2_TURTWIG, Route203_Text_BarryChallenge, Route203_Text_BarryDefeat, Route203_EventScript_AfterBattle, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route203_EventScript_AfterBattle::
	msgbox Route203_Text_BarryAfter, MSGBOX_DEFAULT
	closemessage
	getplayerxy VAR_TEMP_0, VAR_TEMP_1
	goto_if_eq VAR_TEMP_1, 15, Route203_EventScript_BarryLeaveHigh
	applymovement LOCALID_ROUTE203_BARRY, Route203_Movement_BarryLeaveLow
	waitmovement 0
	goto Route203_EventScript_BarryGone
	end

Route203_EventScript_BarryLeaveHigh::
	applymovement LOCALID_ROUTE203_BARRY, Route203_Movement_BarryLeaveHigh
	waitmovement 0
	goto Route203_EventScript_BarryGone
	end

Route203_EventScript_BarryGone::
	removeobject LOCALID_ROUTE203_BARRY
	setflag FLAG_HIDE_ROUTE203_BARRY
	setvar VAR_ROUTE203_STATE, 1
	releaseall
	end

Route203_EventScript_Barry::
	msgbox Route203_Text_BarryWait, MSGBOX_NPC
	end

Route203_Movement_BarryApproach:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

Route203_Movement_BarryApproachLow:
	walk_fast_down
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

@ Barry leaves along whichever road row the player is not standing on.
Route203_Movement_BarryLeaveLow:
	walk_fast_down
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

Route203_Movement_BarryLeaveHigh:
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

Route203_EventScript_Michael::
	trainerbattle_single TRAINER_YOUNGSTER_MICHAEL, Route203_Text_MichaelIntro, Route203_Text_MichaelDefeat
	msgbox Route203_Text_MichaelAfter, MSGBOX_AUTOCLOSE
	end

Route203_EventScript_Dallas::
	trainerbattle_single TRAINER_YOUNGSTER_DALLAS, Route203_Text_DallasIntro, Route203_Text_DallasDefeat
	msgbox Route203_Text_DallasAfter, MSGBOX_AUTOCLOSE
	end

Route203_EventScript_Sebastian::
	trainerbattle_single TRAINER_YOUNGSTER_SEBASTIAN, Route203_Text_SebastianIntro, Route203_Text_SebastianDefeat
	msgbox Route203_Text_SebastianAfter, MSGBOX_AUTOCLOSE
	end

Route203_EventScript_Kaitlin::
	trainerbattle_single TRAINER_LASS_KAITLIN, Route203_Text_KaitlinIntro, Route203_Text_KaitlinDefeat
	msgbox Route203_Text_KaitlinAfter, MSGBOX_AUTOCLOSE
	end

Route203_EventScript_Madeline::
	trainerbattle_single TRAINER_LASS_MADELINE, Route203_Text_MadelineIntro, Route203_Text_MadelineDefeat
	msgbox Route203_Text_MadelineAfter, MSGBOX_AUTOCLOSE
	end

Route203_EventScript_Lass::
	msgbox Route203_Text_Lass, MSGBOX_NPC
	end

Route203_EventScript_JubilifeSign::
	msgbox Route203_Text_JubilifeSign, MSGBOX_SIGN
	end

Route203_EventScript_TipsWest::
	msgbox Route203_Text_TipsWest, MSGBOX_SIGN
	end

Route203_EventScript_TipsEast::
	msgbox Route203_Text_TipsEast, MSGBOX_SIGN
	end

Route203_EventScript_GateSign::
	msgbox Route203_Text_GateSign, MSGBOX_SIGN
	end

Route203_Text_BarryIntro:
	.string "BARRY: {PLAYER}! There you are!\p"
	.string "I got a POKéTCH too, so we're even.\n"
	.string "Now let's see whose team is tougher!$"

Route203_Text_BarryChallenge:
	.string "BARRY: I've been training this whole\n"
	.string "way. Get ready!$"

Route203_Text_BarryDefeat:
	.string "What just happened?\n"
	.string "I lost?!$"

Route203_Text_BarryAfter:
	.string "BARRY: Fine, you win this one.\p"
	.string "OREBURGH has a GYM, and I'm getting\n"
	.string "the badge first. Don't you dare\l"
	.string "fall behind!$"

Route203_Text_BarryWait:
	.string "BARRY: Come on, {PLAYER}!$"

Route203_Text_MichaelIntro:
	.string "I caught these two right here.\n"
	.string "Want to see how they fight?$"

Route203_Text_MichaelDefeat:
	.string "They fought, and then they fainted.$"

Route203_Text_MichaelAfter:
	.string "ZUBAT only come out at night.\n"
	.string "I stayed up late for this one.$"

Route203_Text_DallasIntro:
	.string "My SHINX has been sparking all day.\n"
	.string "Let's go!$"

Route203_Text_DallasDefeat:
	.string "Out of sparks.$"

Route203_Text_DallasAfter:
	.string "SHINX gets stronger the longer\n"
	.string "you stick with it. So will I.$"

Route203_Text_SebastianIntro:
	.string "My MACHOP trains on this hill every\n"
	.string "day. Ready?$"

Route203_Text_SebastianDefeat:
	.string "We need more hill.$"

Route203_Text_SebastianAfter:
	.string "The miners in OREBURGH love\n"
	.string "MACHOP. They work hard too.$"

Route203_Text_KaitlinIntro:
	.string "Four POKéMON! One of each kind\n"
	.string "I could find!$"

Route203_Text_KaitlinDefeat:
	.string "All four of them, gone.$"

Route203_Text_KaitlinAfter:
	.string "Maybe a few strong ones beat\n"
	.string "a lot of small ones.$"

Route203_Text_MadelineIntro:
	.string "My PSYDUCK gets a headache when\n"
	.string "it battles. Be gentle!$"

Route203_Text_MadelineDefeat:
	.string "Its head still hurts.$"

Route203_Text_MadelineAfter:
	.string "PSYDUCK swims in the pond here.\n"
	.string "That's where we met.$"

Route203_Text_Lass:
	.string "The tunnel past the hill goes\n"
	.string "to OREBURGH. They say it's being\l"
	.string "cleared out right now.$"

Route203_Text_JubilifeSign:
	.string "ROUTE 203\n"
	.string "WEST: JUBILIFE CITY$"

Route203_Text_TipsWest:
	.string "TRAINER TIPS\p"
	.string "Every move has POWER POINTS, or PP.\n"
	.string "When PP runs low, visit a\l"
	.string "POKéMON CENTER.$"

Route203_Text_TipsEast:
	.string "TRAINER TIPS\p"
	.string "Press the B Button while a POKéMON\n"
	.string "is evolving to stop the evolution.$"

Route203_Text_GateSign:
	.string "OREBURGH GATE\n"
	.string "The tunnel leads to OREBURGH CITY.$"
