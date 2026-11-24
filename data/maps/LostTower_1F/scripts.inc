LostTower_1F_MapScripts::
	.byte 0

LostTower_1F_EventScript_Karina::
	trainerbattle_single TRAINER_CHANNELER_KARINA_LT, LostTower_1F_Text_KarinaIntro, LostTower_1F_Text_KarinaDefeat
	msgbox LostTower_1F_Text_KarinaAfter, MSGBOX_AUTOCLOSE
	end

LostTower_1F_Text_KarinaIntro:
	.string "Spirits linger on every step...$"

LostTower_1F_Text_KarinaDefeat:
	.string "Quieted...$"

LostTower_1F_Text_KarinaAfter:
	.string "Climb with respect.$"
