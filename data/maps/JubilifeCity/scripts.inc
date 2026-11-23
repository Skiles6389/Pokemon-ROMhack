JubilifeCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, JubilifeCity_OnTransition
	.byte 0

JubilifeCity_OnTransition:
	call SandgemTown_EventScript_SetAssistantGfx
	end

JubilifeCity_EventScript_Galactic::
	lockall
	call SandgemTown_EventScript_SetAssistantGfx
	applymovement LOCALID_JUBILIFE_GRUNT, Common_Movement_FacePlayer
	applymovement LOCALID_JUBILIFE_GRUNT_2, Common_Movement_FacePlayer
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, JubilifeCity_EventScript_LucasIntro
	msgbox JubilifeCity_Text_DawnIntro, MSGBOX_DEFAULT
	goto JubilifeCity_EventScript_GruntBattle
	end

JubilifeCity_EventScript_LucasIntro::
	msgbox JubilifeCity_Text_LucasIntro, MSGBOX_DEFAULT
	goto JubilifeCity_EventScript_GruntBattle
	end

JubilifeCity_EventScript_GruntBattle::
	msgbox JubilifeCity_Text_GruntChallenge, MSGBOX_DEFAULT
	special HealPlayerParty
	trainerbattle LOCALID_JUBILIFE_GRUNT, TRAINER_GALACTIC_GRUNT_JUBILIFE, JubilifeCity_Text_GruntIntro, JubilifeCity_Text_GruntDefeat, JubilifeCity_EventScript_AfterGrunt, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

JubilifeCity_EventScript_AfterGrunt::
	msgbox JubilifeCity_Text_GruntsLeave, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_JUBILIFE_GRUNT, JubilifeCity_Movement_GruntLeave
	applymovement LOCALID_JUBILIFE_GRUNT_2, JubilifeCity_Movement_Grunt2Leave
	waitmovement 0
	removeobject LOCALID_JUBILIFE_GRUNT
	removeobject LOCALID_JUBILIFE_GRUNT_2
	setflag FLAG_HIDE_JUBILIFE_GRUNTS
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, JubilifeCity_EventScript_LucasThanks
	msgbox JubilifeCity_Text_DawnThanks, MSGBOX_DEFAULT
	goto JubilifeCity_EventScript_AssistantLeaves
	end

JubilifeCity_EventScript_LucasThanks::
	msgbox JubilifeCity_Text_LucasThanks, MSGBOX_DEFAULT
	goto JubilifeCity_EventScript_AssistantLeaves
	end

JubilifeCity_EventScript_AssistantLeaves::
	closemessage
	applymovement LOCALID_JUBILIFE_ASSISTANT, JubilifeCity_Movement_AssistantLeave
	waitmovement 0
	removeobject LOCALID_JUBILIFE_ASSISTANT
	setflag FLAG_HIDE_JUBILIFE_ASSISTANT
	clearflag FLAG_HIDE_JUBILIFE_BARRY
	addobject LOCALID_JUBILIFE_BARRY
	applymovement LOCALID_JUBILIFE_BARRY, JubilifeCity_Movement_BarryIn
	waitmovement 0
	applymovement LOCALID_JUBILIFE_BARRY, Common_Movement_FacePlayer
	waitmovement 0
	msgbox JubilifeCity_Text_Barry, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_JUBILIFE_BARRY, JubilifeCity_Movement_BarryLeave
	waitmovement 0
	removeobject LOCALID_JUBILIFE_BARRY
	setflag FLAG_HIDE_JUBILIFE_BARRY
	setvar VAR_JUBILIFE_STATE, 2
	releaseall
	end

JubilifeCity_EventScript_Assistant::
	lock
	faceplayer
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, JubilifeCity_EventScript_LucasWait
	msgbox JubilifeCity_Text_DawnWait, MSGBOX_DEFAULT
	release
	end

JubilifeCity_EventScript_LucasWait::
	msgbox JubilifeCity_Text_LucasWait, MSGBOX_DEFAULT
	release
	end

JubilifeCity_EventScript_Grunt::
	msgbox JubilifeCity_Text_GruntWait, MSGBOX_NPC
	end

JubilifeCity_EventScript_BarryLater::
	msgbox JubilifeCity_Text_BarryLater, MSGBOX_NPC
	end

JubilifeCity_EventScript_Poketch::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_POKETCH, JubilifeCity_EventScript_PoketchDone
	msgbox JubilifeCity_Text_PoketchIntro, MSGBOX_DEFAULT
	playfanfare MUS_OBTAIN_ITEM
	message JubilifeCity_Text_ReceivedPoketch
	waitmessage
	waitfanfare
	setflag FLAG_RECEIVED_POKETCH
	msgbox JubilifeCity_Text_PoketchApps, MSGBOX_DEFAULT
	release
	end

JubilifeCity_EventScript_PoketchDone::
	msgbox JubilifeCity_Text_PoketchDone, MSGBOX_DEFAULT
	release
	end

JubilifeCity_EventScript_Woman::
	msgbox JubilifeCity_Text_Woman, MSGBOX_NPC
	end

