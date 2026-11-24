GraniteCave_1F_MapScripts::
	.byte 0

GraniteCave_1F_EventScript_Hiker::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_HM_FLASH, GraniteCave_1F_EventScript_ReceivedFlash
	msgbox GraniteCave_1F_Text_GetsDarkAheadHereYouGo, MSGBOX_DEFAULT
	giveitem ITEM_ESCAPE_ROPE
	setflag FLAG_RECEIVED_HM_FLASH
	msgbox GraniteCave_1F_Text_ExplainFlash, MSGBOX_DEFAULT
	release
	end

GraniteCave_1F_EventScript_ReceivedFlash::
	msgbox GraniteCave_1F_Text_ExplainFlash, MSGBOX_DEFAULT
	release
	end

GraniteCave_1F_Text_GetsDarkAheadHereYouGo:
	.string "Hey, you.\n"
	.string "It gets awfully dark ahead.\l"
	.string "It'll be tough trying to explore.\p"
	.string "That guy who came by earlier…\n"
	.string "STEVEN, I think it was.\p"
	.string "He knew how to light the way, so he\n"
	.string "ought to be all right, but…\p"
	.string "Well, for us HIKERS, helping out those\n"
	.string "that we meet is our motto.\p"
	.string "Take this rope. If the dark closes in,\n"
	.string "you can always pull yourself out.$"

GraniteCave_1F_Text_ExplainFlash:
	.string "Cave darkness is no joke.\n"
	.string "Keep a cool head and a clear path.\p"
	.string "If a POKéMON knows a light move, that\n"
	.string "helps too-just stay ready.$"

