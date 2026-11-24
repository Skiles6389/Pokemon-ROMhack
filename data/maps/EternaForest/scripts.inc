EternaForest_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, EternaForest_OnTransition
	.byte 0

EternaForest_OnTransition:
	call_if_eq VAR_ETERNA_FOREST_CHERYL_STATE, 2, EternaForest_EventScript_HideCheryl
	end

EternaForest_EventScript_HideCheryl::
	setflag FLAG_HIDE_ETERNA_FOREST_CHERYL
	return

EternaForest_EventScript_Cheryl::
	lock
	faceplayer
	goto_if_ge VAR_ETERNA_FOREST_CHERYL_STATE, 2, EternaForest_EventScript_CherylDone
	goto_if_eq VAR_ETERNA_FOREST_CHERYL_STATE, 1, EternaForest_EventScript_CherylFollowing
	msgbox EternaForest_Text_CherylGreeting, MSGBOX_DEFAULT
	release
	end

EternaForest_EventScript_CherylJoinTrigger::
	lockall
	applymovement LOCALID_ETERNA_FOREST_CHERYL, Common_Movement_FacePlayer
	waitmovement 0
	msgbox EternaForest_Text_CherylJoinOffer, MSGBOX_DEFAULT
	closemessage
	setvar VAR_ETERNA_FOREST_CHERYL_STATE, 1
	setfollowernpc LOCALID_ETERNA_FOREST_CHERYL, FNPC_WHITE_OUT, EternaForest_EventScript_CherylTalk, PARTNER_CHERYL
	msgbox EternaForest_Text_CherylJoined, MSGBOX_DEFAULT
	releaseall
	end

EternaForest_EventScript_CherylTalk::
	msgbox EternaForest_Text_CherylFollowChat, MSGBOX_NPC
	end

EternaForest_EventScript_CherylLeaveTrigger::
	lockall
	destroyfollowernpc
	msgbox EternaForest_Text_CherylParting, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_ETERNA_FOREST_CHERYL, EternaForest_Movement_CherylLeave
	waitmovement 0
	removeobject LOCALID_ETERNA_FOREST_CHERYL
	setvar VAR_ETERNA_FOREST_CHERYL_STATE, 2
	setflag FLAG_HIDE_ETERNA_FOREST_CHERYL
	releaseall
	end

EternaForest_Movement_CherylLeave:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

EternaForest_EventScript_CherylFollowing::
	msgbox EternaForest_Text_CherylFollowChat, MSGBOX_NPC
	end

EternaForest_EventScript_CherylDone::
	msgbox EternaForest_Text_CherylAfter, MSGBOX_NPC
	end

EternaForest_EventScript_MossRock::
	lock
	faceplayer
	msgbox EternaForest_Text_MossRock, MSGBOX_DEFAULT
	release
	end

EternaForest_EventScript_Jack::
	trainerbattle_single TRAINER_BUG_CATCHER_JACK, EternaForest_Text_JackIntro, EternaForest_Text_JackDefeat
	msgbox EternaForest_Text_JackAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Phillip::
	trainerbattle_single TRAINER_BUG_CATCHER_PHILLIP, EternaForest_Text_PhillipIntro, EternaForest_Text_PhillipDefeat
	msgbox EternaForest_Text_PhillipAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Donald::
	trainerbattle_single TRAINER_BUG_CATCHER_DONALD, EternaForest_Text_DonaldIntro, EternaForest_Text_DonaldDefeat
	msgbox EternaForest_Text_DonaldAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Kody::
	trainerbattle_single TRAINER_PSYCHIC_KODY, EternaForest_Text_KodyIntro, EternaForest_Text_KodyDefeat
	msgbox EternaForest_Text_KodyAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Lindsey::
	trainerbattle_single TRAINER_PSYCHIC_LINDSEY, EternaForest_Text_LindseyIntro, EternaForest_Text_LindseyDefeat
	msgbox EternaForest_Text_LindseyAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Elijah::
	trainerbattle_single TRAINER_PSYCHIC_ELIJAH, EternaForest_Text_ElijahIntro, EternaForest_Text_ElijahDefeat
	msgbox EternaForest_Text_ElijahAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Rachael::
	trainerbattle_single TRAINER_PSYCHIC_RACHAEL, EternaForest_Text_RachaelIntro, EternaForest_Text_RachaelDefeat
	msgbox EternaForest_Text_RachaelAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Briana::
	trainerbattle_single TRAINER_LASS_BRIANA, EternaForest_Text_BrianaIntro, EternaForest_Text_BrianaDefeat
	msgbox EternaForest_Text_BrianaAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Caroline::
	trainerbattle_single TRAINER_LASS_CAROLINE_FOREST, EternaForest_Text_CarolineIntro, EternaForest_Text_CarolineDefeat
	msgbox EternaForest_Text_CarolineAfter, MSGBOX_AUTOCLOSE
	end

EternaForest_EventScript_Potion::
	finditem ITEM_POTION
	end

EternaForest_EventScript_Ether::
	finditem ITEM_ETHER
	end

EternaForest_EventScript_Antidote::
	finditem ITEM_ANTIDOTE
	end

