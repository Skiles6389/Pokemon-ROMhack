CanalaveCity_MapScripts::
	.byte 0

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

