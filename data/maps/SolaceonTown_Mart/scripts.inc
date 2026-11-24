SolaceonTown_Mart_MapScripts::
	.byte 0

SolaceonTown_Mart_EventScript_Clerk::
	lock
	faceplayer
	msgbox SolaceonTown_Mart_Text_ClerkAsk, MSGBOX_DEFAULT
	pokemart SolaceonTown_Mart_Pokemart
	msgbox SolaceonTown_Mart_Text_ClerkFarewell, MSGBOX_DEFAULT
	release
	end

SolaceonTown_Mart_EventScript_Girl::
	msgbox SolaceonTown_Mart_Text_Girl, MSGBOX_NPC
	end

	.align 2
SolaceonTown_Mart_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_NONE
	release
	end

SolaceonTown_Mart_Text_ClerkAsk:
	.string "Welcome to Solaceon Mart!\n"
	.string "What can I get you?$"

SolaceonTown_Mart_Text_ClerkFarewell:
	.string "Come again!$"

SolaceonTown_Mart_Text_Girl:
	.string "Stock up before Route 215.\n"
	.string "That rain soaks everything!$"
