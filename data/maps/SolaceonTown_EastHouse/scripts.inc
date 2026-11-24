SolaceonTown_EastHouse_MapScripts::
	.byte 0

SolaceonTown_EastHouse_EventScript_Woman::
	msgbox SolaceonTown_EastHouse_Text_Woman, MSGBOX_NPC
	end

SolaceonTown_EastHouse_EventScript_Boy::
	msgbox SolaceonTown_EastHouse_Text_Boy, MSGBOX_NPC
	end

SolaceonTown_EastHouse_Text_Woman:
	.string "Hearthome Contests are famous, but\n"
	.string "Solaceon stays peacefully quiet.$"

SolaceonTown_EastHouse_Text_Boy:
	.string "I want to read every Unown letter!$"
