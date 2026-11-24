IronIsland_MapScripts::
	.byte 0

IronIsland_EventScript_PlatNpc0::
	msgbox IronIsland_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

IronIsland_EventScript_PlatNpc0_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

IronIsland_EventScript_PlatNpc1::
	msgbox IronIsland_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

IronIsland_EventScript_PlatNpc1_Text:
	.string "Ships, steel, and stories pile up\n"
	.string "along this western shore.$"

IronIsland_EventScript_ReturnFerry::
	lock
	faceplayer
	msgbox IronIsland_Text_ReturnFerry, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, IronIsland_EventScript_Stay
	warpsilent MAP_CANALAVE_CITY, 16, 51
	waitstate
	release
	end

IronIsland_EventScript_Stay::
	msgbox IronIsland_Text_Stay, MSGBOX_DEFAULT
	release
	end

IronIsland_Text_ReturnFerry:
	.string "Head back to Canalave?$"

IronIsland_Text_Stay:
	.string "Watch your step in the shafts.$"

