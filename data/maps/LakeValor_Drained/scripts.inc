LakeValor_Drained_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LakeValor_Drained_EventScript_CheckDrained
	.byte 0

LakeValor_Drained_EventScript_CheckDrained::
	end

LakeValor_Drained_EventScript_Attendant::
	msgbox LakeValor_Drained_Text, MSGBOX_NPC
	end

LakeValor_Drained_Text:
	.string "The water line dropped after the\n"
	.string "last shock from the crater.$"
