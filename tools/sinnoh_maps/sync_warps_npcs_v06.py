#!/usr/bin/env python3
"""
v0.6: Sync outdoor/cave warps + NPCs/items toward pret/pokeplatinum events.json.

Creates Emerald-tile interior scaffolds when destinations are missing.
Original dialogue only. Trainers: IVs 0, Platinum-ish levels.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAT_MAPS = Path("/tmp/pokeplatinum-ref/res/field/maps")
MAPS = REPO / "data" / "maps"
GROUPS = REPO / "data" / "maps" / "map_groups.json"
FLAGS_H = REPO / "include" / "constants" / "flags.h"
PARTY = REPO / "src" / "data" / "trainers.party"
LAYOUTS_JSON = REPO / "data" / "layouts" / "layouts.json"

# Emerald outdoor/cave map -> (platinum folder, origin or None for warp-fit)
OUTDOOR = {
    "TwinleafTown": ("twinleaf_town", (96, 864)),
    "Route201": ("route_201", None),
    "SandgemTown": ("sandgem_town", (160, 832)),
    "Route202": ("route_202", None),
    "JubilifeCity": ("jubilife_city", (128, 736)),
    "Route203": ("route_203", (192, 736)),
    "OreburghCity": ("oreburgh_city", (256, 736)),
    "OreburghGate_1F": ("oreburgh_gate_1f", (0, 0)),
    "OreburghGate_B1F": ("oreburgh_gate_b1f", (0, 0)),
    "OreburghMine_B1F": ("oreburgh_mine_b1f", (0, 0)),
    "OreburghMine_B2F": ("oreburgh_mine_b2f", (0, 0)),
    "Route204_South": ("route_204_south", (160, 704)),
    "Route204_North": ("route_204_north", (160, 672)),
    "RavagedPath": ("ravaged_path", (0, 0)),
    "FloaromaTown": ("floaroma_town", (160, 608)),
    "FloaromaMeadow": ("floaroma_meadow", (0, 0)),
    "Route205_South": ("route_205_south", (192, 576)),
    "ValleyWindworks_Exterior": ("valley_windworks_outside", (224, 640)),
    "EternaForest": ("eterna_forest", (0, 0)),
    "Route205_North": ("route_205_north", (256, 512)),
    "EternaCity": ("eterna_city", (288, 512)),
    "Route206": ("route_206", (288, 576)),
    "Route207": ("route_207", (288, 704)),
    "MtCoronet_1F_South": ("mt_coronet_1f_south", (0, 0)),
    "Route208": ("route_208", (384, 704)),
    "HearthomeCity": ("hearthome_city", (448, 672)),
    "Route209": ("route_209", (512, 672)),
    "SolaceonTown": ("solaceon_town", (544, 640)),
    "Route210_South": ("route_210_south", (544, 544)),
    "Route215": ("route_215", (576, 576)),
    "VeilstoneCity": ("veilstone_city", (672, 576)),
    "Route214": ("route_214", (704, 640)),
    "ValorLakefront": ("valor_lakefront", (672, 736)),
    "Route213": ("route_213", (640, 800)),
    "PastoriaCity": ("pastoria_city", (576, 800)),
    "VerityLakefront": ("verity_lakefront", None),
    "LakeVerity": ("lake_verity", (0, 0)),
}

# Platinum MAP_HEADER_* -> (MAP_*, folder, layout_id|None)
# layout None = must already exist; else scaffold with that layout.
HEADER_TO_EM = {
    "MAP_HEADER_JUBILIFE_CITY_MART": ("MAP_JUBILIFE_CITY_MART", "JubilifeCity_Mart", None),
    "MAP_HEADER_JUBILIFE_CITY_POKECENTER_1F": ("MAP_JUBILIFE_CITY_POKEMON_CENTER_1F", "JubilifeCity_PokemonCenter_1F", None),
    "MAP_HEADER_POKETCH_CO_1F": ("MAP_JUBILIFE_CITY_POKETCH_COMPANY", "JubilifeCity_PoketchCompany", None),
    "MAP_HEADER_TRAINERS_SCHOOL": ("MAP_JUBILIFE_CITY_TRAINERS_SCHOOL", "JubilifeCity_TrainersSchool", None),
    "MAP_HEADER_JUBILIFE_CITY_CONDOMINIUMS_1F": ("MAP_JUBILIFE_CITY_CONDO_1F", "JubilifeCity_Condo_1F", "LAYOUT_HOUSE1"),
    "MAP_HEADER_JUBILIFE_TV_1F": ("MAP_JUBILIFE_TV_1F", "JubilifeTV_1F", "LAYOUT_HOUSE1"),
    "MAP_HEADER_GLOBAL_TERMINAL_1F": ("MAP_JUBILIFE_GLOBAL_TERMINAL_1F", "JubilifeCity_GlobalTerminal_1F", "LAYOUT_HOUSE1"),
    "MAP_HEADER_JUBILIFE_CITY_SOUTH_HOUSE_1F": ("MAP_JUBILIFE_CITY_SOUTH_HOUSE", "JubilifeCity_SouthHouse", "LAYOUT_HOUSE1"),
    "MAP_HEADER_JUBILIFE_CITY_SOUTHWEST_HOUSE_1F": ("MAP_JUBILIFE_CITY_SOUTHWEST_HOUSE", "JubilifeCity_SouthwestHouse", "LAYOUT_HOUSE1"),
    "MAP_HEADER_ROUTE_218_GATE_TO_JUBILIFE_CITY": (
        "MAP_ROUTE218_JUBILIFE_GATE",
        "Route218_JubilifeGate",
        "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE",
    ),
    "MAP_HEADER_OREBURGH_CITY_GYM": ("MAP_OREBURGH_CITY_GYM", "OreburghCity_Gym", None),
    "MAP_HEADER_OREBURGH_CITY_MART": ("MAP_OREBURGH_CITY_MART", "OreburghCity_Mart", None),
    "MAP_HEADER_OREBURGH_CITY_POKECENTER_1F": ("MAP_OREBURGH_CITY_POKEMON_CENTER_1F", "OreburghCity_PokemonCenter_1F", None),
    "MAP_HEADER_MINING_MUSEUM": ("MAP_OREBURGH_CITY_MINING_MUSEUM", "OreburghCity_MiningMuseum", None),
    "MAP_HEADER_OREBURGH_CITY_WEST_HOUSE": ("MAP_OREBURGH_CITY_HOUSE2", "OreburghCity_House2", None),
    "MAP_HEADER_OREBURGH_CITY_NORTHWEST_HOUSE_1F": ("MAP_OREBURGH_CITY_HOUSE1", "OreburghCity_House1", None),
    "MAP_HEADER_OREBURGH_CITY_EAST_HOUSE_1F": ("MAP_OREBURGH_CITY_EAST_HOUSE", "OreburghCity_EastHouse", "LAYOUT_HOUSE1"),
    "MAP_HEADER_OREBURGH_CITY_NORTH_HOUSE_1F": ("MAP_OREBURGH_CITY_NORTH_HOUSE", "OreburghCity_NorthHouse", "LAYOUT_HOUSE1"),
    "MAP_HEADER_OREBURGH_CITY_MIDDLE_HOUSE": ("MAP_OREBURGH_CITY_MIDDLE_HOUSE", "OreburghCity_MiddleHouse", "LAYOUT_HOUSE1"),
    "MAP_HEADER_OREBURGH_CITY_SOUTH_HOUSE": ("MAP_OREBURGH_CITY_SOUTH_HOUSE", "OreburghCity_SouthHouse", "LAYOUT_HOUSE1"),
    "MAP_HEADER_OREBURGH_GATE_1F": ("MAP_OREBURGH_GATE_1F", "OreburghGate_1F", None),
    "MAP_HEADER_OREBURGH_GATE_B1F": ("MAP_OREBURGH_GATE_B1F", "OreburghGate_B1F", None),
    "MAP_HEADER_OREBURGH_MINE_B1F": ("MAP_OREBURGH_MINE_B1F", "OreburghMine_B1F", None),
    "MAP_HEADER_OREBURGH_MINE_B2F": ("MAP_OREBURGH_MINE_B2F", "OreburghMine_B2F", None),
    "MAP_HEADER_OREBURGH_CITY": ("MAP_OREBURGH_CITY", "OreburghCity", None),
    "MAP_HEADER_ROUTE_203": ("MAP_ROUTE203", "Route203", None),
    "MAP_HEADER_ROUTE_206_CYCLING_ROAD_NORTH_GATE": (
        "MAP_ROUTE206_CYCLING_ROAD_NORTH_GATE",
        "Route206_CyclingRoadNorthGate",
        None,
    ),
    "MAP_HEADER_ROUTE_206_CYCLING_ROAD_SOUTH_GATE": (
        "MAP_ROUTE206_CYCLING_ROAD_SOUTH_GATE",
        "Route206_CyclingRoadSouthGate",
        None,
    ),
    "MAP_HEADER_WAYWARD_CAVE_1F": ("MAP_WAYWARD_CAVE_1F", "WaywardCave_1F", "LAYOUT_GRANITE_CAVE_1F"),
    "MAP_HEADER_MT_CORONET_1F_SOUTH": ("MAP_MT_CORONET_1F_SOUTH", "MtCoronet_1F_South", None),
    "MAP_HEADER_MT_CORONET_2F": ("MAP_MT_CORONET_2F_STUB", "MtCoronet_2F_Stub", "LAYOUT_GRANITE_CAVE_1F"),
    "MAP_HEADER_ROUTE_207": ("MAP_ROUTE207", "Route207", None),
    "MAP_HEADER_ROUTE_208": ("MAP_ROUTE208", "Route208", None),
    "MAP_HEADER_RUIN_MANIAC_CAVE_SHORT": ("MAP_RUIN_MANIAC_CAVE", "RuinManiacCave", "LAYOUT_GRANITE_CAVE_1F"),
    "MAP_HEADER_RUIN_MANIAC_CAVE_LONG": ("MAP_RUIN_MANIAC_CAVE", "RuinManiacCave", "LAYOUT_GRANITE_CAVE_1F"),
    "MAP_HEADER_MANIAC_TUNNEL": ("MAP_MANIAC_TUNNEL", "ManiacTunnel", "LAYOUT_GRANITE_CAVE_1F"),
    "MAP_HEADER_ROUTE_214_GATE_TO_VEILSTONE_CITY": (
        "MAP_VEILSTONE_CITY_ROUTE214_GATE",
        "VeilstoneCity_Route214Gate",
        None,
    ),
    "MAP_HEADER_FOOTSTEP_HOUSE": ("MAP_ROUTE213_DR_FOOTSTEP_HOUSE", "Route213_DrFootstepHouse", None),
    "MAP_HEADER_GRAND_LAKE_ROUTE_213_LOBBY": ("MAP_ROUTE213_HOTEL_LOBBY", "Route213_HotelLobby", None),
    "MAP_HEADER_GRAND_LAKE_ROUTE_213_EAST_HOUSE": (
        "MAP_ROUTE213_EAST_HOUSE",
        "Route213_EastHouse",
        "LAYOUT_HOUSE1",
    ),
    "MAP_HEADER_GRAND_LAKE_ROUTE_213_NORTHWEST_HOUSE": (
        "MAP_ROUTE213_NORTHWEST_HOUSE",
        "Route213_NorthwestHouse",
        "LAYOUT_HOUSE1",
    ),
    "MAP_HEADER_GRAND_LAKE_ROUTE_213_NORTHEAST_HOUSE": (
        "MAP_ROUTE213_NORTHEAST_HOUSE",
        "Route213_NortheastHouse",
        "LAYOUT_HOUSE1",
    ),
    "MAP_HEADER_ROUTE_213_GATE_TO_PASTORIA_CITY": (
        "MAP_ROUTE213_PASTORIA_GATE",
        "Route213_PastoriaGate",
        "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE",
    ),
    "MAP_HEADER_RESTAURANT": ("MAP_VALOR_LAKEFRONT_RESTAURANT", "ValorLakefront_Restaurant", None),
    "MAP_HEADER_GRAND_LAKE_VALOR_LAKEFRONT_EAST_HOUSE": (
        "MAP_VALOR_LAKEFRONT_EAST_COTTAGE",
        "ValorLakefront_EastCottage",
        None,
    ),
    "MAP_HEADER_GRAND_LAKE_VALOR_LAKEFRONT_WEST_HOUSE": (
        "MAP_VALOR_LAKEFRONT_WEST_COTTAGE",
        "ValorLakefront_WestCottage",
        None,
    ),
    "MAP_HEADER_LAKE_VALOR": ("MAP_LAKE_VALOR_STUB", "LakeValor_Stub", "LAYOUT_GRANITE_CAVE_1F"),
    "MAP_HEADER_LAKE_VALOR_DRAINED": ("MAP_LAKE_VALOR_STUB", "LakeValor_Stub", "LAYOUT_GRANITE_CAVE_1F"),
    "MAP_HEADER_PASTORIA_CITY_GYM": ("MAP_PASTORIA_CITY_GYM", "PastoriaCity_Gym", None),
    "MAP_HEADER_PASTORIA_CITY_POKECENTER_1F": (
        "MAP_PASTORIA_CITY_POKEMON_CENTER_1F",
        "PastoriaCity_PokemonCenter_1F",
        None,
    ),
    "MAP_HEADER_PASTORIA_CITY_MART": ("MAP_PASTORIA_CITY_MART", "PastoriaCity_Mart", None),
    "MAP_HEADER_PASTORIA_CITY_NORTH_HOUSE": ("MAP_PASTORIA_CITY_NORTH_HOUSE", "PastoriaCity_NorthHouse", None),
    "MAP_HEADER_PASTORIA_CITY_EAST_HOUSE": ("MAP_PASTORIA_CITY_EAST_HOUSE", "PastoriaCity_EastHouse", None),
    "MAP_HEADER_PASTORIA_CITY_NORTHEAST_HOUSE": (
        "MAP_PASTORIA_CITY_NORTHEAST_HOUSE",
        "PastoriaCity_NortheastHouse",
        None,
    ),
    "MAP_HEADER_PASTORIA_CITY_SOUTHWEST_HOUSE": (
        "MAP_PASTORIA_CITY_SOUTHWEST_HOUSE",
        "PastoriaCity_SouthwestHouse",
        None,
    ),
    "MAP_HEADER_PASTORIA_CITY_MIDDLE_HOUSE": (
        "MAP_PASTORIA_CITY_MOVE_REMINDER_HOUSE",
        "PastoriaCity_MoveReminderHouse",
        None,
    ),
    "MAP_HEADER_PASTORIA_CITY_OBSERVATORY_GATE_1F": (
        "MAP_PASTORIA_CITY_GREAT_MARSH_GATE",
        "PastoriaCity_GreatMarshGate",
        None,
    ),
    "MAP_HEADER_LAKE_VERITY": ("MAP_LAKE_VERITY", "LakeVerity", None),
    "MAP_HEADER_LAKE_VERITY_LOW_WATER": ("MAP_LAKE_VERITY", "LakeVerity", None),
    "MAP_HEADER_VERITY_LAKEFRONT": ("MAP_VERITY_LAKEFRONT", "VerityLakefront", None),
    "MAP_HEADER_VERITY_CAVERN": ("MAP_VERITY_CAVERN_STUB", "VerityCavern_Stub", "LAYOUT_GRANITE_CAVE_1F"),
    "MAP_HEADER_ROUTE_201": ("MAP_ROUTE201", "Route201", None),
}

SKIP_HEADERS = {
    "MAP_HEADER_UNUSED_JUBILIFE_CITY_HOUSE_3",
    "MAP_HEADER_UNUSED_JUBILIFE_CITY_HOUSE_4",
}

# Destinations that are mid-road cycling underpasses on Route206 — keep Emerald end warps only.
SKIP_ADD_ON_MAP = {
    "Route206": {
        "MAP_HEADER_ROUTE_206_CYCLING_ROAD_SOUTH_GATE",
        "MAP_HEADER_ROUTE_206_CYCLING_ROAD_NORTH_GATE",
    },
}

NPC_GFX = [
    "OBJ_EVENT_GFX_BOY_1",
    "OBJ_EVENT_GFX_GIRL_1",
    "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_MAN_2",
    "OBJ_EVENT_GFX_OLD_MAN",
    "OBJ_EVENT_GFX_OLD_WOMAN",
    "OBJ_EVENT_GFX_YOUNGSTER",
    "OBJ_EVENT_GFX_LASS",
]
TRAINER_GFX = [
    "OBJ_EVENT_GFX_YOUNGSTER",
    "OBJ_EVENT_GFX_LASS",
    "OBJ_EVENT_GFX_CAMPER",
    "OBJ_EVENT_GFX_PICNICKER",
    "OBJ_EVENT_GFX_BUG_CATCHER",
    "OBJ_EVENT_GFX_HIKER",
]

CREATED: list[str] = []
PROGRESS_LEVEL = {
    "TwinleafTown": 3,
    "Route201": 3,
    "SandgemTown": 4,
    "Route202": 5,
    "JubilifeCity": 6,
    "Route203": 7,
    "OreburghCity": 10,
    "OreburghGate_1F": 8,
    "OreburghGate_B1F": 9,
    "OreburghMine_B1F": 10,
    "OreburghMine_B2F": 11,
    "Route204_South": 8,
    "Route204_North": 9,
    "RavagedPath": 9,
    "FloaromaTown": 12,
    "FloaromaMeadow": 12,
    "Route205_South": 13,
    "ValleyWindworks_Exterior": 13,
    "EternaForest": 14,
    "Route205_North": 15,
    "EternaCity": 16,
    "Route206": 17,
    "Route207": 18,
    "MtCoronet_1F_South": 18,
    "Route208": 19,
    "HearthomeCity": 20,
    "Route209": 21,
    "SolaceonTown": 22,
    "Route210_South": 23,
    "Route215": 24,
    "VeilstoneCity": 25,
    "Route214": 26,
    "ValorLakefront": 27,
    "Route213": 28,
    "PastoriaCity": 30,
    "VerityLakefront": 4,
    "LakeVerity": 4,
}


def layout_ids() -> set[str]:
    return {L["id"] for L in json.loads(LAYOUTS_JSON.read_text())["layouts"]}


def map_size(name: str) -> tuple[int, int]:
    for L in json.loads(LAYOUTS_JSON.read_text())["layouts"]:
        if L.get("name") == f"{name}_Layout":
            return int(L["width"]), int(L["height"])
    return 32, 32


def mapsec_for(return_map: str) -> str:
    folder = None
    for em_name in OUTDOOR:
        if f"MAP_{em_name.upper()}" == return_map or return_map.endswith(em_name.upper()):
            folder = em_name
            break
    # Prefer reading return map's mapsec
    # Convert MAP_JUBILIFE_CITY -> JubilifeCity-ish by scanning
    for p in MAPS.iterdir():
        if not p.is_dir():
            continue
        mj = p / "map.json"
        if not mj.exists():
            continue
        d = json.loads(mj.read_text())
        if d.get("id") == return_map:
            return d.get("region_map_section", "MAPSEC_LITTLEROOT_TOWN")
    return "MAPSEC_LITTLEROOT_TOWN"


def create_scaffold(folder: str, map_id: str, layout_id: str, mapsec: str, return_map: str) -> None:
    path = MAPS / folder
    if path.exists():
        return
    ids = layout_ids()
    if layout_id not in ids:
        layout_id = "LAYOUT_HOUSE1"
    is_gate = "SEASIDE_CYCLING" in layout_id or "GATE" in layout_id
    is_cave = "CAVE" in layout_id or "MINE" in layout_id or "GRANITE" in layout_id
    if is_gate:
        exit_x, exit_y = 1, 5
        exit2 = (2, 5)
    elif is_cave:
        # GraniteCave_1F is 42x15 — exit near south
        exit_x, exit_y = 20, 13
        exit2 = (21, 13)
    else:
        exit_x, exit_y = 3, 8
        exit2 = (4, 8)

    data = {
        "id": map_id,
        "name": folder,
        "layout": layout_id,
        "music": "MUS_PL_JUBILIFE",
        "night_music": "MUS_PL_JUBILIFE_NIGHT",
        "region": "REGION_HOENN",
        "region_map_section": mapsec,
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_UNDERGROUND" if is_cave else "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": bool(is_cave),
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": [
            {
                "graphics_id": "OBJ_EVENT_GFX_MAN_2",
                "x": 5 if not is_cave else 18,
                "y": 4 if not is_cave else 8,
                "elevation": 3,
                "movement_type": "MOVEMENT_TYPE_FACE_DOWN",
                "movement_range_x": 0,
                "movement_range_y": 0,
                "trainer_type": "TRAINER_TYPE_NONE",
                "trainer_sight_or_berry_tree_id": "0",
                "script": f"{folder}_EventScript_Attendant",
                "flag": "0",
            }
        ],
        "warp_events": [
            {"x": exit_x, "y": exit_y, "elevation": 0, "dest_map": return_map, "dest_warp_id": "0"},
            {"x": exit2[0], "y": exit2[1], "elevation": 0, "dest_map": return_map, "dest_warp_id": "0"},
        ],
        "coord_events": [],
        "bg_events": [],
    }
    path.mkdir(parents=True)
    (path / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (path / "scripts.inc").write_text(
        f"{folder}_MapScripts::\n\t.byte 0\n\n"
        f"{folder}_EventScript_Attendant::\n"
        f"\tmsgbox {folder}_Text_Attendant, MSGBOX_NPC\n\tend\n\n"
        f"{folder}_Text_Attendant:\n"
        f'\t.string "This spot is still settling in.\\n"\n'
        f'\t.string "The door you used will take you\\l"\n'
        f'\t.string "straight back outside.$"\n'
    )
    CREATED.append(folder)
    print(f"  + scaffold {folder} ({map_id}) {layout_id}")


def register_scaffolds_in_groups() -> None:
    if not CREATED:
        return
    groups = json.loads(GROUPS.read_text())
    key = "gMapGroup_IndoorV06"
    lst = groups.setdefault(key, [])
    for folder in CREATED:
        if folder not in lst:
            lst.append(folder)
    order = groups["group_order"]
    if key not in order:
        anchor = "gMapGroup_IndoorM20"
        order.insert(order.index(anchor) + 1 if anchor in order else len(order), key)
    GROUPS.write_text(json.dumps(groups, indent=2) + "\n")


def resolve_dest(header: str, return_map: str):
    if header in SKIP_HEADERS:
        return None
    info = HEADER_TO_EM.get(header)
    if info is None:
        print(f"  ? unmapped header {header}")
        return None
    map_id, folder, layout = info
    if not (MAPS / folder).exists():
        if layout is None:
            print(f"  ! missing required map {folder} for {header}")
            return None
        create_scaffold(folder, map_id, layout, mapsec_for(return_map), return_map)
    return map_id, folder


def fit_origin(plat_warps, em_warps, w, h):
    best = None
    for pw in plat_warps:
        for ew in em_warps:
            ox, oz = pw["x"] - ew["x"], pw["z"] - ew["y"]
            hits = 0
            for p2 in plat_warps:
                lx, ly = p2["x"] - ox, p2["z"] - oz
                if 0 <= lx < w and 0 <= ly < h:
                    if any(abs(lx - e["x"]) + abs(ly - e["y"]) <= 1 for e in em_warps):
                        hits += 1
            if best is None or hits > best[0]:
                best = (hits, (ox, oz))
    return best[1] if best else (0, 0)


def allocate_item_flag(label: str) -> str | None:
    text = FLAGS_H.read_text()
    m = re.search(r"#define (FLAG_UNUSED_0x[0-9A-Fa-f]+)\s+(0x[0-9A-Fa-f]+)", text)
    if not m:
        return None
    old, val = m.group(1), m.group(2)
    new = re.sub(r"[^A-Z0-9_]", "", f"FLAG_ITEM_{label}")[:48]
    base = new
    i = 0
    while re.search(rf"#define {new}\b", text):
        i += 1
        new = f"{base}_{i}"[:48]
    text = text.replace(m.group(0), f"#define {new}  {val} // was {old}", 1)
    FLAGS_H.write_text(text)
    return new


def ensure_trainer(tid: str, level: int, class_name="Youngster", name="TRAVELER", pic="Youngster"):
    party = PARTY.read_text()
    if f"=== {tid} ===" in party:
        return
    block = (
        f"=== {tid} ===\n"
        f"Name: {name}\n"
        f"Class: {class_name}\n"
        f"Pic: {pic}\n"
        f"Gender: Male\n"
        f"Music: Male\n"
        f"Double Battle: No\n"
        f"AI: Check Bad Move\n"
        f"\n"
        f"Starly (M)\n"
        f"Level: {level}\n"
        f"IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe\n"
        f"- Tackle\n"
        f"\n"
        f"Bidoof (M)\n"
        f"Level: {max(3, level - 1)}\n"
        f"IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe\n"
        f"- Tackle\n"
        f"\n"
    )
    PARTY.write_text(party.rstrip() + "\n\n" + block)


def append_script(folder: str, label: str, kind: str, trainer_id: str | None = None):
    sc = MAPS / folder / "scripts.inc"
    text = sc.read_text() if sc.exists() else f"{folder}_MapScripts::\n\t.byte 0\n\n"
    if f"{label}::" in text:
        return
    if kind == "npc":
        block = (
            f"{label}::\n"
            f"\tmsgbox {label}_Text, MSGBOX_NPC\n"
            f"\tend\n\n"
            f"{label}_Text:\n"
            f'\t.string "These roads keep surprising me.\\n"\n'
            f'\t.string "Every corner hides another path.$"\n\n'
        )
    else:
        block = (
            f"{label}::\n"
            f"\ttrainerbattle_single {trainer_id}, {label}_Intro, {label}_Defeat\n"
            f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n"
            f"\tend\n\n"
            f"{label}_Intro:\n"
            f'\t.string "A quick match will wake us both up!$"\n\n'
            f"{label}_Defeat:\n"
            f'\t.string "You were ready for that.$"\n\n'
            f"{label}_After:\n"
            f'\t.string "Keep going. The next landmark is\\n"\n'
            f'\t.string "closer than it looks.$"\n\n'
        )
    sc.write_text(text + block)


def pclass(o: dict) -> str:
    g = (o.get("graphics_id") or "").upper()
    if "POKEBALL" in g or g.endswith("_ITEM") or "ITEMBALL" in g:
        return "item"
    tt = o.get("trainer_type")
    if tt not in (None, "0", 0, "TRAINER_TYPE_NONE"):
        return "trainer"
    if any(x in g for x in ("ROCK_SMASH", "STRENGTH", "BOULDER", "CUTTABLE", "BREAKABLE")):
        return "field"
    return "npc"


def sync_map(em_name: str, plat_folder: str, origin):
    plat_path = PLAT_MAPS / plat_folder
    if not plat_path.exists():
        # try alternate names
        alts = list(PLAT_MAPS.glob(plat_folder.replace("_south", "") + "*"))
        print(f"skip {em_name}: no plat folder {plat_folder}")
        return
    em_path = MAPS / em_name
    if not em_path.exists():
        print(f"skip {em_name}: missing emerald map")
        return
    em = json.loads((em_path / "map.json").read_text())
    pe = json.loads((plat_path / "events.json").read_text())
    w, h = map_size(em_name)
    map_id = em["id"]

    plat_warps = pe.get("warp_events") or []
    em_warps = list(em.get("warp_events") or [])
    if origin is None:
        origin = fit_origin(plat_warps, em_warps, w, h) if em_warps else (0, 0)
        # VerityLakefront special: fit so lake warps land on north edge
        if em_name == "VerityLakefront" and plat_warps:
            # Prefer local y near 0 (north toward lake connection)
            for pw in plat_warps:
                # try ox such that lx in [0,w)
                for guess_ox in range(pw["x"] - w + 1, pw["x"] + 1):
                    for guess_oz in range(pw["z"] - h + 1, pw["z"] + 1):
                        lx, ly = pw["x"] - guess_ox, pw["z"] - guess_oz
                        if 0 <= lx < w and 0 <= ly < h and ly <= 2:
                            origin = (guess_ox, guess_oz)
                            break
    ox, oz = origin

    skip_headers = SKIP_ADD_ON_MAP.get(em_name, set())
    new_warps = list(em_warps)
    added_w = 0
    for pw in plat_warps:
        if pw["dest_header_id"] in skip_headers:
            continue
        lx, ly = pw["x"] - ox, pw["z"] - oz
        if not (0 <= lx < w and 0 <= ly < h):
            continue
        if any(abs(lx - e["x"]) + abs(ly - e["y"]) <= 1 for e in new_warps):
            continue
        resolved = resolve_dest(pw["dest_header_id"], map_id)
        if not resolved:
            continue
        dest_map, dest_folder = resolved
        new_warps.append(
            {
                "x": int(lx),
                "y": int(ly),
                "elevation": 0,
                "dest_map": dest_map,
                "dest_warp_id": "0",
            }
        )
        added_w += 1
        idx = len(new_warps) - 1
        dest_json = MAPS / dest_folder / "map.json"
        if dest_json.exists() and dest_folder in CREATED:
            dj = json.loads(dest_json.read_text())
            dwarfs = dj.get("warp_events") or []
            for dw in dwarfs:
                dw["dest_map"] = map_id
                dw["dest_warp_id"] = str(idx)
            dj["warp_events"] = dwarfs
            dest_json.write_text(json.dumps(dj, indent=2) + "\n")
    em["warp_events"] = new_warps

    # Objects
    plat_objs = pe.get("object_events") or []
    em_objs = list(em.get("object_events") or [])
    occupied = {(o["x"], o["y"]) for o in em_objs}

    def free_tile(x, y):
        x = max(1, min(w - 2, int(x)))
        y = max(1, min(h - 2, int(y)))
        if (x, y) not in occupied:
            return x, y
        for r in range(1, 5):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    nx, ny = x + dx, y + dy
                    if 1 <= nx < w - 1 and 1 <= ny < h - 1 and (nx, ny) not in occupied:
                        return nx, ny
        return None

    def count_kind(objs, kind):
        n = 0
        for o in objs:
            g = (o.get("graphics_id") or "")
            if kind == "item":
                if "ITEM" in g:
                    n += 1
            elif kind == "trainer":
                if o.get("trainer_type") not in (None, "0", "TRAINER_TYPE_NONE"):
                    n += 1
            elif kind == "npc":
                if "ITEM" not in g and o.get("trainer_type") in (None, "0", "TRAINER_TYPE_NONE"):
                    if not any(x in g for x in ("BREAKABLE", "CUTTABLE", "BOULDER", "PUSHABLE")):
                        n += 1
        return n

    target_npc = sum(1 for o in plat_objs if pclass(o) == "npc")
    target_tr = sum(1 for o in plat_objs if pclass(o) == "trainer")
    target_item = sum(1 for o in plat_objs if pclass(o) == "item")
    have_npc, have_tr, have_item = count_kind(em_objs, "npc"), count_kind(em_objs, "trainer"), count_kind(em_objs, "item")
    MAX_OBJ = 40
    added_npc = added_tr = added_item = 0
    level = PROGRESS_LEVEL.get(em_name, 10)

    plat_npcs = [o for o in plat_objs if pclass(o) == "npc"]
    for i, po in enumerate(plat_npcs):
        if have_npc + added_npc >= min(target_npc, have_npc + 8):
            break
        if len(em_objs) >= MAX_OBJ:
            break
        lx, ly = po["x"] - ox, po["z"] - oz
        if not (0 <= lx < w and 0 <= ly < h):
            continue
        if any(abs(lx - e["x"]) + abs(ly - e["y"]) <= 2 for e in em_objs):
            continue
        tile = free_tile(lx, ly)
        if not tile:
            continue
        label = f"{em_name}_EventScript_PlatNpc{i}"
        em_objs.append(
            {
                "graphics_id": NPC_GFX[i % len(NPC_GFX)],
                "x": tile[0],
                "y": tile[1],
                "elevation": 3,
                "movement_type": "MOVEMENT_TYPE_WANDER_AROUND",
                "movement_range_x": 1,
                "movement_range_y": 1,
                "trainer_type": "TRAINER_TYPE_NONE",
                "trainer_sight_or_berry_tree_id": "0",
                "script": label,
                "flag": "0",
            }
        )
        occupied.add(tile)
        append_script(em_name, label, "npc")
        added_npc += 1

    plat_trs = [o for o in plat_objs if pclass(o) == "trainer"]
    for i, po in enumerate(plat_trs):
        if have_tr + added_tr >= min(target_tr, have_tr + 6):
            break
        if len(em_objs) >= MAX_OBJ:
            break
        lx, ly = po["x"] - ox, po["z"] - oz
        if not (0 <= lx < w and 0 <= ly < h):
            continue
        if any(
            abs(lx - e["x"]) + abs(ly - e["y"]) <= 2
            and e.get("trainer_type") not in (None, "0", "TRAINER_TYPE_NONE")
            for e in em_objs
        ):
            continue
        tile = free_tile(lx, ly)
        if not tile:
            continue
        tid = re.sub(r"[^A-Z0-9_]", "", f"TRAINER_{em_name.upper()}_V06_{i}")[:40]
        ensure_trainer(tid, level)
        label = f"{em_name}_EventScript_V06Trainer{i}"
        em_objs.append(
            {
                "graphics_id": TRAINER_GFX[i % len(TRAINER_GFX)],
                "x": tile[0],
                "y": tile[1],
                "elevation": 3,
                "movement_type": "MOVEMENT_TYPE_FACE_DOWN",
                "movement_range_x": 0,
                "movement_range_y": 0,
                "trainer_type": "TRAINER_TYPE_NORMAL",
                "trainer_sight_or_berry_tree_id": "3",
                "script": label,
                "flag": "0",
            }
        )
        occupied.add(tile)
        append_script(em_name, label, "trainer", tid)
        added_tr += 1

    plat_items = [o for o in plat_objs if pclass(o) == "item"]
    for i, po in enumerate(plat_items):
        if have_item + added_item >= min(target_item, have_item + 5):
            break
        if len(em_objs) >= MAX_OBJ:
            break
        lx, ly = po["x"] - ox, po["z"] - oz
        if not (0 <= lx < w and 0 <= ly < h):
            continue
        if any(abs(lx - e["x"]) + abs(ly - e["y"]) <= 1 for e in em_objs):
            continue
        tile = free_tile(lx, ly)
        if not tile:
            continue
        flag = allocate_item_flag(f"{em_name.upper()}_V06_{i}")
        if not flag:
            break
        em_objs.append(
            {
                "graphics_id": "OBJ_EVENT_GFX_ITEM_BALL",
                "x": tile[0],
                "y": tile[1],
                "elevation": 3,
                "movement_type": "MOVEMENT_TYPE_LOOK_AROUND",
                "movement_range_x": 0,
                "movement_range_y": 0,
                "trainer_type": "TRAINER_TYPE_NONE",
                "trainer_sight_or_berry_tree_id": "ITEM_POTION",
                "script": "Common_EventScript_FindItem",
                "flag": flag,
            }
        )
        occupied.add(tile)
        added_item += 1

    em["object_events"] = em_objs
    (em_path / "map.json").write_text(json.dumps(em, indent=2) + "\n")
    print(
        f"{em_name}: +warps={added_w} +npc={added_npc} +tr={added_tr} +item={added_item} "
        f"(warps={len(new_warps)} objs={len(em_objs)}) origin={origin}"
    )


def patch_verity_and_mine_specials():
    """Ensure LakeVerity cavern stub + south exits; Mine B1F multi-tile stairs."""
    # LakeVerity: add south warps to VerityLakefront + cavern stub near north center
    lake = MAPS / "LakeVerity" / "map.json"
    if lake.exists():
        d = json.loads(lake.read_text())
        w, h = map_size("LakeVerity")
        warps = list(d.get("warp_events") or [])
        # south exits toward lakefront
        if not any(ww["dest_map"] == "MAP_VERITY_LAKEFRONT" for ww in warps):
            warps.append({"x": min(46, w - 2), "y": h - 2, "elevation": 0, "dest_map": "MAP_VERITY_LAKEFRONT", "dest_warp_id": "0"})
            warps.append({"x": min(47, w - 1), "y": h - 2, "elevation": 0, "dest_map": "MAP_VERITY_LAKEFRONT", "dest_warp_id": "0"})
        if not any(ww["dest_map"] == "MAP_VERITY_CAVERN_STUB" for ww in warps):
            create_scaffold(
                "VerityCavern_Stub",
                "MAP_VERITY_CAVERN_STUB",
                "LAYOUT_GRANITE_CAVE_1F",
                "MAPSEC_LAKE_VERITY",
                "MAP_LAKE_VERITY",
            )
            warps.append({"x": min(32, w // 2), "y": min(4, h - 2), "elevation": 0, "dest_map": "MAP_VERITY_CAVERN_STUB", "dest_warp_id": "0"})
            # wire stub exit
            stub = MAPS / "VerityCavern_Stub" / "map.json"
            if stub.exists():
                sj = json.loads(stub.read_text())
                for dw in sj.get("warp_events") or []:
                    dw["dest_map"] = "MAP_LAKE_VERITY"
                    dw["dest_warp_id"] = str(len(warps) - 1)
                stub.write_text(json.dumps(sj, indent=2) + "\n")
        d["warp_events"] = warps
        lake.write_text(json.dumps(d, indent=2) + "\n")
        print(f"LakeVerity special warps -> {len(warps)}")

    # OreburghMine_B1F: add side tiles for city/B2F if missing near Platinum locals
    mine = MAPS / "OreburghMine_B1F" / "map.json"
    if mine.exists():
        d = json.loads(mine.read_text())
        warps = list(d.get("warp_events") or [])
        # Plat has city exits at (11,1),(12,1),(13,1) and B2F at (11-13,21)
        for x in (11, 13):
            if not any(ww["x"] == x and ww["y"] == 1 for ww in warps):
                warps.append({"x": x, "y": 1, "elevation": 0, "dest_map": "MAP_OREBURGH_CITY", "dest_warp_id": "9"})
        for x in (11, 13):
            if not any(ww["x"] == x and ww["y"] == 21 for ww in warps):
                warps.append({"x": x, "y": 21, "elevation": 0, "dest_map": "MAP_OREBURGH_MINE_B2F", "dest_warp_id": "0"})
        d["warp_events"] = warps
        mine.write_text(json.dumps(d, indent=2) + "\n")
        print(f"OreburghMine_B1F warps -> {len(warps)}")

    # MtCoronet: add 2F stub warp at Platinum (25,3)
    mt = MAPS / "MtCoronet_1F_South" / "map.json"
    if mt.exists():
        d = json.loads(mt.read_text())
        warps = list(d.get("warp_events") or [])
        if not any(ww.get("dest_map") == "MAP_MT_CORONET_2F_STUB" for ww in warps):
            create_scaffold(
                "MtCoronet_2F_Stub",
                "MAP_MT_CORONET_2F_STUB",
                "LAYOUT_GRANITE_CAVE_1F",
                "MAPSEC_MT_CORONET",
                "MAP_MT_CORONET_1F_SOUTH",
            )
            warps.append({"x": 25, "y": 3, "elevation": 0, "dest_map": "MAP_MT_CORONET_2F_STUB", "dest_warp_id": "0"})
            stub = MAPS / "MtCoronet_2F_Stub" / "map.json"
            if stub.exists():
                sj = json.loads(stub.read_text())
                for dw in sj.get("warp_events") or []:
                    dw["dest_map"] = "MAP_MT_CORONET_1F_SOUTH"
                    dw["dest_warp_id"] = str(len(warps) - 1)
                stub.write_text(json.dumps(sj, indent=2) + "\n")
        d["warp_events"] = warps
        mt.write_text(json.dumps(d, indent=2) + "\n")
        print(f"MtCoronet_1F_South warps -> {len(warps)}")


def main():
    ids = layout_ids()
    assert "LAYOUT_HOUSE1" in ids
    assert "LAYOUT_GRANITE_CAVE_1F" in ids
    assert "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE" in ids

    for em_name, (plat, origin) in OUTDOOR.items():
        print(f"== {em_name} ==")
        sync_map(em_name, plat, origin)

    patch_verity_and_mine_specials()
    register_scaffolds_in_groups()
    print(f"\nCreated scaffolds ({len(CREATED)}): {CREATED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
