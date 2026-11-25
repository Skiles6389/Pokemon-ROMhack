EternaCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, EternaCity_OnTransition
	.byte 0

EternaCity_OnTransition:
	setflag FLAG_VISITED_ETERNA_CITY
	end

EternaCity_EventScript_Cynthia::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_HM_CUT, EternaCity_EventScript_CynthiaDone
	msgbox EternaCity_Text_CynthiaIntro, MSGBOX_DEFAULT
	giveitem ITEM_HM_CUT
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_HM_CUT
	setvar VAR_ETERNA_CITY_STATE, 2
	msgbox EternaCity_Text_CynthiaGiveCut, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_ETERNA_CITY_CYNTHIA, EternaCity_Movement_CynthiaLeave
	waitmovement 0
	removeobject LOCALID_ETERNA_CITY_CYNTHIA
	setflag FLAG_HIDE_ETERNA_CITY_CYNTHIA
	release
	end

EternaCity_Movement_CynthiaLeave:
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

EternaCity_EventScript_CynthiaDone::
	msgbox EternaCity_Text_CynthiaAfterGift, MSGBOX_DEFAULT
	release
	end

EternaCity_EventScript_Gardenia::
	lock
	faceplayer
	msgbox EternaCity_Text_GardeniaCameo, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_ETERNA_CITY_GARDENIA, EternaCity_Movement_GardeniaLeave
	waitmovement 0
	removeobject LOCALID_ETERNA_CITY_GARDENIA
	setflag FLAG_HIDE_ETERNA_CITY_GARDENIA
	release
	end

EternaCity_Movement_GardeniaLeave:
	walk_down
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

EternaCity_EventScript_GalacticGrunt1::
	goto_if_set FLAG_HIDE_ETERNA_CITY_GALACTIC, EternaCity_EventScript_GruntGone
	msgbox EternaCity_Text_GalacticBlock, MSGBOX_NPC
	end

EternaCity_EventScript_GalacticGrunt2::
	goto_if_set FLAG_HIDE_ETERNA_CITY_GALACTIC, EternaCity_EventScript_GruntGone
	msgbox EternaCity_Text_GalacticBlock, MSGBOX_NPC
	end

EternaCity_EventScript_GruntGone::
	end

EternaCity_EventScript_SuperRepel::
	finditem ITEM_SUPER_REPEL
	end

EternaCity_EventScript_CyclingRoadGate::
	lock
	msgbox EternaCity_Text_CyclingRoadClosed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, EternaCity_Movement_PushBack
	waitmovement 0
	release
	end

EternaCity_EventScript_Route211Gate::
	lock
	msgbox EternaCity_Text_Route211Closed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, EternaCity_Movement_PushWest
	waitmovement 0
	release
	end

EternaCity_Movement_PushBack:
	walk_down
	step_end

EternaCity_Movement_PushWest:
	walk_left
	step_end

EternaCity_EventScript_GymSign::
	msgbox EternaCity_Text_GymSign, MSGBOX_SIGN
	end

EternaCity_EventScript_CitySign::
	msgbox EternaCity_Text_CitySign, MSGBOX_SIGN
	end

EternaCity_Text_CynthiaIntro:
	.string "Oh, that device you have...\p"
	.string "It is a POKéDEX?\n"
	.string "Wow, it brings back some memories.\p"
	.string "Pardon me, but what's your name?\p"
	.string "...\p"
	.string "OK, hello, {PLAYER}.\n"
	.string "I'll be sure to remember that name!\p"
	.string "My name is CYNTHIA.\n"
	.string "I'm a Trainer just like you.\p"
	.string "I've been studying POKéMON mythology\n"
	.string "lately, just out of curiosity.\p"
	.string "Here in Eterna City, there is a statue\n"
	.string "of an ancient POKéMON.\p"
	.string "Who knows? You may encounter something\n"
	.string "like it while you're traveling.\p"
	.string "Oh, I know! Try using this.\n"
	.string "It should be helpful.$"

EternaCity_Text_CynthiaGiveCut:
	.string "CYNTHIA: Remember, the hidden move\n"
	.string "Cut can be used in the field.\p"
	.string "It will let you go places that were\n"
	.string "previously inaccessible to you.\p"
	.string "That's important for filling up your\n"
	.string "POKéDEX, right?\p"
	.string "Then luck be with you, young Trainer!\p"
	.string "Oh, there's one last thing!\n"
	.string "Please give my regards to Prof. Rowan.$"

EternaCity_Text_CynthiaAfterGift:
	.string "CYNTHIA: Cut will open new paths.\n"
	.string "Use it wisely, {PLAYER}.$"

EternaCity_Text_GardeniaCameo:
	.string "GARDENIA: The Gym's open!\n"
	.string "My Grass types are waiting.$"

EternaCity_Text_GalacticBlock:
	.string "GRUNT: Commander Jupiter's orders!\n"
	.string "No one interrupts our work!$"

EternaCity_Text_CyclingRoadClosed:
	.string "CYCLING ROAD AHEAD\n"
	.string "The gate is open. Grab a Bicycle\n"
	.string "from the Bike Shop if you need one.$"

EternaCity_Text_Route211Closed:
	.string "ROUTE 211\n"
	.string "This path isn't open yet.\n"
	.string "Please come back another time.$"

EternaCity_Text_GymSign:
	.string "ETERNA CITY POKéMON GYM\n"
	.string "LEADER: GARDENIA\n"
	.string "The Verdant Virtuoso$"

EternaCity_Text_CitySign:
	.string "ETERNA CITY\n"
	.string "History Blooming$"
EternaCity_EventScript_PlatNpc0::
	msgbox EternaCity_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

EternaCity_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaCity_EventScript_PlatNpc1::
	msgbox EternaCity_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

EternaCity_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaCity_EventScript_PlatNpc2::
	msgbox EternaCity_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

EternaCity_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaCity_EventScript_PlatNpc3::
	msgbox EternaCity_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

EternaCity_EventScript_PlatNpc3_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaCity_EventScript_PlatNpc4::
	msgbox EternaCity_EventScript_PlatNpc4_Text, MSGBOX_NPC
	end

EternaCity_EventScript_PlatNpc4_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaCity_EventScript_PlatNpc5::
	msgbox EternaCity_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

EternaCity_EventScript_PlatNpc5_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaCity_EventScript_PlatNpc6::
	msgbox EternaCity_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

EternaCity_EventScript_PlatNpc6_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaCity_EventScript_PlatNpc7::
	msgbox EternaCity_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

EternaCity_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

