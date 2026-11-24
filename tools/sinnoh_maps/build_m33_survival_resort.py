#!/usr/bin/env python3
"""
M33 Postgame: Survival Area, Resort Area, Routes 226–230.

Land IDs / origins (TownsAndRoutes matrix):
  SurvivalArea [[166, 167]]           origin (640, 320)
  Route226     [[None, 171], [168, 169]]  origin (704, 288)
  Route227     [[170], [171], [169]]  origin (736, 256)  # soft-close Stark north
  Route228     [[139], [140], [141]]  origin (768, 320)
  Route229     [[134, 135], [None, 142]] origin (768, 416)
  Route230     [[136, 137, 138]]      origin (672, 416)
  ResortArea   [[135], [142]]         origin (800, 416)

Opens Route225 Survival soft-close → SurvivalArea. Soft-closes Stark on R227 north.
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
    ensure_trainer,
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

SURVIVAL = [[166, 167]]
R226 = [[None, 171], [168, 169]]
R227 = [[170], [171], [169]]
R228 = [[139], [140], [141]]
R229 = [[134, 135], [None, 142]]
R230 = [[136, 137, 138]]
RESORT = [[135], [142]]

SURVIVAL_ORIGIN = (20 * 32, 10 * 32)  # 640, 320
R226_ORIGIN = (22 * 32, 9 * 32)  # 704, 288
R227_ORIGIN = (23 * 32, 8 * 32)  # 736, 256
R228_ORIGIN = (24 * 32, 10 * 32)  # 768, 320
R229_ORIGIN = (24 * 32, 13 * 32)  # 768, 416
R230_ORIGIN = (21 * 32, 13 * 32)  # 672, 416
RESORT_ORIGIN = (25 * 32, 13 * 32)  # 800, 416


def densify(em, plat, origin, w, h, level):
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
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_MAN_5")
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
                "Cooltrainer",
                "Cooltrainer M",
                [("Floatzel", level), ("Luxray", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title(),
                tag="Sinnoh Postgame",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(
                obj(
                    gfx,
                    lx,
                    ly,
                    label,
                    trainer="TRAINER_TYPE_NORMAL",
                    sight=str(tr.get("sight_range") or 2),
                    movement=face(po.get("initial_dir")),
                )
            )
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f'{label}_Intro:\n\t.string "Battle Zone trainers train hard!$"\n\n'
                f'{label}_Defeat:\n\t.string "Down...$"\n\n'
                f'{label}_After:\n\t.string "Keep pushing toward Stark Mountain.$"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "The Battle Zone stretches across these routes.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or ""))
    return objs, scripts, warps


def resolve_dest(dest: str) -> str | None:
    d = dest.upper()
    mapping = [
        ("SURVIVAL_AREA_POKECENTER", "MAP_SURVIVAL_AREA_POKEMON_CENTER_1F"),
        ("SURVIVAL_AREA_MART", "MAP_SURVIVAL_AREA_MART"),
        ("SURVIVAL_AREA_SOUTH_HOUSE", "MAP_SURVIVAL_AREA_SOUTH_HOUSE"),
        ("SURVIVAL_AREA_NORTH_HOUSE", "MAP_SURVIVAL_AREA_NORTH_HOUSE"),
        ("BATTLEGROUND", "MAP_SURVIVAL_AREA"),  # stub self until dedicated map
        ("RESORT_AREA_POKECENTER", "MAP_RESORT_AREA_POKEMON_CENTER_1F"),
        ("RESORT_AREA_HOUSE", "MAP_RESORT_AREA_HOUSE"),
        ("RESORT_AREA_RIBBON", "MAP_RESORT_AREA_RIBBON_SYNDICATE"),
        ("VILLA", "MAP_RESORT_AREA_VILLA"),
        ("ROUTE_226_HOUSE", "MAP_ROUTE226_HOUSE"),
        ("ROUTE_227_HOUSE", "MAP_ROUTE227_HOUSE"),
        ("ROUTE_228_NORTH_HOUSE", "MAP_ROUTE228_NORTH_HOUSE"),
        ("ROUTE_228_SOUTH_HOUSE", "MAP_ROUTE228_SOUTH_HOUSE"),
        ("ROUTE_228_GATE", "MAP_ROUTE228"),  # skip unbuilt gate → route
        ("ROUTE_228_ROCK_PEAK", None),
        ("ROCK_PEAK_RUINS", None),
        ("STARK_MOUNTAIN", None),  # soft-close later
        ("ROUTE_226", "MAP_ROUTE226"),
        ("ROUTE_227", "MAP_ROUTE227"),
        ("ROUTE_228", "MAP_ROUTE228"),
        ("ROUTE_229", "MAP_ROUTE229"),
        ("ROUTE_230", "MAP_ROUTE230"),
        ("ROUTE_225", "MAP_ROUTE225"),
        ("FIGHT_AREA", "MAP_FIGHT_AREA"),
        ("SURVIVAL_AREA", "MAP_SURVIVAL_AREA"),
        ("RESORT_AREA", "MAP_RESORT_AREA"),
    ]
    for key, mid in mapping:
        if key in d:
            return mid
    return None


def stub_indoor(name, mid, layout, exit_map, exit_wid, line):
    indoor_room(name, w=10, h=8)
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": layout,
            "music": "MUS_POKE_MART" if "Mart" in name else "MUS_RG_PEWTER",
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
            "object_events": [
                obj(
                    "OBJ_EVENT_GFX_MART_EMPLOYEE" if "Mart" in name else "OBJ_EVENT_GFX_MAN_5",
                    4,
                    3,
                    f"{name}_EventScript_Npc",
                )
            ],
            "warp_events": [warp(4, 7, exit_map, exit_wid), warp(5, 7, exit_map, exit_wid)],
            "coord_events": [],
            "bg_events": [],
        },
        f"""{name}_MapScripts::
	.byte 0

