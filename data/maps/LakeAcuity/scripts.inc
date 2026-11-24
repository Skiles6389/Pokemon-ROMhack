LakeAcuity_MapScripts::
	.byte 0

LakeAcuity_EventScript_Npc0::
	msgbox LakeAcuity_EventScript_Npc0_Text, MSGBOX_NPC
	end

LakeAcuity_EventScript_Npc0_Text:
	.string "Galactic camps still scar the shore.\n"
	.string "Their Commander was spotted inland.$"

LakeAcuity_EventScript_Npc1::
	msgbox LakeAcuity_EventScript_Npc1_Text, MSGBOX_NPC
	end

LakeAcuity_EventScript_Npc1_Text:
	.string "Galactic camps still scar the shore.\n"
	.string "Their Commander was spotted inland.$"

LakeAcuity_EventScript_Npc2::
	msgbox LakeAcuity_EventScript_Npc2_Text, MSGBOX_NPC
	end

LakeAcuity_EventScript_Npc2_Text:
	.string "Galactic camps still scar the shore.\n"
	.string "Their Commander was spotted inland.$"

LakeAcuity_EventScript_Jupiter::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_JUPITER_LAKE_ACUITY, LakeAcuity_EventScript_JupiterAfter
	trainerbattle_single TRAINER_COMMANDER_JUPITER_ACUITY, LakeAcuity_Text_JupiterIntro, LakeAcuity_Text_JupiterDefeat, LakeAcuity_EventScript_JupiterDefeated
	release
	end

LakeAcuity_EventScript_JupiterDefeated::
	setflag FLAG_DEFEATED_JUPITER_LAKE_ACUITY
	msgbox LakeAcuity_Text_JupiterAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_LAKE_ACUITY_JUPITER, LakeAcuity_Movement_JupiterLeave
	waitmovement 0
	removeobject LOCALID_LAKE_ACUITY_JUPITER
	setflag FLAG_HIDE_LAKE_ACUITY_JUPITER
	release
	end

LakeAcuity_Movement_JupiterLeave:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

LakeAcuity_EventScript_JupiterAfter::
	msgbox LakeAcuity_Text_JupiterAfter, MSGBOX_DEFAULT
	release
	end

LakeAcuity_Text_JupiterIntro:
	.string "JUPITER: Three lakes, three keys.\n"
	.string "You will not halt the next phase.$"

LakeAcuity_Text_JupiterDefeat:
	.string "Impossible...$"

LakeAcuity_Text_JupiterAfter:
	.string "JUPITER: Headquarters will settle this.\n"
	.string "Veilstone still answers to Galactic.$"

