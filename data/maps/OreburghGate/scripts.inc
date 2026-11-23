OreburghGate_MapScripts::
	.byte 0

OreburghGate_EventScript_Russell::
	trainerbattle_single TRAINER_HIKER_RUSSELL, OreburghGate_Text_RussellIntro, OreburghGate_Text_RussellDefeat
	msgbox OreburghGate_Text_RussellAfter, MSGBOX_AUTOCLOSE
	end

OreburghGate_EventScript_CitySign::
	msgbox OreburghGate_Text_CitySign, MSGBOX_SIGN
	end

OreburghGate_Text_RussellIntro:
	.string "GEODUDE likes a low ceiling.\n"
	.string "So do I. Battle.$"

OreburghGate_Text_RussellDefeat:
	.string "The ceiling won.$"

OreburghGate_Text_RussellAfter:
	.string "ZUBAT in the dark, GEODUDE on\n"
	.string "the rock, PSYDUCK if you find water.$"

OreburghGate_Text_CitySign:
	.string "EAST: OREBURGH CITY\n"
	.string "The far door is still shut.$"