{name}_EventScript_Npc::
	msgbox {name}_Text, MSGBOX_NPC
	end

{name}_Text:
	.string "{line}$"
""",
    )
    return name


def stub_pc(name, mid, layout, exit_map, exit_wid):
    indoor_room(name, w=10, h=8)
    nurse = obj("OBJ_EVENT_GFX_NURSE", 4, 3, f"{name}_EventScript_Nurse")
    nurse["local_id"] = "LOCALID_NURSE"
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": layout,
            "music": "MUS_POKE_CENTER",
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
            "object_events": [nurse],
            "warp_events": [warp(4, 7, exit_map, exit_wid), warp(5, 7, exit_map, exit_wid)],
            "coord_events": [],
            "bg_events": [],
        },
        f"""{name}_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, {name}_OnTransition
	.byte 0

{name}_OnTransition::
	setrespawn HEAL_LOCATION_EVER_GRANDE_CITY
	end

{name}_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end
""",
    )
    return name


def write_outdoor(name, mid, layout, chunks, origin, plat, level, connections, music="MUS_RG_ROUTE1", extra_objs=None, extra_scripts=""):
    grid, w, h = grid_from_chunks(chunks)
    clear_plat_walkables(grid, chunks)
    write_layout(name, w, h, "gTileset_General", "gTileset_Petalburg", pack(grid))
    objs, scripts, vwarps = densify(name, plat, origin, w, h, level)
    if extra_objs:
        objs.extend(extra_objs)
    scripts += extra_scripts
    warps = []
    for lx, ly, dest in vwarps:
        dmap = resolve_dest(dest)
        if dmap:
            warps.append(warp(lx, ly, dmap, 0))
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": layout,
            "music": music,
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_ROUTE" if "Route" in name else "MAP_TYPE_TOWN",
            "allow_cycling": True,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": connections,
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )
    return w, h, warps


def open_route225_to_survival():
    """Replace Survival soft-close NPC with a guide + east warp into Survival."""
    path = MAPS / "Route225" / "map.json"
    data = json.loads(path.read_text())
    objs = []
    for o in data.get("object_events") or []:
        if o.get("script") == "Route225_EventScript_SurvivalClosed":
            o = dict(o)
            o["script"] = "Route225_EventScript_SurvivalGuide"
            o["graphics_id"] = "OBJ_EVENT_GFX_MAN_2"
        objs.append(o)
    data["object_events"] = objs
    # Add east-edge warps toward Survival if missing
    warps = data.get("warp_events") or []
    # Place near east center of 64-wide map
    east = [(62, 16, "MAP_SURVIVAL_AREA", 0), (63, 16, "MAP_SURVIVAL_AREA", 0)]
    have = {(w["x"], w["y"]) for w in warps}
    for x, y, dest, wid in east:
        if (x, y) not in have:
            warps.append({"x": x, "y": y, "elevation": 0, "dest_map": dest, "dest_warp_id": str(wid)})
    data["warp_events"] = warps
    # Connection right to Survival (offset so Survival's west aligns)
    conns = data.get("connections") or []
    if not any(c.get("map") == "MAP_SURVIVAL_AREA" for c in conns):
        conns.append({"map": "MAP_SURVIVAL_AREA", "offset": 0, "direction": "right"})
    data["connections"] = conns
    path.write_text(json.dumps(data, indent=2) + "\n")

    scripts = (MAPS / "Route225" / "scripts.inc").read_text()
    scripts = scripts.replace("Route225_EventScript_SurvivalClosed", "Route225_EventScript_SurvivalGuide")
    scripts = scripts.replace(
        "Survival Area opens in a later postgame\\n"
        "\t.string \"build. Train in the Fight Area for now.$\"",
        "Survival Area is east of here.\\n"
        "\t.string \"Routes 226–230 weave through the Battle Zone.$\"",
    )
    if "Route225_EventScript_SurvivalGuide" not in scripts:
        scripts += """
