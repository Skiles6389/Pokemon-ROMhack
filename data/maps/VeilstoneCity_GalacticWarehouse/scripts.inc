VeilstoneCity_GalacticWarehouse_MapScripts::
	.byte 0

VeilstoneCity_GalacticWarehouse_EventScript_ItemHMFly::
	lock
	giveitem ITEM_HM_FLY
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	removeobject VAR_LAST_TALKED
	setflag FLAG_GOT_HM_FLY_VEILSTONE
	msgbox VeilstoneCity_GalacticWarehouse_Text_ExplainFly, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_GalacticWarehouse_EventScript_LockedDoor::
	lockall
	msgbox VeilstoneCity_GalacticWarehouse_Text_LockedDoor, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, VeilstoneCity_GalacticWarehouse_Movement_StepBack
	waitmovement 0
	releaseall
	end

VeilstoneCity_GalacticWarehouse_Movement_StepBack:
	walk_down
	step_end

VeilstoneCity_GalacticWarehouse_EventScript_Scientist::
	lock
	faceplayer
	msgbox VeilstoneCity_GalacticWarehouse_Text_Scientist, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_GalacticWarehouse_Text_ExplainFly:
	.string "HM02 contains FLY!\p"
	.string "A POKéMON that learns it can carry\n"
	.string "you to any town you've visited.\p"
	.string "You'll need the COBBLE BADGE to use\n"
	.string "it outside of battle.$"

VeilstoneCity_GalacticWarehouse_Text_LockedDoor:
	.string "The door is locked tight.\p"
	.string "A card reader beside it reads:\n"
	.string "“STORAGE KEY REQUIRED.”$"

VeilstoneCity_GalacticWarehouse_Text_Scientist:
	.string "Eek! Please don't hurt me!\p"
	.string "I just catalog crates for TEAM\n"
	.string "GALACTIC. The rest of the crew\l"
	.string "left in a rush.\p"
	.string "The real storage is behind that\n"
	.string "locked door. Only the Commander\l"
	.string "carries the STORAGE KEY.$"

VeilstoneCity_GalacticWarehouse_EventScript_Crates::
	msgbox VeilstoneCity_GalacticWarehouse_Text_Crates, MSGBOX_SIGN
	end

VeilstoneCity_GalacticWarehouse_Text_Crates:
	.string "Stacked crates marked with the\n"
	.string "TEAM GALACTIC logo. All empty.$"
