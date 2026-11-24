Route214_MapScripts::
	.byte 0

Route214_EventScript_Mitchell::
	trainerbattle_single TRAINER_PSYCHIC_MITCHELL_R214, Route214_Text_MitchellIntro, Route214_Text_MitchellDefeat
	msgbox Route214_Text_MitchellAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_MitchellIntro:
	.string "Quiet your thoughts.\n"
	.string "My POKéMON already know yours.$"

Route214_Text_MitchellDefeat:
	.string "Your will cut through mine...$"

Route214_Text_MitchellAfter:
	.string "Meditation helps on long roads.\n"
	.string "Try it before the next Gym.$"

Route214_EventScript_Abigail::
	trainerbattle_single TRAINER_PSYCHIC_ABIGAIL_R214, Route214_Text_AbigailIntro, Route214_Text_AbigailDefeat
	msgbox Route214_Text_AbigailAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_AbigailIntro:
	.string "I foresaw a strong Trainer\n"
	.string "walking this ridge. Was it you?$"

Route214_Text_AbigailDefeat:
	.string "Ah... the vision was incomplete.$"

Route214_Text_AbigailAfter:
	.string "Pastoria's marsh muddles focus.\n"
	.string "Stay sharp down south!$"

Route214_EventScript_Douglas::
	trainerbattle_single TRAINER_COLLECTOR_DOUGLAS_R214, Route214_Text_DouglasIntro, Route214_Text_DouglasDefeat
	msgbox Route214_Text_DouglasAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_DouglasIntro:
	.string "Rare specimens roam this trail!\n"
	.string "I'll catalog yours in battle!$"

Route214_Text_DouglasDefeat:
	.string "Noted... under “formidable.”$"

Route214_Text_DouglasAfter:
	.string "Collectors never stop looking.\n"
	.string "Every route has a prize.$"

Route214_EventScript_Brady::
	trainerbattle_single TRAINER_COLLECTOR_BRADY_R214, Route214_Text_BradyIntro, Route214_Text_BradyDefeat
	msgbox Route214_Text_BradyAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_BradyIntro:
	.string "Hold still! I need one more\n"
	.string "entry for my binder!$"

Route214_Text_BradyDefeat:
	.string "Page torn... metaphorically.$"

Route214_Text_BradyAfter:
	.string "A good collection needs guts,\n"
	.string "not just luck.$"

Route214_EventScript_Jamal::
	trainerbattle_single TRAINER_COLLECTOR_JAMAL_R214, Route214_Text_JamalIntro, Route214_Text_JamalDefeat
	msgbox Route214_Text_JamalAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_JamalIntro:
	.string "Trade you a story for a fight?\n"
	.string "No? Fine--battle it is!$"

Route214_Text_JamalDefeat:
	.string "That chapter ended too fast...$"

Route214_Text_JamalAfter:
	.string "I'll write you as the rival who\n"
	.string "kept walking south.$"

Route214_EventScript_Bryan::
	trainerbattle_single TRAINER_RUIN_MANIAC_BRYAN_R214, Route214_Text_BryanIntro, Route214_Text_BryanDefeat
	msgbox Route214_Text_BryanAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_BryanIntro:
	.string "Ruins whisper under these cliffs!\n"
	.string "Spar with me while I listen!$"

Route214_Text_BryanDefeat:
	.string "The stones... went quiet.$"

Route214_Text_BryanAfter:
	.string "Ruin Maniac Cave is sealed for\n"
	.string "now. Dig later, train today!$"

Route214_EventScript_Ronald::
	trainerbattle_single TRAINER_RUIN_MANIAC_RONALD_R214, Route214_Text_RonaldIntro, Route214_Text_RonaldDefeat
	msgbox Route214_Text_RonaldAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_RonaldIntro:
	.string "Ancient paths fork every which\n"
	.string "way. Pick mine--and lose!$"

Route214_Text_RonaldDefeat:
	.string "History favors the bold...$"

Route214_Text_RonaldAfter:
	.string "Spring Path can wait. Pastoria\n"
	.string "won't.$"

Route214_EventScript_Devon::
	trainerbattle_single TRAINER_BEAUTY_DEVON_R214, Route214_Text_DevonIntro, Route214_Text_DevonDefeat
	msgbox Route214_Text_DevonAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_DevonIntro:
	.string "Don't scuff the scenery!\n"
	.string "Battle pretty, or not at all.$"

Route214_Text_DevonDefeat:
	.string "Oh! You look good winning...$"

Route214_Text_DevonAfter:
	.string "Valor Lakefront has the best\n"
	.string "sunsets. Don't miss them!$"

Route214_EventScript_Carlos::
	trainerbattle_single TRAINER_GENTLEMAN_CARLOS_R214, Route214_Text_CarlosIntro, Route214_Text_CarlosDefeat
	msgbox Route214_Text_CarlosAfter, MSGBOX_AUTOCLOSE
	end

Route214_Text_CarlosIntro:
	.string "A discreet investigation, hmm?\n"
	.string "Let's call this a field test.$"

Route214_Text_CarlosDefeat:
	.string "Case closed--for me, that is.$"

Route214_Text_CarlosAfter:
	.string "Keep notes on odd footprints.\n"
	.string "Someone's stirring near the lake.$"

Route214_EventScript_CaveComingSoon::
	lockall
	msgbox Route214_Text_CaveComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route214_Movement_PushSouth
	waitmovement 0
	releaseall
	end

Route214_Movement_PushSouth:
	walk_down
	step_end

Route214_Text_CaveComingSoon:
	.string "Ruin Maniac Cave and Spring Path\n"
	.string "aren't open yet.$"

Route214_EventScript_RouteSign::
	msgbox Route214_Text_RouteSign, MSGBOX_SIGN
	end

Route214_Text_RouteSign:
	.string "ROUTE 214\n"
	.string "Veilstone City - Valor Lakefront$"
Route214_EventScript_PlatNpc0::
	msgbox Route214_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

Route214_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route214_EventScript_PlatNpc1::
	msgbox Route214_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

Route214_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route214_EventScript_PlatNpc2::
	msgbox Route214_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

Route214_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route214_EventScript_PlatNpc5::
	msgbox Route214_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

Route214_EventScript_PlatNpc5_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route214_EventScript_PlatNpc6::
	msgbox Route214_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

Route214_EventScript_PlatNpc6_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route214_EventScript_PlatNpc9::
	msgbox Route214_EventScript_PlatNpc9_Text, MSGBOX_NPC
	end

Route214_EventScript_PlatNpc9_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route214_EventScript_PiCarlos::
	trainerbattle_single TRAINER_PI_CARLOS, Route214_EventScript_PiCarlos_Intro, Route214_EventScript_PiCarlos_Defeat
	msgbox Route214_EventScript_PiCarlos_After, MSGBOX_AUTOCLOSE
	end

Route214_EventScript_PiCarlos_Intro:
	.string "A quiet route is the best place to\n"
	.string "test a sharp eye.$"

Route214_EventScript_PiCarlos_Defeat:
	.string "Case closed. You win.$"

Route214_EventScript_PiCarlos_After:
	.string "I will file this under lessons\n"
	.string "learned the hard way.$"

