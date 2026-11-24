HearthomeCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, HearthomeCity_OnTransition
	.byte 0

HearthomeCity_OnTransition:
	setflag FLAG_VISITED_HEARTHOME_CITY
	end

HearthomeCity_EventScript_BarryTrigger::
	lockall
	goto_if_unset FLAG_BADGE03_GET, HearthomeCity_EventScript_NeedRelicBadge
	goto_if_set FLAG_HIDE_HEARTHOME_BARRY, HearthomeCity_EventScript_BarryAlreadyDone
	playse SE_PIN
	applymovement LOCALID_HEARTHOME_BARRY, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_HEARTHOME_BARRY, Common_Movement_FacePlayer
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceRight
	waitmovement 0
	msgbox HearthomeCity_Text_BarryIntro, MSGBOX_DEFAULT
	switch VAR_ROUTE201_BARRY_MON
	case 0, HearthomeCity_EventScript_BattleChimchar
	case 1, HearthomeCity_EventScript_BattlePiplup
	case 2, HearthomeCity_EventScript_BattleTurtwig
	end

HearthomeCity_EventScript_NeedRelicBadge::
	msgbox HearthomeCity_Text_NeedRelicBadge, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, HearthomeCity_Movement_PushWest
	waitmovement 0
	releaseall
	end

HearthomeCity_EventScript_BarryAlreadyDone::
	releaseall
	end

HearthomeCity_EventScript_BattleChimchar::
	trainerbattle LOCALID_HEARTHOME_BARRY, TRAINER_BARRY_3_CHIMCHAR, HearthomeCity_Text_BarryChallenge, HearthomeCity_Text_BarryDefeat, HearthomeCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

HearthomeCity_EventScript_BattlePiplup::
	trainerbattle LOCALID_HEARTHOME_BARRY, TRAINER_BARRY_3_PIPLUP, HearthomeCity_Text_BarryChallenge, HearthomeCity_Text_BarryDefeat, HearthomeCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

HearthomeCity_EventScript_BattleTurtwig::
	trainerbattle LOCALID_HEARTHOME_BARRY, TRAINER_BARRY_3_TURTWIG, HearthomeCity_Text_BarryChallenge, HearthomeCity_Text_BarryDefeat, HearthomeCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

HearthomeCity_EventScript_AfterBarry::
	msgbox HearthomeCity_Text_BarryAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_HEARTHOME_BARRY, HearthomeCity_Movement_BarryLeave
	waitmovement 0
	removeobject LOCALID_HEARTHOME_BARRY
	setflag FLAG_HIDE_HEARTHOME_BARRY
	setvar VAR_HEARTHOME_CITY_STATE, 1
	releaseall
	end

HearthomeCity_EventScript_Barry::
	msgbox HearthomeCity_Text_BarryWait, MSGBOX_NPC
	end

HearthomeCity_Movement_PushWest:
	walk_left
	step_end

HearthomeCity_Movement_BarryLeave:
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

HearthomeCity_EventScript_FantinaCameo::
	msgbox HearthomeCity_Text_FantinaCameo, MSGBOX_NPC
	end

HearthomeCity_EventScript_Woman::
	msgbox HearthomeCity_Text_Woman, MSGBOX_NPC
	end

HearthomeCity_EventScript_Man::
	msgbox HearthomeCity_Text_Man, MSGBOX_NPC
	end

HearthomeCity_EventScript_Girl::
	msgbox HearthomeCity_Text_Girl, MSGBOX_NPC
	end

HearthomeCity_EventScript_Boy::
	msgbox HearthomeCity_Text_Boy, MSGBOX_NPC
	end

HearthomeCity_EventScript_OldWoman::
	msgbox HearthomeCity_Text_OldWoman, MSGBOX_NPC
	end

HearthomeCity_EventScript_FatMan::
	msgbox HearthomeCity_Text_FatMan, MSGBOX_NPC
	end

HearthomeCity_EventScript_GymSign::
	msgbox HearthomeCity_Text_GymSign, MSGBOX_SIGN
	end

HearthomeCity_EventScript_CitySign::
	msgbox HearthomeCity_Text_CitySign, MSGBOX_SIGN
	end

HearthomeCity_EventScript_ContestSign::
	msgbox HearthomeCity_Text_ContestSign, MSGBOX_SIGN
	end

HearthomeCity_Text_NeedRelicBadge:
	.string "The gate to Route 209 is sealed for now.\n"
	.string "Challenge FANTINA for the Relic Badge\l"
	.string "before heading east!$"

HearthomeCity_Text_BarryIntro:
	.string "BARRY: There you are!\p"
	.string "I raced through Hearthome and even\n"
	.string "watched the Contests!\p"
	.string "You're not leaving for Route 209\n"
	.string "without a battle!$"

HearthomeCity_Text_BarryChallenge:
	.string "My team is way tougher than before!\n"
	.string "Let's go!$"

HearthomeCity_Text_BarryDefeat:
	.string "Argh! You're still a step ahead!$"

HearthomeCity_Text_BarryAfter:
	.string "BARRY: Fine! You win this round.\p"
	.string "I'm heading to Solaceon next.\n"
	.string "Don't you dare fall behind!$"

HearthomeCity_Text_BarryWait:
	.string "BARRY: Get that Relic Badge, then\n"
	.string "come battle me here!$"

HearthomeCity_Text_FantinaCameo:
	.string "FANTINA: Ooh la la! Contests and Gym\n"
	.string "battles both shine in Hearthome!\p"
	.string "Visit my Gym when you're ready for a\n"
	.string "ghostly performance!$"

HearthomeCity_Text_Woman:
	.string "Hearthome loves Contests almost as\n"
	.string "much as Gym battles.$"

HearthomeCity_Text_Man:
	.string "Amity Square is a peaceful park.\n"
	.string "They're still tidying the gates.$"

HearthomeCity_Text_Girl:
	.string "Bebe raises the cutest EEVEE!\n"
	.string "Her house is by the POKéMON CENTER.$"

HearthomeCity_Text_Boy:
	.string "The Fan Club chairman talks forever\n"
	.string "about friendship and Poffins.$"

HearthomeCity_Text_OldWoman:
	.string "The Foreign Building is quiet.\n"
	.string "People go there to think.$"

HearthomeCity_Text_FatMan:
	.string "Route 212 to the south is closed for\n"
	.string "now. Try the east gate later!$"

HearthomeCity_Text_GymSign:
	.string "HEARTHOME CITY POKéMON GYM\n"
	.string "LEADER: FANTINA\l"
	.string "The Mystical Dancer!$"

HearthomeCity_Text_CitySign:
	.string "HEARTHOME CITY\n"
	.string "Where soft hearts find a home$"

HearthomeCity_Text_ContestSign:
	.string "HEARTHOME SUPER CONTEST HALL\n"
	.string "Show the world your POKéMON's charm!$"
