Route213_DrFootstepHouse_MapScripts::
	.byte 0

Route213_DrFootstepHouse_EventScript_DrFootstep::
	lock
	faceplayer
	msgbox Route213_DrFootstepHouse_Text_DrFootstep, MSGBOX_DEFAULT
	release
	end

Route213_DrFootstepHouse_Text_DrFootstep:
	.string "DR. FOOTSTEP: Footprints tell\n"
	.string "stories sand can't keep secret.\p"
	.string "A happy POKéMON leaves a light,\n"
	.string "bouncy track. A worried one digs\l"
	.string "deeper prints.\p"
	.string "Walk together often--friendship\n"
	.string "shows in every step!$"
