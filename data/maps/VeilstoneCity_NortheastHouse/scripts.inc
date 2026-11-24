VeilstoneCity_NortheastHouse_MapScripts::
	.byte 0

VeilstoneCity_NortheastHouse_EventScript_Programmer::
	lock
	faceplayer
	goto_if_set FLAG_GOT_VEILSTONE_PORYGON, VeilstoneCity_NortheastHouse_EventScript_ProgrammerAfter
	msgbox VeilstoneCity_NortheastHouse_Text_ProgrammerIntro, MSGBOX_DEFAULT
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_PORYGON
	givemon SPECIES_PORYGON, 25
	goto_if_eq VAR_RESULT, 0, VeilstoneCity_NortheastHouse_EventScript_GetPorygonParty
	goto_if_eq VAR_RESULT, 1, VeilstoneCity_NortheastHouse_EventScript_GetPorygonPC
	goto_if_eq VAR_RESULT, 2, Common_EventScript_NoMoreRoomForPokemon
	release
	end

VeilstoneCity_NortheastHouse_EventScript_GetPorygonParty::
	playfanfare MUS_OBTAIN_ITEM
	message VeilstoneCity_NortheastHouse_Text_ReceivedPorygon
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_PORYGON
	msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, VeilstoneCity_NortheastHouse_EventScript_SetGotPorygon
	call Common_EventScript_GetGiftMonPartySlot
	call Common_EventScript_NameReceivedPartyMon
	goto VeilstoneCity_NortheastHouse_EventScript_SetGotPorygon
	end

VeilstoneCity_NortheastHouse_EventScript_GetPorygonPC::
	playfanfare MUS_OBTAIN_ITEM
	message VeilstoneCity_NortheastHouse_Text_ReceivedPorygon
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_PORYGON
	msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, VeilstoneCity_NortheastHouse_EventScript_TransferPorygon
	call Common_EventScript_NameReceivedBoxMon
	goto VeilstoneCity_NortheastHouse_EventScript_TransferPorygon
	end

VeilstoneCity_NortheastHouse_EventScript_TransferPorygon::
	call Common_EventScript_TransferredToPC
	goto VeilstoneCity_NortheastHouse_EventScript_SetGotPorygon
	end

VeilstoneCity_NortheastHouse_EventScript_SetGotPorygon::
	setflag FLAG_GOT_VEILSTONE_PORYGON
	msgbox VeilstoneCity_NortheastHouse_Text_ProgrammerExplain, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_NortheastHouse_EventScript_ProgrammerAfter::
	msgbox VeilstoneCity_NortheastHouse_Text_ProgrammerAfter, MSGBOX_DEFAULT
	release
	end

VeilstoneCity_NortheastHouse_EventScript_Girl::
	msgbox VeilstoneCity_NortheastHouse_Text_Girl, MSGBOX_NPC
	end

VeilstoneCity_NortheastHouse_Text_Girl:
	.string "Daddy built a POKéMON out of\n"
	.string "numbers! Isn't that silly?$"

VeilstoneCity_NortheastHouse_Text_ProgrammerIntro:
	.string "Ah, a visitor! Perfect timing.\p"
	.string "I write programs for a living, and\n"
	.string "my latest project grew a little\l"
	.string "too clever for my apartment.\p"
	.string "Would you take it off my hands?\n"
	.string "It's a digital POKéMON called\l"
	.string "PORYGON. Please treat it kindly!$"

VeilstoneCity_NortheastHouse_Text_ReceivedPorygon:
	.string "{PLAYER} received PORYGON!$"

VeilstoneCity_NortheastHouse_Text_ProgrammerExplain:
	.string "PORYGON can copy itself into\n"
	.string "just about any data.\p"
	.string "It's a little odd, but it's loyal.\n"
	.string "Look after it for me!$"

VeilstoneCity_NortheastHouse_Text_ProgrammerAfter:
	.string "How's PORYGON doing? I hope it\n"
	.string "isn't getting lonely in there.$"
