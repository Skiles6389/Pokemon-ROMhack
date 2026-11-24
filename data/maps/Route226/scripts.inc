Route226_MapScripts::
	.byte 0

Route226_EventScript_Npc0::
	msgbox Route226_EventScript_Npc0_Text, MSGBOX_NPC
	end

Route226_EventScript_Npc0_Text:
	.string "The Battle Zone stretches across these routes.$"

Route226_EventScript_Tr1::
	trainerbattle_single TRAINER_SWIMMER_LYDIA_PG, Route226_EventScript_Tr1_Intro, Route226_EventScript_Tr1_Defeat
	msgbox Route226_EventScript_Tr1_After, MSGBOX_AUTOCLOSE
	end

Route226_EventScript_Tr1_Intro:
	.string "Battle Zone trainers train hard!$"

Route226_EventScript_Tr1_Defeat:
	.string "Down...$"

Route226_EventScript_Tr1_After:
	.string "Keep pushing toward Stark Mountain.$"

Route226_EventScript_Npc2::
	msgbox Route226_EventScript_Npc2_Text, MSGBOX_NPC
	end

Route226_EventScript_Npc2_Text:
	.string "The Battle Zone stretches across these routes.$"

Route226_EventScript_Tr3::
	trainerbattle_single TRAINER_BIRD_KEEPER_GENEVA_PG, Route226_EventScript_Tr3_Intro, Route226_EventScript_Tr3_Defeat
	msgbox Route226_EventScript_Tr3_After, MSGBOX_AUTOCLOSE
	end

Route226_EventScript_Tr3_Intro:
	.string "Battle Zone trainers train hard!$"

Route226_EventScript_Tr3_Defeat:
	.string "Down...$"

Route226_EventScript_Tr3_After:
	.string "Keep pushing toward Stark Mountain.$"

Route226_EventScript_Tr4::
	trainerbattle_single TRAINER_DRAGON_TAMER_STANLEY_PG, Route226_EventScript_Tr4_Intro, Route226_EventScript_Tr4_Defeat
	msgbox Route226_EventScript_Tr4_After, MSGBOX_AUTOCLOSE
	end

Route226_EventScript_Tr4_Intro:
	.string "Battle Zone trainers train hard!$"

Route226_EventScript_Tr4_Defeat:
	.string "Down...$"

Route226_EventScript_Tr4_After:
	.string "Keep pushing toward Stark Mountain.$"

Route226_EventScript_Npc5::
	msgbox Route226_EventScript_Npc5_Text, MSGBOX_NPC
	end

Route226_EventScript_Npc5_Text:
	.string "The Battle Zone stretches across these routes.$"

Route226_EventScript_Tr6::
	trainerbattle_single TRAINER_SWIMMER_WADE_PG, Route226_EventScript_Tr6_Intro, Route226_EventScript_Tr6_Defeat
	msgbox Route226_EventScript_Tr6_After, MSGBOX_AUTOCLOSE
	end

Route226_EventScript_Tr6_Intro:
	.string "Battle Zone trainers train hard!$"

Route226_EventScript_Tr6_Defeat:
	.string "Down...$"

Route226_EventScript_Tr6_After:
	.string "Keep pushing toward Stark Mountain.$"

