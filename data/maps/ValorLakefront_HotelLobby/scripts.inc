ValorLakefront_HotelLobby_MapScripts::
	.byte 0

ValorLakefront_HotelLobby_EventScript_Clerk::
	msgbox ValorLakefront_HotelLobby_Text_Clerk, MSGBOX_NPC
	end

ValorLakefront_HotelLobby_Text_Clerk:
	.string "Welcome to Valor Lakefront Hotel!\p"
	.string "Stamp your travel log at the desk\n"
	.string "and enjoy the lake breeze.$"

ValorLakefront_HotelLobby_EventScript_Guest::
	msgbox ValorLakefront_HotelLobby_Text_Guest, MSGBOX_NPC
	end

ValorLakefront_HotelLobby_Text_Guest:
	.string "I collected stamps from every\n"
	.string "Sinnoh stop so far. This one's\l"
	.string "my favorite ink color!$"
