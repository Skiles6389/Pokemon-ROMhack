#!/usr/bin/env python3
"""Complete Emerald building stamps lifted from stock layouts (Porymap-accurate).

Each stamp is a contiguous rectangular block of metatile IDs with door_dx/door_dy
relative to the top-left of the stamp. Door warps must land on the door metatile.
"""
from __future__ import annotations

# --- Petalburg / Littleroot houses (gTileset_Petalburg) ---
# From LittlerootTown map.bin doors (5,8) and (14,8). No grass row under door.
HOUSE_PETALBURG_A = {
    "name": "littleroot_house_a",
    "source": "LittlerootTown",
    "door_mt": 0x248,
    "door_dx": 3,
    "door_dy": 4,
    "tiles": [
        [0x208, 0x209, 0x209, 0x209, 0x20A],
        [0x210, 0x211, 0x211, 0x211, 0x212],
        [0x218, 0x219, 0x219, 0x219, 0x21A],
        [0x222, 0x232, 0x230, 0x240, 0x221],
        [0x22A, 0x23A, 0x238, 0x248, 0x229],
    ],
}
HOUSE_PETALBURG_B = {
    "name": "littleroot_house_b",
    "source": "LittlerootTown",
    "door_mt": 0x248,
    "door_dx": 1,
    "door_dy": 4,
    "tiles": [
        [0x208, 0x209, 0x209, 0x209, 0x20A],
        [0x210, 0x211, 0x211, 0x211, 0x212],
        [0x218, 0x219, 0x219, 0x219, 0x21A],
        [0x220, 0x240, 0x231, 0x232, 0x223],
        [0x228, 0x248, 0x239, 0x23A, 0x22B],
    ],
}
# Wider player/rival house (extra mid column, still full roof ridge)
HOUSE_PETALBURG_WIDE = {
    "name": "littleroot_house_wide",
    "source": "LittlerootTown+wide",
    "door_mt": 0x248,
    "door_dx": 3,
    "door_dy": 4,
    "tiles": [
        [0x208, 0x209, 0x209, 0x209, 0x209, 0x20A],
        [0x210, 0x211, 0x211, 0x211, 0x211, 0x212],
        [0x218, 0x219, 0x219, 0x219, 0x219, 0x21A],
        [0x222, 0x232, 0x230, 0x240, 0x230, 0x221],
        [0x22A, 0x23A, 0x238, 0x248, 0x238, 0x229],
    ],
}

# Oldale secondary house (door 0x287) — compact 4×4
HOUSE_OLDALE = {
    "name": "oldale_house",
    "source": "OldaleTown",
    "door_mt": 0x287,
    "door_dx": 1,
    "door_dy": 3,
    "tiles": [
        [0x26C, 0x26D, 0x26D, 0x26E],
        [0x274, 0x275, 0x275, 0x276],
        [0x27C, 0x27F, 0x27D, 0x27E],
        [0x284, 0x287, 0x28F, 0x286],
    ],
}

# --- General tileset PC / Mart (Oldale — complete 4×4) ---
PC_OLDALE = {
    "name": "oldale_pc",
    "source": "OldaleTown",
    "door_mt": 0x061,
    "door_dx": 1,
    "door_dy": 3,
    "tiles": [
        [0x048, 0x049, 0x282, 0x283],
        [0x050, 0x051, 0x052, 0x053],
        [0x058, 0x059, 0x05A, 0x05B],
        [0x060, 0x061, 0x062, 0x063],
    ],
}
MART_OLDALE = {
    "name": "oldale_mart",
    "source": "OldaleTown",
    "door_mt": 0x041,
    "door_dx": 1,
    "door_dy": 3,
    "tiles": [
        [0x028, 0x029, 0x029, 0x285],
        [0x030, 0x031, 0x032, 0x033],
        [0x038, 0x039, 0x03A, 0x03B],
        [0x060, 0x041, 0x042, 0x043],
    ],
}

