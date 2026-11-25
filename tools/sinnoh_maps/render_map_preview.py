#!/usr/bin/env python3
"""Render a map.bin preview using Emerald tileset PNGs (no ROM dump / DS assets).

Matches Porymap / in-game metatile drawing:
  - Primary metatiles 0..511, secondary metatiles 512.. (local = id - 512)
  - Primary tiles 0..511, secondary tiles 512.. (local = tid - 512)
  - Each metatile = 8 little-endian u16s (16 bytes): bottom TL/TR/BL/BR then top
  - Tile word: bits 0-9 tile, 10 hflip, 11 vflip, 12-15 palette
  - Palettes 0-5 from primary tileset, 6-12 from secondary (NUM_PALS_TOTAL = 13);
    palettes 13-15 are UI/text palettes in-game, so a metatile using one is drawn
    in BAD magenta, as are tile / metatile ids past the loaded tileset
  - Color index 0 is transparent; bottom layer then top layer composite over the
    backdrop (primary palette 0 colour 0), like the GBA
  - render_scene(): what the camera shows in-game, including the strip of each
    connected map drawn with the CURRENT map's tilesets (engine seam fallback:
    undrawable metatiles become the neighbour's border metatile) and the map
    border beyond
"""
from __future__ import annotations

import argparse
import json
import struct
from functools import lru_cache
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]

NUM_TILES_IN_PRIMARY = 512
NUM_METATILES_IN_PRIMARY = 512
NUM_PALS_IN_PRIMARY = 6
NUM_PALS_TOTAL = 13
MAP_OFFSET = 7
BAD = (255, 0, 255, 255)
NUM_TILES_PER_METATILE = 8  # bottom 4 + top 4
TILE_BYTES = NUM_TILES_PER_METATILE * 2  # 16
QUAD_POS = ((0, 0), (8, 0), (0, 8), (8, 8))  # TL, TR, BL, BR


def parse_jasc_pal(path: Path) -> list[tuple[int, int, int, int]]:
    colors = parse_jasc_pal_raw(path)
    # Palette index 0 is always transparent for overworld tiles
    colors[0] = (0, 0, 0, 0)
    return colors


def parse_jasc_pal_raw(path: Path) -> list[tuple[int, int, int, int]]:
    lines = path.read_text().strip().splitlines()
    colors: list[tuple[int, int, int, int]] = []
    for line in lines[3:]:
        parts = line.split()
        if len(parts) >= 3:
            # GBA colours are 5-bit: snap like the hardware / mGBA (c5 << 3 | c5 >> 2)
            colors.append(tuple(((int(v) >> 3) << 3) | (int(v) >> 6) for v in parts[:3]) + (255,))
    while len(colors) < 16:
        colors.append((0, 0, 0, 0))
    return colors


def ts_path(name: str) -> Path:
    short = name.replace("gTileset_", "")
    folder = "".join(("_" + c.lower() if c.isupper() else c) for c in short).lstrip("_")
    for root in (REPO / "data/tilesets/primary", REPO / "data/tilesets/secondary"):
        p = root / folder
        if p.exists():
            return p
    raise FileNotFoundError(name)


def load_one(path: Path) -> dict:
    tiles_img = Image.open(path / "tiles.png")
    if tiles_img.mode != "P":
        tiles_img = tiles_img.convert("P")
    index_data = list(tiles_img.getdata())
    tw = tiles_img.width // 8
    th = tiles_img.height // 8
    pals = []
    pal_dir = path / "palettes"
    for i in range(16):
        pf = pal_dir / f"{i:02d}.pal"
        pals.append(parse_jasc_pal(pf) if pf.exists() else [(0, 0, 0, 0)] * 16)
    backdrop = parse_jasc_pal_raw(pal_dir / "00.pal")[0] if (pal_dir / "00.pal").exists() else (0, 0, 0, 255)
    raw = (path / "metatiles.bin").read_bytes()
    n = len(raw) // TILE_BYTES
    metas: list[list[tuple[int, int, int, int]]] = []
    for i in range(n):
        entries = []
        for j in range(NUM_TILES_PER_METATILE):
            v = struct.unpack_from("<H", raw, i * TILE_BYTES + j * 2)[0]
            tid = v & 0x3FF
            hflip = (v >> 10) & 1
            vflip = (v >> 11) & 1
            pal = (v >> 12) & 0xF
            entries.append((tid, hflip, vflip, pal))
        metas.append(entries)
    return {
        "index": index_data,
        "tw": tw,
        "th": th,
        "width": tiles_img.width,
        "metas": metas,
        "pals": pals,
        "backdrop": backdrop,
        "path": path,
    }


def resolve_tile_sheet(primary: dict, secondary: dict, tid: int) -> tuple[dict, int]:
    if tid < NUM_TILES_IN_PRIMARY:
        return primary, tid
    return secondary, tid - NUM_TILES_IN_PRIMARY


