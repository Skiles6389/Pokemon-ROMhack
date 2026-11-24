Route207_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route207_OnTransition
	.byte 0

Route207_OnTransition:
	call Route207_EventScript_SetCounterpartGfx
	end

Route207_EventScript_SetCounterpartGfx::
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, Route207_EventScript_SetDawnGfx
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL
	return

Route207_EventScript_SetDawnGfx::
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RIVAL_MAY_NORMAL
	return

Route207_EventScript_Anthony::
	trainerbattle_single TRAINER_CAMPER_ANTHONY_R207, Route207_Text_AnthonyIntro, Route207_Text_AnthonyDefeat
	msgbox Route207_Text_AnthonyAfter, MSGBOX_AUTOCLOSE
	end

Route207_Text_AnthonyIntro:
	.string "Go for it, my POKéMON!\n"
	.string "I'll do my best, too!$"

Route207_Text_AnthonyDefeat:
	.string "Oh...\n"
	.string "We lost...$"

Route207_Text_AnthonyAfter:
	.string "Dig for Fossils in the Underground.\n"
	.string "The mining museum might be able to\p"
	.string "bring back the ancient POKéMON!$"

Route207_EventScript_Lauren::
	trainerbattle_single TRAINER_PICNICKER_LAUREN_R207, Route207_Text_LaurenIntro, Route207_Text_LaurenDefeat
	msgbox Route207_Text_LaurenAfter, MSGBOX_AUTOCLOSE
	end

Route207_Text_LaurenIntro:
	.string "Go do it, my POKéMON!\n"
	.string "I'll work hard, too!$"

Route207_Text_LaurenDefeat:
	.string "Oh...\n"
	.string "We lost...$"

Route207_Text_LaurenAfter:
	.string "I think we'll visit the TV station in\n"
	.string "Jubilife City next.\p"
	.string "Or maybe we should go to the Global\n"
	.string "Terminal?$"

Route207_EventScript_Austin::
	trainerbattle_single TRAINER_YOUNGSTER_AUSTIN_R207, Route207_Text_AustinIntro, Route207_Text_AustinDefeat
	msgbox Route207_Text_AustinAfter, MSGBOX_AUTOCLOSE
	end

Route207_Text_AustinIntro:
	.string "I wear shorts the whole year!\n"
	.string "I've got energy to burn!$"

Route207_Text_AustinDefeat:
	.string "I couldn't win with just energy...\n"
	.string "Nothing's really that easy!$"

Route207_Text_AustinAfter:
	.string "POKéMON don't wear clothes.\n"
	.string "I worry about them getting cold.$"

Route207_EventScript_Justin::
	trainerbattle_single TRAINER_HIKER_JUSTIN_R207, Route207_Text_JustinIntro, Route207_Text_JustinDefeat
	msgbox Route207_Text_JustinAfter, MSGBOX_AUTOCLOSE
	end

Route207_Text_JustinIntro:
	.string "I just got through Mt. Coronet, but\n"
	.string "I've still got energy to burn!$"

Route207_Text_JustinDefeat:
	.string "Whoops!\n"
	.string "Taken down easily!$"

Route207_Text_JustinAfter:
	.string "We need to rest up in Oreburgh City\n"
	.string "before heading to Mt. Coronet again.$"

Route207_EventScript_Kevin::
	trainerbattle_single TRAINER_HIKER_KEVIN_R207, Route207_Text_KevinIntro, Route207_Text_KevinDefeat
	msgbox Route207_Text_KevinAfter, MSGBOX_AUTOCLOSE
	end

Route207_Text_KevinIntro:
	.string "Wahaha!\n"
	.string "Laughter brings good fortune!$"

Route207_Text_KevinDefeat:
	.string "Wahahaha! There's nothing that\n"
	.string "I can do but laugh!$"

Route207_Text_KevinAfter:
	.string "Wahahahaha!\n"
	.string "...Go ahead, laugh at me--the loser!$"

Route207_EventScript_Helen::
	trainerbattle_single TRAINER_BATTLE_GIRL_HELEN_R207, Route207_Text_HelenIntro, Route207_Text_HelenDefeat
	msgbox Route207_Text_HelenAfter, MSGBOX_AUTOCLOSE
	end

