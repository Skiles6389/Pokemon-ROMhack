SunyshoreCity_Gym_Room2_MapScripts::
	.byte 0

SunyshoreCity_Gym_EventScript_Lonnie::
	trainerbattle_single TRAINER_GUITARIST_SUNY_B, SunyshoreCity_Gym_Text_LonnieIntro, SunyshoreCity_Gym_Text_LonnieDefeat
	msgbox SunyshoreCity_Gym_Text_LonnieAfter, MSGBOX_AUTOCLOSE
	end

SunyshoreCity_Gym_Text_LonnieIntro:
	.string "Amp it up!$"

SunyshoreCity_Gym_Text_LonnieDefeat:
	.string "Blown fuse...$"

SunyshoreCity_Gym_Text_LonnieAfter:
	.string "Volkner is just ahead.$"
