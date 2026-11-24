LostTower_2F_MapScripts::
	.byte 0

LostTower_2F_EventScript_Valerius::
	trainerbattle_single TRAINER_PSYCHIC_VALERIUS_LT, LostTower_2F_Text_ValeriusIntro, LostTower_2F_Text_ValeriusDefeat
	msgbox LostTower_2F_Text_ValeriusAfter, MSGBOX_AUTOCLOSE
	end

LostTower_2F_EventScript_Molly::
	trainerbattle_single TRAINER_CHANNELER_MOLLY_LT, LostTower_2F_Text_MollyIntro, LostTower_2F_Text_MollyDefeat
	msgbox LostTower_2F_Text_MollyAfter, MSGBOX_AUTOCLOSE
	end

LostTower_2F_Text_ValeriusIntro:
	.string "I sense your aura... battle!$"

LostTower_2F_Text_ValeriusDefeat:
	.string "Your mind is sharper.$"

LostTower_2F_Text_ValeriusAfter:
	.string "Ghosts answer calm Trainers.$"

LostTower_2F_Text_MollyIntro:
	.string "Boo! Did I startle you?$"

LostTower_2F_Text_MollyDefeat:
	.string "My spirits fled...$"

LostTower_2F_Text_MollyAfter:
	.string "Higher floors feel colder.$"
