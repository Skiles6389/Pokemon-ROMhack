#!/usr/bin/env python3
"""
M35: Snowpoint Temple floors 1F–B5F (Regigigas) + deeper Acuity cavern (Uxie).

Land IDs (groups.json):
  Temple 1F–B5F: 477–482
  AcuityCavern:  561

Replaces SnowpointTemple_Stub / AcuityCavern_Stub soft-closes.
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
    ensure_flag,
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

TEMPLE = [
    ("SnowpointTemple_1F", [[477]], "snowpoint_temple_1f", "MAP_SNOWPOINT_TEMPLE_1F", "LAYOUT_SNOWPOINT_TEMPLE_1F"),
    ("SnowpointTemple_B1F", [[478]], "snowpoint_temple_b1f", "MAP_SNOWPOINT_TEMPLE_B1F", "LAYOUT_SNOWPOINT_TEMPLE_B1F"),
    ("SnowpointTemple_B2F", [[479]], "snowpoint_temple_b2f", "MAP_SNOWPOINT_TEMPLE_B2F", "LAYOUT_SNOWPOINT_TEMPLE_B2F"),
    ("SnowpointTemple_B3F", [[480]], "snowpoint_temple_b3f", "MAP_SNOWPOINT_TEMPLE_B3F", "LAYOUT_SNOWPOINT_TEMPLE_B3F"),
    ("SnowpointTemple_B4F", [[481]], "snowpoint_temple_b4f", "MAP_SNOWPOINT_TEMPLE_B4F", "LAYOUT_SNOWPOINT_TEMPLE_B4F"),
    ("SnowpointTemple_B5F", [[482]], "snowpoint_temple_b5f", "MAP_SNOWPOINT_TEMPLE_B5F", "LAYOUT_SNOWPOINT_TEMPLE_B5F"),
]
ACUITY = ("AcuityCavern", [[561]], "acuity_cavern", "MAP_ACUITY_CAVERN", "LAYOUT_ACUITY_CAVERN")


def resolve(dest: str) -> str:
    d = (dest or "").upper()
    pairs = [
        ("SNOWPOINT_TEMPLE_B5F", "MAP_SNOWPOINT_TEMPLE_B5F"),
        ("SNOWPOINT_TEMPLE_B4F", "MAP_SNOWPOINT_TEMPLE_B4F"),
        ("SNOWPOINT_TEMPLE_B3F", "MAP_SNOWPOINT_TEMPLE_B3F"),
        ("SNOWPOINT_TEMPLE_B2F", "MAP_SNOWPOINT_TEMPLE_B2F"),
        ("SNOWPOINT_TEMPLE_B1F", "MAP_SNOWPOINT_TEMPLE_B1F"),
        ("SNOWPOINT_TEMPLE_1F", "MAP_SNOWPOINT_TEMPLE_1F"),
        ("SNOWPOINT_CITY", "MAP_SNOWPOINT_CITY"),
        ("ACUITY_CAVERN", "MAP_ACUITY_CAVERN"),
        ("LAKE_ACUITY", "MAP_LAKE_ACUITY"),
    ]
    for key, mid in pairs:
        if key in d:
            return mid
    return "MAP_SNOWPOINT_CITY"


def densify_local(em: str, plat: str, w: int, h: int):
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
        if "REGIGIGAS" in raw:
            label = f"{em}_EventScript_Regigigas"
            objs.append(obj("OBJ_EVENT_GFX_ITEM_BALL", lx, ly, label, flag="FLAG_DEFEATED_REGIGIGAS_TEMPLE"))
            scripts += f"""
{label}::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_REGIGIGAS_TEMPLE, {label}_Gone
	msgbox {label}_Text, MSGBOX_DEFAULT
	setwildbattle SPECIES_REGIGIGAS, 70
	dowildbattle
	setflag FLAG_DEFEATED_REGIGIGAS_TEMPLE
	release
	end

{label}_Gone::
	msgbox {label}_GoneText, MSGBOX_DEFAULT
	release
	end

{label}_Text:
	.string "The colossal statue stirs...\\n"
	.string "Regigigas awakens!$"

{label}_GoneText:
	.string "The pedestal is empty.$"
"""
        elif "UXIE" in raw:
            label = f"{em}_EventScript_Uxie"
            objs.append(obj("OBJ_EVENT_GFX_ITEM_BALL", lx, ly, label, flag="FLAG_DEFEATED_UXIE_ACUITY"))
            scripts += f"""
{label}::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_UXIE_ACUITY, {label}_Gone
	msgbox {label}_Text, MSGBOX_DEFAULT
	setwildbattle SPECIES_UXIE, 50
	dowildbattle
	setflag FLAG_DEFEATED_UXIE_ACUITY
	release
	end

{label}_Gone::
	msgbox {label}_GoneText, MSGBOX_DEFAULT
	release
	end

{label}_Text:
	.string "A knowing gaze pierces the dark...\\n"
	.string "Uxie appears!$"

{label}_GoneText:
	.string "Only ripples remain on the cavern floor.$"
