VeilstoneCity_GameCorner_MapScripts::
	.byte 0

VeilstoneCity_GameCorner_EventScript_Receptionist::
	msgbox VeilstoneCity_GameCorner_Text_Receptionist, MSGBOX_NPC
	end

VeilstoneCity_GameCorner_Text_Receptionist:
	.string "Welcome to the VEILSTONE GAME\n"
	.string "CORNER!\p"
	.string "The machines are being serviced,\n"
	.string "so we can't offer any games yet.\p"
	.string "Feel free to look around!$"

VeilstoneCity_GameCorner_EventScript_Woman::
	msgbox VeilstoneCity_GameCorner_Text_Woman, MSGBOX_NPC
	end

VeilstoneCity_GameCorner_Text_Woman:
	.string "I used to play here every\n"
	.string "evening. Now I just keep the\l"
	.string "seat warm.$"

VeilstoneCity_GameCorner_EventScript_Gentleman::
	msgbox VeilstoneCity_GameCorner_Text_Gentleman, MSGBOX_NPC
	end

VeilstoneCity_GameCorner_Text_Gentleman:
	.string "These machines were rattling long\n"
	.string "before the crews arrived. I\l"
	.string "wonder what's wrong with them.$"

VeilstoneCity_GameCorner_EventScript_Girl::
	msgbox VeilstoneCity_GameCorner_Text_Girl, MSGBOX_NPC
	end

VeilstoneCity_GameCorner_Text_Girl:
	.string "I'm saving up Coins for the\n"
	.string "Prize Exchange next door!$"

VeilstoneCity_GameCorner_EventScript_OldMan::
	msgbox VeilstoneCity_GameCorner_Text_OldMan, MSGBOX_NPC
	end

VeilstoneCity_GameCorner_Text_OldMan:
	.string "In my day we flipped a coin\n"
	.string "and called it fate.$"

VeilstoneCity_GameCorner_EventScript_Maniac::
	msgbox VeilstoneCity_GameCorner_Text_Maniac, MSGBOX_NPC
	end

VeilstoneCity_GameCorner_Text_Maniac:
	.string "They say TEAM GALACTIC stored\n"
	.string "crates in the warehouse near the\l"
	.string "plaza. Strange place for a prize!$"

VeilstoneCity_GameCorner_EventScript_Man::
	msgbox VeilstoneCity_GameCorner_Text_Man, MSGBOX_NPC
	end

VeilstoneCity_GameCorner_Text_Man:
	.string "No games today, and I still came.\n"
	.string "The jingle music is too good.$"

VeilstoneCity_GameCorner_EventScript_OutOfOrder::
	msgbox VeilstoneCity_GameCorner_Text_OutOfOrder, MSGBOX_SIGN
	end

VeilstoneCity_GameCorner_Text_OutOfOrder:
	.string "This machine is switched off for\n"
	.string "servicing.$"
