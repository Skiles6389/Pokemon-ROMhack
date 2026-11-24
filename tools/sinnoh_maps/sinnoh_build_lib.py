#!/usr/bin/env python3
"""Shared helpers for Sinnoh milestone map builders (M27+)."""
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
MT_CAVE_FLOOR = 0x1A1
# Fallarbor cave floor often 0x1A1; if missing in tileset, grass still walks
CAVE_FLOOR = 0x001
CAVE_WALL = 0x079


def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]


def stitch(chunks):
    rows, cols = len(chunks), len(chunks[0])
    out = [[0] * (cols * 32) for _ in range(rows * 32)]
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    out[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return out


def attr_to_mt(v, x, y, *, cave=False, snow=False):
    col, beh = (v >> 15) & 1, v & 0xFF
    if col:
        return CAVE_WALL if cave else MT_TREE[(y & 1) * 2 + (x & 1)]
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
    if cave:
        return CAVE_FLOOR
    if snow:
        return MT_SAND
    return MT_GRASS


def pack(grid):
    h, w = len(grid), len(grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            struct.pack_into("<H", out, (y * w + x) * 2, grid[y][x] & 0x3FF)
    return bytes(out)


def paint_water(grid, chunks):
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    x, y = cx * 32 + lx, cy * 32 + ly
                    beh = attrs[ly * 32 + lx] & 0xFF
                    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
                        grid[y][x] = MT_WATER


def paint_ledges(grid, chunks):
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    x, y = cx * 32 + lx, cy * 32 + ly
                    beh = attrs[ly * 32 + lx] & 0xFF
                    if beh == 0x3B:
                        grid[y][x] = MT_LEDGE_A if (x & 1) == 0 else MT_LEDGE_B


def clear_plat_walkables(grid, chunks, *, cave=False, snow=False):
    """Force Emerald walkables wherever Platinum collision bit is clear (EXACT corridors)."""
    blocked = set(MT_TREE) | {MT_ROCK, CAVE_WALL, IN_WALL}
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    x, y = cx * 32 + lx, cy * 32 + ly
                    v = attrs[ly * 32 + lx]
                    col, beh = (v >> 15) & 1, v & 0xFF
                    if col:
                        continue
                    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
                        grid[y][x] = MT_WATER
                    elif beh == 0x3B:
                        grid[y][x] = MT_LEDGE_A if (x & 1) == 0 else MT_LEDGE_B
                    elif beh in (0x02, 0x03):
                        grid[y][x] = MT_TALL
                    elif grid[y][x] in blocked:
                        grid[y][x] = CAVE_FLOOR if cave else (MT_SAND if snow else MT_GRASS)


def grid_from_chunks(chunks, *, cave=False, snow=False):
    attr = stitch(chunks)
    h, w = len(attr), len(attr[0])
    grid = [[attr_to_mt(attr[y][x], x, y, cave=cave, snow=snow) for x in range(w)] for y in range(h)]
    paint_water(grid, chunks)
    paint_ledges(grid, chunks)
    clear_plat_walkables(grid, chunks, cave=cave, snow=snow)
    paint_water(grid, chunks)
    return grid, w, h


def write_layout(name, w, h, primary, secondary, blob, lid=None):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blob)
    src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(src.read_bytes() if src.exists() else bytes(8))
    if lid is None:
        lid = "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")
        lid = re.sub(r"_+", "_", lid)
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


def write_map(name, data, scripts):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("map", name)


def scrub(names):
    for n in names:
        p = MAPS / n / "scripts.inc"
        if p.exists():
            t = p.read_text()
            if any(ord(c) > 127 for c in t):
                p.write_text("".join(c if ord(c) < 128 else "-" for c in t))


def ensure_flag(name, value_hex, comment, after=None):
    text = FLAGS.read_text()
    if name in text:
        return
    anchors = [
        after,
        "FLAG_DEFEATED_CYRUS_SPEAR_PILLAR",
        "FLAG_DEFEATED_CYRUS_GALACTIC_HQ",
        "FLAG_RECEIVED_SNOWPOINT_GYM_TM",
    ]
    for anchor in anchors:
        if not anchor:
            continue
        needle = f"#define {anchor}"
        if needle in text:
            text = text.replace(needle, f"#define {name}  {value_hex} // {comment}\n{needle}", 1)
            FLAGS.write_text(text)
            return
    FLAGS.write_text(text + f"\n#define {name}  {value_hex} // {comment}\n")


def ensure_trainer(tid, level, cls, pic, mons, display_name=None, gender="Male", tag="Sinnoh"):
    defined = set(re.findall(r"#define (TRAINER_[A-Z0-9_]+)\s+", OPP.read_text()))
    if tid not in defined:
        ids = [int(x) for x in re.findall(r"#define TRAINER_[A-Z0-9_]+\s+(\d+)\b", OPP.read_text())]
        nid = max(i for i in ids if i < 2000) + 1
        text = OPP.read_text()
        text = text.replace(
            "#define TRAINERS_COUNT_EMERALD",
            f"#define {tid}                    {nid} // {tag}\n\n#define TRAINERS_COUNT_EMERALD",
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
        f"Gender: {gender}",
        f"Music: {gender}",
        "Double Battle: No",
        "AI: Basic Trainer",
        "",
    ]
    for sp, lv in mons:
        lines += [sp, f"Level: {lv}", "IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe", "- Tackle", ""]
    PARTY.write_text(PARTY.read_text().rstrip() + "\n\n" + "\n".join(lines) + "\n")


