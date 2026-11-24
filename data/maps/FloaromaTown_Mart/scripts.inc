FloaromaTown_Mart_MapScripts::
	.byte 0

FloaromaTown_Mart_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart FloaromaTown_Mart_Pokemart
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
FloaromaTown_Mart_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_REPEL
	.2byte ITEM_NONE
	release
	end

FloaromaTown_Mart_EventScript_Woman::
	msgbox FloaromaTown_Mart_Text_Woman, MSGBOX_NPC
	end

FloaromaTown_Mart_Text_Woman:
	.string "I always stock up on REPELs before\n"
	.string "walking the meadow trails.$"
