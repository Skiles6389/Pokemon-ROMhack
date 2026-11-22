JubilifeCity_TrainersSchool_MapScripts::
	.byte 0

JubilifeCity_TrainersSchool_EventScript_Teacher::
	msgbox JubilifeCity_TrainersSchool_Text_Teacher, MSGBOX_NPC
	end

JubilifeCity_TrainersSchool_EventScript_Carter::
	trainerbattle_single TRAINER_SCHOOL_KID_CARTER, JubilifeCity_TrainersSchool_Text_CarterIntro, JubilifeCity_TrainersSchool_Text_CarterDefeat
	msgbox JubilifeCity_TrainersSchool_Text_CarterAfter, MSGBOX_AUTOCLOSE
	end

JubilifeCity_TrainersSchool_EventScript_Girl::
	msgbox JubilifeCity_TrainersSchool_Text_Girl, MSGBOX_NPC
	end

JubilifeCity_TrainersSchool_EventScript_Boy::
	msgbox JubilifeCity_TrainersSchool_Text_Boy, MSGBOX_NPC
	end

JubilifeCity_TrainersSchool_EventScript_Board::
	msgbox JubilifeCity_TrainersSchool_Text_Board, MSGBOX_SIGN
	end

JubilifeCity_TrainersSchool_Text_Teacher:
	.string "Types matter, and so does status.\p"
	.string "Water puts out Fire. Fire burns\n"
	.string "Grass. Grass drinks up Water.\p"
	.string "Sleep, poison, and paralysis do\n"
	.string "their work even when you miss.$"

JubilifeCity_TrainersSchool_Text_CarterIntro:
	.string "The lesson sticks better if you\n"
	.string "try it. My STARLY is ready.$"

JubilifeCity_TrainersSchool_Text_CarterDefeat:
	.string "I felt that type chart.$"

JubilifeCity_TrainersSchool_Text_CarterAfter:
	.string "A practice battle still counts.\n"
	.string "Ask the teacher if you forget.$"

JubilifeCity_TrainersSchool_Text_Girl:
	.string "A POTION is for hit points.\n"
	.string "An ANTIDOTE is only for poison.$"

JubilifeCity_TrainersSchool_Text_Boy:
	.string "The board has the chart. I still\n"
	.string "mix up which one burns which.$"

JubilifeCity_TrainersSchool_Text_Board:
	.string "Water beats Fire.\n"
	.string "Fire beats Grass.\l"
	.string "Grass beats Water.$"
