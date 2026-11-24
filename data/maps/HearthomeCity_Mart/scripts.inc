HearthomeCity_Mart_MapScripts::
	.byte 0

HearthomeCity_Mart_EventScript_Clerk::
	lock
	faceplayer
	msgbox HearthomeCity_Mart_Text_ClerkAsk, MSGBOX_DEFAULT
	pokemart HearthomeCity_Mart_Pokemart
	msgbox HearthomeCity_Mart_Text_ClerkFarewell, MSGBOX_DEFAULT
	release
	end

HearthomeCity_Mart_EventScript_Girl::
	msgbox HearthomeCity_Mart_Text_Girl, MSGBOX_NPC
	end

	.align 2
HearthomeCity_Mart_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_NONE
	release
	end

HearthomeCity_Mart_Text_ClerkAsk:
	.string "Welcome to Hearthome Mart!\n"
	.string "May I help you?$"

HearthomeCity_Mart_Text_ClerkFarewell:
	.string "Please come again!$"

HearthomeCity_Mart_Text_Girl:
	.string "Stock up before the Gym.\n"
	.string "Ghost battles get spooky!$"