EternaForest_EventScript_SignSouth::
	msgbox EternaForest_Text_SignSouth, MSGBOX_SIGN
	end

EternaForest_EventScript_OldChateau::
	msgbox EternaForest_Text_OldChateauLocked, MSGBOX_SIGN
	end

EternaForest_Text_CherylGreeting:
	.string "Hello, my name's CHERYL.\n"
	.string "And you are...?$"

EternaForest_Text_CherylJoinOffer:
	.string "OK, so your name is {PLAYER}.\n"
	.string "I'm sincerely glad to meet you.\p"
	.string "{PLAYER}, may I ask a big favor\n"
	.string "of you?\p"
	.string "I want to get through this forest,\n"
	.string "but I'm afraid of doing it alone.\p"
	.string "I've heard that there is a sinister\n"
	.string "group of people called Team Galactic\l"
	.string "about.\p"
	.string "I think there'd be safety in numbers.\n"
	.string "Please, may I go through with you?$"

EternaForest_Text_CherylJoined:
	.string "{PLAYER} decided to go with CHERYL!$"

EternaForest_Text_CherylFollowChat:
	.string "CHERYL: Let's stick together.\n"
	.string "My CHANSEY will help if we battle.$"

EternaForest_Text_CherylParting:
	.string "CHERYL: Oh! There's the exit!\n"
	.string "I'm so relieved... We finally got here.\p"
	.string "I would've never been able to get\n"
	.string "through this by myself.\p"
	.string "Thank you so much, {PLAYER}!$"

EternaForest_Text_CherylAfter:
	.string "CHERYL: Take care on the road\n"
	.string "to Eterna City!$"

EternaForest_Text_MossRock:
	.string "The rock is covered in moss.\n"
	.string "It feels pleasantly cool.$"

EternaForest_Text_JackIntro:
	.string "Bug types love these trees!$"

EternaForest_Text_JackDefeat:
	.string "Swatted down...$"

EternaForest_Text_JackAfter:
	.string "Eterna Forest hides rare bugs.$"

EternaForest_Text_PhillipIntro:
	.string "My net's ready--catch this battle!$"

EternaForest_Text_PhillipDefeat:
	.string "They flew away...$"

EternaForest_Text_PhillipAfter:
	.string "Try a Repel if you're scared of bugs.$"

EternaForest_Text_DonaldIntro:
	.string "Listen to the rustling leaves!\n"
	.string "Time to battle!$"

EternaForest_Text_DonaldDefeat:
	.string "Oops, too loud...$"

EternaForest_Text_DonaldAfter:
	.string "The Old Chateau past here is spooky.$"

EternaForest_Text_KodyIntro:
	.string "I sense a Trainer approaching...$"

EternaForest_Text_KodyDefeat:
	.string "My mind went blank!$"

EternaForest_Text_KodyAfter:
	.string "Psychics train best in quiet woods.$"

EternaForest_Text_LindseyIntro:
	.string "The spirits whisper of a battle!$"

EternaForest_Text_LindseyDefeat:
	.string "Silence falls...$"

EternaForest_Text_LindseyAfter:
	.string "Don't linger by the Old Chateau.$"

EternaForest_Text_ElijahIntro:
	.string "Focus your aura--or lose!$"

EternaForest_Text_ElijahDefeat:
	.string "Unbalanced...$"

EternaForest_Text_ElijahAfter:
	.string "Cheryl's been kind to travelers here.$"

EternaForest_Text_RachaelIntro:
	.string "Can you read the forest's mood?$"

EternaForest_Text_RachaelDefeat:
	.string "I misread you completely!$"

EternaForest_Text_RachaelAfter:
	.string "Eterna City is east of the far side.$"

EternaForest_Text_BrianaIntro:
	.string "Don't get lost--let's fight instead!$"

EternaForest_Text_BrianaDefeat:
	.string "Now I'm dizzy too...$"

EternaForest_Text_BrianaAfter:
	.string "Follow the path, not the mushrooms.$"

EternaForest_Text_CarolineIntro:
	.string "This LASS isn't afraid of the dark!$"

EternaForest_Text_CarolineDefeat:
	.string "See? Even I can lose here.$"

EternaForest_Text_CarolineAfter:
	.string "Team Galactic caused trouble past here.$"

EternaForest_Text_SignSouth:
	.string "ETERNA FOREST\n"
	.string "Route 205$"

EternaForest_Text_OldChateauLocked:
	.string "The Old Chateau's doors are sealed.\n"
	.string "This path isn't open yet.$"
EternaForest_EventScript_PlatNpc1::
	msgbox EternaForest_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

EternaForest_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaForest_EventScript_PlatNpc3::
	msgbox EternaForest_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

EternaForest_EventScript_PlatNpc3_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaForest_EventScript_PlatNpc5::
	msgbox EternaForest_EventScript_PlatNpc5_Text, MSGBOX_NPC
	end

EternaForest_EventScript_PlatNpc5_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaForest_EventScript_PlatNpc7::
	msgbox EternaForest_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

EternaForest_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

EternaForest_EventScript_PlatNpc8::
	msgbox EternaForest_EventScript_PlatNpc8_Text, MSGBOX_NPC
	end

EternaForest_EventScript_PlatNpc8_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

