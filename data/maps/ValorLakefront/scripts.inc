ValorLakefront_MapScripts::
	.byte 0

ValorLakefront_EventScript_LakeComingSoon::
	lockall
	msgbox ValorLakefront_Text_LakeComingSoon, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, ValorLakefront_Movement_PushSouth
	waitmovement 0
	releaseall
	end

ValorLakefront_Movement_PushSouth:
	walk_down
	step_end

ValorLakefront_Text_LakeComingSoon:
	.string "Lake Valor and the Galactic\n"
	.string "storyline coming in a later\l"
	.string "milestone!$"

ValorLakefront_EventScript_EastWorker::
	msgbox ValorLakefront_Text_EastWorker, MSGBOX_NPC
	end

ValorLakefront_Text_EastWorker:
	.string "Route 222 and Sunyshore City\n"
	.string "coming in a later milestone!\p"
	.string "For now, the east path is closed.$"

ValorLakefront_EventScript_Tourist::
	msgbox ValorLakefront_Text_Tourist, MSGBOX_NPC
	end

ValorLakefront_Text_Tourist:
	.string "The lakefront breeze is perfect!\n"
	.string "I could sit here all afternoon.$"

ValorLakefront_EventScript_ResortMan::
	msgbox ValorLakefront_Text_ResortMan, MSGBOX_NPC
	end

ValorLakefront_Text_ResortMan:
	.string "Hotel, restaurant, cottages...\n"
	.string "This strip is Sinnoh's quiet gem.$"

ValorLakefront_EventScript_Kid::
	msgbox ValorLakefront_Text_Kid, MSGBOX_NPC
	end

ValorLakefront_Text_Kid:
	.string "I stamped my travel notebook at\n"
	.string "the hotel desk. Collect them all!$"

ValorLakefront_EventScript_OldWoman::
	msgbox ValorLakefront_Text_OldWoman, MSGBOX_NPC
	end

ValorLakefront_Text_OldWoman:
	.string "Years ago the lake shook once.\n"
	.string "Folks still talk about it softly.$"

ValorLakefront_EventScript_CookOutside::
	msgbox ValorLakefront_Text_CookOutside, MSGBOX_NPC
	end

ValorLakefront_Text_CookOutside:
	.string "Fresh catch special today!\n"
	.string "Come inside if you're hungry.$"

ValorLakefront_EventScript_ResortSign::
	msgbox ValorLakefront_Text_ResortSign, MSGBOX_SIGN
	end

ValorLakefront_Text_ResortSign:
	.string "VALOR LAKEFRONT\n"
	.string "A calm resort by the lake$"

ValorLakefront_EventScript_HotelSign::
	msgbox ValorLakefront_Text_HotelSign, MSGBOX_SIGN
	end

ValorLakefront_Text_HotelSign:
	.string "VALOR LAKEFRONT HOTEL\n"
	.string "Stamp your journey here!$"