"""
        elif "POKEBALL" in raw or "ITEM_BALL" in raw or "ITEM" in raw:
            label = f"{em}_EventScript_Item{n}"
            objs.append(obj("OBJ_EVENT_GFX_ITEM_BALL", lx, ly, label))
            scripts += f"{label}::\n\tfinditem ITEM_ULTRA_BALL\n\tend\n\n"
        elif "STRENGTH_BOULDER" in raw or "BOULDER" in raw:
            objs.append(obj("OBJ_EVENT_GFX_PUSHABLE_BOULDER", lx, ly, "EventScript_StrengthBoulder"))
        elif "ROCK_SMASH" in raw or "BREAKABLE" in raw:
            objs.append(obj("OBJ_EVENT_GFX_BREAKABLE_ROCK", lx, ly, "EventScript_RockSmash"))
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement=face(po.get("initial_dir"))))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "Ice seals every stairwell.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or ""))
    return objs, scripts, warps


def retarget_stub(city_map: str, stub_id: str, new_id: str):
    path = MAPS / city_map / "map.json"
    data = json.loads(path.read_text())
    for w in data.get("warp_events") or []:
        if w.get("dest_map") == stub_id:
            w["dest_map"] = new_id
    path.write_text(json.dumps(data, indent=2) + "\n")


def link_reciprocal(names: list[str]):
    """Point each warp at the destination warp that returns to this map."""
    maps = {}
    for n in names:
        p = MAPS / n / "map.json"
        maps[n] = json.loads(p.read_text())
    id_to_name = {d["id"]: n for n, d in maps.items()}
    for n, data in maps.items():
        mid = data["id"]
        for w in data.get("warp_events") or []:
            dest = w.get("dest_map")
            if dest not in id_to_name and dest not in ("MAP_SNOWPOINT_CITY", "MAP_LAKE_ACUITY"):
                # try resolve via known outdoor
                continue
            if dest in ("MAP_SNOWPOINT_CITY", "MAP_LAKE_ACUITY"):
                # outdoor: keep warp 0 / existing city door
                w["dest_warp_id"] = "0" if dest == "MAP_LAKE_ACUITY" else "5" if dest == "MAP_SNOWPOINT_CITY" else "0"
                # Snowpoint temple door is warp index 5/6 on city
                if dest == "MAP_SNOWPOINT_CITY":
                    w["dest_warp_id"] = "5"
                if dest == "MAP_LAKE_ACUITY":
                    w["dest_warp_id"] = "1"
                continue
            dn = id_to_name.get(dest)
            if not dn:
                continue
            ddata = maps[dn]
            # Prefer a warp on dest that points back here
            back = [i for i, dw in enumerate(ddata.get("warp_events") or []) if dw.get("dest_map") == mid]
            if back:
                w["dest_warp_id"] = str(back[0])
            else:
                w["dest_warp_id"] = "0"
        (MAPS / n / "map.json").write_text(json.dumps(data, indent=2) + "\n")



def build_one(name, chunks, plat, mid, layout, *, snow=True):
    grid, w, h = grid_from_chunks(chunks, cave=True, snow=snow)
    write_layout(name, w, h, "gTileset_General", "gTileset_Cave", pack(grid), lid=layout)
    objs, scripts, vwarps = densify_local(name, plat, w, h)
    warps = [warp(lx, ly, resolve(dest), 0) for lx, ly, dest in vwarps]
    if not warps:
        warps = [warp(*find_walkable(grid, prefer=(w // 2, h - 2)), "MAP_SNOWPOINT_CITY", 0)]
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": layout,
            "music": "MUS_RG_POKE_TOWER" if "Temple" in name else "MUS_ABANDONED_SHIP",
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
    return name


def main() -> int:
    ensure_flag("FLAG_DEFEATED_REGIGIGAS_TEMPLE", "0x4A8", "Sinnoh M35 Regigigas at Snowpoint Temple", after="FLAG_DEFEATED_HEATRAN_STARK")
    ensure_flag("FLAG_DEFEATED_UXIE_ACUITY", "0x4A9", "Sinnoh M35 Uxie at Acuity Cavern", after="FLAG_DEFEATED_REGIGIGAS_TEMPLE")

    indoor = []
    for name, chunks, plat, mid, layout in TEMPLE:
        indoor.append(build_one(name, chunks, plat, mid, layout, snow=True))
    indoor.append(build_one(*ACUITY, snow=False))

    retarget_stub("SnowpointCity", "MAP_SNOWPOINT_TEMPLE_STUB", "MAP_SNOWPOINT_TEMPLE_1F")
    retarget_stub("LakeAcuity", "MAP_ACUITY_CAVERN_STUB", "MAP_ACUITY_CAVERN")
    link_reciprocal(indoor)

    register_maps([], indoor, "gMapGroup_IndoorM35Temple")
    scrub(indoor + ["SnowpointCity", "LakeAcuity"])
    print("M35 Snowpoint Temple + Acuity Cavern build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