Route225_EventScript_SurvivalGuide::
	msgbox Route225_Text_SurvivalGuide, MSGBOX_NPC
	end

Route225_Text_SurvivalGuide:
	.string "Survival Area is east of here.\\n"
	.string "Routes 226-230 weave through the Battle Zone.$"
"""
    (MAPS / "Route225" / "scripts.inc").write_text(scripts)


def main() -> int:
    open_route225_to_survival()
    indoor = []

    # Survival Area
    sx, sy = 8, 16
    write_outdoor(
        "SurvivalArea",
        "MAP_SURVIVAL_AREA",
        "LAYOUT_SURVIVAL_AREA",
        SURVIVAL,
        SURVIVAL_ORIGIN,
        "survival_area",
        52,
        connections=[
            {"map": "MAP_ROUTE225", "offset": 0, "direction": "left"},
            {"map": "MAP_ROUTE226", "offset": 0, "direction": "right"},
        ],
        music="MUS_RG_PEWTER",
    )
    # Fix Survival warps to indoor stubs — rebuild warps with known indices
    sa = json.loads((MAPS / "SurvivalArea" / "map.json").read_text())
    # densify already placed plat warps; ensure indoors exist
    indoor += [
        stub_pc("SurvivalArea_PokemonCenter_1F", "MAP_SURVIVAL_AREA_POKEMON_CENTER_1F", "LAYOUT_SURVIVAL_AREA_POKEMON_CENTER_1_F", "MAP_SURVIVAL_AREA", 0),
        stub_indoor("SurvivalArea_Mart", "MAP_SURVIVAL_AREA_MART", "LAYOUT_SURVIVAL_AREA_MART", "MAP_SURVIVAL_AREA", 0, "Stock up before Stark Mountain."),
        stub_indoor("SurvivalArea_SouthHouse", "MAP_SURVIVAL_AREA_SOUTH_HOUSE", "LAYOUT_SURVIVAL_AREA_SOUTH_HOUSE", "MAP_SURVIVAL_AREA", 0, "Survivors gather here between matches."),
        stub_indoor("SurvivalArea_NorthHouse", "MAP_SURVIVAL_AREA_NORTH_HOUSE", "LAYOUT_SURVIVAL_AREA_NORTH_HOUSE", "MAP_SURVIVAL_AREA", 0, "North house overlooking Route 226."),
    ]

    # Route 226
    write_outdoor(
        "Route226",
        "MAP_ROUTE226",
        "LAYOUT_ROUTE226",
        R226,
        R226_ORIGIN,
        "route_226",
        52,
        connections=[
            {"map": "MAP_SURVIVAL_AREA", "offset": 0, "direction": "left"},
            {"map": "MAP_ROUTE227", "offset": 0, "direction": "up"},
            {"map": "MAP_ROUTE228", "offset": 0, "direction": "right"},
        ],
    )
    indoor.append(stub_indoor("Route226_House", "MAP_ROUTE226_HOUSE", "LAYOUT_ROUTE226_HOUSE", "MAP_ROUTE226", 0, "Waves crash below the cliff houses."))

    # Route 227 — soft-close Stark north
    grid, w, h = grid_from_chunks(R227)
    clear_plat_walkables(grid, R227)
    write_layout("Route227", w, h, "gTileset_General", "gTileset_Petalburg", pack(grid))
    objs, scripts, vwarps = densify("Route227", "route_227", R227_ORIGIN, w, h, 53)
    nx, ny = find_walkable(grid, prefer=(w // 2, 1))
    objs.append(obj("OBJ_EVENT_GFX_MAN_2", nx, ny, "Route227_EventScript_StarkClosed", movement="MOVEMENT_TYPE_FACE_DOWN"))
    scripts += """
