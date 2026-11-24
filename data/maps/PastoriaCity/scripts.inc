PastoriaCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PastoriaCity_OnTransition
	.byte 0

PastoriaCity_OnTransition:
	setflag FLAG_VISITED_PASTORIA_CITY
	end

PastoriaCity_EventScript_BarryTrigger::
	lockall
	goto_if_set FLAG_HIDE_PASTORIA_BARRY, PastoriaCity_EventScript_BarryAlreadyDone
	playse SE_PIN
	applymovement LOCALID_PASTORIA_BARRY, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_PASTORIA_BARRY, Common_Movement_FacePlayer
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceUp
	waitmovement 0
	msgbox PastoriaCity_Text_BarryIntro, MSGBOX_DEFAULT
	switch VAR_ROUTE201_BARRY_MON
	case 0, PastoriaCity_EventScript_BattleChimchar
	case 1, PastoriaCity_EventScript_BattlePiplup
	case 2, PastoriaCity_EventScript_BattleTurtwig
	end

PastoriaCity_EventScript_BarryAlreadyDone::
	releaseall
	end

PastoriaCity_EventScript_BattleChimchar::
	trainerbattle LOCALID_PASTORIA_BARRY, TRAINER_BARRY_4_CHIMCHAR, PastoriaCity_Text_BarryChallenge, PastoriaCity_Text_BarryDefeat, PastoriaCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

PastoriaCity_EventScript_BattlePiplup::
	trainerbattle LOCALID_PASTORIA_BARRY, TRAINER_BARRY_4_PIPLUP, PastoriaCity_Text_BarryChallenge, PastoriaCity_Text_BarryDefeat, PastoriaCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

PastoriaCity_EventScript_BattleTurtwig::
	trainerbattle LOCALID_PASTORIA_BARRY, TRAINER_BARRY_4_TURTWIG, PastoriaCity_Text_BarryChallenge, PastoriaCity_Text_BarryDefeat, PastoriaCity_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

PastoriaCity_EventScript_AfterBarry::
	msgbox PastoriaCity_Text_BarryAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PASTORIA_BARRY, PastoriaCity_Movement_BarryLeave
	waitmovement 0
	removeobject LOCALID_PASTORIA_BARRY
	setflag FLAG_HIDE_PASTORIA_BARRY
	setvar VAR_PASTORIA_CITY_STATE, 1
	releaseall
	end

PastoriaCity_Movement_BarryLeave:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

PastoriaCity_EventScript_Barry::
	msgbox PastoriaCity_Text_BarryWait, MSGBOX_NPC
	end

PastoriaCity_Text_BarryIntro:
	.string "BARRY: {PLAYER}!! I beat you here\n"
	.string "fair and square--mostly!\p"
	.string "Pastoria's Gym Leader uses Water\n"
	.string "types that hit like tidal waves!\p"
	.string "But first, you and me. Right now.\n"
	.string "No warm-ups. Full power!$"

PastoriaCity_Text_BarryChallenge:
	.string "BARRY: Don't blink!\n"
	.string "My team's been training nonstop!$"

PastoriaCity_Text_BarryDefeat:
	.string "What?! Even here you pull ahead?!$"

PastoriaCity_Text_BarryAfter:
	.string "BARRY: Fine! You earned the first\n"
	.string "shot at CRASHER WAKE!\p"
	.string "I'll scout the Great Marsh while\n"
	.string "you wring out that Fen Badge.\p"
	.string "Don't you dare lose--I'd never\n"
	.string "hear the end of it from myself!$"

PastoriaCity_Text_BarryWait:
	.string "BARRY: Quit stalling!\n"
	.string "Step up and battle already!$"

PastoriaCity_EventScript_GalacticChase::
	lockall
	playse SE_PIN
	applymovement LOCALID_PASTORIA_GRUNT, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_PASTORIA_GRUNT, Common_Movement_FacePlayer
	waitmovement 0
	msgbox PastoriaCity_Text_GruntChase, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PASTORIA_GRUNT, PastoriaCity_Movement_GruntFlee
	waitmovement 0
	removeobject LOCALID_PASTORIA_GRUNT
	setflag FLAG_HIDE_PASTORIA_GALACTIC_GRUNT
	setflag FLAG_PASTORIA_GALACTIC_CHASE
	setvar VAR_PASTORIA_CITY_STATE, 3
	msgbox PastoriaCity_Text_ChaseAftermath, MSGBOX_DEFAULT
	closemessage
	releaseall
	end

PastoriaCity_Movement_GruntFlee:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

PastoriaCity_EventScript_GalacticGrunt::
	lock
	faceplayer
	msgbox PastoriaCity_Text_GruntIdle, MSGBOX_DEFAULT
	release
	end

PastoriaCity_Text_GruntChase:
	.string "GRUNT: You again?! Stay out of\n"
	.string "TEAM GALACTIC's business!\p"
	.string "The device by Lake Valor is none\n"
	.string "of your concern. We're already\l"
	.string "ahead of schedule!\p"
	.string "Tell that loud Gym Leader to keep\n"
	.string "his waves to himself--I'm gone!$"

PastoriaCity_Text_ChaseAftermath:
	.string "He bolted east toward the lake\n"
	.string "road. Whatever they're building,\l"
	.string "Lake Valor would be the next stop--\l"
	.string "but that path isn't open yet.$"

PastoriaCity_Text_GruntIdle:
	.string "Buzz off. I'm waiting for a\n"
	.string "signal--and you're not it.$"

