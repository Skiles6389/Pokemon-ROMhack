DistortionWorld_TurnbackCaveRoom_MapScripts::
	.byte 0

DistortionWorld_TurnbackCaveRoom_EventScript_Guide::
	lock
	faceplayer
	goto_if_set FLAG_DISTORTION_WORLD_CLEAR, DistortionWorld_TurnbackCaveRoom_EventScript_Open
	msgbox DistortionWorld_TurnbackCaveRoom_Text_Closed, MSGBOX_DEFAULT
	release
	end

DistortionWorld_TurnbackCaveRoom_EventScript_Open::
	msgbox DistortionWorld_TurnbackCaveRoom_Text_Open, MSGBOX_DEFAULT
	release
	end

DistortionWorld_TurnbackCaveRoom_Text_Closed:
	.string "The exit stays sealed until Giratina\n"
	.string "is settled deeper in.$"

DistortionWorld_TurnbackCaveRoom_Text_Open:
	.string "Sunyshore still waits for its Gym.\n"
	.string "Volkner is the last badge before the League.$"