# --- Rustboro PC / Mart (with roof/sign rows; no surrounding pave) ---
PC_RUSTBORO = {
    "name": "rustboro_pc",
    "source": "RustboroCity",
    "door_mt": 0x061,
    "door_dx": 1,
    "door_dy": 3,
    "tiles": [
        [0x256, 0x25E, 0x25F, 0x257],
        [0x050, 0x051, 0x052, 0x053],
        [0x058, 0x059, 0x05A, 0x05B],
        [0x266, 0x061, 0x062, 0x27E],
    ],
}
MART_RUSTBORO = {
    "name": "rustboro_mart",
    "source": "RustboroCity",
    "door_mt": 0x041,
    "door_dx": 1,
    "door_dy": 3,
    "tiles": [
        [0x325, 0x267, 0x267, 0x326],
        [0x030, 0x031, 0x032, 0x033],
        [0x038, 0x039, 0x03A, 0x03B],
        [0x266, 0x041, 0x042, 0x27F],
    ],
}

# Rustboro flat / school-style (door 0x22F) — complete incl. right edge 223/22B
# From RustboroCity door (9,38)
HOUSE_RUSTBORO = {
    "name": "rustboro_house",
    "source": "RustboroCity",
    "door_mt": 0x22F,
    "door_dx": 2,
    "door_dy": 4,
    "tiles": [
        [0x220, 0x221, 0x221, 0x222, 0x223],
        [0x228, 0x229, 0x229, 0x22A, 0x22B],
        [0x230, 0x231, 0x231, 0x231, 0x233],
        [0x238, 0x23A, 0x227, 0x23A, 0x23B],
        [0x240, 0x241, 0x22F, 0x241, 0x243],
    ],
}
# Mid civic from RustboroCity door (27,34) — 7×5 complete
CIVIC_RUSTBORO = {
    "name": "rustboro_civic",
    "source": "RustboroCity",
    "door_mt": 0x22F,
    "door_dx": 3,
    "door_dy": 4,
    "tiles": [
        [0x220, 0x221, 0x221, 0x221, 0x221, 0x222, 0x223],
        [0x228, 0x229, 0x229, 0x229, 0x229, 0x22A, 0x22B],
        [0x230, 0x231, 0x231, 0x231, 0x231, 0x231, 0x233],
        [0x238, 0x23A, 0x23A, 0x227, 0x23A, 0x23A, 0x23B],
        [0x240, 0x241, 0x241, 0x22F, 0x241, 0x241, 0x243],
    ],
}
# Wide civic from RustboroCity door (13,30) — 9×6 complete (school/TV scale)
CIVIC_RUSTBORO_WIDE = {
    "name": "rustboro_civic_wide",
    "source": "RustboroCity",
    "door_mt": 0x22F,
    "door_dx": 4,
    "door_dy": 5,
    "tiles": [
        [0x220, 0x221, 0x221, 0x221, 0x221, 0x221, 0x221, 0x222, 0x223],
        [0x228, 0x229, 0x229, 0x229, 0x229, 0x229, 0x229, 0x22A, 0x22B],
        [0x230, 0x231, 0x231, 0x231, 0x231, 0x231, 0x231, 0x231, 0x233],
        [0x238, 0x23A, 0x239, 0x23A, 0x239, 0x23A, 0x239, 0x23A, 0x23B],
        [0x238, 0x23A, 0x239, 0x239, 0x227, 0x239, 0x239, 0x23A, 0x23B],
        [0x240, 0x241, 0x241, 0x241, 0x22F, 0x241, 0x241, 0x241, 0x243],
    ],
}

# Gym facade from MauvilleCity (general tileset, door 0x1CD) — complete 6×5
GYM_MAUVILLE = {
    "name": "mauville_gym",
    "source": "MauvilleCity",
    "door_mt": 0x1CD,
    "door_dx": 3,
    "door_dy": 4,
    "tiles": [
        [0x1AA, 0x1AB, 0x1AB, 0x1AB, 0x1AB, 0x1AC],
        [0x1B2, 0x1B3, 0x1B3, 0x1B3, 0x1B3, 0x1B4],
        [0x1B8, 0x1B9, 0x1BA, 0x1B3, 0x1BB, 0x1BC],
        [0x1C0, 0x1C1, 0x1C2, 0x1C5, 0x1C3, 0x1C4],
        [0x1C8, 0x1C9, 0x1CA, 0x1CD, 0x1CB, 0x1CC],
    ],
}