def resolve_palette(
    primary: dict, secondary: dict, pal_idx: int
) -> list[tuple[int, int, int, int]]:
    """VRAM layout: primary owns pals 0-5, secondary owns 6-12; 13-15 are not map palettes."""
    if pal_idx < NUM_PALS_IN_PRIMARY:
        return primary["pals"][pal_idx]
    if pal_idx >= NUM_PALS_TOTAL:
        return [(0, 0, 0, 0)] + [BAD] * 15
    return secondary["pals"][pal_idx]


def get_colored_tile(
    primary: dict,
    secondary: dict,
    tid: int,
    hflip: int,
    vflip: int,
    pal_idx: int,
) -> Image.Image:
    ts, local = resolve_tile_sheet(primary, secondary, tid)
    tw, th, w = ts["tw"], ts["th"], ts["width"]
    max_tid = tw * th
    if local < 0 or local >= max_tid:
        return Image.new("RGBA", (8, 8), BAD)   # uninitialised VRAM in-game
    x0 = (local % tw) * 8
    y0 = (local // tw) * 8
    pal = resolve_palette(primary, secondary, pal_idx)
    pixels = []
    for py in range(8):
        for px in range(8):
            idx = ts["index"][(y0 + py) * w + (x0 + px)] & 0xF
            pixels.append(pal[idx])
    tile = Image.new("RGBA", (8, 8))
    tile.putdata(pixels)
    if hflip:
        tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
    if vflip:
        tile = tile.transpose(Image.FLIP_TOP_BOTTOM)
    return tile


def blit_quad(
    dst: Image.Image,
    primary: dict,
    secondary: dict,
    entries: list[tuple[int, int, int, int]],
) -> None:
    for (tid, hf, vf, pal), (ox, oy) in zip(entries, QUAD_POS):
        tile = get_colored_tile(primary, secondary, tid, hf, vf, pal)
        dst.paste(tile, (ox, oy), tile)


def render_metatile(primary: dict, secondary: dict, mt_id: int) -> Image.Image:
    """Render one 16×16 metatile (bottom then top, color 0 transparent)."""
    if mt_id < NUM_METATILES_IN_PRIMARY:
        ts = primary
        local = mt_id
    else:
        ts = secondary
        local = mt_id - NUM_METATILES_IN_PRIMARY
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    if local < 0 or local >= len(ts["metas"]):
        return Image.new("RGBA", (16, 16), BAD)  # reads past the metatile array in-game
    entries = ts["metas"][local]
    # Bottom layer (tiles 0-3), then top layer (tiles 4-7)
    blit_quad(img, primary, secondary, entries[0:4])
    blit_quad(img, primary, secondary, entries[4:8])
    return img


@lru_cache(maxsize=8)
def load_tilesets(primary_name: str, secondary_name: str) -> tuple[dict, dict]:
    return load_one(ts_path(primary_name)), load_one(ts_path(secondary_name))


def find_layout(layout_name: str) -> dict:
    layouts = json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
    for L in layouts:
        if L["name"] == layout_name or L["name"] == layout_name + "_Layout":
            return L
    for L in layouts:
        if L["name"].startswith(layout_name) or layout_name in L["name"]:
            return L
    raise KeyError(layout_name)


def render(
    layout_name: str,
    out_path: Path,
    cam_x: int = 0,
    cam_y: int = 0,
    view_w: int = 15,
    view_h: int = 10,
    scale: int = 2,
    *,
    bgcolor: tuple[int, int, int, int] | None = None,
) -> Path:
    layout = find_layout(layout_name)
    w, h = int(layout["width"]), int(layout["height"])
    data = (REPO / layout["blockdata_filepath"]).read_bytes()
    primary, secondary = load_tilesets(layout["primary_tileset"], layout["secondary_tileset"])
    if bgcolor is None:
        bgcolor = primary["backdrop"]

    vw = min(view_w, w - cam_x)
    vh = min(view_h, h - cam_y)
    img = Image.new("RGBA", (vw * 16, vh * 16), bgcolor)

    cache: dict[int, Image.Image] = {}
    for ly in range(vh):
        for lx in range(vw):
            mx, my = cam_x + lx, cam_y + ly
            mt = struct.unpack_from("<H", data, (my * w + mx) * 2)[0] & 0x3FF
            tile = cache.get(mt)
            if tile is None:
                tile = render_metatile(primary, secondary, mt)
                cache[mt] = tile
            img.paste(tile, (lx * 16, ly * 16), tile)

    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print("wrote", out_path, img.size)
    return out_path


def _layout_by_id(layout_id: str) -> dict:
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]:
        if L.get("id") == layout_id:
            return L
    raise KeyError(layout_id)


