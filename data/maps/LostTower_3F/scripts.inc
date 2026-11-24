LostTower_3F_MapScripts::
	.byte 0

LostTower_3F_EventScript_Catherine::
	trainerbattle_single TRAINER_LASS_CATHERINE_LT, LostTower_3F_Text_CatherineIntro, LostTower_3F_Text_CatherineDefeat
	msgbox LostTower_3F_Text_CatherineAfter, MSGBOX_AUTOCLOSE
	end

LostTower_3F_Text_CatherineIntro:
	.string "I study Ghost types here!$"

LostTower_3F_Text_CatherineDefeat:
	.string "Lesson learned...$"

LostTower_3F_Text_CatherineAfter:
	.string "Elders wait at the top.$"
