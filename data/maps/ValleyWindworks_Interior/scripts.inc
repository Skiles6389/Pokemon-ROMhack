ValleyWindworks_Interior_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, ValleyWindworks_Interior_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, ValleyWindworks_Interior_OnFrame
	.byte 0

ValleyWindworks_Interior_OnTransition:
	call_if_set FLAG_HIDE_WINDWORKS_INTERIOR_GALACTIC, ValleyWindworks_Interior_EventScript_SetClearedPositions
	end

ValleyWindworks_Interior_EventScript_SetClearedPositions::
	setobjectxyperm LOCALID_WINDWORKS_SCIENTIST, 12, 8
	setobjectxyperm LOCALID_WINDWORKS_DAUGHTER, 11, 8
	return

ValleyWindworks_Interior_OnFrame:
	map_script_2 VAR_TEMP_2, 0, ValleyWindworks_Interior_EventScript_EntryGruntFrame
	.2byte 0

ValleyWindworks_Interior_EventScript_EntryGruntFrame::
	setvar VAR_TEMP_2, 1
	goto_if_set FLAG_HIDE_WINDWORKS_INTERIOR_GALACTIC, ValleyWindworks_Interior_EventScript_EntryGruntFrameEnd
	goto_if_set FLAG_WINDWORKS_ENTRY_GRUNT_DONE, ValleyWindworks_Interior_EventScript_EntryGruntFrameEnd
	lockall
	playbgm MUS_PL_ENCOUNTER_GALACTIC, FALSE
	applymovement LOCALID_WINDWORKS_GRUNT1, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox ValleyWindworks_Interior_Text_EntryGruntPanic, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_WINDWORKS_GRUNT1, ValleyWindworks_Interior_Movement_Grunt1Flee
	waitmovement 0
	removeobject LOCALID_WINDWORKS_GRUNT1
	setflag FLAG_WINDWORKS_ENTRY_GRUNT_DONE
	setvar VAR_VALLEY_WINDWORKS_STATE, 1
	fadedefaultbgm
	releaseall
ValleyWindworks_Interior_EventScript_EntryGruntFrameEnd::
	end

ValleyWindworks_Interior_Movement_Grunt1Flee:
	walk_up
	walk_up
	walk_right
	walk_right
	walk_up
	step_end

ValleyWindworks_Interior_EventScript_EntryGrunt::
	msgbox ValleyWindworks_Interior_Text_EntryGruntIdle, MSGBOX_NPC
	end

ValleyWindworks_Interior_EventScript_EntryGruntTrigger::
	end

ValleyWindworks_Interior_EventScript_Grunt2::
	trainerbattle_single TRAINER_GALACTIC_GRUNT_WINDWORKS_1, ValleyWindworks_Interior_Text_Grunt2Intro, ValleyWindworks_Interior_Text_Grunt2Defeat
	msgbox ValleyWindworks_Interior_Text_Grunt2After, MSGBOX_AUTOCLOSE
	end

ValleyWindworks_Interior_EventScript_Grunt3::
	trainerbattle_single TRAINER_GALACTIC_GRUNT_WINDWORKS_2, ValleyWindworks_Interior_Text_Grunt3Intro, ValleyWindworks_Interior_Text_Grunt3Defeat
	msgbox ValleyWindworks_Interior_Text_Grunt3After, MSGBOX_AUTOCLOSE
	end

ValleyWindworks_Interior_EventScript_Mars::
	goto ValleyWindworks_Interior_EventScript_MarsBattle
	end

ValleyWindworks_Interior_EventScript_MarsTrigger::
	goto_if_set FLAG_HIDE_WINDWORKS_INTERIOR_GALACTIC, ValleyWindworks_Interior_EventScript_MarsTriggerEnd
	goto ValleyWindworks_Interior_EventScript_MarsBattle
ValleyWindworks_Interior_EventScript_MarsTriggerEnd::
	end

