Route204_South_MapScripts::
	.byte 0

Route204_South_EventScript_Sarah::
	trainerbattle_single TRAINER_LASS_SARAH, Route204_South_Text_SarahIntro, Route204_South_Text_SarahDefeat
	msgbox Route204_South_Text_SarahAfter, MSGBOX_AUTOCLOSE
	end

Route204_South_EventScript_Samantha::
	trainerbattle_single TRAINER_LASS_SAMANTHA, Route204_South_Text_SamanthaIntro, Route204_South_Text_SamanthaDefeat
	msgbox Route204_South_Text_SamanthaAfter, MSGBOX_AUTOCLOSE
	end

Route204_South_EventScript_Tyler::
	trainerbattle_single TRAINER_YOUNGSTER_TYLER_R204, Route204_South_Text_TylerIntro, Route204_South_Text_TylerDefeat
	msgbox Route204_South_Text_TylerAfter, MSGBOX_AUTOCLOSE
	end

Route204_South_EventScript_Youngster::
	msgbox Route204_South_Text_Youngster, MSGBOX_NPC
	end

Route204_South_EventScript_SeaIncense::
	finditem ITEM_SEA_INCENSE
	end

Route204_South_EventScript_HPUp::
	finditem ITEM_HP_UP
	end

Route204_South_EventScript_ParlyzHeal::
	finditem ITEM_PARALYZE_HEAL
	end

Route204_South_EventScript_Sign::
	msgbox Route204_South_Text_Sign, MSGBOX_SIGN
	end

Route204_South_Text_SarahIntro:
	.string "You look new around here.\n"
	.string "Let's see what you've got!$"

Route204_South_Text_SarahDefeat:
	.string "Ow... that stung more than I planned.$"

Route204_South_Text_SarahAfter:
	.string "I'm still learning. Don't rub it in!$"

Route204_South_Text_SamanthaIntro:
	.string "Excuse me--would you spare a battle?$"

Route204_South_Text_SamanthaDefeat:
	.string "You're stronger than you look...$"

Route204_South_Text_SamanthaAfter:
	.string "Maybe a Berry would have helped...$"

Route204_South_Text_TylerIntro:
	.string "Dad gave me this MAGIKARP!\n"
	.string "Watch it thrash!$"

Route204_South_Text_TylerDefeat:
	.string "But Dad said it was special...$"

Route204_South_Text_TylerAfter:
	.string "Your first POKéMON is the one\n"
	.string "you remember forever, right?$"

Route204_South_Text_Youngster:
	.string "Ravaged Path is dark and rocky.\n"
	.string "You'll want ROCK SMASH to get through.$"

Route204_South_Text_Sign:
	.string "ROUTE 204\n"
	.string "North to Floaroma via Ravaged Path$"
Route204_South_EventScript_PlatNpc1::
	msgbox Route204_South_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

Route204_South_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route204_South_EventScript_PlatNpc2::
	msgbox Route204_South_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

Route204_South_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

