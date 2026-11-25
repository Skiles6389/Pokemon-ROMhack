VerityLakefront_MapScripts::
	.byte 0

VerityLakefront_EventScript_Sign::
	msgbox VerityLakefront_Text_Sign, MSGBOX_SIGN
	end

@ Platinum's lake-entrance trigger (4..5,4): during the opening (state 1)
@ Barry calls out from inside the trees, then the player walks on north.
VerityLakefront_EventScript_LakeEntrance::
	lockall
	msgbox VerityLakefront_Text_LakeEntrance, MSGBOX_DEFAULT
	closemessage
	releaseall
	end

VerityLakefront_Text_Sign:
	.string "Lake Verity ahead.$"

VerityLakefront_Text_LakeEntrance:
	.string "A voice carries through the trees...\p"
	.string "BARRY: {PLAYER}! The lake's right\n"
	.string "through here! Hurry up!$"
