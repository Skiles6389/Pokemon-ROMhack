Route210_CafeCabin_MapScripts::
	.byte 0

Route210_CafeCabin_EventScript_Waitress::
	lock
	faceplayer
	msgbox Route210_CafeCabin_Text_WaitressAsk, MSGBOX_DEFAULT
	pokemart Route210_CafeCabin_Pokemart
	msgbox Route210_CafeCabin_Text_WaitressBye, MSGBOX_DEFAULT
	release
	end

Route210_CafeCabin_EventScript_Patron::
	msgbox Route210_CafeCabin_Text_Patron, MSGBOX_NPC
	end

Route210_CafeCabin_EventScript_Collector::
	trainerbattle_single TRAINER_CAFE_COLLECTOR_R210, Route210_CafeCabin_Text_CollectorIntro, Route210_CafeCabin_Text_CollectorDefeat
	msgbox Route210_CafeCabin_Text_CollectorAfter, MSGBOX_AUTOCLOSE
	end

	.align 2
Route210_CafeCabin_Pokemart:
	.2byte ITEM_MOOMOO_MILK
	.2byte ITEM_NONE
	release
	end

Route210_CafeCabin_Text_WaitressAsk:
	.string "Welcome! Fresh Moomoo Milk today.\n"
	.string "Care for a bottle?$"

Route210_CafeCabin_Text_WaitressBye:
	.string "Come warm up anytime!$"

Route210_CafeCabin_Text_Patron:
	.string "Milk after a rainy walk hits right.\n"
	.string "Those PSYDUCK could use some, too.$"

Route210_CafeCabin_Text_CollectorIntro:
	.string "I collect cafe stickers!\n"
	.string "Battle me for bragging rights!$"

Route210_CafeCabin_Text_CollectorDefeat:
	.string "Stickerless and beaten...$"

Route210_CafeCabin_Text_CollectorAfter:
	.string "Next cafe stop: somewhere sunnier.$"
