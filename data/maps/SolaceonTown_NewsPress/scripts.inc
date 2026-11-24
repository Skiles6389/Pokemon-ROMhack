SolaceonTown_NewsPress_MapScripts::
	.byte 0

SolaceonTown_NewsPress_EventScript_Editor::
	msgbox SolaceonTown_NewsPress_Text_Editor, MSGBOX_NPC
	end

SolaceonTown_NewsPress_EventScript_Reporter::
	msgbox SolaceonTown_NewsPress_Text_Reporter, MSGBOX_NPC
	end

SolaceonTown_NewsPress_Text_Editor:
	.string "We print Contest buzz and town tips.\n"
	.string "Got a scoop? Tell us later!$"

SolaceonTown_NewsPress_Text_Reporter:
	.string "Headline: PSYDUCK jam Route 210!\n"
	.string "Medicine shortage continues.$"
