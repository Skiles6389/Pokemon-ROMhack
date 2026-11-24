Route209_MapScripts::
	.byte 0

Route209_EventScript_Albert::
	trainerbattle_single TRAINER_BREEDER_ALBERT_R209, Route209_Text_AlbertIntro, Route209_Text_AlbertDefeat
	msgbox Route209_Text_AlbertAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Jennifer::
	trainerbattle_single TRAINER_BREEDER_JENNIFER_R209, Route209_Text_JenniferIntro, Route209_Text_JenniferDefeat
	msgbox Route209_Text_JenniferAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Shelley::
	trainerbattle_single TRAINER_COWGIRL_SHELLEY_R209, Route209_Text_ShelleyIntro, Route209_Text_ShelleyDefeat
	msgbox Route209_Text_ShelleyAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Richard::
	trainerbattle_single TRAINER_JOGGER_RICHARD_R209, Route209_Text_RichardIntro, Route209_Text_RichardDefeat
	msgbox Route209_Text_RichardAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Emma::
	trainerbattle_double TRAINER_TWINS_EMMA_LIL_R209, Route209_Text_EmmaIntro, Route209_Text_EmmaDefeat, Route209_Text_EmmaNotEnough
	msgbox Route209_Text_EmmaAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Lil::
	trainerbattle_double TRAINER_TWINS_EMMA_LIL_R209, Route209_Text_LilIntro, Route209_Text_LilDefeat, Route209_Text_LilNotEnough
	msgbox Route209_Text_LilAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_YoungCoupleF::
	trainerbattle_double TRAINER_YOUNG_COUPLE_R209, Route209_Text_CoupleFIntro, Route209_Text_CoupleDefeat, Route209_Text_CoupleNotEnough
	msgbox Route209_Text_CoupleFAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_YoungCoupleM::
	trainerbattle_double TRAINER_YOUNG_COUPLE_R209, Route209_Text_CoupleMIntro, Route209_Text_CoupleDefeat, Route209_Text_CoupleNotEnough
	msgbox Route209_Text_CoupleMAfter, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_Fisherman::
	msgbox Route209_Text_Fisherman, MSGBOX_NPC
	end

Route209_EventScript_Pokefan::
	msgbox Route209_Text_Pokefan, MSGBOX_NPC
	end

Route209_EventScript_GreatBall::
	finditem ITEM_GREAT_BALL
	end

Route209_EventScript_HyperPotion::
	finditem ITEM_HYPER_POTION
	end

Route209_EventScript_Calcium::
	finditem ITEM_CALCIUM
	end

Route209_EventScript_Ether::
	finditem ITEM_ETHER
	end

Route209_EventScript_HallowedTowerSign::
	msgbox Route209_Text_HallowedTower, MSGBOX_SIGN
	end

Route209_EventScript_RouteSign::
	msgbox Route209_Text_RouteSign, MSGBOX_SIGN
	end

Route209_Text_AlbertIntro:
	.string "I raise POKéMON with care!\n"
	.string "Let's see your team!$"

Route209_Text_AlbertDefeat:
	.string "They still have growing to do...$"

Route209_Text_AlbertAfter:
	.string "Solaceon Day Care knows true care.$"

Route209_Text_JenniferIntro:
	.string "My cute partners are ready!\n"
	.string "Don't hold back!$"

Route209_Text_JenniferDefeat:
	.string "Aww, that sting...$"

Route209_Text_JenniferAfter:
	.string "Hallowed Tower is spooky at night.$"

Route209_Text_ShelleyIntro:
	.string "Yeehaw! Trail ride's over--\n"
	.string "time for a battle!$"

Route209_Text_ShelleyDefeat:
	.string "Whoa there, partner...$"

Route209_Text_ShelleyAfter:
	.string "Lost Tower sits north of here.\n"
	.string "Spirits like quiet visitors.$"

Route209_Text_RichardIntro:
	.string "I jog this loop every dawn!\n"
	.string "Keep up if you can!$"

Route209_Text_RichardDefeat:
	.string "Outpaced in battle...$"

Route209_Text_RichardAfter:
	.string "Cardio and contests both matter!$"

