Route213_MapScripts::
	.byte 0

Route213_EventScript_Jared::
	trainerbattle_single TRAINER_TUBER_JARED_R213, Route213_Text_JaredIntro, Route213_Text_JaredDefeat
	msgbox Route213_Text_JaredAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_JaredIntro:
	.string "Cannonball contest! Loser buys\n"
	.string "juice--winner gets bragging!$"

Route213_Text_JaredDefeat:
	.string "Splash... you win the splash!$"

Route213_Text_JaredAfter:
	.string "The tide's friendly today.\n"
	.string "Perfect for a rematch later!$"

Route213_EventScript_Chelsea::
	trainerbattle_single TRAINER_TUBER_CHELSEA_R213, Route213_Text_ChelseaIntro, Route213_Text_ChelseaDefeat
	msgbox Route213_Text_ChelseaAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_ChelseaIntro:
	.string "Sand in my shoes, salt in my\n"
	.string "hair--and a battle for fun!$"

Route213_Text_ChelseaDefeat:
	.string "Aww, wiped out...$"

Route213_Text_ChelseaAfter:
	.string "Pastoria's marsh is muddy, but\n"
	.string "this beach is pure sparkle!$"

Route213_EventScript_Shelton::
	trainerbattle_single TRAINER_SWIMMER_SHELTON_R213, Route213_Text_SheltonIntro, Route213_Text_SheltonDefeat
	msgbox Route213_Text_SheltonAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_SheltonIntro:
	.string "Laps before lunch!\n"
	.string "You're my warm-up partner!$"

Route213_Text_SheltonDefeat:
	.string "Pulled a muscle in my pride...$"

Route213_Text_SheltonAfter:
	.string "Keep kicking. Endurance wins\n"
	.string "long fights.$"

Route213_EventScript_Evan::
	trainerbattle_single TRAINER_SWIMMER_EVAN_R213, Route213_Text_EvanIntro, Route213_Text_EvanDefeat
	msgbox Route213_Text_EvanAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_EvanIntro:
	.string "Deep water, deep strategy!\n"
	.string "Let's dive into a match!$"

Route213_Text_EvanDefeat:
	.string "I sank under that pressure...$"

Route213_Text_EvanAfter:
	.string "Floatzel love this coastline.\n"
	.string "Watch the shallows!$"

Route213_EventScript_Mary::
	trainerbattle_single TRAINER_SWIMMER_MARY_R213, Route213_Text_MaryIntro, Route213_Text_MaryDefeat
	msgbox Route213_Text_MaryAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_MaryIntro:
	.string "Sun, surf, and a sharp Trainer!\n"
	.string "Don't make me chase you!$"

Route213_Text_MaryDefeat:
	.string "You rode that wave perfectly...$"

Route213_Text_MaryAfter:
	.string "Hotel guests cheer from the\n"
	.string "balcony. Put on a show!$"

Route213_EventScript_Haley::
	trainerbattle_single TRAINER_SWIMMER_HALEY_R213, Route213_Text_HaleyIntro, Route213_Text_HaleyDefeat
	msgbox Route213_Text_HaleyAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_HaleyIntro:
	.string "I timed my strokes for this!\n"
	.string "Ready when you are!$"

Route213_Text_HaleyDefeat:
	.string "Off-beat... nice tempo.$"

Route213_Text_HaleyAfter:
	.string "Cool down before the Gym.\n"
	.string "Wake hits hard and wet.$"

Route213_EventScript_Cyndy::
	trainerbattle_single TRAINER_BEAUTY_CYNDY_R213, Route213_Text_CyndyIntro, Route213_Text_CyndyDefeat
	msgbox Route213_Text_CyndyAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_CyndyIntro:
	.string "Beach fashion meets battle\n"
	.string "fashion. Strike a pose--then go!$"

Route213_Text_CyndyDefeat:
	.string "My look survived. My team didn't.$"

Route213_Text_CyndyAfter:
	.string "Dr. Footstep studies tracks in\n"
	.string "the sand. Say hello if you visit.$"

