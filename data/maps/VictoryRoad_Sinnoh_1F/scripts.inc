VictoryRoad_Sinnoh_1F_MapScripts::
	.byte 0

VictoryRoad_Sinnoh_1F_EventScript_Npc0::
	finditem ITEM_ULTRA_BALL
	end

VictoryRoad_Sinnoh_1F_EventScript_Npc1::
	finditem ITEM_ULTRA_BALL
	end

VictoryRoad_Sinnoh_1F_EventScript_Npc2::
	finditem ITEM_ULTRA_BALL
	end

VictoryRoad_Sinnoh_1F_EventScript_Npc3::
	finditem ITEM_ULTRA_BALL
	end

VictoryRoad_Sinnoh_1F_EventScript_Npc4::
	finditem ITEM_ULTRA_BALL
	end

VictoryRoad_Sinnoh_1F_EventScript_Tr5::
	trainerbattle_single TRAINER_PSYCHIC_BRYCE, VictoryRoad_Sinnoh_1F_EventScript_Tr5_Intro, VictoryRoad_Sinnoh_1F_EventScript_Tr5_Defeat
	msgbox VictoryRoad_Sinnoh_1F_EventScript_Tr5_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_1F_EventScript_Tr5_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_1F_EventScript_Tr5_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr5_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr6::
	trainerbattle_single TRAINER_BLACK_BELT_MILES, VictoryRoad_Sinnoh_1F_EventScript_Tr6_Intro, VictoryRoad_Sinnoh_1F_EventScript_Tr6_Defeat
	msgbox VictoryRoad_Sinnoh_1F_EventScript_Tr6_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_1F_EventScript_Tr6_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_1F_EventScript_Tr6_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr6_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr7::
	trainerbattle_single TRAINER_BIRD_KEEPER_HANA, VictoryRoad_Sinnoh_1F_EventScript_Tr7_Intro, VictoryRoad_Sinnoh_1F_EventScript_Tr7_Defeat
	msgbox VictoryRoad_Sinnoh_1F_EventScript_Tr7_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_1F_EventScript_Tr7_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_1F_EventScript_Tr7_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr7_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr8::
	trainerbattle_single TRAINER_ACE_TRAINER_MARIAH, VictoryRoad_Sinnoh_1F_EventScript_Tr8_Intro, VictoryRoad_Sinnoh_1F_EventScript_Tr8_Defeat
	msgbox VictoryRoad_Sinnoh_1F_EventScript_Tr8_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_1F_EventScript_Tr8_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_1F_EventScript_Tr8_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr8_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr9::
	trainerbattle_single TRAINER_VETERAN_EDGAR, VictoryRoad_Sinnoh_1F_EventScript_Tr9_Intro, VictoryRoad_Sinnoh_1F_EventScript_Tr9_Defeat
	msgbox VictoryRoad_Sinnoh_1F_EventScript_Tr9_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_1F_EventScript_Tr9_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_1F_EventScript_Tr9_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr9_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr10::
	trainerbattle_single TRAINER_DRAGON_TAMER_CLINTON, VictoryRoad_Sinnoh_1F_EventScript_Tr10_Intro, VictoryRoad_Sinnoh_1F_EventScript_Tr10_Defeat
	msgbox VictoryRoad_Sinnoh_1F_EventScript_Tr10_After, MSGBOX_AUTOCLOSE
	end

VictoryRoad_Sinnoh_1F_EventScript_Tr10_Intro:
	.string "Show me your League spirit!$"

VictoryRoad_Sinnoh_1F_EventScript_Tr10_Defeat:
	.string "Crushed.$"

VictoryRoad_Sinnoh_1F_EventScript_Tr10_After:
	.string "The door of the League is close.$"

VictoryRoad_Sinnoh_1F_EventScript_Npc11::
	msgbox VictoryRoad_Sinnoh_1F_EventScript_Npc11_Text, MSGBOX_NPC
	end

VictoryRoad_Sinnoh_1F_EventScript_Npc11_Text:
	.string "Victory Road winds toward the League.$"

