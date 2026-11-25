#!/usr/bin/env python3
"""Render a map.bin preview using Emerald tileset PNGs (no ROM dump / DS assets).

Matches Porymap / in-game metatile drawing:
  - Primary metatiles 0..511, secondary metatiles 512.. (local = id - 512)
  - Primary tiles 0..511, secondary tiles 512.. (local = tid - 512)
  - Each metatile = 8 little-endian u16s (16 bytes): bottom TL/TR/BL/BR then top
  - Tile word: bits 0-9 tile, 10 hflip, 11 vflip, 12-15 palette
  - Palettes 0-5 from primary tileset, 6-15 from secondary
  - Color index 0 is transparent; bottom layer then top layer composite
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
NUM_TILES_PER_METATILE = 8  # bottom 4 + top 4
TILE_BYTES = NUM_TILES_PER_METATILE * 2  # 16
QUAD_POS = ((0, 0), (8, 0), (0, 8), (8, 8))  # TL, TR, BL, BR


def parse_jasc_pal(path: Path) -> list[tuple[int, int, int, int]]:
    lines = path.read_text().strip().splitlines()
    colors: list[tuple[int, int, int, int]] = []
    for line in lines[3:]:
        parts = line.split()
        if len(parts) >= 3:
            colors.append((int(parts[0]), int(parts[1]), int(parts[2]), 255))
    while len(colors) < 16:
        colors.append((0, 0, 0, 0))
    # Palette index 0 is always transparent for overworld tiles
    colors[0] = (0, 0, 0, 0)
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
        "path": path,
    }


def resolve_tile_sheet(primary: dict, secondary: dict, tid: int) -> tuple[dict, int]:
    if tid < NUM_TILES_IN_PRIMARY:
        return primary, tid
    return secondary, tid - NUM_TILES_IN_PRIMARY


def resolve_palette(
    primary: dict, secondary: dict, pal_idx: int
) -> list[tuple[int, int, int, int]]:
    """VRAM layout: primary owns pals 0-5, secondary owns 6-15."""
    if pal_idx < 6:
        return primary["pals"][pal_idx]
    return secondary["pals"][pal_idx % 16]


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
        return Image.new("RGBA", (8, 8), (0, 0, 0, 0))
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
        return img
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
    bgcolor: tuple[int, int, int, int] = (0, 0, 0, 255),
) -> Path:
    layout = find_layout(layout_name)
    w, h = int(layout["width"]), int(layout["height"])
    data = (REPO / layout["blockdata_filepath"]).read_bytes()
    primary, secondary = load_tilesets(layout["primary_tileset"], layout["secondary_tileset"])

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
