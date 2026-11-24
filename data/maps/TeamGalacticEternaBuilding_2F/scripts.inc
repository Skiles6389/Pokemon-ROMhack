TeamGalacticEternaBuilding_2F_MapScripts::
	.byte 0

TeamGalacticEternaBuilding_2F_EventScript_Grunt1::
	trainerbattle_single TRAINER_GALACTIC_GRUNT_ETERNA_2F_1, TeamGalacticEternaBuilding_2F_Text_Grunt1Intro, TeamGalacticEternaBuilding_2F_Text_Grunt1Defeat
	msgbox TeamGalacticEternaBuilding_2F_Text_Grunt1After, MSGBOX_AUTOCLOSE
	end

TeamGalacticEternaBuilding_2F_EventScript_Grunt2::
	trainerbattle_single TRAINER_GALACTIC_GRUNT_ETERNA_2F_2, TeamGalacticEternaBuilding_2F_Text_Grunt2Intro, TeamGalacticEternaBuilding_2F_Text_Grunt2Defeat
	msgbox TeamGalacticEternaBuilding_2F_Text_Grunt2After, MSGBOX_AUTOCLOSE
	end

TeamGalacticEternaBuilding_2F_Text_Grunt1Intro:
	.string "Stay off our turf!$"

TeamGalacticEternaBuilding_2F_Text_Grunt1Defeat:
	.string "Not again...$"

TeamGalacticEternaBuilding_2F_Text_Grunt1After:
	.string "The boss works upstairs!$"

TeamGalacticEternaBuilding_2F_Text_Grunt2Intro:
	.string "You won't reach Jupiter!$"

TeamGalacticEternaBuilding_2F_Text_Grunt2Defeat:
	.string "She'll crush you!$"

TeamGalacticEternaBuilding_2F_Text_Grunt2After:
	.string "Commander Jupiter is ruthless!$"
