VeilstoneCity_Gym_MapScripts::
	.byte 0

VeilstoneCity_Gym_EventScript_Maylene::
	trainerbattle_single TRAINER_LEADER_MAYLENE, VeilstoneCity_Gym_Text_MayleneIntro, VeilstoneCity_Gym_Text_MayleneDefeat, VeilstoneCity_Gym_EventScript_MayleneDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_VEILSTONE_GYM_TM, VeilstoneCity_Gym_EventScript_GiveTM
	msgbox VeilstoneCity_Gym_Text_MayleneAfter, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_Gym_EventScript_MayleneDefeated::
	message VeilstoneCity_Gym_Text_ReceivedCobbleBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox VeilstoneCity_Gym_Text_CobbleBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE04_GET
	setvar VAR_VEILSTONE_CITY_STATE, 0
	clearflag FLAG_HIDE_VEILSTONE_MAYLENE
	clearflag FLAG_HIDE_VEILSTONE_COUNTERPART
	goto VeilstoneCity_Gym_EventScript_GiveTM
	end

VeilstoneCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_DRAIN_PUNCH
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_VEILSTONE_GYM_TM
	msgbox VeilstoneCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE04_GET, VeilstoneCity_Gym_EventScript_GuideVictory
	msgbox VeilstoneCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_Gym_EventScript_GuideVictory::
	msgbox VeilstoneCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE04_GET, VeilstoneCity_Gym_EventScript_StatueWon
	msgbox VeilstoneCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

VeilstoneCity_Gym_EventScript_StatueWon::
	msgbox VeilstoneCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

VeilstoneCity_Gym_EventScript_Colby::
	trainerbattle_single TRAINER_BLACK_BELT_COLBY_VEILSTONE, VeilstoneCity_Gym_Text_ColbyIntro, VeilstoneCity_Gym_Text_ColbyDefeat
	msgbox VeilstoneCity_Gym_Text_ColbyAfter, MSGBOX_AUTOCLOSE
	end

VeilstoneCity_Gym_Text_ColbyIntro:
	.string "Hrrah! Warm-ups are over!\n"
	.string "Show me how you take a punch!$"

VeilstoneCity_Gym_Text_ColbyDefeat:
	.string "Oof! Your guard held firm...$"

VeilstoneCity_Gym_Text_ColbyAfter:
	.string "Strong legs, strong core.\n"
	.string "That's the whole secret.$"

VeilstoneCity_Gym_EventScript_Darren::
	trainerbattle_single TRAINER_BLACK_BELT_DARREN_VEILSTONE, VeilstoneCity_Gym_Text_DarrenIntro, VeilstoneCity_Gym_Text_DarrenDefeat
	msgbox VeilstoneCity_Gym_Text_DarrenAfter, MSGBOX_AUTOCLOSE
	end

VeilstoneCity_Gym_Text_DarrenIntro:
	.string "I've been waiting for a worthy\n"
	.string "sparring partner!$"

VeilstoneCity_Gym_Text_DarrenDefeat:
	.string "Ha! That one rattled my teeth!$"

VeilstoneCity_Gym_Text_DarrenAfter:
	.string "MAYLENE trains harder than all of\n"
	.string "us put together.$"

VeilstoneCity_Gym_EventScript_Jeffery::
	trainerbattle_single TRAINER_BLACK_BELT_JEFFERY_VEILSTONE, VeilstoneCity_Gym_Text_JefferyIntro, VeilstoneCity_Gym_Text_JefferyDefeat
	msgbox VeilstoneCity_Gym_Text_JefferyAfter, MSGBOX_AUTOCLOSE
	end

VeilstoneCity_Gym_Text_JefferyIntro:
	.string "Silence your mind. Focus your\n"
	.string "fists. Now, fight!$"

VeilstoneCity_Gym_Text_JefferyDefeat:
	.string "My focus broke... well fought.$"

VeilstoneCity_Gym_Text_JefferyAfter:
	.string "Stay calm in a tight spot and the\n"
	.string "win comes to you.$"

VeilstoneCity_Gym_EventScript_Rafael::
	trainerbattle_single TRAINER_BLACK_BELT_RAFAEL_VEILSTONE, VeilstoneCity_Gym_Text_RafaelIntro, VeilstoneCity_Gym_Text_RafaelDefeat
	msgbox VeilstoneCity_Gym_Text_RafaelAfter, MSGBOX_AUTOCLOSE
	end

VeilstoneCity_Gym_Text_RafaelIntro:
	.string "Few trainers make it past my\n"
	.string "corner of the Gym!$"

VeilstoneCity_Gym_Text_RafaelDefeat:
	.string "You hit like a boulder...$"

VeilstoneCity_Gym_Text_RafaelAfter:
	.string "Go on. MAYLENE is waiting at the\n"
	.string "far end of the hall.$"

VeilstoneCity_Gym_Text_GuideAdvice:
	.string "Yo! Challenger in the making!\p"
	.string "MAYLENE leads with Fighting-type\n"
	.string "POKéMON. Flying and Psychic moves\l"
	.string "hit them hard!\p"
	.string "Black Belts guard the side rooms.\n"
	.string "Meet their eyes and they'll rush\l"
	.string "you, so choose your moment!$"

VeilstoneCity_Gym_Text_GuideVictory:
	.string "That was a knockout, champ!\p"
	.string "I hear TEAM GALACTIC has been\n"
	.string "busy around the old warehouse.\p"
	.string "Take care out there!$"

VeilstoneCity_Gym_Text_Statue:
	.string "VEILSTONE CITY POKéMON GYM\n"
	.string "LEADER: MAYLENE$"

VeilstoneCity_Gym_Text_StatueWon:
	.string "VEILSTONE CITY POKéMON GYM\n"
	.string "LEADER: MAYLENE\p"
	.string "Certified Trainers:\n"
	.string "{PLAYER}$"

VeilstoneCity_Gym_Text_MayleneIntro:
	.string "MAYLENE: I'm MAYLENE, Veilstone's\n"
	.string "Gym Leader!\p"
	.string "I train with my POKéMON every day,\n"
	.string "bruises and all.\p"
	.string "Strength isn't only muscle. It's\n"
	.string "trust and timing.\p"
	.string "Show me how you fight! I won't\n"
	.string "hold anything back!$"

VeilstoneCity_Gym_Text_MayleneDefeat:
	.string "Oh...that was a clean finish.\n"
	.string "You've earned this!$"

VeilstoneCity_Gym_Text_ReceivedCobbleBadge:
	.string "{PLAYER} received the COBBLE BADGE\n"
	.string "from MAYLENE!$"

VeilstoneCity_Gym_Text_CobbleBadgeInfo:
	.string "The COBBLE BADGE lets POKéMON that\n"
	.string "know FLY soar to towns you've\l"
	.string "already visited.\p"
	.string "Here, take this too. It's one of\n"
	.string "my favorite moves!$"

VeilstoneCity_Gym_Text_ExplainTM:
	.string "That TM contains DRAIN PUNCH.\p"
	.string "It hurts the foe and restores part\n"
	.string "of the damage to the user's HP.\p"
	.string "Fight smart and stay on your feet!$"

VeilstoneCity_Gym_Text_MayleneAfter:
	.string "MAYLENE: Keep that fighting spirit!\p"
	.string "Something odd is going on around\n"
	.string "the warehouse. Watch your back.$"
