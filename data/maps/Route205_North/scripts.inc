Route205_North_MapScripts::
	.byte 0

Route205_North_EventScript_Andrew::
	trainerbattle_single TRAINER_FISHER_ANDREW_R205N, Route205_North_Text_AndrewIntro, Route205_North_Text_AndrewDefeat
	msgbox Route205_North_Text_AndrewAfter, MSGBOX_AUTOCLOSE
	end

Route205_North_EventScript_Joseph::
	trainerbattle_single TRAINER_FISHERMAN_JOSEPH, Route205_North_Text_JosephIntro, Route205_North_Text_JosephDefeat
	msgbox Route205_North_Text_JosephAfter, MSGBOX_AUTOCLOSE
	end

Route205_North_EventScript_Zachary::
	trainerbattle_single TRAINER_FISHERMAN_ZACHARY, Route205_North_Text_ZacharyIntro, Route205_North_Text_ZacharyDefeat
	msgbox Route205_North_Text_ZacharyAfter, MSGBOX_AUTOCLOSE
	end

Route205_North_EventScript_Potion::
	finditem ITEM_POTION
	end

Route205_North_EventScript_Sign::
	msgbox Route205_North_Text_Sign, MSGBOX_SIGN
	end

Route205_North_Text_AndrewIntro:
	.string "Nothing bites like a good battle!$"

Route205_North_Text_AndrewDefeat:
	.string "Line snapped...$"

Route205_North_Text_AndrewAfter:
	.string "Eterna City fishermen swap tips at\n"
	.string "the bridge.$"

Route205_North_Text_JosephIntro:
	.string "Cast your line, cast your best\n"
	.string "POKéMON!$"

Route205_North_Text_JosephDefeat:
	.string "Tangled tackle...$"

Route205_North_Text_JosephAfter:
	.string "Magikarp evolve if you stay patient.$"

Route205_North_Text_ZacharyIntro:
	.string "Reel 'em in--Trainer style!$"

Route205_North_Text_ZacharyDefeat:
	.string "The big one got away...$"

Route205_North_Text_ZacharyAfter:
	.string "The Cycling Road is south in Eterna.$"

Route205_North_Text_Sign:
	.string "ROUTE 205\n"
	.string "Eterna City - Eterna Forest$"
Route205_North_EventScript_PlatNpc0::
	msgbox Route205_North_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

Route205_North_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route205_North_EventScript_PlatNpc1::
	msgbox Route205_North_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

Route205_North_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route205_North_EventScript_PlatNpc2::
	msgbox Route205_North_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

Route205_North_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route205_North_EventScript_PlatNpc3::
	msgbox Route205_North_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

Route205_North_EventScript_PlatNpc3_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route205_North_EventScript_PlatNpc6::
	msgbox Route205_North_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

Route205_North_EventScript_PlatNpc6_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

