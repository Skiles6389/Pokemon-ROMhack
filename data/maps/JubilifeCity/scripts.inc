JubilifeCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, JubilifeCity_OnTransition
	.byte 0

JubilifeCity_OnTransition:
	setflag FLAG_VISITED_JUBILIFE_CITY
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
	waitmovement 0
	removeobject LOCALID_JUBILIFE_GRUNT
	applymovement LOCALID_JUBILIFE_GRUNT_2, JubilifeCity_Movement_Grunt2Leave
	waitmovement 0
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

JubilifeCity_Movement_GruntLeave:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

JubilifeCity_Movement_Grunt2Leave:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

JubilifeCity_Movement_AssistantLeave:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

JubilifeCity_Movement_BarryIn:
	walk_fast_up
	walk_fast_up
	step_end

JubilifeCity_Movement_BarryLeave:
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
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
	.string "ROUTE 203 is wide open now, so\n"
	.string "don't you fall behind!$"

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
	.string "BARRY: East to ROUTE 203.\n"
	.string "Hurry up!$"

JubilifeCity_Text_PoketchIntro:
	.string "A useful gadget for the road.\n"
	.string "Every new TRAINER gets a POKéTCH.$"

JubilifeCity_Text_ReceivedPoketch:
	.string "{PLAYER} received the POKéTCH.$"

JubilifeCity_Text_PoketchApps:
	.string "Open it from the START menu. It has\n"
	.string "a clock and a PARTY checker so far.$"

JubilifeCity_Text_PoketchDone:
	.string "More apps are on the workbench.\n"
	.string "Enjoy the clock for now!$"



JubilifeCity_Text_CitySign:
	.string "JUBILIFE CITY\n"
	.string "Bright, loud, and wide awake.$"

JubilifeCity_Text_Route203Sign:
	.string "EAST: ROUTE 203\n"
	.string "The road toward OREBURGH.$"

JubilifeCity_Text_Route218Sign:
	.string "WEST: ROUTE 218\n"
	.string "The shore waits beyond the gate.$"

JubilifeCity_Text_TvSign:
	.string "JUBILIFE TV\n"
	.string "New ideas are always on the air.$"

JubilifeCity_EventScript_NorthSign::
	msgbox JubilifeCity_EventScript_NorthSign_Text, MSGBOX_SIGN
	end

JubilifeCity_EventScript_NorthSign_Text:
	.string "NORTH: ROUTE 204\n"
	.string "Leave room for returning travelers.$"

JubilifeCity_EventScript_PoketchSign::
	msgbox JubilifeCity_EventScript_PoketchSign_Text, MSGBOX_SIGN
	end

JubilifeCity_EventScript_PoketchSign_Text:
	.string "POKéTCH COMPANY\n"
	.string "Time for another bright idea.$"

JubilifeCity_EventScript_CondoSign::
	msgbox JubilifeCity_EventScript_CondoSign_Text, MSGBOX_SIGN
	end

JubilifeCity_EventScript_CondoSign_Text:
	.string "JUBILIFE RESIDENCES\n"
	.string "A home above the busy streets.$"

JubilifeCity_EventScript_SchoolSign::
	msgbox JubilifeCity_EventScript_SchoolSign_Text, MSGBOX_SIGN
	end

JubilifeCity_EventScript_SchoolSign_Text:
	.string "TRAINERS' SCHOOL\n"
	.string "Try a lesson before the long road.$"

JubilifeCity_EventScript_GtsSign::
	msgbox JubilifeCity_EventScript_GtsSign_Text, MSGBOX_SIGN
	end

JubilifeCity_EventScript_GtsSign_Text:
	.string "GLOBAL TERMINAL\n"
	.string "Every journey starts somewhere.$"

JubilifeCity_EventScript_AceTrainerF::
	msgbox JubilifeCity_EventScript_AceTrainerF_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_AceTrainerF_Text:
	.string "I take the side streets.\n"
	.string "There is always something to notice.$"

JubilifeCity_EventScript_AceTrainerM1::
	msgbox JubilifeCity_EventScript_AceTrainerM1_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_AceTrainerM1_Text:
	.string "A busy city makes a fine place\n"
	.string "to practice keeping your focus.$"

JubilifeCity_EventScript_SchoolKid1::
	msgbox JubilifeCity_EventScript_SchoolKid1_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_SchoolKid1_Text:
	.string "I sketch the streets in my notebook.\n"
	.string "It helps me find my way home.$"

