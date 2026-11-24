#!/usr/bin/env python3
"""
M37: Canalave Library 1F–3F + remaining Canalave interiors (harbor inn, houses).

Land IDs: library 291–293.
Also scaffolds missing Canalave city house warps from Platinum events.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinnoh_build_lib import (  # noqa: E402
    GFX_DEFAULT,
    MAPS,
    PLAT_MAPS,
    face,
    find_walkable,
    grid_from_chunks,
    indoor_room,
    obj,
    pack,
    register_maps,
    scrub,
    warp,
    write_layout,
    write_map,
)

LIBRARY = [
    ("CanalaveCity_Library_1F", [[291]], "canalave_library_1f", "MAP_CANALAVE_CITY_LIBRARY_1F", "LAYOUT_CANALAVE_CITY_LIBRARY_1F"),
    ("CanalaveCity_Library_2F", [[292]], "canalave_library_2f", "MAP_CANALAVE_CITY_LIBRARY_2F", "LAYOUT_CANALAVE_CITY_LIBRARY_2F"),
    ("CanalaveCity_Library_3F", [[293]], "canalave_library_3f", "MAP_CANALAVE_CITY_LIBRARY_3F", "LAYOUT_CANALAVE_CITY_LIBRARY_3F"),
]

# Platinum Canalave interior headers we still lack as distinct maps
HOUSE_STUBS = [
    ("CanalaveCity_House2", "MAP_CANALAVE_CITY_HOUSE2", "canalave_city_west_house", "A quiet Canalave home."),
    ("CanalaveCity_House3", "MAP_CANALAVE_CITY_HOUSE3", "canalave_city_east_house", "Charts and tide tables fill the desk."),
    ("CanalaveCity_House4", "MAP_CANALAVE_CITY_HOUSE4", "canalave_city_southeast_house", "A sailor's boots by the door."),
    ("CanalaveCity_HarborInn", "MAP_CANALAVE_CITY_HARBOR_INN", "canalave_city_harbor_inn", "Captains rest here between voyages."),
    ("CanalaveCity_EldritchHouse", "MAP_CANALAVE_CITY_ELDRITCH_HOUSE", "canalave_city_sailor_eldritch_house", "Old Eldritch mutters about the sea."),
]


def resolve(dest: str) -> str:
    d = (dest or "").upper()
    if "LIBRARY_3F" in d:
        return "MAP_CANALAVE_CITY_LIBRARY_3F"
    if "LIBRARY_2F" in d:
        return "MAP_CANALAVE_CITY_LIBRARY_2F"
    if "LIBRARY_1F" in d or "LIBRARY" in d:
        return "MAP_CANALAVE_CITY_LIBRARY_1F"
    if "CANALAVE_CITY" in d:
        return "MAP_CANALAVE_CITY"
    return "MAP_CANALAVE_CITY"


def densify_local(em, plat, w, h):
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
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_OLD_MAN")
        label = f"{em}_EventScript_Npc{n}"
        objs.append(obj(gfx, lx, ly, label, movement=face(po.get("initial_dir"))))
        scripts += (
            f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
            f'{label}_Text:\n\t.string "Sinnoh history fills these shelves.$"\n\n'
        )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or ""))
    return objs, scripts, warps


def link_reciprocal(names):
    maps = {n: json.loads((MAPS / n / "map.json").read_text()) for n in names}
    id_to_name = {d["id"]: n for n, d in maps.items()}
    for n, data in maps.items():
        mid = data["id"]
        for w in data.get("warp_events") or []:
            dest = w.get("dest_map")
            if dest == "MAP_CANALAVE_CITY":
                w["dest_warp_id"] = "3"  # library door on city
                continue
            dn = id_to_name.get(dest)
            if not dn:
                w["dest_warp_id"] = "0"
                continue
            back = [i for i, dw in enumerate(maps[dn].get("warp_events") or []) if dw.get("dest_map") == mid]
            w["dest_warp_id"] = str(back[0] if back else 0)
        (MAPS / n / "map.json").write_text(json.dumps(data, indent=2) + "\n")


def scaffold_house(name, mid, plat, text):
    lid, w, h = indoor_room(name, w=12, h=10)
    # Prefer platinum warp/obj coords when the land fits; else stub room
    pe_path = PLAT_MAPS / plat / "events.json"
    objs, scripts = [], f"{name}_MapScripts::\n\t.byte 0\n\n"
    warps = [warp(5, 9, "MAP_CANALAVE_CITY", 0), warp(6, 9, "MAP_CANALAVE_CITY", 0)]
    if pe_path.exists():
        pe = json.loads(pe_path.read_text())
        # indoor events are local; if coords exceed stub, clamp NPC to room
        n = 0
        for po in pe.get("object_events") or []:
            lx = min(max(int(po["x"]), 1), w - 2)
            ly = min(max(int(po["z"]), 1), h - 3)
            gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_MAN_3")
            label = f"{name}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "{text}$"\n\n'
            )
            n += 1
        if not objs:
            objs = [obj("OBJ_EVENT_GFX_MAN_3", 5, 4, f"{name}_EventScript_Npc")]
            scripts += (
                f"{name}_EventScript_Npc::\n\tmsgbox {name}_EventScript_Npc_Text, MSGBOX_NPC\n\tend\n\n"
                f'{name}_EventScript_Npc_Text:\n\t.string "{text}$"\n\n'
            )
    else:
        objs = [obj("OBJ_EVENT_GFX_MAN_3", 5, 4, f"{name}_EventScript_Npc")]
        scripts += (
            f"{name}_EventScript_Npc::\n\tmsgbox {name}_EventScript_Npc_Text, MSGBOX_NPC\n\tend\n\n"
            f'{name}_EventScript_Npc_Text:\n\t.string "{text}$"\n\n'
        )
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": lid,
            "music": "MUS_PL_JUBILIFE",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )
    return name


def main() -> int:
    indoor = []
    for name, chunks, plat, mid, layout in LIBRARY:
        grid, w, h, coll = grid_from_chunks(chunks, cave=False)
        # libraries are indoor — force building tiles if stitch looks outdoor
        write_layout(name, w, h, "gTileset_Building", "gTileset_GenericBuilding", pack(grid, coll), lid=layout)
        objs, scripts, vwarps = densify_local(name, plat, w, h)
        warps = [warp(lx, ly, resolve(dest), 0) for lx, ly, dest in vwarps]
        if not warps:
            sx, sy = find_walkable(grid, prefer=(w // 2, h - 2))
            warps = [warp(sx, sy, "MAP_CANALAVE_CITY", 3)]
        write_map(
            name,
            {
                "id": mid,
                "name": name,
                "layout": layout,
                "music": "MUS_PL_JUBILIFE",
                "region": "REGION_HOENN",
                "region_map_section": "MAPSEC_ROUTE_213",
                "requires_flash": False,
                "weather": "WEATHER_NONE",
                "map_type": "MAP_TYPE_INDOOR",
                "allow_cycling": False,
                "allow_escaping": False,
                "allow_running": True,
                "show_map_name": False,
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

    for name, mid, plat, text in HOUSE_STUBS:
        indoor.append(scaffold_house(name, mid, plat, text))

    # Point city library door at new 1F; wire extra house doors from Platinum city events
    city = json.loads((MAPS / "CanalaveCity" / "map.json").read_text())
    for w in city.get("warp_events") or []:
        if w.get("dest_map") in ("MAP_CANALAVE_CITY_LIBRARY", "MAP_CANALAVE_CITY_LIBRARY_1F"):
            w["dest_map"] = "MAP_CANALAVE_CITY_LIBRARY_1F"
            w["dest_warp_id"] = "0"
    # Add missing house warps from platinum if Emerald is short
    pe = json.loads((PLAT_MAPS / "canalave_city" / "events.json").read_text())
    ox, oz = 1 * 32, 22 * 32  # CanalaveCity documented origin (32, 704)
    existing = {(w["x"], w["y"]) for w in city.get("warp_events") or []}
    house_dests = {
        "MAP_HEADER_CANALAVE_CITY_WEST_HOUSE": "MAP_CANALAVE_CITY_HOUSE2",
        "MAP_HEADER_CANALAVE_CITY_EAST_HOUSE": "MAP_CANALAVE_CITY_HOUSE3",
        "MAP_HEADER_CANALAVE_CITY_SOUTHEAST_HOUSE": "MAP_CANALAVE_CITY_HOUSE4",
        "MAP_HEADER_CANALAVE_CITY_HARBOR_INN": "MAP_CANALAVE_CITY_HARBOR_INN",
        "MAP_HEADER_CANALAVE_CITY_SAILOR_ELDRITCH_HOUSE": "MAP_CANALAVE_CITY_ELDRITCH_HOUSE",
    }
    for pw in pe.get("warp_events") or []:
        dest = pw.get("dest_header_id") or ""
        if dest not in house_dests:
            continue
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if (lx, ly) in existing:
            # retarget if currently House1 or missing
            for w in city["warp_events"]:
                if w["x"] == lx and w["y"] == ly and w.get("dest_map") in ("MAP_CANALAVE_CITY_HOUSE1", "MAP_DYNAMIC"):
                    w["dest_map"] = house_dests[dest]
            continue
        if 0 <= lx < 64 and 0 <= ly < 64:
            city.setdefault("warp_events", []).append(warp(lx, ly, house_dests[dest], 0))
            existing.add((lx, ly))
    (MAPS / "CanalaveCity" / "map.json").write_text(json.dumps(city, indent=2) + "\n")

    link_reciprocal([n for n in indoor if "Library" in n])
    register_maps([], indoor, "gMapGroup_IndoorM37Canalave")
    scrub(indoor + ["CanalaveCity"])
    print("M37 Canalave library + interiors build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
