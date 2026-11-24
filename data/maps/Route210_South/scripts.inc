Route210_South_MapScripts::
	.byte 0

Route210_South_EventScript_Teri::
	trainerbattle_double TRAINER_TWINS_TERI_TIA_R210, Route210_South_Text_TeriIntro, Route210_South_Text_TeriDefeat, Route210_South_Text_TeriNotEnough
	msgbox Route210_South_Text_TeriAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Tia::
	trainerbattle_double TRAINER_TWINS_TERI_TIA_R210, Route210_South_Text_TiaIntro, Route210_South_Text_TiaDefeat, Route210_South_Text_TiaNotEnough
	msgbox Route210_South_Text_TiaAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Kahlil::
	trainerbattle_single TRAINER_BREEDER_KAHLIL_R210, Route210_South_Text_KahlilIntro, Route210_South_Text_KahlilDefeat
	msgbox Route210_South_Text_KahlilAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Amber::
	trainerbattle_single TRAINER_BREEDER_AMBER_R210, Route210_South_Text_AmberIntro, Route210_South_Text_AmberDefeat
	msgbox Route210_South_Text_AmberAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Belle::
	trainerbattle_double TRAINER_BELLE_AND_PA_R210, Route210_South_Text_BelleIntro, Route210_South_Text_BellePaDefeat, Route210_South_Text_BelleNotEnough
	msgbox Route210_South_Text_BelleAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Pa::
	trainerbattle_double TRAINER_BELLE_AND_PA_R210, Route210_South_Text_PaIntro, Route210_South_Text_BellePaDefeat, Route210_South_Text_PaNotEnough
	msgbox Route210_South_Text_PaAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Marco::
	trainerbattle_single TRAINER_RANCHER_MARCO_R210, Route210_South_Text_MarcoIntro, Route210_South_Text_MarcoDefeat
	msgbox Route210_South_Text_MarcoAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Wyatt::
	trainerbattle_single TRAINER_JOGGER_WYATT_R210, Route210_South_Text_WyattIntro, Route210_South_Text_WyattDefeat
	msgbox Route210_South_Text_WyattAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_GrassBoy::
	trainerbattle_single TRAINER_BOY_GRASS_R210, Route210_South_Text_GrassBoyIntro, Route210_South_Text_GrassBoyDefeat
	msgbox Route210_South_Text_GrassBoyAfter, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_Psyduck::
	lock
	faceplayer
	msgbox Route210_South_Text_PsyduckHeadache, MSGBOX_DEFAULT
	release
	end

Route210_South_EventScript_PsyduckBlock::
	lockall
	msgbox Route210_South_Text_PsyduckBlock, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route210_South_Movement_PushSouth
	waitmovement 0
	releaseall
	end

Route210_South_Movement_PushSouth:
	walk_down
	step_end

Route210_South_EventScript_Cynthia::
	msgbox Route210_South_Text_CynthiaHint, MSGBOX_NPC
	end

Route210_South_EventScript_ItemHyperPotion::
	finditem ITEM_HYPER_POTION
	end

Route210_South_EventScript_CafeSign::
	msgbox Route210_South_Text_CafeSign, MSGBOX_SIGN
	end

Route210_South_EventScript_RouteSign::
	msgbox Route210_South_Text_RouteSign, MSGBOX_SIGN
	end

Route210_South_Text_TeriIntro:
	.string "TERI: Ready, Tia? Twin combo!$"

Route210_South_Text_TeriDefeat:
	.string "TERI: We stumbled...$"

Route210_South_Text_TeriAfter:
	.string "TERI: Those PSYDUCK look miserable.$"

Route210_South_Text_TeriNotEnough:
	.string "TERI: Bring two POKéMON!$"

Route210_South_Text_TiaIntro:
	.string "TIA: We never lose together!$"

Route210_South_Text_TiaDefeat:
	.string "TIA: Oh no!$"

Route210_South_Text_TiaAfter:
	.string "TIA: Cafe milk helps headaches...maybe.$"

Route210_South_Text_TiaNotEnough:
	.string "TIA: Two on two, please!$"

Route210_South_Text_KahlilIntro:
	.string "Breeding takes patience.\n"
	.string "Battling builds character!$"

Route210_South_Text_KahlilDefeat:
	.string "Character noted...$"

Route210_South_Text_KahlilAfter:
	.string "Solaceon Day Care taught me a lot.$"

Route210_South_Text_AmberIntro:
	.string "Soft grass, soft hearts?\n"
	.string "Not in my battles!$"

Route210_South_Text_AmberDefeat:
	.string "Too soft after all...$"

Route210_South_Text_AmberAfter:
	.string "Route 215 east gets rainy.$"

Route210_South_Text_BelleIntro:
	.string "BELLE: Pa and I make a team!$"

Route210_South_Text_PaIntro:
	.string "PA: Stick with family, kid!$"

Route210_South_Text_BellePaDefeat:
	.string "Family plan failed...$"

Route210_South_Text_BelleAfter:
	.string "BELLE: Pa still tips the waitress.$"

Route210_South_Text_PaAfter:
	.string "PA: Cafe coffee wakes me up.$"

Route210_South_Text_BelleNotEnough:
	.string "BELLE: Need two POKéMON!$"

Route210_South_Text_PaNotEnough:
	.string "PA: Bring a pair!$"

Route210_South_Text_MarcoIntro:
	.string "Ranch trails toughen you up!\n"
	.string "Show me your grit!$"

Route210_South_Text_MarcoDefeat:
	.string "Tough as nails...$"

