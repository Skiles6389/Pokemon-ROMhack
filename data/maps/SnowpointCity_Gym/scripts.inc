SnowpointCity_Gym_MapScripts::
	.byte 0

SnowpointCity_Gym_EventScript_Candice::
	lock
	faceplayer
	trainerbattle_single TRAINER_LEADER_CANDICE, SnowpointCity_Gym_Text_CandiceIntro, SnowpointCity_Gym_Text_CandiceDefeat, SnowpointCity_Gym_EventScript_CandiceDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_SNOWPOINT_GYM_TM, SnowpointCity_Gym_EventScript_GiveTM
	msgbox SnowpointCity_Gym_Text_CandiceAfter, MSGBOX_DEFAULT
	release
	end

SnowpointCity_Gym_EventScript_CandiceDefeated::
	message SnowpointCity_Gym_Text_ReceivedIcicleBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox SnowpointCity_Gym_Text_IcicleBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE07_GET
	goto SnowpointCity_Gym_EventScript_GiveTM
	end

SnowpointCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_AVALANCHE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_SNOWPOINT_GYM_TM
	msgbox SnowpointCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

SnowpointCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE07_GET, SnowpointCity_Gym_EventScript_GuideVictory
	msgbox SnowpointCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

SnowpointCity_Gym_EventScript_GuideVictory::
	msgbox SnowpointCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

SnowpointCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE07_GET, SnowpointCity_Gym_EventScript_StatueWon
	msgbox SnowpointCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

SnowpointCity_Gym_EventScript_StatueWon::
	msgbox SnowpointCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

SnowpointCity_Gym_EventScript_Mia::
	trainerbattle_single TRAINER_SKIER_SNOWPOINT_A, SnowpointCity_Gym_Text_MiaIntro, SnowpointCity_Gym_Text_MiaDefeat
	msgbox SnowpointCity_Gym_Text_MiaAfter, MSGBOX_AUTOCLOSE
	end

SnowpointCity_Gym_EventScript_Trina::
	trainerbattle_single TRAINER_ACE_SNOWPOINT_B, SnowpointCity_Gym_Text_TrinaIntro, SnowpointCity_Gym_Text_TrinaDefeat
	msgbox SnowpointCity_Gym_Text_TrinaAfter, MSGBOX_AUTOCLOSE
	end

SnowpointCity_Gym_Text_CandiceIntro:
	.string "I'm CANDICE, Snowpoint's Gym Leader!\n"
	.string "Ice types shine when the pressure peaks.\p"
	.string "Let's see if your fire can melt this ice!$"

SnowpointCity_Gym_Text_CandiceDefeat:
	.string "You melted right through...$"

SnowpointCity_Gym_Text_CandiceAfter:
	.string "Lake Acuity still holds Galactic's shadow.\n"
	.string "Stay sharp out there.$"

SnowpointCity_Gym_Text_ReceivedIcicleBadge:
	.string "{PLAYER} received the ICICLE BADGE\n"
	.string "from CANDICE.$"

SnowpointCity_Gym_Text_IcicleBadgeInfo:
	.string "With the ICICLE BADGE, more machines\n"
	.string "answer your POK-MON's strength.$"

SnowpointCity_Gym_Text_ExplainTM:
	.string "That TM is AVALANCHE.\n"
	.string "It hits harder if you took damage first.$"

SnowpointCity_Gym_Text_GuideAdvice:
	.string "CANDICE loves Ice types.\n"
	.string "Fire, Fighting, Rock, and Steel crack ice.$"

SnowpointCity_Gym_Text_GuideVictory:
	.string "You earned the Icicle Badge!\n"
	.string "Snowpoint is proud of that fight.$"

SnowpointCity_Gym_Text_Statue:
	.string "SNOWPOINT CITY POK-MON GYM$"

SnowpointCity_Gym_Text_StatueWon:
	.string "SNOWPOINT CITY POK-MON GYM\p"
	.string "CANDICE'S CERTIFIED TRAINERS:\n"
	.string "{PLAYER}$"

SnowpointCity_Gym_Text_MiaIntro:
	.string "Ski trails lead straight into battle!$"

SnowpointCity_Gym_Text_MiaDefeat:
	.string "Wiped out on the slope...$"

SnowpointCity_Gym_Text_MiaAfter:
	.string "CANDICE trains harder than any blizzard.$"

SnowpointCity_Gym_Text_TrinaIntro:
	.string "Cool strategy beats cold feet!$"

SnowpointCity_Gym_Text_TrinaDefeat:
	.string "Frostbitten pride...$"

SnowpointCity_Gym_Text_TrinaAfter:
	.string "Keep your Fire moves ready for CANDICE.$"
