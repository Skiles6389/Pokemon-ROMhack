OreburghCity_Mart_MapScripts::
	.byte 0

@ Platinum's Oreburgh stock with no badges, plus its specialty balls.
@ Tunnel Mail doesn't exist in this engine, so it is left out.
OreburghCity_Mart_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart OreburghCity_Mart_Items
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
OreburghCity_Mart_Items:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_HEAL_BALL
	.2byte ITEM_NET_BALL
	pokemartlistend

OreburghCity_Mart_EventScript_Hiker::
	msgbox OreburghCity_Mart_Text_Hiker, MSGBOX_NPC
	end

OreburghCity_Mart_EventScript_Collector::
	msgbox OreburghCity_Mart_Text_Collector, MSGBOX_NPC
	end

OreburghCity_Mart_Text_Hiker:
	.string "ESCAPE ROPES are a miner's best\n"
	.string "friend. Wish they sold them here.$"

OreburghCity_Mart_Text_Collector:
	.string "NET BALLS work wonders on Water\n"
	.string "and Bug POKéMON.$"
