VeilstoneCity_DepartmentStore_2F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VeilstoneCity_DepartmentStore_2F_OnTransition
	.byte 0

VeilstoneCity_DepartmentStore_2F_OnTransition:
	setvar VAR_DEPT_STORE_FLOOR, DEPT_STORE_FLOORNUM_2F
	setdynamicwarp MAP_VEILSTONE_CITY_DEPARTMENT_STORE_2F, 2, 1
	end

VeilstoneCity_DepartmentStore_2F_EventScript_Cook::
	msgbox VeilstoneCity_DepartmentStore_2F_Text_Cook, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_2F_Text_Cook:
	.string "Stock up on medicine before the\n"
	.string "next Gym. It's just smart.$"

VeilstoneCity_DepartmentStore_2F_EventScript_PokefanF::
	msgbox VeilstoneCity_DepartmentStore_2F_Text_PokefanF, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_2F_Text_PokefanF:
	.string "A fine potion for a fine partner!$"

VeilstoneCity_DepartmentStore_2F_EventScript_Sailor::
	msgbox VeilstoneCity_DepartmentStore_2F_Text_Sailor, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_2F_Text_Sailor:
	.string "Long trips need plenty of\n"
	.string "healing items. Trust me.$"

VeilstoneCity_DepartmentStore_2F_EventScript_ClerkPotions::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_2F_Pokemart_ClerkPotions
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_2F_Pokemart_ClerkPotions:
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_MAX_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_ETHER
	pokemartlistend

VeilstoneCity_DepartmentStore_2F_EventScript_ClerkStatus::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_2F_Pokemart_ClerkStatus
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_2F_Pokemart_ClerkStatus:
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_FULL_HEAL
	pokemartlistend
