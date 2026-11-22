JubilifeCity_Mart_MapScripts::
	.byte 0

JubilifeCity_Mart_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart JubilifeCity_Mart_Items
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
JubilifeCity_Mart_Items:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	pokemartlistend

JubilifeCity_Mart_EventScript_Girl::
	msgbox JubilifeCity_Mart_Text_Girl, MSGBOX_NPC
	end

JubilifeCity_Mart_Text_Girl:
	.string "Status heals sit next to the\n"
	.string "POTIONS. Read the label.$"
