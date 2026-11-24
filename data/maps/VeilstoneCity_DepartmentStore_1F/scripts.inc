VeilstoneCity_DepartmentStore_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VeilstoneCity_DepartmentStore_1F_OnTransition
	.byte 0

VeilstoneCity_DepartmentStore_1F_OnTransition:
	setvar VAR_DEPT_STORE_FLOOR, DEPT_STORE_FLOORNUM_1F
	setdynamicwarp MAP_VEILSTONE_CITY_DEPARTMENT_STORE_1F, 2, 1
	end

VeilstoneCity_DepartmentStore_1F_EventScript_Greeter::
	msgbox VeilstoneCity_DepartmentStore_1F_Text_Greeter, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_1F_Text_Greeter:
	.string "Welcome to the VEILSTONE\n"
	.string "DEPARTMENT STORE!\p"
	.string "1F: POKé BALLS\n"
	.string "2F: MEDICINE\l"
	.string "3F: TECHNICAL MACHINES\l"
	.string "4F: BATTLE ITEMS\l"
	.string "5F: VITAMINS AND EXTRAS\p"
	.string "The elevator is by the west stairs.$"

VeilstoneCity_DepartmentStore_1F_EventScript_ClerkBalls::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_1F_Pokemart_ClerkBalls
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_1F_Pokemart_ClerkBalls:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_NET_BALL
	.2byte ITEM_NEST_BALL
	.2byte ITEM_REPEAT_BALL
	.2byte ITEM_TIMER_BALL
	.2byte ITEM_LUXURY_BALL
	pokemartlistend

VeilstoneCity_DepartmentStore_1F_EventScript_PokefanF::
	msgbox VeilstoneCity_DepartmentStore_1F_Text_PokefanF, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_1F_Text_PokefanF:
	.string "I always buy my POKé BALLS here.\n"
	.string "The selection is wonderful!$"

VeilstoneCity_DepartmentStore_1F_EventScript_LittleGirl::
	msgbox VeilstoneCity_DepartmentStore_1F_Text_LittleGirl, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_1F_Text_LittleGirl:
	.string "I'm not allowed to ride the\n"
	.string "elevator by myself yet!$"

VeilstoneCity_DepartmentStore_1F_EventScript_PokefanM::
	msgbox VeilstoneCity_DepartmentStore_1F_Text_PokefanM, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_1F_Text_PokefanM:
	.string "Five whole floors! You could get\n"
	.string "lost in here for a day.$"
