CanalaveCity_MapScripts::
	.byte 0

CanalaveCity_EventScript_Barry::
	lock
	faceplayer
	goto_if_set FLAG_HIDE_CANALAVE_CITY_RIVAL_BRIDGE, CanalaveCity_EventScript_BarryGone
	msgbox CanalaveCity_Text_BarryIntro, MSGBOX_DEFAULT
	switch VAR_ROUTE201_BARRY_MON
	case 0, CanalaveCity_EventScript_BattleChimchar
	case 1, CanalaveCity_EventScript_BattlePiplup
	case 2, CanalaveCity_EventScript_BattleTurtwig
	end

CanalaveCity_EventScript_BarryGone::
	release
	end

CanalaveCity_EventScript_BattleChimchar::
	trainerbattle_no_intro TRAINER_BARRY_4_CHIMCHAR, CanalaveCity_Text_BarryDefeat
	goto CanalaveCity_EventScript_AfterBarry
	end

CanalaveCity_EventScript_BattlePiplup::
	trainerbattle_no_intro TRAINER_BARRY_4_PIPLUP, CanalaveCity_Text_BarryDefeat
	goto CanalaveCity_EventScript_AfterBarry
	end

CanalaveCity_EventScript_BattleTurtwig::
	trainerbattle_no_intro TRAINER_BARRY_4_TURTWIG, CanalaveCity_Text_BarryDefeat
	goto CanalaveCity_EventScript_AfterBarry
	end

CanalaveCity_EventScript_AfterBarry::
	msgbox CanalaveCity_Text_BarryAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_CANALAVE_CITY_RIVAL_BRIDGE, CanalaveCity_Movement_BarryLeave
	waitmovement 0
	removeobject LOCALID_CANALAVE_CITY_RIVAL_BRIDGE
	setflag FLAG_HIDE_CANALAVE_CITY_RIVAL_BRIDGE
	release
	end

CanalaveCity_Movement_BarryLeave:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

CanalaveCity_EventScript_Counterpart::
	lock
	faceplayer
	msgbox CanalaveCity_Text_Counterpart, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_CANALAVE_CITY_COUNTERPART, CanalaveCity_Movement_LibraryLeave
	waitmovement 0
	removeobject LOCALID_CANALAVE_CITY_COUNTERPART
	setflag FLAG_HIDE_CANALAVE_CITY_COUNTERPART
	release
	end

CanalaveCity_EventScript_Rowan::
	lock
	faceplayer
	msgbox CanalaveCity_Text_Rowan, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_CANALAVE_CITY_PROF_ROWAN, CanalaveCity_Movement_LibraryLeave
	waitmovement 0
	removeobject LOCALID_CANALAVE_CITY_PROF_ROWAN
	setflag FLAG_HIDE_CANALAVE_CITY_PROF_ROWAN
	release
	end

CanalaveCity_Movement_LibraryLeave:
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	step_end

CanalaveCity_Text_BarryIntro:
	.string "BARRY: Canalave's bridge, {PLAYER}!\n"
	.string "Byron's Gym is steel-clad and waiting.\p"
	.string "But first--you and me, right here!$"

CanalaveCity_Text_BarryDefeat:
	.string "What?! Even on the bridge?!$"

CanalaveCity_Text_BarryAfter:
	.string "BARRY: Fine! Hit the Gym while I\n"
	.string "scout Iron Island stories at the library.\p"
	.string "Don't you dare lose to Byron!$"

CanalaveCity_Text_Counterpart:
	.string "The library's legends mention lakes\n"
	.string "and a space-time crisis.\p"
	.string "Prof. Rowan wants us reading upstairs.\n"
	.string "I'll catch up with you later!$"

CanalaveCity_Text_Rowan:
	.string "ROWAN: Canalave's tomes hold clues to\n"
	.string "the lakes' guardians.\p"
	.string "Study hard, then sail when ready.\n"
	.string "I'll return to the lab for now.$"

CanalaveCity_EventScript_PlatNpc0::
	msgbox CanalaveCity_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc0_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc1::
	msgbox CanalaveCity_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc1_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc2::
	msgbox CanalaveCity_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc2_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc3::
	msgbox CanalaveCity_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc3_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc4::
	msgbox CanalaveCity_EventScript_PlatNpc4_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc4_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc5::
	msgbox CanalaveCity_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc5_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc6::
	msgbox CanalaveCity_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc6_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc7::
	msgbox CanalaveCity_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc7_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc8::
	msgbox CanalaveCity_EventScript_PlatNpc8_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc8_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc9::
	msgbox CanalaveCity_EventScript_PlatNpc9_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc9_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc10::
	msgbox CanalaveCity_EventScript_PlatNpc10_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc10_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc11::
	msgbox CanalaveCity_EventScript_PlatNpc11_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc11_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc12::
	msgbox CanalaveCity_EventScript_PlatNpc12_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc12_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc13::
	msgbox CanalaveCity_EventScript_PlatNpc13_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc13_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc14::
	msgbox CanalaveCity_EventScript_PlatNpc14_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc14_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc15::
	msgbox CanalaveCity_EventScript_PlatNpc15_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc15_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc16::
	msgbox CanalaveCity_EventScript_PlatNpc16_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc16_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc17::
	msgbox CanalaveCity_EventScript_PlatNpc17_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc17_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_PlatNpc18::
	msgbox CanalaveCity_EventScript_PlatNpc18_Text, MSGBOX_NPC
	end

CanalaveCity_EventScript_PlatNpc18_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

CanalaveCity_EventScript_FerrySailor::
	lock
	faceplayer
	msgbox CanalaveCity_Text_FerryOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CanalaveCity_EventScript_FerryNo
	warpsilent MAP_IRON_ISLAND, 8, 20
	waitstate
	release
	end

CanalaveCity_EventScript_FerryNo::
	msgbox CanalaveCity_Text_FerryNo, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Text_FerryOffer:
	.string "Ferry to Iron Island?\n"
	.string "The crossing is short.$"

CanalaveCity_Text_FerryNo:
	.string "Come back when the ore calls.$"

