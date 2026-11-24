#!/usr/bin/env python3
"""
Generate M13 Sinnoh outdoor map layouts from pret/pokeplatinum land-data
collision/behaviour tables, using Emerald metatiles only (M11 approach).

Reference: pret/pokeplatinum map_data_*.bin terrain attributes
(collision bit 15, behaviour bits 0-7). No DS graphics are copied.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAT_DATA = Path("/tmp/pokeplatinum-ref/res/field/mapmodels/data")
LAYOUTS = REPO / "data" / "layouts"
LAYOUTS_JSON = LAYOUTS / "layouts.json"

# Emerald metatile IDs (primary general + secondary)
MT_GRASS = 0x001
MT_TALL_GRASS = 0x00D
MT_LONG_GRASS = 0x015
MT_SAND = 0x121
MT_WATER = 0x170
MT_CAVE_FLOOR = 0x211  # secondary cave tileset offset 0x200 + 0x11
MT_CAVE_WALL = 0x211  # placeholder; walls use tree/rock below for outdoors

# Tree pair (parity-tiled) — General secondary range used by M11 routes
MT_TREE_TL, MT_TREE_TR = 0x1D4, 0x1D5
MT_TREE_BL, MT_TREE_BR = 0x1DC, 0x1DD

# Petalburg fence for small obstacles
MT_FENCE = 0x170  # not ideal; use rock wall grass base instead
MT_ROCK = 0x079  # General_RockWall_GrassBase

# Ledges
MT_LEDGE_S = 0x03B  # jump south (common emerald)
# Prefer known Route203 ledge tiles from existing map: 0x0D5/0x0D6 style —
# Route203 used 0x0D5? Inspect showed 0x0D5 not in top; used 213/214 = 0x0D5/0x0D6
MT_LEDGE_DOWN = 0x0D5
MT_LEDGE_DOWN2 = 0x0D6

# Cave secondary tileset metatiles (0x200+)
CAVE_FLOOR = 0x211
CAVE_DARK = 0x201
CAVE_WALL = 0x221
CAVE_ENTRANCE = 0x20A  # dark opening used in Oreburgh Gate

# Tile behaviors (Platinum)
BEH_NONE = 0x00
BEH_TALL_GRASS = 0x02
BEH_VERY_TALL_GRASS = 0x03
BEH_CAVE_FLOOR = 0x08
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
        # Blocked: trees with 2x2 parity, else rock
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
        return MT_ROCK  # approximate other ledges as rock edge
    return MT_GRASS


def attr_to_cave(v: int, x: int, y: int) -> int:
    col = (v >> 15) & 1
    beh = v & 0xFF
    if col:
        return CAVE_WALL
    if beh in (BEH_WATER_RIVER, BEH_WATER_SEA):
        return MT_WATER
    return CAVE_FLOOR


def stitch(chunks: list[tuple[int, int, int]], width_chunks: int, height_chunks: int) -> list[list[int]]:
    """chunks: list of (land_id, chunk_x, chunk_y)."""
    w, h = width_chunks * 32, height_chunks * 32
    grid = [[MT_GRASS for _ in range(w)] for _ in range(h)]
    by_pos = {(cx, cy): lid for lid, cx, cy in chunks}
    for cy in range(height_chunks):
        for cx in range(width_chunks):
            lid = by_pos.get((cx, cy))
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    grid[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return grid


def convert_grid(attr_grid: list[list[int]], cave: bool = False) -> bytes:
    h = len(attr_grid)
    w = len(attr_grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            v = attr_grid[y][x]
            mt = attr_to_cave(v, x, y) if cave else attr_to_outdoor(v, x, y)
            # map.bin stores metatile id in low 10 bits; elevation/collision in engine via behavior
            struct.pack_into("<H", out, (y * w + x) * 2, mt)
    return bytes(out)


def write_layout(name: str, width: int, height: int, primary: str, secondary: str, blockdata: bytes):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blockdata)
    # Copy a sensible border from a similar existing layout
    border_src = LAYOUTS / ("OreburghGate_1F" if "Cave" in secondary or secondary.endswith("Cave") else "Route203") / "border.bin"
    if not border_src.exists():
        border_src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(border_src.read_bytes())

    layouts = json.loads(LAYOUTS_JSON.read_text())
    layout_id = "LAYOUT_" + name.upper()
    # Remove existing entry with same id
    layouts["layouts"] = [L for L in layouts["layouts"] if L.get("id") != layout_id]
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
    print(f"Wrote {name} {width}x{height} ({len(blockdata)} bytes)")


def open_path(grid: list[list[int]], points: list[tuple[int, int]], mt: int = MT_GRASS):
    """Force walkable tiles at connection/warp points."""
    for x, y in points:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = mt
            # clear neighbor trees so player can pass
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                    if grid[ny][nx] in (MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR, CAVE_WALL):
                        grid[ny][nx] = mt


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


def stamp_building(grid, door_x, door_y, kind="house"):
    """Place an Emerald building so its door lands on (door_x, door_y)."""
    # Exact stamps lifted from Twinleaf/Sandgem (Emerald tiles only).
    if kind == "center":
        # Sandgem Pokémon Center (door at bottom row, second tile = 0x061)
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
    else:
        # Twinleaf / Sandgem house (door 0x248)
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


def main():
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        sys.exit(1)

    # --- Route 204 South: land 21, 32x32, origin world (160,704) ---
    a21 = load_attrs(21)
    g = [[a21[y * 32 + x] for x in range(32)] for y in range(32)]
    mt = attrs_to_metatile_grid(g)
    # Jubilife connection along south; cave warp near (11,1)
    open_path(mt, [(x, 31) for x in range(12, 16)] + [(x, 31) for x in range(22, 24)])
    open_path(mt, [(11, 1), (12, 1), (10, 1), (11, 2)])
    # Cave entrance visual
    mt[0][11] = 0x09F  # cave entrance top
    mt[1][11] = 0x0A7  # cave entrance bottom
    write_layout("Route204_South", 32, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Route 204 North: land 31, 32x32, origin (160,672) ---
    a31 = load_attrs(31)
    g = [[a31[y * 32 + x] for x in range(32)] for y in range(32)]
    mt = attrs_to_metatile_grid(g)
    # Floaroma to the north — open north edge path
    open_path(mt, [(x, 0) for x in range(14, 18)])
    # Ravaged Path warp around (20,26)
    open_path(mt, [(20, 26), (19, 26), (20, 25)])
    mt[25][20] = 0x09F
    mt[26][20] = 0x0A7
    write_layout("Route204_North", 32, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Ravaged Path: 435 (N) + 374 (S), 32x64 cave ---
    aN, aS = load_attrs(435), load_attrs(374)
    g = []
    for y in range(32):
        g.append([aN[y * 32 + x] for x in range(32)])
    for y in range(32):
        g.append([aS[y * 32 + x] for x in range(32)])
    mt = attrs_to_metatile_grid(g, cave=True)
    open_path(mt, [(19, 50), (19, 51), (18, 50), (20, 50)], CAVE_FLOOR)
    open_path(mt, [(28, 44), (27, 44), (28, 43), (28, 45)], CAVE_FLOOR)
    # Mark exits
    mt[50][19] = CAVE_ENTRANCE
    mt[44][28] = CAVE_ENTRANCE
    write_layout("RavagedPath", 32, 64, "gTileset_General", "gTileset_Cave", pack(mt))

    # --- Floaroma Town: land 29 (south 32) + land 25-ish north; use 29+31 pattern ---
    # Floaroma is 32x64 at (160,608). South chunk (y32-63) = land 29 works for buildings.
    # North chunk: find neighbor north of 29
    a29 = load_attrs(29)
    # Prefer land 25 as north flower fields (open + grass) — verify meadow warps
    aN = load_attrs(25)
    g = []
    for y in range(32):
        g.append([aN[y * 32 + x] for x in range(32)])
    for y in range(32):
        g.append([a29[y * 32 + x] for x in range(32)])
    mt = attrs_to_metatile_grid(g)
    # Building doors (local to origin 160,608):
    # PC (16,58), Mart (24,49), Flower shop (20,43), SE house (24,58), Mid house (11,46)
    stamp_building(mt, 16, 58, "center")
    stamp_building(mt, 24, 49, "mart")
    stamp_building(mt, 20, 43, "shop")
    stamp_building(mt, 24, 58, "house")
    stamp_building(mt, 11, 46, "house")
    # Connections
    open_path(mt, [(x, 63) for x in range(14, 18)])  # south to R204N
    open_path(mt, [(20, 4), (21, 4), (20, 5), (21, 5)])  # north meadow
    open_path(mt, [(2, 33), (3, 33)])  # west meadow entrance
    open_path(mt, [(31, y) for y in range(48, 52)])  # east gate to Route 205 (M14)
    write_layout("FloaromaTown", 32, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Floaroma Meadow: approximate 64x64 from collision of a grassy cave-like outdoor ---
    # Build from empty grass + tree borders using event bounds; use land 90 style if possible
    # Create a 64x64 meadow with open interior and tree walls
    W, H = 64, 64
    mt = [[MT_GRASS for _ in range(W)] for _ in range(H)]
    for y in range(H):
        for x in range(W):
            edge = x < 2 or x >= W - 2 or y < 2 or y >= H - 2
            # flower patches as tall grass islands
            flower = ((x // 4 + y // 5) % 3 == 0) and 8 <= x < 56 and 8 <= y < 56
            if edge:
                mt[y][x] = MT_TREE_TL if (x + y) % 2 == 0 else MT_TREE_TR
            elif flower:
                mt[y][x] = MT_TALL_GRASS
    # Clear paths for warps/events
    open_path(mt, [(50, 9), (51, 9), (50, 10), (51, 10)])  # to Floaroma NE
    open_path(mt, [(12, 54), (13, 54), (12, 53), (13, 53)])  # to Floaroma west gate
    open_path(mt, [(12, 46), (13, 46), (12, 47), (13, 47), (12, 48), (13, 48)])  # grunt area
    open_path(mt, [(39, 45)])  # meadow house door
    stamp_building(mt, 39, 45, "house")
    write_layout("FloaromaMeadow", 64, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # Open Jubilife north exit toward Route 204 South (eastern half, local x 32-63)
    jub_path = LAYOUTS / "JubilifeCity" / "map.bin"
    w, h = 64, 64
    data = bytearray(jub_path.read_bytes())

    def get(x, y):
        return struct.unpack_from("<H", data, (y * w + x) * 2)[0]

    def set_(x, y, mt_):
        struct.pack_into("<H", data, (y * w + x) * 2, mt_)

    # North edge of Jubilife NE (x 32-63, y 0) — carve path at x 44-47 (world 172-175 ~ R204S opening)
    for x in range(44, 48):
        for y in range(0, 3):
            set_(x, y, MT_GRASS)
    jub_path.write_bytes(data)
    print("Opened Jubilife northern exit at x=44-47")


if __name__ == "__main__":
    main()
