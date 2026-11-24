#!/usr/bin/env python3
"""M22: Route 210 North (fog) + Celestic Town + HM Surf."""
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

MT_GRASS, MT_TALL, MT_WATER, MT_SAND = 0x001, 0x00D, 0x170, 0x121
MT_TREE = (0x1D4, 0x1D5, 0x1DC, 0x1DD)
MT_ROCK, MT_LEDGE_A, MT_LEDGE_B = 0x079, 0x0D5, 0x0D6
IN_FLOOR, IN_WALL, IN_DOOR = 0x201, 0x21A, 0x20E

R210N = [[63, 64, 65]]  # 96x32 origin (480,512)
CELESTIC = [[62]]  # 32x32 origin (448,512)

GFX = {
    "OBJ_EVENT_GFX_NINJA_BOY": "OBJ_EVENT_GFX_NINJA_BOY",
    "OBJ_EVENT_GFX_ACE_TRAINER_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_ACE_TRAINER_F": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_BLACK_BELT": "OBJ_EVENT_GFX_BLACK_BELT",
    "OBJ_EVENT_GFX_BATTLE_GIRL": "OBJ_EVENT_GFX_RUNNING_TRIATHLETE_F",
    "OBJ_EVENT_GFX_HIKER": "OBJ_EVENT_GFX_HIKER",
    "OBJ_EVENT_GFX_YOUNGSTER": "OBJ_EVENT_GFX_YOUNGSTER",
    "OBJ_EVENT_GFX_LASS": "OBJ_EVENT_GFX_LASS",
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


def stitch(chunks):
    rows, cols = len(chunks), len(chunks[0])
    out = [[0] * (cols * 32) for _ in range(rows * 32)]
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    out[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return out


def pack(grid):
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


def paint_from_attrs(grid, chunks):
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    x, y = cx * 32 + lx, cy * 32 + ly
                    v = attrs[ly * 32 + lx]
                    beh = v & 0xFF
                    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
                        grid[y][x] = MT_WATER


def write_layout(name, w, h, primary, secondary, blob):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blob)
    src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(src.read_bytes() if src.exists() else bytes(8))
    lid = "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")
    lname = f"{name}_Layout"
    meta = json.loads(LAYOUTS_JSON.read_text())
    entry = {
        "id": lid,
        "name": lname,
        "width": w,
        "height": h,
        "primary_tileset": primary,
        "secondary_tileset": secondary,
        "border_filepath": f"data/layouts/{name}/border.bin",
        "blockdata_filepath": f"data/layouts/{name}/map.bin",
        "layout_version": "emerald",
    }
    layouts = meta["layouts"]
    for i, L in enumerate(layouts):
        if L.get("id") == lid:
            layouts[i] = entry
            break
    else:
        layouts.append(entry)
    LAYOUTS_JSON.write_text(json.dumps(meta, indent=2) + "\n")
    print("layout", name, w, h)


def obj(gfx, x, y, script, trainer="TRAINER_TYPE_NONE", sight="0", movement="MOVEMENT_TYPE_FACE_DOWN"):
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
        "flag": "0",
    }


def warp(x, y, dest, wid):
    return {"x": int(x), "y": int(y), "elevation": 0, "dest_map": dest, "dest_warp_id": str(wid)}


def ensure_trainer(tid, level, cls, pic, mons):
    defined = set(re.findall(r"#define (TRAINER_[A-Z0-9_]+)\s+", OPP.read_text()))
    if tid not in defined:
        ids = [int(x) for x in re.findall(r"#define TRAINER_[A-Z0-9_]+\s+(\d+)\b", OPP.read_text())]
        nid = max(i for i in ids if i < 2000) + 1
        text = OPP.read_text()
        text = text.replace(
            "#define TRAINERS_COUNT_EMERALD",
            f"#define {tid}                    {nid} // Sinnoh M22\n\n#define TRAINERS_COUNT_EMERALD",
            1,
        )
        text = re.sub(
            r"#define TRAINERS_COUNT_EMERALD\s+\d+",
            f"#define TRAINERS_COUNT_EMERALD     {nid + 1}",
            text,
            count=1,
        )
        OPP.write_text(text)
    if f"=== {tid} ===" in PARTY.read_text():
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
    PARTY.write_text(PARTY.read_text().rstrip() + "\n\n" + "\n".join(lines) + "\n")


