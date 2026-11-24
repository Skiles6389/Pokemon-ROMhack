SpearPillar_MapScripts::
	.byte 0

SpearPillar_EventScript_Cyrus::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_CYRUS_SPEAR_PILLAR, SpearPillar_EventScript_CyrusAfter
	trainerbattle_single TRAINER_LEADER_CYRUS_SPEAR, SpearPillar_Text_CyrusIntro, SpearPillar_Text_CyrusDefeat, SpearPillar_EventScript_CyrusDefeated
	release
	end

SpearPillar_EventScript_CyrusDefeated::
	setflag FLAG_DEFEATED_CYRUS_SPEAR_PILLAR
	msgbox SpearPillar_Text_CyrusAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_SPEAR_PILLAR_CYRUS, SpearPillar_Movement_CyrusLeave
	waitmovement 0
	removeobject LOCALID_SPEAR_PILLAR_CYRUS
	setflag FLAG_HIDE_SPEAR_PILLAR_CYRUS
	release
	end

SpearPillar_Movement_CyrusLeave:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

SpearPillar_EventScript_CyrusAfter::
	msgbox SpearPillar_Text_CyrusAfter, MSGBOX_DEFAULT
	release
	end

SpearPillar_EventScript_DistortionClosed::
	msgbox SpearPillar_Text_DistortionClosed, MSGBOX_NPC
	end

SpearPillar_Text_CyrusIntro:
	.string "CYRUS: Here the pillars pierce sky.\n"
	.string "Witness a world without spirit clutter.$"

SpearPillar_Text_CyrusDefeat:
	.string "Even here... resistance$"

SpearPillar_Text_CyrusAfter:
	.string "CYRUS: The Distortion World stirs.\n"
	.string "Its gate stays sealed until the next chapter.$"

SpearPillar_Text_DistortionClosed:
	.string "A rift shimmers, then freezes shut.\n"
	.string "Return when the Distortion World opens.$"

SpearPillar_EventScript_PlatNpc0::
	msgbox SpearPillar_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

SpearPillar_EventScript_PlatNpc0_Text:
	.string "The pillars hum with wrong silence.\n"
	.string "Cyrus stands at the center.$"

SpearPillar_EventScript_PlatNpc1::
	msgbox SpearPillar_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

SpearPillar_EventScript_PlatNpc1_Text:
	.string "The pillars hum with wrong silence.\n"
	.string "Cyrus stands at the center.$"

SpearPillar_EventScript_PlatNpc2::
	msgbox SpearPillar_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

SpearPillar_EventScript_PlatNpc2_Text:
	.string "The pillars hum with wrong silence.\n"
	.string "Cyrus stands at the center.$"

SpearPillar_EventScript_PlatNpc3::
	msgbox SpearPillar_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

SpearPillar_EventScript_PlatNpc3_Text:
	.string "The pillars hum with wrong silence.\n"
	.string "Cyrus stands at the center.$"

SpearPillar_EventScript_PlatNpc4::
	msgbox SpearPillar_EventScript_PlatNpc4_Text, MSGBOX_NPC
	end

SpearPillar_EventScript_PlatNpc4_Text:
	.string "The pillars hum with wrong silence.\n"
	.string "Cyrus stands at the center.$"

SpearPillar_EventScript_PlatNpc5::
	msgbox SpearPillar_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

SpearPillar_EventScript_PlatNpc5_Text:
	.string "The pillars hum with wrong silence.\n"
	.string "Cyrus stands at the center.$"

SpearPillar_EventScript_DistortionOpen::
	msgbox SpearPillar_Text_DistortionOpen, MSGBOX_NPC
	end

SpearPillar_Text_DistortionOpen:
	.string "The rift yawns open.\n"
	.string "Beyond it lies the Distortion World.$"
