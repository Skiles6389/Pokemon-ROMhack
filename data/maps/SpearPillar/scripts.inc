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
	applymovement LOCALID_SPEAR_PILLAR_MARS, SpearPillar_Movement_SupportLeave
	applymovement LOCALID_SPEAR_PILLAR_JUPITER, SpearPillar_Movement_SupportLeave
	applymovement LOCALID_SPEAR_PILLAR_GRUNT_M, SpearPillar_Movement_SupportLeave
	applymovement LOCALID_SPEAR_PILLAR_GRUNT_F, SpearPillar_Movement_SupportLeave
	applymovement LOCALID_SPEAR_PILLAR_BARRY, SpearPillar_Movement_SupportLeave
	waitmovement 0
	removeobject LOCALID_SPEAR_PILLAR_CYRUS
	removeobject LOCALID_SPEAR_PILLAR_MARS
	removeobject LOCALID_SPEAR_PILLAR_JUPITER
	removeobject LOCALID_SPEAR_PILLAR_GRUNT_M
	removeobject LOCALID_SPEAR_PILLAR_GRUNT_F
	removeobject LOCALID_SPEAR_PILLAR_BARRY
	setflag FLAG_HIDE_SPEAR_PILLAR_CYRUS
	setflag FLAG_HIDE_SPEAR_PILLAR_SUPPORT
	clearflag FLAG_HIDE_SPEAR_PILLAR_LOOKER
	addobject LOCALID_SPEAR_PILLAR_LOOKER
	applymovement LOCALID_SPEAR_PILLAR_LOOKER, SpearPillar_Movement_LookerEnter
	waitmovement 0
	msgbox SpearPillar_Text_LookerArrive, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_SPEAR_PILLAR_LOOKER, SpearPillar_Movement_LookerLeave
	waitmovement 0
	removeobject LOCALID_SPEAR_PILLAR_LOOKER
	setflag FLAG_HIDE_SPEAR_PILLAR_LOOKER
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

SpearPillar_Movement_SupportLeave:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

SpearPillar_Movement_LookerEnter:
	walk_up
	walk_up
	walk_up
	walk_up
	step_end

SpearPillar_Movement_LookerLeave:
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

SpearPillar_EventScript_GruntM::
	msgbox SpearPillar_Text_GruntIdle, MSGBOX_NPC
	end

SpearPillar_EventScript_GruntF::
	msgbox SpearPillar_Text_GruntIdle, MSGBOX_NPC
	end

SpearPillar_EventScript_Mars::
	msgbox SpearPillar_Text_MarsIdle, MSGBOX_NPC
	end

SpearPillar_EventScript_Jupiter::
	msgbox SpearPillar_Text_JupiterIdle, MSGBOX_NPC
	end

SpearPillar_EventScript_Barry::
	msgbox SpearPillar_Text_BarryIdle, MSGBOX_NPC
	end

SpearPillar_EventScript_LookerIdle::
	msgbox SpearPillar_Text_LookerArrive, MSGBOX_NPC
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
	.string "Its gate yawns--pursue if you dare.$"

SpearPillar_Text_GruntIdle:
	.string "Boss Cyrus will remake everything.\n"
	.string "Stay out of the way!$"

SpearPillar_Text_MarsIdle:
	.string "MARS: The boss's vision is absolute.\n"
	.string "Dialga and Palkia will obey.$"

SpearPillar_Text_JupiterIdle:
	.string "JUPITER: Space and time bend here.\n"
	.string "Your struggle is already late.$"

SpearPillar_Text_BarryIdle:
	.string "BARRY: {PLAYER}! We stop Cyrus now!\n"
	.string "I've got your back--somehow!$"

SpearPillar_Text_LookerArrive:
	.string "LOOKER: International Police.\n"
	.string "Cyrus fled into Distortion?\p"
	.string "I will pursue the trail. You--\n"
	.string "follow when the rift is stable.$"

SpearPillar_Text_DistortionClosed:
	.string "A rift shimmers, then freezes shut.\n"
	.string "Return when the Distortion World opens.$"

SpearPillar_EventScript_DistortionOpen::
	msgbox SpearPillar_Text_DistortionOpen, MSGBOX_SIGN
	end

SpearPillar_Text_DistortionOpen:
	.string "The rift to Distortion World flickers.\n"
	.string "Step through when you are ready.$"