# Corner garden: signposts as posts + flower beds (0x004) + shrubs on grass.
# Must NOT use Petalburg roof/lab tiles (0x208–0x24B building range) — those read as
# "roof slabs with plants". All IDs here are General-primary (safe on any secondary).
GARDEN_FENCED = {
    "name": "fenced_flower_garden",
    "source": "General_flowers+signs",
    "door_mt": None,
    "door_dx": 0,
    "door_dy": 0,
    "tiles": [
        [0x003, 0x004, 0x004, 0x004, 0x003],
        [0x004, 0x00D, 0x001, 0x00D, 0x004],
        [0x004, 0x00D, 0x00E, 0x00D, 0x004],
        [0x003, 0x004, 0x004, 0x004, 0x003],
    ],
}

# --- General / Mauville houses used by the Platinum-shape maps (maps_src) ---
# General red-roof house (General primary; door 0x021). 4x4 and a 5x5 tall-roof
# variant (roof mid row doubled) for Platinum's 5x5 footprints.
GENERAL_HOUSE_4 = {
    "name": "general_house_4",
    "source": "General primary (Petalburg-style house)",
    "door_mt": 0x021,
    "door_dx": 1,
    "door_dy": 3,
    "tiles": [
        [0x008, 0x009, 0x009, 0x00A],
        [0x010, 0x011, 0x011, 0x012],
        [0x018, 0x019, 0x00B, 0x01A],
        [0x020, 0x021, 0x013, 0x022],
    ],
}
GENERAL_HOUSE_5T = {
    "name": "general_house_5t",
    "source": "General primary (Petalburg-style house, tall roof)",
    "door_mt": 0x021,
    "door_dx": 1,
    "door_dy": 4,
    "tiles": [
        [0x008, 0x009, 0x009, 0x009, 0x00A],
        [0x010, 0x011, 0x011, 0x011, 0x012],
        [0x010, 0x011, 0x011, 0x011, 0x012],
        [0x018, 0x019, 0x00B, 0x00B, 0x01A],
        [0x020, 0x021, 0x013, 0x013, 0x022],
    ],
}
# Mauville pink-roof house (gTileset_Mauville; door 0x2AC) — from MauvilleCity.
MAUVILLE_HOUSE_4 = {
    "name": "mauville_house_4",
    "source": "MauvilleCity",
    "door_mt": 0x2AC,
    "door_dx": 1,
    "door_dy": 3,
    "tiles": [
        [0x283, 0x284, 0x284, 0x285],
        [0x28B, 0x28C, 0x28C, 0x28D],
        [0x293, 0x2A4, 0x26F, 0x295],
        [0x29B, 0x2AC, 0x277, 0x29D],
    ],
}
MAUVILLE_HOUSE_5T = {
    "name": "mauville_house_5t",
    "source": "MauvilleCity (5-wide house, roof stripe row doubled)",
    "door_mt": 0x2AC,
    "door_dx": 1,
    "door_dy": 4,
    "tiles": [
        [0x283, 0x284, 0x284, 0x284, 0x285],
        [0x28B, 0x28C, 0x28C, 0x28C, 0x28D],
        [0x28B, 0x28C, 0x28C, 0x28C, 0x28D],
        [0x2A0, 0x2A4, 0x2A1, 0x2A3, 0x2A2],
        [0x2A8, 0x2AC, 0x2A9, 0x2AB, 0x2AA],
    ],
}
# Verdanturf green-roof house (gTileset_Mauville; door 0x3A1) — from VerdanturfTown.
VERDANTURF_HOUSE_4 = {
    "name": "verdanturf_house_4",
    "source": "VerdanturfTown",
    "door_mt": 0x3A1,
    "door_dx": 1,
    "door_dy": 3,
    "tiles": [
        [0x388, 0x389, 0x389, 0x38A],
        [0x390, 0x391, 0x391, 0x392],
        [0x398, 0x399, 0x38B, 0x38C],
        [0x3A0, 0x3A1, 0x393, 0x394],
    ],
}


