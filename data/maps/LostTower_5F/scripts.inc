LostTower_5F_MapScripts::
	.byte 0

LostTower_5F_EventScript_ElderCleanse::
	lock
	faceplayer
	goto_if_set FLAG_GOT_LOST_TOWER_CLEANSE_TAG, LostTower_5F_EventScript_ElderCleanseAfter
	msgbox LostTower_5F_Text_CleanseOffer, MSGBOX_DEFAULT
	giveitem ITEM_CLEANSE_TAG
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_LOST_TOWER_CLEANSE_TAG
	msgbox LostTower_5F_Text_CleanseExplain, MSGBOX_DEFAULT
	release
	end

LostTower_5F_EventScript_ElderCleanseAfter::
	msgbox LostTower_5F_Text_CleanseAfter, MSGBOX_DEFAULT
	release
	end

LostTower_5F_EventScript_ElderStrength::
	lock
	faceplayer
	goto_if_set FLAG_GOT_HM04_STRENGTH_LOST_TOWER, LostTower_5F_EventScript_ElderStrengthAfter
	msgbox LostTower_5F_Text_StrengthOffer, MSGBOX_DEFAULT
	giveitem ITEM_HM_STRENGTH
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_HM04_STRENGTH_LOST_TOWER
	msgbox LostTower_5F_Text_StrengthExplain, MSGBOX_DEFAULT
	release
	end

LostTower_5F_EventScript_ElderStrengthAfter::
	msgbox LostTower_5F_Text_StrengthAfter, MSGBOX_DEFAULT
	release
	end

LostTower_5F_Text_CleanseOffer:
	.string "Welcome, child.\p"
	.string "This tower shelters restless souls.\n"
	.string "Take a CLEANSE TAG for safe travels.$"

LostTower_5F_Text_CleanseExplain:
	.string "Hold it close. Wild spirits keep\n"
	.string "a little more distance.$"

LostTower_5F_Text_CleanseAfter:
	.string "May your path stay peaceful.$"

LostTower_5F_Text_StrengthOffer:
	.string "Strong bodies move heavy stones.\p"
	.string "In this land, we entrust Trainers\n"
	.string "with STRENGTH here in the tower.\p"
	.string "Please accept this HM.$"

LostTower_5F_Text_StrengthExplain:
	.string "Teach STRENGTH to a sturdy partner.\n"
	.string "Boulders on the road will yield.$"

LostTower_5F_Text_StrengthAfter:
	.string "Push onward with steady hearts.$"
