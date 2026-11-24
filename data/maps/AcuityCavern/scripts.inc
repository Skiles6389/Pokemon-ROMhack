AcuityCavern_MapScripts::
	.byte 0


AcuityCavern_EventScript_Uxie::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_UXIE_ACUITY, AcuityCavern_EventScript_Uxie_Gone
	msgbox AcuityCavern_EventScript_Uxie_Text, MSGBOX_DEFAULT
	setwildbattle SPECIES_UXIE, 50
	dowildbattle
	setflag FLAG_DEFEATED_UXIE_ACUITY
	release
	end

AcuityCavern_EventScript_Uxie_Gone::
	msgbox AcuityCavern_EventScript_Uxie_GoneText, MSGBOX_DEFAULT
	release
	end

AcuityCavern_EventScript_Uxie_Text:
	.string "A knowing gaze pierces the dark...\n"
	.string "Uxie appears!$"

AcuityCavern_EventScript_Uxie_GoneText:
	.string "Only ripples remain on the cavern floor.$"
