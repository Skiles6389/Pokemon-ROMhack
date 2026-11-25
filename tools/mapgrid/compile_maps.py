#!/usr/bin/env python3
"""Compile maps_src/*.grid → data/layouts/<Map>/map.bin + map.json event updates.

Deterministic. Generated bins/json are committed; `make` does not invoke this.
Run via `make mapgrid` or `python3 tools/mapgrid/compile_maps.py`.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.emerald_building_stamps import (  # noqa: E402
    ALL_STAMPS,
    HOUSE_PETALBURG_A,
    HOUSE_PETALBURG_B,
    HOUSE_PETALBURG_WIDE,
)
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    MT_GRASS,
    MT_LEDGE_A,
    MT_LEDGE_B,
    MT_PATH_C,
    MT_ROCK,
    MT_SAND,
    MT_TALL,
    MT_TREE,
    MT_TREE_BL,
    MT_TREE_BR,
    MT_TREE_TL,
    MT_TREE_TR,
    MT_WATER,
    path_metatile_for_neighbors,
)

STAMP_BY_NAME = {s["name"].upper().replace("-", "_"): s for s in ALL_STAMPS}
STAMP_BY_NAME.update(
    {
        "HOUSE_PETALBURG_A": HOUSE_PETALBURG_A,
        "HOUSE_PETALBURG_B": HOUSE_PETALBURG_B,
        "HOUSE_PETALBURG_WIDE": HOUSE_PETALBURG_WIDE,
        "HOUSE1": HOUSE_PETALBURG_WIDE,
        "HOUSE2": HOUSE_PETALBURG_A,
        "HOUSE3": HOUSE_PETALBURG_B,
        "HOUSE_A": HOUSE_PETALBURG_A,
        "HOUSE_B": HOUSE_PETALBURG_B,
        "HOUSE_WIDE": HOUSE_PETALBURG_WIDE,
        "PLAYER_HOUSE": HOUSE_PETALBURG_WIDE,
        "RIVAL_HOUSE": HOUSE_PETALBURG_B,
    }
)

LEGEND_PATH = Path(__file__).with_name("legend.json")
MT_FLOWER = 0x004
MT_SIGN = 0x003
MT_FENCE = 0x215  # Petalburg secondary rail
MT_VOID = 0x000


def cell(mt: int, coll: int, elev: int = 3) -> int:
    return (mt & 0x3FF) | ((coll & 3) << 10) | ((elev & 0xF) << 12)


def pack_grid(grid: list[list[int]]) -> bytes:
    buf = bytearray()
    for row in grid:
        for v in row:
            buf += struct.pack("<H", v)
    return bytes(buf)


class GridFile:
    def __init__(self) -> None:
        self.name = ""
        self.layout_id = ""
        self.width = 0
        self.height = 0
        self.primary = "gTileset_General"
        self.secondary = "gTileset_Petalburg"
        self.connections: list[dict] = []
        self.stamps: list[dict] = []  # {char, stamp, dest_map, dest_warp}
        self.signs: list[dict] = []  # {script} in encounter order of S
        self.warps: list[dict] = []  # {dest_map, dest_warp_id} in encounter order of W
        self.rows: list[str] = []


def parse_grid(path: Path) -> GridFile:
    gf = GridFile()
    lines = path.read_text().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("@"):
            parts = line[1:].split()
            key = parts[0].lower()
            if key == "name":
                gf.name = parts[1]
            elif key == "layout":
                gf.layout_id = parts[1]
            elif key == "width":
                gf.width = int(parts[1])
            elif key == "height":
                gf.height = int(parts[1])
            elif key == "primary":
                gf.primary = parts[1]
            elif key == "secondary":
                gf.secondary = parts[1]
            elif key == "connection":
                # @connection <dir> <MAP_ID> <offset>
                gf.connections.append(
                    {"direction": parts[1], "map": parts[2], "offset": int(parts[3])}
                )
            elif key == "stamp":
                # @stamp <char> <STAMP_NAME> <DEST_MAP> <dest_warp_id>
                gf.stamps.append(
                    {
                        "char": parts[1],
                        "stamp": parts[2],
                        "dest_map": parts[3],
                        "dest_warp_id": parts[4],
                    }
                )
            elif key == "sign":
                # @sign <script>  (applied to S chars in row-major order)
                gf.signs.append({"script": parts[1]})
            elif key == "warp":
                # @warp <DEST_MAP> <dest_warp_id>
                gf.warps.append({"dest_map": parts[1], "dest_warp_id": parts[2]})
            elif key == "grid":
                i += 1
                break
            i += 1
            continue
        if line.strip() == "" or line.startswith("#"):
            i += 1
            continue
        # Implicit start of grid if no @grid
        break
    # Remaining non-empty non-# lines are grid rows
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith("#") or line.startswith("@"):
            continue
        if line.strip() == "":
            if gf.rows:
                break
            continue
        # Strip trailing CR; keep spaces as grass
        gf.rows.append(line.rstrip("\n").rstrip("\r"))
    if not gf.name:
        gf.name = path.stem
    if not gf.layout_id:
        gf.layout_id = f"LAYOUT_{gf.name.upper()}"
    if not gf.width:
        gf.width = max(len(r) for r in gf.rows)
    if not gf.height:
        gf.height = len(gf.rows)
    # Pad rows
    padded = []
    for r in gf.rows:
        if len(r) < gf.width:
            r = r + "." * (gf.width - len(r))
        elif len(r) > gf.width:
            r = r[: gf.width]
        padded.append(r)
    while len(padded) < gf.height:
        padded.append("." * gf.width)
    gf.rows = padded[: gf.height]
    return gf


def compile_char_grid(gf: GridFile) -> tuple[list[list[int]], dict]:
    """Return (cell_grid, meta_events)."""
    w, h = gf.width, gf.height
    chars = [list(r) for r in gf.rows]
    grid = [[cell(MT_GRASS, 0) for _ in range(w)] for _ in range(h)]
    walk = [[False] * w for _ in range(h)]

    stamp_chars = {s["char"] for s in gf.stamps}

    # Pass 1: base terrain (ignore stamp anchors as grass for now)
    for y in range(h):
        for x in range(w):
            ch = chars[y][x]
            if ch in stamp_chars:
                grid[y][x] = cell(MT_GRASS, 0)
                walk[y][x] = True
                continue
            if ch == "T":
                grid[y][x] = cell(MT_ROCK, 1)  # placeholder; trees stamped next
                walk[y][x] = False
            elif ch == ".":
                grid[y][x] = cell(MT_GRASS, 0)
                walk[y][x] = True
            elif ch == ",":
                grid[y][x] = cell(MT_TALL, 0)
                walk[y][x] = True
            elif ch == "=":
                grid[y][x] = cell(MT_PATH_C, 0)
                walk[y][x] = True
            elif ch == "~":
                grid[y][x] = cell(MT_WATER, 0, 1)
                walk[y][x] = False
            elif ch == "L":
                grid[y][x] = cell(MT_LEDGE_A if (x & 1) == 0 else MT_LEDGE_B, 1, 0)
                walk[y][x] = False
            elif ch == "F":
                grid[y][x] = cell(MT_FENCE, 1)
                walk[y][x] = False
            elif ch == "f":
                grid[y][x] = cell(MT_FLOWER, 0)
                walk[y][x] = True
            elif ch == "S":
                grid[y][x] = cell(MT_SIGN, 1)
                walk[y][x] = False
            elif ch == "R" or ch == "#":
                grid[y][x] = cell(MT_ROCK, 1)
                walk[y][x] = False
            elif ch == "_":
                grid[y][x] = cell(MT_GRASS, 0)
                walk[y][x] = True
            elif ch == ":":
                grid[y][x] = cell(MT_SAND, 0)
                walk[y][x] = True
            elif ch == "W":
                grid[y][x] = cell(MT_GRASS, 0)
                walk[y][x] = True
            elif ch == " ":
                grid[y][x] = cell(MT_GRASS, 0)
                walk[y][x] = True
            else:
                # Unknown → grass (stamp letters already handled)
                grid[y][x] = cell(MT_GRASS, 0)
                walk[y][x] = True

    # Pass 2: tree 2×2 autotile on even alignments where all 4 are T
    tree_mask = [[chars[y][x] == "T" for x in range(w)] for y in range(h)]
    covered = [[False] * w for _ in range(h)]
    for y in range(0, h - 1, 2):
        for x in range(0, w - 1, 2):
            if (
                tree_mask[y][x]
                and tree_mask[y][x + 1]
                and tree_mask[y + 1][x]
                and tree_mask[y + 1][x + 1]
            ):
                grid[y][x] = cell(MT_TREE_TL, 1)
                grid[y][x + 1] = cell(MT_TREE_TR, 1)
                grid[y + 1][x] = cell(MT_TREE_BL, 1)
                grid[y + 1][x + 1] = cell(MT_TREE_BR, 1)
                for dy in (0, 1):
                    for dx in (0, 1):
                        covered[y + dy][x + dx] = True
                        walk[y + dy][x + dx] = False
    # Orphan T → rock (no fragment trees)
    orphans = 0
    for y in range(h):
        for x in range(w):
            if tree_mask[y][x] and not covered[y][x]:
                grid[y][x] = cell(MT_ROCK, 1)
                walk[y][x] = False
                orphans += 1

    # Pass 3: path autotile
    def is_path(x: int, y: int) -> bool:
        if not (0 <= x < w and 0 <= y < h):
            return False
        return chars[y][x] == "="

    for y in range(h):
        for x in range(w):
            if chars[y][x] != "=":
                continue
            n = is_path(x, y - 1)
            s = is_path(x, y + 1)
            ww = is_path(x - 1, y)
            e = is_path(x + 1, y)
            mt = path_metatile_for_neighbors(n, s, ww, e)
            grid[y][x] = cell(mt, 0)
            walk[y][x] = True

    # Pass 4: place building stamps (door on anchor)
    warp_events: list[dict] = []
    for spec in gf.stamps:
        ch = spec["char"]
        sname = spec["stamp"].upper().replace("-", "_")
        stamp = STAMP_BY_NAME.get(sname)
        if not stamp:
            raise SystemExit(f"{gf.name}: unknown stamp {spec['stamp']}")
        # Find all anchors
        anchors = [(x, y) for y in range(h) for x in range(w) if chars[y][x] == ch]
        if not anchors:
            raise SystemExit(f"{gf.name}: stamp anchor '{ch}' not found in grid")
        for ax, ay in anchors:
            dx, dy = stamp["door_dx"], stamp["door_dy"]
            tlx, tly = ax - dx, ay - dy
            tiles = stamp["tiles"]
            th, tw = len(tiles), len(tiles[0])
            if tlx < 0 or tly < 0 or tlx + tw > w or tly + th > h:
                raise SystemExit(
                    f"{gf.name}: stamp {sname} at door ({ax},{ay}) OOB "
                    f"(tl={tlx},{tly} size={tw}x{th} map={w}x{h})"
                )
            for sy in range(th):
                for sx in range(tw):
                    mt = tiles[sy][sx]
                    # Door metatile coll=1; others coll=1 for building body
                    coll = 1
                    elev = 0 if mt == stamp.get("door_mt") else 3
                    grid[tly + sy][tlx + sx] = cell(mt, coll, elev)
                    walk[tly + sy][tlx + sx] = mt == stamp.get("door_mt")
            warp_events.append(
                {
                    "x": ax,
                    "y": ay,
                    "elevation": 0,
                    "dest_map": spec["dest_map"],
                    "dest_warp_id": str(spec["dest_warp_id"]),
                }
            )

    # Pass 5: W warps (in row-major order)
    w_idx = 0
    for y in range(h):
        for x in range(w):
            if chars[y][x] != "W":
                continue
            if w_idx >= len(gf.warps):
                raise SystemExit(f"{gf.name}: more W tiles than @warp lines")
            dest = gf.warps[w_idx]
            w_idx += 1
            grid[y][x] = cell(MT_GRASS, 0)
            walk[y][x] = True
            warp_events.append(
                {
                    "x": x,
                    "y": y,
                    "elevation": 0,
                    "dest_map": dest["dest_map"],
                    "dest_warp_id": str(dest["dest_warp_id"]),
                }
            )
    if w_idx != len(gf.warps):
        raise SystemExit(
            f"{gf.name}: {len(gf.warps)} @warp lines but only {w_idx} W tiles"
        )

    # Pass 6: signs
    bg_events: list[dict] = []
    s_idx = 0
    for y in range(h):
        for x in range(w):
            if chars[y][x] != "S":
                continue
            script = (
                gf.signs[s_idx]["script"]
                if s_idx < len(gf.signs)
                else f"{gf.name}_EventScript_Sign"
            )
            s_idx += 1
            bg_events.append(
                {
                    "type": "sign",
                    "x": x,
                    "y": y,
                    "elevation": 0,
                    "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                    "script": script,
                }
            )

    meta = {
        "warp_events": warp_events,
        "bg_events": bg_events,
        "walk": walk,
        "orphans": orphans,
        "chars": chars,
    }
    return grid, meta


def validate(
    gf: GridFile, grid: list[list[int]], meta: dict
) -> list[str]:
    fails: list[str] = []
    w, h = gf.width, gf.height
    walk = meta["walk"]

    # No void metatiles
    for y in range(h):
        for x in range(w):
            mt = grid[y][x] & 0x3FF
            if mt == MT_VOID:
                fails.append(f"void metatile at ({x},{y})")

    # Flood fill from connection openings + warps
    seeds: list[tuple[int, int]] = []
    for ev in meta["warp_events"]:
        seeds.append((int(ev["x"]), int(ev["y"])))
    # Connection edge openings: walkable cells on that edge
    for conn in gf.connections:
        d = conn["direction"]
        if d == "left":
            seeds += [(0, y) for y in range(h) if walk[y][0]]
        elif d == "right":
            seeds += [(w - 1, y) for y in range(h) if walk[y][w - 1]]
        elif d == "up":
            seeds += [(x, 0) for x in range(w) if walk[0][x]]
        elif d == "down":
            seeds += [(x, h - 1) for x in range(w) if walk[h - 1][x]]

    if not seeds:
        fails.append("no entrance seeds (warps/connections)")
        return fails

    seen = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()
    for x, y in seeds:
        if 0 <= x < w and 0 <= y < h and walk[y][x] and not seen[y][x]:
            seen[y][x] = True
            q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and walk[ny][nx] and not seen[ny][nx]:
                seen[ny][nx] = True
                q.append((nx, ny))

    unreachable = 0
    for y in range(h):
        for x in range(w):
            if walk[y][x] and not seen[y][x]:
                unreachable += 1
    if unreachable:
        fails.append(f"{unreachable} walkable cells unreachable from entrances")

    # Warps must be walkable
    for ev in meta["warp_events"]:
        x, y = int(ev["x"]), int(ev["y"])
        if not walk[y][x]:
            fails.append(f"warp ({x},{y}) not walkable")

    # Orphan T cells are converted to rock (solid, no half-tree fragments).
    # Count is informational only — odd carved edges are expected.

    return fails


def write_outputs(gf: GridFile, grid: list[list[int]], meta: dict) -> None:
    layout_dir = REPO / "data" / "layouts" / gf.name
    layout_dir.mkdir(parents=True, exist_ok=True)
    map_bin = layout_dir / "map.bin"
    map_bin.write_bytes(pack_grid(grid))
    # border.bin — 2x2 grass if missing
    border = layout_dir / "border.bin"
    if not border.exists():
        border.write_bytes(struct.pack("<HHHH", *[cell(MT_GRASS, 0)] * 4))

    # layouts.json
    layouts_path = REPO / "data" / "layouts" / "layouts.json"
    layouts = json.loads(layouts_path.read_text())
    found = False
    for L in layouts["layouts"]:
        if L["id"] == gf.layout_id or L["name"] == f"{gf.name}_Layout":
            L["width"] = gf.width
            L["height"] = gf.height
            L["primary_tileset"] = gf.primary
            L["secondary_tileset"] = gf.secondary
            L["blockdata_filepath"] = f"data/layouts/{gf.name}/map.bin"
            L["border_filepath"] = f"data/layouts/{gf.name}/border.bin"
            found = True
            break
    if not found:
        layouts["layouts"].append(
            {
                "id": gf.layout_id,
                "name": f"{gf.name}_Layout",
                "width": gf.width,
                "height": gf.height,
                "primary_tileset": gf.primary,
                "secondary_tileset": gf.secondary,
                "border_filepath": f"data/layouts/{gf.name}/border.bin",
                "blockdata_filepath": f"data/layouts/{gf.name}/map.bin",
                "layout_version": "emerald",
            }
        )
    layouts_path.write_text(json.dumps(layouts, indent=2) + "\n")

    # layouts.inc width/height
    inc = REPO / "data" / "layouts" / "layouts.inc"
    if inc.exists():
        text = inc.read_text()
        # Replace `.4byte W` / `.4byte H` under MapName_Layout::
        pat = re.compile(
            rf"({gf.name}_Layout::\n\t\.4byte )\d+(\n\t\.4byte )\d+",
            re.M,
        )
        text2, n = pat.subn(rf"\g<1>{gf.width}\g<2>{gf.height}", text)
        if n:
            inc.write_text(text2)

    # map.json — preserve object_events; replace warps/bg/connections
    mj_path = REPO / "data" / "maps" / gf.name / "map.json"
    if mj_path.exists():
        mj = json.loads(mj_path.read_text())
    else:
        mj = {
            "id": f"MAP_{gf.name.upper()}",
            "name": gf.name,
            "layout": gf.layout_id,
            "music": "MUS_PL_ROUTE201",
            "region_map_section": "MAPSEC_LITTLEROOT_TOWN",
            "requires_flash": False,
            "weather": "WEATHER_SUNNY",
            "map_type": "MAP_TYPE_TOWN",
            "allow_cycling": True,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "object_events": [],
            "coord_events": [],
        }
    mj["layout"] = gf.layout_id
    if gf.connections:
        mj["connections"] = [
            {"map": c["map"], "offset": c["offset"], "direction": c["direction"]}
            for c in gf.connections
        ]
    mj["warp_events"] = meta["warp_events"]
    # Merge signs: keep non-generated signs? Replace all bg signs from grid
    other_bg = [e for e in (mj.get("bg_events") or []) if e.get("type") != "sign"]
    mj["bg_events"] = other_bg + meta["bg_events"]
    mj_path.parent.mkdir(parents=True, exist_ok=True)
    mj_path.write_text(json.dumps(mj, indent=2) + "\n")


def compile_one(path: Path, *, check_only: bool = False) -> int:
    if "@compiler platinum" in path.read_text():
        from tools.mapgrid import platinum_compiler

        return platinum_compiler.compile_one(path, check_only)
    gf = parse_grid(path)
    grid, meta = compile_char_grid(gf)
    fails = validate(gf, grid, meta)
    if fails:
        print(f"FAIL {gf.name}:")
        for f in fails:
            print(" -", f)
        return 1
    if check_only:
        print(f"OK {gf.name} (check-only)")
        return 0
    write_outputs(gf, grid, meta)
    print(
        f"OK {gf.name} {gf.width}x{gf.height} "
        f"warps={len(meta['warp_events'])} signs={len(meta['bg_events'])} "
        f"orphans={meta['orphans']}"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "grids",
        nargs="*",
        type=Path,
        help="Grid files (default: maps_src/*.grid)",
    )
    ap.add_argument("--check", action="store_true", help="Validate only")
    args = ap.parse_args()
    grids = args.grids or sorted((REPO / "maps_src").glob("*.grid"))
    if not grids:
        print("No .grid files found", file=sys.stderr)
        return 1
    rc = 0
    for g in grids:
        rc |= compile_one(g, check_only=args.check)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
