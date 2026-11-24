Route205_South_MapScripts::
	.byte 0

Route205_South_EventScript_Daniel::
	trainerbattle_single TRAINER_HIKER_DANIEL, Route205_South_Text_DanielIntro, Route205_South_Text_DanielDefeat
	msgbox Route205_South_Text_DanielAfter, MSGBOX_AUTOCLOSE
	end

Route205_South_EventScript_Elizabeth::
	trainerbattle_single TRAINER_AROMA_ELIZABETH, Route205_South_Text_ElizabethIntro, Route205_South_Text_ElizabethDefeat
	msgbox Route205_South_Text_ElizabethAfter, MSGBOX_AUTOCLOSE
	end

Route205_South_EventScript_Jacob::
	trainerbattle_single TRAINER_CAMPER_JACOB, Route205_South_Text_JacobIntro, Route205_South_Text_JacobDefeat
	msgbox Route205_South_Text_JacobAfter, MSGBOX_AUTOCLOSE
	end

Route205_South_EventScript_Siena::
	trainerbattle_single TRAINER_PICNICKER_SIENA, Route205_South_Text_SienaIntro, Route205_South_Text_SienaDefeat
	msgbox Route205_South_Text_SienaAfter, MSGBOX_AUTOCLOSE
	end

Route205_South_EventScript_Nicholas::
	trainerbattle_single TRAINER_HIKER_NICHOLAS, Route205_South_Text_NicholasIntro, Route205_South_Text_NicholasDefeat
	msgbox Route205_South_Text_NicholasAfter, MSGBOX_AUTOCLOSE
	end

Route205_South_EventScript_Kelsey::
	trainerbattle_single TRAINER_BATTLE_GIRL_KELSEY, Route205_South_Text_KelseyIntro, Route205_South_Text_KelseyDefeat
	msgbox Route205_South_Text_KelseyAfter, MSGBOX_AUTOCLOSE
	end

Route205_South_EventScript_Karina::
	trainerbattle_single TRAINER_PICNICKER_KARINA, Route205_South_Text_KarinaIntro, Route205_South_Text_KarinaDefeat
	msgbox Route205_South_Text_KarinaAfter, MSGBOX_AUTOCLOSE
	end

Route205_South_EventScript_Zackary::
	trainerbattle_single TRAINER_CAMPER_ZACKARY, Route205_South_Text_ZackaryIntro, Route205_South_Text_ZackaryDefeat
	msgbox Route205_South_Text_ZackaryAfter, MSGBOX_AUTOCLOSE
	end

Route205_South_EventScript_BugCatcher::
	msgbox Route205_South_Text_BugCatcher, MSGBOX_NPC
	end

Route205_South_EventScript_LittleGirl::
	goto_if_set FLAG_GOT_WORKS_KEY, Route205_South_EventScript_LittleGirlAfterKey
	msgbox Route205_South_Text_LittleGirlHelp, MSGBOX_NPC
	setvar VAR_VALLEY_WINDWORKS_STATE, 1
	end

Route205_South_EventScript_LittleGirlAfterKey::
	msgbox Route205_South_Text_LittleGirlPleaseHurry, MSGBOX_NPC
	setvar VAR_VALLEY_WINDWORKS_STATE, 1
	end

Route205_South_EventScript_ForestGrunts::
	msgbox Route205_South_Text_ForestGruntBlock, MSGBOX_NPC
	end

Route205_South_EventScript_ForestGruntTrigger::
	goto_if_set FLAG_HIDE_ROUTE205_FOREST_GRUNTS, Route205_South_EventScript_ForestGruntTriggerEnd
	lockall
	playbgm MUS_PL_ENCOUNTER_GALACTIC, FALSE
	applymovement LOCALID_R205_GRUNT_WEST, Common_Movement_ExclamationMark
	applymovement LOCALID_R205_GRUNT_EAST, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox Route205_South_Text_ForestGruntBlock, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route205_South_Movement_PushSouth
	waitmovement 0
	fadedefaultbgm
	releaseall
Route205_South_EventScript_ForestGruntTriggerEnd::
	end

Route205_South_Movement_PushSouth:
	walk_down
	step_end

Route205_South_EventScript_EternaGate::
	msgbox Route205_South_Text_EternaGate, MSGBOX_NPC
	end

Route205_South_EventScript_EternaGateTrigger::
	lockall
	msgbox Route205_South_Text_EternaGate, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route205_South_Movement_PushSouth
	waitmovement 0
	releaseall
	end

Route205_South_EventScript_HealBall::
	finditem ITEM_HEAL_BALL
	end

