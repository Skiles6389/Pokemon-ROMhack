#!/usr/bin/env python3
"""
M21: Route 212 N/S + Great Marsh + HM Defog (post–Fen Badge).

Layouts from pret/pokeplatinum TownsAndRoutes / GreatMarsh_DP land IDs.
Emerald tilesets only. Original dialogue. Trainers IVs 0.
"""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAT_DATA = Path("/tmp/pokeplatinum-ref/res/field/mapmodels/data")
PLAT_MAPS = Path("/tmp/pokeplatinum-ref/res/field/maps")
LAYOUTS = REPO / "data" / "layouts"
LAYOUTS_JSON = LAYOUTS / "layouts.json"
MAPS = REPO / "data" / "maps"
GROUPS = MAPS / "map_groups.json"
EVENT_SCRIPTS = REPO / "data" / "event_scripts.s"
OPP = REPO / "include" / "constants" / "opponents.h"
PARTY = REPO / "src" / "data" / "trainers.party"
FLAGS = REPO / "include" / "constants" / "flags.h"

MT_GRASS, MT_TALL, MT_WATER, MT_SAND = 0x001, 0x00D, 0x170, 0x121
MT_TREE = (0x1D4, 0x1D5, 0x1DC, 0x1DD)
MT_ROCK, MT_LEDGE_A, MT_LEDGE_B = 0x079, 0x0D5, 0x0D6
IN_FLOOR, IN_WALL, IN_DOOR = 0x201, 0x21A, 0x20E

# Land IDs (TownsAndRoutes / GreatMarsh_DP)
R212N = [[85], [86], [87]]  # 32x96 origin (448,736)
R212S = [[88, 89, 90, 91]]  # 128x32 origin (448,832)
MARSH = [[383, 384], [385, 386], [387, 388]]  # 64x96

GFX = {
    "OBJ_EVENT_GFX_RICH_BOY": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_LADY": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_GENTLEMAN": "OBJ_EVENT_GFX_GENTLEMAN",
    "OBJ_EVENT_GFX_SOCIALITE": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_POLICEMAN": "OBJ_EVENT_GFX_POLICEMAN",
    "OBJ_EVENT_GFX_FISHERMAN": "OBJ_EVENT_GFX_FISHERMAN",
    "OBJ_EVENT_GFX_ACE_TRAINER_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_ACE_TRAINER_F": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_SCIENTIST_M": "OBJ_EVENT_GFX_SCIENTIST_1",
    "OBJ_EVENT_GFX_COLLECTOR": "OBJ_EVENT_GFX_MANIAC",
    "OBJ_EVENT_GFX_PARASOL_LADY": "OBJ_EVENT_GFX_WOMAN_2",
}


def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]


def attr_to_mt(v: int, x: int, y: int) -> int:
    col, beh = (v >> 15) & 1, v & 0xFF
    if col:
        return MT_TREE[(y & 1) * 2 + (x & 1)]
    if beh in (0x02, 0x03):
        return MT_TALL
    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
        return MT_WATER
    if beh == 0x21:
        return MT_SAND
    if beh == 0x3B:
        return MT_LEDGE_A if (x & 1) == 0 else MT_LEDGE_B
    if beh in (0x38, 0x39, 0x3A):
        return MT_ROCK
    return MT_GRASS


