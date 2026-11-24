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
	lock
	faceplayer
	msgbox HearthomeCity_Text_FantinaCameo, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_HEARTHOME_FANTINA, HearthomeCity_Movement_FantinaLeave
	waitmovement 0
	removeobject LOCALID_HEARTHOME_FANTINA
	setflag FLAG_HIDE_HEARTHOME_FANTINA
	release
	end

HearthomeCity_Movement_FantinaLeave:
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

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
HearthomeCity_EventScript_PlatNpc0::
	msgbox HearthomeCity_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

HearthomeCity_EventScript_PlatNpc1::
	msgbox HearthomeCity_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

HearthomeCity_EventScript_PlatNpc2::
	msgbox HearthomeCity_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

HearthomeCity_EventScript_PlatNpc4::
	msgbox HearthomeCity_EventScript_PlatNpc4_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_PlatNpc4_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

HearthomeCity_EventScript_PlatNpc5::
	msgbox HearthomeCity_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_PlatNpc5_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

HearthomeCity_EventScript_PlatNpc6::
	msgbox HearthomeCity_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_PlatNpc6_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

HearthomeCity_EventScript_PlatNpc7::
	msgbox HearthomeCity_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

HearthomeCity_EventScript_PlatNpc8::
	msgbox HearthomeCity_EventScript_PlatNpc8_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_PlatNpc8_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

HearthomeCity_EventScript_DensifyNpc0::
	msgbox HearthomeCity_EventScript_DensifyNpc0_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc0_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc1::
	msgbox HearthomeCity_EventScript_DensifyNpc1_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc1_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc2::
	msgbox HearthomeCity_EventScript_DensifyNpc2_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc2_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc3::
	msgbox HearthomeCity_EventScript_DensifyNpc3_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc3_Text:
	.string "What a lovely day for a stroll.$"

HearthomeCity_EventScript_DensifyNpc4::
	msgbox HearthomeCity_EventScript_DensifyNpc4_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc4_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc5::
	msgbox HearthomeCity_EventScript_DensifyNpc5_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc5_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc6::
	msgbox HearthomeCity_EventScript_DensifyNpc6_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc6_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc7::
	msgbox HearthomeCity_EventScript_DensifyNpc7_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc7_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc8::
	msgbox HearthomeCity_EventScript_DensifyNpc8_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc8_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc9::
	msgbox HearthomeCity_EventScript_DensifyNpc9_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc9_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc10::
	msgbox HearthomeCity_EventScript_DensifyNpc10_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc10_Text:
	.string "Pachi!$"

HearthomeCity_EventScript_DensifySign11::
	msgbox HearthomeCity_EventScript_DensifySign11_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign11_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifySign12::
	msgbox HearthomeCity_EventScript_DensifySign12_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign12_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifySign13::
	msgbox HearthomeCity_EventScript_DensifySign13_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign13_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifySign14::
	msgbox HearthomeCity_EventScript_DensifySign14_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign14_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifySign15::
	msgbox HearthomeCity_EventScript_DensifySign15_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign15_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifySign16::
	msgbox HearthomeCity_EventScript_DensifySign16_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign16_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifySign17::
	msgbox HearthomeCity_EventScript_DensifySign17_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign17_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifySign18::
	msgbox HearthomeCity_EventScript_DensifySign18_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign18_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifyNpc19::
	msgbox HearthomeCity_EventScript_DensifyNpc19_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc19_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc20::
	msgbox HearthomeCity_EventScript_DensifyNpc20_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc20_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc21::
	msgbox HearthomeCity_EventScript_DensifyNpc21_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc21_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc22::
	msgbox HearthomeCity_EventScript_DensifyNpc22_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc22_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc23::
	msgbox HearthomeCity_EventScript_DensifyNpc23_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc23_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc24::
	msgbox HearthomeCity_EventScript_DensifyNpc24_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc24_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc25::
	msgbox HearthomeCity_EventScript_DensifyNpc25_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc25_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc26::
	msgbox HearthomeCity_EventScript_DensifyNpc26_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc26_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc27::
	msgbox HearthomeCity_EventScript_DensifyNpc27_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc27_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc28::
	msgbox HearthomeCity_EventScript_DensifyNpc28_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc28_Text:
	.string "What a lovely day for a stroll.$"

HearthomeCity_EventScript_DensifyNpc29::
	msgbox HearthomeCity_EventScript_DensifyNpc29_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc29_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifySign30::
	msgbox HearthomeCity_EventScript_DensifySign30_Text, MSGBOX_SIGN
	end

HearthomeCity_EventScript_DensifySign30_Text:
	.string "Hearthome City$"

HearthomeCity_EventScript_DensifyNpc31::
	msgbox HearthomeCity_EventScript_DensifyNpc31_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc31_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc32::
	msgbox HearthomeCity_EventScript_DensifyNpc32_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc32_Text:
	.string "Welcome to Hearthome!$"

HearthomeCity_EventScript_DensifyNpc33::
	msgbox HearthomeCity_EventScript_DensifyNpc33_Text, MSGBOX_NPC
	end

HearthomeCity_EventScript_DensifyNpc33_Text:
	.string "Welcome to Hearthome!$"