Route205_South_EventScript_XSpDef::
	finditem ITEM_X_SP_DEF
	end

Route205_South_EventScript_SuperPotion::
	finditem ITEM_SUPER_POTION
	end

Route205_South_EventScript_Repel::
	finditem ITEM_REPEL
	end

Route205_South_EventScript_SignFloaroma::
	msgbox Route205_South_Text_SignFloaroma, MSGBOX_SIGN
	end

Route205_South_EventScript_SignEterna::
	msgbox Route205_South_Text_SignEterna, MSGBOX_SIGN
	end

Route205_South_EventScript_TrainerTips::
	msgbox Route205_South_Text_TrainerTips, MSGBOX_SIGN
	end

Route205_South_Text_DanielIntro:
	.string "These slopes chew up soft shoes.\n"
	.string "Let's see if your team can climb!$"

Route205_South_Text_DanielDefeat:
	.string "I slipped... and so did my strategy.$"

Route205_South_Text_DanielAfter:
	.string "Pack sturdy boots if you're heading\n"
	.string "toward Eterna Forest.$"

Route205_South_Text_ElizabethIntro:
	.string "Smell that breeze? My ROSELIA loves\n"
	.string "Route 205's flowers. Battle me!$"

Route205_South_Text_ElizabethDefeat:
	.string "Even sweet petals wilt sometimes.$"

Route205_South_Text_ElizabethAfter:
	.string "Try a Berry if the pollen gets to you.$"

Route205_South_Text_JacobIntro:
	.string "Campfire's warm, but a battle's warmer!$"

Route205_South_Text_JacobDefeat:
	.string "Guess I need more kindling...$"

Route205_South_Text_JacobAfter:
	.string "The Windworks lights the valley at night.\n"
	.string "Pretty, until the wrong people show up.$"

Route205_South_Text_SienaIntro:
	.string "Picnic's packed. Now for dessert-\n"
	.string "a quick battle!$"

Route205_South_Text_SienaDefeat:
	.string "My lunch tasted better than that...$"

Route205_South_Text_SienaAfter:
	.string "Share a sandwich sometime?$"

Route205_South_Text_NicholasIntro:
	.string "ONIX and I train on every ledge here!$"

Route205_South_Text_NicholasDefeat:
	.string "Rock-hard defense... soft results.$"

Route205_South_Text_NicholasAfter:
	.string "Watch your step on the northern stairs.$"

Route205_South_Text_KelseyIntro:
	.string "Fist bumps first. Battles second!$"

Route205_South_Text_KelseyDefeat:
	.string "Ow. Respect.$"

Route205_South_Text_KelseyAfter:
	.string "Strength isn't only muscles.\n"
	.string "You proved that.$"

Route205_South_Text_KarinaIntro:
	.string "My PIPLUP insisted we challenge you!$"

Route205_South_Text_KarinaDefeat:
	.string "PIPLUP... we'll train harder.$"

Route205_South_Text_KarinaAfter:
	.string "Water-types shine near the bridge.$"

Route205_South_Text_ZackaryIntro:
	.string "AIPOM, show them those hands!$"

Route205_South_Text_ZackaryDefeat:
	.string "We got outplayed...$"

Route205_South_Text_ZackaryAfter:
	.string "If you see Galactic uniforms, keep clear.$"

Route205_South_Text_BugCatcher:
	.string "Eterna Forest is thick with bugs...\n"
	.string "and rumors about Team Galactic.$"

Route205_South_Text_LittleGirlHelp:
	.string "Please help! Spacemen pushed me out of\n"
	.string "Valley Windworks and kept my papa!\p"
	.string "They're making him work the turbines.\n"
	.string "I just want him home...$"

Route205_South_Text_LittleGirlPleaseHurry:
	.string "You have a key? Then hurry!\n"
	.string "Papa's still inside the Windworks!$"

Route205_South_Text_ForestGruntBlock:
	.string "GRUNT: Team Galactic's busy ahead.\n"
	.string "Eterna Forest is off-limits, brat!\p"
	.string "Clear out--unless you fancy a beating.$"

Route205_South_Text_EternaGate:
	.string "Eterna Forest lies ahead.\n"
	.string "Watch your step in the shade.$"

Route205_South_Text_SignFloaroma:
	.string "ROUTE 205\n"
	.string "West to Floaroma Town$"

Route205_South_Text_SignEterna:
	.string "ROUTE 205\n"
	.string "North to Eterna Forest$"

Route205_South_Text_TrainerTips:
	.string "TRAINER TIPS!\p"
	.string "Items in your BAG sort themselves into\n"
	.string "the right pockets. Handy on long walks!$"
