LakeValor_Stub_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, LakeValor_Stub_MapScripts_FrameTable
	.byte 0

LakeValor_Stub_MapScripts_FrameTable:
	map_script_2 VAR_TEMP_0, 0, LakeValor_Stub_EventScript_RouteState
	.2byte 0

LakeValor_Stub_EventScript_RouteState::
	setvar VAR_TEMP_0, 1
	goto_if_set FLAG_LAKE_VALOR_DRAINED, LakeValor_Stub_EventScript_ToDrained
	warp MAP_LAKE_VALOR_NORMAL, 20, 13
	waitstate
	end

LakeValor_Stub_EventScript_ToDrained::
	warp MAP_LAKE_VALOR_DRAINED, 20, 13
	waitstate
	end

LakeValor_Stub_EventScript_Attendant::
	msgbox LakeValor_Stub_Text_Attendant, MSGBOX_NPC
	end

LakeValor_Stub_Text_Attendant:
	.string "This shore leads into Lake Valor.\n"
	.string "The water line changes with the news.$"
