EternaCity_HerbShop_MapScripts::
	.byte 0

EternaCity_HerbShop_EventScript_Clerk::
	lock
	faceplayer
	msgbox EternaCity_HerbShop_Text_ClerkAsk, MSGBOX_DEFAULT
	pokemart EternaCity_HerbShop_Pokemart
	msgbox EternaCity_HerbShop_Text_Farewell, MSGBOX_DEFAULT
	release
	end

	.align 2
EternaCity_HerbShop_Pokemart:
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
		.2byte ITEM_NONE
	release
	end

EternaCity_HerbShop_Text_ClerkAsk:
	.string "Herbal remedies from the forest!\n"
	.string "They smell strong but work fast.$"

EternaCity_HerbShop_Text_Farewell:
	.string "Bitter medicine heals best!$"
