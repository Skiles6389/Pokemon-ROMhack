#!/usr/bin/env python3
"""
M26: Veilstone Galactic HQ rematch path + Spear Pillar approach.

- Galactic HQ 1F from lands 520–521 (64x32 indoor-cave stitch) + upper stubs
- Spear Pillar 64x64 from lands 375–378 (EXACT outdoor)
- Mt Coronet upper stub links toward Spear Pillar; Distortion exit closed

Emerald tilesets only. Original dialogue. Trainer IVs 0.
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

MT_GRASS, MT_TALL, MT_WATER = 0x001, 0x00D, 0x170
MT_TREE = (0x1D4, 0x1D5, 0x1DC, 0x1DD)
MT_ROCK, MT_LEDGE_A, MT_LEDGE_B = 0x079, 0x0D5, 0x0D6
IN_FLOOR, IN_WALL, IN_DOOR = 0x201, 0x21A, 0x20E
MT_CAVE = 0x1A1  # fallarbor/cave-ish stand-in if present; else grass

HQ1F = [[520, 521]]
SPEAR = [[375, 376], [377, 378]]


def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]


def attr_to_mt(v, x, y, cave=False):
    col, beh = (v >> 15) & 1, v & 0xFF
    if col:
        return MT_ROCK if cave else MT_TREE[(y & 1) * 2 + (x & 1)]
    if beh in (0x02, 0x03):
        return MT_TALL
    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
        return MT_WATER
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


def paint_water(grid, chunks):
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    x, y = cx * 32 + lx, cy * 32 + ly
                    beh = attrs[ly * 32 + lx] & 0xFF
                    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
                        grid[y][x] = MT_WATER


def write_layout(name, w, h, primary, secondary, blob, lid=None):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blob)
    src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(src.read_bytes() if src.exists() else bytes(8))
    if lid is None:
        lid = "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")
    meta = json.loads(LAYOUTS_JSON.read_text())
    entry = {
        "id": lid,
        "name": f"{name}_Layout",
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
        if L.get("id") == lid or L.get("name") == entry["name"]:
            layouts[i] = entry
            break
    else:
        layouts.append(entry)
    LAYOUTS_JSON.write_text(json.dumps(meta, indent=2) + "\n")
    print("layout", name, w, h, lid)
    return lid


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


def ensure_flag(name, value_hex, comment):
    text = FLAGS.read_text()
    if name in text:
        return
    anchor = "FLAG_DEFEATED_JUPITER_LAKE_ACUITY"
    needle = f"#define {anchor}" if anchor in text else "#define FLAG_RECEIVED_SNOWPOINT_GYM_TM"
    if needle in text:
        text = text.replace(needle, f"#define {name}  {value_hex} // {comment}\n{needle}", 1)
    else:
        text += f"\n#define {name}  {value_hex} // {comment}\n"
    FLAGS.write_text(text)


def ensure_trainer(tid, level, cls, pic, mons, display_name=None):
    defined = set(re.findall(r"#define (TRAINER_[A-Z0-9_]+)\s+", OPP.read_text()))
    if tid not in defined:
        ids = [int(x) for x in re.findall(r"#define TRAINER_[A-Z0-9_]+\s+(\d+)\b", OPP.read_text())]
        nid = max(i for i in ids if i < 2000) + 1
        text = OPP.read_text()
        text = text.replace(
            "#define TRAINERS_COUNT_EMERALD",
            f"#define {tid}                    {nid} // Sinnoh M26\n\n#define TRAINERS_COUNT_EMERALD",
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
    name = display_name or tid.split("_")[-1][:10].title()
    lines = [
        f"=== {tid} ===",
        f"Name: {name}",
        f"Class: {cls}",
        f"Pic: {pic}",
        "Gender: Male",
        "Music: Male",
        "Double Battle: No",
        "AI: Basic Trainer",
        "",
    ]
    for sp, lv in mons:
        lines += [sp, f"Level: {lv}", "IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe", "- Tackle", ""]
    PARTY.write_text(PARTY.read_text().rstrip() + "\n\n" + "\n".join(lines) + "\n")


def write_map(name, data, scripts):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("map", name)


def indoor_room(name, mid, mapsec, exit_map, exit_wid, w=16, h=12):
    grid = [
        [IN_WALL if y in (0, h - 1) or x in (0, w - 1) else (IN_DOOR if y == h - 1 and x in (w // 2 - 1, w // 2) else IN_FLOOR)
         for x in range(w)]
        for y in range(h)
    ]
    # north door optional for multi-floor
    if name.endswith("_2F") or name.endswith("_3F") or "Cyrus" in name:
        for x in (w // 2 - 1, w // 2):
            grid[0][x] = IN_DOOR
    lid = write_layout(name, w, h, "gTileset_Building", "gTileset_Facility", pack(grid))
    return lid


def scrub(names):
    for n in names:
        p = MAPS / n / "scripts.inc"
        if p.exists():
            t = p.read_text()
            if any(ord(c) > 127 for c in t):
                p.write_text("".join(c if ord(c) < 128 else "-" for c in t))


def main():
    ensure_flag("FLAG_DEFEATED_CYRUS_GALACTIC_HQ", "0x2B0", "Sinnoh M26 Cyrus at HQ")
    ensure_flag("FLAG_DEFEATED_CYRUS_SPEAR_PILLAR", "0x2B1", "Sinnoh M26 Cyrus at Spear Pillar")

    # --- Galactic HQ 1F (stitched) ---
    attr = stitch(HQ1F)
    grid = [[attr_to_mt(attr[y][x], x, y, cave=True) for x in range(64)] for y in range(32)]
    paint_water(grid, HQ1F)
    open_path(grid, [(x, y) for x in range(8, 56) for y in range(8, 28)])
    paint_water(grid, HQ1F)
    write_layout("VeilstoneCity_GalacticHQ_1F", 64, 32, "gTileset_General", "gTileset_Facility", pack(grid), "LAYOUT_VEILSTONE_CITY_GALACTIC_HQ_1F")
    ensure_trainer("TRAINER_GALACTIC_HQ_GRUNT_A", 37, "Team Aqua", "Aqua Grunt M", [("Golbat", 37)], "Grunt")
    ensure_trainer("TRAINER_GALACTIC_HQ_GRUNT_B", 38, "Team Aqua", "Aqua Grunt F", [("Toxicroak", 38)], "Grunt")
    ensure_trainer(
        "TRAINER_COMMANDER_MARS_HQ",
        41,
        "Team Aqua",
        "Aqua Admin F",
        [("Purugly", 40), ("Bronzor", 40), ("Golbat", 41)],
        "Mars",
    )
    hq1_scripts = (
        "VeilstoneCity_GalacticHQ_1F_MapScripts::\n\t.byte 0\n\n"
        "VeilstoneCity_GalacticHQ_1F_EventScript_GruntA::\n"
        "\ttrainerbattle_single TRAINER_GALACTIC_HQ_GRUNT_A, VeilstoneCity_GalacticHQ_1F_Text_GruntAIntro, VeilstoneCity_GalacticHQ_1F_Text_GruntADefeat\n"
        "\tmsgbox VeilstoneCity_GalacticHQ_1F_Text_GruntAAfter, MSGBOX_AUTOCLOSE\n\tend\n\n"
        "VeilstoneCity_GalacticHQ_1F_EventScript_GruntB::\n"
        "\ttrainerbattle_single TRAINER_GALACTIC_HQ_GRUNT_B, VeilstoneCity_GalacticHQ_1F_Text_GruntBIntro, VeilstoneCity_GalacticHQ_1F_Text_GruntBDefeat\n"
        "\tmsgbox VeilstoneCity_GalacticHQ_1F_Text_GruntBAfter, MSGBOX_AUTOCLOSE\n\tend\n\n"
        "VeilstoneCity_GalacticHQ_1F_EventScript_Mars::\n"
        "\ttrainerbattle_single TRAINER_COMMANDER_MARS_HQ, VeilstoneCity_GalacticHQ_1F_Text_MarsIntro, VeilstoneCity_GalacticHQ_1F_Text_MarsDefeat\n"
        "\tmsgbox VeilstoneCity_GalacticHQ_1F_Text_MarsAfter, MSGBOX_AUTOCLOSE\n\tend\n\n"
        'VeilstoneCity_GalacticHQ_1F_Text_GruntAIntro:\n\t.string "Headquarters security!\\n"\n\t.string "No tourists allowed!$\"\n\n'
        'VeilstoneCity_GalacticHQ_1F_Text_GruntADefeat:\n\t.string "Cleared...$"\n\n'
        'VeilstoneCity_GalacticHQ_1F_Text_GruntAAfter:\n\t.string "The boss waits upstairs.$"\n\n'
        'VeilstoneCity_GalacticHQ_1F_Text_GruntBIntro:\n\t.string "You again?!\\n"\n\t.string "This ends here!$\"\n\n'
        'VeilstoneCity_GalacticHQ_1F_Text_GruntBDefeat:\n\t.string "Not again...$"\n\n'
        'VeilstoneCity_GalacticHQ_1F_Text_GruntBAfter:\n\t.string "Mars is covering the stairs.$"\n\n'
        'VeilstoneCity_GalacticHQ_1F_Text_MarsIntro:\n\t.string "MARS: Lakes were only the opening act.\\n"\n\t.string "Cyrus rewrites the world above!$\"\n\n'
        'VeilstoneCity_GalacticHQ_1F_Text_MarsDefeat:\n\t.string "How...$"\n\n'
        'VeilstoneCity_GalacticHQ_1F_Text_MarsAfter:\n\t.string "Climb if you dare.\\n"\n\t.string "Spear Pillar is already chosen.$"\n\n'
    )
    # fix escaped quotes - I accidentally used $\" 
    hq1_scripts = hq1_scripts.replace('$\\"', '$"')
    write_map(
        "VeilstoneCity_GalacticHQ_1F",
        {
            "id": "MAP_VEILSTONE_CITY_GALACTIC_HQ_1F",
            "name": "VeilstoneCity_GalacticHQ_1F",
            "layout": "LAYOUT_VEILSTONE_CITY_GALACTIC_HQ_1F",
            "music": "MUS_AQUA_MAGMA_HIDEOUT",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_VEILSTONE_CITY" if False else "MAPSEC_ROUTE_215",
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
                obj("OBJ_EVENT_GFX_AQUA_MEMBER_M", 20, 20, "VeilstoneCity_GalacticHQ_1F_EventScript_GruntA", trainer="TRAINER_TYPE_NORMAL", sight="3"),
                obj("OBJ_EVENT_GFX_AQUA_MEMBER_F", 40, 18, "VeilstoneCity_GalacticHQ_1F_EventScript_GruntB", trainer="TRAINER_TYPE_NORMAL", sight="3"),
                obj("OBJ_EVENT_GFX_ARCHIE", 32, 10, "VeilstoneCity_GalacticHQ_1F_EventScript_Mars"),
            ],
            "warp_events": [
                warp(32, 30, "MAP_VEILSTONE_CITY", 15),
                warp(33, 30, "MAP_VEILSTONE_CITY", 16),
                warp(32, 2, "MAP_VEILSTONE_CITY_GALACTIC_HQ_2F", 0),
                warp(33, 2, "MAP_VEILSTONE_CITY_GALACTIC_HQ_2F", 1),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        hq1_scripts,
    )

    # Retarget Veilstone warps from stub -> 1F
    vl = json.loads((MAPS / "VeilstoneCity" / "map.json").read_text())
    for w in vl.get("warp_events") or []:
        if w.get("dest_map") == "MAP_VEILSTONE_CITY_GALACTIC_HQ_STUB":
            w["dest_map"] = "MAP_VEILSTONE_CITY_GALACTIC_HQ_1F"
            w["dest_warp_id"] = "0"
    (MAPS / "VeilstoneCity" / "map.json").write_text(json.dumps(vl, indent=2) + "\n")

    # HQ 2F / Cyrus room stubs
    for floor, mid, next_map, next_wid, objs, scripts in [
        (
            "VeilstoneCity_GalacticHQ_2F",
            "MAP_VEILSTONE_CITY_GALACTIC_HQ_2F",
            "MAP_VEILSTONE_CITY_GALACTIC_HQ_CYRUS",
            0,
            [obj("OBJ_EVENT_GFX_AQUA_MEMBER_M", 8, 5, "VeilstoneCity_GalacticHQ_2F_EventScript_Grunt")],
            None,
        ),
    ]:
        pass
    ensure_trainer("TRAINER_GALACTIC_HQ_GRUNT_C", 39, "Team Aqua", "Aqua Grunt M", [("Bronzor", 39)], "Grunt")
    lid2 = indoor_room("VeilstoneCity_GalacticHQ_2F", "MAP_VEILSTONE_CITY_GALACTIC_HQ_2F", "MAPSEC_ROUTE_215", "MAP_VEILSTONE_CITY_GALACTIC_HQ_1F", 2)
    write_map(
        "VeilstoneCity_GalacticHQ_2F",
        {
            "id": "MAP_VEILSTONE_CITY_GALACTIC_HQ_2F",
            "name": "VeilstoneCity_GalacticHQ_2F",
            "layout": lid2,
            "music": "MUS_AQUA_MAGMA_HIDEOUT",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_215",
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
                obj("OBJ_EVENT_GFX_AQUA_MEMBER_M", 8, 5, "VeilstoneCity_GalacticHQ_2F_EventScript_Grunt", trainer="TRAINER_TYPE_NORMAL", sight="2"),
            ],
            "warp_events": [
                warp(7, 11, "MAP_VEILSTONE_CITY_GALACTIC_HQ_1F", 2),
                warp(8, 11, "MAP_VEILSTONE_CITY_GALACTIC_HQ_1F", 3),
                warp(7, 0, "MAP_VEILSTONE_CITY_GALACTIC_HQ_CYRUS", 0),
                warp(8, 0, "MAP_VEILSTONE_CITY_GALACTIC_HQ_CYRUS", 1),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "VeilstoneCity_GalacticHQ_2F_MapScripts::\n\t.byte 0\n\n"
        "VeilstoneCity_GalacticHQ_2F_EventScript_Grunt::\n"
        "\ttrainerbattle_single TRAINER_GALACTIC_HQ_GRUNT_C, VeilstoneCity_GalacticHQ_2F_Text_Intro, VeilstoneCity_GalacticHQ_2F_Text_Defeat\n"
        "\tmsgbox VeilstoneCity_GalacticHQ_2F_Text_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
        'VeilstoneCity_GalacticHQ_2F_Text_Intro:\n\t.string "Cyrus is finishing the sequence!\\n"\n\t.string "You will not interrupt!$\"\n\n'
        'VeilstoneCity_GalacticHQ_2F_Text_Defeat:\n\t.string "Broken...$"\n\n'
        'VeilstoneCity_GalacticHQ_2F_Text_After:\n\t.string "His room is just ahead.$"\n'.replace('$\\"', '$"'),
    )

    ensure_trainer(
        "TRAINER_LEADER_CYRUS_HQ",
        44,
        "Team Aqua",
        "Aqua Leader Archie",
        [("Honchkrow", 41), ("Gyarados", 42), ("Weavile", 44)],
        "Cyrus",
    )
    lidc = indoor_room("VeilstoneCity_GalacticHQ_Cyrus", "MAP_VEILSTONE_CITY_GALACTIC_HQ_CYRUS", "MAPSEC_ROUTE_215", "MAP_VEILSTONE_CITY_GALACTIC_HQ_2F", 2)
    write_map(
        "VeilstoneCity_GalacticHQ_Cyrus",
        {
            "id": "MAP_VEILSTONE_CITY_GALACTIC_HQ_CYRUS",
            "name": "VeilstoneCity_GalacticHQ_Cyrus",
            "layout": lidc,
            "music": "MUS_AQUA_MAGMA_HIDEOUT",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_215",
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
                obj("OBJ_EVENT_GFX_MAXIE", 8, 3, "VeilstoneCity_GalacticHQ_Cyrus_EventScript_Cyrus"),
            ],
            "warp_events": [
                warp(7, 11, "MAP_VEILSTONE_CITY_GALACTIC_HQ_2F", 2),
                warp(8, 11, "MAP_VEILSTONE_CITY_GALACTIC_HQ_2F", 3),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "VeilstoneCity_GalacticHQ_Cyrus_MapScripts::\n\t.byte 0\n\n"
        "VeilstoneCity_GalacticHQ_Cyrus_EventScript_Cyrus::\n"
        "\tlock\n\tfaceplayer\n"
        "\tgoto_if_set FLAG_DEFEATED_CYRUS_GALACTIC_HQ, VeilstoneCity_GalacticHQ_Cyrus_EventScript_After\n"
        "\ttrainerbattle_single TRAINER_LEADER_CYRUS_HQ, VeilstoneCity_GalacticHQ_Cyrus_Text_Intro, VeilstoneCity_GalacticHQ_Cyrus_Text_Defeat, VeilstoneCity_GalacticHQ_Cyrus_EventScript_Defeated\n"
        "\trelease\n\tend\n\n"
        "VeilstoneCity_GalacticHQ_Cyrus_EventScript_Defeated::\n"
        "\tsetflag FLAG_DEFEATED_CYRUS_GALACTIC_HQ\n"
        "\tmsgbox VeilstoneCity_GalacticHQ_Cyrus_Text_After, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        "VeilstoneCity_GalacticHQ_Cyrus_EventScript_After::\n"
        "\tmsgbox VeilstoneCity_GalacticHQ_Cyrus_Text_After, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        'VeilstoneCity_GalacticHQ_Cyrus_Text_Intro:\n\t.string "CYRUS: Emotion is waste.\\n"\n'
        '\t.string "At Spear Pillar I will silence this world.$"\n\n'
        'VeilstoneCity_GalacticHQ_Cyrus_Text_Defeat:\n\t.string "A flawed calculation...$"\n\n'
        'VeilstoneCity_GalacticHQ_Cyrus_Text_After:\n\t.string "CYRUS: Meet me atop Mt. Coronet.\\n"\n'
        '\t.string "Spear Pillar will decide everything.$"\n',
    )

    # --- Mt Coronet upper approach stub ---
    cave = [
        [IN_WALL if y in (0, 15) or x in (0, 19) else (IN_DOOR if (y == 15 and x in (9, 10)) or (y == 0 and x in (9, 10)) else IN_FLOOR)
         for x in range(20)]
        for y in range(16)
    ]
    lid = write_layout("MtCoronet_UpperStub", 20, 16, "gTileset_General", "gTileset_Cave", pack(cave), "LAYOUT_MT_CORONET_UPPER_STUB")
    write_map(
        "MtCoronet_UpperStub",
        {
            "id": "MAP_MT_CORONET_UPPER_STUB",
            "name": "MtCoronet_UpperStub",
            "layout": lid,
            "music": "MUS_PETALBURG_WOODS",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_210",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_UNDERGROUND",
            "allow_cycling": False,
            "allow_escaping": True,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [obj("OBJ_EVENT_GFX_HIKER", 10, 8, "MtCoronet_UpperStub_EventScript_Hiker")],
            "warp_events": [
                warp(9, 15, "MAP_MT_CORONET_NORTH_STUB", 2),
                warp(10, 15, "MAP_MT_CORONET_NORTH_STUB", 3),
                warp(9, 0, "MAP_SPEAR_PILLAR", 0),
                warp(10, 0, "MAP_SPEAR_PILLAR", 1),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "MtCoronet_UpperStub_MapScripts::\n\t.byte 0\n\n"
        "MtCoronet_UpperStub_EventScript_Hiker::\n\tmsgbox MtCoronet_UpperStub_Text, MSGBOX_NPC\n\tend\n\n"
        'MtCoronet_UpperStub_Text:\n\t.string "The summit path opens onto Spear Pillar.\\n"\n'
        '\t.string "Galactic already climbed ahead.$"\n',
    )
    # Link MtCoronet_NorthStub north exit to UpperStub instead of Route216 only -
    # Keep R216 warps; add alternate: change north warps of NorthStub to UpperStub
    # Actually NorthStub north currently goes to Route216. Better: from NorthStub add side warp,
    # or change MtCoronet_2F_Stub to lead to UpperStub.
    mc2 = json.loads((MAPS / "MtCoronet_2F_Stub" / "map.json").read_text())
    # Point one warp to UpperStub
    if mc2.get("warp_events"):
        mc2["warp_events"][0] = warp(mc2["warp_events"][0]["x"], mc2["warp_events"][0]["y"], "MAP_MT_CORONET_UPPER_STUB", 0)
    (MAPS / "MtCoronet_2F_Stub" / "map.json").write_text(json.dumps(mc2, indent=2) + "\n")
    # Also wire NorthStub: keep south to R211E, north to UpperStub (Spear approach) — Route216 still reachable via east door on R216
    ns = json.loads((MAPS / "MtCoronet_NorthStub" / "map.json").read_text())
    for w in ns.get("warp_events") or []:
        if w.get("dest_map") == "MAP_ROUTE216":
            w["dest_map"] = "MAP_MT_CORONET_UPPER_STUB"
            # map north exits to upper stub south
            w["dest_warp_id"] = "0"
    (MAPS / "MtCoronet_NorthStub" / "map.json").write_text(json.dumps(ns, indent=2) + "\n")
    # Fix UpperStub south to NorthStub
    # Already set. Route216 loses coronet connection — add note NPC on R216 or restore dual path:
    # Restore Route216 <-> NorthStub by pointing UpperStub south to NorthStub and NorthStub north to UpperStub;
    # Route216 keeps its own warps to NorthStub.
    r216 = json.loads((MAPS / "Route216" / "map.json").read_text())
    # unchanged warps to NorthStub — but NorthStub north no longer returns to R216.
    # Add R216 connection via UpperStub? Simpler: NorthStub has 4 warps: 0,1 south R211; 2,3 north UpperStub.
    # Route216 warps still to NorthStub 2,3 — conflict.
    # Fix: Route216 warps -> UpperStub south instead; NorthStub north -> UpperStub; UpperStub east optional.
    for w in r216.get("warp_events") or []:
        if w.get("dest_map") == "MAP_MT_CORONET_NORTH_STUB":
            w["dest_map"] = "MAP_MT_CORONET_UPPER_STUB"
            w["dest_warp_id"] = "0"
    (MAPS / "Route216" / "map.json").write_text(json.dumps(r216, indent=2) + "\n")
    # UpperStub: south -> Route216 and NorthStub both? Use south to Route216, keep NorthStub linked from R211 only.
    us = json.loads((MAPS / "MtCoronet_UpperStub" / "map.json").read_text())
    us["warp_events"] = [
        warp(9, 15, "MAP_ROUTE216", 0),
        warp(10, 15, "MAP_ROUTE216", 1),
        warp(9, 0, "MAP_SPEAR_PILLAR", 0),
        warp(10, 0, "MAP_SPEAR_PILLAR", 1),
    ]
    (MAPS / "MtCoronet_UpperStub" / "map.json").write_text(json.dumps(us, indent=2) + "\n")
    # NorthStub north stays to UpperStub for Celestic climbers
    ns = json.loads((MAPS / "MtCoronet_NorthStub" / "map.json").read_text())
    for w in ns.get("warp_events") or []:
        if w.get("y") == 0:
            w["dest_map"] = "MAP_MT_CORONET_UPPER_STUB"
            w["dest_warp_id"] = "0"
    (MAPS / "MtCoronet_NorthStub" / "map.json").write_text(json.dumps(ns, indent=2) + "\n")

    # --- Spear Pillar ---
    attr = stitch(SPEAR)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(64)] for y in range(64)]
    paint_water(grid, SPEAR)
    open_path(grid, [(x, y) for x in range(16, 48) for y in range(16, 48)])
    paint_water(grid, SPEAR)
    write_layout("SpearPillar", 64, 64, "gTileset_General", "gTileset_Fortree", pack(grid), "LAYOUT_SPEAR_PILLAR")
    ensure_trainer(
        "TRAINER_LEADER_CYRUS_SPEAR",
        47,
        "Team Aqua",
        "Aqua Leader Archie",
        [("Honchkrow", 45), ("Crobat", 45), ("Gyarados", 46), ("Weavile", 47)],
        "Cyrus",
    )
    scripts = (
        "SpearPillar_MapScripts::\n\t.byte 0\n\n"
        "SpearPillar_EventScript_Cyrus::\n"
        "\tlock\n\tfaceplayer\n"
        "\tgoto_if_set FLAG_DEFEATED_CYRUS_SPEAR_PILLAR, SpearPillar_EventScript_CyrusAfter\n"
        "\ttrainerbattle_single TRAINER_LEADER_CYRUS_SPEAR, SpearPillar_Text_CyrusIntro, SpearPillar_Text_CyrusDefeat, SpearPillar_EventScript_CyrusDefeated\n"
        "\trelease\n\tend\n\n"
        "SpearPillar_EventScript_CyrusDefeated::\n"
        "\tsetflag FLAG_DEFEATED_CYRUS_SPEAR_PILLAR\n"
        "\tmsgbox SpearPillar_Text_CyrusAfter, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        "SpearPillar_EventScript_CyrusAfter::\n"
        "\tmsgbox SpearPillar_Text_CyrusAfter, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        "SpearPillar_EventScript_DistortionClosed::\n"
        "\tmsgbox SpearPillar_Text_DistortionClosed, MSGBOX_NPC\n\tend\n\n"
        'SpearPillar_Text_CyrusIntro:\n\t.string "CYRUS: Here the pillars pierce sky.\\n"\n'
        '\t.string "Witness a world without spirit clutter.$"\n\n'
        'SpearPillar_Text_CyrusDefeat:\n\t.string "Even here... resistance$"\n\n'
        'SpearPillar_Text_CyrusAfter:\n\t.string "CYRUS: The Distortion World stirs.\\n"\n'
        '\t.string "Its gate stays sealed until the next chapter.$"\n\n'
        'SpearPillar_Text_DistortionClosed:\n\t.string "A rift shimmers, then freezes shut.\\n"\n'
        '\t.string "Return when the Distortion World opens.$"\n'
    )
    write_map(
        "SpearPillar",
        {
            "id": "MAP_SPEAR_PILLAR",
            "name": "SpearPillar",
            "layout": "LAYOUT_SPEAR_PILLAR",
            "music": "MUS_PETALBURG_WOODS",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_210",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_ROUTE",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [
                obj("OBJ_EVENT_GFX_MAXIE", 32, 28, "SpearPillar_EventScript_Cyrus"),
                obj("OBJ_EVENT_GFX_VAR_0", 32, 20, "SpearPillar_EventScript_DistortionClosed") if False else obj("OBJ_EVENT_GFX_ITEM_BALL", 32, 20, "SpearPillar_EventScript_DistortionClosed"),
            ],
            "warp_events": [
                warp(32, 60, "MAP_MT_CORONET_UPPER_STUB", 2),
                warp(33, 60, "MAP_MT_CORONET_UPPER_STUB", 3),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # Register
    outdoor = ["SpearPillar"]
    indoor_names = [
        "VeilstoneCity_GalacticHQ_1F",
        "VeilstoneCity_GalacticHQ_2F",
        "VeilstoneCity_GalacticHQ_Cyrus",
        "MtCoronet_UpperStub",
    ]
    g = json.loads(GROUPS.read_text())
    g.setdefault("gMapGroup_TownsAndRoutes", [])
    for n in outdoor:
        if n not in g["gMapGroup_TownsAndRoutes"]:
            g["gMapGroup_TownsAndRoutes"].append(n)
    g.setdefault("gMapGroup_IndoorM26", [])
    for n in indoor_names:
        if n not in g["gMapGroup_IndoorM26"]:
            g["gMapGroup_IndoorM26"].append(n)
    if "group_order" in g and "gMapGroup_IndoorM26" not in g["group_order"]:
        g["group_order"].append("gMapGroup_IndoorM26")
    GROUPS.write_text(json.dumps(g, indent=2) + "\n")

    es = EVENT_SCRIPTS.read_text()
    for n in outdoor + indoor_names:
        inc = f'\t.include "data/maps/{n}/scripts.inc"'
        if inc not in es:
            es = es.rstrip() + "\n" + inc + "\n"
    EVENT_SCRIPTS.write_text(es)
    scrub(outdoor + indoor_names)
    print("M26 build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
