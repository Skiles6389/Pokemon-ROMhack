HearthomeCity_ContestLobby_MapScripts::
	.byte 0

HearthomeCity_ContestLobby_EventScript_Receptionist::
	msgbox HearthomeCity_ContestLobby_Text_Receptionist, MSGBOX_NPC
	end

HearthomeCity_ContestLobby_EventScript_Keira::
	msgbox HearthomeCity_ContestLobby_Text_Keira, MSGBOX_NPC
	end

HearthomeCity_ContestLobby_EventScript_Mom::
	msgbox HearthomeCity_ContestLobby_Text_Mom, MSGBOX_NPC
	end

HearthomeCity_ContestLobby_EventScript_Fan::
	msgbox HearthomeCity_ContestLobby_Text_Fan, MSGBOX_NPC
	end

HearthomeCity_ContestLobby_Text_Receptionist:
	.string "Welcome to the Super Contest Hall!\p"
	.string "Full Contest performances aren't open\n"
	.string "yet, but please enjoy the lobby!\p"
	.string "FANTINA often visits--she's both a\n"
	.string "Contest star and our Gym Leader!$"

HearthomeCity_ContestLobby_Text_Keira:
	.string "KEIRA: I'm studying Contest appeals.\p"
	.string "When the stage is ready, I'll teach\n"
	.string "you how to dazzle the judges!$"

HearthomeCity_ContestLobby_Text_Mom:
	.string "My child loves watching Contests.\n"
	.string "Hearthome feels so lively!$"

HearthomeCity_ContestLobby_Text_Fan:
	.string "I hope FANTINA dances on stage again.\n"
	.string "Her Ghost appeals are unforgettable!$"
