VeilstoneCity_GalacticHQ_Cyrus_MapScripts::
	.byte 0

VeilstoneCity_GalacticHQ_Cyrus_EventScript_Cyrus::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_CYRUS_GALACTIC_HQ, VeilstoneCity_GalacticHQ_Cyrus_EventScript_After
	trainerbattle_single TRAINER_LEADER_CYRUS_HQ, VeilstoneCity_GalacticHQ_Cyrus_Text_Intro, VeilstoneCity_GalacticHQ_Cyrus_Text_Defeat, VeilstoneCity_GalacticHQ_Cyrus_EventScript_Defeated
	release
	end

VeilstoneCity_GalacticHQ_Cyrus_EventScript_Defeated::
	setflag FLAG_DEFEATED_CYRUS_GALACTIC_HQ
	msgbox VeilstoneCity_GalacticHQ_Cyrus_Text_After, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_GalacticHQ_Cyrus_EventScript_After::
	msgbox VeilstoneCity_GalacticHQ_Cyrus_Text_After, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_GalacticHQ_Cyrus_Text_Intro:
	.string "CYRUS: Emotion is waste.\n"
	.string "At Spear Pillar I will silence this world.$"

VeilstoneCity_GalacticHQ_Cyrus_Text_Defeat:
	.string "A flawed calculation...$"

VeilstoneCity_GalacticHQ_Cyrus_Text_After:
	.string "CYRUS: Meet me atop Mt. Coronet.\n"
	.string "Spear Pillar will decide everything.$"
