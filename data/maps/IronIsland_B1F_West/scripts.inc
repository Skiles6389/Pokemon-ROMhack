IronIsland_B1F_West_MapScripts::
	.byte 0

IronIsland_B1F_West_EventScript_Item0::
	finditem ITEM_ULTRA_BALL
	end

IronIsland_B1F_West_EventScript_Tr1::
	trainerbattle_single TRAINER_CAMPER_LAWRENCE_II, IronIsland_B1F_West_EventScript_Tr1_Intro, IronIsland_B1F_West_EventScript_Tr1_Defeat
	msgbox IronIsland_B1F_West_EventScript_Tr1_After, MSGBOX_AUTOCLOSE
	end

IronIsland_B1F_West_EventScript_Tr1_Intro:
	.string "Iron Island forges tough trainers!$"

IronIsland_B1F_West_EventScript_Tr1_Defeat:
	.string "Tempered...$"

IronIsland_B1F_West_EventScript_Tr1_After:
	.string "Watch your step on the lifts.$"

IronIsland_B1F_West_EventScript_Item2::
	finditem ITEM_ULTRA_BALL
	end