Route210_South_Text_MarcoAfter:
	.string "Mind the muddy path in the rain.$"

Route210_South_Text_WyattIntro:
	.string "Mile twenty--and a battle!$"

Route210_South_Text_WyattDefeat:
	.string "Hit the wall...$"

Route210_South_Text_WyattAfter:
	.string "Hydrate. Moomoo Milk works wonders.$"

Route210_South_Text_GrassBoyIntro:
	.string "Surprise from the tall grass!$"

Route210_South_Text_GrassBoyDefeat:
	.string "Spotted too soon...$"

Route210_South_Text_GrassBoyAfter:
	.string "Ninja lessons can wait.$"

Route210_South_Text_PsyduckHeadache:
	.string "PSYDUCK: Psyyaaa...\p"
	.string "It clutches its head.\n"
	.string "A splitting headache!$"

Route210_South_Text_PsyduckBlock:
	.string "The PSYDUCK have splitting headaches\n"
	.string "and won't budge!\p"
	.string "You'll need a SecretPotion later.$"

Route210_South_Text_CynthiaHint:
	.string "Those PSYDUCK need special medicine.\n"
	.string "Keep exploring--help will come.$"

Route210_South_Text_CafeSign:
	.string "CAFE CABIN\n"
	.string "Warm drinks for weary Trainers$"

Route210_South_Text_RouteSign:
	.string "ROUTE 210\n"
	.string "Solaceon Town - Celestic Town$"
Route210_South_EventScript_PlatNpc0::
	msgbox Route210_South_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

Route210_South_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route210_South_EventScript_PlatNpc1::
	msgbox Route210_South_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

Route210_South_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route210_South_EventScript_PlatNpc2::
	msgbox Route210_South_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

Route210_South_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route210_South_EventScript_PlatNpc5::
	msgbox Route210_South_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

Route210_South_EventScript_PlatNpc5_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route210_South_EventScript_PlatNpc7::
	msgbox Route210_South_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

Route210_South_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route210_South_EventScript_PlatNpc8::
	msgbox Route210_South_EventScript_PlatNpc8_Text, MSGBOX_NPC
	end

Route210_South_EventScript_PlatNpc8_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route210_South_EventScript_PlatNpc15::
	msgbox Route210_South_EventScript_PlatNpc15_Text, MSGBOX_NPC
	end

Route210_South_EventScript_PlatNpc15_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"



Route210_South_EventScript_NinjaBoyFabian::
	trainerbattle_single TRAINER_NINJA_BOY_FABIAN, Route210_South_EventScript_NinjaBoyFabian_Intro, Route210_South_EventScript_NinjaBoyFabian_Defeat
	msgbox Route210_South_EventScript_NinjaBoyFabian_After, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_NinjaBoyFabian_Intro:
	.string "Hold up! A battle will tell me how\n"
	.string "far you have come.$"

Route210_South_EventScript_NinjaBoyFabian_Defeat:
	.string "That was cleaner than I expected.$"

Route210_South_EventScript_NinjaBoyFabian_After:
	.string "Keep moving. Every route has a\n"
	.string "lesson if you look for it.$"

Route210_South_EventScript_NinjaBoyBrennan::
	trainerbattle_single TRAINER_NINJA_BOY_BRENNAN, Route210_South_EventScript_NinjaBoyBrennan_Intro, Route210_South_EventScript_NinjaBoyBrennan_Defeat
	msgbox Route210_South_EventScript_NinjaBoyBrennan_After, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_NinjaBoyBrennan_Intro:
	.string "Hold up! A battle will tell me how\n"
	.string "far you have come.$"

Route210_South_EventScript_NinjaBoyBrennan_Defeat:
	.string "That was cleaner than I expected.$"

Route210_South_EventScript_NinjaBoyBrennan_After:
	.string "Keep moving. Every route has a\n"
	.string "lesson if you look for it.$"

Route210_South_EventScript_NinjaBoyBruce::
	trainerbattle_single TRAINER_NINJA_BOY_BRUCE, Route210_South_EventScript_NinjaBoyBruce_Intro, Route210_South_EventScript_NinjaBoyBruce_Defeat
	msgbox Route210_South_EventScript_NinjaBoyBruce_After, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_NinjaBoyBruce_Intro:
	.string "Hold up! A battle will tell me how\n"
	.string "far you have come.$"

Route210_South_EventScript_NinjaBoyBruce_Defeat:
	.string "That was cleaner than I expected.$"

Route210_South_EventScript_NinjaBoyBruce_After:
	.string "Keep moving. Every route has a\n"
	.string "lesson if you look for it.$"

Route210_South_EventScript_BelleAndPaAvaAndMatt::
	trainerbattle_single TRAINER_BELLE_AND_PA_AVA_AND_MATT, Route210_South_EventScript_BelleAndPaAvaAndMatt_Intro, Route210_South_EventScript_BelleAndPaAvaAndMatt_Defeat
	msgbox Route210_South_EventScript_BelleAndPaAvaAndMatt_After, MSGBOX_AUTOCLOSE
	end

Route210_South_EventScript_BelleAndPaAvaAndMatt_Intro:
	.string "Hold up! A battle will tell me how\n"
	.string "far you have come.$"

Route210_South_EventScript_BelleAndPaAvaAndMatt_Defeat:
	.string "That was cleaner than I expected.$"

Route210_South_EventScript_BelleAndPaAvaAndMatt_After:
	.string "Keep moving. Every route has a\n"
	.string "lesson if you look for it.$"

