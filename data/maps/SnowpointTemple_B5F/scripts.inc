SnowpointTemple_B5F_MapScripts::
	.byte 0


SnowpointTemple_B5F_EventScript_Regigigas::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_REGIGIGAS_TEMPLE, SnowpointTemple_B5F_EventScript_Regigigas_Gone
	msgbox SnowpointTemple_B5F_EventScript_Regigigas_Text, MSGBOX_DEFAULT
	setwildbattle SPECIES_REGIGIGAS, 70
	dowildbattle
	setflag FLAG_DEFEATED_REGIGIGAS_TEMPLE
	release
	end

SnowpointTemple_B5F_EventScript_Regigigas_Gone::
	msgbox SnowpointTemple_B5F_EventScript_Regigigas_GoneText, MSGBOX_DEFAULT
	release
	end

SnowpointTemple_B5F_EventScript_Regigigas_Text:
	.string "The colossal statue stirs...\n"
	.string "Regigigas awakens!$"

SnowpointTemple_B5F_EventScript_Regigigas_GoneText:
	.string "The pedestal is empty.$"
