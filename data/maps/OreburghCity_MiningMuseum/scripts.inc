OreburghCity_MiningMuseum_MapScripts::
	.byte 0

@ A basic Mining Museum. The upper floor and fossil restoration come later.
OreburghCity_MiningMuseum_EventScript_Receptionist::
	msgbox OreburghCity_MiningMuseum_Text_Receptionist, MSGBOX_NPC
	end

OreburghCity_MiningMuseum_EventScript_OldMan::
	msgbox OreburghCity_MiningMuseum_Text_OldMan, MSGBOX_NPC
	end

OreburghCity_MiningMuseum_EventScript_Scientist::
	msgbox OreburghCity_MiningMuseum_Text_Scientist, MSGBOX_NPC
	end

OreburghCity_MiningMuseum_EventScript_Worker::
	msgbox OreburghCity_MiningMuseum_Text_Worker, MSGBOX_NPC
	end

OreburghCity_MiningMuseum_EventScript_ExhibitCoal::
	msgbox OreburghCity_MiningMuseum_Text_ExhibitCoal, MSGBOX_SIGN
	end

OreburghCity_MiningMuseum_EventScript_ExhibitTools::
	msgbox OreburghCity_MiningMuseum_Text_ExhibitTools, MSGBOX_SIGN
	end

OreburghCity_MiningMuseum_EventScript_ExhibitHistory::
	msgbox OreburghCity_MiningMuseum_Text_ExhibitHistory, MSGBOX_SIGN
	end

OreburghCity_MiningMuseum_Text_Receptionist:
	.string "Welcome to the OREBURGH MINING\n"
	.string "MUSEUM! Entry is free.$"

OreburghCity_MiningMuseum_Text_OldMan:
	.string "I swung a pickaxe in that mine\n"
	.string "for forty years.$"

OreburghCity_MiningMuseum_Text_Scientist:
	.string "Old fossils turn up in the mine\n"
	.string "now and then. Fascinating!$"

OreburghCity_MiningMuseum_Text_Worker:
	.string "Most of SINNOH's coal comes out\n"
	.string "of the ground right here.$"

OreburghCity_MiningMuseum_Text_ExhibitCoal:
	.string "A lump of coal from the deepest\n"
	.string "seam in the mine.$"

OreburghCity_MiningMuseum_Text_ExhibitTools:
	.string "Pickaxes and lamps used by the\n"
	.string "town's first miners.$"

OreburghCity_MiningMuseum_Text_ExhibitHistory:
	.string "A map of the mine's tunnels.\n"
	.string "They run under the whole town!$"
