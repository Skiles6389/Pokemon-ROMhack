#!/usr/bin/env python3
"""Render full top-down PNGs of every Sinnoh LAND_TABLE map + related interiors.

Uses Emerald tileset PNGs only (tools/sinnoh_maps/render_map_preview).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.platinum_1to1_audit import LAND_TABLE  # noqa: E402
from tools.sinnoh_maps.render_map_preview import render  # noqa: E402

LAYOUTS_JSON = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
}
MAP_GROUPS = json.loads((REPO / "data/maps/map_groups.json").read_text())


def sinnoh_map_names() -> list[str]:
    """LAND_TABLE outdoor/cave maps + interiors whose name starts with a known root."""
    names = set(LAND_TABLE)
    roots = tuple(LAND_TABLE) + (
        "LakeVerity", "VerityLakefront", "Jubilife", "Sandgem", "Twinleaf",
        "Oreburgh", "Route201", "Route202", "Route203",
    )
    for group, maps in MAP_GROUPS.items():
        if not isinstance(maps, list):
            continue
        for m in maps:
            if any(m == r or m.startswith(r + "_") for r in roots):
                names.add(m)
    # Prefer stable order: LAND_TABLE first, then interiors
    ordered = list(LAND_TABLE)
    for n in sorted(names):
        if n not in LAND_TABLE:
            ordered.append(n)
    return [n for n in ordered if n in LAYOUTS_JSON]


def render_one(name: str, out_dir: Path, *, max_dim: int = 96, scale: int = 1) -> Path | None:
    meta = LAYOUTS_JSON[name]
    w, h = int(meta["width"]), int(meta["height"])
    vw, vh = min(w, max_dim), min(h, max_dim)
    # Scale down huge maps so contact sheets stay manageable
    sc = scale
    if max(vw, vh) > 64:
        sc = 1
    elif max(vw, vh) <= 32:
        sc = max(scale, 2)
    out = out_dir / f"{name}.png"
    try:
        render(name, out, cam_x=0, cam_y=0, view_w=vw, view_h=vh, scale=sc)
    except Exception as e:  # noqa: BLE001 — keep batch going
        print(f"SKIP {name}: {e}")
        return None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa/renders"))
    ap.add_argument("--only", nargs="*", help="Optional map name filter")
    ap.add_argument("--max-dim", type=int, default=96)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    names = sinnoh_map_names()
    if args.only:
        want = set(args.only)
        names = [n for n in names if n in want]
    ok = 0
    for n in names:
        if render_one(n, args.out, max_dim=args.max_dim):
            ok += 1
    print(f"=== rendered {ok}/{len(names)} maps → {args.out} ===")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
