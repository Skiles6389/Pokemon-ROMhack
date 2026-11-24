VeilstoneCity_GalacticHQ_1F_MapScripts::
	.byte 0

VeilstoneCity_GalacticHQ_1F_EventScript_GruntA::
	trainerbattle_single TRAINER_GALACTIC_HQ_GRUNT_A, VeilstoneCity_GalacticHQ_1F_Text_GruntAIntro, VeilstoneCity_GalacticHQ_1F_Text_GruntADefeat
	msgbox VeilstoneCity_GalacticHQ_1F_Text_GruntAAfter, MSGBOX_AUTOCLOSE
	end

VeilstoneCity_GalacticHQ_1F_EventScript_GruntB::
	trainerbattle_single TRAINER_GALACTIC_HQ_GRUNT_B, VeilstoneCity_GalacticHQ_1F_Text_GruntBIntro, VeilstoneCity_GalacticHQ_1F_Text_GruntBDefeat
	msgbox VeilstoneCity_GalacticHQ_1F_Text_GruntBAfter, MSGBOX_AUTOCLOSE
	end

VeilstoneCity_GalacticHQ_1F_EventScript_Mars::
	trainerbattle_single TRAINER_COMMANDER_MARS_HQ, VeilstoneCity_GalacticHQ_1F_Text_MarsIntro, VeilstoneCity_GalacticHQ_1F_Text_MarsDefeat
	msgbox VeilstoneCity_GalacticHQ_1F_Text_MarsAfter, MSGBOX_AUTOCLOSE
	end

VeilstoneCity_GalacticHQ_1F_Text_GruntAIntro:
	.string "Headquarters security!\n"
	.string "No tourists allowed!$"

VeilstoneCity_GalacticHQ_1F_Text_GruntADefeat:
	.string "Cleared...$"

VeilstoneCity_GalacticHQ_1F_Text_GruntAAfter:
	.string "The boss waits upstairs.$"

VeilstoneCity_GalacticHQ_1F_Text_GruntBIntro:
	.string "You again?!\n"
	.string "This ends here!$"

VeilstoneCity_GalacticHQ_1F_Text_GruntBDefeat:
	.string "Not again...$"

VeilstoneCity_GalacticHQ_1F_Text_GruntBAfter:
	.string "Mars is covering the stairs.$"

VeilstoneCity_GalacticHQ_1F_Text_MarsIntro:
	.string "MARS: Lakes were only the opening act.\n"
	.string "Cyrus rewrites the world above!$"

VeilstoneCity_GalacticHQ_1F_Text_MarsDefeat:
	.string "How...$"

VeilstoneCity_GalacticHQ_1F_Text_MarsAfter:
	.string "Climb if you dare.\n"
	.string "Spear Pillar is already chosen.$"

