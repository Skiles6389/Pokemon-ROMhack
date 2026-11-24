EternaCity_Mart_MapScripts::
	.byte 0

EternaCity_Mart_EventScript_Clerk::
	lock
	faceplayer
	msgbox EternaCity_Mart_Text_ClerkAsk, MSGBOX_DEFAULT
	pokemart EternaCity_Mart_Pokemart
	msgbox EternaCity_Mart_Text_ClerkFarewell, MSGBOX_DEFAULT
	release
	end

EternaCity_Mart_EventScript_Scientist::
	msgbox EternaCity_Mart_Text_Scientist, MSGBOX_NPC
	end

	.align 2
EternaCity_Mart_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
		.2byte ITEM_NONE
	release
	end

EternaCity_Mart_Text_ClerkAsk:
	.string "Welcome to Eterna Mart!\n"
	.string "What can I get you?$"

EternaCity_Mart_Text_ClerkFarewell:
	.string "Herbs are popular near the forest.\n"
	.string "Stock up before you go!$"

EternaCity_Mart_Text_Scientist:
	.string "Team Galactic can't steal shopping\n"
	.string "time from me!$"