def stitch(chunks: list[list[int]]) -> list[list[int]]:
    rows, cols = len(chunks), len(chunks[0])
    out = [[0] * (cols * 32) for _ in range(rows * 32)]
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    out[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return out


def attrs_to_grid(attr: list[list[int]]) -> list[list[int]]:
    return [
        [attr_to_mt(attr[y][x], x, y) for x in range(len(attr[0]))]
        for y in range(len(attr))
    ]


def pack(grid: list[list[int]]) -> bytes:
    h, w = len(grid), len(grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            struct.pack_into("<H", out, (y * w + x) * 2, grid[y][x] & 0x3FF)
    return bytes(out)


def open_path(grid, pts, mt=MT_GRASS):
    blocked = set(MT_TREE) | {MT_ROCK, IN_WALL}
    for x, y in pts:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = mt
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] in blocked:
                    grid[ny][nx] = mt


def stamp_door(grid, x, y):
    facade = [
        [0x210, 0x211, 0x211, 0x212],
        [0x218, 0x219, 0x219, 0x21A],
        [0x222, 0x230, 0x240, 0x221],
    ]
    top, left = y - 2, x - 1
    for dy, row in enumerate(facade):
        for dx, mt in enumerate(row):
            gx, gy = left + dx, top + dy
            if 0 <= gy < len(grid) and 0 <= gx < len(grid[0]):
                grid[gy][gx] = mt


def layout_const(name: str) -> str:
    return "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")


def write_layout(name: str, w: int, h: int, primary: str, secondary: str, blob: bytes):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blob)
    border_src = LAYOUTS / "Route203" / "border.bin"
    if border_src.exists():
        (folder / "border.bin").write_bytes(border_src.read_bytes())
    else:
        (folder / "border.bin").write_bytes(bytes(16))
    lid = layout_const(name)
    meta = json.loads(LAYOUTS_JSON.read_text())
    layouts = meta["layouts"]
    entry = {
        "id": lid,
        "name": lid,
        "width": w,
        "height": h,
        "primary_tileset": primary,
        "secondary_tileset": secondary,
        "border_filepath": f"data/layouts/{name}/border.bin",
        "blockdata_filepath": f"data/layouts/{name}/map.bin",
    }
    found = False
    for i, L in enumerate(layouts):
        if L.get("name") == lid or L.get("id") == lid:
            layouts[i] = {**L, **entry}
            found = True
            break
    if not found:
        # insert before layouts_table terminator null
        layouts.append(entry)
    LAYOUTS_JSON.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"layout {name} {w}x{h}")


