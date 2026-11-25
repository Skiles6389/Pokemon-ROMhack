#!/usr/bin/env python3
"""Render Platinum layout reference heatmaps from land attrs (NOT ripped tiles).

Colors encode collision + behavior only — suitable for side-by-side contact sheets
without committing Nintendo art.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: E402
    PLAT_DATA,
    is_plat_path_behavior,
    load_attrs,
    plat_behavior,
    plat_collision,
    stitch,
)

# Classified palette (legend drawn on each sheet)
COLORS = {
    "solid": (40, 40, 40, 255),
    "walk": (120, 180, 90, 255),       # plain ground
    "path": (190, 170, 120, 255),      # dirt / town walkway
    "tall": (50, 130, 50, 255),
    "water": (50, 100, 200, 255),
    "sand": (210, 190, 120, 255),
    "ledge": (140, 100, 70, 255),
    "other": (90, 90, 110, 255),
}


def classify_attr(v: int) -> str:
    if plat_collision(v):
        return "solid"
    beh = plat_behavior(v)
    if beh in (0x02, 0x03):
        return "tall"
    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
        return "water"
    if beh == 0x21:
        return "sand"
    if is_plat_path_behavior(beh) or beh in {0xA1, 0xA2, 0xA3, 0xA8, 0xA9}:
        return "path"
    if beh == 0x3B:
        return "ledge"
    if beh == 0:
        return "walk"
    return "other"


def render_plat(name: str, scale: int = 3) -> Image.Image | None:
    chunks = LAND_TABLE.get(name)
    if not chunks or not PLAT_DATA.exists():
        return None
    try:
        grid = stitch(chunks)
    except FileNotFoundError:
        return None
    h, w = len(grid), len(grid[0])
    img = Image.new("RGBA", (w * scale, h * scale))
    px = img.load()
    for y in range(h):
        for x in range(w):
            c = COLORS[classify_attr(grid[y][x])]
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, y * scale + dy] = c
    draw = ImageDraw.Draw(img)
    draw.text((4, 4), f"Platinum layout: {name}", fill=(255, 255, 255, 255))
    return img


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa/platinum_ref"))
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    names = list(LAND_TABLE) if not args.only else [n for n in args.only if n in LAND_TABLE]
    ok = 0
    for n in names:
        img = render_plat(n)
        if img is None:
            print(f"SKIP {n}")
            continue
        img.save(args.out / f"{n}.png")
        ok += 1
    print(f"=== platinum refs {ok}/{len(names)} → {args.out} ===")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
