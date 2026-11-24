TeamGalacticEternaBuilding_3F_MapScripts::
	.byte 0

TeamGalacticEternaBuilding_3F_EventScript_Travon::
	trainerbattle_single TRAINER_SCIENTIST_TRAVON, TeamGalacticEternaBuilding_3F_Text_TravonIntro, TeamGalacticEternaBuilding_3F_Text_TravonDefeat
	msgbox TeamGalacticEternaBuilding_3F_Text_TravonAfter, MSGBOX_AUTOCLOSE
	end

TeamGalacticEternaBuilding_3F_EventScript_Grunt::
	trainerbattle_single TRAINER_GALACTIC_GRUNT_ETERNA_3F, TeamGalacticEternaBuilding_3F_Text_GruntIntro, TeamGalacticEternaBuilding_3F_Text_GruntDefeat
	msgbox TeamGalacticEternaBuilding_3F_Text_GruntAfter, MSGBOX_AUTOCLOSE
	end

TeamGalacticEternaBuilding_3F_Text_TravonIntro:
	.string "My data says you'll lose here!$"

TeamGalacticEternaBuilding_3F_Text_TravonDefeat:
	.string "Error... unexpected outcome...$"

TeamGalacticEternaBuilding_3F_Text_TravonAfter:
	.string "Jupiter uses energy from kidnapped\n"
	.string "Pokémon upstairs!$"

TeamGalacticEternaBuilding_3F_Text_GruntIntro:
	.string "Science and muscle combo!$"

TeamGalacticEternaBuilding_3F_Text_GruntDefeat:
	.string "Experiment failed!$"

TeamGalacticEternaBuilding_3F_Text_GruntAfter:
	.string "Hurry up--finish this kid!$"
