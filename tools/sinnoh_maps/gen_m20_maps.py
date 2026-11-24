#!/usr/bin/env python3
"""
Generate M20 Sinnoh layouts from pret/pokeplatinum land-data collision tables,
using Emerald metatiles only (same approach as M13–M19).

Land IDs (TownsAndRoutes matrix):
  Route 214 (1x3): MAP_152 / 153 / 154          origin c22,r20
  Valor Lakefront (2x2): MAP_155|156 / 157|158  origin c21,r23
  Route 213 (3x2): MAP_143|144|145 / 146|147|148 origin c20,r25
  Pastoria City (2x2): MAP_081|082 / 083|084    origin c18,r25

Interiors (Emerald Building / Facility footprints inspired by Platinum):
  Pastoria Gym (Water hall with bridge lanes) — custom
  Hotel / restaurant / houses reuse House1 / Motel / Shop layouts

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
IN_COUNTER = 0x219
IN_WATER = 0x170  # outdoor water reused as gym pool accent when tileset allows
# Building secondary (RustboroGym / Facility) water stand-ins
GYM_FLOOR = 0x201
GYM_WALL = 0x21A
GYM_WATER = 0x208  # dark tile used as "deep water" lane
GYM_BRIDGE = 0x201
GYM_SWITCH = 0x218
GYM_DOOR = 0x20E

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
    blocked = (MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR, IN_WALL, MT_ROCK, GYM_WALL, GYM_WATER)
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
    elif kind == "hotel":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x230, 0x231, 0x230, 0x219, 0x21A],
            [0x218, 0x219, 0x238, 0x248, 0x238, 0x219, 0x21A],
            [0x222, 0x232, 0x240, 0x248, 0x240, 0x240, 0x221],
        ]
        door_dx = 3
    elif kind == "restaurant":
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
    elif kind == "cave":
        facade = [
            [0x079, 0x079, 0x079],
            [0x079, 0x20A, 0x079],
        ]
        door_dx = 1
    elif kind == "marsh":
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x230, 0x231, 0x219, 0x21A],
            [0x222, 0x232, 0x238, 0x248, 0x240, 0x221],
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
    border_src = LAYOUTS / ("AquaHideout_1F" if "Facility" in secondary else "Route203") / "border.bin"
    if "Building" in primary or "Gym" in secondary:
        for cand in ("DewfordTown_Gym", "PetalburgCity_Gym", "RustboroCity_Gym", "House1"):
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


def make_water_gym(width: int = 24, height: int = 40) -> list[list[int]]:
    """Platinum-inspired Water gym: multi-level water lanes with bridge corridors."""
    g = [[GYM_WALL for _ in range(width)] for _ in range(height)]
    # Flood most of the hall with "water"
    for y in range(2, height - 2):
        for x in range(1, width - 1):
            g[y][x] = GYM_WATER
    # Central north-south bridge
    for y in range(2, height - 1):
        for x in range(10, 14):
            g[y][x] = GYM_BRIDGE
    # Side platforms / switch pads
    for room_y in (8, 16, 24, 30):
        for y in range(room_y, room_y + 4):
            for x in range(2, 8):
                g[y][x] = GYM_BRIDGE
            for x in range(16, 22):
                g[y][x] = GYM_BRIDGE
        # bridge links
        for x in range(8, 16):
            g[room_y + 1][x] = GYM_BRIDGE
            g[room_y + 2][x] = GYM_BRIDGE
        g[room_y + 1][4] = GYM_SWITCH
        g[room_y + 1][19] = GYM_SWITCH
    # Leader dais
    for y in range(2, 7):
        for x in range(8, 16):
            g[y][x] = GYM_BRIDGE
    # Entrance lobby
    for y in range(height - 6, height - 1):
        for x in range(6, 18):
            g[y][x] = GYM_BRIDGE
    g[height - 1][11] = GYM_DOOR
    g[height - 1][12] = GYM_DOOR
    return g


def make_observatory(width: int = 14, height: int = 12) -> list[list[int]]:
    g = [[IN_WALL for _ in range(width)] for _ in range(height)]
    for y in range(2, height - 1):
        for x in range(1, width - 1):
            g[y][x] = IN_FLOOR
    g[3][3] = IN_COUNTER
    g[3][4] = IN_COUNTER
    g[3][5] = IN_COUNTER
    g[height - 1][6] = IN_DOOR
    g[height - 1][7] = IN_DOOR
    # North door toward marsh (gated)
    g[2][6] = IN_DOOR
    g[2][7] = IN_DOOR
    return g


def main():
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        sys.exit(1)

    # --- Route 214: 32x96 ---
    r214_ids = [[152], [153], [154]]
    g = stitch_chunks(r214_ids)
    mt = attrs_to_metatile_grid(g)
    open_path(mt, [(x, y) for x in range(10, 22) for y in range(0, 8)], MT_SAND)  # north gate approach
    open_path(mt, [(x, y) for x in range(12, 24) for y in range(88, 96)], MT_SAND)  # south to Valor
    open_path(mt, [(x, y) for x in range(8, 28) for y in range(30, 70)], MT_SAND)  # mid corridor
    stamp_building(mt, 14, 5, "gate")
    open_path(mt, [(14, 5), (15, 5), (14, 6), (15, 6)], MT_SAND)
    # Ruin Maniac Cave / Spring Path turnoff (gated for later)
    stamp_building(mt, 9, 30, "cave")
    open_path(mt, [(9, 30), (9, 31), (10, 30)], MT_SAND)
    write_layout("Route214", 32, 96, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Valor Lakefront: 64x64 ---
    valor_ids = [
        [155, 156],
        [157, 158],
    ]
    g = stitch_chunks(valor_ids)
    mt = attrs_to_metatile_grid(g)
    open_path(mt, [(x, y) for x in range(28, 48) for y in range(0, 8)], MT_SAND)  # north from R214
    open_path(mt, [(x, y) for x in range(0, 40) for y in range(56, 64)], MT_SAND)  # SW to R213
    open_path(mt, [(x, y) for x in range(16, 52) for y in range(40, 58)], MT_SAND)  # resort plaza
    open_path(mt, [(x, y) for x in range(40, 52) for y in range(20, 30)], MT_SAND)  # Lake Valor approach
    open_path(mt, [(x, y) for x in range(48, 64) for y in range(48, 58)], MT_SAND)  # east toward R222
    doors = [
        (34, 54, "restaurant"),
        (43, 45, "house"),
        (18, 55, "house"),
        (45, 24, "cave"),  # Lake Valor entrance (gated)
        (40, 40, "hotel"),
    ]
    for dx, dy, kind in doors:
        stamp_building(mt, dx, dy, kind)
        open_path(mt, [(dx, dy), (dx, dy + 1)], MT_SAND)
    write_layout("ValorLakefront", 64, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Route 213: 96x64 coastal ---
    r213_ids = [
        [143, 144, 145],
        [146, 147, 148],
    ]
    g = stitch_chunks(r213_ids)
    mt = attrs_to_metatile_grid(g)
    open_path(mt, [(x, y) for x in range(0, 12) for y in range(8, 18)], MT_SAND)  # west to Pastoria
    open_path(mt, [(x, y) for x in range(28, 64) for y in range(0, 8)], MT_SAND)  # north/NE to Valor
    open_path(mt, [(x, y) for x in range(8, 80) for y in range(20, 40)], MT_SAND)  # beach path
    open_path(mt, [(x, y) for x in range(60, 78) for y in range(8, 22)], MT_SAND)  # hotel area
    doors = [
        (6, 12, "gate"),
        (23, 34, "house"),  # Dr. Footstep
        (66, 18, "hotel"),
        (70, 10, "house"),
        (61, 5, "house"),
        (72, 5, "house"),
    ]
    for dx, dy, kind in doors:
        stamp_building(mt, dx, dy, kind)
        open_path(mt, [(dx, dy), (dx, dy + 1)], MT_SAND)
    write_layout("Route213", 96, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Pastoria City: 64x64 ---
    past_ids = [
        [81, 82],
        [83, 84],
    ]
    g = stitch_chunks(past_ids)
    mt = attrs_to_metatile_grid(g)
    open_path(mt, [(x, y) for x in range(52, 64) for y in range(8, 18)], MT_SAND)  # east to R213
    open_path(mt, [(x, y) for x in range(0, 8) for y in range(40, 52)], MT_SAND)  # west R212 gate
    open_path(mt, [(x, y) for x in range(10, 50) for y in range(14, 48)], MT_SAND)  # town streets
    doors = [
        (13, 27, "gym"),
        (24, 15, "center"),
        (25, 44, "mart"),
        (25, 35, "house"),  # Move Reminder / middle
        (24, 24, "house"),
        (35, 35, "house"),
        (48, 19, "house"),
        (13, 44, "house"),
        (34, 9, "marsh"),  # Great Marsh observatory gate
    ]
    for dx, dy, kind in doors:
        stamp_building(mt, dx, dy, kind)
        open_path(mt, [(dx, dy), (dx, dy + 1)], MT_SAND)
    # West Route 212 gate facade (blocked)
    stamp_building(mt, 2, 46, "gate")
    open_path(mt, [(2, 46), (3, 46)], MT_SAND)
    write_layout("PastoriaCity", 64, 64, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Pastoria Gym ---
    gym = make_water_gym(24, 40)
    write_layout("PastoriaCity_Gym", 24, 40, "gTileset_Building", "gTileset_DewfordGym", pack(gym))

    # --- Great Marsh Observatory Gate 1F ---
    obs = make_observatory(14, 12)
    write_layout(
        "PastoriaCity_GreatMarshGate",
        14,
        12,
        "gTileset_Building",
        "gTileset_Shop",
        pack(obs),
    )

    print("M20 layouts done.")


if __name__ == "__main__":
    main()
