TeamGalacticEternaBuilding_1F_MapScripts::
	.byte 0

TeamGalacticEternaBuilding_1F_EventScript_Grunt1::
	trainerbattle_single TRAINER_GALACTIC_GRUNT_ETERNA_1F_1, TeamGalacticEternaBuilding_1F_Text_Grunt1Intro, TeamGalacticEternaBuilding_1F_Text_Grunt1Defeat
	msgbox TeamGalacticEternaBuilding_1F_Text_Grunt1After, MSGBOX_AUTOCLOSE
	end

TeamGalacticEternaBuilding_1F_EventScript_Grunt2::
	trainerbattle_single TRAINER_GALACTIC_GRUNT_ETERNA_1F_2, TeamGalacticEternaBuilding_1F_Text_Grunt2Intro, TeamGalacticEternaBuilding_1F_Text_Grunt2Defeat
	msgbox TeamGalacticEternaBuilding_1F_Text_Grunt2After, MSGBOX_AUTOCLOSE
	end

TeamGalacticEternaBuilding_1F_Text_Grunt1Intro:
	.string "Intruder on 1F!$"

TeamGalacticEternaBuilding_1F_Text_Grunt1Defeat:
	.string "Warn the Commander...$"

TeamGalacticEternaBuilding_1F_Text_Grunt1After:
	.string "Jupiter's on the top floor!$"

TeamGalacticEternaBuilding_1F_Text_Grunt2Intro:
	.string "Team Galactic doesn't welcome guests!$"

TeamGalacticEternaBuilding_1F_Text_Grunt2Defeat:
	.string "Ugh!$"

TeamGalacticEternaBuilding_1F_Text_Grunt2After:
	.string "We're stealing Pokémon energy for\n"
	.string "something bigger than you!$"
