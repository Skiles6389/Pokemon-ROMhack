CanalaveCity_Gym_MapScripts::
	.byte 0

CanalaveCity_Gym_EventScript_Byron::
	lock
	faceplayer
	trainerbattle_single TRAINER_LEADER_BYRON, CanalaveCity_Gym_Text_ByronIntro, CanalaveCity_Gym_Text_ByronDefeat, CanalaveCity_Gym_EventScript_ByronDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_CANALAVE_GYM_TM, CanalaveCity_Gym_EventScript_GiveTM
	msgbox CanalaveCity_Gym_Text_ByronAfter, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Gym_EventScript_ByronDefeated::
	message CanalaveCity_Gym_Text_ReceivedMineBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox CanalaveCity_Gym_Text_MineBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE06_GET
	goto CanalaveCity_Gym_EventScript_GiveTM
	end

CanalaveCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_FLASH_CANNON
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_CANALAVE_GYM_TM
	msgbox CanalaveCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE06_GET, CanalaveCity_Gym_EventScript_GuideVictory
	msgbox CanalaveCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Gym_EventScript_GuideVictory::
	msgbox CanalaveCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE06_GET, CanalaveCity_Gym_EventScript_StatueWon
	msgbox CanalaveCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

CanalaveCity_Gym_EventScript_StatueWon::
	msgbox CanalaveCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

CanalaveCity_Gym_EventScript_WorkerAlan::
	trainerbattle_single TRAINER_WORKER_ALAN_CANALAVE, CanalaveCity_Gym_Text_AlanIntro, CanalaveCity_Gym_Text_AlanDefeat
	msgbox CanalaveCity_Gym_Text_AlanAfter, MSGBOX_AUTOCLOSE
	end

CanalaveCity_Gym_EventScript_SailorJonah::
	trainerbattle_single TRAINER_SAILOR_JONAH_CANALAVE, CanalaveCity_Gym_Text_JonahIntro, CanalaveCity_Gym_Text_JonahDefeat
	msgbox CanalaveCity_Gym_Text_JonahAfter, MSGBOX_AUTOCLOSE
	end

CanalaveCity_Gym_Text_ByronIntro:
	.string "I'm BYRON, Canalave's Gym Leader!\n"
	.string "Steel types don't bend for soft hits.\p"
	.string "Show me a will that can reshape ore!$"

CanalaveCity_Gym_Text_ByronDefeat:
	.string "You hammered through my armor...$"

CanalaveCity_Gym_Text_ByronAfter:
	.string "Keep tempering that team.\n"
	.string "The next stretch of Sinnoh gets hotter.$"

CanalaveCity_Gym_Text_ReceivedMineBadge:
	.string "{PLAYER} received the MINE BADGE\n"
	.string "from BYRON.$"

CanalaveCity_Gym_Text_MineBadgeInfo:
	.string "With the MINE BADGE, more machines\n"
	.string "will answer your POK-MON's strength.$"

CanalaveCity_Gym_Text_ExplainTM:
	.string "That TM is FLASH CANNON.\n"
	.string "A steel beam that can lower Sp. Def.$"

CanalaveCity_Gym_Text_GuideAdvice:
	.string "BYRON favors Steel types.\n"
	.string "Fire and Ground crack that shell.$"

CanalaveCity_Gym_Text_GuideVictory:
	.string "You forged a win against BYRON!\n"
	.string "The Mine Badge looks good on you.$"

CanalaveCity_Gym_Text_Statue:
	.string "CANALAVE CITY POK-MON GYM$"

CanalaveCity_Gym_Text_StatueWon:
	.string "CANALAVE CITY POK-MON GYM\p"
	.string "BYRON'S CERTIFIED TRAINERS:\n"
	.string "{PLAYER}$"

CanalaveCity_Gym_Text_AlanIntro:
	.string "Steel beams don't flinch!$"

CanalaveCity_Gym_Text_AlanDefeat:
	.string "Bent out of shape...$"

CanalaveCity_Gym_Text_AlanAfter:
	.string "BYRON taught us to stand firm.$"

CanalaveCity_Gym_Text_JonahIntro:
	.string "Harbor grit meets gym steel!$"

CanalaveCity_Gym_Text_JonahDefeat:
	.string "Washed out.$"

CanalaveCity_Gym_Text_JonahAfter:
	.string "Take the ferry to Iron Island\n"
	.string "if you want raw ore practice.$"
