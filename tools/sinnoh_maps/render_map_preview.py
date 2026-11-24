#!/usr/bin/env python3
"""Render a map.bin preview using Emerald tileset PNGs (no ROM dump / DS assets)."""
from __future__ import annotations

import json
import struct
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]

# Fallback fills for metatiles whose quadrant defs are empty in the tileset
# (Emerald tree halves often store graphics in only 2 of 4 metatiles).
FALLBACK = {
    0x001: (88, 168, 72, 255),    # grass
    0x00D: (56, 120, 48, 255),    # tall grass
    0x00E: (72, 140, 64, 255),    # moss
    0x079: (120, 112, 96, 255),   # rock
    0x0D5: (96, 88, 72, 255),     # ledge
    0x0D6: (96, 88, 72, 255),
    0x121: (200, 184, 120, 255),  # sand
    0x170: (64, 120, 200, 255),   # water
    0x1D4: (24, 88, 40, 255),     # tree TL
    0x1D5: (28, 96, 44, 255),     # tree TR
    0x1DC: (20, 72, 32, 255),     # tree BL
    0x1DD: (32, 104, 48, 255),    # tree BR
    0x201: (168, 160, 152, 255),  # indoor floor
    0x20E: (96, 72, 56, 255),     # door
    0x21A: (88, 80, 96, 255),     # indoor wall
}


def parse_jasc_pal(path: Path):
    lines = path.read_text().strip().splitlines()
    colors = []
    for line in lines[3:]:
        parts = line.split()
        if len(parts) >= 3:
            colors.append((int(parts[0]), int(parts[1]), int(parts[2]), 255))
    while len(colors) < 16:
        colors.append((0, 0, 0, 0))
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


def load_one(path: Path):
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
    metatiles = (path / "metatiles.bin").read_bytes()
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
    return {
        "index": index_data,
        "tw": tw,
        "th": th,
        "width": tiles_img.width,
        "metas": metas,
        "pals": pals,
    }


def get_colored_tile(ts, tid_local, hflip, vflip, pal_idx):
    tw, th, w = ts["tw"], ts["th"], ts["width"]
    max_tid = tw * th
    if tid_local >= max_tid:
        return Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    x0 = (tid_local % tw) * 8
    y0 = (tid_local // tw) * 8
    pal = ts["pals"][pal_idx % 16]
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


def render_metatile(primary, secondary, mt_id: int) -> Image.Image:
    """Render one 16x16 metatile; fall back to solid color if defs are empty."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    if mt_id < 0x200:
        ts = primary
        other = secondary
        local = mt_id
    else:
        ts = secondary
        other = primary
        local = mt_id - 0x200
    if local >= len(ts["metas"]):
        color = FALLBACK.get(mt_id, (48, 96, 56, 255))
        return Image.new("RGBA", (16, 16), color)

    entries = ts["metas"][local]
    positions = [(0, 0), (8, 0), (0, 8), (8, 8)]
    painted = 0
    for (tid, hf, vf, pal), (ox, oy) in zip(entries, positions):
        # Tile IDs 0-511 = primary sheet, 512-1023 = secondary sheet
        if tid < 512:
            src = primary if mt_id < 0x200 else (primary if tid < 512 else secondary)
            # When rendering secondary metatile with tid<512, it's primary tiles
            src = primary
            local_tid = tid
        else:
            src = secondary
            local_tid = tid - 512
        tile = get_colored_tile(src, local_tid, hf, vf, pal)
        # Count non-transparent pixels
        alphas = tile.getchannel("A").getdata()
        if any(a > 0 for a in alphas):
            painted += 1
        img.paste(tile, (ox, oy), tile)

    if painted == 0:
        color = FALLBACK.get(mt_id, (48, 96, 56, 255))
        return Image.new("RGBA", (16, 16), color)
    return img


def render(
    layout_name: str,
    out_path: Path,
    cam_x: int = 0,
    cam_y: int = 0,
    view_w: int = 15,
    view_h: int = 10,
    scale: int = 2,
):
    layouts = json.loads((REPO / "data/layouts/layouts.json").read_text())
    layout = next(
        L
        for L in layouts["layouts"]
        if L["name"].startswith(layout_name)
        or layout_name in L["name"]
    )
    w, h = layout["width"], layout["height"]
    data = (REPO / layout["blockdata_filepath"]).read_bytes()
    primary = load_one(ts_path(layout["primary_tileset"]))
    secondary = load_one(ts_path(layout["secondary_tileset"]))

    vw = min(view_w, w - cam_x)
    vh = min(view_h, h - cam_y)
    img = Image.new("RGBA", (vw * 16, vh * 16), (40, 72, 48, 255))

    for ly in range(vh):
        for lx in range(vw):
            mx, my = cam_x + lx, cam_y + ly
            mt = struct.unpack_from("<H", data, (my * w + mx) * 2)[0] & 0x3FF
            tile = render_metatile(primary, secondary, mt)
            img.paste(tile, (lx * 16, ly * 16), tile)

    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print("wrote", out_path, img.size)


def main():
    out = Path("/opt/cursor/artifacts")
    # M20 verification shots (Emerald tiles only — no live ROM dump / DS assets)
    render("Route214", out / "m20_route214_valor_lakefront.png", cam_x=8, cam_y=0, view_w=20, view_h=16, scale=2)
    # Composite-ish Valor plaza view
    render("ValorLakefront", out / "m20_valor_lakefront_resort.png", cam_x=16, cam_y=36, view_w=24, view_h=18, scale=2)
    render("PastoriaCity", out / "m20_pastoria_city.png", cam_x=8, cam_y=8, view_w=24, view_h=18, scale=2)
    render("PastoriaCity_Gym", out / "m20_pastoria_gym_crasher_wake.png", cam_x=4, cam_y=0, view_w=16, view_h=16, scale=2)
    render("PastoriaCity", out / "m20_galactic_chase_trigger.png", cam_x=28, cam_y=4, view_w=20, view_h=14, scale=2)


if __name__ == "__main__":
    main()
