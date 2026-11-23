OreburghCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OreburghCity_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, OreburghCity_OnFrame
	.byte 0

@ Once the player has met Roark in the mine, the guide steps aside from the Gym door.
OreburghCity_OnTransition:
	call_if_ge VAR_OREBURGH_STATE, 2, OreburghCity_EventScript_GuideStepAside
	end

OreburghCity_EventScript_GuideStepAside::
	setobjectxyperm LOCALID_OREBURGH_GYM_GUIDE, 27, 21
	setobjectmovementtype LOCALID_OREBURGH_GYM_GUIDE, MOVEMENT_TYPE_FACE_LEFT
	return

@ State 3 is set when Roark is beaten. Stepping out of the Gym ends the demo.
OreburghCity_OnFrame:
	map_script_2 VAR_OREBURGH_STATE, 3, OreburghCity_EventScript_DemoEnd
	.2byte 0

OreburghCity_EventScript_DemoEnd::
	lockall
	msgbox OreburghCity_Text_DemoEnd, MSGBOX_DEFAULT
	setvar VAR_OREBURGH_STATE, 4
	releaseall
	end

@ Platinum's arrival beat: Barry runs into the player and says Roark is at the
@ mine. The trigger spans the full width of the path out of Oreburgh Gate.
OreburghCity_EventScript_BarryTrigger::
	lockall
	getplayerxy VAR_TEMP_0, VAR_TEMP_1
	addvar VAR_TEMP_0, 3
	setobjectxyperm LOCALID_OREBURGH_BARRY, VAR_TEMP_0, VAR_TEMP_1
	addobject LOCALID_OREBURGH_BARRY
	applymovement LOCALID_OREBURGH_BARRY, OreburghCity_Movement_BarryRunUp
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceRight
	waitmovement 0
	msgbox OreburghCity_Text_BarryBump, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_OREBURGH_BARRY, OreburghCity_Movement_BarryRunOff
	waitmovement 0
	removeobject LOCALID_OREBURGH_BARRY
	setflag FLAG_HIDE_OREBURGH_BARRY
	setvar VAR_OREBURGH_STATE, 1
	releaseall
	end

OreburghCity_EventScript_Barry::
	msgbox OreburghCity_Text_BarryBump, MSGBOX_NPC
	end

OreburghCity_Movement_BarryRunUp:
	walk_fast_left
	walk_fast_left
	step_end

OreburghCity_Movement_BarryRunOff:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

@ The Gym opens in milestone 9. Until then its guide stands in the doorway.
OreburghCity_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_ge VAR_OREBURGH_STATE, 2, OreburghCity_EventScript_GymGuideLater
	msgbox OreburghCity_Text_GymGuideMine, MSGBOX_DEFAULT
	release
	end

OreburghCity_EventScript_GymGuideLater::
	msgbox OreburghCity_Text_GymGuideLater, MSGBOX_DEFAULT
	release
	end

@ Route 207 stays closed until a later milestone.
OreburghCity_EventScript_Route207Closed::
	lockall
	msgbox OreburghCity_Text_Route207Closed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkDown
	waitmovement 0
	releaseall
	end

OreburghCity_EventScript_Route207Worker::
	msgbox OreburghCity_Text_Route207Closed, MSGBOX_NPC
	end

OreburghCity_EventScript_Hiker::
	msgbox OreburghCity_Text_Hiker, MSGBOX_NPC
	end

OreburghCity_EventScript_SchoolKid::
	msgbox OreburghCity_Text_SchoolKid, MSGBOX_NPC
	end

OreburghCity_EventScript_PokefanF::
	msgbox OreburghCity_Text_PokefanF, MSGBOX_NPC
	end

OreburghCity_EventScript_MineWorker::
	msgbox OreburghCity_Text_MineWorker, MSGBOX_NPC
	end

OreburghCity_EventScript_Worker2::
	msgbox OreburghCity_Text_Worker2, MSGBOX_NPC
	end

OreburghCity_EventScript_Camper::
	msgbox OreburghCity_Text_Camper, MSGBOX_NPC
	end

OreburghCity_EventScript_BattleGirl::
	msgbox OreburghCity_Text_BattleGirl, MSGBOX_NPC
	end

OreburghCity_EventScript_CitySign::
	msgbox OreburghCity_Text_CitySign, MSGBOX_SIGN
	end

OreburghCity_EventScript_GymSign::
	msgbox OreburghCity_Text_GymSign, MSGBOX_SIGN
	end

OreburghCity_EventScript_MuseumSign::
	msgbox OreburghCity_Text_MuseumSign, MSGBOX_SIGN
	end

OreburghCity_EventScript_MineSign::
	msgbox OreburghCity_Text_MineSign, MSGBOX_SIGN
	end

OreburghCity_EventScript_Route207Sign::
	msgbox OreburghCity_Text_Route207Sign, MSGBOX_SIGN
	end

OreburghCity_Text_BarryBump:
	.string "BARRY: Oof! Hey, watch it!\n"
	.string "…Oh, it's you! Perfect timing!\p"
	.string "I went to the GYM, but the LEADER,\n"
	.string "ROARK, isn't even there!\p"
	.string "Word is he's down in the OREBURGH\n"
	.string "MINE south of town. I'm off to\l"
	.string "find him before you do!$"

OreburghCity_Text_GymGuideMine:
	.string "Here for the GYM? ROARK's not in.\p"
	.string "He's working down in the OREBURGH\n"
	.string "MINE. The entrance is in the big\l"
	.string "rock hill in the south-east.$"

OreburghCity_Text_GymGuideLater:
	.string "ROARK's back! Go on in.\p"
	.string "He uses Rock types. Water, Grass\n"
	.string "and Fighting moves hit them hard,\l"
	.string "and Normal moves barely scratch!$"

OreburghCity_Text_Route207Closed:
	.string "Sorry, ROUTE 207 is closed while\n"
	.string "we shore up the hillside.$"

OreburghCity_Text_Hiker:
	.string "Coal from the mine keeps the\n"
	.string "lights on all over SINNOH.$"

OreburghCity_Text_SchoolKid:
	.string "My dad digs in the mine. He comes\n"
	.string "home black from head to toe!$"

OreburghCity_Text_PokefanF:
	.string "The MINING MUSEUM has rocks you\n"
	.string "can't find anywhere else.$"

OreburghCity_Text_MineWorker:
	.string "That hill is the OREBURGH MINE.\n"
	.string "Watch your step down there.$"

OreburghCity_Text_Worker2:
	.string "Our GYM LEADER works the mine with\n"
	.string "the rest of us. Good guy.$"

OreburghCity_Text_Camper:
	.string "Rock types shrug off normal hits.\n"
	.string "Bring something stronger!$"

OreburghCity_Text_BattleGirl:
	.string "I train by hauling rocks with the\n"
	.string "miners. Great for the legs!$"

OreburghCity_Text_CitySign:
	.string "OREBURGH CITY\n"
	.string "“Built on coal and hard work.”$"

OreburghCity_Text_GymSign:
	.string "OREBURGH CITY POKéMON GYM\n"
	.string "LEADER: ROARK$"

OreburghCity_Text_MuseumSign:
	.string "OREBURGH MINING MUSEUM\n"
	.string "The story of the mine and its coal.$"

OreburghCity_Text_MineSign:
	.string "OREBURGH MINE\n"
	.string "Keep out of the work areas!$"

OreburghCity_Text_Route207Sign:
	.string "North: ROUTE 207$"

OreburghCity_Text_DemoEnd:
	.string "Thanks for playing the demo!\n"
	.string "More of Sinnoh is coming.$"
