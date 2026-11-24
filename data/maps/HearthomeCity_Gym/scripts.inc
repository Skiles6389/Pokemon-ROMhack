HearthomeCity_Gym_MapScripts::
	.byte 0

HearthomeCity_Gym_EventScript_Fantina::
	trainerbattle_single TRAINER_LEADER_FANTINA, HearthomeCity_Gym_Text_FantinaIntro, HearthomeCity_Gym_Text_FantinaDefeat, HearthomeCity_Gym_EventScript_FantinaDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_HEARTHOME_GYM_TM, HearthomeCity_Gym_EventScript_GiveTM
	msgbox HearthomeCity_Gym_Text_FantinaPost, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Gym_EventScript_FantinaDefeated::
	message HearthomeCity_Gym_Text_ReceivedRelicBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox HearthomeCity_Gym_Text_RelicBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE03_GET
	clearflag FLAG_HIDE_HEARTHOME_FANTINA
	goto HearthomeCity_Gym_EventScript_GiveTM
	end

HearthomeCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_SHADOW_BALL
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_HEARTHOME_GYM_TM
	msgbox HearthomeCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Gym_EventScript_Molly::
	trainerbattle_single TRAINER_LASS_MOLLY_HEARTHOME, HearthomeCity_Gym_Text_MollyIntro, HearthomeCity_Gym_Text_MollyDefeat
	msgbox HearthomeCity_Gym_Text_MollyAfter, MSGBOX_AUTOCLOSE
	end

HearthomeCity_Gym_EventScript_Karina::
	trainerbattle_single TRAINER_SCHOOL_KID_KARINA_HEARTHOME, HearthomeCity_Gym_Text_KarinaIntro, HearthomeCity_Gym_Text_KarinaDefeat
	msgbox HearthomeCity_Gym_Text_KarinaAfter, MSGBOX_AUTOCLOSE
	end

HearthomeCity_Gym_EventScript_Bryce::
	trainerbattle_single TRAINER_ACE_TRAINER_BRYCE_HEARTHOME, HearthomeCity_Gym_Text_BryceIntro, HearthomeCity_Gym_Text_BryceDefeat
	msgbox HearthomeCity_Gym_Text_BryceAfter, MSGBOX_AUTOCLOSE
	end

HearthomeCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE03_GET, HearthomeCity_Gym_EventScript_GuideVictory
	msgbox HearthomeCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Gym_EventScript_GuideVictory::
	msgbox HearthomeCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE03_GET, HearthomeCity_Gym_EventScript_StatueWon
	msgbox HearthomeCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

HearthomeCity_Gym_EventScript_StatueWon::
	msgbox HearthomeCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

HearthomeCity_Gym_Text_GuideAdvice:
	.string "Yo! Champ-to-be!\p"
	.string "FANTINA uses Ghost-type POKéMON.\n"
	.string "Dark and Ghost moves hit hard here.\p"
	.string "Torchlit side rooms hide Trainers.\n"
	.string "Clear them, then face the Leader!$"

HearthomeCity_Gym_Text_GuideVictory:
	.string "That Relic Badge looks great on you!\n"
	.string "BARRY is pacing near the east gate.$"

HearthomeCity_Gym_Text_Statue:
	.string "HEARTHOME CITY POKéMON GYM\p"
	.string "LEADER: FANTINA$"

HearthomeCity_Gym_Text_StatueWon:
	.string "HEARTHOME CITY POKéMON GYM\p"
	.string "LEADER: FANTINA\p"
	.string "Certified Trainers:\n"
	.string "{PLAYER}$"

HearthomeCity_Gym_Text_MollyIntro:
	.string "Boo! Did I scare you?$"

HearthomeCity_Gym_Text_MollyDefeat:
	.string "My ghosts floated away...$"

HearthomeCity_Gym_Text_MollyAfter:
	.string "FANTINA's dance is even spookier.$"

HearthomeCity_Gym_Text_KarinaIntro:
	.string "I studied every Ghost type!\n"
	.string "Pop quiz--battle!$"

HearthomeCity_Gym_Text_KarinaDefeat:
	.string "I need more homework...$"

HearthomeCity_Gym_Text_KarinaAfter:
	.string "Dark-type moves ignore immunities.\n"
	.string "Keep that in mind!$"

HearthomeCity_Gym_Text_BryceIntro:
	.string "Only the calm reach FANTINA.\n"
	.string "Prove your nerve!$"

HearthomeCity_Gym_Text_BryceDefeat:
	.string "Chilling composure...$"

HearthomeCity_Gym_Text_BryceAfter:
	.string "The Leader awaits on the dais.$"

HearthomeCity_Gym_Text_FantinaIntro:
	.string "I am FANTINA, the Gym Leader!\p"
	.string "I adore Contests, but battling lets\n"
	.string "Ghost POKéMON truly shine!\p"
	.string "Can you keep your feet in this dark\n"
	.string "dance hall? Ooh la la--let us begin!$"

HearthomeCity_Gym_Text_FantinaDefeat:
	.string "Magnifique! You outshone my ghosts!$"

HearthomeCity_Gym_Text_ReceivedRelicBadge:
	.string "{PLAYER} received the RELIC BADGE\n"
	.string "from FANTINA!$"

HearthomeCity_Gym_Text_RelicBadgeInfo:
	.string "With the RELIC BADGE, your journey\n"
	.string "through Sinnoh presses onward.\p"
	.string "And take this--my favorite TM!$"

HearthomeCity_Gym_Text_ExplainTM:
	.string "That TM contains SHADOW BALL.\p"
	.string "It may also lower Sp. Def!\n"
	.string "A dramatic flourish for any team!$"

HearthomeCity_Gym_Text_FantinaPost:
	.string "FANTINA: Contests and Gym battles\n"
	.string "both reward passion!\p"
	.string "Visit the Contest Hall anytime--\n"
	.string "even if the stage is still warming up!$"
