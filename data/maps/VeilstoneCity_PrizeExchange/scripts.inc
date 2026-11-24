VeilstoneCity_PrizeExchange_MapScripts::
	.byte 0

VeilstoneCity_PrizeExchange_EventScript_Clerk::
	msgbox VeilstoneCity_PrizeExchange_Text_Clerk, MSGBOX_NPC
	end

VeilstoneCity_PrizeExchange_Text_Clerk:
	.string "Welcome to the PRIZE EXCHANGE!\p"
	.string "We're waiting on a fresh shipment\n"
	.string "of prizes, so the counter is\l"
	.string "closed for the time being.\p"
	.string "Please check back later!$"

VeilstoneCity_PrizeExchange_EventScript_Woman::
	msgbox VeilstoneCity_PrizeExchange_Text_Woman, MSGBOX_NPC
	end

VeilstoneCity_PrizeExchange_Text_Woman:
	.string "I'm just here to admire the\n"
	.string "prize shelves. Pretty, aren't they?$"
