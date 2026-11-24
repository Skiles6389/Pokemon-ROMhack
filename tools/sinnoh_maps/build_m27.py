#!/usr/bin/env python3
"""
M27: Distortion World / Giratina (Platinum order after Spear Pillar).

Land matrices (groups.json):
  SpearPillar_Distorted  [[379,380],[381,382]]  64x64
  DistortionWorld_1F     [[598,599],[600,601]]  64x64
  DistortionWorld_B1F    [[602,603]]            64x32
  DistortionWorld_B2F    [[604,605],[606,607]]  64x64
  DistortionWorld_B3F    [[608,609],[610,611]]  64x64
  DistortionWorld_B4F    [[612,613],[614,615]]  64x64
  DistortionWorld_B5F    [[620,621],[622,623]]  64x64
  DistortionWorld_B6F    [[624,625],[626,627]]  64x64
  DistortionWorld_B7F    [[628],[629]]          32x64
  DistortionWorld_GiratinaRoom [[630]]          32x32
  DistortionWorld_TurnbackCaveRoom [[631,632],[633,634]] 64x64

Emerald tiles only. Original dialogue. Trainer IVs 0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinnoh_build_lib import (  # noqa: E402
    MAPS,
    GFX_DEFAULT,
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

FLOORS = [
    ("SpearPillar_Distorted", [[379, 380], [381, 382]], "spear_pillar_distorted", False),
    ("DistortionWorld_1F", [[598, 599], [600, 601]], "distortion_world_1f", True),
    ("DistortionWorld_B1F", [[602, 603]], "distortion_world_b1f", True),
    ("DistortionWorld_B2F", [[604, 605], [606, 607]], "distortion_world_b2f", True),
    ("DistortionWorld_B3F", [[608, 609], [610, 611]], "distortion_world_b3f", True),
    ("DistortionWorld_B4F", [[612, 613], [614, 615]], "distortion_world_b4f", True),
    ("DistortionWorld_B5F", [[620, 621], [622, 623]], "distortion_world_b5f", True),
    ("DistortionWorld_B6F", [[624, 625], [626, 627]], "distortion_world_b6f", True),
    ("DistortionWorld_B7F", [[628], [629]], "distortion_world_b7f", True),
    ("DistortionWorld_GiratinaRoom", [[630]], "distortion_world_giratina_room", True),
    ("DistortionWorld_TurnbackCaveRoom", [[631, 632], [633, 634]], "distortion_world_turnback_cave_room", True),
]

# Linear play order for warps (skip unused B4 unused floor 616-619)
PATH = [
    "SpearPillar_Distorted",
    "DistortionWorld_1F",
    "DistortionWorld_B1F",
    "DistortionWorld_B2F",
    "DistortionWorld_B3F",
    "DistortionWorld_B4F",
    "DistortionWorld_B5F",
    "DistortionWorld_B6F",
    "DistortionWorld_B7F",
    "DistortionWorld_GiratinaRoom",
    "DistortionWorld_TurnbackCaveRoom",
]


def mid(name: str) -> str:
    explicit = {
        "SpearPillar_Distorted": "MAP_SPEAR_PILLAR_DISTORTED",
        "DistortionWorld_1F": "MAP_DISTORTION_WORLD_1F",
        "DistortionWorld_B1F": "MAP_DISTORTION_WORLD_B1F",
        "DistortionWorld_B2F": "MAP_DISTORTION_WORLD_B2F",
        "DistortionWorld_B3F": "MAP_DISTORTION_WORLD_B3F",
        "DistortionWorld_B4F": "MAP_DISTORTION_WORLD_B4F",
        "DistortionWorld_B5F": "MAP_DISTORTION_WORLD_B5F",
        "DistortionWorld_B6F": "MAP_DISTORTION_WORLD_B6F",
        "DistortionWorld_B7F": "MAP_DISTORTION_WORLD_B7F",
        "DistortionWorld_GiratinaRoom": "MAP_DISTORTION_WORLD_GIRATINA_ROOM",
        "DistortionWorld_TurnbackCaveRoom": "MAP_DISTORTION_WORLD_TURNBACK_CAVE_ROOM",
    }
    return explicit[name]


def layout_id(name: str) -> str:
    return mid(name).replace("MAP_", "LAYOUT_")


def densify_from_plat(em, plat_folder, origin, w, h, level=45):
    from pathlib import Path
    from sinnoh_build_lib import PLAT_MAPS

    pe_path = PLAT_MAPS / plat_folder / "events.json"
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    warps = []
    if not pe_path.exists():
        return objs, warps, scripts
    pe = json.loads(pe_path.read_text())
    ox, oz = origin if origin else (0, 0)
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"] - ox), int(po["z"] - oz)
        if not (0 <= lx < w and 0 <= ly < h) or (lx, ly) in occupied:
            continue
        occupied.add((lx, ly))
        gfx = GFX_DEFAULT.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_MAN_5")
        if "BALL" in (po.get("graphics_id") or "").upper() or "ITEM" in (po.get("graphics_id") or "").upper():
            gfx = "OBJ_EVENT_GFX_ITEM_BALL"
        label = f"{em}_EventScript_Npc{n}"
        objs.append(obj(gfx, lx, ly, label, movement=face(po.get("initial_dir"))))
        scripts += (
            f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
            f'{label}_Text:\n\t.string "Gravity twists. Paths fold.\\n"\n'
            f'\t.string "Keep your bearings somehow.$"\n\n'
        )
        n += 1
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < w and 0 <= ly < h:
            warps.append((lx, ly, pw))
    return objs, warps, scripts


def main():
    ensure_flag("FLAG_DEFEATED_GIRATINA_DISTORTION", "0x2B2", "Sinnoh M27 Giratina")
    ensure_flag("FLAG_ENTERED_DISTORTION_WORLD", "0x2B3", "Sinnoh M27 entered Distortion")
    ensure_flag("FLAG_DISTORTION_WORLD_CLEAR", "0x2B4", "Sinnoh M27 cleared Distortion path")

    built = {}  # name -> (grid, w, h, entry_xy, exit_xy)

    for name, chunks, plat, cave in FLOORS:
        grid, w, h, coll = grid_from_chunks(chunks, cave=cave)
        clear_plat_walkables(grid, chunks, cave=cave)
        primary = "gTileset_General"
        secondary = "gTileset_Cave" if cave else "gTileset_Fortree"
        write_layout(name, w, h, primary, secondary, pack(grid, coll), layout_id(name))
        entry = find_walkable(grid, prefer=(w // 2, h - 3))
        exit_ = find_walkable(grid, prefer=(w // 2, 3))
        if entry == exit_:
            exit_ = find_walkable(grid, prefer=(w // 2 + 2, 3))
        built[name] = (grid, w, h, entry, exit_, plat, cave)

    # Build maps with linear warps along PATH
    outdoor_names = []
    indoor_names = []
    for i, name in enumerate(PATH):
        grid, w, h, entry, exit_, plat, cave = built[name]
        is_outdoorish = name.startswith("SpearPillar")
        if is_outdoorish:
            outdoor_names.append(name)
        else:
            indoor_names.append(name)

        prev_name = PATH[i - 1] if i > 0 else None
        next_name = PATH[i + 1] if i + 1 < len(PATH) else None

        # Origins: distorted spear uses local coords in events (x~29)
        origin = (0, 0)
        objs, plat_warps, scripts = densify_from_plat(name, plat, origin, w, h)

        warps = []
        # Entry warp (from previous) at entry tile
        if prev_name:
            warps.append(warp(entry[0], entry[1], mid(prev_name), 1))  # dest warp 1 = exit of prev
        else:
            # SpearPillar_Distorted entry from normal SpearPillar
            warps.append(warp(entry[0], entry[1], "MAP_SPEAR_PILLAR", 0))

        # Exit warp (to next) at exit tile
        if next_name:
            warps.append(warp(exit_[0], exit_[1], mid(next_name), 0))
        else:
            # Turnback cave returns to SpearPillar after clear
            warps.append(warp(exit_[0], exit_[1], "MAP_SPEAR_PILLAR", 0))

        # Align with platinum warp tiles when present
        if plat_warps:
            # Replace first warp xy with first plat warp if in bounds
            lx, ly, _pw = plat_warps[0]
            warps[0] = {**warps[0], "x": lx, "y": ly}
            if len(plat_warps) > 1 and len(warps) > 1:
                lx2, ly2, _ = plat_warps[1]
                warps[1] = {**warps[1], "x": lx2, "y": ly2}

        # Special scripts
        if name == "SpearPillar_Distorted":
            ensure_trainer(
                "TRAINER_LEADER_CYRUS_DISTORTED",
                47,
                "Team Aqua",
                "Aqua Leader Archie",
                [("Honchkrow", 45), ("Crobat", 46), ("Gyarados", 46), ("Weavile", 47)],
                "Cyrus",
                tag="Sinnoh M27",
            )
            objs.append(obj("OBJ_EVENT_GFX_MAXIE", w // 2, h // 2 - 4, f"{name}_EventScript_Cyrus"))
            scripts += (
                f"{name}_EventScript_Cyrus::\n"
                "\tlock\n\tfaceplayer\n"
                f"\tgoto_if_set FLAG_DEFEATED_CYRUS_SPEAR_PILLAR, {name}_EventScript_CyrusAfterDist\n"
                f"\ttrainerbattle_single TRAINER_LEADER_CYRUS_DISTORTED, {name}_Text_CyrusIntro, {name}_Text_CyrusDefeat\n"
                f"\tmsgbox {name}_Text_CyrusAfter, MSGBOX_DEFAULT\n"
                "\trelease\n\tend\n\n"
                f"{name}_EventScript_CyrusAfterDist::\n"
                f"\tmsgbox {name}_Text_CyrusAfter, MSGBOX_DEFAULT\n"
                "\trelease\n\tend\n\n"
                f'{name}_Text_CyrusIntro:\n\t.string "CYRUS: The pillars cracked open.\\n"\n'
                f'\t.string "Step through, and witness absence.$"\n\n'
                f'{name}_Text_CyrusDefeat:\n\t.string "Still... the rift remains.$"\n\n'
                f'{name}_Text_CyrusAfter:\n\t.string "CYRUS: The Distortion World awaits.\\n"\n'
                f'\t.string "Giratina stirs in the depths.$"\n\n'
            )
            # Mark entered
            scripts = scripts.replace(
                f"{name}_MapScripts::\n\t.byte 0\n",
                f"{name}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, {name}_OnTransition\n\t.byte 0\n\n"
                f"{name}_OnTransition::\n\tsetflag FLAG_ENTERED_DISTORTION_WORLD\n\tend\n\n",
            )

        if name == "DistortionWorld_GiratinaRoom":
            gx, gy = find_walkable(grid, prefer=(w // 2, h // 2))
            objs.append(obj("OBJ_EVENT_GFX_ITEM_BALL", gx, gy, f"{name}_EventScript_Giratina", flag="FLAG_DEFEATED_GIRATINA_DISTORTION"))
            scripts += (
                f"{name}_EventScript_Giratina::\n"
                "\tlock\n\tfaceplayer\n"
                f"\tgoto_if_set FLAG_DEFEATED_GIRATINA_DISTORTION, {name}_EventScript_Gone\n"
                f"\tmsgbox {name}_Text_Appear, MSGBOX_DEFAULT\n"
                "\tsetwildbattle SPECIES_GIRATINA, 47\n"
                "\tdowildbattle\n"
                "\tsetflag FLAG_DEFEATED_GIRATINA_DISTORTION\n"
                "\tsetflag FLAG_DISTORTION_WORLD_CLEAR\n"
                f"\tmsgbox {name}_Text_After, MSGBOX_DEFAULT\n"
                "\trelease\n\tend\n\n"
                f"{name}_EventScript_Gone::\n"
                f"\tmsgbox {name}_Text_Gone, MSGBOX_DEFAULT\n"
                "\trelease\n\tend\n\n"
                f'{name}_Text_Appear:\n\t.string "A shadow coils against reversed gravity.\\n"\n'
                f'\t.string "Giratina emerges!$"\n\n'
                f'{name}_Text_After:\n\t.string "The Renegade Pokemon fades.\\n"\n'
                f'\t.string "A path back toward Spear Pillar opens.$"\n\n'
                f'{name}_Text_Gone:\n\t.string "Only distorted silence remains.$"\n\n'
            )

        if name == "DistortionWorld_TurnbackCaveRoom":
            objs.append(obj("OBJ_EVENT_GFX_OLD_MAN", exit_[0], max(1, exit_[1] - 2), f"{name}_EventScript_Guide"))
            scripts += (
                f"{name}_EventScript_Guide::\n"
                "\tlock\n\tfaceplayer\n"
                f"\tgoto_if_set FLAG_DISTORTION_WORLD_CLEAR, {name}_EventScript_Open\n"
                f"\tmsgbox {name}_Text_Closed, MSGBOX_DEFAULT\n"
                "\trelease\n\tend\n\n"
                f"{name}_EventScript_Open::\n"
                f"\tmsgbox {name}_Text_Open, MSGBOX_DEFAULT\n"
                "\trelease\n\tend\n\n"
                f'{name}_Text_Closed:\n\t.string "The exit stays sealed until Giratina\\n"\n'
                f'\t.string "is settled deeper in.$"\n\n'
                f'{name}_Text_Open:\n\t.string "Sunyshore still waits for its Gym.\\n"\n'
                f'\t.string "Volkner is the last badge before the League.$"\n\n'
            )

        # Soft-close filler NPC on early floors
        if name.startswith("DistortionWorld_") and name not in (
            "DistortionWorld_GiratinaRoom",
            "DistortionWorld_TurnbackCaveRoom",
        ):
            nx, ny = find_walkable(grid, prefer=(3, h // 2))
            objs.append(obj("OBJ_EVENT_GFX_AQUA_MEMBER_M", nx, ny, f"{name}_EventScript_Grunt"))
            scripts += (
                f"{name}_EventScript_Grunt::\n\tmsgbox {name}_Text_Grunt, MSGBOX_NPC\n\tend\n\n"
                f'{name}_Text_Grunt:\n\t.string "Boss Cyrus went deeper.\\n"\n'
                f'\t.string "This place eats directions.$"\n\n'
            )

        map_type = "MAP_TYPE_ROUTE" if is_outdoorish else "MAP_TYPE_UNDERGROUND"
        music = "MUS_PETALBURG_WOODS" if is_outdoorish else "MUS_AQUA_MAGMA_HIDEOUT"
        write_map(
            name,
            {
                "id": mid(name),
                "name": name,
                "layout": layout_id(name),
                "music": music,
                "region": "REGION_HOENN",
                "region_map_section": "MAPSEC_ROUTE_210",
                "requires_flash": False,
                "weather": "WEATHER_NONE",
                "map_type": map_type,
                "allow_cycling": False,
                "allow_escaping": not is_outdoorish,
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

    # Retarget SpearPillar distortion soft-close -> Distorted map
    sp = json.loads((MAPS / "SpearPillar" / "map.json").read_text())
    # Replace DistortionClosed NPC with warp-adjacent guide + open path
    objs = sp.get("object_events") or []
    for o in objs:
        if o.get("script") == "SpearPillar_EventScript_DistortionClosed":
            o["script"] = "SpearPillar_EventScript_DistortionOpen"
            o["x"] = 32
            o["y"] = 18
    # Ensure warp into Distorted near that tile
    warps = sp.get("warp_events") or []
    # Keep existing return warps; add rift warp
    warps.append(warp(32, 16, "MAP_SPEAR_PILLAR_DISTORTED", 0))
    warps.append(warp(33, 16, "MAP_SPEAR_PILLAR_DISTORTED", 0))
    sp["warp_events"] = warps
    sp["object_events"] = objs
    (MAPS / "SpearPillar" / "map.json").write_text(json.dumps(sp, indent=2) + "\n")
    scripts_sp = (MAPS / "SpearPillar" / "scripts.inc").read_text()
    if "SpearPillar_EventScript_DistortionOpen" not in scripts_sp:
        scripts_sp += (
            "\nSpearPillar_EventScript_DistortionOpen::\n"
            "\tmsgbox SpearPillar_Text_DistortionOpen, MSGBOX_NPC\n\tend\n\n"
            'SpearPillar_Text_DistortionOpen:\n\t.string "The rift yawns open.\\n"\n'
            '\t.string "Beyond it lies the Distortion World.$"\n'
        )
        # Soften old closed text if still referenced
        (MAPS / "SpearPillar" / "scripts.inc").write_text(scripts_sp)

    register_maps(outdoor_names, indoor_names, "gMapGroup_IndoorM27")
    scrub(outdoor_names + indoor_names + ["SpearPillar"])
    print("M27 build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
