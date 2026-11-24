VeilstoneCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VeilstoneCity_OnTransition
	.byte 0

VeilstoneCity_OnTransition:
	setflag FLAG_VISITED_VEILSTONE_CITY
	call VeilstoneCity_EventScript_SetCounterpartGfx
	end

VeilstoneCity_EventScript_SetCounterpartGfx::
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, VeilstoneCity_EventScript_SetDawnGfx
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL
	return

VeilstoneCity_EventScript_SetDawnGfx::
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_MAY_NORMAL
	return

VeilstoneCity_EventScript_SetCounterpartName::
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, VeilstoneCity_EventScript_NameDawn
	bufferstring STR_VAR_1, VeilstoneCity_Text_NameLucas
	return

VeilstoneCity_EventScript_NameDawn::
	bufferstring STR_VAR_1, VeilstoneCity_Text_NameDawn
	return

VeilstoneCity_Text_NameDawn:
	.string "DAWN$"

VeilstoneCity_Text_NameLucas:
	.string "LUCAS$"

@ Fires when the player steps out of the Gym with the Cobble Badge (state 0).
VeilstoneCity_EventScript_GymExitScene::
	goto_if_unset FLAG_BADGE04_GET, VeilstoneCity_EventScript_NoScene
	goto_if_set FLAG_HIDE_VEILSTONE_COUNTERPART, VeilstoneCity_EventScript_NoScene
	lockall
	call VeilstoneCity_EventScript_SetCounterpartName
	playse SE_PIN
	applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_VEILSTONE_COUNTERPART, VeilstoneCity_Movement_CounterpartToPlayer
	waitmovement 0
	applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_FacePlayer
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceRight
	waitmovement 0
	msgbox VeilstoneCity_Text_CounterpartRush, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_VEILSTONE_COUNTERPART, VeilstoneCity_Movement_CounterpartRunOff
	waitmovement 0
	removeobject LOCALID_VEILSTONE_COUNTERPART
	setobjectxyperm LOCALID_VEILSTONE_COUNTERPART, 28, 18
	setobjectmovementtype LOCALID_VEILSTONE_COUNTERPART, MOVEMENT_TYPE_FACE_RIGHT
	addobject LOCALID_VEILSTONE_COUNTERPART
	setvar VAR_VEILSTONE_CITY_STATE, 1
	releaseall
	end

VeilstoneCity_EventScript_NoScene::
	end

VeilstoneCity_Movement_CounterpartToPlayer:
	walk_fast_left
	step_end

VeilstoneCity_Movement_CounterpartRunOff:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

VeilstoneCity_Text_CounterpartRush:
	.string "{STR_VAR_1}: {PLAYER}! Over here!\p"
	.string "I watched your match through the\n"
	.string "Gym window. Unbelievable!\p"
	.string "But there's no time to celebrate.\n"
	.string "TEAM GALACTIC hauled crates into\l"
	.string "the old warehouse up north.\p"
	.string "One of them holds the prototype\n"
	.string "POKéDEX Prof. Rowan sent here\l"
	.string "for testing!\p"
	.string "If they pry it open, it's gone.\p"
	.string "I'll scout ahead. Meet me at the\n"
	.string "warehouse, and bring your best!$"

@ Counterpart waiting outside the warehouse (state 1) or idling by the Gym.
VeilstoneCity_EventScript_Counterpart::
	lock
	faceplayer
	call VeilstoneCity_EventScript_SetCounterpartName
	goto_if_eq VAR_VEILSTONE_CITY_STATE, 1, VeilstoneCity_EventScript_CounterpartWaiting
	msgbox VeilstoneCity_Text_CounterpartIdle, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_EventScript_CounterpartWaiting::
	msgbox VeilstoneCity_Text_CounterpartWaiting, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_Text_CounterpartIdle:
	.string "{STR_VAR_1}: Congratulations on the\n"
	.string "COBBLE BADGE, {PLAYER}!$"

VeilstoneCity_Text_CounterpartWaiting:
	.string "{STR_VAR_1}: Two grunts, one door.\p"
	.string "Step up to the warehouse and we'll\n"
	.string "take them on together!$"

@ State 0: the warehouse is sealed off.
VeilstoneCity_EventScript_WarehouseBlocked::
	lockall
	applymovement LOCALID_VEILSTONE_GRUNT_1, Common_Movement_FacePlayer
	applymovement LOCALID_VEILSTONE_GRUNT_2, Common_Movement_FacePlayer
	waitmovement 0
	msgbox VeilstoneCity_Text_WarehouseBlocked, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, VeilstoneCity_Movement_PushBack
	waitmovement 0
	releaseall
	end

VeilstoneCity_Movement_PushBack:
	walk_down
	walk_down
	step_end

