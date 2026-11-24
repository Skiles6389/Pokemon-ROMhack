Route213_HotelLobby_MapScripts::
	.byte 0

Route213_HotelLobby_EventScript_Clerk::
	msgbox Route213_HotelLobby_Text_Clerk, MSGBOX_NPC
	end

Route213_HotelLobby_Text_Clerk:
	.string "Route 213 Hotel--ocean on three\n"
	.string "sides and pillows on the fourth!$"

Route213_HotelLobby_EventScript_Sailor::
	msgbox Route213_HotelLobby_Text_Sailor, MSGBOX_NPC
	end

Route213_HotelLobby_Text_Sailor:
	.string "Shore leave never lasts long.\n"
	.string "I'll catch one more sunrise.$"
