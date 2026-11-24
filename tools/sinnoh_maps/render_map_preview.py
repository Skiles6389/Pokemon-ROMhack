#!/usr/bin/env python3
"""Render a map.bin preview using Emerald tileset PNGs (no ROM dump / DS assets)."""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]


def load_tileset(primary: str, secondary: str):
    """Load 8x8 tiles + metatile definitions for primary/secondary tilesets."""

    def ts_path(name: str) -> Path:
        # gTileset_General -> primary/general or secondary/...
        short = name.replace("gTileset_", "")
        # camel to path: Petalburg -> petalburg, BikeShop -> bike_shop-ish
        folder = "".join(("_" + c.lower() if c.isupper() else c) for c in short).lstrip("_")
        for root in (REPO / "data/tilesets/primary", REPO / "data/tilesets/secondary"):
            p = root / folder
            if p.exists():
                return p
        # special cases
        aliases = {
            "general": "general",
            "petalburg": "petalburg",
            "facility": "facility",
            "cave": "cave",
            "building": "building",
        }
        key = folder
        for root in (REPO / "data/tilesets/primary", REPO / "data/tilesets/secondary"):
            if (root / key).exists():
                return root / key
        raise FileNotFoundError(name)

    def load_one(path: Path):
        tiles_img = Image.open(path / "tiles.png").convert("RGBA")
        # tiles.png is usually 128px wide (16 tiles)
        tw = tiles_img.width // 8
        metatiles = (path / "metatiles.bin").read_bytes()
        # each metatile: 8 bytes = 4 tiles * (tile_id:10 + flip:2 + pal:4) as u16 little
        n = len(metatiles) // 8
        metas = []
        for i in range(n):
            entries = []
            for j in range(4):
                v = struct.unpack_from("<H", metatiles, i * 8 + j * 2)[0]
                tid = v & 0x3FF
                hflip = (v >> 10) & 1
                vflip = (v >> 11) & 1
                pal = (v >> 12) & 0xF
                entries.append((tid, hflip, vflip, pal))
            metas.append(entries)
        return tiles_img, tw, metas

    p_path = ts_path(primary)
    s_path = ts_path(secondary)
    p_tiles, p_tw, p_meta = load_one(p_path)
    s_tiles, s_tw, s_meta = load_one(s_path)
    return (p_tiles, p_tw, p_meta), (s_tiles, s_tw, s_meta)


def get_tile(tiles_img, tw, tid, hflip, vflip):
    x = (tid % tw) * 8
    y = (tid // tw) * 8
    tile = tiles_img.crop((x, y, x + 8, y + 8))
    if hflip:
        tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
    if vflip:
        tile = tile.transpose(Image.FLIP_TOP_BOTTOM)
    return tile


def render(layout_name: str, out_path: Path, cam_x: int = 0, cam_y: int = 0, view_w: int = 15, view_h: int = 10, scale: int = 2):
    layouts = json.loads((REPO / "data/layouts/layouts.json").read_text())
    layout = next(L for L in layouts["layouts"] if L["name"].startswith(layout_name) or L["id"] == "LAYOUT_" + layout_name.upper() or layout_name in L["name"])
    w, h = layout["width"], layout["height"]
    data = (REPO / layout["blockdata_filepath"]).read_bytes()
    (p_tiles, p_tw, p_meta), (s_tiles, s_tw, s_meta) = load_tileset(layout["primary_tileset"], layout["secondary_tileset"])

    vw = min(view_w, w - cam_x)
    vh = min(view_h, h - cam_y)
    img = Image.new("RGBA", (vw * 16, vh * 16), (40, 80, 40, 255))

    for ly in range(vh):
        for lx in range(vw):
            mx, my = cam_x + lx, cam_y + ly
            mt = struct.unpack_from("<H", data, (my * w + mx) * 2)[0] & 0x3FF
            if mt < 0x200:
                tiles_img, tw, metas = p_tiles, p_tw, p_meta
                local = mt
            else:
                tiles_img, tw, metas = s_tiles, s_tw, s_meta
                local = mt - 0x200
            if local >= len(metas):
                continue
            entries = metas[local]
            # metatile quadrants: TL TR BL BR
            positions = [(0, 0), (8, 0), (0, 8), (8, 8)]
            for (tid, hf, vf, _pal), (ox, oy) in zip(entries, positions):
                tile = get_tile(tiles_img, tw, tid, hf, vf)
                img.paste(tile, (lx * 16 + ox, ly * 16 + oy), tile)

    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print("wrote", out_path, img.size)


def main():
    out = Path("/opt/cursor/artifacts")
    # Route 205 South - near Floaroma connection / bridge area
    render("Route205_South", out / "m14_route205_south.png", cam_x=8, cam_y=78, view_w=16, view_h=12)
    # Valley Windworks exterior - door area
    render("ValleyWindworks_Exterior", out / "m14_valley_windworks_exterior.png", cam_x=10, cam_y=6, view_w=16, view_h=12)
    # Interior - generator hall / Mars area
    render("ValleyWindworks_Interior", out / "m14_valley_windworks_interior.png", cam_x=8, cam_y=2, view_w=16, view_h=12)
    # Mars encounter stand-in: interior near Mars coords with caption bar
    render("ValleyWindworks_Interior", out / "m14_commander_mars_encounter.png", cam_x=12, cam_y=3, view_w=12, view_h=10)


if __name__ == "__main__":
    main()
