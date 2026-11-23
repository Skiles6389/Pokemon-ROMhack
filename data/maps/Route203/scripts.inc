Route203_MapScripts::
	.byte 0

Route203_EventScript_Barry::
	lockall
	clearflag FLAG_HIDE_ROUTE203_BARRY
	addobject LOCALID_ROUTE203_BARRY
	applymovement LOCALID_ROUTE203_BARRY, Route203_Movement_BarryIn
	waitmovement 0
	applymovement LOCALID_ROUTE203_BARRY, Common_Movement_FacePlayer
	waitmovement 0
	msgbox Route203_Text_BarryIntro, MSGBOX_DEFAULT
	closemessage
	special HealPlayerParty
	switch VAR_ROUTE201_BARRY_MON
	case BARRY_MON_CHIMCHAR, Route203_EventScript_BattleChimchar
	case BARRY_MON_PIPLUP, Route203_EventScript_BattlePiplup
	case BARRY_MON_TURTWIG, Route203_EventScript_BattleTurtwig
	end

Route203_EventScript_BattleChimchar::
	trainerbattle LOCALID_ROUTE203_BARRY, TRAINER_BARRY_2_CHIMCHAR, Route203_Text_BarryChallenge, Route203_Text_BarryDefeat, Route203_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route203_EventScript_BattlePiplup::
	trainerbattle LOCALID_ROUTE203_BARRY, TRAINER_BARRY_2_PIPLUP, Route203_Text_BarryChallenge, Route203_Text_BarryDefeat, Route203_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route203_EventScript_BattleTurtwig::
	trainerbattle LOCALID_ROUTE203_BARRY, TRAINER_BARRY_2_TURTWIG, Route203_Text_BarryChallenge, Route203_Text_BarryDefeat, Route203_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

Route203_EventScript_AfterBarry::
	msgbox Route203_Text_BarryAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_ROUTE203_BARRY, Route203_Movement_BarryLeave
	waitmovement 0
	removeobject LOCALID_ROUTE203_BARRY
	setflag FLAG_HIDE_ROUTE203_BARRY
	setvar VAR_ROUTE203_STATE, 2
	releaseall
	end

Route203_EventScript_BarryLater::
	msgbox Route203_Text_BarryLater, MSGBOX_NPC
	end

Route203_EventScript_Michael::
	trainerbattle_single TRAINER_YOUNGSTER_MICHAEL, Route203_Text_MichaelIntro, Route203_Text_MichaelDefeat
	msgbox Route203_Text_MichaelAfter, MSGBOX_AUTOCLOSE
	end

Route203_EventScript_Kaitlin::
	trainerbattle_single TRAINER_LASS_KAITLIN, Route203_Text_KaitlinIntro, Route203_Text_KaitlinDefeat
	msgbox Route203_Text_KaitlinAfter, MSGBOX_AUTOCLOSE
	end

Route203_EventScript_Dallas::
	trainerbattle_single TRAINER_YOUNGSTER_DALLAS, Route203_Text_DallasIntro, Route203_Text_DallasDefeat
	msgbox Route203_Text_DallasAfter, MSGBOX_AUTOCLOSE
	end

Route203_EventScript_GateSign::
	msgbox Route203_Text_GateSign, MSGBOX_SIGN
	end

Route203_Movement_BarryIn:
	walk_fast_left
	walk_fast_left
	step_end

Route203_Movement_BarryLeave:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

Route203_Text_BarryIntro:
	.string "BARRY: There you are!\p"
	.string "This road is mine first. One\n"
	.string "battle, then the cave!$"

Route203_Text_BarryChallenge:
	.string "I've been training the whole way!$"

Route203_Text_BarryDefeat:
	.string "Again? I just got that STARLY!$"

Route203_Text_BarryAfter:
	.string "BARRY: Fine. The cave is east.\n"
	.string "Oreburgh is past it, so hurry up!$"

Route203_Text_BarryLater:
	.string "BARRY: Don't stand around.\n"
	.string "The cave is right there.$"

Route203_Text_MichaelIntro:
	.string "KRICKETOT sings if you let it.\n"
	.string "Listen!$"

Route203_Text_MichaelDefeat:
	.string "It stopped singing.$"

Route203_Text_MichaelAfter:
	.string "A KRICKETOT at night is louder\n"
	.string "than this.$"

Route203_Text_KaitlinIntro:
	.string "BIDOOF and STARLY, together.\n"
	.string "That's the whole road.$"

Route203_Text_KaitlinDefeat:
	.string "The road was bigger than that.$"

Route203_Text_KaitlinAfter:
	.string "ABRA shows up if you look long\n"
	.string "enough. I never have.$"

Route203_Text_DallasIntro:
	.string "SHINX sparks when it wants the\n"
	.string "path. Move.$"

Route203_Text_DallasDefeat:
	.string "The spark went out.$"

Route203_Text_DallasAfter:
	.string "The cave ahead is dark. Bring\n"
	.string "something that isn't scared.$"

Route203_Text_GateSign:
	.string "EAST: OREBURGH GATE\n"
	.string "A cave on the way to the city.$"