JubilifeCity_EventScript_Boy::
	msgbox JubilifeCity_Text_Boy, MSGBOX_NPC
	end

JubilifeCity_EventScript_CitySign::
	msgbox JubilifeCity_Text_CitySign, MSGBOX_SIGN
	end

JubilifeCity_EventScript_Route203Sign::
	msgbox JubilifeCity_Text_Route203Sign, MSGBOX_SIGN
	end

JubilifeCity_EventScript_Route218Sign::
	msgbox JubilifeCity_Text_Route218Sign, MSGBOX_SIGN
	end

JubilifeCity_EventScript_TvSign::
	msgbox JubilifeCity_Text_TvSign, MSGBOX_SIGN
	end

JubilifeCity_EventScript_LockedHouse::
	msgbox JubilifeCity_Text_LockedHouse, MSGBOX_SIGN
	end

JubilifeCity_Movement_GruntLeave:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

JubilifeCity_Movement_Grunt2Leave:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

JubilifeCity_Movement_AssistantLeave:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

JubilifeCity_Movement_BarryIn:
	walk_fast_right
	walk_fast_right
	step_end

JubilifeCity_Movement_BarryLeave:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_up
	step_end

JubilifeCity_Text_DawnIntro:
	.string "GRUNT: The lake notes. Now.\p"
	.string "DAWN: They belong to the professor.\n"
	.string "I am not handing them over.\p"
	.string "DAWN: {PLAYER}! These two stopped\n"
	.string "me on the way into the city.$"

JubilifeCity_Text_LucasIntro:
	.string "GRUNT: The lake notes. Now.\p"
	.string "LUCAS: They belong to the professor.\n"
	.string "I am not handing them over.\p"
	.string "LUCAS: {PLAYER}! These two stopped\n"
	.string "me on the way into the city.$"

JubilifeCity_Text_GruntChallenge:
	.string "GRUNT: Then the kid with a POKéMON\n"
	.string "can talk to my ZUBAT.$"

JubilifeCity_Text_GruntIntro:
	.string "GALACTIC takes what it asks for.$"

JubilifeCity_Text_GruntDefeat:
	.string "A ZUBAT wasn't enough?$"

JubilifeCity_Text_GruntsLeave:
	.string "GRUNT: Remember the uniform.\n"
	.string "We don't forget a face.$"

JubilifeCity_Text_DawnThanks:
	.string "DAWN: Thank you. They wanted the\n"
	.string "notes from LAKE VERITY.\p"
	.string "The TRAINERS' SCHOOL is on the\n"
	.string "east side, if you want a lesson.\p"
	.string "I'll take the notes back to the lab.$"

JubilifeCity_Text_LucasThanks:
	.string "LUCAS: Thank you. They wanted the\n"
	.string "notes from LAKE VERITY.\p"
	.string "The TRAINERS' SCHOOL is on the\n"
	.string "east side, if you want a lesson.\p"
	.string "I'll take the notes back to the lab.$"

JubilifeCity_Text_Barry:
	.string "BARRY: {PLAYER}! JUBILIFE!\p"
	.string "I'm cutting through the school,\n"
	.string "then heading east out of town.\p"
	.string "The east road is open. Don't you\n"
	.string "beat me to the cave!$"

JubilifeCity_Text_DawnWait:
	.string "DAWN: Stay close. They won't\n"
	.string "listen to me alone.$"

JubilifeCity_Text_LucasWait:
	.string "LUCAS: Stay close. They won't\n"
	.string "listen to me alone.$"

JubilifeCity_Text_GruntWait:
	.string "This doesn't concern you.\n"
	.string "Keep walking.$"

JubilifeCity_Text_BarryLater:
	.string "BARRY: East. As soon as the\n"
	.string "road opens.$"

JubilifeCity_Text_PoketchIntro:
	.string "The costume is the campaign.\n"
	.string "Every new TRAINER gets a POKéTCH.$"

JubilifeCity_Text_ReceivedPoketch:
	.string "{PLAYER} received the POKéTCH.$"

JubilifeCity_Text_PoketchApps:
	.string "The little apps are still on the\n"
	.string "workbench. Today it keeps the time.$"

JubilifeCity_Text_PoketchDone:
	.string "Come back when the apps are ready.\n"
	.string "The watch already works.$"

JubilifeCity_Text_Woman:
	.string "The Center is west. The Mart is\n"
	.string "east. The school is farther east.$"

JubilifeCity_Text_Boy:
	.string "JUBILIFE TV is locked today.\n"
	.string "The POKéTCH building is open.$"

JubilifeCity_Text_CitySign:
	.string "JUBILIFE CITY\n"
	.string "Bright, loud, and wide awake.$"

JubilifeCity_Text_Route203Sign:
	.string "EAST: ROUTE 203\n"
	.string "A grass road to the cave.$"

JubilifeCity_Text_Route218Sign:
	.string "WEST: ROUTE 218\n"
	.string "The gate is still shut.$"

JubilifeCity_Text_TvSign:
	.string "JUBILIFE TV\n"
	.string "The studio doors are locked.$"

JubilifeCity_Text_LockedHouse:
	.string "The door is locked.$"
