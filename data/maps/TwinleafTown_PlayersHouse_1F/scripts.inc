TwinleafTown_PlayersHouse_1F_MapScripts::
	.byte 0

TwinleafTown_PlayersHouse_1F_EventScript_Mom::
	lock
	faceplayer
	goto_if_eq VAR_TWINLEAF_STATE, 0, TwinleafTown_PlayersHouse_1F_EventScript_MomMorning
	goto_if_eq VAR_TWINLEAF_STATE, 1, TwinleafTown_PlayersHouse_1F_EventScript_MomBeforeShoes
	@ After the opening, Mom heals the party whenever you talk to her.
	goto_if_set FLAG_SYS_POKEMON_GET, TwinleafTown_PlayersHouse_1F_EventScript_MomHeal
	msgbox TwinleafTown_PlayersHouse_1F_Text_MomAfterShoes, MSGBOX_DEFAULT
	release
	end

TwinleafTown_PlayersHouse_1F_EventScript_MomMorning::
	msgbox TwinleafTown_PlayersHouse_1F_Text_MomMorning, MSGBOX_DEFAULT
	release
	end

TwinleafTown_PlayersHouse_1F_EventScript_MomBeforeShoes::
	msgbox TwinleafTown_PlayersHouse_1F_Text_MomBeforeShoes, MSGBOX_DEFAULT
	release
	end

TwinleafTown_PlayersHouse_1F_EventScript_MomHeal::
	msgbox TwinleafTown_PlayersHouse_1F_Text_MomHealOffer, MSGBOX_DEFAULT
	closemessage
	call Common_EventScript_OutOfCenterPartyHeal
	incrementgamestat GAME_STAT_RESTED_AT_HOME
	msgbox TwinleafTown_PlayersHouse_1F_Text_MomHealDone, MSGBOX_DEFAULT
	release
	end

TwinleafTown_PlayersHouse_1F_EventScript_BarryArrives::
	lockall
	playse SE_DOOR
	waitse
	clearflag FLAG_HIDE_TWINLEAF_BARRY
	addobject LOCALID_TWINLEAF_BARRY
	applymovement LOCALID_TWINLEAF_BARRY, TwinleafTown_PlayersHouse_1F_Movement_BarryRushIn
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox TwinleafTown_PlayersHouse_1F_Text_BarryLate, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_TWINLEAF_BARRY, TwinleafTown_PlayersHouse_1F_Movement_BarryRushOut
	waitmovement 0
	removeobject LOCALID_TWINLEAF_BARRY
	setflag FLAG_HIDE_TWINLEAF_BARRY
	setvar VAR_TWINLEAF_STATE, 1
	releaseall
	end

TwinleafTown_PlayersHouse_1F_EventScript_MomGivesShoes::
	lockall
	goto_if_set FLAG_RECEIVED_RUNNING_SHOES, TwinleafTown_PlayersHouse_1F_EventScript_MomShoesAlready
	applymovement LOCALID_TWINLEAF_MOM, TwinleafTown_PlayersHouse_1F_Movement_MomToPlayer
	waitmovement 0
	msgbox TwinleafTown_PlayersHouse_1F_Text_MomShoes, MSGBOX_DEFAULT
	playfanfare MUS_OBTAIN_ITEM
	message TwinleafTown_PlayersHouse_1F_Text_ReceivedRunningShoes
	waitfanfare
	setflag FLAG_RECEIVED_RUNNING_SHOES
	setflag FLAG_SYS_B_DASH
	msgbox TwinleafTown_PlayersHouse_1F_Text_MomHoldB, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_TWINLEAF_MOM, TwinleafTown_PlayersHouse_1F_Movement_MomReturn
	waitmovement 0
	setvar VAR_TWINLEAF_STATE, 2
	releaseall
	end

TwinleafTown_PlayersHouse_1F_EventScript_MomShoesAlready::
	msgbox TwinleafTown_PlayersHouse_1F_Text_MomAfterShoes, MSGBOX_DEFAULT
	setvar VAR_TWINLEAF_STATE, 2
	releaseall
	end

TwinleafTown_PlayersHouse_1F_Movement_BarryRushIn:
	walk_fast_up
	walk_fast_left
	face_up
	step_end

TwinleafTown_PlayersHouse_1F_Movement_BarryRushOut:
	walk_fast_right
	walk_fast_down
	step_end

TwinleafTown_PlayersHouse_1F_Movement_MomToPlayer:
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_up
	face_right
	step_end

TwinleafTown_PlayersHouse_1F_Movement_MomReturn:
	walk_down
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_up
	walk_up
	face_up
	step_end

TwinleafTown_PlayersHouse_1F_Text_MomMorning:
	.string "MOM: Morning, {PLAYER}.\p"
	.string "Your friend was here earlier.\n"
	.string "He couldn't stand still for a second.$"

TwinleafTown_PlayersHouse_1F_Text_MomBeforeShoes:
	.string "MOM: If you're heading out, don't\n"
	.string "leave without saying so.$"

TwinleafTown_PlayersHouse_1F_Text_BarryLate:
	.string "BARRY: {PLAYER}! You're late!\p"
	.string "I've been pacing outside forever.\n"
	.string "The Professor is already at the lake.\p"
	.string "Meet me there. Don't wander off!$"

TwinleafTown_PlayersHouse_1F_Text_MomShoes:
	.string "MOM: That boy never slows down.\p"
	.string "{PLAYER}, if you're going after him,\n"
	.string "wear these RUNNING SHOES.$"

TwinleafTown_PlayersHouse_1F_Text_ReceivedRunningShoes:
	.string "{PLAYER} switched to the\n"
	.string "RUNNING SHOES.$"

TwinleafTown_PlayersHouse_1F_Text_MomHoldB:
	.string "MOM: Hold the B Button to run.\p"
	.string "The lake is north of town, along\n"
	.string "the route. Come home if you need me.$"

TwinleafTown_PlayersHouse_1F_Text_MomAfterShoes:
	.string "MOM: I'll be here. The lake road\n"
	.string "is the one that leaves town north.$"

TwinleafTown_PlayersHouse_1F_Text_MomHealOffer:
	.string "MOM: You look worn out.\n"
	.string "Lie down for a minute. I'll watch\l"
	.string "over your POKéMON.$"

TwinleafTown_PlayersHouse_1F_Text_MomHealDone:
	.string "MOM: Your team looks ready again.\n"
	.string "Take care out there, honey.$"