def gen_layouts():
    g = stitch(R212N)
    mt = attrs_to_grid(g)
    open_path(mt, [(x, y) for x in range(8, 16) for y in range(0, 96)])
    open_path(mt, [(x, y) for x in range(4, 28) for y in range(30, 70)])
    stamp_door(mt, 22, 36)
    write_layout("Route212_North", 32, 96, "gTileset_General", "gTileset_Petalburg", pack(mt))

    g = stitch(R212S)
    mt = attrs_to_grid(g)
    open_path(mt, [(x, y) for x in range(0, 128) for y in range(10, 22)])
    open_path(mt, [(x, y) for x in range(100, 128) for y in range(0, 32)])  # east to Pastoria
    stamp_door(mt, 69, 14)
    write_layout("Route212_South", 128, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    g = stitch(MARSH)
    mt = attrs_to_grid(g)
    open_path(mt, [(x, y) for x in range(20, 44) for y in range(80, 96)])  # south mouth
    open_path(mt, [(x, y) for x in range(8, 56) for y in range(8, 88)])
    write_layout("GreatMarsh", 64, 96, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # Tiny mansion stub + marsh lookout reuse shop
    indoor = [[IN_WALL] * 12 for _ in range(10)]
    for y in range(1, 9):
        for x in range(1, 11):
            indoor[y][x] = IN_FLOOR
    indoor[8][5] = IN_DOOR
    indoor[8][6] = IN_DOOR
    write_layout("PokemonMansion_Stub", 12, 10, "gTileset_Building", "gTileset_GenericBuilding", pack(indoor))
    house = [
        [
            IN_WALL
            if y in (0, 7) or x in (0, 9)
            else (IN_DOOR if y == 7 and x in (4, 5) else IN_FLOOR)
            for x in range(10)
        ]
        for y in range(8)
    ]
    write_layout("Route212_House", 10, 8, "gTileset_Building", "gTileset_GenericBuilding", pack(house))


def obj(gfx, x, y, script, trainer="TRAINER_TYPE_NONE", sight="0", movement="MOVEMENT_TYPE_FACE_DOWN", flag="0"):
    return {
        "graphics_id": gfx,
        "x": int(x),
        "y": int(y),
        "elevation": 3,
        "movement_type": movement,
        "movement_range_x": 0,
        "movement_range_y": 0,
        "trainer_type": trainer,
        "trainer_sight_or_berry_tree_id": str(sight),
        "script": script,
        "flag": flag,
    }


def warp(x, y, dest, wid):
    return {"x": int(x), "y": int(y), "elevation": 0, "dest_map": dest, "dest_warp_id": str(wid)}


def outdoor_base(mid, name, layout, mapsec, weather="WEATHER_SUNNY", mtype="MAP_TYPE_ROUTE"):
    return {
        "id": mid,
        "name": name,
        "layout": layout,
        "music": "MUS_PL_ROUTE203",
        "night_music": "MUS_PL_ROUTE203",
        "region": "REGION_HOENN",
        "region_map_section": mapsec,
        "requires_flash": False,
        "weather": weather,
        "map_type": mtype,
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [],
        "object_events": [],
        "warp_events": [],
        "coord_events": [],
        "bg_events": [],
    }


def write_map(name: str, data: dict, scripts: str):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("map", name)


def ensure_trainer(tid: str, level: int, cls: str, pic: str, mons: list[tuple[str, int]]):
    defined = set(re.findall(r"#define (TRAINER_[A-Z0-9_]+)\s+", OPP.read_text()))
    if tid not in defined:
        ids = [int(x) for x in re.findall(r"#define TRAINER_[A-Z0-9_]+\s+(\d+)\b", OPP.read_text())]
        nid = max(i for i in ids if i < 2000) + 1
        if nid >= 1024:
            raise SystemExit("trainer cap full")
        text = OPP.read_text()
        text = text.replace(
            "#define TRAINERS_COUNT_EMERALD",
            f"#define {tid}                    {nid} // Sinnoh M21\n\n#define TRAINERS_COUNT_EMERALD",
            1,
        )
        text = re.sub(
            r"#define TRAINERS_COUNT_EMERALD\s+\d+",
            f"#define TRAINERS_COUNT_EMERALD     {nid + 1}",
            text,
            count=1,
        )
        OPP.write_text(text)
    party = PARTY.read_text()
    if f"=== {tid} ===" in party:
        return
    name = tid.split("_")[-1][:10].title()
    lines = [
        f"=== {tid} ===",
        f"Name: {name}",
        f"Class: {cls}",
        f"Pic: {pic}",
        "Gender: Male",
        "Music: Male",
        "Double Battle: No",
        "AI: Check Bad Move",
        "",
    ]
    for sp, lv in mons:
        lines += [sp, f"Level: {lv}", "IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe", "- Tackle", ""]
    PARTY.write_text(party.rstrip() + "\n\n" + "\n".join(lines) + "\n")


def party_for(tid: str, level: int) -> tuple[str, str, list[tuple[str, int]]]:
    u = tid.upper()
    if "FISHERMAN" in u or "FISHER" in u:
        return "Fisherman", "Fisherman", [("Magikarp", level), ("Gyarados", level)]
    if "RANGER" in u and "F" in u.split("_")[-1]:
        return "Cooltrainer", "Cooltrainer F", [("Staravia", level), ("Roselia", level - 1)]
    if "RANGER" in u or "ACE" in u:
        return "Cooltrainer", "Cooltrainer M", [("Staravia", level), ("Floatzel", level - 1)]
    if "SCIENTIST" in u:
        return "Scientist Frlg", "Scientist Frlg", [("Kadabra", level), ("Magnemite", level - 1)]
    if "COLLECTOR" in u:
        return "Collector", "Collector", [("Mr. Mime", level)]
    if "PARASOL" in u:
        return "Parasol Lady", "Parasol Lady", [("Surskit", level), ("Wooper", level)]
    if "POLICEMAN" in u or "OFFICER" in u:
        return "Gentleman", "Gentleman", [("Houndour", level), ("Growlithe", level)]
    if "GENTLEMAN" in u:
        return "Gentleman", "Gentleman", [("Chatot", level)]
    if "SOCIALITE" in u or "LADY" in u:
        return "Lady", "Lady", [("Clefairy", level)]
    if "RICH_BOY" in u:
        return "Rich Boy", "Rich Boy", [("Mime Jr.", level)]
    return "Youngster", "Youngster", [("Starly", level), ("Bidoof", level)]


def face(dir_name: str | None) -> str:
    return {
        "DIR_NORTH": "MOVEMENT_TYPE_FACE_UP",
        "DIR_SOUTH": "MOVEMENT_TYPE_FACE_DOWN",
        "DIR_WEST": "MOVEMENT_TYPE_FACE_LEFT",
        "DIR_EAST": "MOVEMENT_TYPE_FACE_RIGHT",
    }.get(dir_name or "", "MOVEMENT_TYPE_FACE_DOWN")


def place_plat_trainers(em: str, plat: str, origin: tuple[int, int], level: int) -> tuple[list, str]:
    pe = json.loads((PLAT_MAPS / plat / "events.json").read_text())
    ox, oz = origin
    objs = []
    scripts = f"{em}_MapScripts::\n\t.byte 0\n\n"
    for po in pe.get("object_events") or []:
        tr = po.get("trainer") or {}
        tid_plat = tr.get("id")
        if not tid_plat:
            continue
        tid = tid_plat if tid_plat.startswith("TRAINER_") else f"TRAINER_{tid_plat}"
        # Unique Sinnoh alias if name collides with emerald stock later — keep plat id
        cls, pic, mons = party_for(tid, level)
        ensure_trainer(tid, level, cls, pic, mons)
        short = tid.replace("TRAINER_", "").title().replace("_", "")
        label = f"{em}_EventScript_{short}"
        lx, ly = po["x"] - ox, po["z"] - oz
        if not (0 <= lx < 200 and 0 <= ly < 200):
            continue
        gfx = GFX.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_YOUNGSTER")
        objs.append(
            obj(
                gfx,
                lx,
                ly,
                label,
                trainer="TRAINER_TYPE_NORMAL",
                sight=str(tr.get("sight_range") or 2),
                movement=face(po.get("initial_dir")),
            )
        )
        scripts += (
            f"{label}::\n"
            f"\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
            f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n"
            f"\tend\n\n"
            f"{label}_Intro:\n"
            f'\t.string "A battle on this stretch will keep\\n"\n'
            f'\t.string "both of us sharp.$"\n\n'
            f"{label}_Defeat:\n"
            f'\t.string "Clean hit. I will remember that.$"\n\n'
            f"{label}_After:\n"
            f'\t.string "Keep your pace. The marsh and the\\n"\n'
            f'\t.string "mansion both reward patience.$"\n\n'
        )
    return objs, scripts


def register_group(group: str, names: list[str]):
    g = json.loads(GROUPS.read_text())
    lst = g.setdefault(group, [])
    for n in names:
        if n not in lst:
            lst.append(n)
    if group not in g.get("group_order", []):
        # map_groups uses top-level keys; group_order may be separate
        pass
    GROUPS.write_text(json.dumps(g, indent=2) + "\n")


def include_scripts(names: list[str]):
    text = EVENT_SCRIPTS.read_text()
    for n in names:
        inc = f'\t.include "data/maps/{n}/scripts.inc"'
        if inc not in text:
            text = text.rstrip() + "\n" + inc + "\n"
    EVENT_SCRIPTS.write_text(text)


def scaffold_maps():
    # Route 212 North
    objs, scripts = place_plat_trainers("Route212_North", "route_212_north", (448, 736), 28)
    data = outdoor_base("MAP_ROUTE212_NORTH", "Route212_North", "LAYOUT_ROUTE212_NORTH", "MAPSEC_ROUTE_212")
    data["connections"] = [
        {"map": "MAP_ROUTE212_SOUTH", "offset": 0, "direction": "down"},
    ]
    data["warp_events"] = [
        warp(10, 0, "MAP_HEARTHOME_CITY_ROUTE212_GATE", 2),
        warp(11, 0, "MAP_HEARTHOME_CITY_ROUTE212_GATE", 3),
        warp(22, 36, "MAP_POKEMON_MANSION_STUB", 0),
    ]
    data["object_events"] = objs
    data["bg_events"] = [
        {"type": "sign", "x": 14, "y": 8, "elevation": 0,
         "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
         "script": "Route212_North_EventScript_Sign"}
    ]
    scripts += (
        "Route212_North_EventScript_Sign::\n"
        "\tmsgbox Route212_North_Text_Sign, MSGBOX_SIGN\n\tend\n\n"
        "Route212_North_Text_Sign:\n"
        '\t.string "Route 212\\n"\n'
        '\t.string "North to Hearthome City$"\n'
    )
    write_map("Route212_North", data, scripts)

    # Route 212 South
    objs, scripts = place_plat_trainers("Route212_South", "route_212_south", (448, 832), 26)
    data = outdoor_base("MAP_ROUTE212_SOUTH", "Route212_South", "LAYOUT_ROUTE212_SOUTH", "MAPSEC_ROUTE_212")
    data["connections"] = [
        {"map": "MAP_ROUTE212_NORTH", "offset": 0, "direction": "up"},
        {"map": "MAP_PASTORIA_CITY", "offset": -32, "direction": "right"},  # Pastoria local y vs R212S
    ]
    data["warp_events"] = [warp(69, 14, "MAP_ROUTE212_HOUSE", 0)]
    data["object_events"] = objs
    write_map("Route212_South", data, scripts)

    # Great Marsh (fog; Defog clears)
    data = outdoor_base(
        "MAP_GREAT_MARSH",
        "GreatMarsh",
        "LAYOUT_GREAT_MARSH",
        "MAPSEC_GREAT_MARSH",
        weather="WEATHER_FOG_HORIZONTAL",
        mtype="MAP_TYPE_ROUTE",
    )
    data["warp_events"] = [
        warp(30, 95, "MAP_PASTORIA_CITY_GREAT_MARSH_GATE", 2),
        warp(31, 95, "MAP_PASTORIA_CITY_GREAT_MARSH_GATE", 3),
    ]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_CAMPER", 28, 70, "GreatMarsh_EventScript_Lookout", movement="MOVEMENT_TYPE_FACE_DOWN"),
    ]
    scripts = (
        "GreatMarsh_MapScripts::\n\t.byte 0\n\n"
        "GreatMarsh_EventScript_Lookout::\n"
        "\tmsgbox GreatMarsh_Text_Lookout, MSGBOX_NPC\n\tend\n\n"
        "GreatMarsh_Text_Lookout:\n"
        '\t.string "Fog hugs every reed here.\\n"\n'
        '\t.string "A sharp gust from a POKéMON clears\\l"\n'
        '\t.string "the worst of it.$"\n'
    )
    write_map("GreatMarsh", data, scripts)

    # Pokemon Mansion stub
    data = {
        "id": "MAP_POKEMON_MANSION_STUB",
        "name": "PokemonMansion_Stub",
        "layout": "LAYOUT_POKEMON_MANSION_STUB",
        "music": "MUS_PL_JUBILIFE",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_POKEMON_MANSION",
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": [
            obj("OBJ_EVENT_GFX_OLD_MAN", 5, 4, "PokemonMansion_Stub_EventScript_Butler"),
        ],
        "warp_events": [
            warp(5, 8, "MAP_ROUTE212_NORTH", 2),
            warp(6, 8, "MAP_ROUTE212_NORTH", 2),
        ],
        "coord_events": [],
        "bg_events": [],
    }
    scripts = (
        "PokemonMansion_Stub_MapScripts::\n\t.byte 0\n\n"
        "PokemonMansion_Stub_EventScript_Butler::\n"
        "\tmsgbox PokemonMansion_Stub_Text_Butler, MSGBOX_NPC\n\tend\n\n"
        "PokemonMansion_Stub_Text_Butler:\n"
        '\t.string "The trophy garden is quiet today.\\n"\n'
        '\t.string "Do enjoy the grounds, but mind the fog\\l"\n'
        '\t.string "on the marsh road.$"\n'
    )
    write_map("PokemonMansion_Stub", data, scripts)

    # Route 212 house
    data = {
        "id": "MAP_ROUTE212_HOUSE",
        "name": "Route212_House",
        "layout": "LAYOUT_ROUTE212_HOUSE",
        "music": "MUS_PL_JUBILIFE",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_212",
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": False,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": [
            obj("OBJ_EVENT_GFX_WOMAN_2", 4, 3, "Route212_House_EventScript_Woman"),
        ],
        "warp_events": [
            warp(4, 7, "MAP_ROUTE212_SOUTH", 0),
            warp(5, 7, "MAP_ROUTE212_SOUTH", 0),
        ],
        "coord_events": [],
        "bg_events": [],
    }
    scripts = (
        "Route212_House_MapScripts::\n\t.byte 0\n\n"
        "Route212_House_EventScript_Woman::\n"
        "\tmsgbox Route212_House_Text_Woman, MSGBOX_NPC\n\tend\n\n"
        "Route212_House_Text_Woman:\n"
        '\t.string "Marsh air rolls in by evening.\\n"\n'
        '\t.string "I keep the windows shut tight.$"\n'
    )
    write_map("Route212_House", data, scripts)

    register_group("gMapGroup_TownsAndRoutes", ["Route212_North", "Route212_South", "GreatMarsh"])
    register_group("gMapGroup_IndoorM21", ["PokemonMansion_Stub", "Route212_House"])
    # ensure group_order if present
    g = json.loads(GROUPS.read_text())
    if "group_order" in g and "gMapGroup_IndoorM21" not in g["group_order"]:
        g["group_order"].append("gMapGroup_IndoorM21")
        GROUPS.write_text(json.dumps(g, indent=2) + "\n")
    include_scripts(
        ["Route212_North", "Route212_South", "GreatMarsh", "PokemonMansion_Stub", "Route212_House"]
    )