def party_for(tid, level):
    u = tid.upper()
    if "NINJA" in u:
        return "Ninja Boy", "Ninja Boy", [("Zubat", level), ("Croagunk", level - 1)]
    if "BLACK_BELT" in u:
        return "Black Belt", "Black Belt", [("Machop", level), ("Meditite", level)]
    if "BATTLE_GIRL" in u:
        return "Battle Girl", "Battle Girl", [("Meditite", level)]
    if "HIKER" in u:
        return "Hiker", "Hiker", [("Geodude", level), ("Onix", level)]
    if "ACE" in u or "RANGER" in u:
        return "Cooltrainer", "Cooltrainer M", [("Staravia", level), ("Floatzel", level - 1)]
    if "LASS" in u:
        return "Lass", "Lass", [("Budew", level)]
    return "Youngster", "Youngster", [("Starly", level), ("Bidoof", level)]


def face(d):
    return {
        "DIR_NORTH": "MOVEMENT_TYPE_FACE_UP",
        "DIR_SOUTH": "MOVEMENT_TYPE_FACE_DOWN",
        "DIR_WEST": "MOVEMENT_TYPE_FACE_LEFT",
        "DIR_EAST": "MOVEMENT_TYPE_FACE_RIGHT",
    }.get(d or "", "MOVEMENT_TYPE_FACE_DOWN")


