RuinManiacCave_MapScripts::
	.byte 0

RuinManiacCave_EventScript_Attendant::
	lock
	faceplayer
	goto_if_eq VAR_RUIN_MANIAC_STAGE, 2, RuinManiacCave_EventScript_TalkTunnel
	goto_if_eq VAR_RUIN_MANIAC_STAGE, 1, RuinManiacCave_EventScript_TalkLong
	msgbox RuinManiacCave_Text_Short, MSGBOX_DEFAULT
	msgbox RuinManiacCave_Text_Expand, MSGBOX_DEFAULT
	setvar VAR_RUIN_MANIAC_STAGE, 1
	warp MAP_RUIN_MANIAC_CAVE_LONG, 20, 13
	waitstate
	release
	end

RuinManiacCave_EventScript_TalkLong::
	msgbox RuinManiacCave_Text_Long, MSGBOX_DEFAULT
	setvar VAR_RUIN_MANIAC_STAGE, 2
	warp MAP_MANIAC_TUNNEL, 20, 13
	waitstate
	release
	end

RuinManiacCave_EventScript_TalkTunnel::
	msgbox RuinManiacCave_Text_Tunnel, MSGBOX_DEFAULT
	release
	end

RuinManiacCave_Text_Short:
	.string "I am digging toward the ruins.\n"
	.string "Stay close and I will show you the\l"
	.string "next stretch of tunnel.$"

RuinManiacCave_Text_Expand:
	.string "There! A longer path just opened.$"

RuinManiacCave_Text_Long:
	.string "One more blast and the maniac tunnel\n"
	.string "will connect all the way through.$"

RuinManiacCave_Text_Tunnel:
	.string "The maniac tunnel is finished.\n"
	.string "Watch your step in the dark.$"
