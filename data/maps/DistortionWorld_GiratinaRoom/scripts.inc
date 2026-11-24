DistortionWorld_GiratinaRoom_MapScripts::
	.byte 0

DistortionWorld_GiratinaRoom_EventScript_Giratina::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_GIRATINA_DISTORTION, DistortionWorld_GiratinaRoom_EventScript_Gone
	msgbox DistortionWorld_GiratinaRoom_Text_Appear, MSGBOX_DEFAULT
	setwildbattle SPECIES_GIRATINA, 47
	dowildbattle
	setflag FLAG_DEFEATED_GIRATINA_DISTORTION
	setflag FLAG_DISTORTION_WORLD_CLEAR
	msgbox DistortionWorld_GiratinaRoom_Text_After, MSGBOX_DEFAULT
	release
	end

DistortionWorld_GiratinaRoom_EventScript_Gone::
	msgbox DistortionWorld_GiratinaRoom_Text_Gone, MSGBOX_DEFAULT
	release
	end

DistortionWorld_GiratinaRoom_Text_Appear:
	.string "A shadow coils against reversed gravity.\n"
	.string "Giratina emerges!$"

DistortionWorld_GiratinaRoom_Text_After:
	.string "The Renegade Pokemon fades.\n"
	.string "A path back toward Spear Pillar opens.$"

DistortionWorld_GiratinaRoom_Text_Gone:
	.string "Only distorted silence remains.$"

