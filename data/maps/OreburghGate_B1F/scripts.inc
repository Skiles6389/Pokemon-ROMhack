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

OreburghGate_B1F_EventScript_VeteranGrant::
	trainerbattle_single TRAINER_VETERAN_GRANT, OreburghGate_B1F_EventScript_VeteranGrant_Intro, OreburghGate_B1F_EventScript_VeteranGrant_Defeat
	msgbox OreburghGate_B1F_EventScript_VeteranGrant_After, MSGBOX_AUTOCLOSE
	end

OreburghGate_B1F_EventScript_VeteranGrant_Intro:
	.string "Hold up! A battle will tell me how\n"
	.string "far you have come.$"

OreburghGate_B1F_EventScript_VeteranGrant_Defeat:
	.string "That was cleaner than I expected.$"

OreburghGate_B1F_EventScript_VeteranGrant_After:
	.string "Keep moving. Every route has a\n"
	.string "lesson if you look for it.$"