def place_all(em, plat, origin, wmax, hmax, level):
    pe = json.loads((PLAT_MAPS / plat / "events.json").read_text())
    ox, oz = origin
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"] - ox), int(po["z"] - oz)
        if not (0 <= lx < wmax and 0 <= ly < hmax) or (lx, ly) in occupied:
            continue
        tr = po.get("trainer") or {}
        tid_plat = tr.get("id")
        if tid_plat:
            tid = tid_plat if tid_plat.startswith("TRAINER_") else f"TRAINER_{tid_plat}"
            cls, pic, mons = party_for(tid, level)
            ensure_trainer(tid, level, cls, pic, mons)
            short = tid.replace("TRAINER_", "").title().replace("_", "")
            # Index keeps labels unique when Platinum reuses a trainer id/name.
            label = f"{em}_EventScript_{short}_{n}"
            gfx = GFX.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_YOUNGSTER")
            objs.append(
                obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2), movement=face(po.get("initial_dir")))
            )
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f"{label}_Intro:\n\t.string \"Fog or clear skies, I still want\\n\"\n\t.string \"a proper battle.$\"\n\n"
                f"{label}_Defeat:\n\t.string \"You cut through that cleanly.$\"\n\n"
                f"{label}_After:\n\t.string \"Celestic is just west of here.\\n\"\n\t.string \"Mind the mist on the cliffs.$\"\n\n"
            )
            n += 1
        else:
            label = f"{em}_EventScript_PlatNpc{n}"
            objs.append(obj("OBJ_EVENT_GFX_GIRL_1", lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f"{label}_Text:\n\t.string \"This fog used to scare me.\\n\"\n\t.string \"A strong gust from a POKéMON helps.$\"\n\n"
            )
            n += 1
        occupied.add((lx, ly))
    return objs, scripts


def write_map(name, data, scripts):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("map", name)


def indoor(name, mid, mapsec, exit_map, exit_wid, script_label, text):
    grid = [[IN_WALL if y in (0, 7) or x in (0, 9) else (IN_DOOR if y == 7 and x in (4, 5) else IN_FLOOR) for x in range(10)] for y in range(8)]
    write_layout(name, 10, 8, "gTileset_Building", "gTileset_GenericBuilding", pack(grid))
    data = {
        "id": mid,
        "name": name,
        "layout": f"LAYOUT_{re.sub(r'(?<!^)(?=[A-Z])', '_', name).upper().replace('__', '_')}",
        "music": "MUS_PL_JUBILIFE",
        "region": "REGION_HOENN",
        "region_map_section": mapsec,
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": False,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": [obj("OBJ_EVENT_GFX_OLD_WOMAN", 4, 3, script_label)],
        "warp_events": [warp(4, 7, exit_map, exit_wid), warp(5, 7, exit_map, exit_wid)],
        "coord_events": [],
        "bg_events": [],
    }
    scripts = (
        f"{name}_MapScripts::\n\t.byte 0\n\n"
        f"{script_label}::\n\tmsgbox {script_label}_Text, MSGBOX_NPC\n\tend\n\n"
        f"{script_label}_Text:\n\t.string \"{text}\"\n"
    )
    write_map(name, data, scripts)


def main():
    # Layouts
    attr = stitch(R210N)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(96)] for y in range(32)]
    paint_from_attrs(grid, R210N)
    open_path(grid, [(x, y) for x in range(0, 96) for y in range(12, 22)])
    open_path(grid, [(x, y) for x in range(60, 90) for y in range(28, 32)])  # south to R210S
    stamp_x, stamp_y = 84, 4
    # small door stamp
    for dy, row in enumerate([[0x210, 0x211, 0x212], [0x218, 0x219, 0x21A], [0x222, 0x230, 0x221]]):
        for dx, mt in enumerate(row):
            x, y = stamp_x - 1 + dx, stamp_y - 2 + dy
            if 0 <= y < 32 and 0 <= x < 96:
                grid[y][x] = mt
    write_layout("Route210_North", 96, 32, "gTileset_General", "gTileset_Petalburg", pack(grid))

    attr = stitch(CELESTIC)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(32)] for y in range(32)]
    paint_from_attrs(grid, CELESTIC)
    open_path(grid, [(x, y) for x in range(4, 28) for y in range(8, 28)])
    for door in ((15, 3), (2, 3), (25, 3), (6, 26), (15, 9), (24, 26)):
        x, y = door
        for dy, row in enumerate([[0x210, 0x211, 0x212], [0x218, 0x219, 0x21A], [0x222, 0x230, 0x221]]):
            for dx, mt in enumerate(row):
                gx, gy = x - 1 + dx, y - 2 + dy
                if 0 <= gy < 32 and 0 <= gx < 32:
                    grid[gy][gx] = mt
    write_layout("CelesticTown", 32, 32, "gTileset_General", "gTileset_Petalburg", pack(grid))

    # Maps
    objs, scripts = place_all("Route210_North", "route_210_north", (480, 512), 96, 32, 30)
    data = {
        "id": "MAP_ROUTE210_NORTH",
        "name": "Route210_North",
        "layout": "LAYOUT_ROUTE210_NORTH",
        "music": "MUS_PL_ROUTE203",
        "night_music": "MUS_PL_ROUTE203_NIGHT",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_210",
        "requires_flash": False,
        "weather": "WEATHER_FOG_HORIZONTAL",
        "map_type": "MAP_TYPE_ROUTE",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [
            {"map": "MAP_CELESTIC_TOWN", "offset": 0, "direction": "left"},
            {"map": "MAP_ROUTE210_SOUTH", "offset": 64, "direction": "down"},
        ],
        "object_events": objs,
        "warp_events": [warp(84, 4, "MAP_ROUTE210_WILMA_HOUSE", 0)],
        "coord_events": [],
        "bg_events": [],
    }
    write_map("Route210_North", data, scripts)

    objs, scripts = place_all("CelesticTown", "celestic_town", (448, 512), 32, 32, 28)
    # Grandma Surf giver replaces one NPC at southwest expert
    objs.append(obj("OBJ_EVENT_GFX_OLD_WOMAN", 14, 26, "CelesticTown_EventScript_GrandmaSurf", movement="MOVEMENT_TYPE_FACE_DOWN"))
    scripts += (
        "CelesticTown_EventScript_GrandmaSurf::\n"
        "\tlock\n\tfaceplayer\n"
        "\tgoto_if_set FLAG_RECEIVED_HM_SURF, CelesticTown_EventScript_GrandmaAfter\n"
        "\tgoto_if_unset FLAG_GOT_PASTORIA_HM_DEFOG, CelesticTown_EventScript_GrandmaWait\n"
        "\tmsgbox CelesticTown_Text_GrandmaOffer, MSGBOX_DEFAULT\n"
        "\tgiveitem ITEM_HM_SURF\n"
        "\tsetflag FLAG_RECEIVED_HM_SURF\n"
        "\tmsgbox CelesticTown_Text_GrandmaExplain, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        "CelesticTown_EventScript_GrandmaWait::\n"
        "\tmsgbox CelesticTown_Text_GrandmaWait, MSGBOX_DEFAULT\n\trelease\n\tend\n\n"
        "CelesticTown_EventScript_GrandmaAfter::\n"
        "\tmsgbox CelesticTown_Text_GrandmaAfter, MSGBOX_DEFAULT\n\trelease\n\tend\n\n"
        "CelesticTown_Text_GrandmaOffer:\n"
        '\t.string "You cleared the fog to reach us.\\n"\n'
        '\t.string "Take this—the water roads open next.$"\n\n'
        "CelesticTown_Text_GrandmaExplain:\n"
        '\t.string "HM03 Surf lets a POKéMON ferry you\\n"\n'
        '\t.string "across deep water. Use it wisely.$"\n\n'
        "CelesticTown_Text_GrandmaWait:\n"
        '\t.string "The cliffs stay misty until someone\\n"\n'
        '\t.string "brings a proper Defog from Pastoria.$"\n\n'
        "CelesticTown_Text_GrandmaAfter:\n"
        '\t.string "Canalave lies west across the water.\\n"\n'
        '\t.string "Iron Island waits beyond the harbor.$"\n\n'
    )
    data = {
        "id": "MAP_CELESTIC_TOWN",
        "name": "CelesticTown",
        "layout": "LAYOUT_CELESTIC_TOWN",
        "music": "MUS_PL_JUBILIFE",
        "night_music": "MUS_PL_JUBILIFE_NIGHT",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_SOLACEON_TOWN",
        "requires_flash": False,
        "weather": "WEATHER_SUNNY",
        "map_type": "MAP_TYPE_TOWN",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [
            {"map": "MAP_ROUTE210_NORTH", "offset": 0, "direction": "right"},
        ],
        "object_events": objs,
        "warp_events": [
            warp(15, 3, "MAP_CELESTIC_NORTH_HOUSE", 0),
            warp(2, 3, "MAP_CELESTIC_NORTHWEST_HOUSE", 0),
            warp(25, 3, "MAP_CELESTIC_NORTHEAST_HOUSE", 0),
            warp(6, 26, "MAP_CELESTIC_SOUTHWEST_HOUSE", 0),
            warp(15, 9, "MAP_CELESTIC_CAVE_STUB", 0),
            warp(24, 26, "MAP_CELESTIC_POKEMON_CENTER_1F", 0),
        ],
        "coord_events": [],
        "bg_events": [],
    }
    write_map("CelesticTown", data, scripts)

    # Interiors (reuse tiny house layout pattern)
    for folder, mid, exit_wid, text in [
        ("Celestic_NorthHouse", "MAP_CELESTIC_NORTH_HOUSE", 0, "Our murals tell older stories than\\nany guidebook."),
        ("Celestic_NorthwestHouse", "MAP_CELESTIC_NORTHWEST_HOUSE", 1, "Cynthia grew up around these hills."),
        ("Celestic_NortheastHouse", "MAP_CELESTIC_NORTHEAST_HOUSE", 2, "Bring an open mind to the ruins."),
        ("Celestic_SouthwestHouse", "MAP_CELESTIC_SOUTHWEST_HOUSE", 3, "Tea tastes better after a foggy walk."),
        ("Route210_WilmaHouse", "MAP_ROUTE210_WILMA_HOUSE", 0, "Knit one, purl one—battles can wait."),
    ]:
        indoor(folder, mid, "MAPSEC_SOLACEON_TOWN", "MAP_CELESTIC_TOWN" if "Celestic" in folder else "MAP_ROUTE210_NORTH", exit_wid if "Celestic" in folder else 0,
               f"{folder}_EventScript_Npc", text.replace("\\n", "\\n"))

    # Fix indoor exit warps properly
    for folder, dest, wid in [
        ("Celestic_NorthHouse", "MAP_CELESTIC_TOWN", 0),
        ("Celestic_NorthwestHouse", "MAP_CELESTIC_TOWN", 1),
        ("Celestic_NortheastHouse", "MAP_CELESTIC_TOWN", 2),
        ("Celestic_SouthwestHouse", "MAP_CELESTIC_TOWN", 3),
        ("Route210_WilmaHouse", "MAP_ROUTE210_NORTH", 0),
    ]:
        p = MAPS / folder / "map.json"
        j = json.loads(p.read_text())
        j["warp_events"] = [warp(4, 7, dest, wid), warp(5, 7, dest, wid)]
        p.write_text(json.dumps(j, indent=2) + "\n")

    # Cave stub + PC reuse House1 / PokemonCenter
    cave = [[IN_WALL] * 12 for _ in range(10)]
    for y in range(1, 9):
        for x in range(1, 11):
            cave[y][x] = IN_FLOOR
    cave[8][5] = cave[8][6] = IN_DOOR
    write_layout("Celestic_Cave_Stub", 12, 10, "gTileset_Building", "gTileset_GenericBuilding", pack(cave))
    write_map(
        "Celestic_Cave_Stub",
        {
            "id": "MAP_CELESTIC_CAVE_STUB",
            "name": "Celestic_Cave_Stub",
            "layout": "LAYOUT_CELESTIC_CAVE_STUB",
            "music": "MUS_PL_LAKE",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_SOLACEON_TOWN",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_UNDERGROUND",
            "allow_cycling": False,
            "allow_escaping": True,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [obj("OBJ_EVENT_GFX_OLD_MAN", 5, 4, "Celestic_Cave_Stub_EventScript_Elder")],
            "warp_events": [warp(5, 8, "MAP_CELESTIC_TOWN", 4), warp(6, 8, "MAP_CELESTIC_TOWN", 4)],
            "coord_events": [],
            "bg_events": [],
        },
        "Celestic_Cave_Stub_MapScripts::\n\t.byte 0\n\n"
        "Celestic_Cave_Stub_EventScript_Elder::\n\tmsgbox Celestic_Cave_Stub_Text, MSGBOX_NPC\n\tend\n\n"
        "Celestic_Cave_Stub_Text:\n\t.string \"Paint and prayer share this chamber.\\n\"\n\t.string \"Leave only footprints.$\"\n",
    )

    # Pokemon Center: reuse layout
    write_map(
        "Celestic_PokemonCenter_1F",
        {
            "id": "MAP_CELESTIC_POKEMON_CENTER_1F",
            "name": "Celestic_PokemonCenter_1F",
            "layout": "LAYOUT_POKEMON_CENTER_1F",
            "music": "MUS_POKE_CENTER",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_SOLACEON_TOWN",
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
                obj("OBJ_EVENT_GFX_NURSE", 7, 2, "Celestic_PokemonCenter_1F_EventScript_Nurse"),
            ],
            "warp_events": [
                warp(6, 8, "MAP_CELESTIC_TOWN", 5),
                warp(7, 8, "MAP_CELESTIC_TOWN", 5),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "Celestic_PokemonCenter_1F_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, Celestic_PokemonCenter_1F_OnTransition\n\t.byte 0\n\n"
        "Celestic_PokemonCenter_1F_OnTransition::\n\tsetrespawn HEAL_LOCATION_CELESTIC_TOWN\n\tend\n\n"
        "Celestic_PokemonCenter_1F_EventScript_Nurse::\n\tsetvar VAR_0x800B, LOCALID_NURSE\n\tcall Common_EventScript_PkmnCenterNurse\n\twaitmessage\n\twaitbuttonpress\n\trelease\n\tend\n",
    )

    # Patch Route210_South connection up
    p = MAPS / "Route210_South" / "map.json"
    j = json.loads(p.read_text())
    conns = j.get("connections") or []
    conns = [c for c in conns if c.get("map") != "MAP_ROUTE210_NORTH"]
    conns.append({"map": "MAP_ROUTE210_NORTH", "offset": -64, "direction": "up"})
    j["connections"] = conns
    p.write_text(json.dumps(j, indent=2) + "\n")

    # Groups + includes
    g = json.loads(GROUPS.read_text())
    for n in ("Route210_North", "CelesticTown"):
        if n not in g["gMapGroup_TownsAndRoutes"]:
            g["gMapGroup_TownsAndRoutes"].append(n)
    indoor_names = [
        "Celestic_NorthHouse",
        "Celestic_NorthwestHouse",
        "Celestic_NortheastHouse",
        "Celestic_SouthwestHouse",
        "Route210_WilmaHouse",
        "Celestic_Cave_Stub",
        "Celestic_PokemonCenter_1F",
    ]
    g.setdefault("gMapGroup_IndoorM22", [])
    for n in indoor_names:
        if n not in g["gMapGroup_IndoorM22"]:
            g["gMapGroup_IndoorM22"].append(n)
    if "group_order" in g and "gMapGroup_IndoorM22" not in g["group_order"]:
        g["group_order"].append("gMapGroup_IndoorM22")
    GROUPS.write_text(json.dumps(g, indent=2) + "\n")

    es = EVENT_SCRIPTS.read_text()
    for n in ["Route210_North", "CelesticTown"] + indoor_names:
        inc = f'\t.include "data/maps/{n}/scripts.inc"'
        if inc not in es:
            es = es.rstrip() + "\n" + inc + "\n"
    EVENT_SCRIPTS.write_text(es)

    # Heal location - add if missing
    heal = REPO / "src" / "data" / "heal_locations.h"
    # skip if complex; nurse uses HEAL_LOCATION_CELESTIC_TOWN - need constant
    hl = REPO / "include" / "constants" / "heal_locations.h"
    if hl.exists() and "HEAL_LOCATION_CELESTIC_TOWN" not in hl.read_text():
        # Prefer reusing Solaceon heal to avoid table surgery
        pc = MAPS / "Celestic_PokemonCenter_1F" / "scripts.inc"
        pc.write_text(
            pc.read_text().replace("HEAL_LOCATION_CELESTIC_TOWN", "HEAL_LOCATION_SOLACEON_TOWN")
        )
        print("PC heal reused Solaceon")

    # Strip non-ascii from M22 scripts only (never touch the rest of the tree)
    for n in ["Route210_North", "CelesticTown"] + indoor_names:
        p = MAPS / n / "scripts.inc"
        if not p.exists():
            continue
        t = p.read_text()
        if any(ord(c) > 127 for c in t):
            p.write_text("".join(c if ord(c) < 128 else "-" for c in t))

    print("M22 build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
