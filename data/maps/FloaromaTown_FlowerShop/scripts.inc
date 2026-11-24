FloaromaTown_FlowerShop_MapScripts::
	.byte 0

FloaromaTown_FlowerShop_EventScript_Owner::
	msgbox FloaromaTown_FlowerShop_Text_Owner, MSGBOX_NPC
	end

FloaromaTown_FlowerShop_EventScript_BerryGirl::
	msgbox FloaromaTown_FlowerShop_Text_BerryGirl, MSGBOX_NPC
	end

FloaromaTown_FlowerShop_EventScript_Sprayduck::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_WAILMER_PAIL, FloaromaTown_FlowerShop_EventScript_HaveSprayduck
	msgbox FloaromaTown_FlowerShop_Text_OfferSprayduck, MSGBOX_DEFAULT
	giveitem ITEM_SPRAYDUCK
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_WAILMER_PAIL
	msgbox FloaromaTown_FlowerShop_Text_ExplainSprayduck, MSGBOX_DEFAULT
	release
	end

FloaromaTown_FlowerShop_EventScript_HaveSprayduck::
	msgbox FloaromaTown_FlowerShop_Text_HaveSprayduck, MSGBOX_DEFAULT
	release
	end

FloaromaTown_FlowerShop_Text_Owner:
	.string "Welcome to Pick a Peck of Colors!\n"
	.string "Our blooms are Sinnoh-grown.$"

FloaromaTown_FlowerShop_Text_BerryGirl:
	.string "Berries love a drink after planting.\n"
	.string "Don't forget to water them!$"

FloaromaTown_FlowerShop_Text_OfferSprayduck:
	.string "You look like a Trainer who plants\n"
	.string "Berries. Take this SPRAYDUCK!$"

FloaromaTown_FlowerShop_Text_ExplainSprayduck:
	.string "Use it on soft soil to keep your\n"
	.string "Berry trees happy.$"

FloaromaTown_FlowerShop_Text_HaveSprayduck:
	.string "How are the Berries growing?$"