Route209_Text_EmmaIntro:
	.string "EMMA: Twin power, go!$"

Route209_Text_EmmaDefeat:
	.string "EMMA: We slipped!$"

Route209_Text_EmmaAfter:
	.string "EMMA: Lil, we need more drills.$"

Route209_Text_EmmaNotEnough:
	.string "EMMA: Bring two POKéMON!$"

Route209_Text_LilIntro:
	.string "LIL: We battle as a pair!$"

Route209_Text_LilDefeat:
	.string "LIL: No fair!$"

Route209_Text_LilAfter:
	.string "LIL: Practice makes perfect.$"

Route209_Text_LilNotEnough:
	.string "LIL: You need two partners!$"

Route209_Text_CoupleFIntro:
	.string "We're on a date... and a battle!$"

Route209_Text_CoupleMIntro:
	.string "Two hearts, one battle plan!$"

Route209_Text_CoupleDefeat:
	.string "Our rhythm broke...$"

Route209_Text_CoupleFAfter:
	.string "Romance can wait. Training first!$"

Route209_Text_CoupleMAfter:
	.string "Next stop: Solaceon Town.$"

Route209_Text_CoupleNotEnough:
	.string "Come back with two POKéMON!$"

Route209_Text_Fisherman:
	.string "The brook here is quiet.\n"
	.string "Good place to think and cast.$"

Route209_Text_Pokefan:
	.string "I walk this route for my health.\n"
	.string "My POKéMON enjoy the air, too.$"

Route209_Text_HallowedTower:
	.string "HALLOWED TOWER\n"
	.string "A quiet shrine for wandering souls$"

Route209_Text_RouteSign:
	.string "ROUTE 209\n"
	.string "Hearthome City - Solaceon Town$"
Route209_EventScript_PlatNpc0::
	msgbox Route209_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

Route209_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route209_EventScript_PlatNpc1::
	msgbox Route209_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

Route209_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route209_EventScript_PlatNpc2::
	msgbox Route209_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

Route209_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route209_EventScript_PlatNpc3::
	msgbox Route209_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

Route209_EventScript_PlatNpc3_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route209_EventScript_PlatNpc5::
	msgbox Route209_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

Route209_EventScript_PlatNpc5_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route209_EventScript_PlatNpc7::
	msgbox Route209_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

Route209_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route209_EventScript_PlatNpc9::
	msgbox Route209_EventScript_PlatNpc9_Text, MSGBOX_NPC
	end

Route209_EventScript_PlatNpc9_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route209_EventScript_PlatNpc11::
	msgbox Route209_EventScript_PlatNpc11_Text, MSGBOX_NPC
	end

Route209_EventScript_PlatNpc11_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"



Route209_EventScript_JoggerRaul::
	trainerbattle_single TRAINER_JOGGER_RAUL, Route209_EventScript_JoggerRaul_Intro, Route209_EventScript_JoggerRaul_Defeat
	msgbox Route209_EventScript_JoggerRaul_After, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_JoggerRaul_Intro:
	.string "Hold up! A battle will tell me how\n"
	.string "far you have come.$"

Route209_EventScript_JoggerRaul_Defeat:
	.string "That was cleaner than I expected.$"

Route209_EventScript_JoggerRaul_After:
	.string "Keep moving. Every route has a\n"
	.string "lesson if you look for it.$"

Route209_EventScript_PokeKidDanielle::
	trainerbattle_single TRAINER_POKE_KID_DANIELLE, Route209_EventScript_PokeKidDanielle_Intro, Route209_EventScript_PokeKidDanielle_Defeat
	msgbox Route209_EventScript_PokeKidDanielle_After, MSGBOX_AUTOCLOSE
	end

Route209_EventScript_PokeKidDanielle_Intro:
	.string "Hold up! A battle will tell me how\n"
	.string "far you have come.$"

Route209_EventScript_PokeKidDanielle_Defeat:
	.string "That was cleaner than I expected.$"

Route209_EventScript_PokeKidDanielle_After:
	.string "Keep moving. Every route has a\n"
	.string "lesson if you look for it.$"

