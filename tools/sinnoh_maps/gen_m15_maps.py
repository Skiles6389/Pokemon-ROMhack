#!/usr/bin/env python3
"""
Generate M15 Sinnoh layouts from pret/pokeplatinum land-data collision tables,
using Emerald metatiles only (same approach as M13/M14).

Land IDs:
  Eterna Forest (3x3): MAP_338..346
  Route 205 North: MAP_043
  Eterna City (2x2 L): MAP_044,046 / MAP_045,(empty)
  Eterna Gym: MAP_294
  Team Galactic Eterna Building: MAP_333,238,239,240

No DS graphics are copied.
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAT_DATA = Path("/tmp/pokeplatinum-ref/res/field/mapmodels/data")
LAYOUTS = REPO / "data" / "layouts"
LAYOUTS_JSON = LAYOUTS / "layouts.json"

MT_GRASS = 0x001
MT_TALL_GRASS = 0x00D
MT_SAND = 0x121
MT_WATER = 0x170
MT_TREE_TL, MT_TREE_TR = 0x1D4, 0x1D5
MT_TREE_BL, MT_TREE_BR = 0x1DC, 0x1DD
MT_ROCK = 0x079
MT_LEDGE_DOWN = 0x0D5
MT_LEDGE_DOWN2 = 0x0D6
MT_MOSS = 0x00E  # leafy / mossy ground stand-in

IN_FLOOR = 0x201
IN_WALL = 0x21A
IN_DOOR = 0x20E

BEH_TALL_GRASS = 0x02
BEH_VERY_TALL_GRASS = 0x03
BEH_WATER_RIVER = 0x10
BEH_WATER_SEA = 0x15
BEH_SAND = 0x21
BEH_JUMP_EAST = 0x38
BEH_JUMP_WEST = 0x39
BEH_JUMP_NORTH = 0x3A
BEH_JUMP_SOUTH = 0x3B


def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]


def attr_to_outdoor(v: int, x: int, y: int) -> int:
    col = (v >> 15) & 1
    beh = v & 0xFF
    if col:
        if (x & 1) == 0 and (y & 1) == 0:
            return MT_TREE_TL
        if (x & 1) == 1 and (y & 1) == 0:
            return MT_TREE_TR
        if (x & 1) == 0 and (y & 1) == 1:
            return MT_TREE_BL
        return MT_TREE_BR
    if beh in (BEH_TALL_GRASS, BEH_VERY_TALL_GRASS):
        return MT_TALL_GRASS
    if beh in (BEH_WATER_RIVER, BEH_WATER_SEA):
        return MT_WATER
    if beh == BEH_SAND:
        return MT_SAND
    if beh == BEH_JUMP_SOUTH:
        return MT_LEDGE_DOWN if (x & 1) == 0 else MT_LEDGE_DOWN2
    if beh in (BEH_JUMP_EAST, BEH_JUMP_WEST, BEH_JUMP_NORTH):
        return MT_ROCK
    return MT_GRASS


def attr_to_indoor(v: int, x: int, y: int) -> int:
    col = (v >> 15) & 1
    if col:
        return IN_WALL
    return IN_FLOOR


def attrs_to_metatile_grid(attr_grid: list[list[int]], indoor: bool = False) -> list[list[int]]:
    h, w = len(attr_grid), len(attr_grid[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            out[y][x] = attr_to_indoor(attr_grid[y][x], x, y) if indoor else attr_to_outdoor(attr_grid[y][x], x, y)
    return out


def pack(grid: list[list[int]]) -> bytes:
    h, w = len(grid), len(grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            struct.pack_into("<H", out, (y * w + x) * 2, __import__("tools.sinnoh_maps.sinnoh_build_lib", fromlist=["encode_map_cell"]).encode_map_cell(grid[y][x]))
    return bytes(out)


def open_path(grid: list[list[int]], points: list[tuple[int, int]], mt: int = MT_GRASS):
    blocked = (MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR, IN_WALL, MT_ROCK)
    for x, y in points:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = mt
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                    if grid[ny][nx] in blocked:
                        grid[ny][nx] = mt


def stamp_building(grid, door_x, door_y, kind="house"):
    if kind == "center":
        facade = [
            [0x048, 0x049, 0x282, 0x283],
            [0x050, 0x051, 0x052, 0x053],
            [0x058, 0x059, 0x05A, 0x05B],
            [0x060, 0x061, 0x062, 0x063],
        ]
        door_dx = 1
    elif kind == "mart":
        facade = [
            [0x030, 0x031, 0x032, 0x033],
            [0x038, 0x039, 0x03A, 0x03B],
            [0x060, 0x041, 0x042, 0x043],
        ]
        door_dx = 1
    elif kind == "gym":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x230, 0x231, 0x219, 0x21A],
            [0x222, 0x232, 0x238, 0x248, 0x240, 0x221],
            [0x22A, 0x23A, 0x238, 0x248, 0x248, 0x229],
        ]
        door_dx = 2
    elif kind == "galactic":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x230, 0x219, 0x219, 0x21A],
            [0x218, 0x219, 0x231, 0x238, 0x231, 0x219, 0x21A],
            [0x222, 0x232, 0x240, 0x248, 0x240, 0x240, 0x221],
        ]
        door_dx = 3
    else:
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x219, 0x21A],
            [0x222, 0x232, 0x230, 0x240, 0x221],
            [0x22A, 0x23A, 0x238, 0x248, 0x229],
        ]
        door_dx = 3
    top = door_y - (len(facade) - 1)
    left = door_x - door_dx
    for dy, row in enumerate(facade):
        for dx, mt_id in enumerate(row):
            x, y = left + dx, top + dy
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = mt_id


def layout_id_for(name: str) -> str:
    return "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")


def write_layout(name: str, width: int, height: int, primary: str, secondary: str, blockdata: bytes):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blockdata)
    border_src = LAYOUTS / ("AquaHideout_1F" if "Facility" in secondary else "Route203") / "border.bin"
    if "Building" in primary or secondary.endswith("Gym"):
        for cand in ("RustboroCity_Gym", "PetalburgCity_Gym", "House1"):
            if (LAYOUTS / cand / "border.bin").exists():
                border_src = LAYOUTS / cand / "border.bin"
                break
    if not border_src.exists():
        border_src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(border_src.read_bytes())

    layouts = json.loads(LAYOUTS_JSON.read_text())
    layout_id = layout_id_for(name)
    alt = "LAYOUT_" + name.upper()
    layouts["layouts"] = [L for L in layouts["layouts"] if L.get("id") not in (layout_id, alt)]
    layouts["layouts"].append(
        {
            "id": layout_id,
            "name": f"{name}_Layout",
            "width": width,
            "height": height,
            "primary_tileset": primary,
            "secondary_tileset": secondary,
            "border_filepath": f"data/layouts/{name}/border.bin",
            "blockdata_filepath": f"data/layouts/{name}/map.bin",
            "layout_version": "emerald",
        }
    )
    LAYOUTS_JSON.write_text(json.dumps(layouts, indent=2) + "\n")
    print(f"Wrote {name} {width}x{height} ({len(blockdata)} bytes) id={layout_id}")


def stitch_chunks(chunk_ids: list[list[int | None]]) -> list[list[int]]:
    rows = len(chunk_ids)
    cols = len(chunk_ids[0])
    h, w = rows * 32, cols * 32
    grid = [[0] * w for _ in range(h)]
    for cy in range(rows):
        for cx in range(cols):
            lid = chunk_ids[cy][cx]
            if lid is None:
                for ly in range(32):
                    for lx in range(32):
                        # solid trees for unused city quadrant
                        grid[cy * 32 + ly][cx * 32 + lx] = 0x8000  # collision
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    grid[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return grid


def crop_indoor(land_id: int, width: int, height: int) -> list[list[int]]:
    attrs = load_attrs(land_id)
    return [[attrs[y * 32 + x] for x in range(width)] for y in range(height)]


def main():
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        sys.exit(1)

    # --- Eterna Forest 3x3: MAP_338..346 ---
    # groups.json: [["MAP_338","MAP_339","MAP_340"],["MAP_341","MAP_342","MAP_343"],["MAP_344","MAP_345","MAP_346"]]
    forest_ids = [
        [338, 339, 340],
        [341, 342, 343],
        [344, 345, 346],
    ]
    g = stitch_chunks(forest_ids)
    mt = attrs_to_metatile_grid(g)
    # South exit to Route 205 South (28-29,86)
    open_path(mt, [(x, y) for x in range(27, 31) for y in range(84, 90)])
    # East exit to Route 205 North (86,36-37)
    open_path(mt, [(x, y) for x in range(84, 90) for y in range(34, 40)])
    # Old Chateau exterior approach (74,15) — leave path, gate interior in scripts
    open_path(mt, [(x, y) for x in range(72, 77) for y in range(13, 18)])
    # Moss Rock area (17,66)
    open_path(mt, [(x, y) for x in range(15, 20) for y in range(64, 69)])
    mt[66][17] = MT_MOSS
    # Cheryl start (28,83)
    open_path(mt, [(x, y) for x in range(26, 31) for y in range(81, 86)])
    write_layout("EternaForest", 96, 96, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Route 205 North: MAP_043 ---
    a43 = load_attrs(43)
    g = [[a43[y * 32 + x] for x in range(32)] for y in range(32)]
    mt = attrs_to_metatile_grid(g)
    # West warps to forest (3,12-13)
    open_path(mt, [(x, y) for x in range(1, 6) for y in range(10, 16)])
    # East connection into Eterna City (~y 16-22)
    open_path(mt, [(31, y) for y in range(14, 24)])
    write_layout("Route205_North", 32, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Eterna City: 64x64 from MAP_044|046 / MAP_045|None ---
    city_ids = [
        [44, 46],
        [45, None],
    ]
    g = stitch_chunks(city_ids)
    mt = attrs_to_metatile_grid(g)
    # West connection from Route 205 North
    open_path(mt, [(0, y) for y in range(14, 24)])
    # Building doors (local coords from Platinum events)
    doors = {
        "center": (17, 18),
        "mart": (21, 36),
        "house": (22, 27),  # bike shop
        "galactic": (17, 7),
        "house": (27, 36),  # condo — overwritten; stamp individually below
        "gym": (24, 50),
    }
    stamp_building(mt, 17, 18, "center")
    open_path(mt, [(17, 18), (16, 18), (18, 18), (17, 19)])
    stamp_building(mt, 21, 36, "mart")
    open_path(mt, [(21, 36), (20, 36), (22, 36), (21, 37)])
    stamp_building(mt, 22, 27, "house")  # bike shop
    open_path(mt, [(22, 27), (21, 27), (23, 27), (22, 28)])
    stamp_building(mt, 17, 7, "galactic")
    open_path(mt, [(17, 7), (16, 7), (18, 7), (17, 8)])
    stamp_building(mt, 27, 36, "house")  # condo / name rater
    open_path(mt, [(27, 36), (26, 36), (28, 36), (27, 37)])
    stamp_building(mt, 10, 50, "house")  # south house / underground man nearby
    open_path(mt, [(10, 50), (9, 50), (11, 50), (10, 51)])
    stamp_building(mt, 22, 18, "house")  # underground man
    open_path(mt, [(22, 18), (21, 18), (23, 18), (22, 19)])
    stamp_building(mt, 39, 25, "house")  # east house
    open_path(mt, [(39, 25), (38, 25), (40, 25), (39, 26)])
    stamp_building(mt, 28, 9, "house")  # herb shop
    open_path(mt, [(28, 9), (27, 9), (29, 9), (28, 10)])
    stamp_building(mt, 24, 50, "gym")
    open_path(mt, [(24, 50), (23, 50), (25, 50), (24, 51)])
    # Cynthia / Galactic cut-tree approach
    open_path(mt, [(x, y) for x in range(14, 20) for y in range(7, 14)])
    # Statue plaza (~39,13)
    open_path(mt, [(x, y) for x in range(36, 44) for y in range(10, 18)])
    # South cycling road gate (16-17,57) — progression gated in scripts
    open_path(mt, [(x, y) for x in range(15, 19) for y in range(55, 60)])
    # East Route 211 exit (~56-63,y~18)
    open_path(mt, [(x, y) for x in range(55, 64) for y in range(14, 24)])
    write_layout("EternaCity", 64, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Eterna Gym: crop MAP_294 to 22x28 ---
    g = crop_indoor(294, 22, 28)
    mt = attrs_to_metatile_grid(g, indoor=True)
    open_path(mt, [(x, y) for x in range(8, 15) for y in range(1, 28)], IN_FLOOR)
    open_path(mt, [(x, y) for x in range(1, 21) for y in range(15, 27)], IN_FLOOR)
    mt[27][11] = IN_DOOR
    write_layout("EternaCity_Gym", 22, 28, "gTileset_Building", "gTileset_RustboroGym", pack(mt))

    # --- Team Galactic Eterna Building floors ---
    # 1F MAP_333 → 22x18
    g = crop_indoor(333, 22, 18)
    mt = attrs_to_metatile_grid(g, indoor=True)
    open_path(mt, [(x, y) for x in range(2, 21) for y in range(3, 17)], IN_FLOOR)
    mt[15][11] = IN_DOOR
    write_layout("TeamGalacticEternaBuilding_1F", 22, 18, "gTileset_General", "gTileset_Facility", pack(mt))

    # 2F MAP_238 → 24x16
    g = crop_indoor(238, 24, 16)
    mt = attrs_to_metatile_grid(g, indoor=True)
    open_path(mt, [(x, y) for x in range(2, 22) for y in range(2, 15)], IN_FLOOR)
    write_layout("TeamGalacticEternaBuilding_2F", 24, 16, "gTileset_General", "gTileset_Facility", pack(mt))

    # 3F MAP_239 → 22x14
    g = crop_indoor(239, 22, 14)
    mt = attrs_to_metatile_grid(g, indoor=True)
    open_path(mt, [(x, y) for x in range(1, 21) for y in range(2, 13)], IN_FLOOR)
    write_layout("TeamGalacticEternaBuilding_3F", 22, 14, "gTileset_General", "gTileset_Facility", pack(mt))

    # 4F MAP_240 → 24x14
    g = crop_indoor(240, 24, 14)
    mt = attrs_to_metatile_grid(g, indoor=True)
    open_path(mt, [(x, y) for x in range(2, 22) for y in range(2, 13)], IN_FLOOR)
    write_layout("TeamGalacticEternaBuilding_4F", 24, 14, "gTileset_General", "gTileset_Facility", pack(mt))

    # Reinforce Route 205 South north exit into forest (already opened in M14)
    r205 = LAYOUTS / "Route205_South" / "map.bin"
    w, h = 32, 96
    data = bytearray(r205.read_bytes())

    def set_(x, y, mt_):
        struct.pack_into("<H", data, (y * w + x) * 2, mt_)

    for y in range(3, 8):
        for x in range(13, 17):
            set_(x, y, MT_GRASS)
    r205.write_bytes(data)
    print("Reinforced Route205_South north exit into Eterna Forest")


if __name__ == "__main__":
    main()
