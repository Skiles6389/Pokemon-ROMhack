IronIsland_B3F_MapScripts::
	.byte 0

IronIsland_B3F_EventScript_Item0::
	finditem ITEM_ULTRA_BALL
	end


IronIsland_B3F_EventScript_RuinsNote::
	msgbox IronIsland_B3F_Text_RuinsNote, MSGBOX_NPC
	end

IronIsland_B3F_Text_RuinsNote:
	.string "The Iron Ruins seal is still locked.\n"
	.string "Only the proper keys will open it.$"
