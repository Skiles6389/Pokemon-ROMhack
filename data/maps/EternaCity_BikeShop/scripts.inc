EternaCity_BikeShop_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, EternaCity_BikeShop_OnTransition
	.byte 0

EternaCity_BikeShop_OnTransition:
	call_if_set FLAG_ETERNA_BUILDING_CLEARED, EternaCity_BikeShop_EventScript_ShowOwner
	return

EternaCity_BikeShop_EventScript_ShowOwner::
	clearflag FLAG_HIDE_BIKE_SHOP_OWNER
	return

EternaCity_BikeShop_EventScript_Owner::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_BIKE, EternaCity_BikeShop_EventScript_AlreadyHasBike
	goto_if_unset FLAG_ETERNA_BUILDING_CLEARED, EternaCity_BikeShop_EventScript_Closed
	msgbox EternaCity_BikeShop_Text_GiveBike, MSGBOX_DEFAULT
	giveitem ITEM_BICYCLE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_BIKE
	msgbox EternaCity_BikeShop_Text_EnjoyBike, MSGBOX_DEFAULT
	release
	end

EternaCity_BikeShop_EventScript_Closed::
	msgbox EternaCity_BikeShop_Text_Closed, MSGBOX_DEFAULT
	release
	end

EternaCity_BikeShop_EventScript_AlreadyHasBike::
	msgbox EternaCity_BikeShop_Text_AlreadyBike, MSGBOX_DEFAULT
	release
	end

EternaCity_BikeShop_EventScript_Customer::
	msgbox EternaCity_BikeShop_Text_Customer, MSGBOX_NPC
	end

EternaCity_BikeShop_Text_Closed:
	.string "OWNER: Can't open--shop's a mess while\n"
	.string "Galactic's upstairs!$"

EternaCity_BikeShop_Text_GiveBike:
	.string "OWNER: Jupiter's gone! You saved us.\n"
	.string "Take this Bicycle, free of charge!$"

EternaCity_BikeShop_Text_EnjoyBike:
	.string "OWNER: Pedal to the Cycling Road\n"
	.string "south of town. Show them your Bike!$"

EternaCity_BikeShop_Text_AlreadyBike:
	.string "OWNER: Treat that bike well!$"

EternaCity_BikeShop_Text_Customer:
	.string "I wanted a bike, but Galactic ruined\n"
	.string "business for everyone.$"
