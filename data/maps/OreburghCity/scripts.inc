OreburghCity_MapScripts::
	.byte 0

@ Platinum's arrival beat: Barry runs into the player and says Roark is at the
@ mine. The path out of Oreburgh Gate is two tiles wide, so the trigger can't be skirted.
OreburghCity_EventScript_BarryTrigger::
	lockall
	getplayerxy VAR_TEMP_0, VAR_TEMP_1
	goto_if_ne VAR_TEMP_0, 7, OreburghCity_EventScript_BarryAppear
	setobjectxyperm LOCALID_OREBURGH_BARRY, 7, 15
OreburghCity_EventScript_BarryAppear::
	addobject LOCALID_OREBURGH_BARRY
	applymovement LOCALID_OREBURGH_BARRY, OreburghCity_Movement_BarryRunUp
	waitmovement 0
	playse SE_PIN
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceDown
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
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

OreburghCity_Movement_BarryRunOff:
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
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
	.string "ROARK's on his way back up, but\n"
	.string "the GYM's still being set up for\l"
	.string "challengers.\p"
	.string "Check back soon, okay?$"

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
