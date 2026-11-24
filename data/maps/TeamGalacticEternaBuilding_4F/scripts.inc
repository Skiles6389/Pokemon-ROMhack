TeamGalacticEternaBuilding_4F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, TeamGalacticEternaBuilding_4F_OnTransition
	.byte 0

TeamGalacticEternaBuilding_4F_OnTransition:
	call_if_set FLAG_ETERNA_BUILDING_CLEARED, TeamGalacticEternaBuilding_4F_EventScript_HideJupiter
	return

TeamGalacticEternaBuilding_4F_EventScript_HideJupiter::
	clearflag FLAG_HIDE_ETERNA_BUILDING_RICKSHAW
	return

TeamGalacticEternaBuilding_4F_EventScript_Jupiter::
	goto TeamGalacticEternaBuilding_4F_EventScript_JupiterBattle
	end

TeamGalacticEternaBuilding_4F_EventScript_JupiterTrigger::
	goto_if_set FLAG_ETERNA_BUILDING_CLEARED, TeamGalacticEternaBuilding_4F_EventScript_JupiterTriggerEnd
	goto TeamGalacticEternaBuilding_4F_EventScript_JupiterBattle
TeamGalacticEternaBuilding_4F_EventScript_JupiterTriggerEnd::
	end

TeamGalacticEternaBuilding_4F_EventScript_JupiterBattle::
	lockall
	playbgm MUS_PL_ENCOUNTER_GALACTIC, FALSE
	applymovement LOCALID_GALACTIC_JUPITER, Common_Movement_FacePlayer
	waitmovement 0
	msgbox TeamGalacticEternaBuilding_4F_Text_JupiterIntro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_COMMANDER_JUPITER, TeamGalacticEternaBuilding_4F_Text_JupiterDefeat
	msgbox TeamGalacticEternaBuilding_4F_Text_JupiterAfter, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_GALACTIC_JUPITER, TeamGalacticEternaBuilding_4F_Movement_JupiterLeave
	waitmovement 0
	removeobject LOCALID_GALACTIC_JUPITER
	setflag FLAG_ETERNA_BUILDING_CLEARED
	setflag FLAG_HIDE_ETERNA_CITY_GALACTIC
	clearflag FLAG_HIDE_ETERNA_BUILDING_RICKSHAW
	clearflag FLAG_HIDE_BIKE_SHOP_OWNER
	fadedefaultbgm
	msgbox TeamGalacticEternaBuilding_4F_Text_Rickshaw, MSGBOX_DEFAULT
	releaseall
	end

TeamGalacticEternaBuilding_4F_Movement_JupiterLeave:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

TeamGalacticEternaBuilding_4F_EventScript_Rickshaw::
	msgbox TeamGalacticEternaBuilding_4F_Text_RickshawChat, MSGBOX_NPC
	end

TeamGalacticEternaBuilding_4F_Text_JupiterIntro:
	.string "Eh? Did you want something?\p"
	.string "How silly of me to even ask.\n"
	.string "You want to free the POKéMON.\p"
	.string "Fine!\n"
	.string "I, JUPITER, will deal with you.$"

TeamGalacticEternaBuilding_4F_Text_JupiterDefeat:
	.string "Losing to some child...\n"
	.string "Being careless cost me too much.$"

TeamGalacticEternaBuilding_4F_Text_JupiterAfter:
	.string "Well, aren't you tough...?\p"
	.string "It's OK, though. Our official POKéMON-\n"
	.string "statue investigation is finished.\p"
	.string "We're withdrawing from Eterna for now.\n"
	.string "Remember the name Team Galactic!$"

TeamGalacticEternaBuilding_4F_Text_Rickshaw:
	.string "I got my CLEFAIRY back, and it's all\n"
	.string "thanks to you!\p"
	.string "Please visit my Cycle Shop.\n"
	.string "I insist on thanking you properly!$"

TeamGalacticEternaBuilding_4F_Text_RickshawChat:
	.string "RICKSHAW: Galactic's gone. Eterna can\n"
	.string "breathe again.$"
