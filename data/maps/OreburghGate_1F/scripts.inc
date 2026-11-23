OreburghGate_1F_MapScripts::
	.byte 0

OreburghGate_1F_EventScript_Hiker::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_HM_ROCK_SMASH, OreburghGate_1F_EventScript_HikerAfter
	msgbox OreburghGate_1F_Text_HikerGive, MSGBOX_DEFAULT
	giveitem ITEM_HM_ROCK_SMASH
	setflag FLAG_RECEIVED_HM_ROCK_SMASH
	msgbox OreburghGate_1F_Text_HikerExplain, MSGBOX_DEFAULT
	release
	end

OreburghGate_1F_EventScript_HikerAfter::
	msgbox OreburghGate_1F_Text_HikerExplain, MSGBOX_DEFAULT
	release
	end

OreburghGate_1F_EventScript_Diana::
	trainerbattle_single TRAINER_PICNICKER_DIANA_GATE, OreburghGate_1F_Text_DianaIntro, OreburghGate_1F_Text_DianaDefeat
	msgbox OreburghGate_1F_Text_DianaAfter, MSGBOX_AUTOCLOSE
	end

OreburghGate_1F_EventScript_Curtis::
	trainerbattle_single TRAINER_CAMPER_CURTIS, OreburghGate_1F_Text_CurtisIntro, OreburghGate_1F_Text_CurtisDefeat
	msgbox OreburghGate_1F_Text_CurtisAfter, MSGBOX_AUTOCLOSE
	end

OreburghGate_1F_Text_HikerGive:
	.string "Breaking rocks is what I do best.\n"
	.string "Here, you take this too.$"

OreburghGate_1F_Text_HikerExplain:
	.string "That's ROCK SMASH. It cracks\n"
	.string "boulders right open.\p"
	.string "You'll need a GYM BADGE before you\n"
	.string "can use it outside of battle.$"

OreburghGate_1F_Text_DianaIntro:
	.string "A picnic in a cave is cozy.\n"
	.string "A battle in a cave is cozier!$"

OreburghGate_1F_Text_DianaDefeat:
	.string "Picnic's over.$"

OreburghGate_1F_Text_DianaAfter:
	.string "My BIDOOF likes the cool air in\n"
	.string "here. So do I.$"

OreburghGate_1F_Text_CurtisIntro:
	.string "I camp here so I can be first\n"
	.string "to battle anyone headed east!$"

OreburghGate_1F_Text_CurtisDefeat:
	.string "First to battle, first to lose.$"

OreburghGate_1F_Text_CurtisAfter:
	.string "OREBURGH is right through there.\n"
	.string "Mind the soot on your shoes!$"

