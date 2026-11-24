Route215_MapScripts::
	.byte 0

Route215_EventScript_Derek::
	trainerbattle_single TRAINER_BLACK_BELT_DEREK_R215, Route215_Text_DerekIntro, Route215_Text_DerekDefeat
	msgbox Route215_Text_DerekAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Gregory::
	trainerbattle_single TRAINER_BLACK_BELT_GREGORY_R215, Route215_Text_GregoryIntro, Route215_Text_GregoryDefeat
	msgbox Route215_Text_GregoryAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Nathaniel::
	trainerbattle_single TRAINER_BLACK_BELT_NATHANIEL_R215, Route215_Text_NathanielIntro, Route215_Text_NathanielDefeat
	msgbox Route215_Text_NathanielAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Calvin::
	trainerbattle_single TRAINER_RUIN_MANIAC_CALVIN_R215, Route215_Text_CalvinIntro, Route215_Text_CalvinDefeat
	msgbox Route215_Text_CalvinAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Craig::
	trainerbattle_single TRAINER_JOGGER_CRAIG_R215, Route215_Text_CraigIntro, Route215_Text_CraigDefeat
	msgbox Route215_Text_CraigAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Scott::
	trainerbattle_single TRAINER_JOGGER_SCOTT_R215, Route215_Text_ScottIntro, Route215_Text_ScottDefeat
	msgbox Route215_Text_ScottAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Dennis::
	trainerbattle_single TRAINER_ACE_TRAINER_DENNIS_R215, Route215_Text_DennisIntro, Route215_Text_DennisDefeat
	msgbox Route215_Text_DennisAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Alexia::
	trainerbattle_single TRAINER_ACE_TRAINER_ALEXIA_R215, Route215_Text_AlexiaIntro, Route215_Text_AlexiaDefeat
	msgbox Route215_Text_AlexiaAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_Ernest::
	trainerbattle_single TRAINER_ACE_TRAINER_ERNEST_R215, Route215_Text_ErnestIntro, Route215_Text_ErnestDefeat
	msgbox Route215_Text_ErnestAfter, MSGBOX_AUTOCLOSE
	end

Route215_EventScript_PaybackGift::
	lock
	faceplayer
	goto_if_set FLAG_GOT_TM_PAYBACK_R215, Route215_EventScript_PaybackAfter
	msgbox Route215_Text_PaybackOffer, MSGBOX_DEFAULT
	giveitem ITEM_TM_PAYBACK
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_TM_PAYBACK_R215
	msgbox Route215_Text_PaybackExplain, MSGBOX_DEFAULT
	release
	end

Route215_EventScript_PaybackAfter::
	msgbox Route215_Text_PaybackAfter, MSGBOX_DEFAULT
	release
	end

Route215_EventScript_ItemEther::
	finditem ITEM_ETHER
	end

Route215_EventScript_ItemHyperPotion::
	finditem ITEM_HYPER_POTION
	end

Route215_EventScript_RouteSign::
	msgbox Route215_Text_RouteSign, MSGBOX_SIGN
	end

Route215_EventScript_VeilstoneSign::
	msgbox Route215_Text_VeilstoneSign, MSGBOX_SIGN
	end

Route215_Text_DerekIntro:
	.string "Rain or shine, my fists train!$"

Route215_Text_DerekDefeat:
	.string "Drenched in defeat...$"

Route215_Text_DerekAfter:
	.string "Mud builds character.$"

Route215_Text_GregoryIntro:
	.string "Karate cuts through the rain!$"

Route215_Text_GregoryDefeat:
	.string "My stance slipped...$"

Route215_Text_GregoryAfter:
	.string "Veilstone Gym waits ahead--soon.$"

Route215_Text_NathanielIntro:
	.string "Power punch! Feel the storm!$"

Route215_Text_NathanielDefeat:
	.string "Thunderous loss...$"

Route215_Text_NathanielAfter:
	.string "Keep your footing on wet roads.$"

Route215_Text_CalvinIntro:
	.string "Ruins whisper even in rainfall.$"

Route215_Text_CalvinDefeat:
	.string "History repeats--I lost.$"

Route215_Text_CalvinAfter:
	.string "Solaceon Ruins still call to me.$"

Route215_Text_CraigIntro:
	.string "Rainy miles make strong legs!$"

Route215_Text_CraigDefeat:
	.string "Splashed out...$"

Route215_Text_CraigAfter:
	.string "Watch for puddles near Veilstone.$"

Route215_Text_ScottIntro:
	.string "I'm warming up for a marathon!$"

Route215_Text_ScottDefeat:
	.string "Pulled a muscle...$"

Route215_Text_ScottAfter:
	.string "Stretch before every battle.$"

Route215_Text_DennisIntro:
	.string "Ace Trainers don't fear weather!$"

Route215_Text_DennisDefeat:
	.string "Your team shines brighter.$"

Route215_Text_DennisAfter:
	.string "Type coverage wins wet battles.$"

Route215_Text_AlexiaIntro:
	.string "Strategy over splash!$"

Route215_Text_AlexiaDefeat:
	.string "Outplayed...$"

Route215_Text_AlexiaAfter:
	.string "Veilstone City isn't open yet.$"

Route215_Text_ErnestIntro:
	.string "Final exam before the gate!$"

Route215_Text_ErnestDefeat:
	.string "You pass with honors.$"

Route215_Text_ErnestAfter:
	.string "Come back when Veilstone opens.$"

Route215_Text_PaybackOffer:
	.string "Took a cheap shot in the rain once.\n"
	.string "Never again!\p"
	.string "Take this TM--PAYBACK hits harder\n"
	.string "when you've already been hurt!$"

Route215_Text_PaybackExplain:
	.string "PAYBACK doubles power if you move\n"
	.string "after your foe. Wait, then strike!$"

Route215_Text_PaybackAfter:
	.string "Remember--patience fuels PAYBACK.$"

Route215_Text_RouteSign:
	.string "ROUTE 215\n"
	.string "Solaceon side - Veilstone side$"

Route215_Text_VeilstoneSign:
	.string "East: VEILSTONE CITY\n"
	.string "Gate ahead$"
