Route208_BerryMastersHouse_MapScripts::
	.byte 0

Route208_BerryMastersHouse_EventScript_BerryMaster::
	lock
	faceplayer
	dotimebasedevents
	goto_if_set FLAG_DAILY_BERRY_MASTER_RECEIVED_BERRY, Route208_BerryMastersHouse_EventScript_ReceivedToday
	msgbox Route208_BerryMastersHouse_Text_DeserveBerry, MSGBOX_DEFAULT
	giverandomberry BERRY_ID_CHERI, BERRY_ID_SITRUS
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_DAILY_BERRY_MASTER_RECEIVED_BERRY
	msgbox Route208_BerryMastersHouse_Text_FeedBerries, MSGBOX_DEFAULT
	release
	end

Route208_BerryMastersHouse_EventScript_ReceivedToday::
	msgbox Route208_BerryMastersHouse_Text_FeedBerries, MSGBOX_DEFAULT
	release
	end

Route208_BerryMastersHouse_EventScript_Wife::
	msgbox Route208_BerryMastersHouse_Text_Wife, MSGBOX_NPC
	end

Route208_BerryMastersHouse_Text_DeserveBerry:
	.string "Everyone seems to call me the Berry\n"
	.string "Master.\pI hand out Berries daily because\p"
	.string "I want people to learn how wonderful\lthey are.\pYou're deserving of one!$"
Route208_BerryMastersHouse_Text_FeedBerries:
	.string "Berries are gifts of nature.\pI encourage you to feed Berries to\n"
	.string "POKéMON.\pThat will make POKéMON happy.\p"
	.string "Seeing that, people will be motivated\lto plant more Berries.\pAnd that will make Sinnoh a greener,\n"
	.string "more natural place.$"
Route208_BerryMastersHouse_Text_Wife:
	.string "My husband loves Berries so much.\n"
	.string "He gives them away every day!$"
