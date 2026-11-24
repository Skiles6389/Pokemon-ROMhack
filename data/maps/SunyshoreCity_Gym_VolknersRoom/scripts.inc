SunyshoreCity_Gym_VolknersRoom_MapScripts::
	.byte 0

SunyshoreCity_Gym_EventScript_Volkner::
	lock
	faceplayer
	trainerbattle_single TRAINER_LEADER_VOLKNER, SunyshoreCity_Gym_Text_VolknerIntro, SunyshoreCity_Gym_Text_VolknerDefeat, SunyshoreCity_Gym_EventScript_VolknerDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_SUNYSHORE_GYM_TM, SunyshoreCity_Gym_EventScript_GiveTM
	msgbox SunyshoreCity_Gym_Text_VolknerAfter, MSGBOX_DEFAULT
	release
	end

SunyshoreCity_Gym_EventScript_VolknerDefeated::
	message SunyshoreCity_Gym_Text_ReceivedBeaconBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox SunyshoreCity_Gym_Text_BeaconBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE08_GET
	goto SunyshoreCity_Gym_EventScript_GiveTM
	end

SunyshoreCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_DISCHARGE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_SUNYSHORE_GYM_TM
	msgbox SunyshoreCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

SunyshoreCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE08_GET, SunyshoreCity_Gym_EventScript_StatueWon
	msgbox SunyshoreCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

SunyshoreCity_Gym_EventScript_StatueWon::
	msgbox SunyshoreCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

SunyshoreCity_Gym_Text_VolknerIntro:
	.string "I'm VOLKNER, the Sunyshore Gym Leader!\n"
	.string "Electric types never get boring when you\l"
	.string "keep inventing new circuits.\p"
	.string "Let's see if you can short my design!$"

SunyshoreCity_Gym_Text_VolknerDefeat:
	.string "You overcharged my plans...$"

SunyshoreCity_Gym_Text_VolknerAfter:
	.string "Take Route 223 north when you're ready.\n"
	.string "Victory Road waits beyond the surf.$"

SunyshoreCity_Gym_Text_ReceivedBeaconBadge:
	.string "{PLAYER} received the BEACON BADGE\n"
	.string "from VOLKNER.$"

SunyshoreCity_Gym_Text_BeaconBadgeInfo:
	.string "With the BEACON BADGE, every machine\n"
	.string "recognizes your team's full voltage.$"

SunyshoreCity_Gym_Text_ExplainTM:
	.string "That's TM Discharge.\n"
	.string "It shocks everything around the user.$"

SunyshoreCity_Gym_Text_Statue:
	.string "Sunyshore City Pokemon Gym$"

SunyshoreCity_Gym_Text_StatueWon:
	.string "Sunyshore City Pokemon Gym\n"
	.string "Certified Trainer: {PLAYER}$"
