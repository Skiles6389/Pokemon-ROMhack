OreburghMine_B1F_MapScripts::
	.byte 0

OreburghMine_B1F_EventScript_Worker::
	msgbox OreburghMine_B1F_Text_Worker, MSGBOX_NPC
	end

OreburghMine_B1F_EventScript_Twin::
	msgbox OreburghMine_B1F_Text_Twin, MSGBOX_NPC
	end

OreburghMine_B1F_EventScript_Hiker::
	msgbox OreburghMine_B1F_Text_Hiker, MSGBOX_NPC
	end

OreburghMine_B1F_Text_Worker:
	.string "Kid, you're in the mine. Stay\n"
	.string "close to the lamps.$"

OreburghMine_B1F_Text_Twin:
	.string "I'm waiting for my dad to finish\n"
	.string "his shift!$"

OreburghMine_B1F_Text_Hiker:
	.string "Looking for ROARK? He's down on\n"
	.string "the lowest floor, way at the back.$"