JubilifeCity_EventScript_Twin::
	msgbox JubilifeCity_EventScript_Twin_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Twin_Text:
	.string "These flower beds are my favorites.\n"
	.string "I stop here on the way to school.$"

JubilifeCity_EventScript_Expert1::
	msgbox JubilifeCity_EventScript_Expert1_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Expert1_Text:
	.string "The city grew around these roads.\n"
	.string "Some footsteps are older than mine.$"

JubilifeCity_EventScript_SchoolKid2::
	msgbox JubilifeCity_EventScript_SchoolKid2_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_SchoolKid2_Text:
	.string "One more lap before class!\n"
	.string "Walking helps me remember lessons.$"

JubilifeCity_EventScript_Expert2::
	msgbox JubilifeCity_EventScript_Expert2_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Expert2_Text:
	.string "My team enjoys the city lights.\n"
	.string "I prefer the quiet early hours.$"

JubilifeCity_EventScript_AceTrainerM2::
	msgbox JubilifeCity_EventScript_AceTrainerM2_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_AceTrainerM2_Text:
	.string "North, south, east, west...\n"
	.string "Each road asks a different question.$"

JubilifeCity_EventScript_AceTrainerM3::
	msgbox JubilifeCity_EventScript_AceTrainerM3_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_AceTrainerM3_Text:
	.string "I rest here before heading out.\n"
	.string "A calm start makes a good journey.$"

JubilifeCity_EventScript_Clown1::
	msgbox JubilifeCity_EventScript_Clown1_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Clown1_Text:
	.string "A wristwatch and a bright idea!\n"
	.string "That is my whole sales pitch.$"

JubilifeCity_EventScript_Clown2::
	msgbox JubilifeCity_EventScript_Clown2_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Clown2_Text:
	.string "I practice my jokes between crowds.\n"
	.string "The lamp never laughs.$"

JubilifeCity_EventScript_Clown3::
	msgbox JubilifeCity_EventScript_Clown3_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Clown3_Text:
	.string "My shoes squeak louder than traffic.\n"
	.string "That is useful in a big city.$"

JubilifeCity_EventScript_GameKid1::
	msgbox JubilifeCity_EventScript_GameKid1_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_GameKid1_Text:
	.string "We are comparing our team notes.\n"
	.string "My friend always spots what I miss.$"

JubilifeCity_EventScript_GameKid2::
	msgbox JubilifeCity_EventScript_GameKid2_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_GameKid2_Text:
	.string "We trade ideas before we travel.\n"
	.string "Two notebooks beat one.$"

JubilifeCity_EventScript_Collector::
	msgbox JubilifeCity_EventScript_Collector_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Collector_Text:
	.string "I save little souvenirs from trips.\n"
	.string "A pebble can hold a big memory.$"

JubilifeCity_EventScript_Looker::
	msgbox JubilifeCity_EventScript_Looker_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Looker_Text:
	.string "I am learning the neighborhood.\n"
	.string "Good directions save a lot of shoes.$"

JubilifeCity_EventScript_Counterpart::
	msgbox JubilifeCity_EventScript_Counterpart_Text, MSGBOX_NPC
	end

JubilifeCity_EventScript_Counterpart_Text:
	.string "The school is west of the Center.\n"
	.string "Take your time exploring the city.$"

JubilifeCity_EventScript_FirstArrival::
	lockall
	call SandgemTown_EventScript_SetAssistantGfx
	applymovement LOCALID_JUBILIFE_COUNTERPART, JubilifeCity_Movement_CounterpartGreet
	waitmovement 0
	applymovement LOCALID_JUBILIFE_COUNTERPART, Common_Movement_FacePlayer
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	msgbox JubilifeCity_Text_CounterpartArrival, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_JUBILIFE_COUNTERPART, JubilifeCity_Movement_CounterpartReturn
	waitmovement 0
	setvar VAR_JUBILIFE_ARRIVAL_STATE, 1
	removeobject LOCALID_JUBILIFE_COUNTERPART
	setflag FLAG_HIDE_JUBILIFE_COUNTERPART
	releaseall
	end

JubilifeCity_Movement_CounterpartGreet:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

JubilifeCity_Movement_CounterpartReturn:
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	step_end

JubilifeCity_Text_CounterpartArrival:
	.string "Welcome to JUBILIFE CITY!\p"
	.string "The professor asked me to go ahead\n"
	.string "and check the north side of town.\p"
	.string "Look around first. The TRAINERS'\n"
	.string "SCHOOL and the Center are close by.$"
