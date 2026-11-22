SandgemTown_Mart_MapScripts::
	.byte 0

SandgemTown_Mart_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart SandgemTown_Mart_Items
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
SandgemTown_Mart_Items:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	pokemartlistend

SandgemTown_Mart_EventScript_Girl::
	msgbox SandgemTown_Mart_Text_Girl, MSGBOX_NPC
	end

SandgemTown_Mart_Text_Girl:
	.string "A POTION for the hurt ones, and a\n"
	.string "POKé BALL for the ones still wild.$"