ValleyWindworks_Interior_EventScript_MarsBattle::
	lockall
	playbgm MUS_PL_ENCOUNTER_GALACTIC, FALSE
	applymovement LOCALID_WINDWORKS_MARS, Common_Movement_FacePlayer
	waitmovement 0
	msgbox ValleyWindworks_Interior_Text_MarsIntro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_COMMANDER_MARS, ValleyWindworks_Interior_Text_MarsDefeat
	msgbox ValleyWindworks_Interior_Text_MarsAfter, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_WINDWORKS_MARS
	removeobject LOCALID_WINDWORKS_GRUNT2
	removeobject LOCALID_WINDWORKS_GRUNT3
	setflag FLAG_HIDE_WINDWORKS_INTERIOR_GALACTIC
	setflag FLAG_HIDE_WINDWORKS_DOOR_GRUNT
	setflag FLAG_HIDE_ROUTE205_FOREST_GRUNTS
	setflag FLAG_HIDE_ROUTE205_LITTLE_GIRL
	clearflag FLAG_HIDE_WINDWORKS_DAUGHTER
	setflag FLAG_VALLEY_WINDWORKS_CLEARED
	setvar VAR_VALLEY_WINDWORKS_STATE, 2
	addobject LOCALID_WINDWORKS_DAUGHTER
	setobjectxy LOCALID_WINDWORKS_DAUGHTER, 11, 8
	setobjectxy LOCALID_WINDWORKS_SCIENTIST, 12, 8
	fadescreen FADE_FROM_BLACK
	fadedefaultbgm
	applymovement LOCALID_WINDWORKS_DAUGHTER, ValleyWindworks_Interior_Movement_DaughterRun
	waitmovement 0
	msgbox ValleyWindworks_Interior_Text_DaughterReunion, MSGBOX_DEFAULT
	msgbox ValleyWindworks_Interior_Text_ScientistThanks, MSGBOX_DEFAULT
	msgbox ValleyWindworks_Interior_Text_DaughterThanks, MSGBOX_DEFAULT
	closemessage
	releaseall
	end

ValleyWindworks_Interior_Movement_DaughterRun:
	walk_right
	walk_up
	walk_up
	walk_right
	face_right
	step_end

ValleyWindworks_Interior_EventScript_Scientist::
	goto_if_set FLAG_VALLEY_WINDWORKS_CLEARED, ValleyWindworks_Interior_EventScript_ScientistAfter
	msgbox ValleyWindworks_Interior_Text_ScientistHeld, MSGBOX_NPC
	end

ValleyWindworks_Interior_EventScript_ScientistAfter::
	msgbox ValleyWindworks_Interior_Text_ScientistAfter, MSGBOX_NPC
	end

ValleyWindworks_Interior_EventScript_Daughter::
	msgbox ValleyWindworks_Interior_Text_DaughterThanks, MSGBOX_NPC
	end

ValleyWindworks_Interior_Text_EntryGruntPanic:
	.string "GRUNT: You have the key?!\n"
	.string "Locking the door was pointless!\p"
	.string "No time to sulk-I've got to warn\n"
	.string "the Commander!$"

ValleyWindworks_Interior_Text_EntryGruntIdle:
	.string "Keep out of Team Galactic business!$"

ValleyWindworks_Interior_Text_Grunt2Intro:
	.string "This isn't a game! We're on a real job!$"

ValleyWindworks_Interior_Text_Grunt2Defeat:
	.string "A kid wrecked my assignment...$"

ValleyWindworks_Interior_Text_Grunt2After:
	.string "Team Galactic needs this electricity\n"
	.string "for something huge!$"

ValleyWindworks_Interior_Text_Grunt3Intro:
	.string "Sucking power from Valley Windworks-\n"
	.string "that's the mission. You're in the way!$"

ValleyWindworks_Interior_Text_Grunt3Defeat:
	.string "Tough kids are the worst...$"

ValleyWindworks_Interior_Text_Grunt3After:
	.string "You don't know what Galactic wants.\n"
	.string "Honestly, neither do the grunts...$"

ValleyWindworks_Interior_Text_MarsIntro:
	.string "MARS: I'm Mars-one of Team Galactic's\n"
	.string "Commanders.\p"
	.string "We're building a world better than this\n"
	.string "one. Few people understand that.\p"
	.string "You don't either, do you?\n"
	.string "Then a battle will decide what next.\p"
	.string "I win, you leave. You win, we leave.\n"
	.string "Simple enough for a child?$"

ValleyWindworks_Interior_Text_MarsDefeat:
	.string "I lost?! You uppity brat!$"

ValleyWindworks_Interior_Text_MarsAfter:
	.string "MARS: Hmph. That one got away from me.\n"
	.string "Still-the fight was fun.\p"
	.string "We've taken enough electricity.\n"
	.string "Team Galactic is done here... for now!$"

ValleyWindworks_Interior_Text_ScientistHeld:
	.string "They forced me to keep the turbines\n"
	.string "running... Please, stop them!$"

ValleyWindworks_Interior_Text_ScientistThanks:
	.string "SCIENTIST: Team Galactic wanted POKéMON\n"
	.string "and energy for some “new universe.”\p"
	.string "None of it made sense. Thank you for\n"
	.string "saving me-I can see my daughter again!$"

ValleyWindworks_Interior_Text_DaughterReunion:
	.string "GIRL: Papa!\n"
	.string "You're all dusty-go wash up!$"

ValleyWindworks_Interior_Text_DaughterThanks:
	.string "GIRL: Thank you, Trainer!\n"
	.string "You chased the bad people away!$"

ValleyWindworks_Interior_Text_ScientistAfter:
	.string "These turbines catch canyon winds.\n"
	.string "Nature's power is wonderful-when it\l"
	.string "isn't stolen.$"