Route213_EventScript_Kenneth::
	trainerbattle_single TRAINER_FISHERMAN_KENNETH_R213, Route213_Text_KennethIntro, Route213_Text_KennethDefeat
	msgbox Route213_Text_KennethAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_KennethIntro:
	.string "Hook, line, and a challenger!\n"
	.string "Let's see who flops first!$"

Route213_Text_KennethDefeat:
	.string "Reeled in--and tossed back.$"

Route213_Text_KennethAfter:
	.string "Patience on the pier beats\n"
	.string "hurrying into Pastoria.$"

Route213_EventScript_Paul::
	trainerbattle_single TRAINER_SAILOR_PAUL_R213, Route213_Text_PaulIntro, Route213_Text_PaulDefeat
	msgbox Route213_Text_PaulAfter, MSGBOX_AUTOCLOSE
	end

Route213_Text_PaulIntro:
	.string "Shore leave means sparring!\n"
	.string "Permission to engage?$"

Route213_Text_PaulDefeat:
	.string "Aye... permission granted to you.$"

Route213_Text_PaulAfter:
	.string "Ships watch this coast for\n"
	.string "weather. Stay weather-ready!$"

Route213_EventScript_Beachgoer::
	msgbox Route213_Text_Beachgoer, MSGBOX_NPC
	end

Route213_Text_Beachgoer:
	.string "The hotel pool is nice, but the\n"
	.string "real ocean is right here!$"

Route213_EventScript_RouteSign::
	msgbox Route213_Text_RouteSign, MSGBOX_SIGN
	end

Route213_Text_RouteSign:
	.string "ROUTE 213\n"
	.string "Pastoria City - Valor Lakefront$"

Route213_EventScript_HotelSign::
	msgbox Route213_Text_HotelSign, MSGBOX_SIGN
	end

Route213_Text_HotelSign:
	.string "ROUTE 213 HOTEL\n"
	.string "Ocean views and soft pillows$"
Route213_EventScript_PlatNpc0::
	msgbox Route213_EventScript_PlatNpc0_Text, MSGBOX_NPC
	end

Route213_EventScript_PlatNpc0_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route213_EventScript_PlatNpc1::
	msgbox Route213_EventScript_PlatNpc1_Text, MSGBOX_NPC
	end

Route213_EventScript_PlatNpc1_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route213_EventScript_PlatNpc2::
	msgbox Route213_EventScript_PlatNpc2_Text, MSGBOX_NPC
	end

Route213_EventScript_PlatNpc2_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route213_EventScript_PlatNpc3::
	msgbox Route213_EventScript_PlatNpc3_Text, MSGBOX_NPC
	end

Route213_EventScript_PlatNpc3_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route213_EventScript_PlatNpc6::
	msgbox Route213_EventScript_PlatNpc6_Text, MSGBOX_NPC
	end

Route213_EventScript_PlatNpc6_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route213_EventScript_PlatNpc7::
	msgbox Route213_EventScript_PlatNpc7_Text, MSGBOX_NPC
	end

Route213_EventScript_PlatNpc7_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route213_EventScript_PlatNpc8::
	msgbox Route213_EventScript_PlatNpc8_Text, MSGBOX_NPC
	end

Route213_EventScript_PlatNpc8_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route213_EventScript_PlatNpc9::
	msgbox Route213_EventScript_PlatNpc9_Text, MSGBOX_NPC
	end

Route213_EventScript_PlatNpc9_Text:
	.string "These roads keep surprising me.\n"
	.string "Every corner hides another path.$"

Route213_EventScript_SwimmerSheltin::
	trainerbattle_single TRAINER_SWIMMER_SHELTIN, Route213_EventScript_SwimmerSheltin_Intro, Route213_EventScript_SwimmerSheltin_Defeat
	msgbox Route213_EventScript_SwimmerSheltin_After, MSGBOX_AUTOCLOSE
	end

Route213_EventScript_SwimmerSheltin_Intro:
	.string "Hold up! A battle will tell me how\n"
	.string "far you have come.$"

Route213_EventScript_SwimmerSheltin_Defeat:
	.string "That was cleaner than I expected.$"

Route213_EventScript_SwimmerSheltin_After:
	.string "Keep moving. Every route has a\n"
	.string "lesson if you look for it.$"