@ State 1: the counterpart joins the player against both grunts.
VeilstoneCity_EventScript_WarehouseTeamUp::
	lockall
	special HasEnoughMonsForDoubleBattle
	goto_if_ne VAR_RESULT, PLAYER_HAS_TWO_USABLE_MONS, VeilstoneCity_EventScript_NeedTwoMons
	call VeilstoneCity_EventScript_SetCounterpartName
	playse SE_PIN
	applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_FacePlayer
	waitmovement 0
	msgbox VeilstoneCity_Text_TeamUp, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_VEILSTONE_GRUNT_1, Common_Movement_FacePlayer
	applymovement LOCALID_VEILSTONE_GRUNT_2, Common_Movement_FacePlayer
	waitmovement 0
	msgbox VeilstoneCity_Text_GruntsWarn, MSGBOX_DEFAULT
	closemessage
	trainerbattle_two_trainers TRAINER_GALACTIC_GRUNT_VEILSTONE_1, VeilstoneCity_Text_Grunt1Defeat, TRAINER_GALACTIC_GRUNT_VEILSTONE_2, VeilstoneCity_Text_Grunt2Defeat
	setflag FLAG_DEFEATED_VEILSTONE_WAREHOUSE_GRUNTS
	msgbox VeilstoneCity_Text_GruntsRetreat, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_VEILSTONE_GRUNT_1, VeilstoneCity_Movement_GruntFleeWest
	applymovement LOCALID_VEILSTONE_GRUNT_2, VeilstoneCity_Movement_GruntFleeEast
	waitmovement 0
	removeobject LOCALID_VEILSTONE_GRUNT_1
	removeobject LOCALID_VEILSTONE_GRUNT_2
	setflag FLAG_HIDE_VEILSTONE_WAREHOUSE_GRUNTS
	applymovement LOCALID_VEILSTONE_COUNTERPART, Common_Movement_FacePlayer
	waitmovement 0
	msgbox VeilstoneCity_Text_CounterpartThanks, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_VEILSTONE_COUNTERPART, VeilstoneCity_Movement_CounterpartLeave
	waitmovement 0
	removeobject LOCALID_VEILSTONE_COUNTERPART
	setflag FLAG_HIDE_VEILSTONE_COUNTERPART
	setvar VAR_VEILSTONE_CITY_STATE, 2
	releaseall
	end

VeilstoneCity_EventScript_NeedTwoMons::
	msgbox VeilstoneCity_Text_NeedTwoMons, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, VeilstoneCity_Movement_PushBack
	waitmovement 0
	releaseall
	end

VeilstoneCity_Movement_GruntFleeWest:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

VeilstoneCity_Movement_GruntFleeEast:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

VeilstoneCity_Movement_CounterpartLeave:
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	step_end

VeilstoneCity_EventScript_WarehouseGrunt::
	lock
	faceplayer
	msgbox VeilstoneCity_Text_WarehouseGrunt, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_Text_WarehouseBlocked:
	.string "GRUNT: Hold it, kid!\p"
	.string "This depot belongs to TEAM GALACTIC\n"
	.string "now. Nobody gets through.\p"
	.string "Go play somewhere else!$"

VeilstoneCity_Text_TeamUp:
	.string "{STR_VAR_1}: There you are, {PLAYER}!\p"
	.string "Two grunts on the door, and they\n"
	.string "won't listen to reason.\p"
	.string "So let's not ask nicely. We take\n"
	.string "them together, side by side!$"

VeilstoneCity_Text_GruntsWarn:
	.string "GRUNT: Two brats for the price of\n"
	.string "one? Fine by us!\p"
	.string "TEAM GALACTIC doesn't lose to\n"
	.string "kids. Get ready!$"

VeilstoneCity_Text_Grunt1Defeat:
	.string "Tch... The Commander will have my\n"
	.string "head for this!$"

VeilstoneCity_Text_Grunt2Defeat:
	.string "We were supposed to be the muscle...$"

VeilstoneCity_Text_GruntsRetreat:
	.string "GRUNT: This depot isn't worth the\n"
	.string "trouble! Fall back!$"

VeilstoneCity_Text_CounterpartThanks:
	.string "{STR_VAR_1}: That's how it's done,\n"
	.string "{PLAYER}! The door's clear.\p"
	.string "The crate with the POKéDEX was\n"
	.string "already carried out the back way.\p"
	.string "There's a sealed door deeper inside\n"
	.string "that needs a STORAGE KEY. I'll\l"
	.string "track down where they went.\p"
	.string "Have a look around in there--they\n"
	.string "left a lot behind in a hurry!$"

VeilstoneCity_Text_NeedTwoMons:
	.string "You need at least two POKéMON able\n"
	.string "to battle to take on both grunts.$"

VeilstoneCity_Text_WarehouseGrunt:
	.string "Move along. This warehouse is off\n"
	.string "limits to civilians.$"

VeilstoneCity_EventScript_MayleneCameo::
	lock
	faceplayer
	goto_if_eq VAR_VEILSTONE_CITY_STATE, 2, VeilstoneCity_EventScript_MayleneAfter
	msgbox VeilstoneCity_Text_MayleneCameo, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_EventScript_MayleneAfter::
	msgbox VeilstoneCity_Text_MayleneAfter, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_Text_MayleneCameo:
	.string "MAYLENE: You fought with heart in\n"
	.string "there. I like that!\p"
	.string "I heard shouting up near the old\n"
	.string "warehouse. Be careful, okay?$"

