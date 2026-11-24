#!/usr/bin/env python3
"""
M24: Lake Valor (drained / Galactic fallout), Route 216–217 snow approach.

Fantina (Relic) already exists from earlier milestones — no gym work here.

Land IDs (pret/pokeplatinum):
  Route216          [[110, 111, 112]]           96x32 origin (288, 384)
  Route217          [[106], [107], [108], [109]] 32x128 origin (288, 256)
  Route211_East     [[61]]                      32x32 origin (416, 512)
  LakeValor_Drained [[544, 545], [546, 547]]    64x64 (dungeon group local)

Emerald tilesets only. Original dialogue. Trainer IVs 0.
ASCII-scrub only M24 map scripts.
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
MT_SNOW = 0x121  # stand-in sand metatile; weather sells the snow
IN_FLOOR, IN_WALL, IN_DOOR = 0x201, 0x21A, 0x20E

R216 = [[110, 111, 112]]
R217 = [[106], [107], [108], [109]]
R211E = [[61]]
VALOR_DRAINED = [[544, 545], [546, 547]]

GFX = {
    "OBJ_EVENT_GFX_ACE_TRAINER_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_ACE_TRAINER_F": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_SKIER_M": "OBJ_EVENT_GFX_MAN_5",
    "OBJ_EVENT_GFX_SKIER_F": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_NINJA_BOY": "OBJ_EVENT_GFX_NINJA_BOY",
    "OBJ_EVENT_GFX_BLACK_BELT": "OBJ_EVENT_GFX_BLACK_BELT",
    "OBJ_EVENT_GFX_HIKER": "OBJ_EVENT_GFX_HIKER",
    "OBJ_EVENT_GFX_SCIENTIST_M": "OBJ_EVENT_GFX_SCIENTIST_1",
    "OBJ_EVENT_GFX_GALACTIC_GRUNT_M": "OBJ_EVENT_GFX_AQUA_MEMBER_M",
    "OBJ_EVENT_GFX_GALACTIC_GRUNT_F": "OBJ_EVENT_GFX_AQUA_MEMBER_F",
    "OBJ_EVENT_GFX_COMMANDER_SATURN": "OBJ_EVENT_GFX_MAXIE",
}


def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]


def attr_to_mt(v: int, x: int, y: int, snow=False) -> int:
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
    return MT_SNOW if snow else MT_GRASS


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
                    beh = attrs[ly * 32 + lx] & 0xFF
                    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
                        grid[y][x] = MT_WATER


def write_layout(name, w, h, primary, secondary, blob):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blob)
    src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(src.read_bytes() if src.exists() else bytes(8))
    # Keep digits glued (Route211_East -> LAYOUT_ROUTE211_EAST, not ROUTE_211)
    lid = "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")
    lid = re.sub(r"([A-Z])_(\d)", r"\1\2", lid)  # undo digit splits: ROUTE_211 -> ROUTE211? 
    # Actually re.sub on ROUTE211_EAST is fine from name Route211_East -> ROUTE211_EAST
    # Route216 -> LAYOUT_ROUTE216. Good if name has no lower-upper digit issue.
    # IronIsland_1F_Stub became LAYOUT_IRON_ISLAND_1_F_STUB — avoid by explicit override.
    if name == "MtCoronet_NorthStub":
        lid = "LAYOUT_MT_CORONET_NORTH_STUB"
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
    anchor = "FLAG_RECEIVED_CANALAVE_GYM_TM"
    if anchor in text:
        text = text.replace(
            f"#define {anchor}",
            f"#define {name}  {value_hex} // {comment}\n#define {anchor}",
            1,
        )
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
            f"#define {tid}                    {nid} // Sinnoh M24\n\n#define TRAINERS_COUNT_EMERALD",
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


def party_for(tid, level):
    u = tid.upper()
    if "SKIER" in u or "NINJA" in u:
        return "Ninja Boy", "Ninja Boy", [("Snover", level), ("Sneasel", level - 1)]
    if "ACE" in u or "RANGER" in u:
        return "Cooltrainer", "Cooltrainer M", [("Snorunt", level), ("Piloswine", level - 1)]
    if "HIKER" in u or "BLACK_BELT" in u:
        return "Hiker", "Hiker", [("Geodude", level), ("Onix", level)]
    if "GALACTIC" in u or "SATURN" in u:
        return "Team Aqua", "Aqua Grunt M", [("Zubat", level), ("Bronzor", level)]
    return "Youngster", "Youngster", [("Snover", level), ("Swinub", level)]


def face(d):
    return {
        "DIR_NORTH": "MOVEMENT_TYPE_FACE_UP",
        "DIR_SOUTH": "MOVEMENT_TYPE_FACE_DOWN",
        "DIR_WEST": "MOVEMENT_TYPE_FACE_LEFT",
        "DIR_EAST": "MOVEMENT_TYPE_FACE_RIGHT",
    }.get(d or "", "MOVEMENT_TYPE_FACE_DOWN")


def place_all(em, plat, origin, wmax, hmax, level, flavor="snow"):
    pe = json.loads((PLAT_MAPS / plat / "events.json").read_text())
    ox, oz = origin
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    occupied = set()
    n = 0
    if flavor == "snow":
        intro_a, intro_b = "Cold enough to freeze a battle!\\n", "Warm up against me!$"
        after_a, after_b = "Snowpoint is farther north.\\n", "The path gets steeper ahead.$"
    else:
        intro_a, intro_b = "The lake went quiet overnight.\\n", "Something drained the hope here.$"
        after_a, after_b = "Galactic left scars on the shore.\\n", "Keep your team ready.$"
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"] - ox), int(po["z"] - oz)
        if not (0 <= lx < wmax and 0 <= ly < hmax) or (lx, ly) in occupied:
            continue
        tr = po.get("trainer") or {}
        tid_plat = tr.get("id")
        if tid_plat:
            tid = tid_plat if str(tid_plat).startswith("TRAINER_") else f"TRAINER_{tid_plat}"
            cls, pic, mons = party_for(tid, level)
            ensure_trainer(tid, level, cls, pic, mons)
            short = tid.replace("TRAINER_", "").title().replace("_", "")
            label = f"{em}_EventScript_{short}_{n}"
            gfx = GFX.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_MAN_5")
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
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f"{label}_Intro:\n\t.string \"{intro_a}\"\n\t.string \"{intro_b}\"\n\n"
                f"{label}_Defeat:\n\t.string \"Chilled out.$\"\n\n"
                f"{label}_After:\n\t.string \"{after_a}\"\n\t.string \"{after_b}\"\n\n"
            )
            n += 1
        else:
            label = f"{em}_EventScript_PlatNpc{n}"
            gfx = GFX.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_GIRL_1")
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f"{label}_Text:\n\t.string \"Snow piles higher every mile north.\\n\"\n"
                f"\t.string \"Pack warm clothes and warmer POKéMON.$\"\n\n"
            )
            n += 1
        occupied.add((lx, ly))
    return objs, scripts, pe


def stamp_door(grid, x, y):
    for dy, row in enumerate([[0x210, 0x211, 0x212], [0x218, 0x219, 0x21A], [0x222, 0x230, 0x221]]):
        for dx, mt in enumerate(row):
            sx, sy = x - 1 + dx, y - 2 + dy
            if 0 <= sy < len(grid) and 0 <= sx < len(grid[0]):
                grid[sy][sx] = mt


def write_map(name, data, scripts):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("map", name)


def indoor(name, mid, mapsec, exit_map, exit_wid, label, text):
    grid = [
        [IN_WALL if y in (0, 7) or x in (0, 9) else (IN_DOOR if y == 7 and x in (4, 5) else IN_FLOOR) for x in range(10)]
        for y in range(8)
    ]
    lid = write_layout(name, 10, 8, "gTileset_Building", "gTileset_GenericBuilding", pack(grid))
    data = {
        "id": mid,
        "name": name,
        "layout": lid,
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
        "object_events": [obj("OBJ_EVENT_GFX_OLD_MAN", 4, 3, label)],
        "warp_events": [warp(4, 7, exit_map, exit_wid), warp(5, 7, exit_map, exit_wid)],
        "coord_events": [],
        "bg_events": [],
    }
    scripts = (
        f"{name}_MapScripts::\n\t.byte 0\n\n"
        f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
        f"{label}_Text:\n\t.string \"{text}\"\n"
    )
    write_map(name, data, scripts)


def scrub(names):
    for n in names:
        p = MAPS / n / "scripts.inc"
        if not p.exists():
            continue
        t = p.read_text()
        if any(ord(c) > 127 for c in t):
            p.write_text("".join(c if ord(c) < 128 else "-" for c in t))


def main():
    ensure_flag("FLAG_DEFEATED_SATURN_LAKE_VALOR", "0x2AD", "Sinnoh M24 Saturn at drained lake")

    # --- Route 211 East (Celestic west approach) ---
    attr = stitch(R211E)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(32)] for y in range(32)]
    paint_from_attrs(grid, R211E)
    open_path(grid, [(x, y) for x in range(0, 32) for y in range(12, 20)])
    paint_from_attrs(grid, R211E)
    # Cave door toward Mt Coronet (west side)
    stamp_door(grid, 2, 16)
    write_layout("Route211_East", 32, 32, "gTileset_General", "gTileset_Petalburg", pack(grid))
    objs, scripts, pe = place_all("Route211_East", "route_211_east", (416, 512), 32, 32, 30, flavor="snow")
    r211 = {
        "id": "MAP_ROUTE211_EAST",
        "name": "Route211_East",
        "layout": "LAYOUT_ROUTE211_EAST",
        "music": "MUS_PL_ROUTE203",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_210",
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_ROUTE",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [
            {"map": "MAP_CELESTIC_TOWN", "offset": 0, "direction": "right"},
        ],
        "object_events": objs,
        "warp_events": [
            warp(2, 16, "MAP_MT_CORONET_NORTH_STUB", 0),
            warp(1, 16, "MAP_MT_CORONET_NORTH_STUB", 0),
        ],
        "coord_events": [],
        "bg_events": [],
    }
    write_map("Route211_East", r211, scripts)

    # Celestic left connection
    cel = json.loads((MAPS / "CelesticTown" / "map.json").read_text())
    conns = cel.get("connections") or []
    if not any(c.get("map") == "MAP_ROUTE211_EAST" for c in conns):
        conns.append({"map": "MAP_ROUTE211_EAST", "offset": 0, "direction": "left"})
        cel["connections"] = conns
        (MAPS / "CelesticTown" / "map.json").write_text(json.dumps(cel, indent=2) + "\n")

    # --- Mt Coronet north stub (bridge Celestic approach -> Route 216) ---
    cave = [
        [IN_WALL if y in (0, 11) or x in (0, 15) else (IN_DOOR if (y == 11 and x in (7, 8)) or (y == 0 and x in (7, 8)) else IN_FLOOR)
         for x in range(16)]
        for y in range(12)
    ]
    # north door row y=0 already doors; south y=11 doors
    lid = write_layout("MtCoronet_NorthStub", 16, 12, "gTileset_General", "gTileset_Cave", pack(cave))
    write_map(
        "MtCoronet_NorthStub",
        {
            "id": "MAP_MT_CORONET_NORTH_STUB",
            "name": "MtCoronet_NorthStub",
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
            "object_events": [
                obj("OBJ_EVENT_GFX_HIKER", 8, 5, "MtCoronet_NorthStub_EventScript_Hiker")
            ],
            "warp_events": [
                warp(7, 11, "MAP_ROUTE211_EAST", 0),
                warp(8, 11, "MAP_ROUTE211_EAST", 1),
                warp(7, 0, "MAP_ROUTE216", 0),
                warp(8, 0, "MAP_ROUTE216", 1),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "MtCoronet_NorthStub_MapScripts::\n\t.byte 0\n\n"
        "MtCoronet_NorthStub_EventScript_Hiker::\n"
        "\tmsgbox MtCoronet_NorthStub_Text, MSGBOX_NPC\n\tend\n\n"
        'MtCoronet_NorthStub_Text:\n\t.string "North exit dumps you onto Route 216.\\n"\n'
        '\t.string "Bundled trainers wait in the snow.$"\n',
    )

    # --- Route 216 ---
    attr = stitch(R216)
    grid = [[attr_to_mt(attr[y][x], x, y, snow=True) for x in range(96)] for y in range(32)]
    paint_from_attrs(grid, R216)
    open_path(grid, [(x, y) for x in range(0, 96) for y in range(12, 22)], mt=MT_SNOW)
    paint_from_attrs(grid, R216)
    # House stamp from platinum warps
    pe216 = json.loads((PLAT_MAPS / "route_216" / "events.json").read_text())
    ox, oz = 288, 384
    for pw in pe216.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < 96 and 0 <= ly < 32:
            stamp_door(grid, lx, ly)
    write_layout("Route216", 96, 32, "gTileset_General", "gTileset_Fallarbor", pack(grid))
    objs, scripts, pe = place_all("Route216", "route_216", (288, 384), 96, 32, 32, flavor="snow")
    # Warps: coronet stub on east, house, north to R217 via connection
    house_xy = (80, 16)
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        dest = (pw.get("dest_header_id") or "").upper()
        if "HOUSE" in dest:
            house_xy = (lx, ly)
    r216 = {
        "id": "MAP_ROUTE216",
        "name": "Route216",
        "layout": "LAYOUT_ROUTE216",
        "music": "MUS_PL_ROUTE203",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_210",
        "requires_flash": False,
        "weather": "WEATHER_SNOW",
        "map_type": "MAP_TYPE_ROUTE",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [
            {"map": "MAP_ROUTE217", "offset": 0, "direction": "up"},
        ],
        "object_events": objs,
        "warp_events": [
            warp(90, 20, "MAP_MT_CORONET_NORTH_STUB", 2),
            warp(91, 20, "MAP_MT_CORONET_NORTH_STUB", 3),
            warp(house_xy[0], house_xy[1], "MAP_ROUTE216_HOUSE", 0),
        ],
        "coord_events": [],
        "bg_events": [],
    }
    # Prefer platinum local cave warps if any
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        dest = (pw.get("dest_header_id") or "").upper()
        if "CORONET" in dest or "CAVE" in dest:
            r216["warp_events"][0] = warp(lx, ly, "MAP_MT_CORONET_NORTH_STUB", 2)
            r216["warp_events"][1] = warp(lx + 1, ly, "MAP_MT_CORONET_NORTH_STUB", 3)
            break
    write_map("Route216", r216, scripts)
    indoor(
        "Route216_House",
        "MAP_ROUTE216_HOUSE",
        "MAPSEC_ROUTE_210",
        "MAP_ROUTE216",
        2,
        "Route216_House_EventScript_Resident",
        "Skiers rest here between whiteouts.\\nSnowpoint is still a long climb north.$",
    )

    # --- Route 217 ---
    attr = stitch(R217)
    grid = [[attr_to_mt(attr[y][x], x, y, snow=True) for x in range(32)] for y in range(128)]
    paint_from_attrs(grid, R217)
    open_path(grid, [(x, y) for x in range(8, 24) for y in range(0, 128)], mt=MT_SNOW)
    paint_from_attrs(grid, R217)
    # Soft-close Snowpoint (M25) via NPC only — do not alter Platinum walk collision.
    pe217 = json.loads((PLAT_MAPS / "route_217" / "events.json").read_text())
    ox, oz = 288, 256
    for pw in pe217.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < 32 and 0 <= ly < 128:
            stamp_door(grid, lx, ly)
    write_layout("Route217", 32, 128, "gTileset_General", "gTileset_Fallarbor", pack(grid))
    objs, scripts, pe = place_all("Route217", "route_217", (288, 256), 32, 128, 34, flavor="snow")
    # Blocker NPC at north
    objs.append(obj("OBJ_EVENT_GFX_HIKER", 16, 5, "Route217_EventScript_SnowpointClosed"))
    scripts += (
        "Route217_EventScript_SnowpointClosed::\n"
        "\tmsgbox Route217_Text_SnowpointClosed, MSGBOX_NPC\n\tend\n\n"
        'Route217_Text_SnowpointClosed:\n\t.string "Blizzard buried the road into Snowpoint.\\n"\n'
        '\t.string "Come back when the next storm clears.$"\n\n'
    )
    house_warps = []
    for i, pw in enumerate(pe.get("warp_events") or []):
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < 32 and 0 <= ly < 128:
            house_warps.append(warp(lx, ly, "MAP_ROUTE217_HOUSE", 0 if i == 0 else 0))
    if not house_warps:
        house_warps = [warp(8, 40, "MAP_ROUTE217_HOUSE", 0)]
    r217 = {
        "id": "MAP_ROUTE217",
        "name": "Route217",
        "layout": "LAYOUT_ROUTE217",
        "music": "MUS_PL_ROUTE203",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_210",
        "requires_flash": False,
        "weather": "WEATHER_SNOW",
        "map_type": "MAP_TYPE_ROUTE",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [
            {"map": "MAP_ROUTE216", "offset": 0, "direction": "down"},
        ],
        "object_events": objs,
        "warp_events": house_warps[:2],
        "coord_events": [],
        "bg_events": [],
    }
    write_map("Route217", r217, scripts)
    indoor(
        "Route217_House",
        "MAP_ROUTE217_HOUSE",
        "MAPSEC_ROUTE_210",
        "MAP_ROUTE217",
        0,
        "Route217_House_EventScript_Resident",
        "Whiteouts erase the trail marks.\\nFollow the fence posts north when they reopen.$",
    )

    # --- Lake Valor Drained (1:1 outdoor) ---
    attr = stitch(VALOR_DRAINED)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(64)] for y in range(64)]
    paint_from_attrs(grid, VALOR_DRAINED)
    open_path(grid, [(x, y) for x in range(16, 48) for y in range(16, 48)])
    paint_from_attrs(grid, VALOR_DRAINED)
    write_layout("LakeValor_Drained", 64, 64, "gTileset_General", "gTileset_Pacifidlog", pack(grid))
    # Local events — lake_valor_drained uses local coords already in dungeon group
    pe = json.loads((PLAT_MAPS / "lake_valor_drained" / "events.json").read_text())
    # Events appear to use local-ish coords in 10-53 range already
    objs, scripts = [], "LakeValor_Drained_MapScripts::\n\t.byte 0\n\n"
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"]), int(po["z"])
        # Some dungeon events are already local; clamp to map
        if not (0 <= lx < 64 and 0 <= ly < 64) or (lx, ly) in occupied:
            continue
        tr = po.get("trainer") or {}
        tid_plat = tr.get("id")
        gfx_id = po.get("graphics_id") or ""
        if tid_plat or "GALACTIC" in str(gfx_id).upper() or "SATURN" in str(gfx_id).upper():
            tid = tid_plat if tid_plat and str(tid_plat).startswith("TRAINER_") else (
                f"TRAINER_{tid_plat}" if tid_plat else f"TRAINER_GALACTIC_VALOR_{n}"
            )
            cls, pic, mons = party_for(tid, 35)
            ensure_trainer(tid, 35, cls, pic, mons)
            label = f"LakeValor_Drained_EventScript_Grunt{n}"
            gfx = GFX.get(gfx_id, "OBJ_EVENT_GFX_AQUA_MEMBER_M")
            objs.append(obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2)))
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f"{label}_Intro:\n\t.string \"Team Galactic claims this crater!\\n\"\n\t.string \"Turn back!$\"\n\n"
                f"{label}_Defeat:\n\t.string \"Mission compromised...$\"\n\n"
                f"{label}_After:\n\t.string \"The Commander is deeper in.\\n\"\n\t.string \"You will not stop the plan.$\"\n\n"
            )
            n += 1
        else:
            label = f"LakeValor_Drained_EventScript_Npc{n}"
            objs.append(obj("OBJ_EVENT_GFX_MAN_4", lx, ly, label))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f"{label}_Text:\n\t.string \"The water vanished after the blast.\\n\"\n"
                f"\t.string \"Galactic left nothing but mud.$\"\n\n"
            )
            n += 1
        occupied.add((lx, ly))
    # Saturn commander
    ensure_trainer(
        "TRAINER_COMMANDER_SATURN_VALOR",
        38,
        "Team Aqua",
        "Aqua Admin M",
        [("Kadabra", 35), ("Toxicroak", 37), ("Bronzor", 38)],
        display_name="Saturn",
    )
    objs.append(obj("OBJ_EVENT_GFX_MAXIE", 32, 28, "LakeValor_Drained_EventScript_Saturn"))
    scripts += (
        "LakeValor_Drained_EventScript_Saturn::\n"
        "\tlock\n\tfaceplayer\n"
        "\tgoto_if_set FLAG_DEFEATED_SATURN_LAKE_VALOR, LakeValor_Drained_EventScript_SaturnAfter\n"
        "\ttrainerbattle_single TRAINER_COMMANDER_SATURN_VALOR, LakeValor_Drained_Text_SaturnIntro, LakeValor_Drained_Text_SaturnDefeat, LakeValor_Drained_EventScript_SaturnDefeated\n"
        "\trelease\n\tend\n\n"
        "LakeValor_Drained_EventScript_SaturnDefeated::\n"
        "\tsetflag FLAG_DEFEATED_SATURN_LAKE_VALOR\n"
        "\tmsgbox LakeValor_Drained_Text_SaturnAfter, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        "LakeValor_Drained_EventScript_SaturnAfter::\n"
        "\tmsgbox LakeValor_Drained_Text_SaturnAfter, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        'LakeValor_Drained_Text_SaturnIntro:\n\t.string "SATURN: The lake answers our call.\\n"\n'
        '\t.string "You are too late to matter.$"\n\n'
        'LakeValor_Drained_Text_SaturnDefeat:\n\t.string "A temporary setback...$"\n\n'
        'LakeValor_Drained_Text_SaturnAfter:\n\t.string "SATURN: The other lakes await.\\n"\n'
        '\t.string "Snowpoint\'s lake will be next on the list.$"\n\n'
    )
    # Exit warps back to Valor Lakefront — use plat warps if local
    warps = []
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        if 0 <= lx < 64 and 0 <= ly < 64:
            warps.append(warp(lx, ly, "MAP_VALOR_LAKEFRONT", 4))
    if len(warps) < 2:
        warps = [warp(32, 60, "MAP_VALOR_LAKEFRONT", 4), warp(33, 60, "MAP_VALOR_LAKEFRONT", 4)]
    write_map(
        "LakeValor_Drained",
        {
            "id": "MAP_LAKE_VALOR_DRAINED",
            "name": "LakeValor_Drained",
            "layout": "LAYOUT_LAKE_VALOR_DRAINED",
            "music": "MUS_PETALBURG_WOODS",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_ROUTE",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": objs,
            "warp_events": warps[:4],
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # Point ValorLakefront lake warps at drained map
    vl = json.loads((MAPS / "ValorLakefront" / "map.json").read_text())
    for w in vl.get("warp_events") or []:
        if w.get("dest_map") in ("MAP_LAKE_VALOR_STUB", "MAP_LAKE_VALOR_NORMAL"):
            w["dest_map"] = "MAP_LAKE_VALOR_DRAINED"
    (MAPS / "ValorLakefront" / "map.json").write_text(json.dumps(vl, indent=2) + "\n")

    # Register groups + event scripts
    outdoor = ["Route211_East", "Route216", "Route217"]  # LakeValor_Drained already grouped
    outdoor_all = outdoor + ["LakeValor_Drained"]
    indoor_names = ["MtCoronet_NorthStub", "Route216_House", "Route217_House"]
    g = json.loads(GROUPS.read_text())
    g.setdefault("gMapGroup_TownsAndRoutes", [])
    for n in outdoor:
        if n not in g["gMapGroup_TownsAndRoutes"]:
            g["gMapGroup_TownsAndRoutes"].append(n)
    g.setdefault("gMapGroup_IndoorM24", [])
    for n in indoor_names:
        if n not in g["gMapGroup_IndoorM24"]:
            g["gMapGroup_IndoorM24"].append(n)
    if "group_order" in g and "gMapGroup_IndoorM24" not in g["group_order"]:
        g["group_order"].append("gMapGroup_IndoorM24")
    GROUPS.write_text(json.dumps(g, indent=2) + "\n")

    es = EVENT_SCRIPTS.read_text()
    for n in outdoor_all + indoor_names:
        inc = f'\t.include "data/maps/{n}/scripts.inc"'
        if inc not in es:
            es = es.rstrip() + "\n" + inc + "\n"
    EVENT_SCRIPTS.write_text(es)

    scrub(outdoor_all + indoor_names)
    print("M24 build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
