IronIsland_B2F_East_MapScripts::
	.byte 0

IronIsland_B2F_East_EventScript_Item0::
	finditem ITEM_ULTRA_BALL
	end

IronIsland_B2F_East_EventScript_Item1::
	finditem ITEM_ULTRA_BALL
	end

IronIsland_B2F_East_EventScript_Tr2::
	trainerbattle_single TRAINER_WORKER_NOEL_II, IronIsland_B2F_East_EventScript_Tr2_Intro, IronIsland_B2F_East_EventScript_Tr2_Defeat
	msgbox IronIsland_B2F_East_EventScript_Tr2_After, MSGBOX_AUTOCLOSE
	end

IronIsland_B2F_East_EventScript_Tr2_Intro:
	.string "Iron Island forges tough trainers!$"

IronIsland_B2F_East_EventScript_Tr2_Defeat:
	.string "Tempered...$"

IronIsland_B2F_East_EventScript_Tr2_After:
	.string "Watch your step on the lifts.$"

IronIsland_B2F_East_EventScript_Tr3::
	trainerbattle_single TRAINER_WORKER_BRADEN_II, IronIsland_B2F_East_EventScript_Tr3_Intro, IronIsland_B2F_East_EventScript_Tr3_Defeat
	msgbox IronIsland_B2F_East_EventScript_Tr3_After, MSGBOX_AUTOCLOSE
	end

IronIsland_B2F_East_EventScript_Tr3_Intro:
	.string "Iron Island forges tough trainers!$"

IronIsland_B2F_East_EventScript_Tr3_Defeat:
	.string "Tempered...$"

IronIsland_B2F_East_EventScript_Tr3_After:
	.string "Watch your step on the lifts.$"

