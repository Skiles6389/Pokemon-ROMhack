EternaCity_Gym_MapScripts::
	.byte 0

EternaCity_Gym_EventScript_Gardenia::
	trainerbattle_single TRAINER_LEADER_GARDENIA, EternaCity_Gym_Text_GardeniaIntro, EternaCity_Gym_Text_GardeniaDefeat, EternaCity_Gym_EventScript_GardeniaDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_ETERNA_GYM_TM, EternaCity_Gym_EventScript_GiveTM
	msgbox EternaCity_Gym_Text_GardeniaPost, MSGBOX_DEFAULT
	release
	end

EternaCity_Gym_EventScript_GardeniaDefeated::
	message EternaCity_Gym_Text_ReceivedForestBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox EternaCity_Gym_Text_ForestBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE02_GET
	setvar VAR_ETERNA_CITY_STATE, 3
	clearflag FLAG_HIDE_ETERNA_CITY_GARDENIA
	goto EternaCity_Gym_EventScript_GiveTM
	end

EternaCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_GIGA_DRAIN
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_ETERNA_GYM_TM
	msgbox EternaCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

EternaCity_Gym_EventScript_Caroline::
	trainerbattle_single TRAINER_LASS_CAROLINE, EternaCity_Gym_Text_CarolineIntro, EternaCity_Gym_Text_CarolineDefeat
	msgbox EternaCity_Gym_Text_CarolineAfter, MSGBOX_AUTOCLOSE
	end

EternaCity_Gym_EventScript_Jenna::
	trainerbattle_single TRAINER_AROMA_LADY_JENNA, EternaCity_Gym_Text_JennaIntro, EternaCity_Gym_Text_JennaDefeat
	msgbox EternaCity_Gym_Text_JennaAfter, MSGBOX_AUTOCLOSE
	end

EternaCity_Gym_EventScript_Angela::
	trainerbattle_single TRAINER_AROMA_LADY_ANGELA, EternaCity_Gym_Text_AngelaIntro, EternaCity_Gym_Text_AngelaDefeat
	msgbox EternaCity_Gym_Text_AngelaAfter, MSGBOX_AUTOCLOSE
	end

EternaCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE02_GET, EternaCity_Gym_EventScript_GuideVictory
	msgbox EternaCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

EternaCity_Gym_EventScript_GuideVictory::
	msgbox EternaCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

EternaCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE02_GET, EternaCity_Gym_EventScript_StatueWon
	msgbox EternaCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

EternaCity_Gym_EventScript_StatueWon::
	msgbox EternaCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

EternaCity_Gym_Text_GuideAdvice:
	.string "Hey, there!\n"
	.string "How's it going, Champ-to-be?\p"
	.string "The GYM LEADER, GARDENIA, is a user\n"
	.string "of Grass-type POKéMON.\p"
	.string "It should be obvious, but Grass-type\n"
	.string "POKéMON really hate fire.\p"
	.string "They're also at a huge disadvantage\n"
	.string "against the Flying type, too.\p"
	.string "You can't challenge the GYM LEADER\n"
	.string "until you beat all the GYM's Trainers.$"

EternaCity_Gym_Text_GuideVictory:
	.string "Oh! {PLAYER}!\n"
	.string "You've beaten the GYM LEADER!\p"
	.string "Your POKéMON look much tougher than\n"
	.string "when they went in, too!$"

EternaCity_Gym_Text_Statue:
	.string "ETERNA CITY POKéMON GYM\p"
	.string "LEADER: GARDENIA$"

EternaCity_Gym_Text_StatueWon:
	.string "ETERNA CITY POKéMON GYM\p"
	.string "LEADER: GARDENIA\p"
	.string "Certified Trainers:\n"
	.string "{PLAYER}$"

EternaCity_Gym_Text_CarolineIntro:
	.string "Aromatherapy keeps my team calm!\n"
	.string "Can you?$"

EternaCity_Gym_Text_CarolineDefeat:
	.string "Wilting...$"

EternaCity_Gym_Text_CarolineAfter:
	.string "GARDENIA's tougher than sweet scents.$"

EternaCity_Gym_Text_JennaIntro:
	.string "Feel this floral power!$"

EternaCity_Gym_Text_JennaDefeat:
	.string "Petals scattered...$"

EternaCity_Gym_Text_JennaAfter:
	.string "Use status moves wisely in here.$"

EternaCity_Gym_Text_AngelaIntro:
	.string "Grass types rule Eterna!$"

EternaCity_Gym_Text_AngelaDefeat:
	.string "Trimmed down...$"

EternaCity_Gym_Text_AngelaAfter:
	.string "The leader's waiting above.$"

EternaCity_Gym_Text_GardeniaIntro:
	.string "You kept me waiting!\p"
	.string "I'm Eterna's GYM LEADER, GARDENIA,\n"
	.string "the Grass-type master!\p"
	.string "When I first saw you, I was convinced\n"
	.string "you'd find your way to me.\p"
	.string "My hunch was right on the money.\n"
	.string "You have a winning aura about you.\p"
	.string "So, anyway, this will be fun.\n"
	.string "Let's have our battle!$"

EternaCity_Gym_Text_GardeniaDefeat:
	.string "Amazing!\n"
	.string "You're very good, aren't you?$"

EternaCity_Gym_Text_ReceivedForestBadge:
	.string "{PLAYER} received the FOREST BADGE\n"
	.string "from GARDENIA!$"

EternaCity_Gym_Text_ForestBadgeInfo:
	.string "With the FOREST BADGE, your POKéMON\n"
	.string "can use the hidden move Cut outside\l"
	.string "of battle.\p"
	.string "I've also got something else.\n"
	.string "It's a gift from me!$"

EternaCity_Gym_Text_ExplainTM:
	.string "That TM contains GIGA DRAIN.\p"
	.string "It's one of my favorite moves.\n"
	.string "Steal HP while you deal damage!$"

EternaCity_Gym_Text_GardeniaPost:
	.string "Yup! If there's one thing I can tell\n"
	.string "you, it's this…\p"
	.string "Being a Gym Leader is tough, but it's\n"
	.string "also a lot of fun!\p"
	.string "Come back anytime you want tips\n"
	.string "about Grass-type Pokémon!$"
