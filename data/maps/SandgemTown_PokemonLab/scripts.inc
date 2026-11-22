SandgemTown_PokemonLab_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SandgemTown_PokemonLab_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SandgemTown_PokemonLab_OnFrame
	.byte 0

SandgemTown_PokemonLab_OnTransition:
	call SandgemTown_EventScript_SetAssistantGfx
	end

SandgemTown_PokemonLab_OnFrame:
	map_script_2 VAR_SANDGEM_STATE, 0, SandgemTown_PokemonLab_EventScript_Pokedex
	map_script_2 VAR_SANDGEM_STATE, 1, SandgemTown_PokemonLab_EventScript_Pokedex
	.2byte 0

SandgemTown_PokemonLab_EventScript_Pokedex::
	lockall
	applymovement LOCALID_SANDGEM_ROWAN, SandgemTown_PokemonLab_Movement_RowanDown
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	msgbox SandgemTown_PokemonLab_Text_Rowan, MSGBOX_DEFAULT
	playfanfare MUS_OBTAIN_ITEM
	message SandgemTown_PokemonLab_Text_ReceivedPokedex
	waitmessage
	waitfanfare
	setflag FLAG_SYS_POKEDEX_GET
	special SetUnlockedPokedexFlags
	setflag FLAG_ADVENTURE_STARTED
	msgbox SandgemTown_PokemonLab_Text_ReceivedPokedexHold, MSGBOX_DEFAULT
	setobjectxyperm LOCALID_SANDGEM_LAB_ASSISTANT, 8, 9
	clearflag FLAG_HIDE_SANDGEM_LAB_ASSISTANT
	addobject LOCALID_SANDGEM_LAB_ASSISTANT
	applymovement LOCALID_SANDGEM_LAB_ASSISTANT, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, SandgemTown_PokemonLab_EventScript_Lucas
	msgbox SandgemTown_PokemonLab_Text_DawnOutside, MSGBOX_DEFAULT
	goto SandgemTown_PokemonLab_EventScript_Leave
	end

SandgemTown_PokemonLab_EventScript_Lucas::
	msgbox SandgemTown_PokemonLab_Text_LucasOutside, MSGBOX_DEFAULT
	goto SandgemTown_PokemonLab_EventScript_Leave
	end

SandgemTown_PokemonLab_EventScript_Leave::
	closemessage
	removeobject LOCALID_SANDGEM_LAB_ASSISTANT
	setflag FLAG_HIDE_SANDGEM_LAB_ASSISTANT
	setvar VAR_SANDGEM_STATE, 3
	warpsilent MAP_SANDGEM_TOWN, 6, 10
	waitstate
	releaseall
	end

SandgemTown_PokemonLab_EventScript_Rowan::
	lock
	faceplayer
	goto_if_set FLAG_SYS_POKEDEX_GET, SandgemTown_PokemonLab_EventScript_RowanAfter
	msgbox SandgemTown_PokemonLab_Text_RowanWait, MSGBOX_DEFAULT
	release
	end

SandgemTown_PokemonLab_EventScript_RowanAfter::
	msgbox SandgemTown_PokemonLab_Text_RowanLater, MSGBOX_DEFAULT
	release
	end

SandgemTown_PokemonLab_EventScript_Assistant::
	msgbox SandgemTown_PokemonLab_Text_AssistantLater, MSGBOX_NPC
	end

SandgemTown_PokemonLab_EventScript_Machine::
	msgbox SandgemTown_PokemonLab_Text_Machine, MSGBOX_SIGN
	end

SandgemTown_PokemonLab_Movement_RowanDown:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

SandgemTown_PokemonLab_Text_Rowan:
	.string "ROWAN: So. You chose a POKéMON,\n"
	.string "and you have already tested it.\p"
	.string "A trainer's real work is meeting\n"
	.string "many more. Take this POKéDEX.\l"
	.string "It keeps a record of them.$"

SandgemTown_PokemonLab_Text_ReceivedPokedex:
	.string "{PLAYER} received the POKéDEX!$"

SandgemTown_PokemonLab_Text_ReceivedPokedexHold:
	.string "ROWAN: Open it from the menu when\n"
	.string "you have seen something new.$"

SandgemTown_PokemonLab_Text_DawnOutside:
	.string "DAWN: Come back outside.\n"
	.string "I'll show you the rest of town.$"

SandgemTown_PokemonLab_Text_LucasOutside:
	.string "LUCAS: Come back outside.\n"
	.string "I'll show you the rest of town.$"

SandgemTown_PokemonLab_Text_RowanWait:
	.string "ROWAN: One moment. I am in the\n"
	.string "middle of a thought.$"

SandgemTown_PokemonLab_Text_RowanLater:
	.string "ROWAN: Fill that POKéDEX. The\n"
	.string "road north will open in time.$"

SandgemTown_PokemonLab_Text_AssistantLater:
	.string "The lab keeps notes on every\n"
	.string "POKéMON that passes through.$"

SandgemTown_PokemonLab_Text_Machine:
	.string "A heavy machine hums. Whatever\n"
	.string "it measures, it doesn't say.$"