Route207_Text_HelenIntro:
	.string "OK, OK!\n"
	.string "Let's be quick about this!$"

Route207_Text_HelenDefeat:
	.string "Oh, yeah? Let's do this again!\n"
	.string "...Oops. I'm out of POKéMON!$"

Route207_Text_HelenAfter:
	.string "Yup! Good going!\n"
	.string "I like the way you battle!$"


Route207_EventScript_Counterpart::
	lock
	faceplayer
	goto_if_set FLAG_GOT_VS_SEEKER_SINNOH, Route207_EventScript_CounterpartAfter
	goto Route207_EventScript_CounterpartGift
	end

Route207_EventScript_CounterpartScene::
	lockall
	goto_if_set FLAG_GOT_VS_SEEKER_SINNOH, Route207_EventScript_CounterpartSceneDone
	call Route207_EventScript_SetCounterpartGfx
	setobjectxyperm LOCALID_ROUTE207_COUNTERPART, 51, 8
	setobjectmovementtype LOCALID_ROUTE207_COUNTERPART, MOVEMENT_TYPE_FACE_RIGHT
	clearflag FLAG_HIDE_ROUTE207_COUNTERPART
	addobject LOCALID_ROUTE207_COUNTERPART
	applymovement LOCALID_ROUTE207_COUNTERPART, Common_Movement_FacePlayer
	waitmovement 0
	goto Route207_EventScript_CounterpartGift
	end

Route207_EventScript_CounterpartSceneDone::
	releaseall
	end

Route207_EventScript_CounterpartGift::
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route207_EventScript_LucasGift
	msgbox Route207_Text_DawnChoose, MSGBOX_DEFAULT
	msgbox Route207_Text_DawnWantSeeker, MSGBOX_DEFAULT
	giveitem ITEM_VS_SEEKER
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_VS_SEEKER_SINNOH
	msgbox Route207_Text_DawnHaveThisToo, MSGBOX_DEFAULT
	giveitem ITEM_DOWSING_MACHINE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	msgbox Route207_Text_DawnDowsing, MSGBOX_DEFAULT
	goto Route207_EventScript_CounterpartFinish
	end

Route207_EventScript_LucasGift::
	msgbox Route207_Text_LucasChoose, MSGBOX_DEFAULT
	msgbox Route207_Text_LucasWantSeeker, MSGBOX_DEFAULT
	giveitem ITEM_VS_SEEKER
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_GOT_VS_SEEKER_SINNOH
	msgbox Route207_Text_LucasHaveThisToo, MSGBOX_DEFAULT
	giveitem ITEM_DOWSING_MACHINE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	msgbox Route207_Text_LucasDowsing, MSGBOX_DEFAULT
	goto Route207_EventScript_CounterpartFinish
	end

Route207_EventScript_CounterpartFinish::
	closemessage
	applymovement LOCALID_ROUTE207_COUNTERPART, Route207_Movement_CounterpartLeave
	waitmovement 0
	removeobject LOCALID_ROUTE207_COUNTERPART
	setflag FLAG_HIDE_ROUTE207_COUNTERPART
	setvar VAR_ROUTE207_STATE, 1
	releaseall
	end

Route207_EventScript_CounterpartAfter::
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route207_EventScript_LucasAfter
	msgbox Route207_Text_DawnDowsing, MSGBOX_DEFAULT
	release
	end

Route207_EventScript_LucasAfter::
	msgbox Route207_Text_LucasDowsing, MSGBOX_DEFAULT
	release
	end

Route207_EventScript_CyclistTip::
	checkitem ITEM_BICYCLE
	goto_if_eq VAR_RESULT, FALSE, Route207_EventScript_NeedBikeTip
	msgbox Route207_Text_ChangeGear, MSGBOX_NPC
	end

Route207_EventScript_NeedBikeTip::
	msgbox Route207_Text_NeedBike, MSGBOX_NPC
	end

Route207_EventScript_BlockedLedge::
	lockall
	msgbox Route207_Text_BlockedLedge, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkLeft
	waitmovement 0
	releaseall
	end