# Birch's lab (LittlerootTown door (7,16), Petalburg secondary) re-ordered to an
# 8-wide facade with the door third from the left, matching Sandgem's Platinum
# lab footprint (door 2 tiles in from the west wall). Columns: west wall, door
# bay (3), plain wall bay, chimney bay (2), east wall.
BIRCH_LAB_W8 = {
    "name": "birch_lab_w8",
    "source": "LittlerootTown(reordered)",
    "door_mt": 0x249,
    "door_dx": 2,
    "door_dy": 4,
    "tiles": [
        [0x20C, 0x20D, 0x20D, 0x20D, 0x20D, 0x242, 0x243, 0x20E],
        [0x214, 0x215, 0x215, 0x215, 0x215, 0x24A, 0x24B, 0x216],
        [0x214, 0x215, 0x215, 0x215, 0x215, 0x215, 0x215, 0x216],
        [0x21E, 0x22C, 0x241, 0x22D, 0x20F, 0x20F, 0x20F, 0x21F],
        [0x226, 0x234, 0x249, 0x235, 0x217, 0x217, 0x217, 0x227],
    ],
}

DOOR_MAT = 0x201
MAILBOX = 0x003

# Kind → preferred stamp for city remediations
STAMPS_BY_KIND = {
    "center": PC_RUSTBORO,
    "mart": MART_RUSTBORO,
    "house": HOUSE_RUSTBORO,
    "house_petalburg": HOUSE_PETALBURG_A,
    "house_petalburg_wide": HOUSE_PETALBURG_WIDE,
    "house_oldale": HOUSE_OLDALE,
    "civic": CIVIC_RUSTBORO,
    "civic_wide": CIVIC_RUSTBORO_WIDE,
    "gym": GYM_MAUVILLE,
    "garden": GARDEN_FENCED,
    "pc_oldale": PC_OLDALE,
    "mart_oldale": MART_OLDALE,
}

ALL_STAMPS = [
    HOUSE_PETALBURG_A, HOUSE_PETALBURG_B, HOUSE_PETALBURG_WIDE, HOUSE_OLDALE,
    PC_OLDALE, MART_OLDALE, PC_RUSTBORO, MART_RUSTBORO,
    HOUSE_RUSTBORO, CIVIC_RUSTBORO, CIVIC_RUSTBORO_WIDE, GYM_MAUVILLE, GARDEN_FENCED,
    GENERAL_HOUSE_4, GENERAL_HOUSE_5T, MAUVILLE_HOUSE_4, MAUVILLE_HOUSE_5T, VERDANTURF_HOUSE_4,
    BIRCH_LAB_W8,
]


def stamp_at(grid, door_x: int, door_y: int, stamp: dict, *, fill_mat: bool = True) -> tuple[int, int]:
    """Place stamp so door metatile lands on (door_x, door_y). Returns top-left."""
    tiles = stamp["tiles"]
    dx, dy = stamp["door_dx"], stamp["door_dy"]
    left, top = door_x - dx, door_y - dy
    h, w = len(grid), len(grid[0])
    for row_i, row in enumerate(tiles):
        for col_i, mt in enumerate(row):
            x, y = left + col_i, top + row_i
            if 0 <= x < w and 0 <= y < h:
                grid[y][x] = mt
    if fill_mat and stamp.get("door_mt") and door_y + 1 < h:
        # Only place mat on grass/path/pave — not water/trees
        under = grid[door_y + 1][door_x]
        if under < 0x200 or under in (0x2BB, 0x2C3):
            grid[door_y + 1][door_x] = DOOR_MAT
    return left, top


def clear_rect(grid, collision, left: int, top: int, sw: int, sh: int, fill: int, coll: int = 0) -> None:
    h, w = len(grid), len(grid[0])
    for y in range(top, top + sh):
        for x in range(left, left + sw):
            if 0 <= x < w and 0 <= y < h:
                grid[y][x] = fill
                if collision is not None:
                    collision[y][x] = coll


def stamp_with_clear(grid, collision, door_x, door_y, stamp, fill: int, pad: int = 1) -> None:
    tiles = stamp["tiles"]
    dx, dy = stamp["door_dx"], stamp["door_dy"]
    left, top = door_x - dx - pad, door_y - dy - pad
    clear_rect(grid, collision, left, top, len(tiles[0]) + pad * 2, len(tiles) + pad * 2 + 1, fill, 0)
    stamp_at(grid, door_x, door_y, stamp)
