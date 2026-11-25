#!/usr/bin/env python3
"""Switch paved cities to Rustboro secondary; scrub remaining black metatiles.

Petalburg secondary only has 144 metas (max 0x28F). Rustboro pave/civic IDs
(0x2BB, 0x22F, …) render as solid black there. Emerald RustboroCity uses
gTileset_Rustboro — paved Sinnoh cities should too.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.black_metatile_audit import (  # noqa: E402
    BLACK_FRAC,
    metatile_black_frac,
)
from tools.sinnoh_maps.city_door_warp_audit import OUTDOOR_SETTLEMENTS  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import MT_GRASS, pack  # noqa: E402

LAYOUTS_PATH = REPO / "data/layouts/layouts.json"
LAYOUTS = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads(LAYOUTS_PATH.read_text())["layouts"]
}

# Cities that need Rustboro civic/pave stamps
RUSTBORO_CITIES = {
    "JubilifeCity", "OreburghCity", "EternaCity", "HearthomeCity",
    "VeilstoneCity", "PastoriaCity", "CanalaveCity", "SnowpointCity",
    "SunyshoreCity", "PokemonLeague_Exterior", "FightArea",
}
# Towns stay on Petalburg (house/PC_OLDALE stamps)
PETALBURG_TOWNS = {
    "TwinleafTown", "SandgemTown", "FloaromaTown", "SolaceonTown",
    "CelesticTown", "SurvivalArea", "ResortArea",
}

MT_CITY_PAVE = 0x2BB


def switch_secondary(name: str, secondary: str) -> bool:
    layouts = json.loads(LAYOUTS_PATH.read_text())
    changed = False
    for L in layouts["layouts"]:
        if L["name"].replace("_Layout", "") == name:
            if L.get("secondary_tileset") != secondary:
                L["secondary_tileset"] = secondary
                changed = True
            break
    if changed:
        LAYOUTS_PATH.write_text(json.dumps(layouts, indent=2) + "\n")
        LAYOUTS[name]["secondary_tileset"] = secondary
    return changed


def scrub_black(name: str, fill: int) -> int:
    meta = LAYOUTS[name]
    primary = meta.get("primary_tileset") or "gTileset_General"
    secondary = meta.get("secondary_tileset") or "gTileset_Petalburg"
    w, h = int(meta["width"]), int(meta["height"])
    path = REPO / meta["blockdata_filepath"]
    data = bytearray(path.read_bytes())
    n = 0
    for i in range(w * h):
        v = struct.unpack_from("<H", data, i * 2)[0]
        mt = v & 0x3FF
        coll = (v >> 10) & 3
        elev = (v >> 12) & 0xF
        if metatile_black_frac(primary, secondary, mt) > BLACK_FRAC:
            # Prefer pave fill on cities, grass on towns
            new_mt = fill
            new_coll = 0
            new_elev = elev if elev else 3
            struct.pack_into("<H", data, i * 2, (new_mt & 0x3FF) | (new_coll << 10) | (new_elev << 12))
            n += 1
    if n:
        path.write_bytes(bytes(data))
    return n


def main() -> int:
    switched = scrubbed = 0
    # Outdoor settlements only — never scrub indoor League rooms / caves.
    targets = sorted(set(OUTDOOR_SETTLEMENTS) | set(RUSTBORO_CITIES) | set(PETALBURG_TOWNS))
    for name in targets:
        if name not in LAYOUTS:
            continue
        if name in RUSTBORO_CITIES:
            if switch_secondary(name, "gTileset_Rustboro"):
                print(f"{name}: secondary → Rustboro")
                switched += 1
            n = scrub_black(name, MT_CITY_PAVE)
        else:
            if name in PETALBURG_TOWNS or name.endswith("Town"):
                if switch_secondary(name, "gTileset_Petalburg"):
                    print(f"{name}: secondary → Petalburg")
                    switched += 1
            n = scrub_black(name, MT_GRASS)
        if n:
            print(f"{name}: scrubbed {n} black cells")
            scrubbed += n
    # refresh module cache after tileset switches
    metatile_black_frac.cache_clear()
    print(f"=== remediate_tileset_and_black: switched={switched} scrubbed={scrubbed} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
