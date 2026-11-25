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
MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR = 0x1D4, 0x1D5, 0x1DC, 0x1DD
MT_TREE = (MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR)
MT_ROCK, MT_LEDGE_A, MT_LEDGE_B = 0x079, 0x0D5, 0x0D6
# Emerald General jump metatiles (south pair used by converter; E/W approx as rock edge)
MT_LEDGE_S_A, MT_LEDGE_S_B = MT_LEDGE_A, MT_LEDGE_B
IN_FLOOR, IN_WALL, IN_DOOR = 0x201, 0x21A, 0x20E
MT_CAVE_FLOOR = 0x1A1
# Fallarbor cave floor often 0x1A1; if missing in tileset, grass still walks
CAVE_FLOOR = 0x001
CAVE_WALL = 0x079

# Emerald General dirt-path 3x3 (Oldale / Route101 style) + soft grass corners
#   1D0 1D1 1D2
#   1D8 1D9 1DA
#   1E0 1E1 1E2
MT_PATH_TL, MT_PATH_T, MT_PATH_TR = 0x1D0, 0x1D1, 0x1D2
MT_PATH_L, MT_PATH_C, MT_PATH_R = 0x1D8, 0x1D9, 0x1DA
MT_PATH_BL, MT_PATH_B, MT_PATH_BR = 0x1E0, 0x1E1, 0x1E2
MT_PATH_TABLE = (
    (MT_PATH_TL, MT_PATH_T, MT_PATH_TR),
    (MT_PATH_L, MT_PATH_C, MT_PATH_R),
    (MT_PATH_BL, MT_PATH_B, MT_PATH_BR),
)
PATH_METATILES = {mt for row in MT_PATH_TABLE for mt in row} | {
    0x1E4, 0x1E5, 0x1E6, 0x1E7, 0x003, 0x004,
    # Littleroot-style dirt strips (Twinleaf / early towns)
    0x1CE, 0x1CF,
    # Emerald city sidewalk / plaza (Rustboro / Lilycove) — paved cities
    0x2BB, 0x2C3, 0x22B, 0x233,
}

# Platinum terrain behaviors that are dirt / bike / town walkways (not plain grass).
# 0xA9 = Twinleaf walkways; 0x70/0x71/… = route bike & dirt trails; 0xA4/0xA5 = marsh boardwalk-ish.
PLAT_PATH_BEHAVIORS = {
    0x70, 0x71, 0x73, 0x75, 0x76, 0x79, 0x7A, 0x7C, 0x7D,
    0xA4, 0xA5, 0xA9,
}
# Snow route/town packed snow used as path stand-in (sand metatile keeps elev walkable).
PLAT_SNOW_PATH_BEHAVIORS = {0xA1, 0xA2, 0xA3, 0xA8}

# Metatile IDs that must be impassable when packing map.bin (bits 10-11).
# Building facade IDs from stamp_building also belong here.
SOLID_METATILES = set(MT_TREE) | {
    MT_ROCK,
    CAVE_WALL,
    IN_WALL,
    0x139,  # cliff / wall stand-in used on early routes
    # Twinleaf/Sandgem/Petalburg house + gym facade tiles (secondary)
    0x208, 0x20A, 0x210, 0x211, 0x212, 0x218, 0x219, 0x21A,
    0x221, 0x222, 0x229, 0x22A, 0x230, 0x231, 0x232, 0x238, 0x23A,
    0x240, 0x241, 0x242, 0x248, 0x282, 0x283,
    0x29A, 0x2A2, 0x2F9,
}
# Ledges (0x0D5/0x0D6) MUST stay collision=1 so only JumpSouth works — not walkable.
WALKABLE_METATILES = {
    MT_GRASS, MT_TALL, MT_WATER, MT_SAND, CAVE_FLOOR, IN_FLOOR, IN_DOOR,
    0x00E, 0x015, 0x048, 0x049, 0x201, 0x209, 0x20E,
} | PATH_METATILES
# Calm + reflective + rough water — all need Surf elev packing (coll=0, elev=1).
WATER_METATILES = {MT_WATER, 0x0A1, 0x14E, 0x14F}


def is_plat_path_behavior(beh: int) -> bool:
    return beh in PLAT_PATH_BEHAVIORS


def path_metatile_for_neighbors(n: bool, s: bool, w: bool, e: bool) -> int:
    """Pick Emerald dirt-path metatile from 4-neighbor path connectivity."""
    # Thin strips use the center row/col so 1-wide trails aren't all edge tiles.
    if not n and not s:
        row = 1
    elif not n:
        row = 0
    elif not s:
        row = 2
    else:
        row = 1
    if not w and not e:
        col = 1
    elif not w:
        col = 0
    elif not e:
        col = 2
    else:
        col = 1
    return MT_PATH_TABLE[row][col]


