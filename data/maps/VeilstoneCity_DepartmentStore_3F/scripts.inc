VeilstoneCity_DepartmentStore_3F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VeilstoneCity_DepartmentStore_3F_OnTransition
	.byte 0

VeilstoneCity_DepartmentStore_3F_OnTransition:
	setvar VAR_DEPT_STORE_FLOOR, DEPT_STORE_FLOORNUM_3F
	setdynamicwarp MAP_VEILSTONE_CITY_DEPARTMENT_STORE_3F, 2, 1
	end

VeilstoneCity_DepartmentStore_3F_EventScript_Triathlete::
	msgbox VeilstoneCity_DepartmentStore_3F_Text_Triathlete, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_3F_Text_Triathlete:
	.string "The TMs on this floor are a good\n"
	.string "fit for any fighter.$"

VeilstoneCity_DepartmentStore_3F_EventScript_PokefanM::
	msgbox VeilstoneCity_DepartmentStore_3F_Text_PokefanM, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_3F_Text_PokefanM:
	.string "Brick Break shatters walls,\n"
	.string "and Bulk Up builds a champion.$"

VeilstoneCity_DepartmentStore_3F_EventScript_Woman::
	msgbox VeilstoneCity_DepartmentStore_3F_Text_Woman, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_3F_Text_Woman:
	.string "A TM can be used over and over.\n"
	.string "What a great invention!$"

VeilstoneCity_DepartmentStore_3F_EventScript_ClerkFighting::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_3F_Pokemart_ClerkFighting
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_3F_Pokemart_ClerkFighting:
	.2byte ITEM_TM_BRICK_BREAK
	.2byte ITEM_TM_BULK_UP
	.2byte ITEM_TM_FOCUS_PUNCH
	pokemartlistend

VeilstoneCity_DepartmentStore_3F_EventScript_ClerkUtility::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_3F_Pokemart_ClerkUtility
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_3F_Pokemart_ClerkUtility:
	.2byte ITEM_TM_ROCK_TOMB
	.2byte ITEM_TM_DOUBLE_TEAM
	.2byte ITEM_TM_REST
	pokemartlistend
