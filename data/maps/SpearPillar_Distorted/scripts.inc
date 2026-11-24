SpearPillar_Distorted_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SpearPillar_Distorted_OnTransition
	.byte 0

SpearPillar_Distorted_OnTransition::
	setflag FLAG_ENTERED_DISTORTION_WORLD
	end


SpearPillar_Distorted_EventScript_Npc0::
	msgbox SpearPillar_Distorted_EventScript_Npc0_Text, MSGBOX_NPC
	end

SpearPillar_Distorted_EventScript_Npc0_Text:
	.string "Gravity twists. Paths fold.\n"
	.string "Keep your bearings somehow.$"

SpearPillar_Distorted_EventScript_Npc1::
	msgbox SpearPillar_Distorted_EventScript_Npc1_Text, MSGBOX_NPC
	end

SpearPillar_Distorted_EventScript_Npc1_Text:
	.string "Gravity twists. Paths fold.\n"
	.string "Keep your bearings somehow.$"

SpearPillar_Distorted_EventScript_Npc2::
	msgbox SpearPillar_Distorted_EventScript_Npc2_Text, MSGBOX_NPC
	end

SpearPillar_Distorted_EventScript_Npc2_Text:
	.string "Gravity twists. Paths fold.\n"
	.string "Keep your bearings somehow.$"

SpearPillar_Distorted_EventScript_Npc3::
	msgbox SpearPillar_Distorted_EventScript_Npc3_Text, MSGBOX_NPC
	end

SpearPillar_Distorted_EventScript_Npc3_Text:
	.string "Gravity twists. Paths fold.\n"
	.string "Keep your bearings somehow.$"

SpearPillar_Distorted_EventScript_Npc4::
	msgbox SpearPillar_Distorted_EventScript_Npc4_Text, MSGBOX_NPC
	end

SpearPillar_Distorted_EventScript_Npc4_Text:
	.string "Gravity twists. Paths fold.\n"
	.string "Keep your bearings somehow.$"

SpearPillar_Distorted_EventScript_Npc5::
	msgbox SpearPillar_Distorted_EventScript_Npc5_Text, MSGBOX_NPC
	end

SpearPillar_Distorted_EventScript_Npc5_Text:
	.string "Gravity twists. Paths fold.\n"
	.string "Keep your bearings somehow.$"

SpearPillar_Distorted_EventScript_Cyrus::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_CYRUS_SPEAR_PILLAR, SpearPillar_Distorted_EventScript_CyrusAfterDist
	trainerbattle_single TRAINER_LEADER_CYRUS_DISTORTED, SpearPillar_Distorted_Text_CyrusIntro, SpearPillar_Distorted_Text_CyrusDefeat, SpearPillar_Distorted_EventScript_CyrusDefeated
	release
	end

SpearPillar_Distorted_EventScript_CyrusDefeated::
	setflag FLAG_DEFEATED_CYRUS_SPEAR_PILLAR
	msgbox SpearPillar_Distorted_Text_CyrusAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_SPEAR_PILLAR_DIST_CYRUS, SpearPillar_Distorted_Movement_CyrusLeave
	waitmovement 0
	removeobject LOCALID_SPEAR_PILLAR_DIST_CYRUS
	setflag FLAG_HIDE_SPEAR_PILLAR_DISTORTED_CYRUS
	clearflag FLAG_HIDE_SPEAR_PILLAR_LOOKER
	addobject LOCALID_SPEAR_PILLAR_DIST_LOOKER
	applymovement LOCALID_SPEAR_PILLAR_DIST_LOOKER, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	msgbox SpearPillar_Distorted_Text_Looker, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_SPEAR_PILLAR_DIST_LOOKER, SpearPillar_Distorted_Movement_LookerLeave
	waitmovement 0
	removeobject LOCALID_SPEAR_PILLAR_DIST_LOOKER
	setflag FLAG_HIDE_SPEAR_PILLAR_LOOKER
	release
	end

SpearPillar_Distorted_Movement_LookerLeave:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

SpearPillar_Distorted_EventScript_Looker::
	lock
	faceplayer
	msgbox SpearPillar_Distorted_Text_Looker, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_SPEAR_PILLAR_DIST_LOOKER, SpearPillar_Distorted_Movement_LookerLeave
	waitmovement 0
	removeobject LOCALID_SPEAR_PILLAR_DIST_LOOKER
	setflag FLAG_HIDE_SPEAR_PILLAR_LOOKER
	release
	end

SpearPillar_Distorted_Text_Looker:
	.string "LOOKER: Even here, Cyrus slips away.\n"
	.string "Giratina's world is not finished with us.\p"
	.string "I will file my report. You--keep\n"
	.string "pressing into Distortion.$"

SpearPillar_Distorted_Movement_CyrusLeave:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

SpearPillar_Distorted_EventScript_CyrusAfterDist::
	msgbox SpearPillar_Distorted_Text_CyrusAfter, MSGBOX_DEFAULT
	release
	end

SpearPillar_Distorted_Text_CyrusIntro:
	.string "CYRUS: The pillars cracked open.\n"
	.string "Step through, and witness absence.$"

SpearPillar_Distorted_Text_CyrusDefeat:
	.string "Still... the rift remains.$"

SpearPillar_Distorted_Text_CyrusAfter:
	.string "CYRUS: The Distortion World awaits.\n"
	.string "Giratina stirs in the depths.$"

