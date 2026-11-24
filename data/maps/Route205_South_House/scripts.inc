Route205_South_House_MapScripts::
	.byte 0

Route205_South_House_EventScript_Healer::
	lock
	faceplayer
	msgbox Route205_South_House_Text_Rest, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	playfanfare MUS_PL_HEAL
	waitfanfare
	special HealPlayerParty
	fadescreen FADE_FROM_BLACK
	msgbox Route205_South_House_Text_Refreshed, MSGBOX_DEFAULT
	release
	end

Route205_South_House_Text_Rest:
	.string "You look worn out from the hills.\n"
	.string "Rest here a while.$"

Route205_South_House_Text_Refreshed:
	.string "There. You and your POKéMON look\n"
	.string "ready for the road again.\p"
	.string "Being young is no excuse to push\n"
	.string "yourself past your limits.$"
