SunyshoreCity_MapScripts::
	.byte 0

SunyshoreCity_EventScript_Npc0::
	msgbox SunyshoreCity_EventScript_Npc0_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc0_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc1::
	msgbox SunyshoreCity_EventScript_Npc1_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc1_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc2::
	msgbox SunyshoreCity_EventScript_Npc2_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc2_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc3::
	msgbox SunyshoreCity_EventScript_Npc3_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc3_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc4::
	msgbox SunyshoreCity_EventScript_Npc4_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc4_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc5::
	msgbox SunyshoreCity_EventScript_Npc5_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc5_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc6::
	msgbox SunyshoreCity_EventScript_Npc6_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc6_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc7::
	msgbox SunyshoreCity_EventScript_Npc7_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc7_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc8::
	msgbox SunyshoreCity_EventScript_Npc8_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc8_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc9::
	msgbox SunyshoreCity_EventScript_Npc9_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc9_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc10::
	msgbox SunyshoreCity_EventScript_Npc10_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc10_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc11::
	msgbox SunyshoreCity_EventScript_Npc11_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc11_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc12::
	msgbox SunyshoreCity_EventScript_Npc12_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc12_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc13::
	msgbox SunyshoreCity_EventScript_Npc13_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc13_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc14::
	msgbox SunyshoreCity_EventScript_Npc14_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc14_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc15::
	msgbox SunyshoreCity_EventScript_Npc15_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc15_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc16::
	msgbox SunyshoreCity_EventScript_Npc16_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc16_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc17::
	msgbox SunyshoreCity_EventScript_Npc17_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc17_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc18::
	msgbox SunyshoreCity_EventScript_Npc18_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc18_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc19::
	msgbox SunyshoreCity_EventScript_Npc19_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc19_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Npc20::
	msgbox SunyshoreCity_EventScript_Npc20_Text, MSGBOX_NPC
	end

SunyshoreCity_EventScript_Npc20_Text:
	.string "Sunyshore never sleeps.\n"
	.string "The lighthouse keeps the tide honest.$"

SunyshoreCity_EventScript_Route223Closed::
	lock
	faceplayer
	goto_if_set FLAG_BADGE08_GET, SunyshoreCity_EventScript_Route223Hint
	msgbox SunyshoreCity_Text_NeedBadge, MSGBOX_DEFAULT
	release
	end

SunyshoreCity_EventScript_Route223Hint::
	msgbox SunyshoreCity_Text_OpenSoon, MSGBOX_DEFAULT
	release
	end

SunyshoreCity_Text_NeedBadge:
	.string "Route 223's current is rough.\n"
	.string "Earn the Beacon Badge before surfing north.$"

SunyshoreCity_Text_OpenSoon:
	.string "With the Beacon Badge, Victory Road\n"
	.string "opens past Route 223. Pack plenty of Repels.$"

