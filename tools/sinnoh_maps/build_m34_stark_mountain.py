#!/usr/bin/env python3
"""
M34 Postgame: Stark Mountain (outside + rooms 1–3 / Heatran chamber).

Land IDs:
  StarkMountain_Outside [[172]] origin (736, 224)
  StarkMountain_Room1   [[454, 455]]
  StarkMountain_Room2   [[456,457,458],[459,460,461],[462,463,464]]
  StarkMountain_HeatranRoom [[465]]

Opens Route227 Stark soft-close.
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
    clear_plat_walkables,
    ensure_flag,
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

OUTSIDE = [[172]]
ROOM1 = [[454, 455]]
ROOM2 = [[456, 457, 458], [459, 460, 461], [462, 463, 464]]
HEATRAN = [[465]]
OUT_ORIGIN = (23 * 32, 7 * 32)  # 736, 224


def densify_world(em, plat, origin, w, h, level):
    pe_path = PLAT_MAPS / plat / "events.json"
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    warps = []
    if not pe_path.exists():
        return objs, scripts, warps
    pe = json.loads(pe_path.read_text())
    ox, oz = origin
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"] - ox), int(po["z"] - oz)
        if not (0 <= lx < w and 0 <= ly < h) or (lx, ly) in occupied:
            continue
        occupied.add((lx, ly))
        tr = po.get("trainer") or {}
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_HIKER")
        if tr.get("id"):
            tid = tr["id"] if str(tr["id"]).startswith("TRAINER_") else f"TRAINER_{tr['id']}"
            tid = re.sub(r"[^A-Z0-9_]", "_", tid.upper())
            if not tid.startswith("TRAINER_"):
                tid = "TRAINER_" + tid
            if not tid.endswith("_PG"):
                tid = tid + "_PG"
            ensure_trainer(
                tid,
                level,
                "Hiker",
                "Hiker",
                [("Camerupt", level), ("Rhydon", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title(),
                tag="Sinnoh Stark",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(
                obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2), movement=face(po.get("initial_dir")))
            )
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f'{label}_Intro:\n\t.string "Ash and steel — Stark Mountain!$"\n\n'
                f'{label}_Defeat:\n\t.string "Burned out...$"\n\n'
                f'{label}_After:\n\t.string "Heatran sleeps deeper inside.$"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "The mountain breathes fire and ash.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or ""))
    return objs, scripts, warps


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
        tr = po.get("trainer") or {}
        raw_gfx = po.get("graphics_id") or ""
        gfx = GFX_DEFAULT.get(raw_gfx, "OBJ_EVENT_GFX_HIKER")
        # Field objects / items must keep Emerald gfx so 1:1 audit class matches Platinum
        ug = raw_gfx.upper()
        if "POKEBALL" in ug or "ITEM_BALL" in ug or "ITEM" in ug:
            gfx = "OBJ_EVENT_GFX_ITEM_BALL"
            label = f"{em}_EventScript_Item{n}"
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += f"{label}::\n\tfinditem ITEM_ULTRA_BALL\n\tend\n\n"
        elif "STRENGTH_BOULDER" in ug or "BOULDER" in ug:
            gfx = "OBJ_EVENT_GFX_PUSHABLE_BOULDER"
            label = f"{em}_EventScript_Boulder{n}"
            objs.append(obj(gfx, lx, ly, "EventScript_StrengthBoulder", movement="MOVEMENT_TYPE_FACE_DOWN"))
            scripts += ""  # shared Strength script
        elif "ROCK_SMASH" in ug or "BREAKABLE" in ug:
            gfx = "OBJ_EVENT_GFX_BREAKABLE_ROCK"
            label = f"{em}_EventScript_Rock{n}"
            objs.append(obj(gfx, lx, ly, "EventScript_RockSmash", movement="MOVEMENT_TYPE_FACE_DOWN"))
            scripts += ""
        elif tr.get("id"):
            tid = tr["id"] if str(tr["id"]).startswith("TRAINER_") else f"TRAINER_{tr['id']}"
            tid = re.sub(r"[^A-Z0-9_]", "_", tid.upper())
            if not tid.startswith("TRAINER_"):
                tid = "TRAINER_" + tid
            if not tid.endswith("_PG"):
                tid = tid + "_PG"
            ensure_trainer(
                tid,
                level,
                "Hiker",
                "Hiker",
                [("Camerupt", level), ("Magcargo", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title(),
                tag="Sinnoh Stark",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2)))
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f'{label}_Intro:\n\t.string "This cave forges champions!$"\n\n'
                f'{label}_Defeat:\n\t.string "Tempered...$"\n\n'
                f'{label}_After:\n\t.string "Deeper still - watch the heat.$"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "Lava light paints the walls.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or ""))
    return objs, scripts, warps


def resolve(dest: str) -> str:
    d = dest.upper()
    if "OUTSIDE" in d:
        return "MAP_STARK_MOUNTAIN_OUTSIDE"
    if "ROOM_2" in d or "ROOM2" in d:
        return "MAP_STARK_MOUNTAIN_ROOM2"
    if "ROOM_3" in d or "ROOM3" in d or "HEATRAN" in d:
        return "MAP_STARK_MOUNTAIN_HEATRAN_ROOM"
    if "ROOM_1" in d or "ROOM1" in d:
        return "MAP_STARK_MOUNTAIN_ROOM1"
    if "ROUTE_227" in d:
        return "MAP_ROUTE227"
    return "MAP_STARK_MOUNTAIN_OUTSIDE"


def open_route227():
    path = MAPS / "Route227" / "map.json"
    data = json.loads(path.read_text())
    objs = []
    for o in data.get("object_events") or []:
        if o.get("script") == "Route227_EventScript_StarkClosed":
            continue  # remove soft-close
        objs.append(o)
    data["object_events"] = objs
    # Platinum R227 only has the house warp; Stark Outside is a north matrix connection.
    warps = [w for w in (data.get("warp_events") or []) if w.get("dest_map") != "MAP_STARK_MOUNTAIN_OUTSIDE"]
    data["warp_events"] = warps
    conns = data.get("connections") or []
    if not any(c.get("map") == "MAP_STARK_MOUNTAIN_OUTSIDE" for c in conns):
        conns.append({"map": "MAP_STARK_MOUNTAIN_OUTSIDE", "offset": 0, "direction": "up"})
    data["connections"] = conns
    path.write_text(json.dumps(data, indent=2) + "\n")
    scripts = (MAPS / "Route227" / "scripts.inc").read_text()
    # strip closed scripts if present
    if "StarkClosed" in scripts:
        lines = scripts.splitlines()
        out, skip = [], False
        for line in lines:
            if "StarkClosed" in line or "StarkClosed" in line or line.startswith("Route227_Text_StarkClosed"):
                skip = True
            if skip:
                if line.startswith("Route227_") and "StarkClosed" not in line and "Text_Stark" not in line:
                    skip = False
                    out.append(line)
                continue
            out.append(line)
        # simpler: rewrite without closed blocks
        scripts = re.sub(
            r"Route227_EventScript_StarkClosed::.*?Route227_Text_StarkClosed:.*?\$\"\n",
            "",
            scripts,
            flags=re.S,
        )
    (MAPS / "Route227" / "scripts.inc").write_text(scripts)


def main() -> int:
    ensure_flag("FLAG_DEFEATED_HEATRAN_STARK", "0x4A7", "Sinnoh M34 Heatran at Stark", after="FLAG_LAKE_VALOR_DRAINED")
    open_route227()

    # Outside
    grid, w, h = grid_from_chunks(OUTSIDE, snow=False)
    clear_plat_walkables(grid, OUTSIDE)
    write_layout("StarkMountain_Outside", w, h, "gTileset_General", "gTileset_Petalburg", pack(grid))
    objs, scripts, vwarps = densify_world("StarkMountain_Outside", "stark_mountain_outside", OUT_ORIGIN, w, h, 54)
    # Platinum Outside only has the cave mouth warp; R227 is a matrix connection (south).
    warps = [warp(lx, ly, resolve(dest), 0) for lx, ly, dest in vwarps if "ROUTE_227" not in (dest or "").upper()]
    write_map(
        "StarkMountain_Outside",
        {
            "id": "MAP_STARK_MOUNTAIN_OUTSIDE",
            "name": "StarkMountain_Outside",
            "layout": "LAYOUT_STARK_MOUNTAIN_OUTSIDE",
            "music": "MUS_RG_ROUTE1",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_VOLCANIC_ASH",
            "map_type": "MAP_TYPE_ROUTE",
            "allow_cycling": True,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": [{"map": "MAP_ROUTE227", "offset": 0, "direction": "down"}],
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    indoor = []
    for name, chunks, plat, mid, layout, level in [
        ("StarkMountain_Room1", ROOM1, "stark_mountain_room_1", "MAP_STARK_MOUNTAIN_ROOM1", "LAYOUT_STARK_MOUNTAIN_ROOM1", 55),
        ("StarkMountain_Room2", ROOM2, "stark_mountain_room_2", "MAP_STARK_MOUNTAIN_ROOM2", "LAYOUT_STARK_MOUNTAIN_ROOM2", 56),
        ("StarkMountain_HeatranRoom", HEATRAN, "stark_mountain_room_3", "MAP_STARK_MOUNTAIN_HEATRAN_ROOM", "LAYOUT_STARK_MOUNTAIN_HEATRAN_ROOM", 57),
    ]:
        grid, w, h = grid_from_chunks(chunks, cave=True)
        clear_plat_walkables(grid, chunks, cave=True)
        write_layout(name, w, h, "gTileset_General", "gTileset_Cave", pack(grid))
        objs, scripts, vwarps = densify_local(name, plat, w, h, level)
        warps = [warp(lx, ly, resolve(dest), 0) for lx, ly, dest in vwarps]
        if name.endswith("HeatranRoom"):
            # Place Heatran encounter NPC
            hx, hy = find_walkable(grid, prefer=(w // 2, h // 2))
            objs.append(obj("OBJ_EVENT_GFX_ITEM_BALL", hx, hy, f"{name}_EventScript_Heatran"))
            scripts += f"""
{name}_EventScript_Heatran::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_HEATRAN_STARK, {name}_EventScript_HeatranGone
	msgbox {name}_Text_Heatran, MSGBOX_DEFAULT
	setwildbattle SPECIES_HEATRAN, 70
	dowildbattle
	setflag FLAG_DEFEATED_HEATRAN_STARK
	release
	end

{name}_EventScript_HeatranGone::
	msgbox {name}_Text_HeatranGone, MSGBOX_DEFAULT
	release
	end

{name}_Text_Heatran:
	.string "A fierce heat wells up from the rock...\\n"
	.string "Heatran appears!$"

{name}_Text_HeatranGone:
	.string "The magma chamber is quiet now.$"
"""
        write_map(
            name,
            {
                "id": mid,
                "name": name,
                "layout": layout,
                "music": "MUS_VICTORY_ROAD",
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
                "warp_events": warps or [warp(w // 2, h - 2, "MAP_STARK_MOUNTAIN_OUTSIDE", 0)],
                "coord_events": [],
                "bg_events": [],
            },
            scripts,
        )
        indoor.append(name)

    outdoor = ["StarkMountain_Outside"]
    register_maps(outdoor, indoor, "gMapGroup_IndoorM34Stark")
    scrub(outdoor + indoor + ["Route227"])
    print("M34 Stark Mountain build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
