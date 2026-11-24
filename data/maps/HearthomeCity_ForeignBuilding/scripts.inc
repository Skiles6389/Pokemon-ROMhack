HearthomeCity_ForeignBuilding_MapScripts::
	.byte 0

HearthomeCity_ForeignBuilding_EventScript_Elder::
	msgbox HearthomeCity_ForeignBuilding_Text_Elder, MSGBOX_NPC
	end

HearthomeCity_ForeignBuilding_EventScript_Woman::
	msgbox HearthomeCity_ForeignBuilding_Text_Woman, MSGBOX_NPC
	end

HearthomeCity_ForeignBuilding_Text_Elder:
	.string "This hall is for quiet thoughts.\p"
	.string "Sit a while. Let your journey settle\n"
	.string "like dust in a sunbeam.$"

HearthomeCity_ForeignBuilding_Text_Woman:
	.string "I come here when battles grow loud.\n"
	.string "Silence helps me hear my POKéMON.$"