Route207_EventScript_PokeBall::
	finditem ITEM_POKE_BALL
	end

Route207_EventScript_SignOreburgh::
	msgbox Route207_Text_SignOreburgh, MSGBOX_SIGN
	end

Route207_EventScript_SignMtCoronet::
	msgbox Route207_Text_SignMtCoronet, MSGBOX_SIGN
	end

Route207_EventScript_TrainerTips::
	msgbox Route207_Text_TrainerTips, MSGBOX_SIGN
	end

Route207_Movement_CounterpartLeave:
	walk_down
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

Route207_Text_DawnChoose:
	.string "DAWN: Hi, {PLAYER}!\n"
	.string "How's your POKéDEX coming along?\pMe? I'm somewhere between fantastic\p"
	.string "and, uh, hopeless...\pBut this isn't about me!\n"
	.string "I've got something nice for you.\p{PLAYER}, choose which hand\p"
	.string "you want.$"
Route207_Text_DawnWantSeeker:
	.string "DAWN: I see...\n"
	.string "You want the Vs. Seeker.\pI'm impressed, {PLAYER}.\p"
	.string "You know what's important.$"
Route207_Text_DawnHaveThisToo:
	.string "DAWN: Using that Vs. Seeker, you can\n"
	.string "find Trainers who want a rematch\lwith you.\pOh, {PLAYER}, do you also have\p"
	.string "a gadget for finding items?\pYup, you do.\n"
	.string "You can have this too, then.\pYou deserve it for all your hard\p"
	.string "work, {PLAYER}.$"
Route207_Text_DawnDowsing:
	.string "DAWN: The DOWSING MACHINE is\n"
	.string "something you should use often.\pIt will tell you if there is an item\p"
	.string "on the ground that you can't see.\pOK, let's keep working on our\n"
	.string "POKéDEXES.\pProfessor Rowan is counting on us!$"
Route207_Text_LucasChoose:
	.string "LUCAS: Hey, {PLAYER}!\n"
	.string "How's your POKéDEX coming along?\pMe? I'm always doing great!\p"
	.string "...I wish...\pBut that's not important.\n"
	.string "Lately, I've been experimenting with\la couple of neat tools.\p{PLAYER}, I'll share with you.\p"
	.string "Choose a hand!$"
Route207_Text_LucasWantSeeker:
	.string "LUCAS: Oh yeah.\n"
	.string "You want the Vs. Seeker.\pYup, {PLAYER}, you know what's\p"
	.string "important.$"
Route207_Text_LucasHaveThisToo:
	.string "LUCAS: Using that Vs. Seeker, you can\n"
	.string "find Trainers who want to battle with\lyou again.\p{PLAYER}, what about finding items?\p"
	.string "Do you have a Dowsing Machine?\pYup, you do.\n"
	.string "You can have this too, then.\pYou deserve it for all of your\p"
	.string "effort, {PLAYER}.$"
Route207_Text_LucasDowsing:
	.string "LUCAS: The DOWSING MACHINE is...\n"
	.string "Just try using it.\pIt'll alert you if there is an\p"
	.string "unseeable item on the ground.\pOK, keep working on your POKéDEX.\n"
	.string "Professor Rowan is counting on us!$"
Route207_Text_NeedBike:
	.string "That slope's too slippery.\n"
	.string "You'll need a Bike to get up.\pYou don't have a Bicycle?\p"
	.string "There's a Cycle Shop in Eterna City.$"
Route207_Text_ChangeGear:
	.string "Change gears and take a run.\n"
	.string "That'll shoot you right up that slope.$"
Route207_Text_BlockedLedge:
	.string "A steep ledge blocks the path.\n"
	.string "You'll need a better technique later!$"
Route207_Text_SignOreburgh:
	.string "Rt. 207\n"
	.string "Oreburgh City$"
Route207_Text_SignMtCoronet:
	.string "Rt. 207\n"
	.string "Mt. Coronet$"
Route207_Text_TrainerTips:
	.string "TRAINER TIPS\pPOKéMON may become immobilized if\n"
	.string "they are asleep or paralyzed.\pIf it happens to your POKéMON,\p"
	.string "heal them right away!$"
