FloaromaTown_MapScripts::
	.byte 0

FloaromaTown_EventScript_Breeder::
	msgbox FloaromaTown_Text_Breeder, MSGBOX_NPC
	end

FloaromaTown_EventScript_LassWest::
	msgbox FloaromaTown_Text_LassWest, MSGBOX_NPC
	end

FloaromaTown_EventScript_SchoolKid::
	msgbox FloaromaTown_Text_SchoolKid, MSGBOX_NPC
	end

FloaromaTown_EventScript_Beauty::
	msgbox FloaromaTown_Text_Beauty, MSGBOX_NPC
	end

FloaromaTown_EventScript_LassEast::
	msgbox FloaromaTown_Text_LassEast, MSGBOX_NPC
	end

FloaromaTown_EventScript_Camper::
	msgbox FloaromaTown_Text_Camper, MSGBOX_NPC
	end

FloaromaTown_EventScript_EastGate::
	msgbox FloaromaTown_Text_EastGate, MSGBOX_NPC
	end

FloaromaTown_EventScript_EastGateTrigger::
	lockall
	msgbox FloaromaTown_Text_EastGateBlock, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, FloaromaTown_Movement_PushBack
	waitmovement 0
	releaseall
	end

FloaromaTown_Movement_PushBack:
	walk_left
	step_end

FloaromaTown_EventScript_TownSign::
	msgbox FloaromaTown_Text_TownSign, MSGBOX_SIGN
	end

FloaromaTown_EventScript_FlowerShopSign::
	msgbox FloaromaTown_Text_FlowerShopSign, MSGBOX_SIGN
	end

FloaromaTown_EventScript_MeadowSign::
	msgbox FloaromaTown_Text_MeadowSign, MSGBOX_SIGN
	end

FloaromaTown_Text_Breeder:
	.string "The meadows north of town are thick\n"
	.string "with Honey. Watch your step!$"

FloaromaTown_Text_LassWest:
	.string "Pick a Peck of Colors sells Berries\n"
	.string "and watering cans. It smells amazing.$"

FloaromaTown_Text_SchoolKid:
	.string "I wrote a report on flower POKéMON.\n"
	.string "My teacher said it was fragrant.$"

FloaromaTown_Text_Beauty:
	.string "Floaroma never rushes anyone.\n"
	.string "Even the wind takes its time.$"

FloaromaTown_Text_LassEast:
	.string "If you follow the east road, you'll\n"
	.string "reach Valley Windworks eventually.$"

FloaromaTown_Text_Camper:
	.string "Some shady characters headed for\n"
	.string "the meadow. They smelled like trouble.$"

FloaromaTown_Text_EastGate:
	.string "Valley Windworks is that way, but\n"
	.string "the path isn't ready yet.$"

FloaromaTown_Text_EastGateBlock:
	.string "Valley Windworks is coming in the\n"
	.string "next milestone. Turn back for now.$"

FloaromaTown_Text_TownSign:
	.string "FLOAROMA TOWN\n"
	.string "A town of blooming breezes$"

FloaromaTown_Text_FlowerShopSign:
	.string "PICK A PECK OF COLORS\n"
	.string "Flower Shop$"

FloaromaTown_Text_MeadowSign:
	.string "FLOAROMA MEADOW\n"
	.string "Honey trees ahead$"
