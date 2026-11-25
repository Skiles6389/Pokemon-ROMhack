#!/usr/bin/env python3
"""Side-by-side Emerald render vs Platinum layout-reference contact sheets."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402


def _classified_emerald(name: str, scale: int = 3) -> Image.Image | None:
    """Role-colored Emerald map.bin (clearer than sparse secondary tiles)."""
    import json
    import struct
    import sys
    from pathlib import Path as P

    repo = P(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo))
    from tools.sinnoh_maps.sinnoh_build_lib import (  # noqa: WPS433
        MT_GRASS, MT_ROCK, MT_TALL, MT_TREE, PATH_METATILES, WATER_METATILES,
    )
    door = {0x061, 0x062, 0x041, 0x042, 0x22F, 0x248, 0x287, 0x1CD, 0x20E, 0x09F, 0x0A7}
    layouts = {
        L["name"].replace("_Layout", ""): L
        for L in json.loads((repo / "data/layouts/layouts.json").read_text())["layouts"]
    }
    if name not in layouts:
        return None
    meta = layouts[name]
    w, h = int(meta["width"]), int(meta["height"])
    data = (repo / meta["blockdata_filepath"]).read_bytes()
    colors = {
        "door": (160, 80, 40, 255),
        "pave": (170, 170, 180, 255),
        "building": (200, 170, 130, 255),
        "pc": (80, 140, 220, 255),
        "tree": (30, 100, 40, 255),
        "rock": (110, 100, 90, 255),
        "grass": (90, 170, 70, 255),
        "water": (60, 120, 200, 255),
        "other": (70, 70, 70, 255),
    }
    pc_body = set(range(0x048, 0x064)) | {0x256, 0x25E, 0x25F, 0x257, 0x266, 0x27E}
    img = Image.new("RGBA", (w * scale, h * scale))
    px = img.load()
    for y in range(h):
        for x in range(w):
            mt = struct.unpack_from("<H", data, (y * w + x) * 2)[0] & 0x3FF
            if mt in door:
                c = colors["door"]
            elif mt in pc_body or mt in set(range(0x028, 0x044)):
                c = colors["pc"]
            elif mt in PATH_METATILES or mt == 0x2BB:
                c = colors["pave"]
            elif mt >= 0x200:
                c = colors["building"]
            elif mt in set(MT_TREE):
                c = colors["tree"]
            elif mt in {MT_ROCK, 0x07C, 0x091, 0x139}:
                c = colors["rock"]
            elif mt in (MT_GRASS, MT_TALL):
                c = colors["grass"]
            elif mt in WATER_METATILES:
                c = colors["water"]
            else:
                c = colors["other"]
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, y * scale + dy] = c
    return img


def pair(emerald: Path, plat: Path, out: Path, title: str) -> None:
    # Prefer classified Emerald view (readable) beside Platinum layout attrs
    a = _classified_emerald(title) or Image.open(emerald).convert("RGBA")
    b = Image.open(plat).convert("RGBA")
    # Match heights
    th = max(a.height, b.height) + 28
    tw = a.width + b.width + 24
    canvas = Image.new("RGBA", (tw, th), (24, 24, 28, 255))
    canvas.paste(a, (8, 24), a if a.mode == "RGBA" else None)
    canvas.paste(b, (a.width + 16, 24), b)
    d = ImageDraw.Draw(canvas)
    d.text((8, 4), f"{title} — Emerald map.bin (classified)", fill=(180, 255, 180, 255))
    d.text((a.width + 16, 4), "Platinum layout attrs (not ripped art)", fill=(180, 200, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", type=Path, default=Path("/tmp/sinnoh_qa/renders"))
    ap.add_argument("--plat", type=Path, default=Path("/tmp/sinnoh_qa/platinum_ref"))
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa/contact"))
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    names = list(LAND_TABLE) if not args.only else args.only
    ok = 0
    for n in names:
        er, pr = args.renders / f"{n}.png", args.plat / f"{n}.png"
        if not er.exists() or not pr.exists():
            continue
        pair(er, pr, args.out / f"{n}_contact.png", n)
        ok += 1
    # Early-game montage
    early = [
        "TwinleafTown", "Route201", "SandgemTown", "Route202",
        "JubilifeCity", "Route203", "OreburghCity",
    ]
    tiles = []
    for n in early:
        p = args.out / f"{n}_contact.png"
        if p.exists():
            tiles.append(Image.open(p).convert("RGBA"))
    if tiles:
        # Stack vertically, scale to common width
        w = max(t.width for t in tiles)
        scaled = []
        for t in tiles:
            if t.width != w:
                nh = int(t.height * (w / t.width))
                t = t.resize((w, nh), Image.NEAREST)
            scaled.append(t)
        h = sum(t.height for t in scaled) + 8 * len(scaled)
        montage = Image.new("RGBA", (w, h), (24, 24, 28, 255))
        y = 0
        for t in scaled:
            montage.paste(t, (0, y), t)
            y += t.height + 8
        montage.save(args.out / "early_game_montage.png")
        print("wrote early_game_montage.png", montage.size)
    print(f"=== contact sheets {ok} → {args.out} ===")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
