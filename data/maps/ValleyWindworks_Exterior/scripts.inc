ValleyWindworks_Exterior_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, ValleyWindworks_Exterior_OnTransition
	.byte 0

ValleyWindworks_Exterior_OnTransition:
	call_if_set FLAG_WINDWORKS_DOOR_UNLOCKED, ValleyWindworks_Exterior_EventScript_HideDoorGrunt
	end

ValleyWindworks_Exterior_EventScript_HideDoorGrunt::
	setflag FLAG_HIDE_WINDWORKS_DOOR_GRUNT
	return

ValleyWindworks_Exterior_EventScript_DoorGrunt::
	lock
	faceplayer
	playbgm MUS_PL_ENCOUNTER_GALACTIC, FALSE
	msgbox ValleyWindworks_Exterior_Text_DoorGruntIntro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_GALACTIC_GRUNT_WINDWORKS_DOOR, ValleyWindworks_Exterior_Text_DoorGruntDefeat
	msgbox ValleyWindworks_Exterior_Text_DoorGruntFlee, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_WINDWORKS_DOOR_GRUNT, ValleyWindworks_Exterior_Movement_GruntEnter
	waitmovement 0
	removeobject LOCALID_WINDWORKS_DOOR_GRUNT
	setflag FLAG_HIDE_WINDWORKS_DOOR_GRUNT
	setflag FLAG_WINDWORKS_DOOR_LOCKED
	fadedefaultbgm
	release
	end

ValleyWindworks_Exterior_Movement_GruntEnter:
	walk_up
	step_end

ValleyWindworks_Exterior_EventScript_DoorGuard::
	goto_if_set FLAG_WINDWORKS_DOOR_UNLOCKED, ValleyWindworks_Exterior_EventScript_DoorGuardEnd
	lockall
	goto_if_set FLAG_WINDWORKS_DOOR_LOCKED, ValleyWindworks_Exterior_EventScript_TryUnlockFromGuard
	msgbox ValleyWindworks_Exterior_Text_DoorShut, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, ValleyWindworks_Exterior_Movement_PushDown
	waitmovement 0
	releaseall
	end

ValleyWindworks_Exterior_Movement_PushDown:
	walk_down
	step_end

ValleyWindworks_Exterior_EventScript_TryUnlockFromGuard::
	checkitem ITEM_WORKS_KEY
	goto_if_eq VAR_RESULT, FALSE, ValleyWindworks_Exterior_EventScript_LockedPushBack
	msgbox ValleyWindworks_Exterior_Text_UseWorksKey, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ValleyWindworks_Exterior_EventScript_LockedPushBack
	playse SE_PIN
	waitse
	msgbox ValleyWindworks_Exterior_Text_DoorOpened, MSGBOX_DEFAULT
	setflag FLAG_WINDWORKS_DOOR_UNLOCKED
	clearflag FLAG_WINDWORKS_DOOR_LOCKED
	releaseall
	end

ValleyWindworks_Exterior_EventScript_LockedPushBack::
	msgbox ValleyWindworks_Exterior_Text_LockedInside, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, ValleyWindworks_Exterior_Movement_PushDown
	waitmovement 0
	releaseall
	end

ValleyWindworks_Exterior_EventScript_DoorGuardEnd::
	end

ValleyWindworks_Exterior_EventScript_Door::
	lockall
	goto_if_set FLAG_WINDWORKS_DOOR_UNLOCKED, ValleyWindworks_Exterior_EventScript_Enter
	goto_if_set FLAG_WINDWORKS_DOOR_LOCKED, ValleyWindworks_Exterior_EventScript_TryUnlock
	msgbox ValleyWindworks_Exterior_Text_DoorShut, MSGBOX_DEFAULT
	releaseall
	end

ValleyWindworks_Exterior_EventScript_TryUnlock::
	checkitem ITEM_WORKS_KEY
	goto_if_eq VAR_RESULT, FALSE, ValleyWindworks_Exterior_EventScript_LockedNoKey
	msgbox ValleyWindworks_Exterior_Text_UseWorksKey, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ValleyWindworks_Exterior_EventScript_CancelUnlock
	playse SE_PIN
	waitse
	msgbox ValleyWindworks_Exterior_Text_DoorOpened, MSGBOX_DEFAULT
	setflag FLAG_WINDWORKS_DOOR_UNLOCKED
	clearflag FLAG_WINDWORKS_DOOR_LOCKED
	releaseall
	end

ValleyWindworks_Exterior_EventScript_CancelUnlock::
	releaseall
	end

ValleyWindworks_Exterior_EventScript_LockedNoKey::
	msgbox ValleyWindworks_Exterior_Text_LockedInside, MSGBOX_DEFAULT
	releaseall
	end

ValleyWindworks_Exterior_EventScript_Enter::
	msgbox ValleyWindworks_Exterior_Text_DoorOpenedShort, MSGBOX_DEFAULT
	closemessage
	warp MAP_VALLEY_WINDWORKS_INTERIOR, 12, 15
	waitstate
	releaseall
	end

ValleyWindworks_Exterior_EventScript_Potion::
	finditem ITEM_POTION
	end

ValleyWindworks_Exterior_EventScript_Sign::
	msgbox ValleyWindworks_Exterior_Text_Sign, MSGBOX_SIGN
	end

ValleyWindworks_Exterior_Text_DoorGruntIntro:
	.string "GRUNT: Nobody gets into Valley Windworks\n"
	.string "unless they wear Galactic colors!\p"
	.string "That look says you're going to try.\n"
	.string "Fine--earn your way past me!$"

ValleyWindworks_Exterior_Text_DoorGruntDefeat:
	.string "Beaten by some kid...?$"

ValleyWindworks_Exterior_Text_DoorGruntFlee:
	.string "Hah! Doesn't matter!\n"
	.string "I'll lock the door from inside!\p"
	.string "The other Works Key is with our crew\n"
	.string "in the Floaroma flower patch!\p"
	.string "Without it, you're stuck outside!$"

ValleyWindworks_Exterior_Text_DoorShut:
	.string "The door is shut tight.$"

ValleyWindworks_Exterior_Text_LockedInside:
	.string "It's locked from the inside!$"

ValleyWindworks_Exterior_Text_UseWorksKey:
	.string "It's locked from the inside!\n"
	.string "Use the WORKS KEY?$"

ValleyWindworks_Exterior_Text_DoorOpened:
	.string "Ker-chunk!\p"
	.string "The WORKS KEY opened Valley Windworks!$"

ValleyWindworks_Exterior_Text_DoorOpenedShort:
	.string "The door is unlocked.$"

ValleyWindworks_Exterior_Text_Sign:
	.string "VALLEY WINDWORKS\n"
	.string "Clean power from canyon winds$"
ValleyWindworks_Exterior_EventScript_PlatNpc1::
	msgbox ValleyWindworks_Exterior_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

ValleyWindworks_Exterior_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

