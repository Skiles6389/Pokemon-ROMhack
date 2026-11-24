#!/usr/bin/env python3
"""
Generate M16 Sinnoh layouts from pret/pokeplatinum land-data collision tables,
using Emerald metatiles only (same approach as M13–M15).

Land IDs:
  Route 206 (4x1): MAP_030,029,028,027
  Route 207 (1x2): MAP_025,026
  Mt. Coronet 1F South: MAP_351
  Route 208 (1x2): MAP_055,056

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
MT_CAVE_ENTRANCE = 0x121  # sand/dirt stand-in for cave mouth

CAVE_FLOOR = 0x211
CAVE_DARK = 0x201
CAVE_WALL = 0x221
CAVE_WATER = 0x201

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


def attr_to_cave(v: int, x: int, y: int) -> int:
    col = (v >> 15) & 1
    beh = v & 0xFF
    if col:
        return CAVE_WALL
    if beh in (BEH_WATER_RIVER, BEH_WATER_SEA):
        return CAVE_WATER
    return CAVE_FLOOR


def attrs_to_metatile_grid(attr_grid: list[list[int]], cave: bool = False) -> list[list[int]]:
    h, w = len(attr_grid), len(attr_grid[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            out[y][x] = attr_to_cave(attr_grid[y][x], x, y) if cave else attr_to_outdoor(attr_grid[y][x], x, y)
    return out


def pack(grid: list[list[int]]) -> bytes:
    h, w = len(grid), len(grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            struct.pack_into("<H", out, (y * w + x) * 2, grid[y][x] & 0x3FF)
    return bytes(out)


def open_path(grid: list[list[int]], points: list[tuple[int, int]], mt: int = MT_GRASS):
    blocked = (MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR, CAVE_WALL, MT_ROCK, IN_WALL)
    for x, y in points:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = mt
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                    if grid[ny][nx] in blocked:
                        grid[ny][nx] = mt


def stamp_building(grid, door_x, door_y, kind="house"):
    if kind == "gate":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x230, 0x219, 0x21A],
            [0x222, 0x232, 0x238, 0x240, 0x221],
            [0x22A, 0x23A, 0x238, 0x248, 0x229],
        ]
        door_dx = 2
    else:
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x219, 0x21A],
            [0x222, 0x232, 0x230, 0x240, 0x221],
            [0x22A, 0x23A, 0x238, 0x248, 0x229],
        ]
        door_dx = 2
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
    if "Cave" in secondary:
        border_src = LAYOUTS / "OreburghGate_1F" / "border.bin"
    else:
        border_src = LAYOUTS / "Route203" / "border.bin"
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
                        grid[cy * 32 + ly][cx * 32 + lx] = 0x8000
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    grid[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return grid


def main():
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        sys.exit(1)

    # --- Route 206: 32x128 from MAP_030/029/028/027 ---
    r206_ids = [[30], [29], [28], [27]]
    g = stitch_chunks(r206_ids)
    mt = attrs_to_metatile_grid(g)
    # North gate warps (16-17, 0)
    open_path(mt, [(x, y) for x in range(14, 20) for y in range(0, 4)])
    # Wayward Cave exterior entrance (~11, 35)
    open_path(mt, [(x, y) for x in range(9, 14) for y in range(33, 38)])
    mt[35][11] = MT_CAVE_ENTRANCE
    # Hidden Wayward entrance (~22, 31) — keep approach open, gate in scripts
    open_path(mt, [(x, y) for x in range(20, 25) for y in range(29, 33)])
    # South connection into Route 207 (~14-18, 127)
    open_path(mt, [(x, y) for x in range(12, 20) for y in range(124, 128)])
    # Cycling road spine (approx center column)
    open_path(mt, [(x, y) for x in range(14, 18) for y in range(0, 128)])
    write_layout("Route206", 32, 128, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Route 207: 64x32 from MAP_025|026 ---
    r207_ids = [[25, 26]]
    g = stitch_chunks(r207_ids)
    mt = attrs_to_metatile_grid(g)
    # North connection from Route 206 / Cycling Road south (~14-18, 0) matching R206 south
    open_path(mt, [(x, y) for x in range(12, 20) for y in range(0, 4)])
    # Oreburgh south connection — open corridor matching Oreburgh north exit x≈41-46
    open_path(mt, [(x, y) for x in range(40, 48) for y in range(28, 32)])
    # Also keep west-path open for Platinum-authentic south slope near x≈14
    open_path(mt, [(x, y) for x in range(12, 20) for y in range(28, 32)])
    # Mt. Coronet warp (~53, 8)
    open_path(mt, [(x, y) for x in range(50, 56) for y in range(6, 12)])
    mt[8][53] = MT_CAVE_ENTRANCE
    # Block Mt. Coronet 2F ledge approach (~60, 13) with rocks for later badges
    for x, y in [(59, 12), (60, 12), (61, 12), (60, 13)]:
        if 0 <= y < 32 and 0 <= x < 64:
            mt[y][x] = MT_ROCK
    # Dawn/Lucas counterpart (~13, 12) and trigger near cave (~52, 8)
    open_path(mt, [(x, y) for x in range(11, 16) for y in range(10, 15)])
    open_path(mt, [(x, y) for x in range(50, 55) for y in range(6, 12)])
    write_layout("Route207", 64, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Mt. Coronet 1F South: 32x32 MAP_351 ---
    attrs = load_attrs(351)
    g = [[attrs[y * 32 + x] for x in range(32)] for y in range(32)]
    mt = attrs_to_metatile_grid(g, cave=True)
    # West warp to Route 207 (4, 8)
    open_path(mt, [(x, y) for x in range(2, 7) for y in range(6, 11)], CAVE_FLOOR)
    # East warp to Route 208 (27, 20)
    open_path(mt, [(x, y) for x in range(24, 30) for y in range(17, 23)], CAVE_FLOOR)
    # Main tunnel corridor
    open_path(mt, [(x, y) for x in range(4, 28) for y in range(8, 22)], CAVE_FLOOR)
    # Block northern 2F passage (25, 3) with walls/rocks for later
    for x in range(22, 29):
        for y in range(1, 6):
            mt[y][x] = CAVE_WALL
    # Cyrus area (15, 17) and trigger (14, 23)
    open_path(mt, [(x, y) for x in range(12, 18) for y in range(15, 25)], CAVE_FLOOR)
    write_layout("MtCoronet_1F_South", 32, 32, "gTileset_General", "gTileset_Cave", pack(mt))

    # --- Route 208: 64x32 from MAP_055|056 ---
    r208_ids = [[55, 56]]
    g = stitch_chunks(r208_ids)
    mt = attrs_to_metatile_grid(g)
    # West Mt. Coronet warp (~8, 20)
    open_path(mt, [(x, y) for x in range(5, 12) for y in range(17, 23)])
    mt[20][8] = MT_CAVE_ENTRANCE
    # Berry Master house door (~57, 12)
    stamp_building(mt, 57, 12, "house")
    open_path(mt, [(57, 12), (56, 12), (58, 12), (57, 13)])
    # East Hearthome gate (~63, 22-23)
    open_path(mt, [(x, y) for x in range(60, 64) for y in range(20, 26)])
    stamp_building(mt, 62, 22, "gate")
    open_path(mt, [(62, 22), (61, 22), (63, 22), (62, 23)])
    # Main path
    open_path(mt, [(x, y) for x in range(8, 63) for y in range(18, 24)])
    write_layout("Route208", 64, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # Reinforce Eterna City south exit into cycling road gate warps (16-17, 57)
    eterna = LAYOUTS / "EternaCity" / "map.bin"
    w, h = 64, 64
    data = bytearray(eterna.read_bytes())

    def set_(x, y, mt_):
        struct.pack_into("<H", data, (y * w + x) * 2, mt_)

    for y in range(55, 60):
        for x in range(15, 19):
            set_(x, y, MT_GRASS)
    eterna.write_bytes(data)
    print("Reinforced EternaCity south exit for Cycling Road gate")

    # Reinforce Oreburgh north slope into Route 207 (x 41-46, y 0-2)
    ore = LAYOUTS / "OreburghCity" / "map.bin"
    w, h = 64, 64
    data = bytearray(ore.read_bytes())

    def seto(x, y, mt_):
        struct.pack_into("<H", data, (y * w + x) * 2, mt_)

    for y in range(0, 3):
        for x in range(40, 48):
            seto(x, y, MT_GRASS)
    ore.write_bytes(data)
    print("Reinforced OreburghCity north exit into Route 207")


if __name__ == "__main__":
    main()
