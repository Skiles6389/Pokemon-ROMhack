#!/usr/bin/env python3
"""
Generate M17 Sinnoh layouts from pret/pokeplatinum land-data collision tables,
using Emerald metatiles only (same approach as M13–M16).

Land IDs:
  Hearthome City (2x2): MAP_057|058 / MAP_059|060
  Hearthome Gym: custom Ghost-torch hall (Emerald Building + RustboroGym tiles)

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

IN_FLOOR = 0x201
IN_WALL = 0x21A
IN_DOOR = 0x20E
IN_TORCH = 0x219  # lit wall stand-in inside gym tileset secondary range

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
            struct.pack_into("<H", out, (y * w + x) * 2, grid[y][x] & 0x3FF)
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
    elif kind == "contest":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x230, 0x231, 0x230, 0x219, 0x21A],
            [0x218, 0x219, 0x238, 0x248, 0x238, 0x219, 0x21A],
            [0x222, 0x232, 0x240, 0x248, 0x240, 0x240, 0x221],
        ]
        door_dx = 3
    elif kind == "gate":
        facade = [
            [0x210, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x21A],
            [0x222, 0x230, 0x240, 0x221],
        ]
        door_dx = 1
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
                        grid[cy * 32 + ly][cx * 32 + lx] = 0x8000
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    grid[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return grid


def make_ghost_gym(width: int = 20, height: int = 30) -> list[list[int]]:
    """Platinum-inspired torch-room Ghost gym as a single Emerald layout."""
    g = [[IN_WALL for _ in range(width)] for _ in range(height)]
    # Main corridor up the middle
    for y in range(2, height - 1):
        for x in range(8, 12):
            g[y][x] = IN_FLOOR
    # Entrance lobby
    for y in range(height - 6, height - 1):
        for x in range(5, 15):
            g[y][x] = IN_FLOOR
    # Side torch rooms (room-choice flavor)
    for room_y in (8, 14, 20):
        for y in range(room_y, room_y + 4):
            for x in range(2, 7):
                g[y][x] = IN_FLOOR
            for x in range(13, 18):
                g[y][x] = IN_FLOOR
        # openings into corridor
        g[room_y + 1][7] = IN_FLOOR
        g[room_y + 2][7] = IN_FLOOR
        g[room_y + 1][12] = IN_FLOOR
        g[room_y + 2][12] = IN_FLOOR
        # torch wall accents
        g[room_y][3] = IN_TORCH
        g[room_y][15] = IN_TORCH
    # Leader dais
    for y in range(2, 6):
        for x in range(6, 14):
            g[y][x] = IN_FLOOR
    g[height - 1][9] = IN_DOOR
    g[height - 1][10] = IN_DOOR
    return g


def main():
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        sys.exit(1)

    # --- Hearthome City: 64x64 from MAP_057|058 / MAP_059|060 ---
    city_ids = [
        [57, 58],
        [59, 60],
    ]
    g = stitch_chunks(city_ids)
    mt = attrs_to_metatile_grid(g)

    # Clear plazas / approaches first (sand paths for readable town streets),
    # then stamp buildings so facades stay intact.
    open_path(mt, [(x, y) for x in range(14, 52) for y in range(24, 28)], MT_SAND)
    open_path(mt, [(x, y) for x in range(10, 48) for y in range(36, 41)], MT_SAND)
    open_path(mt, [(x, y) for x in range(28, 36) for y in range(18, 40)], MT_SAND)
    open_path(mt, [(x, y) for x in range(4, 10) for y in range(52, 58)], MT_SAND)
    open_path(mt, [(x, y) for x in range(54, 62) for y in range(52, 58)], MT_SAND)
    open_path(mt, [(x, y) for x in range(8, 14) for y in range(55, 62)], MT_SAND)
    open_path(mt, [(x, y) for x in range(8, 14) for y in range(9, 14)], MT_SAND)
    open_path(mt, [(x, y) for x in range(50, 56) for y in range(9, 14)], MT_SAND)

    # Building doors (local coords converted from Platinum global events)
    doors = [
        (17, 25, "center"),
        (22, 25, "house"),  # Bebe
        (51, 25, "gym"),
        (29, 38, "mart"),
        (40, 38, "house"),  # Fan Club
        (12, 37, "house"),  # Foreign Building
        (24, 38, "house"),  # Poffin House
        (31, 19, "contest"),
        (38, 25, "house"),  # NE condo
        (46, 38, "house"),  # SE house
        (10, 11, "gate"),  # Amity west
        (52, 11, "gate"),  # Amity east
        (6, 54, "gate"),  # Route 208
        (57, 54, "gate"),  # Route 209
        (10, 57, "gate"),  # Route 212
    ]
    for dx, dy, kind in doors:
        stamp_building(mt, dx, dy, kind)
        # Only clear the door tile + south approach so facade walls stay put.
        open_path(mt, [(dx, dy), (dx, dy + 1)], MT_SAND)

    write_layout("HearthomeCity", 64, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Hearthome Gym (custom Ghost torch hall) ---
    gym = make_ghost_gym(20, 30)
    write_layout("HearthomeCity_Gym", 20, 30, "gTileset_Building", "gTileset_RustboroGym", pack(gym))

    print("M17 layouts done.")


if __name__ == "__main__":
    main()
