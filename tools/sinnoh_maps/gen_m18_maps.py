#!/usr/bin/env python3
"""
Generate M18 Sinnoh layouts from pret/pokeplatinum land-data collision tables,
using Emerald metatiles only (same approach as M13–M17).

Land IDs (TownsAndRoutes matrix):
  Route 209 (2x2 L):  [None,74] / [76,75]  origin c16,r21
  Solaceon Town (1x2): [72,73]             origin c17,r20
  Route 210 South:     [66]/[67]/[68]      origin c17,r17  (32x96)
  Route 215 (1x3):     [69,70,71]          origin c18,r18  (96x32)

Interiors (custom Emerald Building layouts inspired by Platinum footprints):
  Lost Tower 1F–5F, Cafe Cabin

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
MT_CAVE_ENTRANCE = 0x079

IN_FLOOR = 0x201
IN_WALL = 0x21A
IN_DOOR = 0x20E
IN_STAIRS = 0x20F
IN_COUNTER = 0x219

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
    elif kind == "cave":
        facade = [
            [MT_ROCK, MT_ROCK, MT_ROCK, MT_ROCK],
            [MT_ROCK, MT_CAVE_ENTRANCE, MT_CAVE_ENTRANCE, MT_ROCK],
        ]
        door_dx = 1
    elif kind == "tower":
        facade = [
            [0x210, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x21A],
            [0x222, 0x230, 0x240, 0x221],
        ]
        door_dx = 1
    elif kind == "cafe":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x219, 0x21A],
            [0x222, 0x232, 0x230, 0x240, 0x221],
        ]
        door_dx = 2
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
    border_src = LAYOUTS / "Route203" / "border.bin"
    if "Building" in primary or secondary.endswith("Gym") or "Facility" in secondary:
        for cand in ("RustboroCity_Gym", "PetalburgCity_Gym", "House1", "PokemonCenter_1F"):
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
                        # Fill empty quadrant with solid trees so players can't wander off
                        grid[cy * 32 + ly][cx * 32 + lx] = 0x8000
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    grid[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return grid


def make_tower_floor(width: int, height: int, entrance_bottom: bool, stairs_up=None, stairs_down=None) -> list[list[int]]:
    """Simple Emerald tower hall: walls with a central floor corridor."""
    g = [[IN_WALL for _ in range(width)] for _ in range(height)]
    for y in range(2, height - 1):
        for x in range(2, width - 2):
            g[y][x] = IN_FLOOR
    # Side alcoves for trainers
    for room_y in (4, height // 2, height - 6):
        for y in range(room_y, min(room_y + 3, height - 2)):
            for x in range(2, 5):
                g[y][x] = IN_FLOOR
            for x in range(width - 5, width - 2):
                g[y][x] = IN_FLOOR
    if entrance_bottom:
        for x in range(width // 2 - 1, width // 2 + 2):
            g[height - 1][x] = IN_DOOR
            g[height - 2][x] = IN_FLOOR
    if stairs_up:
        sx, sy = stairs_up
        g[sy][sx] = IN_STAIRS
        g[sy][sx + 1] = IN_STAIRS
    if stairs_down:
        sx, sy = stairs_down
        g[sy][sx] = IN_STAIRS
        g[sy][sx + 1] = IN_STAIRS
    return g


def make_cafe(width: int = 12, height: int = 10) -> list[list[int]]:
    g = [[IN_WALL for _ in range(width)] for _ in range(height)]
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            g[y][x] = IN_FLOOR
    # Counter near north wall
    for x in range(3, 9):
        g[2][x] = IN_COUNTER
    g[height - 1][width // 2] = IN_DOOR
    g[height - 1][width // 2 - 1] = IN_DOOR
    return g


def main():
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        sys.exit(1)

    # --- Route 209: 64x64 L-shape [None,74]/[76,75] ---
    r209_ids = [
        [None, 74],
        [76, 75],
    ]
    g = stitch_chunks(r209_ids)
    mt = attrs_to_metatile_grid(g)
    # West gate approach (0,54-55)
    open_path(mt, [(x, y) for x in range(0, 6) for y in range(52, 58)], MT_SAND)
    # Path north toward Solaceon through east column
    open_path(mt, [(x, y) for x in range(40, 56) for y in range(0, 20)], MT_SAND)
    open_path(mt, [(x, y) for x in range(32, 48) for y in range(16, 40)], MT_GRASS)
    # Lost Tower approach (56,8)
    open_path(mt, [(x, y) for x in range(52, 60) for y in range(6, 14)], MT_SAND)
    stamp_building(mt, 56, 8, "tower")
    open_path(mt, [(56, 8), (56, 9), (55, 8), (57, 8)], MT_SAND)
    # Hallowed Tower landmark plaza (~54,41)
    open_path(mt, [(x, y) for x in range(52, 58) for y in range(39, 45)], MT_SAND)
    for x, y in ((54, 41), (55, 41), (54, 42), (55, 42)):
        mt[y][x] = MT_ROCK
    write_layout("Route209", 64, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Solaceon Town: 64x32 ---
    sol_ids = [[72, 73]]
    g = stitch_chunks(sol_ids)
    mt = attrs_to_metatile_grid(g)
    open_path(mt, [(x, y) for x in range(8, 40) for y in range(14, 22)], MT_SAND)
    open_path(mt, [(x, y) for x in range(16, 30) for y in range(4, 28)], MT_SAND)
    open_path(mt, [(x, y) for x in range(0, 20) for y in range(28, 32)], MT_SAND)  # south to R209
    open_path(mt, [(x, y) for x in range(12, 24) for y in range(0, 4)], MT_SAND)  # north to R210
    doors = [
        (9, 5, "house"),   # Day Care
        (22, 16, "center"),
        (27, 25, "mart"),
        (27, 16, "house"),  # News Press
        (21, 6, "house"),   # North house
        (35, 8, "house"),   # NE house
        (37, 16, "house"),  # East house
    ]
    for dx, dy, kind in doors:
        stamp_building(mt, dx, dy, kind)
        open_path(mt, [(dx, dy), (dx, dy + 1)], MT_SAND)
    # Ruins exterior approach (east ledge / cave mouths)
    open_path(mt, [(x, y) for x in range(48, 56) for y in range(10, 18)], MT_SAND)
    stamp_building(mt, 51, 15, "cave")
    open_path(mt, [(51, 15), (51, 16)], MT_SAND)
    stamp_building(mt, 53, 12, "cave")
    open_path(mt, [(53, 12), (53, 13)], MT_SAND)
    write_layout("SolaceonTown", 64, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Route 210 South: 32x96 ---
    r210_ids = [[66], [67], [68]]
    g = stitch_chunks(r210_ids)
    mt = attrs_to_metatile_grid(g)
    open_path(mt, [(x, y) for x in range(12, 24) for y in range(88, 96)], MT_SAND)  # south to Solaceon
    open_path(mt, [(x, y) for x in range(14, 24) for y in range(40, 56)], MT_SAND)  # cafe / psyduck area
    open_path(mt, [(31, y) for y in range(48, 60)], MT_SAND)  # east toward R215 mid
    stamp_building(mt, 22, 47, "cafe")
    open_path(mt, [(22, 47), (22, 48), (21, 47), (23, 47)], MT_SAND)
    # Psyduck blockade corridor — keep walkable south of ducks, trees north beyond
    open_path(mt, [(x, y) for x in range(14, 20) for y in range(44, 50)], MT_SAND)
    write_layout("Route210_South", 32, 96, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Route 215: 96x32 rainy route ---
    r215_ids = [[69, 70, 71]]
    g = stitch_chunks(r215_ids)
    mt = attrs_to_metatile_grid(g)
    open_path(mt, [(0, y) for y in range(16, 28)], MT_SAND)  # west from R210
    open_path(mt, [(x, y) for x in range(0, 96) for y in range(18, 26)], MT_SAND)  # main road
    open_path(mt, [(x, y) for x in range(90, 96) for y in range(20, 26)], MT_SAND)  # Veilstone gate
    write_layout("Route215", 96, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Lost Tower floors ---
    # 1F: entrance south, stairs up north
    t1 = make_tower_floor(16, 16, entrance_bottom=True, stairs_up=(4, 3))
    write_layout("LostTower_1F", 16, 16, "gTileset_Building", "gTileset_Facility", pack(t1))
    t2 = make_tower_floor(16, 16, entrance_bottom=False, stairs_up=(10, 3), stairs_down=(4, 12))
    write_layout("LostTower_2F", 16, 16, "gTileset_Building", "gTileset_Facility", pack(t2))
    t3 = make_tower_floor(16, 16, entrance_bottom=False, stairs_up=(4, 3), stairs_down=(10, 12))
    write_layout("LostTower_3F", 16, 16, "gTileset_Building", "gTileset_Facility", pack(t3))
    t4 = make_tower_floor(16, 16, entrance_bottom=False, stairs_up=(10, 3), stairs_down=(4, 12))
    write_layout("LostTower_4F", 16, 16, "gTileset_Building", "gTileset_Facility", pack(t4))
    t5 = make_tower_floor(16, 16, entrance_bottom=False, stairs_down=(10, 3))
    # Elder alcove
    for y in range(7, 12):
        for x in range(5, 11):
            t5[y][x] = IN_FLOOR
    write_layout("LostTower_5F", 16, 16, "gTileset_Building", "gTileset_Facility", pack(t5))

    # --- Cafe Cabin ---
    cafe = make_cafe(12, 10)
    write_layout("Route210_CafeCabin", 12, 10, "gTileset_Building", "gTileset_Shop", pack(cafe))

    print("M18 layouts done.")


if __name__ == "__main__":
    main()
