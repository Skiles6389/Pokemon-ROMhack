Route202_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route202_OnTransition
	.byte 0

Route202_OnTransition:
	call SandgemTown_EventScript_SetAssistantGfx
	end

Route202_EventScript_CatchTutorial::
	lockall
	call SandgemTown_EventScript_SetAssistantGfx
	applymovement LOCALID_ROUTE202_ASSISTANT, Common_Movement_FacePlayer
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route202_EventScript_LucasIntro
	msgbox Route202_Text_DawnIntro, MSGBOX_DEFAULT
	goto Route202_EventScript_DoCatch
	end

Route202_EventScript_LucasIntro::
	msgbox Route202_Text_LucasIntro, MSGBOX_DEFAULT
	goto Route202_EventScript_DoCatch
	end

Route202_EventScript_DoCatch::
	closemessage
	setvar VAR_ROUTE202_STATE, 1
	special StartRoute202CatchTutorial
	waitstate
	lock
	faceplayer
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route202_EventScript_LucasBalls
	msgbox Route202_Text_DawnBalls, MSGBOX_DEFAULT
	goto Route202_EventScript_GiveBalls
	end

Route202_EventScript_LucasBalls::
	msgbox Route202_Text_LucasBalls, MSGBOX_DEFAULT
	goto Route202_EventScript_GiveBalls
	end

Route202_EventScript_GiveBalls::
	giveitem ITEM_POKE_BALL, 5
	setvar VAR_ROUTE202_STATE, 2
	releaseall
	end

Route202_EventScript_Assistant::
	lock
	faceplayer
	goto_if_ge VAR_ROUTE202_STATE, 2, Route202_EventScript_AssistantAfter
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route202_EventScript_LucasWait
	msgbox Route202_Text_DawnWait, MSGBOX_DEFAULT
	release
	end

Route202_EventScript_LucasWait::
	msgbox Route202_Text_LucasWait, MSGBOX_DEFAULT
	release
	end

Route202_EventScript_AssistantAfter::
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route202_EventScript_LucasAfter
	msgbox Route202_Text_DawnAfter, MSGBOX_DEFAULT
	release
	end

Route202_EventScript_LucasAfter::
	msgbox Route202_Text_LucasAfter, MSGBOX_DEFAULT
	release
	end

Route202_EventScript_Tristan::
	trainerbattle_single TRAINER_YOUNGSTER_TRISTAN, Route202_Text_TristanIntro, Route202_Text_TristanDefeat
	msgbox Route202_Text_TristanAfter, MSGBOX_AUTOCLOSE
	end

Route202_EventScript_Natalie::
	trainerbattle_single TRAINER_LASS_NATALIE, Route202_Text_NatalieIntro, Route202_Text_NatalieDefeat
	msgbox Route202_Text_NatalieAfter, MSGBOX_AUTOCLOSE
	end

Route202_EventScript_Logan::
	trainerbattle_single TRAINER_YOUNGSTER_LOGAN, Route202_Text_LoganIntro, Route202_Text_LoganDefeat
	msgbox Route202_Text_LoganAfter, MSGBOX_AUTOCLOSE
	end

Route202_EventScript_JubilifeSign::
	msgbox Route202_Text_JubilifeSign, MSGBOX_SIGN
	end

Route202_Text_DawnIntro:
	.string "DAWN: {PLAYER}! Tall grass means\n"
	.string "a wild POKéMON can jump out.\p"
	.string "Watch. I'll catch this one.$"

Route202_Text_LucasIntro:
	.string "LUCAS: {PLAYER}! Tall grass means\n"
	.string "a wild POKéMON can jump out.\p"
	.string "Watch. I'll catch this one.$"

Route202_Text_DawnBalls:
	.string "DAWN: Weaken it first, then throw\n"
	.string "a POKé BALL. These five are yours.$"

Route202_Text_LucasBalls:
	.string "LUCAS: Weaken it first, then throw\n"
	.string "a POKé BALL. These five are yours.$"

Route202_Text_DawnWait:
	.string "DAWN: Step into the grass.\n"
	.string "I'll show you the catch.$"

Route202_Text_LucasWait:
	.string "LUCAS: Step into the grass.\n"
	.string "I'll show you the catch.$"

Route202_Text_DawnAfter:
	.string "DAWN: The city is north, but the\n"
	.string "gate is still shut.$"

Route202_Text_LucasAfter:
	.string "LUCAS: The city is north, but the\n"
	.string "gate is still shut.$"

Route202_Text_TristanIntro:
	.string "I just got a STARLY! You don't\n"
	.string "stand a chance!$"

Route202_Text_TristanDefeat:
	.string "My STARLY fell already?$"

Route202_Text_TristanAfter:
	.string "STARLY is fast. Yours was\n"
	.string "just faster today.$"

Route202_Text_NatalieIntro:
	.string "BIDOOF is plain, and plain is\n"
	.string "plenty. Come on!$"

Route202_Text_NatalieDefeat:
	.string "Plain wasn't plenty.$"

Route202_Text_NatalieAfter:
	.string "A BIDOOF that sticks around\n"
	.string "becomes someone you count on.$"

Route202_Text_LoganIntro:
	.string "This cloak is a BURMY. Don't\n"
	.string "ask me which leaf is which.$"

Route202_Text_LoganDefeat:
	.string "The cloak didn't help.$"

Route202_Text_LoganAfter:
	.string "BURMY wears whatever it finds.\n"
	.string "Today, that's grass.$"

Route202_Text_JubilifeSign:
	.string "NORTH: JUBILIFE CITY\n"
	.string "The gate is still shut.$"
