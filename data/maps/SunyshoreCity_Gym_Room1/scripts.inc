SunyshoreCity_Gym_Room1_MapScripts::
	.byte 0

SunyshoreCity_Gym_EventScript_Jerry::
	trainerbattle_single TRAINER_GUITARIST_SUNY_A, SunyshoreCity_Gym_Text_JerryIntro, SunyshoreCity_Gym_Text_JerryDefeat
	msgbox SunyshoreCity_Gym_Text_JerryAfter, MSGBOX_AUTOCLOSE
	end

SunyshoreCity_Gym_EventScript_Guide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE08_GET, SunyshoreCity_Gym_EventScript_GuideWon
	msgbox SunyshoreCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

SunyshoreCity_Gym_EventScript_GuideWon::
	msgbox SunyshoreCity_Gym_Text_GuideWon, MSGBOX_DEFAULT
	release
	end

SunyshoreCity_Gym_Text_JerryIntro:
	.string "Feel that bass drop?\n"
	.string "Electric types love the beat!$"

SunyshoreCity_Gym_Text_JerryDefeat:
	.string "Unplugged...$"

SunyshoreCity_Gym_Text_JerryAfter:
	.string "Volkner is upstairs in the last room.$"

SunyshoreCity_Gym_Text_GuideAdvice:
	.string "Volkner thrives on Electric-type pressure.\n"
	.string "Ground moves cut the circuit.$"

SunyshoreCity_Gym_Text_GuideWon:
	.string "Beacon Badge earned!\n"
	.string "Victory Road is next along Route 223.$"
