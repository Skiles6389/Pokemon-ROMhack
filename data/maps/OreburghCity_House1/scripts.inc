OreburghCity_House1_MapScripts::
	.byte 0

OreburghCity_House1_EventScript_Woman::
	msgbox OreburghCity_House1_Text_Woman, MSGBOX_NPC
	end

OreburghCity_House1_EventScript_Worker::
	msgbox OreburghCity_House1_Text_Worker, MSGBOX_NPC
	end

OreburghCity_House1_Text_Woman:
	.string "I sweep coal dust off the steps\n"
	.string "every single morning.$"

OreburghCity_House1_Text_Worker:
	.string "Day off! No digging today.$"
