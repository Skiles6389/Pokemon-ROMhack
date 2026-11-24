VeilstoneCity_GalacticHQ_2F_MapScripts::
	.byte 0

VeilstoneCity_GalacticHQ_2F_EventScript_Grunt::
	trainerbattle_single TRAINER_GALACTIC_HQ_GRUNT_C, VeilstoneCity_GalacticHQ_2F_Text_Intro, VeilstoneCity_GalacticHQ_2F_Text_Defeat
	msgbox VeilstoneCity_GalacticHQ_2F_Text_After, MSGBOX_AUTOCLOSE
	end

VeilstoneCity_GalacticHQ_2F_Text_Intro:
	.string "Cyrus is finishing the sequence!\n"
	.string "You will not interrupt!$"

VeilstoneCity_GalacticHQ_2F_Text_Defeat:
	.string "Broken...$"

VeilstoneCity_GalacticHQ_2F_Text_After:
	.string "His room is just ahead.$"
