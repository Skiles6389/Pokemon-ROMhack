EternaCity_Condo_MapScripts::
	.byte 0

EternaCity_Condo_EventScript_NameRater::
	lock
	faceplayer
	msgbox EternaCity_Condo_Text_NameRaterOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, EternaCity_Condo_EventScript_ChooseMon
	msgbox EternaCity_Condo_Text_Decline, MSGBOX_DEFAULT
	release
	end

EternaCity_Condo_EventScript_ChooseMon::
	msgbox EternaCity_Condo_Text_WhichMon, MSGBOX_DEFAULT
	chooseboxmon
	waitstate
	goto_if_eq VAR_0x8004, PARTY_NOTHING_CHOSEN, EternaCity_Condo_EventScript_Decline
	call Common_EventScript_NameReceivedPartyMon
	msgbox EternaCity_Condo_Text_Happy, MSGBOX_DEFAULT
	release
	end

EternaCity_Condo_Text_NameRaterOffer:
	.string "I rate nicknames. Would you like\n"
	.string "my opinion?$"

EternaCity_Condo_Text_WhichMon:
	.string "Which POKéMON's nickname?$"

EternaCity_Condo_Text_Happy:
	.string "A fine bond deserves a fine name!$"

EternaCity_Condo_EventScript_Decline::
	msgbox EternaCity_Condo_Text_Decline, MSGBOX_DEFAULT
	release
	end

EternaCity_Condo_Text_Decline:
	.string "Visit anytime.$"
