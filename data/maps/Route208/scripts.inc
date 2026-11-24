Route208_MapScripts::
	.byte 0

Route208_EventScript_Robert::
	trainerbattle_single TRAINER_HIKER_ROBERT_R208, Route208_Text_RobertIntro, Route208_Text_RobertDefeat
	msgbox Route208_Text_RobertAfter, MSGBOX_AUTOCLOSE
	end

Route208_Text_RobertIntro:
	.string "Gahahaha! You're just a little kid!\n"
	.string "How're you supposed to beat a big\p"
	.string "man like me?$"

Route208_Text_RobertDefeat:
	.string "Oh my, a big man like me got schooled\n"
	.string "by a little kid like you!$"

Route208_Text_RobertAfter:
	.string "Wow, you're sure impressive!\n"
	.string "I guess it makes no difference if\p"
	.string "you're young or old in battles.$"

Route208_EventScript_Jonathan::
	trainerbattle_single TRAINER_HIKER_JONATHAN_R208, Route208_Text_JonathanIntro, Route208_Text_JonathanDefeat
	msgbox Route208_Text_JonathanAfter, MSGBOX_AUTOCLOSE
	end

Route208_Text_JonathanIntro:
	.string "If I beat you, will you share some\n"
	.string "food with me?$"

Route208_Text_JonathanDefeat:
	.string "We were starved for food, and now\n"
	.string "we're starved for a win...$"

Route208_Text_JonathanAfter:
	.string "Sigh... I feel even hungrier...\n"
	.string "Maybe I'll chow down some Berries...\p"
	.string "But that's kind of gross.\n"
	.string "What am I, a POKéMON?$"

Route208_EventScript_Kyle::
	trainerbattle_single TRAINER_BLACK_BELT_KYLE_R208, Route208_Text_KyleIntro, Route208_Text_KyleDefeat
	msgbox Route208_Text_KyleAfter, MSGBOX_AUTOCLOSE
	end

Route208_Text_KyleIntro:
	.string "This karate man's going to pulverize\n"
	.string "you!$"

Route208_Text_KyleDefeat:
	.string "We got pulverized...$"

Route208_Text_KyleAfter:
	.string "It's obvious I need to train myself\n"
	.string "and my POKéMON harder.\p"
	.string "Hey, if you've got a Vs. Seeker, you'd\n"
	.string "better put it to good use.\p"
	.string "Nothing beats some repeated battling\n"
	.string "for toughening up your POKéMON.$"

Route208_EventScript_Cody::
	trainerbattle_single TRAINER_FISHERMAN_CODY_R208, Route208_Text_CodyIntro, Route208_Text_CodyDefeat
	msgbox Route208_Text_CodyAfter, MSGBOX_AUTOCLOSE
	end

Route208_Text_CodyIntro:
	.string "Muhihi...\n"
	.string "I'll haul you up and out!$"

Route208_Text_CodyDefeat:
	.string "Restraint is my favorite word.\n"
	.string "Like...from crushing my opponents.$"

Route208_Text_CodyAfter:
	.string "You need a Good Rod if you want to\n"
	.string "catch good POKéMON.$"

Route208_EventScript_Hannah::
	trainerbattle_single TRAINER_AROMA_LADY_HANNAH_R208, Route208_Text_HannahIntro, Route208_Text_HannahDefeat
	msgbox Route208_Text_HannahAfter, MSGBOX_AUTOCLOSE
	end

Route208_Text_HannahIntro:
	.string "Oh, you want to have a battle?\n"
	.string "I was meaning to enter a Contest,\p"
	.string "but beating you won't take long...$"

Route208_Text_HannahDefeat:
	.string "Oh, you have us beaten.$"

Route208_Text_HannahAfter:
	.string "You and your POKéMON have so much\n"
	.string "energy.\p"
	.string "I think you would do well in\n"
	.string "Contests, too.$"

Route208_EventScript_William::
	trainerbattle_single TRAINER_ARTIST_WILLIAM_R208, Route208_Text_WilliamIntro, Route208_Text_WilliamDefeat
	msgbox Route208_Text_WilliamAfter, MSGBOX_AUTOCLOSE
	end

