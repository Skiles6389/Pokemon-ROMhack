VeilstoneCity_MassageHouse_MapScripts::
	.byte 0

VeilstoneCity_MassageHouse_EventScript_Masseuse::
	lock
	faceplayer
	goto_if_lt VAR_MASSAGE_COOLDOWN_STEP_COUNTER, 500, VeilstoneCity_MassageHouse_EventScript_RateMonFriendship
	msgbox VeilstoneCity_MassageHouse_Text_OfferMassage, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, VeilstoneCity_MassageHouse_EventScript_DeclineMassage
	msgbox VeilstoneCity_MassageHouse_Text_WhichMon
	special ChoosePartyMon
	lock
	faceplayer
	goto_if_ge VAR_0x8004, PARTY_SIZE, VeilstoneCity_MassageHouse_EventScript_DeclineMassage
	specialvar VAR_RESULT, ScriptGetPartyMonSpecies
	goto_if_eq VAR_RESULT, SPECIES_EGG, VeilstoneCity_MassageHouse_EventScript_CantMassageEgg
	msgbox VeilstoneCity_MassageHouse_Text_SettleIn
	closemessage
	fadescreen FADE_TO_BLACK
	playfanfare MUS_HEAL
	waitfanfare
	special DaisyMassageServices
	fadescreen FADE_FROM_BLACK
	special BufferMonNickname
	msgbox VeilstoneCity_MassageHouse_Text_AllDone
	release
	end

VeilstoneCity_MassageHouse_EventScript_CantMassageEgg::
	msgbox VeilstoneCity_MassageHouse_Text_CantMassageEgg
	release
	end

VeilstoneCity_MassageHouse_EventScript_DeclineMassage::
	msgbox VeilstoneCity_MassageHouse_Text_DeclineMassage
	release
	end

VeilstoneCity_MassageHouse_EventScript_RateMonFriendship::
	msgbox VeilstoneCity_MassageHouse_Text_LetMeSeeFirstMon
	specialvar VAR_RESULT, GetLeadMonFriendship
	switch VAR_RESULT
	case 0, VeilstoneCity_MassageHouse_EventScript_Friendship0
	case 1, VeilstoneCity_MassageHouse_EventScript_Friendship1
	case 2, VeilstoneCity_MassageHouse_EventScript_Friendship2
	case 3, VeilstoneCity_MassageHouse_EventScript_Friendship3
	case 4, VeilstoneCity_MassageHouse_EventScript_Friendship4
	case 5, VeilstoneCity_MassageHouse_EventScript_Friendship5
	case 6, VeilstoneCity_MassageHouse_EventScript_Friendship6
	end

VeilstoneCity_MassageHouse_EventScript_Friendship0::
	msgbox VeilstoneCity_MassageHouse_Text_Friendship0
	release
	end

VeilstoneCity_MassageHouse_EventScript_Friendship1::
	msgbox VeilstoneCity_MassageHouse_Text_Friendship1
	release
	end

VeilstoneCity_MassageHouse_EventScript_Friendship2::
	msgbox VeilstoneCity_MassageHouse_Text_Friendship2
	release
	end

VeilstoneCity_MassageHouse_EventScript_Friendship3::
	msgbox VeilstoneCity_MassageHouse_Text_Friendship3
	release
	end

VeilstoneCity_MassageHouse_EventScript_Friendship4::
	msgbox VeilstoneCity_MassageHouse_Text_Friendship4
	release
	end

VeilstoneCity_MassageHouse_EventScript_Friendship5::
	msgbox VeilstoneCity_MassageHouse_Text_Friendship5
	release
	end

VeilstoneCity_MassageHouse_EventScript_Friendship6::
	msgbox VeilstoneCity_MassageHouse_Text_Friendship6
	release
	end

VeilstoneCity_MassageHouse_EventScript_Boy::
	msgbox VeilstoneCity_MassageHouse_Text_Boy, MSGBOX_NPC
	end

VeilstoneCity_MassageHouse_Text_Boy:
	.string "Mom's hands are magic. My\n"
	.string "POKéMON falls asleep every time!$"

VeilstoneCity_MassageHouse_Text_OfferMassage:
	.string "Welcome to my little parlor.\p"
	.string "A good massage melts away stress\n"
	.string "and brings POKéMON closer to\l"
	.string "their Trainers.\p"
	.string "Would you like me to knead out the\n"
	.string "knots in one of yours?$"

VeilstoneCity_MassageHouse_Text_WhichMon:
	.string "Which POKéMON needs a rubdown?$"

VeilstoneCity_MassageHouse_Text_SettleIn:
	.string "Wonderful! Let your POKéMON settle\n"
	.string "in. This won't take long.$"

VeilstoneCity_MassageHouse_Text_AllDone:
	.string "There! {STR_VAR_1} looks relaxed and\n"
	.string "very happy.\p"
	.string "Come back after you've walked a\n"
	.string "good while together.$"

VeilstoneCity_MassageHouse_Text_CantMassageEgg:
	.string "Oh, that's an Egg! I can't massage\n"
	.string "something so delicate.$"

VeilstoneCity_MassageHouse_Text_DeclineMassage:
	.string "No rubdown today? Perfectly fine.\n"
	.string "Drop by whenever you like.$"

VeilstoneCity_MassageHouse_Text_LetMeSeeFirstMon:
	.string "Your POKéMON should rest a while\n"
	.string "before another massage.\p"
	.string "In the meantime, may I see the\n"
	.string "first POKéMON in your party?$"

VeilstoneCity_MassageHouse_Text_Friendship0:
	.string "Oh dear. It hardly trusts you at\n"
	.string "all.\p"
	.string "Be gentle with it, and be patient.$"

VeilstoneCity_MassageHouse_Text_Friendship1:
	.string "It stays guarded around you.\n"
	.string "Spend more time together.$"

VeilstoneCity_MassageHouse_Text_Friendship2:
	.string "It doesn't know you well yet.\n"
	.string "Walk with it, battle with it.$"

VeilstoneCity_MassageHouse_Text_Friendship3:
	.string "I can tell it's warming up to you.\n"
	.string "Keep it up!$"

VeilstoneCity_MassageHouse_Text_Friendship4:
	.string "It's quite fond of you. Look how\n"
	.string "it leans toward you!$"

VeilstoneCity_MassageHouse_Text_Friendship5:
	.string "What a happy face! It adores you.$"

VeilstoneCity_MassageHouse_Text_Friendship6:
	.string "It couldn't love you more!\n"
	.string "You two are inseparable.$"
