LostTower_4F_MapScripts::
	.byte 0

LostTower_4F_EventScript_Reina::
	trainerbattle_single TRAINER_CHANNELER_REINA_LT, LostTower_4F_Text_ReinaIntro, LostTower_4F_Text_ReinaDefeat
	msgbox LostTower_4F_Text_ReinaAfter, MSGBOX_AUTOCLOSE
	end

LostTower_4F_EventScript_Lindsay::
	trainerbattle_single TRAINER_PSYCHIC_LINDSAY_LT, LostTower_4F_Text_LindsayIntro, LostTower_4F_Text_LindsayDefeat
	msgbox LostTower_4F_Text_LindsayAfter, MSGBOX_AUTOCLOSE
	end

LostTower_4F_Text_ReinaIntro:
	.string "Whispers guide my team...$"

LostTower_4F_Text_ReinaDefeat:
	.string "Silenced...$"

LostTower_4F_Text_ReinaAfter:
	.string "One more flight of stairs.$"

LostTower_4F_Text_LindsayIntro:
	.string "Focus cuts through fear!$"

LostTower_4F_Text_LindsayDefeat:
	.string "My focus broke...$"

LostTower_4F_Text_LindsayAfter:
	.string "The elders bless kind hearts.$"
