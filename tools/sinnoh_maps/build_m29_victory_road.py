#!/usr/bin/env python3
"""
M28 / Victory Road + League approach (ends at Elite Four door).

Land IDs:
  Route223              [[92],[93],[94],[95]]     32x128 origin (832, 608)
  PokemonLeagueExterior [[114],[113]]             32x64  origin (832, 544)
  VictoryRoad_Sinnoh_1F [[407,408],[409,410],[411,412]] 64x96
  VictoryRoad_Sinnoh_2F [[413,414],[415,416]]     64x64
  VictoryRoad_Sinnoh_B1F [[417,418],[419,420]]    64x64

Soft-closes Elite Four interiors (door NPC). Emerald tiles only.
"""
from __future__ import annotations

import json
import re
import struct
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
    indoor_room,
    obj,
    pack,
    register_maps,
    scrub,
    warp,
    write_layout,
    write_map,
    IN_DOOR,
    IN_FLOOR,
    IN_WALL,
)

ROUTE223 = [[92], [93], [94], [95]]
LEAGUE = [[114], [113]]
VR1 = [[407, 408], [409, 410], [411, 412]]
VR2 = [[413, 414], [415, 416]]
VRB = [[417, 418], [419, 420]]
R223_ORIGIN = (26 * 32, 19 * 32)  # 832, 608
LEAGUE_ORIGIN = (26 * 32, 17 * 32)  # 832, 544


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
        gfx_src = po.get("graphics_id") or ""
        gfx = GFX_DEFAULT.get(gfx_src, "OBJ_EVENT_GFX_SWIMMER_M" if "SWIM" in gfx_src.upper() else "OBJ_EVENT_GFX_MAN_5")
        if tr.get("id"):
            tid = tr["id"] if str(tr["id"]).startswith("TRAINER_") else f"TRAINER_{tr['id']}"
            tid = re.sub(r"[^A-Z0-9_]", "_", tid.upper())
            if not tid.startswith("TRAINER_"):
                tid = "TRAINER_" + tid
            ensure_trainer(
                tid,
                level,
                "Swimmer M",
                "Swimmer M",
                [("Gyarados", level), ("Floatzel", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title(),
                tag="Sinnoh VR",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(
                obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2), movement=face(po.get("initial_dir")))
            )
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f"{label}_Intro:\n\t.string \"Surf's up on the League approach!$\"\n\n"
                f'{label}_Defeat:\n\t.string "Washed out.$"\n\n'
                f'{label}_After:\n\t.string "Victory Road is through the caves ahead.$"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "The Pokemon League waits at the summit.\\n"\n'
                f'\t.string "Only trainers with eight badges pass.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or "", pw.get("id") or ""))
    return objs, scripts, warps


def densify_local(em, plat, w, h, level):
    """Victory Road uses local coords in events.json (not world matrix)."""
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
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_HIKER")
        if tr.get("id"):
            tid = tr["id"] if str(tr["id"]).startswith("TRAINER_") else f"TRAINER_{tr['id']}"
            tid = re.sub(r"[^A-Z0-9_]", "_", tid.upper())
            if not tid.startswith("TRAINER_"):
                tid = "TRAINER_" + tid
            ensure_trainer(
                tid,
                level,
                "Hiker",
                "Hiker",
                [("Onix", level), ("Graveler", max(1, level - 1))],
                display_name=tid.split("_")[-1][:10].title(),
                tag="Sinnoh VR",
            )
            label = f"{em}_EventScript_Tr{n}"
            objs.append(obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2)))
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f'{label}_Intro:\n\t.string "Victory Road sorts the serious trainers!$"\n\n'
                f'{label}_Defeat:\n\t.string "Solid work.$"\n\n'
                f'{label}_After:\n\t.string "The League door is just beyond.$"\n\n'
            )
        else:
            label = f"{em}_EventScript_Npc{n}"
            objs.append(obj(gfx, lx, ly, label))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f'{label}_Text:\n\t.string "Bring Repels. These tunnels are long.$"\n\n'
            )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw.get("dest_header_id") or "", pw.get("id") or ""))
    return objs, scripts, warps