def patch_existing():
    # Pastoria left connection to Route212_South
    p = MAPS / "PastoriaCity" / "map.json"
    j = json.loads(p.read_text())
    conns = j.get("connections") or []
    if not any(c.get("map") == "MAP_ROUTE212_SOUTH" for c in conns):
        # R212S is 128 wide; Pastoria 64. Align so Pastoria west meets R212S east.
        # Pastoria world (576,800); R212S (448,832) → vertical offset = 800-832 = -32
        conns.append({"map": "MAP_ROUTE212_SOUTH", "offset": 32, "direction": "left"})
        j["connections"] = conns
        p.write_text(json.dumps(j, indent=2) + "\n")

    # Hearthome Route212 gate: open south to Route212_North after Fen Badge
    gate = MAPS / "HearthomeCity_Route212Gate"
    gj = json.loads((gate / "map.json").read_text())
    # Seaside cycling gate layout: left pair = city, right pair = route (both y=5)
    gj["warp_events"] = [
        warp(1, 5, "MAP_HEARTHOME_CITY", 16),
        warp(2, 5, "MAP_HEARTHOME_CITY", 16),
        warp(12, 5, "MAP_ROUTE212_NORTH", 0),
        warp(13, 5, "MAP_ROUTE212_NORTH", 1),
    ]
    # Remove closed coord blockers or gate them on badge
    coords = []
    for c in gj.get("coord_events") or []:
        if "Closed" in (c.get("script") or ""):
            c = dict(c)
            c["var"] = "VAR_TEMP_1"
            c["script"] = "HearthomeCity_Route212Gate_EventScript_NeedFen"
        coords.append(c)
    gj["coord_events"] = coords
    (gate / "map.json").write_text(json.dumps(gj, indent=2) + "\n")
    gs = (gate / "scripts.inc").read_text()
    if "NeedFen" not in gs:
        gs = gs.replace(
            "HearthomeCity_Route212Gate_EventScript_Closed::",
            "HearthomeCity_Route212Gate_EventScript_NeedFen::\n"
            "\tgoto_if_set FLAG_BADGE05_GET, HearthomeCity_Route212Gate_EventScript_Open\n"
            "HearthomeCity_Route212Gate_EventScript_Closed::",
            1,
        )
        gs += (
            "\nHearthomeCity_Route212Gate_EventScript_Open::\n"
            "\treleaseall\n"
            "\tend\n\n"
            "HearthomeCity_Route212Gate_EventScript_Guard::\n"
            "\tgoto_if_set FLAG_BADGE05_GET, HearthomeCity_Route212Gate_EventScript_GuardOpen\n"
            "\tmsgbox HearthomeCity_Route212Gate_Text_Guard, MSGBOX_NPC\n"
            "\tend\n\n"
            "HearthomeCity_Route212Gate_EventScript_GuardOpen::\n"
            "\tmsgbox HearthomeCity_Route212Gate_Text_GuardOpen, MSGBOX_NPC\n"
            "\tend\n\n"
            "HearthomeCity_Route212Gate_Text_GuardOpen:\n"
            '\t.string "Fen Badge, hm? The marsh road is\\n"\n'
            '\t.string "yours to walk.$"\n'
        )
        # Fix Closed text
        gs = gs.replace(
            "HearthomeCity_Route212Gate_Text_Closed:\n",
            "HearthomeCity_Route212Gate_Text_Closed:\n"
            # keep existing if present
        )
        if "need the Fen Badge" not in gs:
            gs = re.sub(
                r"HearthomeCity_Route212Gate_Text_Closed:\n(?:\t\.string .*\n)+",
                "HearthomeCity_Route212Gate_Text_Closed:\n"
                '\t.string "Hold it. Marsh country is no place\\n"\n'
                '\t.string "for trainers without a Fen Badge.$"\n\n',
                gs,
            )
        (gate / "scripts.inc").write_text(gs)

    # Great Marsh gate: allow entry after Defog HM / Fen Badge
    mg = MAPS / "PastoriaCity_GreatMarshGate"
    mj = json.loads((mg / "map.json").read_text())
    warps = mj.get("warp_events") or []
    warps = [w for w in warps if w.get("dest_map") != "MAP_GREAT_MARSH"]
    warps += [
        warp(6, 1, "MAP_GREAT_MARSH", 0),
        warp(7, 1, "MAP_GREAT_MARSH", 0),
    ]
    mj["warp_events"] = warps
    for c in mj.get("coord_events") or []:
        if "SafariComingSoon" in (c.get("script") or ""):
            c["script"] = "PastoriaCity_GreatMarshGate_EventScript_EnterCheck"
            c["var"] = "VAR_TEMP_1"
    (mg / "map.json").write_text(json.dumps(mj, indent=2) + "\n")
    ms = (mg / "scripts.inc").read_text()
    if "EnterCheck" not in ms:
        ms += (
            "\nPastoriaCity_GreatMarshGate_EventScript_EnterCheck::\n"
            "\tgoto_if_set FLAG_GOT_PASTORIA_HM_DEFOG, PastoriaCity_GreatMarshGate_EventScript_AllowMarsh\n"
            "\tmsgbox PastoriaCity_GreatMarshGate_Text_SafariComingSoon, MSGBOX_DEFAULT\n"
            "\tclosemessage\n"
            "\tapplymovement OBJ_EVENT_ID_PLAYER, PastoriaCity_GreatMarshGate_Movement_PushSouth\n"
            "\twaitmovement 0\n"
            "\treleaseall\n"
            "\tend\n\n"
            "PastoriaCity_GreatMarshGate_EventScript_AllowMarsh::\n"
            "\treleaseall\n"
            "\tend\n"
        )
        # Update reception to give Defog after Fen Badge
        if "EventScript_GiveDefog" not in ms:
            ms = ms.replace(
                "PastoriaCity_GreatMarshGate_EventScript_Reception::\n"
                "\tlock\n"
                "\tfaceplayer\n"
                "\tmsgbox PastoriaCity_GreatMarshGate_Text_Reception, MSGBOX_DEFAULT\n"
                "\trelease\n"
                "\tend\n",
                "PastoriaCity_GreatMarshGate_EventScript_Reception::\n"
                "\tlock\n"
                "\tfaceplayer\n"
                "\tgoto_if_set FLAG_GOT_PASTORIA_HM_DEFOG, PastoriaCity_GreatMarshGate_EventScript_ReceptionAfter\n"
                "\tgoto_if_unset FLAG_BADGE05_GET, PastoriaCity_GreatMarshGate_EventScript_ReceptionNoBadge\n"
                "\tmsgbox PastoriaCity_GreatMarshGate_Text_OfferDefog, MSGBOX_DEFAULT\n"
                "\tgiveitem ITEM_HM_DEFOG\n"
                "\tsetflag FLAG_GOT_PASTORIA_HM_DEFOG\n"
                "\tmsgbox PastoriaCity_GreatMarshGate_Text_ExplainDefog, MSGBOX_DEFAULT\n"
                "\trelease\n"
                "\tend\n\n"
                "PastoriaCity_GreatMarshGate_EventScript_ReceptionNoBadge::\n"
                "\tmsgbox PastoriaCity_GreatMarshGate_Text_Reception, MSGBOX_DEFAULT\n"
                "\trelease\n"
                "\tend\n\n"
                "PastoriaCity_GreatMarshGate_EventScript_ReceptionAfter::\n"
                "\tmsgbox PastoriaCity_GreatMarshGate_Text_ReceptionAfter, MSGBOX_DEFAULT\n"
                "\trelease\n"
                "\tend\n\n"
                "PastoriaCity_GreatMarshGate_Text_OfferDefog:\n"
                '\t.string "Fen Badge confirmed. The marsh fog\\n"\n'
                '\t.string "bows to a proper gust—take this.$"\n\n'
                "PastoriaCity_GreatMarshGate_Text_ExplainDefog:\n"
                '\t.string "HM05 Defog clears fog on the field\\n"\n'
                '\t.string "and unsettles foes who hide behind it.$"\n\n'
                "PastoriaCity_GreatMarshGate_Text_ReceptionAfter:\n"
                '\t.string "Watch your footing in the reeds.\\n"\n'
                '\t.string "Safari work picks up after a clear sky.$"\n\n',
            )
        (mg / "scripts.inc").write_text(ms)

    # Close path beyond M21: Route210 Cafe north remains fog-locked in M22.
    # Pastoria west gate facade already exists.


def main():
    if not PLAT_DATA.is_dir():
        raise SystemExit(f"missing platinum land data at {PLAT_DATA}")
    print("== gen layouts ==")
    gen_layouts()
    print("== scaffold maps ==")
    scaffold_maps()
    print("== patch existing ==")
    patch_existing()
    print("M21 build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