def register_maps(outdoor, indoor, indoor_group):
    g = json.loads(GROUPS.read_text())
    g.setdefault("gMapGroup_TownsAndRoutes", [])
    for n in outdoor:
        if n not in g["gMapGroup_TownsAndRoutes"]:
            g["gMapGroup_TownsAndRoutes"].append(n)
    g.setdefault(indoor_group, [])
    for n in indoor:
        if n not in g[indoor_group]:
            g[indoor_group].append(n)
    if "group_order" in g and indoor_group not in g["group_order"]:
        g["group_order"].append(indoor_group)
    GROUPS.write_text(json.dumps(g, indent=2) + "\n")
    es = EVENT_SCRIPTS.read_text()
    for n in outdoor + indoor:
        inc = f'\t.include "data/maps/{n}/scripts.inc"'
        if inc not in es:
            es = es.rstrip() + "\n" + inc + "\n"
    EVENT_SCRIPTS.write_text(es)


def find_walkable(grid, prefer=None):
    """Return a walkable tile; prefer near `prefer` (x,y) if given."""
    h, w = len(grid), len(grid[0])
    walk = {MT_GRASS, MT_TALL, MT_SAND, CAVE_FLOOR, 0x001, IN_FLOOR}
    cands = [(x, y) for y in range(h) for x in range(w) if grid[y][x] in walk or grid[y][x] == MT_WATER]
    # Prefer non-water
    land = [(x, y) for x, y in cands if grid[y][x] != MT_WATER]
    pool = land or cands
    if not pool:
        return w // 2, h // 2
    if prefer:
        px, py = prefer
        pool.sort(key=lambda p: abs(p[0] - px) + abs(p[1] - py))
    return pool[0]


def indoor_room(name, w=16, h=12, north_door=False):
    grid = [
        [
            IN_WALL
            if y in (0, h - 1) or x in (0, w - 1)
            else (
                IN_DOOR
                if (y == h - 1 and x in (w // 2 - 1, w // 2))
                or (north_door and y == 0 and x in (w // 2 - 1, w // 2))
                else IN_FLOOR
            )
            for x in range(w)
        ]
        for y in range(h)
    ]
    lid = write_layout(name, w, h, "gTileset_Building", "gTileset_Facility", pack(grid))
    return lid, w, h


def face(d):
    return {
        "DIR_NORTH": "MOVEMENT_TYPE_FACE_UP",
        "DIR_SOUTH": "MOVEMENT_TYPE_FACE_DOWN",
        "DIR_WEST": "MOVEMENT_TYPE_FACE_LEFT",
        "DIR_EAST": "MOVEMENT_TYPE_FACE_RIGHT",
    }.get(d or "", "MOVEMENT_TYPE_FACE_DOWN")


GFX_DEFAULT = {
    "OBJ_EVENT_GFX_GALACTIC_GRUNT_M": "OBJ_EVENT_GFX_AQUA_MEMBER_M",
    "OBJ_EVENT_GFX_GALACTIC_GRUNT_F": "OBJ_EVENT_GFX_AQUA_MEMBER_F",
    "OBJ_EVENT_GFX_COMMANDER_MARS": "OBJ_EVENT_GFX_ARCHIE",
    "OBJ_EVENT_GFX_COMMANDER_JUPITER": "OBJ_EVENT_GFX_ARCHIE",
    "OBJ_EVENT_GFX_COMMANDER_SATURN": "OBJ_EVENT_GFX_MAXIE",
    "OBJ_EVENT_GFX_CYRUS": "OBJ_EVENT_GFX_MAXIE",
    "OBJ_EVENT_GFX_ACE_TRAINER_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_ACE_TRAINER_F": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_SAILOR": "OBJ_EVENT_GFX_SAILOR",
    "OBJ_EVENT_GFX_FISHERMAN": "OBJ_EVENT_GFX_FISHERMAN",
    "OBJ_EVENT_GFX_SWIMMER_M": "OBJ_EVENT_GFX_SWIMMER_M",
    "OBJ_EVENT_GFX_SWIMMER_F": "OBJ_EVENT_GFX_SWIMMER_F",
    "OBJ_EVENT_GFX_TUBER_M": "OBJ_EVENT_GFX_TUBER_M",
    "OBJ_EVENT_GFX_TUBER_F": "OBJ_EVENT_GFX_TUBER_F",
    "OBJ_EVENT_GFX_YOUNGSTER": "OBJ_EVENT_GFX_YOUNGSTER",
    "OBJ_EVENT_GFX_LASS": "OBJ_EVENT_GFX_LASS",
    "OBJ_EVENT_GFX_HIKER": "OBJ_EVENT_GFX_HIKER",
    "OBJ_EVENT_GFX_BEAUTY": "OBJ_EVENT_GFX_BEAUTY",
    "OBJ_EVENT_GFX_GUITARIST": "OBJ_EVENT_GFX_MAN_5",
    "OBJ_EVENT_GFX_WORKER_M": "OBJ_EVENT_GFX_MAN_4",
    "OBJ_EVENT_GFX_RICH_BOY": "OBJ_EVENT_GFX_RICH_BOY",
    "OBJ_EVENT_GFX_LADY": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_POKEFAN_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_POKEFAN_F": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_GIRL_1": "OBJ_EVENT_GFX_GIRL_1",
    "OBJ_EVENT_GFX_BOY_1": "OBJ_EVENT_GFX_BOY_1",
    "OBJ_EVENT_GFX_OLD_MAN": "OBJ_EVENT_GFX_OLD_MAN",
    "OBJ_EVENT_GFX_OLD_WOMAN": "OBJ_EVENT_GFX_OLD_WOMAN",
    "OBJ_EVENT_GFX_NINJA_BOY": "OBJ_EVENT_GFX_NINJA_BOY",
    "OBJ_EVENT_GFX_ITEM_BALL": "OBJ_EVENT_GFX_ITEM_BALL",
}
