VeilstoneCity_DepartmentStore_5F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VeilstoneCity_DepartmentStore_5F_OnTransition
	.byte 0

VeilstoneCity_DepartmentStore_5F_OnTransition:
	setvar VAR_DEPT_STORE_FLOOR, DEPT_STORE_FLOORNUM_5F
	setdynamicwarp MAP_VEILSTONE_CITY_DEPARTMENT_STORE_5F, 2, 1
	end

VeilstoneCity_DepartmentStore_5F_EventScript_LittleGirl::
	msgbox VeilstoneCity_DepartmentStore_5F_Text_LittleGirl, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_5F_Text_LittleGirl:
	.string "Mommy says vitamins make POKéMON\n"
	.string "grow big and strong.$"

VeilstoneCity_DepartmentStore_5F_EventScript_PokefanF::
	msgbox VeilstoneCity_DepartmentStore_5F_Text_PokefanF, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_5F_Text_PokefanF:
	.string "The rooftop is closed for\n"
	.string "repairs. What a shame!$"

VeilstoneCity_DepartmentStore_5F_EventScript_ClerkVitamins::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_5F_Pokemart_ClerkVitamins
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_5F_Pokemart_ClerkVitamins:
	.2byte ITEM_HP_UP
	.2byte ITEM_PROTEIN
	.2byte ITEM_IRON
	.2byte ITEM_CALCIUM
	.2byte ITEM_ZINC
	.2byte ITEM_CARBOS
	pokemartlistend

VeilstoneCity_DepartmentStore_5F_EventScript_ClerkSupplies::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_5F_Pokemart_ClerkSupplies
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_5F_Pokemart_ClerkSupplies:
	.2byte ITEM_PP_UP
	.2byte ITEM_ELIXIR
	.2byte ITEM_MAX_REVIVE
	.2byte ITEM_FULL_HEAL
	pokemartlistend

VeilstoneCity_DepartmentStore_5F_EventScript_Woman::
	msgbox VeilstoneCity_DepartmentStore_5F_Text_Woman, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_5F_Text_Woman:
	.string "Vitamins are pricey, but your\n"
	.string "POKéMON will thank you.$"

VeilstoneCity_DepartmentStore_5F_EventScript_RooftopClosed::
	lockall
	msgbox VeilstoneCity_DepartmentStore_5F_Text_RooftopClosed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, VeilstoneCity_DepartmentStore_5F_Movement_StepBack
	waitmovement 0
	releaseall
	end

VeilstoneCity_DepartmentStore_5F_Movement_StepBack:
	walk_down
	step_end

VeilstoneCity_DepartmentStore_5F_Text_RooftopClosed:
	.string "The rooftop is closed for repairs.\n"
	.string "Please use the stairs or elevator.$"
