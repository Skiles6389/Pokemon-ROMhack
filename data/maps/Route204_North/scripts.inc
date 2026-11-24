Route204_North_MapScripts::
	.byte 0

Route204_North_EventScript_Brandon::
	trainerbattle_single TRAINER_BUG_CATCHER_BRANDON, Route204_North_Text_BrandonIntro, Route204_North_Text_BrandonDefeat
	msgbox Route204_North_Text_BrandonAfter, MSGBOX_AUTOCLOSE
	end

Route204_North_EventScript_Taylor::
	trainerbattle_single TRAINER_AROMA_LADY_TAYLOR, Route204_North_Text_TaylorIntro, Route204_North_Text_TaylorDefeat
	msgbox Route204_North_Text_TaylorAfter, MSGBOX_AUTOCLOSE
	end

Route204_North_EventScript_Liv::
	trainerbattle_double TRAINER_TWINS_LIV_AND_LIZ, Route204_North_Text_LivIntro, Route204_North_Text_LivDefeat, Route204_North_Text_LivNotEnough
	msgbox Route204_North_Text_LivAfter, MSGBOX_AUTOCLOSE
	end

Route204_North_EventScript_Liz::
	trainerbattle_double TRAINER_TWINS_LIV_AND_LIZ, Route204_North_Text_LizIntro, Route204_North_Text_LizDefeat, Route204_North_Text_LizNotEnough
	msgbox Route204_North_Text_LizAfter, MSGBOX_AUTOCLOSE
	end

Route204_North_EventScript_Ace::
	msgbox Route204_North_Text_Ace, MSGBOX_NPC
	end

Route204_North_EventScript_Awakening::
	finditem ITEM_AWAKENING
	end

Route204_North_EventScript_TM09::
	finditem ITEM_TM09
	end

Route204_North_EventScript_Sign::
	msgbox Route204_North_Text_Sign, MSGBOX_SIGN
	end

Route204_North_Text_BrandonIntro:
	.string "Hey! Let me show you my bug POKéMON!$"

Route204_North_Text_BrandonDefeat:
	.string "I didn't even get to explain why\n"
	.string "bugs are the best...$"

Route204_North_Text_BrandonAfter:
	.string "Bugs grow fast, and they're cool.\n"
	.string "You've got to believe me!$"

Route204_North_Text_TaylorIntro:
	.string "Drawn here by the scent of flowers?\n"
	.string "Then battle me!$"

Route204_North_Text_TaylorDefeat:
	.string "A strong Trainer followed the scent...$"

Route204_North_Text_TaylorAfter:
	.string "Have you collected new apps for\n"
	.string "your POKéTCH yet?$"

Route204_North_Text_LivIntro:
	.string "LIV: We can beat this Trainer,\n"
	.string "can't we, Liz?$"

Route204_North_Text_LivDefeat:
	.string "LIV: Oh-oh no!$"

Route204_North_Text_LivAfter:
	.string "LIV: They're going to brag about\n"
	.string "beating us, Liz...$"

Route204_North_Text_LivNotEnough:
	.string "LIV: Only one POKéMON? That's dull!$"

Route204_North_Text_LizIntro:
	.string "LIZ: We're the strongest in class!$"

Route204_North_Text_LizDefeat:
	.string "LIZ: Wait-hold on!$"

Route204_North_Text_LizAfter:
	.string "LIZ: They're really happy they won...$"

Route204_North_Text_LizNotEnough:
	.string "LIZ: Battle both of us, please?$"

Route204_North_Text_Ace:
	.string "Valley Windworks is east of town.\n"
	.string "Something feels off over there...$"

Route204_North_Text_Sign:
	.string "ROUTE 204\n"
	.string "North: Floaroma Town$"
