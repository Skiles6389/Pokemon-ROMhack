SolaceonTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SolaceonTown_OnTransition
	.byte 0

SolaceonTown_OnTransition:
	setflag FLAG_VISITED_SOLACEON_TOWN
	end

SolaceonTown_EventScript_Cowgirl::
	msgbox SolaceonTown_Text_Cowgirl, MSGBOX_NPC
	end

SolaceonTown_EventScript_Rancher::
	msgbox SolaceonTown_Text_Rancher, MSGBOX_NPC
	end

SolaceonTown_EventScript_Twin::
	msgbox SolaceonTown_Text_Twin, MSGBOX_NPC
	end

SolaceonTown_EventScript_RuinManiac::
	msgbox SolaceonTown_Text_RuinManiac, MSGBOX_NPC
	end

SolaceonTown_EventScript_Boy::
	msgbox SolaceonTown_Text_Boy, MSGBOX_NPC
	end

SolaceonTown_EventScript_Girl::
	msgbox SolaceonTown_Text_Girl, MSGBOX_NPC
	end

SolaceonTown_EventScript_TownSign::
	msgbox SolaceonTown_Text_TownSign, MSGBOX_SIGN
	end

SolaceonTown_EventScript_DayCareSign::
	msgbox SolaceonTown_Text_DayCareSign, MSGBOX_SIGN
	end

SolaceonTown_EventScript_NewsPressSign::
	msgbox SolaceonTown_Text_NewsPressSign, MSGBOX_SIGN
	end

SolaceonTown_EventScript_RuinsSign::
	msgbox SolaceonTown_Text_RuinsSign, MSGBOX_SIGN
	end

SolaceonTown_Text_Cowgirl:
	.string "Pastures around Solaceon are wide.\n"
	.string "Great place to raise tough partners!$"

SolaceonTown_Text_Rancher:
	.string "Ranch work starts early.\n"
	.string "POKéMON help with every chore.$"

SolaceonTown_Text_Twin:
	.string "The Day Care Lady is so kind!\n"
	.string "She always remembers my POKéMON.$"

SolaceonTown_Text_RuinManiac:
	.string "Those cliff mouths lead to ruins.\n"
	.string "The interior isn't open yet--patience!$"

SolaceonTown_Text_Boy:
	.string "News Press prints Contest gossip.\n"
	.string "I grab a paper every week!$"

SolaceonTown_Text_Girl:
	.string "Route 210 north is blocked by\n"
	.string "PSYDUCK with headaches. Weird, huh?$"

SolaceonTown_Text_TownSign:
	.string "SOLACEON TOWN\n"
	.string "A town of warm hearts and quiet ruins$"

SolaceonTown_Text_DayCareSign:
	.string "POKéMON DAY CARE\n"
	.string "Let us raise your partners$"

SolaceonTown_Text_NewsPressSign:
	.string "SOLACEON NEWS PRESS\n"
	.string "Fresh headlines daily$"

SolaceonTown_Text_RuinsSign:
	.string "SOLACEON RUINS\n"
	.string "Unown research ongoing$"
SolaceonTown_EventScript_PlatNpc0::
	msgbox SolaceonTown_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

SolaceonTown_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

SolaceonTown_EventScript_PlatNpc1::
	msgbox SolaceonTown_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

SolaceonTown_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

SolaceonTown_EventScript_PlatNpc2::
	msgbox SolaceonTown_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

SolaceonTown_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

SolaceonTown_EventScript_PlatNpc4::
	msgbox SolaceonTown_EventScript_PlatNpc4_Text, MSGBOX_NPC
	end

SolaceonTown_EventScript_PlatNpc4_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

SolaceonTown_EventScript_PlatNpc5::
	msgbox SolaceonTown_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

SolaceonTown_EventScript_PlatNpc5_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

SolaceonTown_EventScript_PlatNpc6::
	msgbox SolaceonTown_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

SolaceonTown_EventScript_PlatNpc6_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

SolaceonTown_EventScript_PlatNpc7::
	msgbox SolaceonTown_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

SolaceonTown_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

SolaceonTown_EventScript_PlatNpc8::
	msgbox SolaceonTown_EventScript_PlatNpc8_Text, MSGBOX_NPC
	end

SolaceonTown_EventScript_PlatNpc8_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