PastoriaCity_EventScript_WakeCameo::
	lock
	faceplayer
	goto_if_set FLAG_PASTORIA_GALACTIC_CHASE, PastoriaCity_EventScript_WakeAfterChase
	msgbox PastoriaCity_Text_WakeCameo, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PASTORIA_WAKE, PastoriaCity_Movement_WakeLeave
	waitmovement 0
	removeobject LOCALID_PASTORIA_WAKE
	setflag FLAG_HIDE_PASTORIA_WAKE_CAMEO
	release
	end

PastoriaCity_EventScript_WakeAfterChase::
	msgbox PastoriaCity_Text_WakeAfterChase, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PASTORIA_WAKE, PastoriaCity_Movement_WakeLeave
	waitmovement 0
	removeobject LOCALID_PASTORIA_WAKE
	setflag FLAG_HIDE_PASTORIA_WAKE_CAMEO
	release
	end

PastoriaCity_Movement_WakeLeave:
	walk_down
	walk_down
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

PastoriaCity_Text_WakeCameo:
	.string "CRASHER WAKE: That badge looks\n"
	.string "good on you!\p"
	.string "I spotted a Galactic goon near the\n"
	.string "marsh gate. Sniff around if you're\l"
	.string "curious--just don't get soaked!$"

PastoriaCity_Text_WakeAfterChase:
	.string "CRASHER WAKE: He ran for the lake?\n"
	.string "Hah! Waves always push troublemakers\l"
	.string "where the current wants them.\p"
	.string "The lake road isn't open yet.\n"
	.string "You've ridden this stretch as far\l"
	.string "as the tide will take you for now!$"

PastoriaCity_EventScript_WestWorker::
	msgbox PastoriaCity_Text_WestWorker, MSGBOX_NPC
	end

PastoriaCity_Text_WestWorker:
	.string "Route 212 and the Trophy Garden\n"
	.string "aren't open yet.\p"
	.string "This gate stays shut for now.$"

PastoriaCity_EventScript_Woman::
	msgbox PastoriaCity_Text_Woman, MSGBOX_NPC
	end

PastoriaCity_Text_Woman:
	.string "Pastoria sits between marsh mist\n"
	.string "and ocean spray. Pack an extra\l"
	.string "pair of socks!$"

PastoriaCity_EventScript_Boy::
	msgbox PastoriaCity_Text_Boy, MSGBOX_NPC
	end

PastoriaCity_Text_Boy:
	.string "I want to tour the Great Marsh,\n"
	.string "but the desk says it isn't open yet.$"

PastoriaCity_EventScript_OldMan::
	msgbox PastoriaCity_Text_OldMan, MSGBOX_NPC
	end

PastoriaCity_Text_OldMan:
	.string "CRASHER WAKE crashes waves and\n"
	.string "Trainers alike. Bring Electric or\l"
	.string "Grass if you value dry shoes.$"

PastoriaCity_EventScript_Girl::
	msgbox PastoriaCity_Text_Girl, MSGBOX_NPC
	end

PastoriaCity_Text_Girl:
	.string "The Move Reminder in the middle\n"
	.string "house loves Heart Scales. Save\l"
	.string "yours from the beach!$"

PastoriaCity_EventScript_Fisherman::
	msgbox PastoriaCity_Text_Fisherman, MSGBOX_NPC
	end

PastoriaCity_Text_Fisherman:
	.string "Marsh, lake, sea--Pastoria's an\n"
	.string "angler paradise. Cast wisely.$"

PastoriaCity_EventScript_GymSign::
	msgbox PastoriaCity_Text_GymSign, MSGBOX_SIGN
	end

PastoriaCity_Text_GymSign:
	.string "PASTORIA CITY POKéMON GYM\n"
	.string "LEADER: CRASHER WAKE\l"
	.string "A Man Who Swims with the Tides!$"

PastoriaCity_EventScript_CitySign::
	msgbox PastoriaCity_Text_CitySign, MSGBOX_SIGN
	end

PastoriaCity_Text_CitySign:
	.string "PASTORIA CITY\n"
	.string "The moist, marshy city of water$"

PastoriaCity_EventScript_MarshSign::
	msgbox PastoriaCity_Text_MarshSign, MSGBOX_SIGN
	end

PastoriaCity_Text_MarshSign:
	.string "GREAT MARSH GATE\n"
	.string "Safari tours temporarily closed$"
PastoriaCity_EventScript_PlatNpc0::
	msgbox PastoriaCity_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

PastoriaCity_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

PastoriaCity_EventScript_PlatNpc1::
	msgbox PastoriaCity_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

PastoriaCity_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

PastoriaCity_EventScript_PlatNpc2::
	msgbox PastoriaCity_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

PastoriaCity_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

PastoriaCity_EventScript_PlatNpc5::
	msgbox PastoriaCity_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

PastoriaCity_EventScript_PlatNpc5_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

PastoriaCity_EventScript_PlatNpc7::
	msgbox PastoriaCity_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

PastoriaCity_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

PastoriaCity_EventScript_PlatNpc9::
	msgbox PastoriaCity_EventScript_PlatNpc9_Text, MSGBOX_NPC
	end

PastoriaCity_EventScript_PlatNpc9_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

PastoriaCity_EventScript_PlatNpc12::
	msgbox PastoriaCity_EventScript_PlatNpc12_Text, MSGBOX_NPC
	end

PastoriaCity_EventScript_PlatNpc12_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

PastoriaCity_EventScript_PlatNpc13::
	msgbox PastoriaCity_EventScript_PlatNpc13_Text, MSGBOX_NPC
	end

PastoriaCity_EventScript_PlatNpc13_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

