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

# Fenced flower garden from LittlerootTown fence ring (rows 13–15)
# Top/sides use real fence posts; interior = tall-grass flowers (0x00D), not roof tiles
GARDEN_FENCED = {
    "name": "fenced_flower_garden",
    "source": "LittlerootTown",
    "door_mt": None,
    "door_dx": 0,
    "door_dy": 0,
    "tiles": [
        [0x214, 0x215, 0x215, 0x215, 0x216],
        [0x214, 0x00D, 0x00D, 0x00D, 0x216],
        [0x21E, 0x00D, 0x00D, 0x00D, 0x21F],
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
