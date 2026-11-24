VeilstoneCity_DepartmentStore_4F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VeilstoneCity_DepartmentStore_4F_OnTransition
	.byte 0

VeilstoneCity_DepartmentStore_4F_OnTransition:
	setvar VAR_DEPT_STORE_FLOOR, DEPT_STORE_FLOORNUM_4F
	setdynamicwarp MAP_VEILSTONE_CITY_DEPARTMENT_STORE_4F, 2, 1
	end

VeilstoneCity_DepartmentStore_4F_EventScript_Gentleman::
	msgbox VeilstoneCity_DepartmentStore_4F_Text_Gentleman, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_4F_Text_Gentleman:
	.string "X items give a short boost in\n"
	.string "battle. A clever trainer's trick.$"

VeilstoneCity_DepartmentStore_4F_EventScript_Woman::
	msgbox VeilstoneCity_DepartmentStore_4F_Text_Woman, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_4F_Text_Woman:
	.string "Repels keep wild POKéMON away.\n"
	.string "Perfect for a long walk!$"

VeilstoneCity_DepartmentStore_4F_EventScript_Youngster::
	msgbox VeilstoneCity_DepartmentStore_4F_Text_Youngster, MSGBOX_NPC
	end

VeilstoneCity_DepartmentStore_4F_Text_Youngster:
	.string "I save my allowance for DIRE HITs!$"

VeilstoneCity_DepartmentStore_4F_EventScript_ClerkBattle::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_4F_Pokemart_ClerkBattle
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_4F_Pokemart_ClerkBattle:
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFENSE
	.2byte ITEM_X_SPEED
	.2byte ITEM_X_ACCURACY
	.2byte ITEM_DIRE_HIT
	.2byte ITEM_GUARD_SPEC
	pokemartlistend

VeilstoneCity_DepartmentStore_4F_EventScript_ClerkEscape::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart VeilstoneCity_DepartmentStore_4F_Pokemart_ClerkEscape
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
VeilstoneCity_DepartmentStore_4F_Pokemart_ClerkEscape:
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_FLUFFY_TAIL
	pokemartlistend