VeilstoneCity_Text_MayleneAfter:
	.string "MAYLENE: You and your friend cleared\n"
	.string "the warehouse? Nicely done!\p"
	.string "With the COBBLE BADGE, POKéMON that\n"
	.string "know FLY will carry you to any\l"
	.string "town you've already visited.$"

VeilstoneCity_EventScript_HQGuard::
	msgbox VeilstoneCity_Text_HQGuard, MSGBOX_NPC
	end

VeilstoneCity_Text_HQGuard:
	.string "Move along.\n"
	.string "TEAM GALACTIC's headquarters is\l"
	.string "closed to the public.$"

VeilstoneCity_EventScript_Woman::
	msgbox VeilstoneCity_Text_Woman, MSGBOX_NPC
	end

VeilstoneCity_Text_Woman:
	.string "Veilstone is the city of stone.\n"
	.string "Even the streets feel sturdy!\p"
	.string "The quarry winds down to the sea\n"
	.string "from here.$"

VeilstoneCity_EventScript_Man::
	msgbox VeilstoneCity_Text_Man, MSGBOX_NPC
	end

VeilstoneCity_Text_Man:
	.string "That crater to the east? A giant\n"
	.string "meteorite crashed there long ago.\p"
	.string "People say it's why the stone in\n"
	.string "this city is so tough.$"

VeilstoneCity_EventScript_Boy::
	msgbox VeilstoneCity_Text_Boy, MSGBOX_NPC
	end

VeilstoneCity_Text_Boy:
	.string "The Department Store has five\n"
	.string "floors and an elevator!\p"
	.string "I ride it up and down all day.$"

VeilstoneCity_EventScript_OldMan::
	msgbox VeilstoneCity_Text_OldMan, MSGBOX_NPC
	end

VeilstoneCity_Text_OldMan:
	.string "That big building to the north is\n"
	.string "TEAM GALACTIC's. I never see who\l"
	.string "goes in or out.\p"
	.string "Something is off about those folks.$"

VeilstoneCity_EventScript_Researcher::
	msgbox VeilstoneCity_Text_Researcher, MSGBOX_NPC
	end

VeilstoneCity_Text_Researcher:
	.string "I'm measuring the crater's depth.\p"
	.string "Space rock or not, it's a fine\n"
	.string "spot to study erosion.$"

VeilstoneCity_EventScript_LittleGirl::
	msgbox VeilstoneCity_Text_LittleGirl, MSGBOX_NPC
	end

VeilstoneCity_Text_LittleGirl:
	.string "The Game Corner is for grown-ups.\n"
	.string "I just like the music from outside!$"

VeilstoneCity_EventScript_GymSign::
	msgbox VeilstoneCity_Text_GymSign, MSGBOX_SIGN
	end

VeilstoneCity_Text_GymSign:
	.string "VEILSTONE CITY POKéMON GYM\n"
	.string "LEADER: MAYLENE\l"
	.string "The Iron-Willed Bruiser!$"

VeilstoneCity_EventScript_CitySign::
	msgbox VeilstoneCity_Text_CitySign, MSGBOX_SIGN
	end

VeilstoneCity_Text_CitySign:
	.string "VEILSTONE CITY\n"
	.string "A city carved from stone$"

VeilstoneCity_EventScript_DeptStoreSign::
	msgbox VeilstoneCity_Text_DeptStoreSign, MSGBOX_SIGN
	end

VeilstoneCity_Text_DeptStoreSign:
	.string "VEILSTONE DEPARTMENT STORE\n"
	.string "Five floors of everything a\l"
	.string "Trainer needs!$"

VeilstoneCity_EventScript_WarehouseSign::
	msgbox VeilstoneCity_Text_WarehouseSign, MSGBOX_SIGN
	end

VeilstoneCity_Text_WarehouseSign:
	.string "NO ENTRY\n"
	.string "Property of TEAM GALACTIC$"

VeilstoneCity_EventScript_GameCornerSign::
	msgbox VeilstoneCity_Text_GameCornerSign, MSGBOX_SIGN
	end

VeilstoneCity_Text_GameCornerSign:
	.string "VEILSTONE GAME CORNER\n"
	.string "Fun and prizes for everyone!$"

VeilstoneCity_EventScript_HQSign::
	msgbox VeilstoneCity_Text_HQSign, MSGBOX_SIGN
	end

VeilstoneCity_Text_HQSign:
	.string "TEAM GALACTIC VEILSTONE HQ\n"
	.string "Visitors are not welcome.$"

VeilstoneCity_EventScript_CraterSign::
	msgbox VeilstoneCity_Text_CraterSign, MSGBOX_SIGN
	end

VeilstoneCity_Text_CraterSign:
	.string "VEILSTONE METEORITE CRATER\n"
	.string "A hollow left by a fallen star.\p"
	.string "Please stay off the rim.$"
