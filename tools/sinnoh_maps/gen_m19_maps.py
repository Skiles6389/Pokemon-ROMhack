#!/usr/bin/env python3
"""
Generate M19 Sinnoh layouts from pret/pokeplatinum land-data collision tables,
using Emerald metatiles only (same approach as M13–M18).

Land IDs (TownsAndRoutes matrix):
  Veilstone City (2x2): MAP_077|078 / MAP_079|080   origin c21,r18

Interiors (Emerald Building / Facility footprints inspired by Platinum):
  Veilstone Gym (Fighting hall) — custom
  Team Galactic Warehouse front room — from MAP_254 cropped
  Dept Store floors reuse Lilycove layouts (no new blockdata)

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
MT_CRATER = 0x079  # rock stand-in for meteorite craters

IN_FLOOR = 0x201
IN_WALL = 0x21A
IN_DOOR = 0x20E
IN_STAIRS = 0x20F
IN_COUNTER = 0x219
IN_BAG = 0x218  # punching-bag / barrier accent

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
    elif kind == "dept":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x230, 0x231, 0x230, 0x219, 0x21A],
            [0x218, 0x219, 0x238, 0x248, 0x238, 0x219, 0x21A],
            [0x222, 0x232, 0x240, 0x248, 0x240, 0x240, 0x221],
        ]
        door_dx = 3
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
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x219, 0x219, 0x21A],
            [0x218, 0x230, 0x231, 0x230, 0x231, 0x21A],
            [0x222, 0x232, 0x240, 0x238, 0x240, 0x221],
        ]
        door_dx = 2
    elif kind == "warehouse":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x219, 0x21A],
            [0x222, 0x232, 0x230, 0x240, 0x221],
        ]
        door_dx = 2
    elif kind == "gamecorner":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x230, 0x231, 0x230, 0x231, 0x21A],
            [0x222, 0x232, 0x238, 0x248, 0x240, 0x221],
        ]
        door_dx = 2
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


def crop_indoor(land_id: int, width: int, height: int) -> list[list[int]]:
    attrs = load_attrs(land_id)
    return [[attrs[y * 32 + x] for x in range(width)] for y in range(height)]


def make_fighting_gym(width: int = 24, height: int = 32) -> list[list[int]]:
    """Platinum-inspired Fighting gym: central hall with side punching-bag rooms."""
    g = [[IN_WALL for _ in range(width)] for _ in range(height)]
    # Main corridor up the middle
    for y in range(2, height - 1):
        for x in range(10, 14):
            g[y][x] = IN_FLOOR
    # Entrance lobby
    for y in range(height - 6, height - 1):
        for x in range(6, 18):
            g[y][x] = IN_FLOOR
    # Side training rooms with bag accents
    for room_y in (8, 14, 20):
        for y in range(room_y, room_y + 4):
            for x in range(2, 8):
                g[y][x] = IN_FLOOR
            for x in range(16, 22):
                g[y][x] = IN_FLOOR
        g[room_y + 1][8] = IN_FLOOR
        g[room_y + 2][8] = IN_FLOOR
        g[room_y + 1][15] = IN_FLOOR
        g[room_y + 2][15] = IN_FLOOR
        g[room_y][4] = IN_BAG
        g[room_y][18] = IN_BAG
        # barrier / door accents between rooms
        g[room_y + 3][9] = IN_COUNTER
        g[room_y + 3][14] = IN_COUNTER
    # Leader dais
    for y in range(2, 7):
        for x in range(8, 16):
            g[y][x] = IN_FLOOR
    g[height - 1][11] = IN_DOOR
    g[height - 1][12] = IN_DOOR
    return g


def make_warehouse(width: int = 16, height: int = 14) -> list[list[int]]:
    """Open front room; locked deeper door on north wall."""
    g = [[IN_WALL for _ in range(width)] for _ in range(height)]
    for y in range(2, height - 1):
        for x in range(1, width - 1):
            g[y][x] = IN_FLOOR
    # Locked deeper door (north)
    g[2][7] = IN_DOOR
    g[2][8] = IN_DOOR
    # South exit to city
    g[height - 1][7] = IN_DOOR
    g[height - 1][8] = IN_DOOR
    # Counter / crates accents
    g[4][3] = IN_COUNTER
    g[4][12] = IN_COUNTER
    return g


def main():
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        sys.exit(1)

    # --- Veilstone City: 64x64 from MAP_077|078 / MAP_079|080 ---
    # World origin c21,r18 → local = world - (672, 576)
    city_ids = [
        [77, 78],
        [79, 80],
    ]
    g = stitch_chunks(city_ids)
    mt = attrs_to_metatile_grid(g)

    # Streets / plazas (sand) before stamping buildings
    open_path(mt, [(x, y) for x in range(4, 50) for y in range(20, 24)], MT_SAND)  # west approach
    open_path(mt, [(x, y) for x in range(10, 50) for y in range(33, 38)], MT_SAND)  # mid street
    open_path(mt, [(x, y) for x in range(16, 48) for y in range(45, 50)], MT_SAND)  # south row
    open_path(mt, [(x, y) for x in range(26, 34) for y in range(14, 36)], MT_SAND)  # N-S spine
    open_path(mt, [(x, y) for x in range(40, 50) for y in range(58, 64)], MT_SAND)  # Route 214 approach
    open_path(mt, [(x, y) for x in range(4, 10) for y in range(20, 26)], MT_SAND)  # Route 215 gate

    # Meteorite crater plaza (east) — rock rings matching Platinum crater landmarks
    for cx, cy in ((57, 40), (58, 53), (60, 52)):
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = cx + dx, cy + dy
                if 0 <= y < 64 and 0 <= x < 64:
                    if abs(dx) == 2 or abs(dy) == 2:
                        mt[y][x] = MT_CRATER
                    else:
                        mt[y][x] = MT_SAND

    # Building doors (local coords from Platinum global events)
    doors = [
        (6, 22, "gate"),       # Route 215 west gate
        (12, 35, "gym"),       # Gym
        (29, 27, "dept"),      # Department Store
        (29, 15, "warehouse"), # Galactic Warehouse
        (34, 47, "gamecorner"),
        (44, 47, "house"),     # Prize Exchange
        (18, 47, "house"),     # SW Massage House
        (24, 47, "house"),     # SE House
        (39, 26, "house"),     # NW House
        (45, 26, "house"),     # NE House (Porygon)
        (45, 35, "center"),    # Pokémon Center
        (46, 62, "gate"),      # Route 214 south gate
        (42, 13, "galactic"),  # Galactic HQ exterior (locked)
    ]
    for dx, dy, kind in doors:
        stamp_building(mt, dx, dy, kind)
        open_path(mt, [(dx, dy), (dx, dy + 1)], MT_SAND)

    # Extra HQ doors
    for dx in (45, 48):
        stamp_building(mt, dx, 13, "galactic")
        open_path(mt, [(dx, 13), (dx, 14)], MT_SAND)

    write_layout("VeilstoneCity", 64, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Veilstone Gym ---
    gym = make_fighting_gym(24, 32)
    write_layout("VeilstoneCity_Gym", 24, 32, "gTileset_Building", "gTileset_RustboroGym", pack(gym))

    # --- Galactic Warehouse (front room) ---
    # Prefer Platinum MAP_254 collision if usable; fall back to custom room.
    try:
        wh_attrs = crop_indoor(254, 16, 14)
        wh = attrs_to_metatile_grid(wh_attrs, indoor=True)
        open_path(wh, [(x, y) for x in range(1, 15) for y in range(2, 13)], IN_FLOOR)
        wh[13][7] = IN_DOOR
        wh[13][8] = IN_DOOR
        wh[2][7] = IN_DOOR
        wh[2][8] = IN_DOOR
    except Exception:
        wh = make_warehouse(16, 14)
    write_layout(
        "VeilstoneCity_GalacticWarehouse",
        16,
        14,
        "gTileset_General",
        "gTileset_Facility",
        pack(wh),
    )

    print("M19 layouts done.")


if __name__ == "__main__":
    main()
