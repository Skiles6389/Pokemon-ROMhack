HearthomeCity_BebesHouse_MapScripts::
	.byte 0

HearthomeCity_BebesHouse_EventScript_Bebe::
	lock
	faceplayer
	goto_if_set FLAG_GOT_BEBE_EEVEE, HearthomeCity_BebesHouse_EventScript_BebeAfter
	msgbox HearthomeCity_BebesHouse_Text_BebeIntro, MSGBOX_DEFAULT
	setvar VAR_TEMP_1, SPECIES_EEVEE
	givemon SPECIES_EEVEE, 20
	goto_if_eq VAR_RESULT, 0, HearthomeCity_BebesHouse_EventScript_GetEeveeParty
	goto_if_eq VAR_RESULT, 1, HearthomeCity_BebesHouse_EventScript_GetEeveePC
	goto_if_eq VAR_RESULT, 2, Common_EventScript_NoMoreRoomForPokemon
	release
	end

HearthomeCity_BebesHouse_EventScript_GetEeveeParty::
	playfanfare MUS_OBTAIN_ITEM
	message HearthomeCity_BebesHouse_Text_ReceivedEevee
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_EEVEE
	msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, HearthomeCity_BebesHouse_EventScript_SetGotEevee
	call Common_EventScript_GetGiftMonPartySlot
	call Common_EventScript_NameReceivedPartyMon
	goto HearthomeCity_BebesHouse_EventScript_SetGotEevee
	end

HearthomeCity_BebesHouse_EventScript_GetEeveePC::
	playfanfare MUS_OBTAIN_ITEM
	message HearthomeCity_BebesHouse_Text_ReceivedEevee
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_EEVEE
	msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, HearthomeCity_BebesHouse_EventScript_TransferEevee
	call Common_EventScript_NameReceivedBoxMon
	goto HearthomeCity_BebesHouse_EventScript_TransferEevee
	end

HearthomeCity_BebesHouse_EventScript_TransferEevee::
	call Common_EventScript_TransferredToPC
	goto HearthomeCity_BebesHouse_EventScript_SetGotEevee
	end

HearthomeCity_BebesHouse_EventScript_SetGotEevee::
	setflag FLAG_GOT_BEBE_EEVEE
	msgbox HearthomeCity_BebesHouse_Text_BebeCare, MSGBOX_DEFAULT
	release
	end

HearthomeCity_BebesHouse_EventScript_BebeAfter::
	msgbox HearthomeCity_BebesHouse_Text_BebeAfter, MSGBOX_DEFAULT
	release
	end

HearthomeCity_BebesHouse_EventScript_Child::
	msgbox HearthomeCity_BebesHouse_Text_Child, MSGBOX_NPC
	end

HearthomeCity_BebesHouse_Text_BebeIntro:
	.string "BEBE: Welcome!\p"
	.string "I raise EEVEE with all my heart.\n"
	.string "You look like a kind Trainer...\p"
	.string "Please take this EEVEE!\n"
	.string "Raise it with love!$"

HearthomeCity_BebesHouse_Text_ReceivedEevee:
	.string "{PLAYER} received an EEVEE!$"

HearthomeCity_BebesHouse_Text_BebeCare:
	.string "BEBE: Friendship changes EEVEE's\n"
	.string "future. Take good care of it!$"

HearthomeCity_BebesHouse_Text_BebeAfter:
	.string "BEBE: How is EEVEE doing?\n"
	.string "I hope you're the best of friends!$"

HearthomeCity_BebesHouse_Text_Child:
	.string "Mom's EEVEE is so soft!\n"
	.string "I want one when I grow up!$"
