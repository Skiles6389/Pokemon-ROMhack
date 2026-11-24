MtCoronet_1F_South_MapScripts::
	.byte 0

MtCoronet_1F_South_EventScript_CyrusIdle::
	msgbox MtCoronet_1F_South_Text_Cyrus1, MSGBOX_NPC
	end

MtCoronet_1F_South_EventScript_CyrusScene::
	lockall
	goto_if_set FLAG_MT_CORONET_CYRUS_DONE, MtCoronet_1F_South_EventScript_CyrusDone
	playbgm MUS_PL_ENCOUNTER_GALACTIC, FALSE
	setobjectxyperm LOCALID_MT_CORONET_CYRUS, 15, 17
	setobjectmovementtype LOCALID_MT_CORONET_CYRUS, MOVEMENT_TYPE_FACE_DOWN
	clearflag FLAG_HIDE_MT_CORONET_CYRUS
	addobject LOCALID_MT_CORONET_CYRUS
	applymovement LOCALID_MT_CORONET_CYRUS, MtCoronet_1F_South_Movement_CyrusWalkIn
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceUp
	waitmovement 0
	msgbox MtCoronet_1F_South_Text_Cyrus1, MSGBOX_DEFAULT
	msgbox MtCoronet_1F_South_Text_Cyrus2, MSGBOX_DEFAULT
	msgbox MtCoronet_1F_South_Text_Cyrus3, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_MT_CORONET_CYRUS, MtCoronet_1F_South_Movement_CyrusWalkOut
	waitmovement 0
	removeobject LOCALID_MT_CORONET_CYRUS
	setflag FLAG_HIDE_MT_CORONET_CYRUS
	setflag FLAG_MT_CORONET_CYRUS_DONE
	setvar VAR_MT_CORONET_SOUTH_STATE, 1
	fadedefaultbgm
	releaseall
	end

MtCoronet_1F_South_EventScript_CyrusDone::
	releaseall
	end

MtCoronet_1F_South_EventScript_BlockedNorth::
	lockall
	msgbox MtCoronet_1F_South_Text_Blocked, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkDown
	waitmovement 0
	releaseall
	end

MtCoronet_1F_South_EventScript_Protein::
	finditem ITEM_PROTEIN
	end

MtCoronet_1F_South_Movement_CyrusWalkIn:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

MtCoronet_1F_South_Movement_CyrusWalkOut:
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	step_end

MtCoronet_1F_South_Text_Cyrus1:
	.string "According to one theory, Mt. Coronet\n"
	.string "is where the Sinnoh region began.$"
MtCoronet_1F_South_Text_Cyrus2:
	.string "...In a newly created world...\pA world where only time flowed and\n"
	.string "space expanded...\pThere should have been no strife.$"
MtCoronet_1F_South_Text_Cyrus3:
	.string "But what became of that world?\pBecause the human spirit is weak and\n"
	.string "incomplete, strife has spread...\pThis world is being ruined by it...\p"
	.string "I find this state of affairs to be\ldeplorable...$"
MtCoronet_1F_South_Text_Blocked:
	.string "Boulders block the northern passage.\n"
	.string "You'll need more badges later!$"