Route227_EventScript_StarkClosed::
	lock
	faceplayer
	msgbox Route227_Text_StarkClosed, MSGBOX_DEFAULT
	release
	end

Route227_Text_StarkClosed:
	.string "Stark Mountain opens in the next build.\\n"
	.string "Ashfall already marks the path.$"
"""
    warps = []
    for lx, ly, dest in vwarps:
        dmap = resolve_dest(dest)
        if dmap:
            warps.append(warp(lx, ly, dmap, 0))
    write_map(
        "Route227",
        {
            "id": "MAP_ROUTE227",
            "name": "Route227",
            "layout": "LAYOUT_ROUTE227",
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
            "connections": [
                {"map": "MAP_ROUTE226", "offset": 0, "direction": "down"},
            ],
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )
    indoor.append(stub_indoor("Route227_House", "MAP_ROUTE227_HOUSE", "LAYOUT_ROUTE227_HOUSE", "MAP_ROUTE227", 0, "Ash settles on every windowsill."))

    # Route 228
    write_outdoor(
        "Route228",
        "MAP_ROUTE228",
        "LAYOUT_ROUTE228",
        R228,
        R228_ORIGIN,
        "route_228",
        52,
        connections=[
            {"map": "MAP_ROUTE226", "offset": 0, "direction": "left"},
            {"map": "MAP_ROUTE229", "offset": 0, "direction": "down"},
        ],
    )
    indoor += [
        stub_indoor("Route228_NorthHouse", "MAP_ROUTE228_NORTH_HOUSE", "LAYOUT_ROUTE228_NORTH_HOUSE", "MAP_ROUTE228", 0, "Northern desert house."),
        stub_indoor("Route228_SouthHouse", "MAP_ROUTE228_SOUTH_HOUSE", "LAYOUT_ROUTE228_SOUTH_HOUSE", "MAP_ROUTE228", 0, "Southern desert house."),
    ]

    # Route 229
    write_outdoor(
        "Route229",
        "MAP_ROUTE229",
        "LAYOUT_ROUTE229",
        R229,
        R229_ORIGIN,
        "route_229",
        52,
        connections=[
            {"map": "MAP_ROUTE228", "offset": 0, "direction": "up"},
            {"map": "MAP_ROUTE230", "offset": 0, "direction": "left"},
            {"map": "MAP_RESORT_AREA", "offset": 0, "direction": "right"},
        ],
    )

    # Route 230
    write_outdoor(
        "Route230",
        "MAP_ROUTE230",
        "LAYOUT_ROUTE230",
        R230,
        R230_ORIGIN,
        "route_230",
        52,
        connections=[
            {"map": "MAP_ROUTE229", "offset": 0, "direction": "right"},
            {"map": "MAP_FIGHT_AREA", "offset": 0, "direction": "left"},
        ],
    )

    # Resort Area
    write_outdoor(
        "ResortArea",
        "MAP_RESORT_AREA",
        "LAYOUT_RESORT_AREA",
        RESORT,
        RESORT_ORIGIN,
        "resort_area",
        50,
        connections=[
            {"map": "MAP_ROUTE229", "offset": 0, "direction": "left"},
        ],
        music="MUS_RG_PEWTER",
    )
    indoor += [
        stub_pc("ResortArea_PokemonCenter_1F", "MAP_RESORT_AREA_POKEMON_CENTER_1F", "LAYOUT_RESORT_AREA_POKEMON_CENTER_1_F", "MAP_RESORT_AREA", 0),
        stub_indoor("ResortArea_House", "MAP_RESORT_AREA_HOUSE", "LAYOUT_RESORT_AREA_HOUSE", "MAP_RESORT_AREA", 0, "A quiet resort cottage."),
        stub_indoor("ResortArea_Villa", "MAP_RESORT_AREA_VILLA", "LAYOUT_RESORT_AREA_VILLA", "MAP_RESORT_AREA", 0, "The villa waits for a famous guest."),
        stub_indoor(
            "ResortArea_RibbonSyndicate",
            "MAP_RESORT_AREA_RIBBON_SYNDICATE",
            "LAYOUT_RESORT_AREA_RIBBON_SYNDICATE",
            "MAP_RESORT_AREA",
            0,
            "Ribbon Syndicate counter — open later.",
        ),
    ]

    outdoor = ["SurvivalArea", "Route226", "Route227", "Route228", "Route229", "Route230", "ResortArea"]
    register_maps(outdoor, indoor, "gMapGroup_IndoorM33SurvivalResort")
    scrub(outdoor + indoor + ["Route225"])
    print("M33 Survival/Resort/routes build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
