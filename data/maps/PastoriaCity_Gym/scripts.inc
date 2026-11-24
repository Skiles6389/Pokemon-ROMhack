PastoriaCity_Gym_MapScripts::
	.byte 0

PastoriaCity_Gym_EventScript_CrasherWake::
	lock
	faceplayer
	goto_if_eq VAR_PASTORIA_CITY_STATE, 0, PastoriaCity_Gym_EventScript_WakeWaitBarry
	trainerbattle_single TRAINER_LEADER_CRASHER_WAKE, PastoriaCity_Gym_Text_WakeIntro, PastoriaCity_Gym_Text_WakeDefeat, PastoriaCity_Gym_EventScript_WakeDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_PASTORIA_GYM_TM, PastoriaCity_Gym_EventScript_GiveTM
	msgbox PastoriaCity_Gym_Text_WakeAfter, MSGBOX_DEFAULT
	release
	end

PastoriaCity_Gym_EventScript_WakeWaitBarry::
	msgbox PastoriaCity_Gym_Text_WakeWaitBarry, MSGBOX_DEFAULT
	release
	end

PastoriaCity_Gym_EventScript_WakeDefeated::
	message PastoriaCity_Gym_Text_ReceivedFenBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox PastoriaCity_Gym_Text_FenBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE05_GET
	setvar VAR_PASTORIA_CITY_STATE, 2
	clearflag FLAG_HIDE_PASTORIA_GALACTIC_GRUNT
	clearflag FLAG_HIDE_PASTORIA_WAKE_CAMEO
	goto PastoriaCity_Gym_EventScript_GiveTM
	end

PastoriaCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_BRINE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_PASTORIA_GYM_TM
	msgbox PastoriaCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

PastoriaCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE05_GET, PastoriaCity_Gym_EventScript_GuideVictory
	msgbox PastoriaCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

PastoriaCity_Gym_EventScript_GuideVictory::
	msgbox PastoriaCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

PastoriaCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE05_GET, PastoriaCity_Gym_EventScript_StatueWon
	msgbox PastoriaCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

PastoriaCity_Gym_EventScript_StatueWon::
	msgbox PastoriaCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

PastoriaCity_Gym_EventScript_Jacky::
	trainerbattle_single TRAINER_TUBER_JACKY_PASTORIA, PastoriaCity_Gym_Text_JackyIntro, PastoriaCity_Gym_Text_JackyDefeat
	msgbox PastoriaCity_Gym_Text_JackyAfter, MSGBOX_AUTOCLOSE
	end

PastoriaCity_Gym_Text_JackyIntro:
	.string "Cannonball into battle!\n"
	.string "Water types make the biggest splash!$"

PastoriaCity_Gym_Text_JackyDefeat:
	.string "I wiped out...$"

PastoriaCity_Gym_Text_JackyAfter:
	.string "Keep your footing on the bridges.\n"
	.string "One slip and you're soaked!$"

PastoriaCity_Gym_EventScript_Caitlyn::
	trainerbattle_single TRAINER_TUBER_CAITLYN_PASTORIA, PastoriaCity_Gym_Text_CaitlynIntro, PastoriaCity_Gym_Text_CaitlynDefeat
	msgbox PastoriaCity_Gym_Text_CaitlynAfter, MSGBOX_AUTOCLOSE
	end

PastoriaCity_Gym_Text_CaitlynIntro:
	.string "Don't drip on my turf!\n"
	.string "I'll wash you out myself!$"

PastoriaCity_Gym_Text_CaitlynDefeat:
	.string "Totally drenched...$"

PastoriaCity_Gym_Text_CaitlynAfter:
	.string "WAKE loves a fair fight.\n"
	.string "Bring your best tide.$"

PastoriaCity_Gym_EventScript_Damian::
	trainerbattle_single TRAINER_SAILOR_DAMIAN_PASTORIA, PastoriaCity_Gym_Text_DamianIntro, PastoriaCity_Gym_Text_DamianDefeat
	msgbox PastoriaCity_Gym_Text_DamianAfter, MSGBOX_AUTOCLOSE
	end

PastoriaCity_Gym_Text_DamianIntro:
	.string "All hands on deck!\n"
	.string "This Gym runs on sea discipline!$"

PastoriaCity_Gym_Text_DamianDefeat:
	.string "Permission to recover granted...$"

PastoriaCity_Gym_Text_DamianAfter:
	.string "Watch the side lanes. Trainers\n"
	.string "hide where the water laps.$"

PastoriaCity_Gym_EventScript_Samson::
	trainerbattle_single TRAINER_SAILOR_SAMSON_PASTORIA, PastoriaCity_Gym_Text_SamsonIntro, PastoriaCity_Gym_Text_SamsonDefeat
	msgbox PastoriaCity_Gym_Text_SamsonAfter, MSGBOX_AUTOCLOSE
	end

