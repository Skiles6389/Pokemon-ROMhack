StarkMountain_HeatranRoom_MapScripts::
	.byte 0

StarkMountain_HeatranRoom_EventScript_Npc0::
	msgbox StarkMountain_HeatranRoom_EventScript_Npc0_Text, MSGBOX_NPC
	end

StarkMountain_HeatranRoom_EventScript_Npc0_Text:
	.string "Lava light paints the walls.$"

StarkMountain_HeatranRoom_EventScript_Npc1::
	msgbox StarkMountain_HeatranRoom_EventScript_Npc1_Text, MSGBOX_NPC
	end

StarkMountain_HeatranRoom_EventScript_Npc1_Text:
	.string "Lava light paints the walls.$"

StarkMountain_HeatranRoom_EventScript_Npc2::
	msgbox StarkMountain_HeatranRoom_EventScript_Npc2_Text, MSGBOX_NPC
	end

StarkMountain_HeatranRoom_EventScript_Npc2_Text:
	.string "Lava light paints the walls.$"

StarkMountain_HeatranRoom_EventScript_Npc4::
	msgbox StarkMountain_HeatranRoom_EventScript_Npc4_Text, MSGBOX_NPC
	end

StarkMountain_HeatranRoom_EventScript_Npc4_Text:
	.string "Lava light paints the walls.$"

StarkMountain_HeatranRoom_EventScript_Npc5::
	msgbox StarkMountain_HeatranRoom_EventScript_Npc5_Text, MSGBOX_NPC
	end

StarkMountain_HeatranRoom_EventScript_Npc5_Text:
	.string "Lava light paints the walls.$"

StarkMountain_HeatranRoom_EventScript_Npc6::
	msgbox StarkMountain_HeatranRoom_EventScript_Npc6_Text, MSGBOX_NPC
	end

StarkMountain_HeatranRoom_EventScript_Npc6_Text:
	.string "Lava light paints the walls.$"

StarkMountain_HeatranRoom_EventScript_Npc7::
	msgbox StarkMountain_HeatranRoom_EventScript_Npc7_Text, MSGBOX_NPC
	end

StarkMountain_HeatranRoom_EventScript_Npc7_Text:
	.string "Lava light paints the walls.$"

StarkMountain_HeatranRoom_EventScript_Npc8::
	msgbox StarkMountain_HeatranRoom_EventScript_Npc8_Text, MSGBOX_NPC
	end

StarkMountain_HeatranRoom_EventScript_Npc8_Text:
	.string "Lava light paints the walls.$"


StarkMountain_HeatranRoom_EventScript_Heatran::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_HEATRAN_STARK, StarkMountain_HeatranRoom_EventScript_HeatranGone
	msgbox StarkMountain_HeatranRoom_Text_Heatran, MSGBOX_DEFAULT
	setwildbattle SPECIES_HEATRAN, 70
	dowildbattle
	setflag FLAG_DEFEATED_HEATRAN_STARK
	release
	end

StarkMountain_HeatranRoom_EventScript_HeatranGone::
	msgbox StarkMountain_HeatranRoom_Text_HeatranGone, MSGBOX_DEFAULT
	release
	end

StarkMountain_HeatranRoom_Text_Heatran:
	.string "A fierce heat wells up from the rock...\n"
	.string "Heatran appears!$"

StarkMountain_HeatranRoom_Text_HeatranGone:
	.string "The magma chamber is quiet now.$"
