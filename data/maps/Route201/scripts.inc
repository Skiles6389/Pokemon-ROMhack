Route201_MapScripts::
	.byte 0

Route201_EventScript_GrassWarning::
	msgbox Route201_Text_GrassWarning, MSGBOX_NPC
	end

Route201_EventScript_LakeSign::
	msgbox Route201_Text_LakeSign, MSGBOX_SIGN
	end

Route201_EventScript_SandgemSign::
	msgbox Route201_Text_SandgemSign, MSGBOX_SIGN
	end

Route201_Text_GrassWarning:
	.string "Hold on a second!\p"
	.string "The tall grass past me is no place\n"
	.string "to wander without a POKéMON.$"

Route201_Text_LakeSign:
	.string "WEST: LAKE VERITY\n"
	.string "The path is closed for now.$"

Route201_Text_SandgemSign:
	.string "EAST: SANDGEM TOWN\n"
	.string "The road is still unfinished.$"
