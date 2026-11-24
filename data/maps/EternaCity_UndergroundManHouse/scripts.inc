EternaCity_UndergroundManHouse_MapScripts::
	.byte 0

EternaCity_UndergroundManHouse_EventScript_NPC::
	lock
	faceplayer
	msgbox EternaCity_UndergroundManHouse_Text_Man, MSGBOX_DEFAULT
	release
	end

EternaCity_UndergroundManHouse_Text_Man:
	.string "The Underground Man drills tunnels\n"
	.string "beneath Sinnoh for fun.\p"
	.string "He might share secrets if you show\n"
	.string "him spheres someday.$"
