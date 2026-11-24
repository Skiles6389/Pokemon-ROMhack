CelesticTown_MapScripts::
	.byte 0

CelesticTown_EventScript_GalacticGrunt::
	lock
	faceplayer
	msgbox CelesticTown_Text_GruntChallenge, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CelesticTown_EventScript_GruntRefuse
	msgbox CelesticTown_Text_GruntBattle, MSGBOX_DEFAULT
	closemessage
	trainerbattle_no_intro TRAINER_GALACTIC_GRUNT_JUBILIFE, CelesticTown_Text_GruntDefeat
	msgbox CelesticTown_Text_GruntLeave, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_CELESTIC_TOWN_GRUNT_M, CelesticTown_Movement_GruntLeave
	waitmovement 0
	removeobject LOCALID_CELESTIC_TOWN_GRUNT_M
	setflag FLAG_HIDE_CELESTIC_TOWN_GRUNT_M
	clearflag FLAG_HIDE_CELESTIC_TOWN_CYNTHIA
	addobject LOCALID_CELESTIC_TOWN_CYNTHIA
	release
	end

CelesticTown_EventScript_GruntRefuse::
	msgbox CelesticTown_Text_GruntRefuse, MSGBOX_DEFAULT
	release
	end

CelesticTown_Movement_GruntLeave:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	step_end

CelesticTown_EventScript_Cynthia::
	lock
	faceplayer
	msgbox CelesticTown_Text_CynthiaRuins, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_CELESTIC_TOWN_CYNTHIA, CelesticTown_Movement_CynthiaLeave
	waitmovement 0
	removeobject LOCALID_CELESTIC_TOWN_CYNTHIA
	setflag FLAG_HIDE_CELESTIC_TOWN_CYNTHIA
	release
	end

CelesticTown_Movement_CynthiaLeave:
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

CelesticTown_Text_GruntChallenge:
	.string "TEAM GALACTIC: These ruins are ours.\n"
	.string "You looking for a beating?$"

CelesticTown_Text_GruntRefuse:
	.string "Smart. Stay out of Galactic business.$"

CelesticTown_Text_GruntBattle:
	.string "Fine! Taste the stars of TEAM GALACTIC!$"

CelesticTown_Text_GruntDefeat:
	.string "Urk... too much to handle...$"

CelesticTown_Text_GruntLeave:
	.string "Boss will hear about this!\n"
	.string "The ruins can wait--I'm out!$"

CelesticTown_Text_CynthiaRuins:
	.string "CYNTHIA: Thank you for clearing that\n"
	.string "Galactic grunt away from the ruins.\p"
	.string "Celestic's murals speak of Dialga and\n"
	.string "Palkia--space and time itself.\p"
	.string "I'll study the cave etchings next.\n"
	.string "Meet me again when the lakes stir.$"

CelesticTown_EventScript_PlatNpc0::
	msgbox CelesticTown_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc0_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc1::
	msgbox CelesticTown_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc1_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc2::
	msgbox CelesticTown_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc2_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc3::
	msgbox CelesticTown_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc3_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc4::
	msgbox CelesticTown_EventScript_PlatNpc4_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc4_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc5::
	msgbox CelesticTown_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc5_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc6::
	msgbox CelesticTown_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc6_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc7::
	msgbox CelesticTown_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc7_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc8::
	msgbox CelesticTown_EventScript_PlatNpc8_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc8_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_PlatNpc9::
	msgbox CelesticTown_EventScript_PlatNpc9_Text, MSGBOX_NPC
	end

CelesticTown_EventScript_PlatNpc9_Text:
	.string "This fog used to scare me.\n"
	.string "A strong gust from a POK-MON helps.$"

CelesticTown_EventScript_GrandmaSurf::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_HM_SURF, CelesticTown_EventScript_GrandmaAfter
	goto_if_unset FLAG_GOT_PASTORIA_HM_DEFOG, CelesticTown_EventScript_GrandmaWait
	msgbox CelesticTown_Text_GrandmaOffer, MSGBOX_DEFAULT
	giveitem ITEM_HM_SURF
	setflag FLAG_RECEIVED_HM_SURF
	msgbox CelesticTown_Text_GrandmaExplain, MSGBOX_DEFAULT
	release
	end

CelesticTown_EventScript_GrandmaWait::
	msgbox CelesticTown_Text_GrandmaWait, MSGBOX_DEFAULT
	release
	end

CelesticTown_EventScript_GrandmaAfter::
	msgbox CelesticTown_Text_GrandmaAfter, MSGBOX_DEFAULT
	release
	end

CelesticTown_Text_GrandmaOffer:
	.string "You cleared the fog to reach us.\n"
	.string "Take this-the water roads open next.$"

CelesticTown_Text_GrandmaExplain:
	.string "HM03 Surf lets a POK-MON ferry you\n"
	.string "across deep water. Use it wisely.$"

CelesticTown_Text_GrandmaWait:
	.string "The cliffs stay misty until someone\n"
	.string "brings a proper Defog from Pastoria.$"

CelesticTown_Text_GrandmaAfter:
	.string "Canalave lies west across the water.\n"
	.string "Iron Island waits beyond the harbor.$"

