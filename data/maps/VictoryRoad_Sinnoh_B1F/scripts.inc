VictoryRoad_Sinnoh_B1F_MapScripts::
	.byte 0

VictoryRoad_Sinnoh_B1F_EventScript_Npc0::
	finditem ITEM_ULTRA_BALL
	end

VictoryRoad_Sinnoh_B1F_EventScript_Tr1::
	trainerbattle_single TRAINER_DOUBLE_TEAM_JO_AND_PAT, VictoryRoad_Sinnoh_B1F_EventScript_Tr1_Intro, VictoryRoad_Sinnoh_B1F_EventScript_Tr1_Defeat
	msgbox VictoryRoad_Sinnoh_B1F_EventScript_Tr1_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_B1F_EventScript_Tr1_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr1_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr1_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr2::
	trainerbattle_single TRAINER_DOUBLE_TEAM_JO_AND_PAT, VictoryRoad_Sinnoh_B1F_EventScript_Tr2_Intro, VictoryRoad_Sinnoh_B1F_EventScript_Tr2_Defeat
	msgbox VictoryRoad_Sinnoh_B1F_EventScript_Tr2_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_B1F_EventScript_Tr2_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr2_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr2_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr3::
	trainerbattle_single TRAINER_DRAGON_TAMER_ONDREJ, VictoryRoad_Sinnoh_B1F_EventScript_Tr3_Intro, VictoryRoad_Sinnoh_B1F_EventScript_Tr3_Defeat
	msgbox VictoryRoad_Sinnoh_B1F_EventScript_Tr3_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_B1F_EventScript_Tr3_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr3_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr3_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr4::
	trainerbattle_single TRAINER_PSYCHIC_VALENCIA, VictoryRoad_Sinnoh_B1F_EventScript_Tr4_Intro, VictoryRoad_Sinnoh_B1F_EventScript_Tr4_Defeat
	msgbox VictoryRoad_Sinnoh_B1F_EventScript_Tr4_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_B1F_EventScript_Tr4_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr4_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr4_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr5::
	trainerbattle_single TRAINER_ACE_TRAINER_HENRY, VictoryRoad_Sinnoh_B1F_EventScript_Tr5_Intro, VictoryRoad_Sinnoh_B1F_EventScript_Tr5_Defeat
	msgbox VictoryRoad_Sinnoh_B1F_EventScript_Tr5_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_B1F_EventScript_Tr5_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr5_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_B1F_EventScript_Tr5_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_B1F_EventScript_Npc6::
	finditem ITEM_ULTRA_BALL
	end

VictoryRoad_Sinnoh_B1F_EventScript_Npc7::
	finditem ITEM_ULTRA_BALL
	end

