OreburghCity_Gym_MapScripts::
	.byte 0

OreburghCity_Gym_EventScript_Roark::
	trainerbattle_single TRAINER_LEADER_ROARK, OreburghCity_Gym_Text_RoarkIntro, OreburghCity_Gym_Text_RoarkDefeat, OreburghCity_Gym_EventScript_RoarkDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_OREBURGH_GYM_TM, OreburghCity_Gym_EventScript_GiveTM
	msgbox OreburghCity_Gym_Text_RoarkPostBattle, MSGBOX_DEFAULT
	release
	end

OreburghCity_Gym_EventScript_RoarkDefeated::
	message OreburghCity_Gym_Text_ReceivedCoalBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox OreburghCity_Gym_Text_CoalBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE01_GET
	setvar VAR_OREBURGH_STATE, 3
	goto OreburghCity_Gym_EventScript_GiveTM
	end

OreburghCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_ROCK_TOMB
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_OREBURGH_GYM_TM
	msgbox OreburghCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

OreburghCity_Gym_EventScript_Jonathon::
	trainerbattle_single TRAINER_YOUNGSTER_JONATHON, OreburghCity_Gym_Text_JonathonIntro, OreburghCity_Gym_Text_JonathonDefeat
	msgbox OreburghCity_Gym_Text_JonathonPostBattle, MSGBOX_AUTOCLOSE
	end

OreburghCity_Gym_EventScript_Darius::
	trainerbattle_single TRAINER_YOUNGSTER_DARIUS, OreburghCity_Gym_Text_DariusIntro, OreburghCity_Gym_Text_DariusDefeat
	msgbox OreburghCity_Gym_Text_DariusPostBattle, MSGBOX_AUTOCLOSE
	end

OreburghCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE01_GET, OreburghCity_Gym_EventScript_GymGuidePostVictory
	msgbox OreburghCity_Gym_Text_GymGuideAdvice, MSGBOX_DEFAULT
	release
	end

OreburghCity_Gym_EventScript_GymGuidePostVictory::
	msgbox OreburghCity_Gym_Text_GymGuidePostVictory, MSGBOX_DEFAULT
	release
	end

OreburghCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE01_GET, OreburghCity_Gym_EventScript_StatueWon
	msgbox OreburghCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

OreburghCity_Gym_EventScript_StatueWon::
	msgbox OreburghCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

OreburghCity_Gym_Text_GymGuideAdvice:
	.string "Hey, future champ! First GYM, huh?\p"
	.string "ROARK trains Rock types. They shrug\n"
	.string "off Normal moves, but Water, Grass\l"
	.string "and Fighting moves crack them open.\p"
	.string "His CRANIDOS hits hard, so keep\n"
	.string "your POKéMON healthy. Good luck!$"

OreburghCity_Gym_Text_GymGuidePostVictory:
	.string "You beat ROARK! That COAL BADGE\n"
	.string "looks great on you!$"

OreburghCity_Gym_Text_Statue:
	.string "OREBURGH CITY POKéMON GYM\p"
	.string "LEADER: ROARK$"

OreburghCity_Gym_Text_StatueWon:
	.string "OREBURGH CITY POKéMON GYM\p"
	.string "LEADER: ROARK\p"
	.string "Certified Trainers:\n"
	.string "{PLAYER}$"

OreburghCity_Gym_Text_JonathonIntro:
	.string "My GEODUDE is tougher than any\n"
	.string "rock in the mine! Let's go!$"

OreburghCity_Gym_Text_JonathonDefeat:
	.string "Crumbled to gravel...$"

OreburghCity_Gym_Text_JonathonPostBattle:
	.string "I'll dig deeper and train harder.\n"
	.string "Next time I won't crack!$"

OreburghCity_Gym_Text_DariusIntro:
	.string "ROARK's waiting up top, but you\n"
	.string "have to get past me first!$"

OreburghCity_Gym_Text_DariusDefeat:
	.string "Aw, rocks! I lost!$"

OreburghCity_Gym_Text_DariusPostBattle:
	.string "ROARK's even harder than me.\n"
	.string "Way, way harder!$"

OreburghCity_Gym_Text_RoarkIntro:
	.string "So you made it up here. Good!\p"
	.string "I'm ROARK, LEADER of this GYM.\n"
	.string "My Rock POKéMON were raised in the\l"
	.string "mine, the same as me.\p"
	.string "Show me how you battle. I won't\n"
	.string "go easy on you!$"

OreburghCity_Gym_Text_RoarkDefeat:
	.string "Hah! That was a real battle.\n"
	.string "You've earned this BADGE!$"

OreburghCity_Gym_Text_ReceivedCoalBadge:
	.string "{PLAYER} received the COAL BADGE\n"
	.string "from ROARK.$"

OreburghCity_Gym_Text_CoalBadgeInfo:
	.string "The COAL BADGE lets your POKéMON\n"
	.string "use ROCK SMASH outside of battle.\p"
	.string "Here, take this too.$"

OreburghCity_Gym_Text_ExplainTM:
	.string "That TM holds ROCK TOMB. It drops\n"
	.string "rocks on the foe and slows it down.\p"
	.string "There are more GYMs across Sinnoh.\n"
	.string "Go see how far you can climb!$"

OreburghCity_Gym_Text_RoarkPostBattle:
	.string "Keep digging and you'll find\n"
	.string "your own strength. Good luck!$"
