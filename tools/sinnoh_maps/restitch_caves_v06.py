#!/usr/bin/env python3
"""
Re-stitch cave layouts from pret/pokeplatinum land-data and clear erroneous
Emerald tree/rock solids on Platinum-walkable outdoor LAND_TABLE tiles.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAYOUTS = REPO / "data" / "layouts"
PLAT_DATA = Path("/tmp/pokeplatinum-ref/res/field/mapmodels/data")

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from post_m20_qa_audit import LAND_TABLE, load_attrs, load_layout_meta, plat_collision  # noqa: E402

CAVE_LAYOUTS = (
    "OreburghGate_1F",
    "OreburghGate_B1F",
    "OreburghMine_B1F",
    "OreburghMine_B2F",
    "MtCoronet_1F_South",
)

MT_GRASS = 0x001
MT_TALL_GRASS = 0x00D
MT_WATER = 0x170
MT_IN_FLOOR = 0x201
MT_IN_WALL = 0x21A
MT_LEDGE_A = 0x0D5
MT_LEDGE_B = 0x0D6

TREE_MT = {0x1D4, 0x1D5, 0x1DC, 0x1DD}
ROCK_MT = {0x079}
CLEAR_SOLID_MT = TREE_MT | ROCK_MT

BEH_TALL = {0x02, 0x03}
BEH_LEDGE = {0x38, 0x39, 0x3A, 0x3B}

WALKABLE_OVERRIDE = {MT_GRASS, MT_TALL_GRASS, MT_WATER, 0x121, MT_IN_FLOOR, MT_LEDGE_A, MT_LEDGE_B}


def is_water_beh(beh: int) -> bool:
    return beh in (0x10, 0x15) or 0x11 <= beh <= 0x17


def stitch_attr_grid(chunks: list[list[int | None]]) -> list[list[int]]:
    """Stitch Platinum land attrs; None chunks default to blocked (collision set)."""
    rows, cols = len(chunks), len(chunks[0])
    w, h = cols * 32, rows * 32
    default_blocked = 0x8000
    grid = [[default_blocked for _ in range(w)] for _ in range(h)]
    for cy, row in enumerate(chunks):
        for cx, land_id in enumerate(row):
            if land_id is None:
                continue
            path = PLAT_DATA / f"map_data_{land_id:03d}.bin"
            if not path.exists():
                raise FileNotFoundError(path)
            attrs = load_attrs(land_id)
            for ly in range(32):
                for lx in range(32):
                    grid[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return grid


def attr_to_cave_mt(v: int, x: int, y: int) -> int:
    col = plat_collision(v)
    beh = v & 0xFF
    if col:
        return MT_IN_WALL
    if is_water_beh(beh):
        return MT_WATER
    if beh in BEH_TALL:
        return MT_TALL_GRASS
    if beh in BEH_LEDGE:
        return MT_LEDGE_A if (x & 1) == 0 else MT_LEDGE_B
    return MT_IN_FLOOR


def load_map_grid(path: Path, width: int, height: int) -> list[list[int]]:
    data = path.read_bytes()
    grid: list[list[int]] = []
    for y in range(height):
        row: list[int] = []
        for x in range(width):
            mt = struct.unpack_from("<H", data, (y * width + x) * 2)[0] & 0x3FF
            row.append(mt)
        grid.append(row)
    return grid


def pack_grid(grid: list[list[int]]) -> bytes:
    h, w = len(grid), len(grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            struct.pack_into("<H", out, (y * w + x) * 2, grid[y][x] & 0x3FF)
    return bytes(out)


def emerald_blocks_walk(mt: int) -> bool:
    if mt in WALKABLE_OVERRIDE:
        return False
    if mt in CLEAR_SOLID_MT or mt == MT_IN_WALL:
        return True
    return False


def count_walk_blocked(attr_grid: list[list[int]], mt_grid: list[list[int]]) -> int:
    h = min(len(attr_grid), len(mt_grid))
    w = min(len(attr_grid[0]), len(mt_grid[0]))
    n = 0
    for y in range(h):
        for x in range(w):
            if plat_collision(attr_grid[y][x]) == 0 and emerald_blocks_walk(mt_grid[y][x]):
                n += 1
    return n


def crop_attr_grid(attr_grid: list[list[int]], width: int, height: int) -> list[list[int]]:
    return [row[:width] for row in attr_grid[:height]]


def clear_outdoor_solids(
    layout_name: str, attr_grid: list[list[int]], mt_grid: list[list[int]]
) -> tuple[list[list[int]], int]:
    """Return updated grid and count of tiles changed."""
    h, w = len(mt_grid), len(mt_grid[0])
    changed = 0
    for y in range(h):
        for x in range(w):
            if y >= len(attr_grid) or x >= len(attr_grid[0]):
                continue
            v = attr_grid[y][x]
            if plat_collision(v) != 0:
                continue
            mt = mt_grid[y][x]
            if mt not in CLEAR_SOLID_MT:
                continue
            beh = v & 0xFF
            new = MT_WATER if is_water_beh(beh) else MT_GRASS
            if new != mt:
                mt_grid[y][x] = new
                changed += 1
    return mt_grid, changed


def main() -> int:
    if not PLAT_DATA.is_dir():
        print(f"Missing platinum ref: {PLAT_DATA}", file=sys.stderr)
        return 1

    meta = load_layout_meta()
    files_changed: list[str] = []
    cave_reports: list[dict] = []

    for name in CAVE_LAYOUTS:
        chunks = LAND_TABLE.get(name)
        if not chunks:
            print(f"SKIP {name}: not in LAND_TABLE")
            continue
        L = meta.get(name)
        if not L:
            print(f"SKIP {name}: missing layouts.json entry")
            continue
        w, h = int(L["width"]), int(L["height"])
        map_bin = LAYOUTS / name / "map.bin"
        if not map_bin.exists():
            print(f"SKIP {name}: no map.bin")
            continue

        attr_full = stitch_attr_grid(chunks)
        attr = crop_attr_grid(attr_full, w, h)
        before_grid = load_map_grid(map_bin, w, h)
        before_wb = count_walk_blocked(attr, before_grid)

        mt_grid = [[attr_to_cave_mt(attr[y][x], x, y) for x in range(w)] for y in range(h)]
        after_wb = count_walk_blocked(attr, mt_grid)

        map_bin.write_bytes(pack_grid(mt_grid))
        files_changed.append(str(map_bin.relative_to(REPO)))
        cave_reports.append(
            {
                "layout": name,
                "walk_blocked_before": before_wb,
                "walk_blocked_after": after_wb,
                "size": f"{w}x{h}",
            }
        )
        print(
            f"{name}: walk_blocked {before_wb} -> {after_wb} "
            f"(size {w}x{h}, wrote {map_bin.name})"
        )

    outdoor_summary: list[dict] = []
    for name, chunks in sorted(LAND_TABLE.items()):
        if name in CAVE_LAYOUTS:
            continue
        L = meta.get(name)
        if not L:
            continue
        w, h = int(L["width"]), int(L["height"])
        map_bin = LAYOUTS / name / "map.bin"
        if not map_bin.exists():
            continue

        attr_full = stitch_attr_grid(chunks)
        attr = crop_attr_grid(attr_full, w, h)
        grid = load_map_grid(map_bin, w, h)
        before_wb = count_walk_blocked(attr, grid)
        grid, nfix = clear_outdoor_solids(name, attr, grid)
        after_wb = count_walk_blocked(attr, grid)

        if nfix > 0:
            map_bin.write_bytes(pack_grid(grid))
            files_changed.append(str(map_bin.relative_to(REPO)))
            outdoor_summary.append(
                {
                    "layout": name,
                    "tiles_cleared": nfix,
                    "walk_blocked_before": before_wb,
                    "walk_blocked_after": after_wb,
                }
            )
            print(
                f"{name} (outdoor): cleared {nfix} solids, "
                f"walk_blocked {before_wb} -> {after_wb}"
            )

    print("\n=== Summary ===")
    print(f"Files changed: {len(files_changed)}")
    for p in files_changed:
        print(f"  {p}")
    print("\nCave walk_blocked:")
    for r in cave_reports:
        print(
            f"  {r['layout']}: {r['walk_blocked_before']} -> {r['walk_blocked_after']} "
            f"({r['size']})"
        )
    if outdoor_summary:
        print(f"\nOutdoor maps with solid clears: {len(outdoor_summary)}")
        for r in outdoor_summary:
            print(
                f"  {r['layout']}: {r['tiles_cleared']} tiles, "
                f"walk_blocked {r['walk_blocked_before']} -> {r['walk_blocked_after']}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())