def clear_blocked(name):
    import tools.sinnoh_maps.platinum_1to1_audit as a
    from importlib import reload

    reload(a)
    if name not in a.LAND_TABLE:
        return
    chunks = a.LAND_TABLE[name]
    pcol, pbeh, pw, ph = a.plat_grid(chunks)
    em, ew, eh = a.load_em_grid(name)
    data = bytearray((Path("data/layouts") / name / "map.bin").read_bytes())
    w = ew
    for y in range(min(eh, ph)):
        for x in range(min(ew, pw)):
            mt = em[y][x]
            if pcol[y][x] == 0 and a.em_solid(mt) and mt not in a.WATER_MT | a.TALL_GRASS_MT | a.SAND_MT | {0x001, 0x121}:
                struct.pack_into("<H", data, (y * w + x) * 2, 0x001)
    (Path("data/layouts") / name / "map.bin").write_bytes(data)


def indoor_stub(name, mid, exit_map, exit_wid, text):
    grid = [
        [IN_WALL if y in (0, 7) or x in (0, 9) else (IN_DOOR if y == 7 and x in (4, 5) else IN_FLOOR) for x in range(10)]
        for y in range(8)
    ]
    write_layout(name, 10, 8, "gTileset_Building", "gTileset_GenericBuilding", pack(grid))
    write_map(
        name,
        {
            "id": mid,
            "name": name,
            "layout": "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z0-9])", "_", name).upper().replace("__", "_").replace("_1_F", "_1F"),
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
            "object_events": [obj("OBJ_EVENT_GFX_NURSE", 4, 3, f"{name}_EventScript_Npc")],
            "warp_events": [warp(4, 7, exit_map, exit_wid), warp(5, 7, exit_map, exit_wid)],
            "coord_events": [],
            "bg_events": [],
        },
        f"{name}_MapScripts::\n\t.byte 0\n\n{name}_EventScript_Npc::\n\tmsgbox {name}_Text, MSGBOX_NPC\n\tend\n\n"
        f'{name}_Text:\n\t.string "{text}"\n',
    )
    # Fix layout id to match write_layout's actual id
    mj = json.loads((MAPS / name / "map.json").read_text())
    # read last layout entry for this name
    layouts = json.loads((Path("data/layouts/layouts.json")).read_text())["layouts"]
    for L in layouts:
        if L.get("name") == f"{name}_Layout":
            mj["layout"] = L["id"]
            break
    (MAPS / name / "map.json").write_text(json.dumps(mj, indent=2) + "\n")


