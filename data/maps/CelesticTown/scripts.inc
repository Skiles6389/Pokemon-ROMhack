CelesticTown_MapScripts::
	.byte 0

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

