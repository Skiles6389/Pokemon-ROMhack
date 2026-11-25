#!/usr/bin/env python3
"""Tileset consistency check: every metatile a map shows must render correctly in-game.

Engine facts (include/fieldmap.h, src/fieldmap.c):
  - metatile ids 0..511 come from the primary tileset, 512.. from the secondary
    (local id = id - 512); an id past the secondary's metatiles.bin reads
    whatever ROM data follows the array -> garbage on screen.
  - tile ids 0..511 are primary VRAM tiles, 512.. secondary; a tile index past
    the secondary's tiles.png is uninitialised VRAM.
  - only NUM_PALS_TOTAL = 13 BG palettes belong to the map (0-5 primary,
    6-12 secondary); palettes 13-15 are overwritten by the text window/UI.
  - only ONE primary+secondary pair is in VRAM.  Cells of a connected map that
    fall inside the MAP_OFFSET (7 tile) band next to the shared edge are drawn
    with the CURRENT map's tilesets.  So every cell of the band must be a primary
    metatile (<512) unless both maps use the same secondary tileset.

Checks per map (FAIL):
  metatile_range, tile_range, palette_range, seam (connection band)
With the engine seam fallback (src/fieldmap.c GetSeamFallbackMetatile) such cells
are drawn as the neighbour's border metatile instead of garbage -> seam_fallback warning.
Warnings:
  hidden_*         - bad bottom-layer tile fully covered by an opaque top-layer tile
  never_in_vanilla - a secondary metatile no vanilla Hoenn layout with the same
  secondary ever uses (catches "sheet filler" tiles such as Rustboro 0x301).

Usage: python3 tools/sinnoh_maps/tileset_consistency_check.py [Map ...] [--json OUT]
Default maps: the m50/m51 early-game set.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from tools.sinnoh_maps.render_map_preview import ts_path  # noqa: E402

NUM_PRIMARY = 512
NUM_PALS_IN_PRIMARY = 6
NUM_PALS_TOTAL = 13
MAP_OFFSET = 7
VIEW_X, VIEW_Y = 7, 5   # metatiles visible beside / above-below the player

DEFAULT_MAPS = ["TwinleafTown", "Route201", "VerityLakefront", "LakeVerity",
                "SandgemTown", "Route202", "JubilifeCity"]

# Vanilla Hoenn layouts (left untouched by the Sinnoh port) - reference usage per secondary.
HOENN = re.compile(
    r"^(Route1[0-3]\d|LittlerootTown|OldaleTown|PetalburgCity|PetalburgWoods|RustboroCity|DewfordTown|"
    r"SlateportCity|MauvilleCity|VerdanturfTown|FallarborTown|LavaridgeTown|FortreeCity|LilycoveCity|"
    r"MossdeepCity|SootopolisCity|PacifidlogTown|EverGrande|SouthernIsland|FarawayIsland|BattleFrontier)"
)

LAYOUTS = {L["id"]: L for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"] if "id" in L}


@lru_cache(None)
def map_index() -> dict:
    out = {}
    for mj in (REPO / "data/maps").glob("*/map.json"):
        d = json.loads(mj.read_text())
        out[d["id"]] = mj.parent.name
    return out


def load_map(name: str) -> dict:
    return json.loads((REPO / "data/maps" / name / "map.json").read_text())


def layout_of(name: str) -> dict:
    return LAYOUTS[load_map(name)["layout"]]


def grid(layout: dict) -> list[list[int]]:
    w, h = int(layout["width"]), int(layout["height"])
    raw = (REPO / layout["blockdata_filepath"]).read_bytes()
    return [[struct.unpack_from("<H", raw, (y * w + x) * 2)[0] & 0x3FF for x in range(w)] for y in range(h)]


@lru_cache(None)
def tileset(name: str) -> dict:
    p = ts_path(name)
    raw = (p / "metatiles.bin").read_bytes()
    metas = [struct.unpack_from("<8H", raw, i * 16) for i in range(len(raw) // 16)]
    im = Image.open(p / "tiles.png")
    if im.mode != "P":
        im = im.convert("P")
    tw = im.width // 8
    ntiles = tw * (im.height // 8)
    px = im.load()
    opaque = []
    for i in range(ntiles):
        ox, oy = (i % tw) * 8, (i // tw) * 8
        opaque.append(all(px[ox + a, oy + b] & 0xF for a in range(8) for b in range(8)))
    return {"metas": metas, "ntiles": ntiles, "opaque": opaque}


@lru_cache(None)
def vanilla_usage(secondary: str) -> frozenset:
    used = set()
    for L in LAYOUTS.values():
        if L.get("secondary_tileset") != secondary or not HOENN.match(L["name"]):
            continue
        for row in grid(L):
            used.update(m for m in row if m >= NUM_PRIMARY)
    return frozenset(used)


def _word_problems(w: int, P: dict, S: dict, sec: str) -> list[str]:
    out = []
    tid, pal = w & 0x3FF, w >> 12
    if tid < NUM_PRIMARY:
        if tid >= P["ntiles"]:
            out.append(f"tile_range: tile {tid} >= primary tiles {P['ntiles']}")
    elif tid - NUM_PRIMARY >= S["ntiles"]:
        out.append(f"tile_range: tile {tid} past {sec} tiles ({S['ntiles']})")
    if pal >= NUM_PALS_TOTAL:
        out.append(f"palette_range: palette {pal} (only 0-{NUM_PALS_TOTAL - 1} are map palettes)")
    return out


def _opaque(w: int, P: dict, S: dict) -> bool:
    tid = w & 0x3FF
    if tid < NUM_PRIMARY:
        return tid < P["ntiles"] and P["opaque"][tid]
    loc = tid - NUM_PRIMARY
    return loc < S["ntiles"] and S["opaque"][loc]


def metatile_report(mt: int, prim: str, sec: str) -> tuple[list[str], list[str]]:
    """(fails, warnings) for drawing metatile `mt` with (prim, sec) loaded.

    A bad tile in the bottom layer that an opaque, valid top-layer tile fully covers
    never reaches the screen (vanilla Littleroot/Sandgem lab vent 0x24A/0x24B), so it
    is only a warning."""
    P, S = tileset(prim), tileset(sec)
    if mt < NUM_PRIMARY:
        if mt >= len(P["metas"]):
            return [f"metatile_range: 0x{mt:03X} >= primary count {len(P['metas'])}"], []
        words = P["metas"][mt]
    else:
        loc = mt - NUM_PRIMARY
        if loc >= len(S["metas"]):
            return [f"metatile_range: 0x{mt:03X} past {sec} ({len(S['metas'])} metatiles, last 0x{NUM_PRIMARY + len(S['metas']) - 1:03X})"], []
        words = S["metas"][loc]
    fails, warns = set(), set()
    for q in range(4):
        bottom, top = words[q], words[4 + q]
        for pr in _word_problems(top, P, S, sec):
            fails.add(pr)
        bp = _word_problems(bottom, P, S, sec)
        if bp and not _word_problems(top, P, S, sec) and _opaque(top, P, S):
            warns.update(f"hidden_{x} (covered by opaque top layer)" for x in bp)
        else:
            fails.update(bp)
    return sorted(fails), sorted(warns)


def metatile_problems(mt: int, prim: str, sec: str) -> list[str]:
    """Why metatile `mt` would not render correctly with (prim, sec) loaded; [] = fine."""
    return metatile_report(mt, prim, sec)[0]


def engine_has_seam_fallback() -> bool:
    """src/fieldmap.c FillConnection swaps undrawable connected-map metatiles for a border metatile."""
    src = REPO / "src/fieldmap.c"
    return src.exists() and "GetSeamFallbackMetatile" in src.read_text()


def raw_grid(layout: dict) -> list[list[int]]:
    w, h = int(layout["width"]), int(layout["height"])
    raw = (REPO / layout["blockdata_filepath"]).read_bytes()
    return [[struct.unpack_from("<H", raw, (y * w + x) * 2)[0] for x in range(w)] for y in range(h)]


def seam_band(src: str, conn: dict) -> tuple[str, list[tuple[int, int, int]]]:
    """Cells of the neighbour map that `src` actually puts on screen.

    The camera shows 7 metatiles left/right of the player and 5 (4.5) above/below;
    the map buffer only holds MAP_OFFSET (7) cells past the edge.  A neighbour cell
    counts when some walkable cell of `src` (collision bits 0) has it in view.
    Returns (neighbour map name, [(x, y, metatile)]) in neighbour coordinates."""
    nb = map_index()[conn["map"]]
    A, B = layout_of(src), layout_of(nb)
    aw, ah = int(A["width"]), int(A["height"])
    bw, bh = int(B["width"]), int(B["height"])
    g = grid(B)
    walk = [(x, y) for y, row in enumerate(raw_grid(A)) for x, v in enumerate(row) if not (v >> 10) & 3]
    off, d = int(conn["offset"]), conn["direction"]
    # neighbour cell (bx, by) -> src coordinates
    if d == "up":
        to_src = lambda bx, by: (bx + off, by - bh)
    elif d == "down":
        to_src = lambda bx, by: (bx + off, by + ah)
    elif d == "left":
        to_src = lambda bx, by: (bx - bw, by + off)
    else:
        to_src = lambda bx, by: (bx + aw, by + off)
    cand = {}
    for by in range(bh):
        for bx in range(bw):
            sx, sy = to_src(bx, by)
            if -MAP_OFFSET <= sx < aw + MAP_OFFSET and -MAP_OFFSET <= sy < ah + MAP_OFFSET:
                cand[(sx, sy)] = (bx, by, g[by][bx])
    seen = set()
    for px, py in walk:
        for dy in range(-VIEW_Y, VIEW_Y + 1):
            for dx in range(-VIEW_X, VIEW_X + 1):
                c = (px + dx, py + dy)
                if c in cand:
                    seen.add(c)
    return nb, [cand[c] for c in sorted(seen)]


def check_map(name: str) -> dict:
    L = layout_of(name)
    prim, sec = L["primary_tileset"], L["secondary_tileset"]
    g = grid(L)
    fails, warns = [], []
    counts = Counter(m for row in g for m in row)
    for mt, n in sorted(counts.items()):
        f_, w_ = metatile_report(mt, prim, sec)
        for p in f_:
            fails.append({"check": p.split(":")[0], "metatile": f"0x{mt:03X}", "cells": n, "detail": f"0x{mt:03X} {p}"})
        for p in w_:
            first = next((x, y) for y, row in enumerate(g) for x, m in enumerate(row) if m == mt)
            warns.append({"check": p.split(":")[0], "metatile": f"0x{mt:03X}", "cells": n, "first": first,
                          "detail": f"0x{mt:03X} {p}"})
    van = vanilla_usage(sec)
    if van:
        for mt, n in sorted(counts.items()):
            if mt >= NUM_PRIMARY and mt not in van:
                first = next((x, y) for y, row in enumerate(g) for x, m in enumerate(row) if m == mt)
                warns.append({"check": "never_in_vanilla", "metatile": f"0x{mt:03X}", "cells": n,
                              "first": first, "detail": f"{sec} 0x{mt:03X} is never used by a vanilla layout"})
    seams = []
    fallback = engine_has_seam_fallback()
    for conn in load_map(name).get("connections") or []:
        nb, cells = seam_band(name, conn)
        NB = layout_of(nb)
        same = NB["secondary_tileset"] == sec and NB["primary_tileset"] == prim
        bad = Counter()
        for x, y, mt in cells:
            if same:
                continue
            if mt >= NUM_PRIMARY or metatile_problems(mt, prim, sec):
                bad[mt] += 1
        seams.append({"neighbour": nb, "direction": conn["direction"], "neighbour_secondary": NB["secondary_tileset"],
                      "band_cells": len(cells), "bad_cells": sum(bad.values())})
        if bad and fallback:
            first = (nb, conn["direction"])
            warns.append({"check": "seam_fallback", "neighbour": nb, "cells": sum(bad.values()), "first": first,
                          "detail": f"{nb}: {sum(bad.values())} cells ({', '.join(f'0x{m:03X}' for m in sorted(bad)[:8])}) "
                                    f"on screen from {name} are drawn as {nb}'s border metatile by the engine seam "
                                    f"fallback until the player crosses (no garbage, but a pop-in)"})
        elif bad:
            fails.append({"check": "seam", "neighbour": nb, "direction": conn["direction"], "cells": sum(bad.values()),
                          "detail": f"{nb} shows {sum(bad.values())} secondary metatiles ({', '.join(f'0x{m:03X}' for m in sorted(bad)[:12])}"
                                    f"{'...' if len(bad) > 12 else ''}) on screen from {name}, which draws them with "
                                    f"{sec}; they belong to {NB['secondary_tileset']}"})
    return {"map": name, "primary": prim, "secondary": sec, "status": "FAIL" if fails else "PASS",
            "fails": fails, "warnings": warns, "seams": seams}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("maps", nargs="*", default=DEFAULT_MAPS)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--strict", action="store_true", help="never_in_vanilla warnings also fail")
    a = ap.parse_args()
    res = [check_map(m) for m in a.maps]
    rc = 0
    for r in res:
        if a.strict and r["warnings"]:
            r["status"] = "FAIL"
        print(f"{r['status']:4}  {r['map']:16} {r['secondary']}")
        for f in r["fails"]:
            print("      FAIL", f["detail"], f"[{f['cells']} cells]")
        for w in r["warnings"]:
            print("      warn", w["detail"], f"[{w['cells']} cells, first {w['first']}]")
        rc |= r["status"] == "FAIL"
    if a.json:
        a.json.write_text(json.dumps(res, indent=1))
    print(f"{sum(r['status'] == 'PASS' for r in res)}/{len(res)} maps pass")
    return int(rc)


if __name__ == "__main__":
    sys.exit(main())