def main():
    ensure_flag("FLAG_REACHED_POKEMON_LEAGUE_DOOR", "0x2B6", "Sinnoh VR reached League door")

    # --- Route 223 ---
    grid, w, h = grid_from_chunks(ROUTE223)
    clear_plat_walkables(grid, ROUTE223)
    # Mostly water route — paint water already done
    write_layout("Route223", w, h, "gTileset_General", "gTileset_Dewford", pack(grid))
    objs, scripts, _ = densify("Route223", "route_223", R223_ORIGIN, w, h, 45)
    write_map(
        "Route223",
        {
            "id": "MAP_ROUTE223",
            "name": "Route223",
            "layout": "LAYOUT_ROUTE223",
            "music": "MUS_ROUTE110",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_ROUTE",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": [
                {"map": "MAP_SUNYSHORE_CITY", "offset": 0, "direction": "down"},
                {"map": "MAP_POKEMON_LEAGUE_EXTERIOR", "offset": 0, "direction": "up"},
            ],
            "object_events": objs,
            "warp_events": [],
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # --- Pokemon League exterior ---
    grid, w, h = grid_from_chunks(LEAGUE)
    clear_plat_walkables(grid, LEAGUE)
    write_layout("PokemonLeague_Exterior", w, h, "gTileset_General", "gTileset_Fortree", pack(grid))
    objs, scripts, plat_warps = densify("PokemonLeague_Exterior", "pokemon_league", LEAGUE_ORIGIN, w, h, 48)
    # Soft-close Elite Four door
    door_x, door_y = find_walkable(grid, prefer=(w // 2, 8))
    for lx, ly, dest, wid in plat_warps:
        if "NORTH_POKECENTER" in dest or "POKECENTER" in dest and "NORTH" in dest:
            door_x, door_y = lx, ly
            break
    objs.append(obj("OBJ_EVENT_GFX_MAN_2", door_x, max(1, door_y + 1), "PokemonLeague_Exterior_EventScript_E4Closed"))
    scripts += (
        "PokemonLeague_Exterior_EventScript_E4Closed::\n"
        "\tlock\n\tfaceplayer\n"
        "\tsetflag FLAG_REACHED_POKEMON_LEAGUE_DOOR\n"
        "\tmsgbox PokemonLeague_Exterior_Text_E4Closed, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        'PokemonLeague_Exterior_Text_E4Closed:\n\t.string "The Elite Four hall is sealed for now.\\n"\n'
        '\t.string "You have reached the League door —\\l"\n'
        '\t.string "the challenge opens in a later chapter.$"\n\n'
    )
    # Warps: south PC, north PC (closed via NPC), VR entrances
    warps = []
    indoor_names = []
    for i, (lx, ly, dest, wid) in enumerate(plat_warps):
        if "VICTORY_ROAD" in dest:
            warps.append(warp(lx, ly, "MAP_VICTORY_ROAD_SINNOH_1F", min(i, 2)))
        elif "SOUTH_POKECENTER" in dest:
            warps.append(warp(lx, ly, "MAP_POKEMON_LEAGUE_SOUTH_PC", 0))
        elif "NORTH_POKECENTER" in dest:
            # Point to stub that soft-closes E4
            warps.append(warp(lx, ly, "MAP_POKEMON_LEAGUE_NORTH_PC", 0))
        else:
            warps.append(warp(lx, ly, "MAP_POKEMON_LEAGUE_SOUTH_PC", 0))

    write_map(
        "PokemonLeague_Exterior",
        {
            "id": "MAP_POKEMON_LEAGUE_EXTERIOR",
            "name": "PokemonLeague_Exterior",
            "layout": "LAYOUT_POKEMON_LEAGUE_EXTERIOR",
            "music": "MUS_VICTORY_ROAD",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_213",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_CITY",
            "allow_cycling": True,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": [
                {"map": "MAP_ROUTE223", "offset": 0, "direction": "down"},
            ],
            "object_events": objs,
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    indoor_stub(
        "PokemonLeague_SouthPC",
        "MAP_POKEMON_LEAGUE_SOUTH_PC",
        "MAP_POKEMON_LEAGUE_EXTERIOR",
        0,
        "League Pokemon Center (south). Rest before Victory Road.$",
    )
    indoor_stub(
        "PokemonLeague_NorthPC",
        "MAP_POKEMON_LEAGUE_NORTH_PC",
        "MAP_POKEMON_LEAGUE_EXTERIOR",
        1,
        "The Elite Four entrance is closed for this build.\\nYou made it to the League door — well fought.$",
    )
    indoor_names += ["PokemonLeague_SouthPC", "PokemonLeague_NorthPC"]

    # --- Victory Road floors ---
    # 1F
    grid, w, h = grid_from_chunks(VR1, cave=True)
    clear_plat_walkables(grid, VR1, cave=True)
    write_layout("VictoryRoad_Sinnoh_1F", w, h, "gTileset_General", "gTileset_Cave", pack(grid))
    objs, scripts, vwarps = densify_local("VictoryRoad_Sinnoh_1F", "victory_road_1f", w, h, 46)
    warps = []
    for lx, ly, dest, wid in vwarps:
        if "2F" in dest:
            warps.append(warp(lx, ly, "MAP_VICTORY_ROAD_SINNOH_2F", 0))
        elif "B1F" in dest:
            warps.append(warp(lx, ly, "MAP_VICTORY_ROAD_SINNOH_B1F", 0))
        elif "ROOM" in dest:
            warps.append(warp(lx, ly, "MAP_VICTORY_ROAD_SINNOH_ROOM1", 0))
        elif "POKEMON_LEAGUE" in dest:
            warps.append(warp(lx, ly, "MAP_POKEMON_LEAGUE_EXTERIOR", 2))
        else:
            warps.append(warp(lx, ly, "MAP_POKEMON_LEAGUE_EXTERIOR", 2))
    write_map(
        "VictoryRoad_Sinnoh_1F",
        {
            "id": "MAP_VICTORY_ROAD_SINNOH_1F",
            "name": "VictoryRoad_Sinnoh_1F",
            "layout": "LAYOUT_VICTORY_ROAD_SINNOH_1F",
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
            "warp_events": warps,
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # 2F
    grid, w, h = grid_from_chunks(VR2, cave=True)
    clear_plat_walkables(grid, VR2, cave=True)
    write_layout("VictoryRoad_Sinnoh_2F", w, h, "gTileset_General", "gTileset_Cave", pack(grid))
    objs, scripts, vwarps = densify_local("VictoryRoad_Sinnoh_2F", "victory_road_2f", w, h, 47)
    warps = [warp(lx, ly, "MAP_VICTORY_ROAD_SINNOH_1F", 0) for lx, ly, dest, wid in vwarps]
    write_map(
        "VictoryRoad_Sinnoh_2F",
        {
            "id": "MAP_VICTORY_ROAD_SINNOH_2F",
            "name": "VictoryRoad_Sinnoh_2F",
            "layout": "LAYOUT_VICTORY_ROAD_SINNOH_2F",
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
            "warp_events": warps or [warp(w // 2, h - 2, "MAP_VICTORY_ROAD_SINNOH_1F", 0)],
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # B1F
    grid, w, h = grid_from_chunks(VRB, cave=True)
    clear_plat_walkables(grid, VRB, cave=True)
    write_layout("VictoryRoad_Sinnoh_B1F", w, h, "gTileset_General", "gTileset_Cave", pack(grid))
    objs, scripts, vwarps = densify_local("VictoryRoad_Sinnoh_B1F", "victory_road_b1f", w, h, 47)
    warps = [warp(lx, ly, "MAP_VICTORY_ROAD_SINNOH_1F", 0) for lx, ly, dest, wid in vwarps]
    write_map(
        "VictoryRoad_Sinnoh_B1F",
        {
            "id": "MAP_VICTORY_ROAD_SINNOH_B1F",
            "name": "VictoryRoad_Sinnoh_B1F",
            "layout": "LAYOUT_VICTORY_ROAD_SINNOH_B1F",
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
            "warp_events": warps or [warp(w // 2, h - 2, "MAP_VICTORY_ROAD_SINNOH_1F", 0)],
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # Small room stub
    indoor_stub(
        "VictoryRoad_Sinnoh_Room1",
        "MAP_VICTORY_ROAD_SINNOH_ROOM1",
        "MAP_VICTORY_ROAD_SINNOH_1F",
        0,
        "A side chamber in Victory Road. Dust and echoes.$",
    )
    indoor_names.append("VictoryRoad_Sinnoh_Room1")

    # Open Sunyshore soft-close: add north connection to Route223
    sc = json.loads((MAPS / "SunyshoreCity" / "map.json").read_text())
    conns = sc.get("connections") or []
    if not any(c.get("map") == "MAP_ROUTE223" for c in conns):
        conns.append({"map": "MAP_ROUTE223", "offset": 0, "direction": "up"})
    sc["connections"] = conns
    # Update soft-close NPC script text already allows after badge
    (MAPS / "SunyshoreCity" / "map.json").write_text(json.dumps(sc, indent=2) + "\n")

    outdoor = ["Route223", "PokemonLeague_Exterior"]
    # VR caves are underground but in LAND_TABLE for audit - register as indoor group + also towns for Route/League
    cave = ["VictoryRoad_Sinnoh_1F", "VictoryRoad_Sinnoh_2F", "VictoryRoad_Sinnoh_B1F"]
    register_maps(outdoor + cave, indoor_names, "gMapGroup_IndoorM29VictoryRoad")
    scrub(outdoor + cave + indoor_names)
    print("Victory Road / League approach build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
