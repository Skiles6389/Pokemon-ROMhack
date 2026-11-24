Route227_MapScripts::
	.byte 0

Route227_EventScript_Npc0::
	msgbox Route227_EventScript_Npc0_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc0_Text:
	.string "The Battle Zone stretches across these routes.$"

Route227_EventScript_Npc1::
	msgbox Route227_EventScript_Npc1_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc1_Text:
	.string "The Battle Zone stretches across these routes.$"

Route227_EventScript_Npc2::
	msgbox Route227_EventScript_Npc2_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc2_Text:
	.string "The Battle Zone stretches across these routes.$"

Route227_EventScript_Npc3::
	msgbox Route227_EventScript_Npc3_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc3_Text:
	.string "The Battle Zone stretches across these routes.$"

Route227_EventScript_Npc4::
	msgbox Route227_EventScript_Npc4_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc4_Text:
	.string "The Battle Zone stretches across these routes.$"

Route227_EventScript_Tr5::
	trainerbattle_single TRAINER_ACE_TRAINER_SAUL_PG, Route227_EventScript_Tr5_Intro, Route227_EventScript_Tr5_Defeat
	msgbox Route227_EventScript_Tr5_After, MSGBOX_AUTOCLOSE
	end

Route227_EventScript_Tr5_Intro:
	.string "Battle Zone trainers train hard!$"

Route227_EventScript_Tr5_Defeat:
	.string "Down...$"

Route227_EventScript_Tr5_After:
	.string "Keep pushing toward Stark Mountain.$"

Route227_EventScript_Tr6::
	trainerbattle_single TRAINER_RANGER_FELICIA_PG, Route227_EventScript_Tr6_Intro, Route227_EventScript_Tr6_Defeat
	msgbox Route227_EventScript_Tr6_After, MSGBOX_AUTOCLOSE
	end

Route227_EventScript_Tr6_Intro:
	.string "Battle Zone trainers train hard!$"

Route227_EventScript_Tr6_Defeat:
	.string "Down...$"

Route227_EventScript_Tr6_After:
	.string "Keep pushing toward Stark Mountain.$"

Route227_EventScript_Tr7::
	trainerbattle_single TRAINER_BLACK_BELT_GRIFFIN_PG, Route227_EventScript_Tr7_Intro, Route227_EventScript_Tr7_Defeat
	msgbox Route227_EventScript_Tr7_After, MSGBOX_AUTOCLOSE
	end

Route227_EventScript_Tr7_Intro:
	.string "Battle Zone trainers train hard!$"

Route227_EventScript_Tr7_Defeat:
	.string "Down...$"

Route227_EventScript_Tr7_After:
	.string "Keep pushing toward Stark Mountain.$"

Route227_EventScript_Tr8::
	trainerbattle_single TRAINER_ACE_TRAINER_MIKAYLA_PG, Route227_EventScript_Tr8_Intro, Route227_EventScript_Tr8_Defeat
	msgbox Route227_EventScript_Tr8_After, MSGBOX_AUTOCLOSE
	end

Route227_EventScript_Tr8_Intro:
	.string "Battle Zone trainers train hard!$"

Route227_EventScript_Tr8_Defeat:
	.string "Down...$"

Route227_EventScript_Tr8_After:
	.string "Keep pushing toward Stark Mountain.$"

Route227_EventScript_Npc9::
	msgbox Route227_EventScript_Npc9_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc9_Text:
	.string "The Battle Zone stretches across these routes.$"

Route227_EventScript_Npc10::
	msgbox Route227_EventScript_Npc10_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc10_Text:
	.string "The Battle Zone stretches across these routes.$"

Route227_EventScript_Npc11::
	msgbox Route227_EventScript_Npc11_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc11_Text:
	.string "The Battle Zone stretches across these routes.$"

Route227_EventScript_Npc12::
	msgbox Route227_EventScript_Npc12_Text, MSGBOX_NPC
	end

Route227_EventScript_Npc12_Text:
	.string "The Battle Zone stretches across these routes.$"


Route227_EventScript_StarkClosed::
	lock
	faceplayer
	msgbox Route227_Text_StarkClosed, MSGBOX_DEFAULT
	release
	end

Route227_Text_StarkClosed:
	.string "Stark Mountain opens in the next build.\n"
	.string "Ashfall already marks the path.$"