PastoriaCity_Gym_Text_SamsonIntro:
	.string "I've sailed rougher than this.\n"
	.string "Show me your sea legs!$"

PastoriaCity_Gym_Text_SamsonDefeat:
	.string "Capsized by a landlubber...$"

PastoriaCity_Gym_Text_SamsonAfter:
	.string "Electric moves sting Water hard.\n"
	.string "Pack a shock if you can.$"

PastoriaCity_Gym_EventScript_Erick::
	trainerbattle_single TRAINER_FISHERMAN_ERICK_PASTORIA, PastoriaCity_Gym_Text_ErickIntro, PastoriaCity_Gym_Text_ErickDefeat
	msgbox PastoriaCity_Gym_Text_ErickAfter, MSGBOX_AUTOCLOSE
	end

PastoriaCity_Gym_Text_ErickIntro:
	.string "Hooked a challenger!\n"
	.string "Let's see who gets reeled in!$"

PastoriaCity_Gym_Text_ErickDefeat:
	.string "Line snapped...$"

PastoriaCity_Gym_Text_ErickAfter:
	.string "Patience wins long battles.\n"
	.string "Don't rush the Leader.$"

PastoriaCity_Gym_EventScript_Walter::
	trainerbattle_single TRAINER_FISHERMAN_WALTER_PASTORIA, PastoriaCity_Gym_Text_WalterIntro, PastoriaCity_Gym_Text_WalterDefeat
	msgbox PastoriaCity_Gym_Text_WalterAfter, MSGBOX_AUTOCLOSE
	end

PastoriaCity_Gym_Text_WalterIntro:
	.string "Quiet waters before the storm.\n"
	.string "You're the storm, aren't you?$"

PastoriaCity_Gym_Text_WalterDefeat:
	.string "The catch got away...$"

PastoriaCity_Gym_Text_WalterAfter:
	.string "WAKE's Floatzel is lightning in\n"
	.string "the water. Brace yourself!$"

PastoriaCity_Gym_Text_WakeWaitBarry:
	.string "CRASHER WAKE: There's a bouncing\n"
	.string "kid outside who wants you first!\p"
	.string "Settle that rivalry, then crash\n"
	.string "through my doors for real.$"

PastoriaCity_Gym_Text_GuideAdvice:
	.string "Yo! Ready to get soaked?\p"
	.string "CRASHER WAKE rides Water-types.\n"
	.string "Grass and Electric moves drain\l"
	.string "the pool fast!\p"
	.string "Tubers, Sailors, and Fishermen\n"
	.string "guard the bridges. Meet their\l"
	.string "eyes and they'll charge!$"

PastoriaCity_Gym_Text_GuideVictory:
	.string "Fen Badge secured! Nice surfing!\p"
	.string "I saw a shady character near the\n"
	.string "Great Marsh gate. Worth a look.$"

PastoriaCity_Gym_Text_Statue:
	.string "PASTORIA CITY POKéMON GYM\n"
	.string "LEADER: CRASHER WAKE$"

PastoriaCity_Gym_Text_StatueWon:
	.string "PASTORIA CITY POKéMON GYM\n"
	.string "LEADER: CRASHER WAKE\p"
	.string "Certified Trainers:\n"
	.string "{PLAYER}$"

PastoriaCity_Gym_Text_WakeIntro:
	.string "CRASHER WAKE: Crash! Splash!\n"
	.string "I'm CRASHER WAKE!\p"
	.string "I surf every wave Sinnoh throws,\n"
	.string "and my POKéMON ride right with me!\p"
	.string "You want the Fen Badge? Then\n"
	.string "bring a storm of your own!\p"
	.string "Let's make a tidal roar!$"

PastoriaCity_Gym_Text_WakeDefeat:
	.string "Whoa! You smashed right through\n"
	.string "my breakers! Outstanding!$"

PastoriaCity_Gym_Text_ReceivedFenBadge:
	.string "{PLAYER} received the FEN BADGE\n"
	.string "from CRASHER WAKE!$"

PastoriaCity_Gym_Text_FenBadgeInfo:
	.string "With the FEN BADGE, POKéMON up to\n"
	.string "Lv. 50 will obey you without fuss.\p"
	.string "And take this--my favorite rainy-\n"
	.string "day technique!$"

PastoriaCity_Gym_Text_ExplainTM:
	.string "That TM contains BRINE!\p"
	.string "It hits harder when the foe's HP\n"
	.string "is half or less. Finish strong!\p"
	.string "Crash onward, champ!$"

PastoriaCity_Gym_Text_WakeAfter:
	.string "CRASHER WAKE: Keep riding those\n"
	.string "highs! If TEAM GALACTIC stirs the\l"
	.string "lake, give them a proper dunking!$"