Route208_Text_WilliamIntro:
	.string "You and I!\n"
	.string "Let us create a scene!\p"
	.string "A fantastic tableau of battle!$"

Route208_Text_WilliamDefeat:
	.string "Magnificent!\n"
	.string "I am aglow with inspiration!$"

Route208_Text_WilliamAfter:
	.string "That battle will surely become a\n"
	.string "stupendous masterpiece painting!\p"
	.string "I shall title it...\n"
	.string "“My POKéMON Is Fight”!$"


Route208_EventScript_OddKeystone::
	lock
	faceplayer
	goto_if_set FLAG_GOT_ODD_KEYSTONE_R208, Route208_EventScript_OddKeystoneAfter
	msgbox Route208_Text_JustTakeIt, MSGBOX_DEFAULT
	giveitem ITEM_ODD_KEYSTONE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_ODD_KEYSTONE_R208
	msgbox Route208_Text_GoUnderground, MSGBOX_DEFAULT
	release
	end

Route208_EventScript_OddKeystoneAfter::
	msgbox Route208_Text_GoUnderground, MSGBOX_DEFAULT
	release
	end

Route208_EventScript_Ether::
	finditem ITEM_ETHER
	end

Route208_EventScript_SignMtCoronet::
	msgbox Route208_Text_SignMtCoronet, MSGBOX_SIGN
	end

Route208_EventScript_SignHearthome::
	msgbox Route208_Text_SignHearthome, MSGBOX_SIGN
	end

Route208_EventScript_SignBerryMaster::
	msgbox Route208_Text_SignBerryMaster, MSGBOX_SIGN
	end

Route208_EventScript_TrainerTips::
	msgbox Route208_Text_TrainerTips, MSGBOX_SIGN
	end

Route208_Text_JustTakeIt:
	.string "...Don't say a word.\n"
	.string "Just take it.$"
Route208_Text_GoUnderground:
	.string "Go to Route 209!\n"
	.string "Go underground!\pListen to the stone pillar!\p"
	.string "Talk to people underground!$"
Route208_Text_SignMtCoronet:
	.string "Rt. 208\n"
	.string "Mt. Coronet$"
Route208_Text_SignHearthome:
	.string "Rt. 208\n"
	.string "Hearthome City$"
Route208_Text_SignBerryMaster:
	.string "Berry Master's House\n"
	.string "Free Berries Available$"
Route208_Text_TrainerTips:
	.string "TRAINER TIPS\pAfter a Berry is planted, watch the\n"
	.string "color of the soil.\pIf the soil is dark, it means it has\p"
	.string "plenty of water.$"
Route208_EventScript_PlatNpc0::
	msgbox Route208_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

Route208_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route208_EventScript_PlatNpc1::
	msgbox Route208_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

Route208_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route208_EventScript_PlatNpc2::
	msgbox Route208_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

Route208_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route208_EventScript_PlatNpc3::
	msgbox Route208_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

Route208_EventScript_PlatNpc3_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route208_EventScript_PlatNpc6::
	msgbox Route208_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

Route208_EventScript_PlatNpc6_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route208_EventScript_PlatNpc7::
	msgbox Route208_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

Route208_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route208_EventScript_PlatNpc8::
	msgbox Route208_EventScript_PlatNpc8_Text, MSGBOX_NPC
	end

Route208_EventScript_PlatNpc8_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route208_EventScript_V06Trainer1::
	trainerbattle_single TRAINER_ROUTE208_V06_1, Route208_EventScript_V06Trainer1_Intro, Route208_EventScript_V06Trainer1_Defeat
	msgbox Route208_EventScript_V06Trainer1_After, MSGBOX_AUTOCLOSE
	end

Route208_EventScript_V06Trainer1_Intro:
	.string "A quick match will wake us both up!$"

Route208_EventScript_V06Trainer1_Defeat:
	.string "You were ready for that.$"

Route208_EventScript_V06Trainer1_After:
	.string "Keep going. The next landmark is\n"
	.string "closer than it looks.$"

