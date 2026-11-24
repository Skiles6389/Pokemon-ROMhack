PastoriaCity_Mart_MapScripts::
	.byte 0

PastoriaCity_Mart_EventScript_Clerk::
	lock
	faceplayer
	msgbox PastoriaCity_Mart_Text_ClerkAsk, MSGBOX_DEFAULT
	pokemart PastoriaCity_Mart_Pokemart
	msgbox PastoriaCity_Mart_Text_ClerkFarewell, MSGBOX_DEFAULT
	release
	end

	.align 2
PastoriaCity_Mart_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_REPEL
	.2byte ITEM_NONE
	release
	end

PastoriaCity_Mart_Text_ClerkAsk:
	.string "Welcome to Pastoria Mart!\n"
	.string "Need supplies for the marsh?$"

PastoriaCity_Mart_Text_ClerkFarewell:
	.string "Stay dry out there!$"

PastoriaCity_Mart_EventScript_Customer::
	msgbox PastoriaCity_Mart_Text_Customer, MSGBOX_NPC
	end

PastoriaCity_Mart_Text_Customer:
	.string "Great Balls and Super Potions--\n"
	.string "that's my marsh kit.$"