# Outdoor settlements/routes where beh-0 ground is the visible dirt trail when
# Platinum omits path behaviors (NSBMD-only nsand). Forests/caves/indoors excluded.
_PATH_FALLBACK_HINTS = (
    "Town", "City", "Route", "Lakefront", "Valor", "Survival", "Fight",
    "Resort", "League_Exterior", "ValleyWindworks", "StarkMountain_Outside",
    "IronIsland", "PokemonLeague_Exterior",
)


def map_allows_path_fallback(name: str) -> bool:
    if not name:
        return False
    if any(bad in name for bad in (
        "Forest", "Cave", "Mine", "Gym", "Gate", "Distortion", "Room", "Elevator",
        "Hall", "Interior", "Library", "Temple", "Ruins", "Chateau", "Manor",
        "Gallery", "Shop", "Center", "House", "Apartment", "Dept", "Museum",
    )):
        return False
    return any(h in name for h in _PATH_FALLBACK_HINTS)


def paint_paths_from_attrs(grid, attr, *, snow=False, fallback_plain=True, map_name: str = ""):
    """Overlay Emerald path metatiles wherever Platinum marks dirt/bike/walkway behaviors.

    Many early towns/routes (Sandgem, Jubilife, Route201) store dirt trails only in the
    NSBMD (`nsand`) with land-attr behavior 0. When path-behavior coverage is sparse,
    treat walkable plain ground (beh 0) as path so trails/walkways are not lost to grass.
    """
    h, w = len(grid), len(grid[0])
    path = [[False] * w for _ in range(h)]
    marked = 0
    for y in range(h):
        for x in range(w):
            if plat_collision(attr[y][x]):
                continue
            beh = plat_behavior(attr[y][x])
            if is_plat_path_behavior(beh):
                path[y][x] = True
                marked += 1
            elif snow and beh in PLAT_SNOW_PATH_BEHAVIORS:
                path[y][x] = True
                marked += 1

    # Fallback: no/few explicit path attrs → plain walkable ground is the trail/walkway.
    # Skip when Twinleaf-style maps already encode walkways (0xA9 etc.).
    if (
        fallback_plain
        and not snow
        and marked < 8
        and map_allows_path_fallback(map_name)
    ):
        for y in range(h):
            for x in range(w):
                if plat_collision(attr[y][x]):
                    continue
                beh = plat_behavior(attr[y][x])
                if beh == 0:
                    path[y][x] = True

    for y in range(h):
        for x in range(w):
            if not path[y][x]:
                continue
            cur = grid[y][x] & 0x3FF
            # Platinum walkable path cells are ground truth — overwrite grass/trees/filler.
            # Keep water & ledges (surf/jump); keep door mats already on walkable cells.
            if cur in WATER_METATILES or cur in (MT_LEDGE_A, MT_LEDGE_B):
                continue
            if cur in (IN_DOOR, 0x209, 0x20E):
                continue
            if snow and plat_behavior(attr[y][x]) in PLAT_SNOW_PATH_BEHAVIORS:
                grid[y][x] = MT_SAND
                continue
            n = y > 0 and path[y - 1][x]
            s = y + 1 < h and path[y + 1][x]
            ww = x > 0 and path[y][x - 1]
            e = x + 1 < w and path[y][x + 1]
            grid[y][x] = path_metatile_for_neighbors(n, s, ww, e)

    # Soft grass-corner accents beside path edges (optional polish, Emerald 1E4-1E7)
    for y in range(h):
        for x in range(w):
            if path[y][x] or plat_collision(attr[y][x]):
                continue
            if grid[y][x] not in (MT_GRASS, MT_TALL):
                continue
            # Only decorate plain grass next to a path cardinally
            neigh = []
            for dy, dx, bit in ((-1, 0, 1), (1, 0, 2), (0, -1, 4), (0, 1, 8)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and path[ny][nx]:
                    neigh.append(bit)
            if len(neigh) == 1:
                # Map single-side contact to a grass-path transition tile
                grid[y][x] = {1: 0x1E4, 2: 0x1E5, 4: 0x1E6, 8: 0x1E7}[neigh[0]]

    return sum(sum(1 for v in row if v) for row in path)


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


def plat_collision(v: int) -> int:
    return (v >> 15) & 1


def plat_behavior(v: int) -> int:
    return v & 0xFF


def attr_to_mt(v, x, y, *, cave=False, snow=False, indoor=False):
    """Legacy single-cell mapper. Prefer grid_from_chunks (2x2 trees)."""
    col, beh = plat_collision(v), plat_behavior(v)
    if col:
        if indoor:
            return IN_WALL
        if cave:
            return CAVE_WALL
        return MT_TREE[(y & 1) * 2 + (x & 1)]
    if beh in (0x02, 0x03):
        return MT_TALL
    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
        return MT_WATER
    if beh == 0x21:
        return MT_SAND
    if is_plat_path_behavior(beh):
        return MT_PATH_C  # edges applied by paint_paths_from_attrs
    if beh == 0x3B:
        return MT_LEDGE_A if (x & 1) == 0 else MT_LEDGE_B
    if beh in (0x38, 0x39, 0x3A):
        return MT_ROCK
    if indoor:
        return IN_FLOOR
    if cave:
        return CAVE_FLOOR
    if snow or beh in PLAT_SNOW_PATH_BEHAVIORS:
        return MT_SAND
    return MT_GRASS


def is_solid_metatile(mt: int) -> bool:
    mt &= 0x3FF
    if mt in WALKABLE_METATILES:
        return False
    if mt in SOLID_METATILES:
        return True
    # Building / cave secondary bodies: treat unknown 0x200+ as solid unless walkable.
    if mt >= 0x200:
        return True
    return False


def encode_map_cell(mt: int, *, collision: int | None = None) -> int:
    """Pack Emerald map.bin cell: metatile | (collision<<10) | (elevation<<12).

    Engine reads collision from these bits (MapGridGetCollisionAt), NOT from
    metatile_attributes. Older converters wrote mt&0x3FF only → walk-through walls.
    """
    mt = mt & 0x3FF
    if collision is None:
        collision = 1 if is_solid_metatile(mt) else 0
    collision = 1 if collision else 0
    if mt in WATER_METATILES:
        # Match vanilla Emerald ocean/pond packing (Route103/104/105):
        # collision=0 + elevation=1 → COLLISION_ELEVATION_MISMATCH vs player
        # elev 3, which blocks walking and enables the Surf prompt.
        elev = 1
        collision = 0
    elif collision:
        elev = 0
    else:
        elev = 3
    return mt | (collision << 10) | (elev << 12)


def pack(grid, collision_grid=None):
    """Write map.bin bytes with collision + elevation bits set.

    If collision_grid is provided (0/1 per cell from Platinum), use it.
    Otherwise infer solidity from metatile ID.
    """
    h, w = len(grid), len(grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            coll = None if collision_grid is None else collision_grid[y][x]
            struct.pack_into("<H", out, (y * w + x) * 2, encode_map_cell(mt, collision=coll))
    return bytes(out)


def pack_reencode(blob: bytes) -> bytes:
    """Re-encode an existing map.bin that had collision/elevation stripped."""
    out = bytearray(len(blob))
    for i in range(0, len(blob), 2):
        mt = struct.unpack_from("<H", blob, i)[0] & 0x3FF
        struct.pack_into("<H", out, i, encode_map_cell(mt))
    return bytes(out)


def place_complete_trees(solid: list[list[bool]], *, cave=False, indoor=False):
    """Place full 2x2 Emerald trees on solid blocks; avoid orphan halves.

    Pass 1: even-aligned solid quads → trees (or cave/indoor walls).
    Pass 2 (outdoor): leftover solids try any TL that covers them, borrowing
    adjacent solid/unused cells so town tree rings stay complete 2x2s.
    Pass 3: still-unused outdoor leftovers stay solid via rock only when they
    cannot form a tree (true cliff stubs); cave/indoor always use walls.
    """
    h, w = len(solid), len(solid[0])
    grid = [[0] * w for _ in range(h)]
    used = [[False] * w for _ in range(h)]
    wall = IN_WALL if indoor else (CAVE_WALL if cave else MT_ROCK)

    def stamp_tree(tx: int, ty: int) -> None:
        grid[ty][tx] = MT_TREE_TL
        grid[ty][tx + 1] = MT_TREE_TR
        grid[ty + 1][tx] = MT_TREE_BL
        grid[ty + 1][tx + 1] = MT_TREE_BR
        for dy in range(2):
            for dx in range(2):
                used[ty + dy][tx + dx] = True
                solid[ty + dy][tx + dx] = True

    def stamp_wall(tx: int, ty: int) -> None:
        for dy in range(2):
            for dx in range(2):
                grid[ty + dy][tx + dx] = wall
                used[ty + dy][tx + dx] = True

    for y in range(0, h - 1, 2):
        for x in range(0, w - 1, 2):
            if solid[y][x] and solid[y][x + 1] and solid[y + 1][x] and solid[y + 1][x + 1]:
                if indoor or cave:
                    stamp_wall(x, y)
                else:
                    stamp_tree(x, y)

    if not indoor and not cave:
        # Greedy non-overlapping: cover leftover solids with 2x2 trees.
        # Require ≥3 of 4 cells already solid so we don't eat walk corridors.
        changed = True
        while changed:
            changed = False
            for y in range(h):
                for x in range(w):
                    if not solid[y][x] or used[y][x]:
                        continue
                    for tx, ty in ((x & ~1, y & ~1), (x, y), (x - 1, y), (x, y - 1), (x - 1, y - 1)):
                        if tx < 0 or ty < 0 or tx + 1 >= w or ty + 1 >= h:
                            continue
                        cells = [(tx, ty), (tx + 1, ty), (tx, ty + 1), (tx + 1, ty + 1)]
                        if any(used[cy][cx] for cx, cy in cells):
                            continue
                        solid_n = sum(1 for cx, cy in cells if solid[cy][cx])
                        if solid_n < 3:
                            continue
                        stamp_tree(tx, ty)
                        changed = True
                        break

    for y in range(h):
        for x in range(w):
            if solid[y][x] and not used[y][x]:
                grid[y][x] = wall
    return grid


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
    blocked = set(MT_TREE) | {MT_ROCK, CAVE_WALL, IN_WALL, 0x139}
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
                    elif is_plat_path_behavior(beh) or (snow and beh in PLAT_SNOW_PATH_BEHAVIORS):
                        continue  # paint_paths_from_attrs owns these
                    elif grid[y][x] in blocked:
                        grid[y][x] = CAVE_FLOOR if cave else (MT_SAND if snow else MT_GRASS)


def grid_from_chunks(chunks, *, cave=False, snow=False, indoor=False):
    """Build Emerald metatile grid from Platinum land chunks.

    Returns (grid, w, h, collision_grid) where collision_grid mirrors Platinum bit15.
    """
    attr = stitch(chunks)
    h, w = len(attr), len(attr[0])
    solid = [[plat_collision(attr[y][x]) == 1 for x in range(w)] for y in range(h)]
    collision = [[1 if solid[y][x] else 0 for x in range(w)] for y in range(h)]
    grid = place_complete_trees(solid, cave=cave, indoor=indoor)

    for y in range(h):
        for x in range(w):
            if solid[y][x]:
                continue
            beh = plat_behavior(attr[y][x])
            if beh in (0x02, 0x03):
                grid[y][x] = MT_TALL
            elif beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
                grid[y][x] = MT_WATER
            elif beh == 0x21:
                grid[y][x] = MT_SAND
            elif beh == 0x3B:
                grid[y][x] = MT_LEDGE_A if (x & 1) == 0 else MT_LEDGE_B
            elif beh in (0x38, 0x39, 0x3A):
                # Side/north jump: rock edge stand-in (Emerald lacks 1:1 ledge tiles)
                grid[y][x] = MT_ROCK
                collision[y][x] = 1
            elif indoor:
                grid[y][x] = IN_FLOOR
            elif cave:
                grid[y][x] = CAVE_FLOOR
            elif snow:
                grid[y][x] = MT_SAND
            else:
                grid[y][x] = MT_GRASS

    paint_water(grid, chunks)
    paint_ledges(grid, chunks)
    clear_plat_walkables(grid, chunks, cave=cave, snow=snow)
    paint_water(grid, chunks)
    if not indoor and not cave:
        # map_name optional; callers that know the layout name should prefer
        # paint_paths_from_attrs(..., map_name=...) after this for fallback trails.
        paint_paths_from_attrs(grid, attr, snow=snow, fallback_plain=False)
    # Re-sync collision after paint/clear helpers
    for y in range(h):
        for x in range(w):
            mt = grid[y][x]
            if mt in WATER_METATILES or mt in PATH_METATILES or mt in (
                MT_TALL, MT_GRASS, MT_SAND, CAVE_FLOOR, IN_FLOOR, IN_DOOR
            ):
                collision[y][x] = 0
            elif mt in (MT_LEDGE_A, MT_LEDGE_B):
                collision[y][x] = 1  # one-way jump only
            elif is_solid_metatile(mt):
                collision[y][x] = 1
    return grid, w, h, collision


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
    "OBJ_EVENT_GFX_POKEBALL": "OBJ_EVENT_GFX_ITEM_BALL",
    "OBJ_EVENT_GFX_STRENGTH_BOULDER": "OBJ_EVENT_GFX_PUSHABLE_BOULDER",
    "OBJ_EVENT_GFX_ROCK_SMASH": "OBJ_EVENT_GFX_BREAKABLE_ROCK",
    "OBJ_EVENT_GFX_MARS": "OBJ_EVENT_GFX_ARCHIE",
    "OBJ_EVENT_GFX_JUPITER": "OBJ_EVENT_GFX_ARCHIE",
    "OBJ_EVENT_GFX_CHARON": "OBJ_EVENT_GFX_MAXIE",
    "OBJ_EVENT_GFX_GRUNT_M": "OBJ_EVENT_GFX_AQUA_MEMBER_M",
    "OBJ_EVENT_GFX_GRUNT_F": "OBJ_EVENT_GFX_AQUA_MEMBER_F",
}
