Route206_MapScripts::
	.byte 0

Route206_EventScript_Axel::
	trainerbattle_single TRAINER_CYCLIST_AXEL_R206, Route206_Text_AxelIntro, Route206_Text_AxelDefeat
	msgbox Route206_Text_AxelAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_AxelIntro:
	.string "Yo! Cycling and POKéMON!\n"
	.string "Which do you prefer?$"

Route206_Text_AxelDefeat:
	.string "Hey, not bad, you!$"

Route206_Text_AxelAfter:
	.string "This Cycling Road is one fine place--\n"
	.string "great bikes, superb POKéMON,\p"
	.string "and awesome Trainers all around!$"

Route206_EventScript_Megan::
	trainerbattle_single TRAINER_CYCLIST_MEGAN_R206, Route206_Text_MeganIntro, Route206_Text_MeganDefeat
	msgbox Route206_Text_MeganAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_MeganIntro:
	.string "Cycling feels great!\n"
	.string "It will feel even better when I beat\p"
	.string "you in a battle!$"

Route206_Text_MeganDefeat:
	.string "Whew!\n"
	.string "You worked us over.$"

Route206_Text_MeganAfter:
	.string "I like spinning the pedals backward\n"
	.string "while sailing downhill.$"

Route206_EventScript_James::
	trainerbattle_single TRAINER_CYCLIST_JAMES_R206, Route206_Text_JamesIntro, Route206_Text_JamesDefeat
	msgbox Route206_Text_JamesAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_JamesIntro:
	.string "Ding-ding! Watch out, you!\n"
	.string "Or, did you want to battle?$"

Route206_Text_JamesDefeat:
	.string "Despite all the effort, I'm just spinning\n"
	.string "my wheels...\p"
	.string "It's always that way with me!$"

Route206_Text_JamesAfter:
	.string "I might try racing through Cycling\n"
	.string "Road in one long shot.$"

Route206_EventScript_Nicole::
	trainerbattle_single TRAINER_CYCLIST_NICOLE_R206, Route206_Text_NicoleIntro, Route206_Text_NicoleDefeat
	msgbox Route206_Text_NicoleAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_NicoleIntro:
	.string "The both of us are on Bikes, and we\n"
	.string "both have POKéMON!\p"
	.string "I can't let you get the better of me!$"

Route206_Text_NicoleDefeat:
	.string "Oh, geez...\n"
	.string "I seem to have fallen off my Bike.$"

Route206_Text_NicoleAfter:
	.string "I should have challenged you to a race,\n"
	.string "not a battle!$"

Route206_EventScript_John::
	trainerbattle_single TRAINER_CYCLIST_JOHN_R206, Route206_Text_JohnIntro, Route206_Text_JohnDefeat
	msgbox Route206_Text_JohnAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_JohnIntro:
	.string "That Bike you've got there...it's the\n"
	.string "type that can change gears!\p"
	.string "You gotta love that!\n"
	.string "Sure, I'll give you a battle!$"

Route206_Text_JohnDefeat:
	.string "Crash! Tinkle...$"

Route206_Text_JohnAfter:
	.string "The 3-speed makes for easy turning,\n"
	.string "and the 4-speed's for going fast.\p"
	.string "I love them both!$"

Route206_EventScript_Kayla::
	trainerbattle_single TRAINER_CYCLIST_KAYLA_R206, Route206_Text_KaylaIntro, Route206_Text_KaylaDefeat
	msgbox Route206_Text_KaylaAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_KaylaIntro:
	.string "If you beat me, you can count on\n"
	.string "something rotten coming your way!$"

Route206_Text_KaylaDefeat:
	.string "Kerrrash!$"

Route206_Text_KaylaAfter:
	.string "Aww!\n"
	.string "Why did you beat me?!\p"
	.string "I hope you get so lost in Wayward Cave\n"
	.string "you cry! Boo-hoo-hoo!$"

Route206_EventScript_Ryan::
	trainerbattle_single TRAINER_CYCLIST_RYAN_R206, Route206_Text_RyanIntro, Route206_Text_RyanDefeat
	msgbox Route206_Text_RyanAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_RyanIntro:
	.string "A bike will carry you a long way.\n"
	.string "The only thing that limits you is your\p"
	.string "own endurance!$"

Route206_Text_RyanDefeat:
	.string "Gasp... Gasp... Gasp...$"

Route206_Text_RyanAfter:
	.string "My POKéMON and I are plumb worn out.\n"
	.string "We should be getting home to rest...$"

Route206_EventScript_Rachel::
	trainerbattle_single TRAINER_CYCLIST_RACHEL_R206, Route206_Text_RachelIntro, Route206_Text_RachelDefeat
	msgbox Route206_Text_RachelAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_RachelIntro:
	.string "Some people compete over speed, and\n"
	.string "some compete over technique.\p"
	.string "Which kind are you?$"

Route206_Text_RachelDefeat:
	.string "You're a speedy technician!$"

Route206_Text_RachelAfter:
	.string "I enjoy the scenery.\n"
	.string "Don't you think the area below\p"
	.string "Cycling Road looks nice?$"

Route206_EventScript_Theodore::
	trainerbattle_single TRAINER_HIKER_THEODORE_R206, Route206_Text_TheodoreIntro, Route206_Text_TheodoreDefeat
	msgbox Route206_Text_TheodoreAfter, MSGBOX_AUTOCLOSE
	end

Route206_Text_TheodoreIntro:
	.string "Whoa! You startled me!\n"
	.string "Well, we may as well battle!$"

Route206_Text_TheodoreDefeat:
	.string "Your power startles me!$"

Route206_Text_TheodoreAfter:
	.string "We Hikers are bighearted guys!\n"
	.string "Losing doesn't bother us!$"


Route206_EventScript_WaywardHiker::
	msgbox Route206_Text_WaywardHiker, MSGBOX_NPC
	end

Route206_EventScript_WaywardCaveGate::
	lockall
	msgbox Route206_Text_WaywardCaveClosed, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkDown
	waitmovement 0
	releaseall
	end

Route206_EventScript_PoisonBarb::
	finditem ITEM_POISON_BARB
	end

Route206_EventScript_PPUp::
	finditem ITEM_PP_UP
	end

Route206_EventScript_SignEterna::
	msgbox Route206_Text_SignEterna, MSGBOX_SIGN
	end

Route206_EventScript_SignOreburgh::
	msgbox Route206_Text_SignOreburgh, MSGBOX_SIGN
	end

Route206_Text_WaywardHiker:
	.string "This is odd... I heard there were two\n"
	.string "caves on Route 206.\pBut I can only find one entrance.$"
Route206_Text_WaywardCaveClosed:
	.string "WAYWARD CAVE\n"
	.string "Coming in a later milestone!$"
Route206_Text_SignEterna:
	.string "Rt. 206\n"
	.string "Eterna City$"
Route206_Text_SignOreburgh:
	.string "Rt. 206\n"
	.string "Oreburgh City$"
