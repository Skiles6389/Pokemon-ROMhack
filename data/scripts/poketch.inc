@ Opened from the start menu once FLAG_RECEIVED_POKETCH is set (see src/start_menu.c).
EventScript_Poketch::
	lockall
EventScript_Poketch_Menu:
	message Text_Poketch_Menu
	waitmessage
	dynmultichoice 0, 0, FALSE, 3, 0, DYN_MULTICHOICE_CB_NONE, Text_Poketch_Clock, Text_Poketch_Party, Text_Poketch_Close
	switch VAR_RESULT
	case 0, EventScript_Poketch_Clock
	case 1, EventScript_Poketch_Party
	closemessage
	releaseall
	end

EventScript_Poketch_Clock:
	special Poketch_BufferTime
	msgbox Text_Poketch_ClockShow, MSGBOX_DEFAULT
	goto EventScript_Poketch_Menu

EventScript_Poketch_Party:
	special Poketch_BufferParty
	msgbox gStringVar4, MSGBOX_DEFAULT
	goto EventScript_Poketch_Menu

Text_Poketch_Menu:
	.string "POKéTCH: which app?$"

Text_Poketch_Clock:
	.string "CLOCK$"

Text_Poketch_Party:
	.string "PARTY$"

Text_Poketch_Close:
	.string "CLOSE$"

Text_Poketch_ClockShow:
	.string "Digital Watch: {STR_VAR_1}\n"
	.string "({STR_VAR_2})$"