def _map_json(map_name: str) -> dict:
    return json.loads((REPO / "data/maps" / map_name / "map.json").read_text())


def _map_dir_for_const(const: str) -> str:
    for mj in (REPO / "data/maps").glob("*/map.json"):
        d = json.loads(mj.read_text())
        if d.get("id") == const:
            return mj.parent.name
    raise KeyError(const)


def _cells(layout: dict, path_key: str = "blockdata_filepath") -> list[list[int]]:
    w, h = int(layout["width"]), int(layout["height"])
    raw = (REPO / layout[path_key]).read_bytes()
    if path_key == "border_filepath":
        n = len(raw) // 2
        bw = 2 if n == 4 else int(layout.get("border_width", 2))
        return [[struct.unpack_from("<H", raw, (y * bw + x) * 2)[0] & 0x3FF for x in range(bw)] for y in range(n // bw)]
    return [[struct.unpack_from("<H", raw, (y * w + x) * 2)[0] & 0x3FF for x in range(w)] for y in range(h)]


def scene_grid(map_name: str, seam_fallback: bool = True) -> tuple[dict, dict[tuple[int, int], int]]:
    """In-game metatile grid around `map_name` (map coords; may be negative / past the edge).

    Mirrors src/fieldmap.c: the map, then MAP_OFFSET cells of every connected map
    (metatiles the current tilesets cannot draw -> neighbour border metatile when
    `seam_fallback`), border metatiles elsewhere (callers fill those)."""
    mj = _map_json(map_name)
    L = _layout_by_id(mj["layout"])
    w, h = int(L["width"]), int(L["height"])
    cells = {}
    for y, row in enumerate(_cells(L)):
        for x, m in enumerate(row):
            cells[(x, y)] = m
    for conn in mj.get("connections") or []:
        nb = _map_dir_for_const(conn["map"])
        B = _layout_by_id(_map_json(nb)["layout"])
        bw, bh = int(B["width"]), int(B["height"])
        same = B["primary_tileset"] == L["primary_tileset"] and B["secondary_tileset"] == L["secondary_tileset"]
        border = _cells(B, "border_filepath")[0][0]
        off, d = int(conn["offset"]), conn["direction"]
        for by, row in enumerate(_cells(B)):
            for bx, m in enumerate(row):
                if d == "up":
                    sx, sy = bx + off, by - bh
                elif d == "down":
                    sx, sy = bx + off, by + h
                elif d == "left":
                    sx, sy = bx - bw, by + off
                else:
                    sx, sy = bx + w, by + off
                if not (-MAP_OFFSET <= sx < w + MAP_OFFSET and -MAP_OFFSET <= sy < h + MAP_OFFSET):
                    continue
                if (sx, sy) in cells:
                    continue
                if not same and seam_fallback:
                    drawable = m < NUM_METATILES_IN_PRIMARY and B["primary_tileset"] == L["primary_tileset"]
                    if not drawable:
                        m = border
                cells[(sx, sy)] = m
    return L, cells


def render_scene(
    map_name: str,
    out_path: Path,
    cam_x: int,
    cam_y: int,
    view_w: int = 15,
    view_h: int = 10,
    scale: int = 2,
    *,
    seam_fallback: bool = True,
) -> Path:
    """Render what the game draws for cells [cam_x, cam_x+view_w) x [cam_y, cam_y+view_h)."""
    L, cells = scene_grid(map_name, seam_fallback)
    primary, secondary = load_tilesets(L["primary_tileset"], L["secondary_tileset"])
    border = _cells(L, "border_filepath")
    img = Image.new("RGBA", (view_w * 16, view_h * 16), primary["backdrop"])
    cache: dict[int, Image.Image] = {}
    for ly in range(view_h):
        for lx in range(view_w):
            x, y = cam_x + lx, cam_y + ly
            m = cells.get((x, y))
            if m is None:
                m = border[y % len(border)][x % len(border[0])]
            tile = cache.get(m)
            if tile is None:
                tile = cache[m] = render_metatile(primary, secondary, m)
            img.paste(tile, (lx * 16, ly * 16), tile)
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("maps", nargs="*", help="Layout names (default: Emerald acceptance set)")
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa/renders"))
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--full", action="store_true", help="Render full map extents")
    args = ap.parse_args()
    names = args.maps or [
        "LittlerootTown", "OldaleTown", "Route101", "RustboroCity", "LilycoveCity",
    ]
    args.out.mkdir(parents=True, exist_ok=True)
    for name in names:
        layout = find_layout(name)
        w, h = int(layout["width"]), int(layout["height"])
        if args.full:
            render(name, args.out / f"{name}.png", 0, 0, w, h, args.scale)
        else:
            render(name, args.out / f"{name}.png", 0, 0, min(w, 40), min(h, 40), args.scale)


if __name__ == "__main__":
    main()
