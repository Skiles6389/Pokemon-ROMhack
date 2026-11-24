OreburghMine_B2F_MapScripts::
	.byte 0

@ Roark waits at the bottom of the mine, tells the player to come to the Gym,
OreburghMine_B2F_EventScript_Roark::
	lock
	faceplayer
	msgbox OreburghMine_B2F_Text_Roark, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_OREBURGH_MINE_ROARK
	setflag FLAG_HIDE_OREBURGH_MINE_ROARK
	setvar VAR_OREBURGH_STATE, 2
	fadescreen FADE_FROM_BLACK
	release
	end

OreburghMine_B2F_EventScript_Colin::
	trainerbattle_single TRAINER_WORKER_COLIN, OreburghMine_B2F_Text_ColinIntro, OreburghMine_B2F_Text_ColinDefeat
	msgbox OreburghMine_B2F_Text_ColinAfter, MSGBOX_AUTOCLOSE
	end

OreburghMine_B2F_EventScript_Mason::
	trainerbattle_single TRAINER_WORKER_MASON, OreburghMine_B2F_Text_MasonIntro, OreburghMine_B2F_Text_MasonDefeat
	msgbox OreburghMine_B2F_Text_MasonAfter, MSGBOX_AUTOCLOSE
	end

OreburghMine_B2F_EventScript_Worker::
	msgbox OreburghMine_B2F_Text_Worker, MSGBOX_NPC
	end

OreburghMine_B2F_Text_Roark:
	.string "Hm? A TRAINER, all the way down\n"
	.string "here? I'm ROARK, the GYM LEADER.\p"
	.string "I was clearing rubble with my\n"
	.string "POKéMON. Work comes first!\p"
	.string "You want a badge? Then come and\n"
	.string "challenge me at the OREBURGH GYM.\p"
	.string "I'll head up now. Don't keep me\n"
	.string "waiting too long!$"

OreburghMine_B2F_Text_ColinIntro:
	.string "My POKéMON dig all day. A battle\n"
	.string "is a nice break!$"

OreburghMine_B2F_Text_ColinDefeat:
	.string "Back to the coal face, I guess.$"

OreburghMine_B2F_Text_ColinAfter:
	.string "MACHOP can haul rocks bigger\n"
	.string "than you or me.$"

OreburghMine_B2F_Text_MasonIntro:
	.string "Hey! No visitors past this point…\n"
	.string "unless you can beat me!$"

OreburghMine_B2F_Text_MasonDefeat:
	.string "Okay, okay, go on through.$"

OreburghMine_B2F_Text_MasonAfter:
	.string "Careful, the floor's uneven down\n"
	.string "at the bottom.$"

OreburghMine_B2F_Text_Worker:
	.string "We're digging a new tunnel this\n"
	.string "way. Mind the loose rocks!$"
