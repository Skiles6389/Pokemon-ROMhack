#!/usr/bin/env python3
"""
Generate M14 Sinnoh outdoor/indoor layouts from pret/pokeplatinum land-data
collision/behaviour tables, using Emerald metatiles only (M11/M13 approach).

Land IDs from TownsAndRoutes matrix (groups.json):
  Route 205 South (col 6): MAP_037 (N) + MAP_035 (mid) + MAP_034 (S) → 32x96
  Valley Windworks Outside (col 7,row 20): MAP_036 → 32x32
  Valley Windworks Building: MAP_305 → cropped indoor

No DS graphics are copied.
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

MT_GRASS = 0x001
MT_TALL_GRASS = 0x00D
MT_SAND = 0x121
MT_WATER = 0x170
MT_TREE_TL, MT_TREE_TR = 0x1D4, 0x1D5
MT_TREE_BL, MT_TREE_BR = 0x1DC, 0x1DD
MT_ROCK = 0x079
MT_LEDGE_DOWN = 0x0D5
MT_LEDGE_DOWN2 = 0x0D6

# Indoor (Facility secondary, 0x200+)
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
    for x, y in points:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = mt
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                    if grid[ny][nx] in (MT_TREE_TL, MT_TREE_TR, MT_TREE_BL, MT_TREE_BR, IN_WALL):
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
    elif kind == "windworks":
        # Larger industrial facade using Emerald building / facility-looking metatiles
        facade = [
            [0x210, 0x211, 0x211, 0x211, 0x211, 0x211, 0x212],
            [0x218, 0x219, 0x219, 0x219, 0x219, 0x219, 0x21A],
            [0x218, 0x219, 0x230, 0x231, 0x230, 0x219, 0x21A],
            [0x222, 0x232, 0x238, 0x248, 0x238, 0x240, 0x221],
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


def write_layout(name: str, width: int, height: int, primary: str, secondary: str, blockdata: bytes):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blockdata)
    border_src = LAYOUTS / ("AquaHideout_1F" if "Facility" in secondary else "Route203") / "border.bin"
    if not border_src.exists():
        border_src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(border_src.read_bytes())

    layouts = json.loads(LAYOUTS_JSON.read_text())
    # Convert CamelCase_Name to LAYOUT_CAMEL_CASE_NAME
    import re
    layout_id = "LAYOUT_" + re.sub(r'(?<!^)(?=[A-Z])', '_', name).upper().replace("__", "_")
    layouts["layouts"] = [L for L in layouts["layouts"] if L.get("id") != layout_id and L.get("id") != "LAYOUT_" + name.upper()]
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


def main():
    if not PLAT_DATA.exists():
        print("Missing pokeplatinum ref at", PLAT_DATA, file=sys.stderr)
        sys.exit(1)

    # --- Route 205 South: lands 37 (N) + 35 (mid) + 34 (S), world origin (192,576) ---
    chunks = [37, 35, 34]
    g = []
    for lid in chunks:
        a = load_attrs(lid)
        for y in range(32):
            g.append([a[y * 32 + x] for x in range(32)])
    mt = attrs_to_metatile_grid(g)

    # West connection to Floaroma (world z 656-660 → local y 80-84)
    open_path(mt, [(0, y) for y in range(80, 85)])
    # East connection to Valley Windworks (southern chunk, around bridge y ~78-82)
    open_path(mt, [(31, y) for y in range(76, 85)])
    # Rest house door (214,594) → local (22,18)
    open_path(mt, [(22, 18), (21, 18), (23, 18), (22, 19)])
    stamp_building(mt, 22, 18, "house")
    # Eterna Forest north warps (206-207,581) → local (14-15,5)
    open_path(mt, [(14, 5), (15, 5), (14, 6), (15, 6), (14, 4), (15, 4)])
    # Girl / bridge approach (211,661) → local (19,85)
    open_path(mt, [(19, 85), (18, 85), (20, 85), (19, 84), (17, 85), (21, 85)])

    write_layout("Route205_South", 32, 96, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Valley Windworks Outside: land 36, world (224,640) ---
    a36 = load_attrs(36)
    g = [[a36[y * 32 + x] for x in range(32)] for y in range(32)]
    mt = attrs_to_metatile_grid(g)
    # West connection back to Route 205
    open_path(mt, [(0, y) for y in range(12, 22)])
    # Door at (243,654) → local (19,14)
    open_path(mt, [(19, 14), (18, 14), (20, 14), (19, 15), (19, 13)])
    stamp_building(mt, 19, 14, "windworks")
    write_layout("ValleyWindworks_Exterior", 32, 32, "gTileset_General", "gTileset_Petalburg", pack(mt))

    # --- Valley Windworks Interior: land 305, crop used 24x18 ---
    a305 = load_attrs(305)
    g = [[a305[y * 32 + x] for x in range(24)] for y in range(18)]
    mt = attrs_to_metatile_grid(g, indoor=True)
    # Entrance warp at Platinum (12,16) — keep walkable
    open_path(mt, [(12, 16), (11, 16), (13, 16), (12, 15)], IN_FLOOR)
    mt[16][12] = IN_DOOR
    # Clear path to Mars area (~20,7) and generator hall
    open_path(mt, [(x, y) for x in range(10, 22) for y in range(6, 16)], IN_FLOOR)
    open_path(mt, [(x, y) for x in range(2, 14) for y in range(2, 15)], IN_FLOOR)
    write_layout("ValleyWindworks_Interior", 24, 18, "gTileset_General", "gTileset_Facility", pack(mt))

    # Open Floaroma east edge toward Route 205 (already opened in M13 gen; reinforce)
    flo_path = LAYOUTS / "FloaromaTown" / "map.bin"
    w, h = 32, 64
    data = bytearray(flo_path.read_bytes())

    def set_(x, y, mt_):
        struct.pack_into("<H", data, (y * w + x) * 2, mt_)

    for y in range(48, 53):
        set_(30, y, MT_GRASS)
        set_(31, y, MT_GRASS)
    flo_path.write_bytes(data)
    print("Reinforced Floaroma eastern exit at x=30-31, y=48-52")


if __name__ == "__main__":
    main()
