OreburghGate_B1F_MapScripts::
	.byte 0

OreburghGate_B1F_EventScript_Cyclist::
	msgbox OreburghGate_B1F_Text_Cyclist, MSGBOX_NPC
	end

OreburghGate_B1F_Text_Cyclist:
	.string "There's a big underground lake past\n"
	.string "these rocks, and ramps you can jump\l"
	.string "with a BIKE on the far side.\p"
	.string "I can't get across without a\n"
	.string "POKéMON that can SURF, though.$"
OreburghGate_B1F_EventScript_V06Trainer0::
	trainerbattle_single TRAINER_OREBURGHGATE_B1F_V06_0, OreburghGate_B1F_EventScript_V06Trainer0_Intro, OreburghGate_B1F_EventScript_V06Trainer0_Defeat
	msgbox OreburghGate_B1F_EventScript_V06Trainer0_After, MSGBOX_AUTOCLOSE
	end

OreburghGate_B1F_EventScript_V06Trainer0_Intro:
	.string "A quick match will wake us both up!$"

OreburghGate_B1F_EventScript_V06Trainer0_Defeat:
	.string "You were ready for that.$"

OreburghGate_B1F_EventScript_V06Trainer0_After:
	.string "Keep going. The next landmark is\n"
	.string "closer than it looks.$"

