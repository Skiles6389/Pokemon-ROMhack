#!/usr/bin/env python3
"""
M36: Iron Island lower floors (1F through B3F).

Land IDs:
  1F              500
  B1F West        501
  B1F East        502
  B2F East        503
  B2F West        504-507 (2x2)
  B3F             508

Replaces IronIsland_1F_Stub.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinnoh_build_lib import (  # noqa: E402
    GFX_DEFAULT,
    MAPS,
    PLAT_MAPS,
    ensure_trainer,
    face,
    find_walkable,
    grid_from_chunks,
    obj,
    pack,
    register_maps,
    scrub,
    warp,
    write_layout,
    write_map,
)

FLOORS = [
    ("IronIsland_1F", [[500]], "iron_island_1f", "MAP_IRON_ISLAND_1F", "LAYOUT_IRON_ISLAND_1F", 32),
    ("IronIsland_B1F_West", [[501]], "iron_island_b1f_left_room", "MAP_IRON_ISLAND_B1F_WEST", "LAYOUT_IRON_ISLAND_B1F_WEST", 33),
    ("IronIsland_B1F_East", [[502]], "iron_island_b1f_right_room", "MAP_IRON_ISLAND_B1F_EAST", "LAYOUT_IRON_ISLAND_B1F_EAST", 34),
    ("IronIsland_B2F_East", [[503]], "iron_island_b2f_right_room", "MAP_IRON_ISLAND_B2F_EAST", "LAYOUT_IRON_ISLAND_B2F_EAST", 35),
    ("IronIsland_B2F_West", [[504, 505], [506, 507]], "iron_island_b2f_left_room", "MAP_IRON_ISLAND_B2F_WEST", "LAYOUT_IRON_ISLAND_B2F_WEST", 36),
    ("IronIsland_B3F", [[508]], "iron_island_b3f", "MAP_IRON_ISLAND_B3F", "LAYOUT_IRON_ISLAND_B3F", 37),
]


def resolve(dest: str) -> str:
    d = (dest or "").upper()
    pairs = [
        ("IRON_ISLAND_B2F_LEFT", "MAP_IRON_ISLAND_B2F_WEST"),
        ("IRON_ISLAND_B2F_RIGHT", "MAP_IRON_ISLAND_B2F_EAST"),
        ("IRON_ISLAND_B1F_LEFT", "MAP_IRON_ISLAND_B1F_WEST"),
        ("IRON_ISLAND_B1F_RIGHT", "MAP_IRON_ISLAND_B1F_EAST"),
        ("IRON_ISLAND_B3F", "MAP_IRON_ISLAND_B3F"),
        ("IRON_ISLAND_1F", "MAP_IRON_ISLAND_1F"),
        ("IRON_RUINS", "MAP_IRON_ISLAND_B3F"),  # stub ruins back into B3F
        ("IRON_ISLAND_IRON_RUINS", "MAP_IRON_ISLAND_B3F"),
        ("IRON_ISLAND", "MAP_IRON_ISLAND"),
    ]
    for key, mid in pairs:
        if key in d:
            return mid
    return "MAP_IRON_ISLAND"


def densify_local(em, plat, w, h, level):
    pe_path = PLAT_MAPS / plat / "events.json"
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    warps = []
    if not pe_path.exists():
        return objs, scripts, warps
    pe = json.loads(pe_path.read_text())
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"]), int(po["z"])
        if not (0 <= lx < w and 0 <= ly < h) or (lx, ly) in occupied:
            continue
        occupied.add((lx, ly))
        raw = (po.get("graphics_id") or "").upper()
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_HIKER")
        tr = po.get("trainer") or {}
        if "POKEBALL" in raw or "ITEM_BALL" in raw:
            label = f"{em}_EventScript_Item{n}"
            objs.append(obj("OBJ_EVENT_GFX_ITEM_BALL", lx, ly, label))
            scripts += f"{label}::\n\tfinditem ITEM_ULTRA_BALL\n\tend\n\n"
        elif "STRENGTH_BOULDER" in raw or "BOULDER" in raw:
            objs.append(obj("OBJ_EVENT_GFX_PUSHABLE_BOULDER", lx, ly, "EventScript_StrengthBoulder"))
        elif "ROCK_SMASH" in raw or "BREAKABLE" in raw:
            objs.append(obj("OBJ_EVENT_GFX_BREAKABLE_ROCK", lx, ly, "EventScript_RockSmash"))
        elif tr.get("id"):
            tid = tr["id"] if str(tr["id"]).startswith("TRAINER_") else f"TRAINER_{tr['id']}"
            tid = re.sub(r"[^A-Z0-9_]", "_", tid.upper())
            if not tid.startswith("TRAINER_"):
                tid = "TRAINER_" + tid
            if not tid.endswith("_II"):
                tid = tid + "_II"
            ensure_trainer(
                tid,
                level,
                "Hiker",
                "Hiker",
                [("Onix", level), ("Graveler", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title() if tid.split("_")[-1] != "II" else tid.split("_")[-2][:10].title(),
                tag="Sinnoh Iron Island",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2), movement=face(po.get("initial_dir"))))
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f'{label}_Intro:\n\t.string "Iron Island forges tough trainers!$"\n\n'
                f'{label}_Defeat:\n\t.string "Tempered...$"\n\n'
                f'{label}_After:\n\t.string "Watch your step on the lifts.$"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement=face(po.get("initial_dir"))))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "Ore carts still rattle below.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or ""))
    return objs, scripts, warps


def link_reciprocal(names):
    maps = {}
    for n in names:
        maps[n] = json.loads((MAPS / n / "map.json").read_text())
    id_to_name = {d["id"]: n for n, d in maps.items()}
    id_to_name["MAP_IRON_ISLAND"] = None
    for n, data in maps.items():
        mid = data["id"]
        for w in data.get("warp_events") or []:
            dest = w.get("dest_map")
            if dest == "MAP_IRON_ISLAND":
                # outdoor cave mouths: warps 1 and 2 on IronIsland exterior
                w["dest_warp_id"] = "1"
                continue
            dn = id_to_name.get(dest)
            if not dn:
                w["dest_warp_id"] = "0"
                continue
            ddata = maps[dn]
            back = [i for i, dw in enumerate(ddata.get("warp_events") or []) if dw.get("dest_map") == mid]
            w["dest_warp_id"] = str(back[0] if back else 0)
        (MAPS / n / "map.json").write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    indoor = []
    for name, chunks, plat, mid, layout, level in FLOORS:
        grid, w, h = grid_from_chunks(chunks, cave=True)
        write_layout(name, w, h, "gTileset_General", "gTileset_Cave", pack(grid), lid=layout)
        objs, scripts, vwarps = densify_local(name, plat, w, h, level)
        warps = [warp(lx, ly, resolve(dest), 0) for lx, ly, dest in vwarps]
        if not warps:
            warps = [warp(*find_walkable(grid), "MAP_IRON_ISLAND", 1)]
        write_map(
            name,
            {
                "id": mid,
                "name": name,
                "layout": layout,
                "music": "MUS_PETALBURG_WOODS",
                "region": "REGION_HOENN",
                "region_map_section": "MAPSEC_ROUTE_213",
                "requires_flash": False,
                "weather": "WEATHER_NONE",
                "map_type": "MAP_TYPE_UNDERGROUND",
                "allow_cycling": True,
                "allow_escaping": True,
                "allow_running": True,
                "show_map_name": True,
                "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
                "connections": None,
                "object_events": objs,
                "warp_events": warps,
                "coord_events": [],
                "bg_events": [],
            },
            scripts,
        )
        indoor.append(name)

    # Retarget exterior stub warps to real 1F
    path = MAPS / "IronIsland" / "map.json"
    data = json.loads(path.read_text())
    for w in data.get("warp_events") or []:
        if w.get("dest_map") == "MAP_IRON_ISLAND_1F_STUB":
            w["dest_map"] = "MAP_IRON_ISLAND_1F"
            w["dest_warp_id"] = "0"
    path.write_text(json.dumps(data, indent=2) + "\n")

    link_reciprocal(indoor)
    register_maps([], indoor, "gMapGroup_IndoorM36IronIsland")
    scrub(indoor + ["IronIsland"])
    print("M36 Iron Island floors build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
