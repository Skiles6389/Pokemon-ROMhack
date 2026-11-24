#!/usr/bin/env python3
"""
M23: Route 218, Canalave City, Iron Island approach, Byron (Mine Badge).

Land IDs from pret/pokeplatinum TownsAndRoutes matrix:
  Route218 [[50, 51]]      64x32 origin (64, 736)
  Canalave [[48], [49]]    32x64 origin (32, 704)
  IronIsland [[54]]        32x32 origin (96, 480)

Emerald tilesets only. Original dialogue. Trainer IVs 0.
Scrubs non-ASCII only in M23 map scripts.
"""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAT_DATA = Path("/tmp/pokeplatinum-ref/res/field/mapmodels/data")
PLAT_MAPS = Path("/tmp/pokeplatinum-ref/res/field/maps")
LAYOUTS = REPO / "data" / "layouts"
LAYOUTS_JSON = LAYOUTS / "layouts.json"
MAPS = REPO / "data" / "maps"
GROUPS = MAPS / "map_groups.json"
EVENT_SCRIPTS = REPO / "data" / "event_scripts.s"
OPP = REPO / "include" / "constants" / "opponents.h"
PARTY = REPO / "src" / "data" / "trainers.party"
FLAGS = REPO / "include" / "constants" / "flags.h"

MT_GRASS, MT_TALL, MT_WATER, MT_SAND = 0x001, 0x00D, 0x170, 0x121
MT_TREE = (0x1D4, 0x1D5, 0x1DC, 0x1DD)
MT_ROCK, MT_LEDGE_A, MT_LEDGE_B = 0x079, 0x0D5, 0x0D6
IN_FLOOR, IN_WALL, IN_DOOR = 0x201, 0x21A, 0x20E

R218 = [[50, 51]]
CANALAVE = [[48], [49]]
IRON = [[54]]

GFX = {
    "OBJ_EVENT_GFX_RICH_BOY": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_LADY": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_GENTLEMAN": "OBJ_EVENT_GFX_GENTLEMAN",
    "OBJ_EVENT_GFX_SOCIALITE": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_POLICEMAN": "OBJ_EVENT_GFX_POLICEMAN",
    "OBJ_EVENT_GFX_FISHERMAN": "OBJ_EVENT_GFX_FISHERMAN",
    "OBJ_EVENT_GFX_ACE_TRAINER_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_ACE_TRAINER_F": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_SCIENTIST_M": "OBJ_EVENT_GFX_SCIENTIST_1",
    "OBJ_EVENT_GFX_COLLECTOR": "OBJ_EVENT_GFX_MANIAC",
    "OBJ_EVENT_GFX_PARASOL_LADY": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_SAILOR": "OBJ_EVENT_GFX_SAILOR",
    "OBJ_EVENT_GFX_WORKER_M": "OBJ_EVENT_GFX_MAN_4",
    "OBJ_EVENT_GFX_WORKER_F": "OBJ_EVENT_GFX_WOMAN_2",
}


def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]


def attr_to_mt(v: int, x: int, y: int) -> int:
    col, beh = (v >> 15) & 1, v & 0xFF
    if col:
        return MT_TREE[(y & 1) * 2 + (x & 1)]
    if beh in (0x02, 0x03):
        return MT_TALL
    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
        return MT_WATER
    if beh == 0x21:
        return MT_SAND
    if beh == 0x3B:
        return MT_LEDGE_A if (x & 1) == 0 else MT_LEDGE_B
    if beh in (0x38, 0x39, 0x3A):
        return MT_ROCK
    return MT_GRASS


def stitch(chunks: list[list[int]]) -> list[list[int]]:
    rows, cols = len(chunks), len(chunks[0])
    out = [[0] * (cols * 32) for _ in range(rows * 32)]
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    out[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return out


def pack(grid, collision_grid=None):
    """Encode metatile + collision + elevation (see sinnoh_build_lib.encode_map_cell)."""
    from tools.sinnoh_maps.sinnoh_build_lib import encode_map_cell
    import struct
    h, w = len(grid), len(grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            coll = None if collision_grid is None else collision_grid[y][x]
            struct.pack_into("<H", out, (y * w + x) * 2, encode_map_cell(grid[y][x], collision=coll))
    return bytes(out)



def open_path(grid, pts, mt=MT_GRASS):
    blocked = set(MT_TREE) | {MT_ROCK, IN_WALL}
    for x, y in pts:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = mt
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] in blocked:
                    grid[ny][nx] = mt


def paint_from_attrs(grid, chunks):
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    x, y = cx * 32 + lx, cy * 32 + ly
                    v = attrs[ly * 32 + lx]
                    beh = v & 0xFF
                    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
                        grid[y][x] = MT_WATER


def write_layout(name, w, h, primary, secondary, blob):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blob)
    src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(src.read_bytes() if src.exists() else bytes(8))
    lid = "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")
    lname = f"{name}_Layout"
    meta = json.loads(LAYOUTS_JSON.read_text())
    entry = {
        "id": lid,
        "name": lname,
        "width": w,
        "height": h,
        "primary_tileset": primary,
        "secondary_tileset": secondary,
        "border_filepath": f"data/layouts/{name}/border.bin",
        "blockdata_filepath": f"data/layouts/{name}/map.bin",
        "layout_version": "emerald",
    }
    layouts = meta["layouts"]
    for i, L in enumerate(layouts):
        if L.get("id") == lid:
            layouts[i] = entry
            break
    else:
        layouts.append(entry)
    LAYOUTS_JSON.write_text(json.dumps(meta, indent=2) + "\n")
    print("layout", name, w, h)
    return lid


def obj(gfx, x, y, script, trainer="TRAINER_TYPE_NONE", sight="0", movement="MOVEMENT_TYPE_FACE_DOWN"):
    return {
        "graphics_id": gfx,
        "x": int(x),
        "y": int(y),
        "elevation": 3,
        "movement_type": movement,
        "movement_range_x": 0,
        "movement_range_y": 0,
        "trainer_type": trainer,
        "trainer_sight_or_berry_tree_id": str(sight),
        "script": script,
        "flag": "0",
    }


def warp(x, y, dest, wid):
    return {"x": int(x), "y": int(y), "elevation": 0, "dest_map": dest, "dest_warp_id": str(wid)}


def ensure_flag(name: str, value_hex: str, comment: str):
    text = FLAGS.read_text()
    if name in text:
        return
    # Insert near other Sinnoh M20 flags
    anchor = "FLAG_GOT_PASTORIA_HM_DEFOG"
    if anchor in text:
        text = text.replace(
            f"#define {anchor}",
            f"#define {name}  {value_hex} // {comment}\n#define {anchor}",
            1,
        )
    else:
        text += f"\n#define {name}  {value_hex} // {comment}\n"
    FLAGS.write_text(text)


def ensure_trainer(tid, level, cls, pic, mons, display_name=None):
    defined = set(re.findall(r"#define (TRAINER_[A-Z0-9_]+)\s+", OPP.read_text()))
    if tid not in defined:
        ids = [int(x) for x in re.findall(r"#define TRAINER_[A-Z0-9_]+\s+(\d+)\b", OPP.read_text())]
        nid = max(i for i in ids if i < 2000) + 1
        text = OPP.read_text()
        text = text.replace(
            "#define TRAINERS_COUNT_EMERALD",
            f"#define {tid}                    {nid} // Sinnoh M23\n\n#define TRAINERS_COUNT_EMERALD",
            1,
        )
        text = re.sub(
            r"#define TRAINERS_COUNT_EMERALD\s+\d+",
            f"#define TRAINERS_COUNT_EMERALD     {nid + 1}",
            text,
            count=1,
        )
        OPP.write_text(text)
    if f"=== {tid} ===" in PARTY.read_text():
        return
    name = display_name or tid.split("_")[-1][:10].title()
    lines = [
        f"=== {tid} ===",
        f"Name: {name}",
        f"Class: {cls}",
        f"Pic: {pic}",
        "Gender: Male",
        "Music: Male",
        "Double Battle: No",
        "AI: Basic Trainer",
        "",
    ]
    for sp, lv in mons:
        lines += [sp, f"Level: {lv}", "IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe", "- Tackle", ""]
    PARTY.write_text(PARTY.read_text().rstrip() + "\n\n" + "\n".join(lines) + "\n")


def party_for(tid, level):
    u = tid.upper()
    if "SAILOR" in u:
        return "Sailor", "Sailor", [("Wingull", level), ("Mantyke", level - 1)]
    if "FISHER" in u:
        return "Fisherman", "Fisherman", [("Finneon", level), ("Magikarp", level)]
    if "WORKER" in u or "HIKER" in u:
        return "Hiker", "Hiker", [("Geodude", level), ("Onix", level)]
    if "ACE" in u or "RANGER" in u:
        return "Cooltrainer", "Cooltrainer M", [("Staravia", level), ("Floatzel", level - 1)]
    if "BLACK_BELT" in u or "BATTLE_GIRL" in u:
        return "Black Belt", "Black Belt", [("Machop", level), ("Meditite", level)]
    if "LASS" in u:
        return "Lass", "Lass", [("Budew", level)]
    if "TUBER" in u:
        return "Tuber M", "Tuber M", [("Remoraid", level)]
    return "Youngster", "Youngster", [("Starly", level), ("Bidoof", level)]


def face(d):
    return {
        "DIR_NORTH": "MOVEMENT_TYPE_FACE_UP",
        "DIR_SOUTH": "MOVEMENT_TYPE_FACE_DOWN",
        "DIR_WEST": "MOVEMENT_TYPE_FACE_LEFT",
        "DIR_EAST": "MOVEMENT_TYPE_FACE_RIGHT",
    }.get(d or "", "MOVEMENT_TYPE_FACE_DOWN")


def place_all(em, plat, origin, wmax, hmax, level, flavor="sea"):
    pe = json.loads((PLAT_MAPS / plat / "events.json").read_text())
    ox, oz = origin
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    occupied = set()
    n = 0
    intro_a = "Salt air and steel nerves!\\n" if flavor == "sea" else "These caves swallow sound.\\n"
    intro_b = "a proper battle.$" if flavor == "sea" else "Prove you belong here.$"
    after_a = "Canalave's gym leader forges\\n" if flavor == "sea" else "The ferry back to Canalave\\n"
    after_b = "teams like tempered steel.$" if flavor == "sea" else "runs when the tide allows.$"
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"] - ox), int(po["z"] - oz)
        if not (0 <= lx < wmax and 0 <= ly < hmax) or (lx, ly) in occupied:
            continue
        tr = po.get("trainer") or {}
        tid_plat = tr.get("id")
        if tid_plat:
            tid = tid_plat if tid_plat.startswith("TRAINER_") else f"TRAINER_{tid_plat}"
            cls, pic, mons = party_for(tid, level)
            ensure_trainer(tid, level, cls, pic, mons)
            short = tid.replace("TRAINER_", "").title().replace("_", "")
            label = f"{em}_EventScript_{short}_{n}"
            gfx = GFX.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_YOUNGSTER")
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
                f"{label}_Intro:\n\t.string \"{intro_a}\"\n\t.string \"{intro_b}\"\n\n"
                f"{label}_Defeat:\n\t.string \"Tempered out.$\"\n\n"
                f"{label}_After:\n\t.string \"{after_a}\"\n\t.string \"{after_b}\"\n\n"
            )
            n += 1
        else:
            label = f"{em}_EventScript_PlatNpc{n}"
            gfx = GFX.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_GIRL_1")
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f"{label}_Text:\n\t.string \"Ships, steel, and stories pile up\\n\"\n"
                f"\t.string \"along this western shore.$\"\n\n"
            )
            n += 1
        occupied.add((lx, ly))
    return objs, scripts, pe


def local_warps(pe, origin, wmax, hmax, mapping):
    """Map platinum outdoor warps into emerald local coords via dest keyword -> (dest_map, wid)."""
    ox, oz = origin
    out = []
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if not (0 <= lx < wmax and 0 <= ly < hmax):
            continue
        dest_key = (pw.get("dest_header_id") or pw.get("id") or "").upper()
        matched = None
        for key, (dm, wid) in mapping.items():
            if key in dest_key:
                matched = (dm, wid)
                break
        if matched is None:
            continue
        out.append(warp(lx, ly, matched[0], matched[1]))
    return out


def stamp_door(grid, x, y):
    for dy, row in enumerate([[0x210, 0x211, 0x212], [0x218, 0x219, 0x21A], [0x222, 0x230, 0x221]]):
        for dx, mt in enumerate(row):
            sx, sy = x - 1 + dx, y - 2 + dy
            if 0 <= sy < len(grid) and 0 <= sx < len(grid[0]):
                grid[sy][sx] = mt


def write_map(name, data, scripts):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("map", name)


def indoor(name, mid, mapsec, exit_map, exit_wid, script_label, text, gfx="OBJ_EVENT_GFX_OLD_MAN"):
    grid = [
        [
            IN_WALL if y in (0, 7) or x in (0, 9) else (IN_DOOR if y == 7 and x in (4, 5) else IN_FLOOR)
            for x in range(10)
        ]
        for y in range(8)
    ]
    write_layout(name, 10, 8, "gTileset_Building", "gTileset_GenericBuilding", pack(grid))
    lid = "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")
    data = {
        "id": mid,
        "name": name,
        "layout": lid,
        "music": "MUS_PL_JUBILIFE",
        "region": "REGION_HOENN",
        "region_map_section": mapsec,
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": False,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": [obj(gfx, 4, 3, script_label)],
        "warp_events": [warp(4, 7, exit_map, exit_wid), warp(5, 7, exit_map, exit_wid)],
        "coord_events": [],
        "bg_events": [],
    }
    scripts = (
        f"{name}_MapScripts::\n\t.byte 0\n\n"
        f"{script_label}::\n\tmsgbox {script_label}_Text, MSGBOX_NPC\n\tend\n\n"
        f"{script_label}_Text:\n\t.string \"{text}\"\n"
    )
    write_map(name, data, scripts)


def build_gym():
    # Compact gym: reuse Pastoria layout to save ROM (steel dialogue only).
    name = "CanalaveCity_Gym"
    mid = "MAP_CANALAVE_CITY_GYM"
    ensure_flag("FLAG_RECEIVED_CANALAVE_GYM_TM", "0x2AC", "Sinnoh M23 Byron TM")
    ensure_trainer(
        "TRAINER_LEADER_BYRON",
        41,
        "Leader",
        "Hiker",
        [("Bronzor", 37), ("Steelix", 40), ("Bastiodon", 41)],
        display_name="Byron",
    )
    data = {
        "id": mid,
        "name": name,
        "layout": "LAYOUT_PASTORIA_CITY_GYM",
        "music": "MUS_GYM",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_JUBILIFE_CITY",
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": False,
        "allow_running": False,
        "show_map_name": False,
        "battle_scene": "MAP_BATTLE_SCENE_GYM",
        "connections": None,
        "object_events": [
            obj("OBJ_EVENT_GFX_EXPERT_M", 12, 4, "CanalaveCity_Gym_EventScript_Byron"),
            obj("OBJ_EVENT_GFX_MAN_2", 8, 34, "CanalaveCity_Gym_EventScript_GymGuide"),
            obj(
                "OBJ_EVENT_GFX_BLACK_BELT",
                4,
                18,
                "CanalaveCity_Gym_EventScript_WorkerAlan",
                trainer="TRAINER_TYPE_NORMAL",
                sight="3",
                movement="MOVEMENT_TYPE_FACE_RIGHT",
            ),
            obj(
                "OBJ_EVENT_GFX_SAILOR",
                19,
                18,
                "CanalaveCity_Gym_EventScript_SailorJonah",
                trainer="TRAINER_TYPE_NORMAL",
                sight="3",
                movement="MOVEMENT_TYPE_FACE_LEFT",
            ),
        ],
        "warp_events": [
            warp(12, 39, "MAP_CANALAVE_CITY", 0),
            warp(13, 39, "MAP_CANALAVE_CITY", 0),
        ],
        "coord_events": [],
        "bg_events": [
            {
                "type": "sign",
                "x": 10,
                "y": 36,
                "elevation": 0,
                "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                "script": "CanalaveCity_Gym_EventScript_Statue",
            },
            {
                "type": "sign",
                "x": 13,
                "y": 36,
                "elevation": 0,
                "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                "script": "CanalaveCity_Gym_EventScript_Statue",
            },
        ],
    }
    ensure_trainer(
        "TRAINER_WORKER_ALAN_CANALAVE",
        33,
        "Hiker",
        "Hiker",
        [("Onix", 33)],
        display_name="Alan",
    )
    ensure_trainer(
        "TRAINER_SAILOR_JONAH_CANALAVE",
        34,
        "Sailor",
        "Sailor",
        [("Pelipper", 34)],
        display_name="Jonah",
    )
    scripts = r"""CanalaveCity_Gym_MapScripts::
	.byte 0

CanalaveCity_Gym_EventScript_Byron::
	lock
	faceplayer
	trainerbattle_single TRAINER_LEADER_BYRON, CanalaveCity_Gym_Text_ByronIntro, CanalaveCity_Gym_Text_ByronDefeat, CanalaveCity_Gym_EventScript_ByronDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_CANALAVE_GYM_TM, CanalaveCity_Gym_EventScript_GiveTM
	msgbox CanalaveCity_Gym_Text_ByronAfter, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Gym_EventScript_ByronDefeated::
	message CanalaveCity_Gym_Text_ReceivedMineBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox CanalaveCity_Gym_Text_MineBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE06_GET
	goto CanalaveCity_Gym_EventScript_GiveTM
	end

CanalaveCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_FLASH_CANNON
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_CANALAVE_GYM_TM
	msgbox CanalaveCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE06_GET, CanalaveCity_Gym_EventScript_GuideVictory
	msgbox CanalaveCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Gym_EventScript_GuideVictory::
	msgbox CanalaveCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

CanalaveCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE06_GET, CanalaveCity_Gym_EventScript_StatueWon
	msgbox CanalaveCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

CanalaveCity_Gym_EventScript_StatueWon::
	msgbox CanalaveCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

CanalaveCity_Gym_EventScript_WorkerAlan::
	trainerbattle_single TRAINER_WORKER_ALAN_CANALAVE, CanalaveCity_Gym_Text_AlanIntro, CanalaveCity_Gym_Text_AlanDefeat
	msgbox CanalaveCity_Gym_Text_AlanAfter, MSGBOX_AUTOCLOSE
	end

CanalaveCity_Gym_EventScript_SailorJonah::
	trainerbattle_single TRAINER_SAILOR_JONAH_CANALAVE, CanalaveCity_Gym_Text_JonahIntro, CanalaveCity_Gym_Text_JonahDefeat
	msgbox CanalaveCity_Gym_Text_JonahAfter, MSGBOX_AUTOCLOSE
	end

CanalaveCity_Gym_Text_ByronIntro:
	.string "I'm BYRON, Canalave's Gym Leader!\n"
	.string "Steel types don't bend for soft hits.\p"
	.string "Show me a will that can reshape ore!$"

CanalaveCity_Gym_Text_ByronDefeat:
	.string "You hammered through my armor...$"

CanalaveCity_Gym_Text_ByronAfter:
	.string "Keep tempering that team.\n"
	.string "The next stretch of Sinnoh gets hotter.$"

CanalaveCity_Gym_Text_ReceivedMineBadge:
	.string "{PLAYER} received the MINE BADGE\n"
	.string "from BYRON.$"

CanalaveCity_Gym_Text_MineBadgeInfo:
	.string "With the MINE BADGE, more machines\n"
	.string "will answer your POKéMON's strength.$"

CanalaveCity_Gym_Text_ExplainTM:
	.string "That TM is FLASH CANNON.\n"
	.string "A steel beam that can lower Sp. Def.$"

CanalaveCity_Gym_Text_GuideAdvice:
	.string "BYRON favors Steel types.\n"
	.string "Fire and Ground crack that shell.$"

CanalaveCity_Gym_Text_GuideVictory:
	.string "You forged a win against BYRON!\n"
	.string "The Mine Badge looks good on you.$"

CanalaveCity_Gym_Text_Statue:
	.string "CANALAVE CITY POKéMON GYM$"

CanalaveCity_Gym_Text_StatueWon:
	.string "CANALAVE CITY POKéMON GYM\p"
	.string "BYRON'S CERTIFIED TRAINERS:\n"
	.string "{PLAYER}$"

CanalaveCity_Gym_Text_AlanIntro:
	.string "Steel beams don't flinch!$"

CanalaveCity_Gym_Text_AlanDefeat:
	.string "Bent out of shape...$"

CanalaveCity_Gym_Text_AlanAfter:
	.string "BYRON taught us to stand firm.$"

CanalaveCity_Gym_Text_JonahIntro:
	.string "Harbor grit meets gym steel!$"

CanalaveCity_Gym_Text_JonahDefeat:
	.string "Washed out.$"

CanalaveCity_Gym_Text_JonahAfter:
	.string "Take the ferry to Iron Island\n"
	.string "if you want raw ore practice.$"
"""
    write_map(name, data, scripts)


def update_jubilife_gate():
    """Point west door of existing Jubilife gate at Route 218."""
    p = MAPS / "Route218_JubilifeGate" / "map.json"
    d = json.loads(p.read_text())
    # Layout Seaside entrance: warps 0,1 east/south to Jubilife; 2,3 should go west to Route218
    warps = d.get("warp_events") or []
    # Keep 0,1 -> Jubilife; set 2,3 -> Route218 east edge
    if len(warps) >= 4:
        warps[2] = warp(warps[2]["x"], warps[2]["y"], "MAP_ROUTE218", 0)
        warps[3] = warp(warps[3]["x"], warps[3]["y"], "MAP_ROUTE218", 1)
    d["warp_events"] = warps
    p.write_text(json.dumps(d, indent=2) + "\n")
    scripts = MAPS / "Route218_JubilifeGate" / "scripts.inc"
    scripts.write_text(
        "Route218_JubilifeGate_MapScripts::\n\t.byte 0\n\n"
        "Route218_JubilifeGate_EventScript_Attendant::\n"
        "\tmsgbox Route218_JubilifeGate_Text_Attendant, MSGBOX_NPC\n\tend\n\n"
        "Route218_JubilifeGate_Text_Attendant:\n"
        '\t.string "West gate to Route 218.\\n"\n'
        '\t.string "Surf the channel toward Canalave.$"\n'
    )
    print("updated Route218_JubilifeGate")


def build_canalave_gate():
    name = "Route218_CanalaveGate"
    # Reuse same entrance layout as Jubilife gate
    data = {
        "id": "MAP_ROUTE218_CANALAVE_GATE",
        "name": name,
        "layout": "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE",
        "music": "MUS_PL_JUBILIFE",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_JUBILIFE_CITY",
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": [obj("OBJ_EVENT_GFX_MAN_2", 5, 4, f"{name}_EventScript_Attendant")],
        "warp_events": [
            warp(1, 5, "MAP_ROUTE218", 2),
            warp(2, 5, "MAP_ROUTE218", 3),
            warp(12, 5, "MAP_CANALAVE_CITY", 1),
            warp(13, 5, "MAP_CANALAVE_CITY", 2),
        ],
        "coord_events": [],
        "bg_events": [],
    }
    scripts = (
        f"{name}_MapScripts::\n\t.byte 0\n\n"
        f"{name}_EventScript_Attendant::\n"
        f"\tmsgbox {name}_Text_Attendant, MSGBOX_NPC\n\tend\n\n"
        f"{name}_Text_Attendant:\n"
        '\t.string "Canalave City ahead.\\n"\n'
        '\t.string "The library and Gym wait past the docks.$"\n'
    )
    write_map(name, data, scripts)


def main():
    ensure_flag("FLAG_RECEIVED_CANALAVE_GYM_TM", "0x2AC", "Sinnoh M23 Byron TM")

    # --- Route 218 ---
    attr = stitch(R218)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(64)] for y in range(32)]
    paint_from_attrs(grid, R218)
    open_path(grid, [(x, y) for x in range(0, 64) for y in range(14, 22)])
    write_layout("Route218", 64, 32, "gTileset_General", "gTileset_Petalburg", pack(grid))
    objs, scripts, pe = place_all("Route218", "route_218", (64, 736), 64, 32, 28, flavor="sea")
    # Warps: east to Jubilife gate, west to Canalave gate (local approx from platinum)
    # Platinum: east warps ~121 -> local 57; west ~70 -> local 6
    warps = [
        warp(57, 22, "MAP_ROUTE218_JUBILIFE_GATE", 2),
        warp(58, 22, "MAP_ROUTE218_JUBILIFE_GATE", 3),
        warp(6, 18, "MAP_ROUTE218_CANALAVE_GATE", 0),
        warp(6, 19, "MAP_ROUTE218_CANALAVE_GATE", 1),
    ]
    # Prefer platinum-fitted warps when available
    fitted = local_warps(
        pe,
        (64, 736),
        64,
        32,
        {
            "GATE_TO_JUBILIFE": ("MAP_ROUTE218_JUBILIFE_GATE", 2),
            "GATE_TO_CANALAVE": ("MAP_ROUTE218_CANALAVE_GATE", 0),
        },
    )
    if len(fitted) >= 2:
        # Pair gate warps
        jubi = [w for w in fitted if "JUBILIFE" in w["dest_map"]]
        cana = [w for w in fitted if "CANALAVE" in w["dest_map"]]
        warps = []
        for i, w in enumerate(jubi[:2]):
            warps.append(warp(w["x"], w["y"], "MAP_ROUTE218_JUBILIFE_GATE", 2 + i))
        for i, w in enumerate(cana[:2]):
            warps.append(warp(w["x"], w["y"], "MAP_ROUTE218_CANALAVE_GATE", i))
        if len(warps) < 4:
            warps = [
                warp(57, 22, "MAP_ROUTE218_JUBILIFE_GATE", 2),
                warp(58, 22, "MAP_ROUTE218_JUBILIFE_GATE", 3),
                warp(6, 18, "MAP_ROUTE218_CANALAVE_GATE", 0),
                warp(6, 19, "MAP_ROUTE218_CANALAVE_GATE", 1),
            ]
    r218 = {
        "id": "MAP_ROUTE218",
        "name": "Route218",
        "layout": "LAYOUT_ROUTE218",
        "music": "MUS_PL_ROUTE203",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_202",
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_ROUTE",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,  # accessed via gates; Surf channel is on-map water
        "object_events": objs,
        "warp_events": warps,
        "coord_events": [],
        "bg_events": [],
    }
    write_map("Route218", r218, scripts)

    # --- Canalave City ---
    attr = stitch(CANALAVE)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(32)] for y in range(64)]
    paint_from_attrs(grid, CANALAVE)
    open_path(grid, [(x, y) for x in range(8, 24) for y in range(20, 56)])
    paint_from_attrs(grid, CANALAVE)  # restore harbor water after path carve
    # Door stamps from platinum warps (local)
    pe_c = json.loads((PLAT_MAPS / "canalave_city" / "events.json").read_text())
    ox, oz = 32, 704
    door_targets = []
    for pw in pe_c.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < 32 and 0 <= ly < 64:
            stamp_door(grid, lx, ly)
            door_targets.append((lx, ly, pw.get("dest_header_id") or ""))
    write_layout("CanalaveCity", 32, 64, "gTileset_General", "gTileset_Petalburg", pack(grid))
    objs, scripts, _ = place_all("CanalaveCity", "canalave_city", (32, 704), 32, 64, 30, flavor="sea")
    # Sailor ferry NPC near south/west dock
    objs.append(obj("OBJ_EVENT_GFX_SAILOR", 16, 50, "CanalaveCity_EventScript_FerrySailor"))
    scripts += (
        "CanalaveCity_EventScript_FerrySailor::\n"
        "\tlock\n\tfaceplayer\n"
        "\tmsgbox CanalaveCity_Text_FerryOffer, MSGBOX_YESNO\n"
        "\tgoto_if_eq VAR_RESULT, NO, CanalaveCity_EventScript_FerryNo\n"
        "\twarpsilent MAP_IRON_ISLAND, 8, 20\n"
        "\twaitstate\n\trelease\n\tend\n\n"
        "CanalaveCity_EventScript_FerryNo::\n"
        "\tmsgbox CanalaveCity_Text_FerryNo, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        'CanalaveCity_Text_FerryOffer:\n\t.string "Ferry to Iron Island?\\n"\n'
        '\t.string "The crossing is short.$"\n\n'
        'CanalaveCity_Text_FerryNo:\n\t.string "Come back when the ore calls.$"\n\n'
    )
    # Build warp list: gym, PC, mart, gate, library stub, houses
    # Warp IDs we will expose on CanalaveCity:
    # 0 gym, 1-2 from canalave gate, 3 PC, 4 mart, 5 library, 6 house
    warps = []
    # Prefer platinum local positions
    def find_door(substr, default):
        for lx, ly, dest in door_targets:
            if substr in dest.upper():
                return lx, ly
        return default

    gx, gy = find_door("GYM", (7, 27))
    px, py = find_door("POKECENTER", (26, 18))
    mx, my = find_door("MART", (21, 36))
    lx_, ly_ = find_door("LIBRARY", (5, 14))
    warps = [
        warp(gx, gy, "MAP_CANALAVE_CITY_GYM", 0),
        warp(31, 40, "MAP_ROUTE218_CANALAVE_GATE", 2),  # east to gate
        warp(31, 41, "MAP_ROUTE218_CANALAVE_GATE", 3),
        warp(px, py, "MAP_CANALAVE_CITY_POKEMON_CENTER_1F", 0),
        warp(mx, my, "MAP_CANALAVE_CITY_MART", 0),
        warp(lx_, ly_, "MAP_CANALAVE_CITY_LIBRARY", 0),
        warp(find_door("WEST_HOUSE", (10, 30))[0], find_door("WEST_HOUSE", (10, 30))[1], "MAP_CANALAVE_CITY_HOUSE1", 0),
    ]
    canalave = {
        "id": "MAP_CANALAVE_CITY",
        "name": "CanalaveCity",
        "layout": "LAYOUT_CANALAVE_CITY",
        "music": "MUS_PL_JUBILIFE",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_JUBILIFE_CITY",
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_CITY",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": objs,
        "warp_events": warps,
        "coord_events": [],
        "bg_events": [],
    }
    write_map("CanalaveCity", canalave, scripts)

    # --- Iron Island outdoor ---
    attr = stitch(IRON)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(32)] for y in range(32)]
    paint_from_attrs(grid, IRON)
    open_path(grid, [(x, y) for x in range(8, 24) for y in range(12, 24)])
    pe_i = json.loads((PLAT_MAPS / "iron_island" / "events.json").read_text())
    ox, oz = 96, 480
    for pw in pe_i.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < 32 and 0 <= ly < 32:
            stamp_door(grid, lx, ly)
    write_layout("IronIsland", 32, 32, "gTileset_General", "gTileset_Fallarbor", pack(grid))
    objs, scripts, _ = place_all("IronIsland", "iron_island", (96, 480), 32, 32, 32, flavor="cave")
    objs.append(obj("OBJ_EVENT_GFX_SAILOR", 8, 22, "IronIsland_EventScript_ReturnFerry"))
    scripts += (
        "IronIsland_EventScript_ReturnFerry::\n"
        "\tlock\n\tfaceplayer\n"
        "\tmsgbox IronIsland_Text_ReturnFerry, MSGBOX_YESNO\n"
        "\tgoto_if_eq VAR_RESULT, NO, IronIsland_EventScript_Stay\n"
        "\twarpsilent MAP_CANALAVE_CITY, 16, 51\n"
        "\twaitstate\n\trelease\n\tend\n\n"
        "IronIsland_EventScript_Stay::\n"
        "\tmsgbox IronIsland_Text_Stay, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        'IronIsland_Text_ReturnFerry:\n\t.string "Head back to Canalave?$"\n\n'
        'IronIsland_Text_Stay:\n\t.string "Watch your step in the shafts.$"\n\n'
    )
    # Interior stubs + closed deeper ruins
    hx, hy = 15, 19
    ix, iy = 21, 9
    for pw in pe_i.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        dest = (pw.get("dest_header_id") or "").upper()
        if "HOUSE" in dest:
            hx, hy = lx, ly
        if "IRON_ISLAND_1F" in dest or dest.endswith("_1F"):
            ix, iy = lx, ly
    iron = {
        "id": "MAP_IRON_ISLAND",
        "name": "IronIsland",
        "layout": "LAYOUT_IRON_ISLAND",
        "music": "MUS_PETALBURG_WOODS",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_202",
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_ROUTE",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": objs,
        "warp_events": [
            warp(hx, hy, "MAP_IRON_ISLAND_HOUSE", 0),
            warp(ix, iy, "MAP_IRON_ISLAND_1F_STUB", 0),
        ],
        "coord_events": [],
        "bg_events": [],
    }
    write_map("IronIsland", iron, scripts)

    # Indoors
    indoor(
        "CanalaveCity_House1",
        "MAP_CANALAVE_CITY_HOUSE1",
        "MAPSEC_JUBILIFE_CITY",
        "MAP_CANALAVE_CITY",
        6,
        "CanalaveCity_House1_EventScript_Resident",
        "Books and boat schedules share\\nthis shelf. Canalave never sleeps.$",
    )
    indoor(
        "CanalaveCity_Library",
        "MAP_CANALAVE_CITY_LIBRARY",
        "MAPSEC_JUBILIFE_CITY",
        "MAP_CANALAVE_CITY",
        5,
        "CanalaveCity_Library_EventScript_Librarian",
        "Old Sinnoh myths fill these stacks.\\nCome back when the shelves open further.$",
    )
    indoor(
        "CanalaveCity_Mart",
        "MAP_CANALAVE_CITY_MART",
        "MAPSEC_JUBILIFE_CITY",
        "MAP_CANALAVE_CITY",
        4,
        "CanalaveCity_Mart_EventScript_Clerk",
        "Stock up before the ferry.\\nIron Island is no place to run dry.$",
        gfx="OBJ_EVENT_GFX_MART_EMPLOYEE",
    )
    # PC - clone Celestic pattern using Lilycove/Slateport layout if present
    pc_layout = "LAYOUT_POKEMON_CENTER_1F"
    for L in json.loads(LAYOUTS_JSON.read_text())["layouts"]:
        if "POKEMON_CENTER_1F" in L["id"] and "LAYOUT_POKEMON_CENTER_1F" == L["id"]:
            pc_layout = L["id"]
            break
    # Prefer an existing center layout from Solaceon/Pastoria
    for cand in ("LAYOUT_SOLACEON_TOWN_POKEMON_CENTER_1F", "LAYOUT_PASTORIA_CITY_POKEMON_CENTER_1F", "LAYOUT_POKEMON_CENTER_1F"):
        if any(L["id"] == cand for L in json.loads(LAYOUTS_JSON.read_text())["layouts"]):
            pc_layout = cand
            break
    pc = {
        "id": "MAP_CANALAVE_CITY_POKEMON_CENTER_1F",
        "name": "CanalaveCity_PokemonCenter_1F",
        "layout": pc_layout,
        "music": "MUS_POKE_CENTER",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_JUBILIFE_CITY",
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
            {
                **obj("OBJ_EVENT_GFX_NURSE", 7, 2, "CanalaveCity_PokemonCenter_1F_EventScript_Nurse"),
                "local_id": "LOCALID_NURSE",
            }
        ],
        "warp_events": [
            warp(7, 8, "MAP_CANALAVE_CITY", 3),
            warp(6, 8, "MAP_CANALAVE_CITY", 3),
            warp(1, 6, "MAP_CANALAVE_CITY", 3),
        ],
        "coord_events": [],
        "bg_events": [],
    }
    write_map(
        "CanalaveCity_PokemonCenter_1F",
        pc,
        "CanalaveCity_PokemonCenter_1F_MapScripts::\n"
        "\tmap_script MAP_SCRIPT_ON_TRANSITION, CanalaveCity_PokemonCenter_1F_OnTransition\n"
        "\t.byte 0\n\n"
        "CanalaveCity_PokemonCenter_1F_OnTransition::\n"
        "\tsetrespawn HEAL_LOCATION_JUBILIFE_CITY\n"
        "\tend\n\n"
        "CanalaveCity_PokemonCenter_1F_EventScript_Nurse::\n"
        "\tsetvar VAR_0x800B, LOCALID_NURSE\n"
        "\tcall Common_EventScript_PkmnCenterNurse\n"
        "\twaitmessage\n\twaitbuttonpress\n\trelease\n\tend\n",
    )

    indoor(
        "IronIsland_House",
        "MAP_IRON_ISLAND_HOUSE",
        "MAPSEC_ROUTE_202",
        "MAP_IRON_ISLAND",
        0,
        "IronIsland_House_EventScript_Resident",
        "Miners rest here between shifts.\\nDeeper shafts stay sealed for now.$",
    )
    # Cave stub - closed beyond M23
    cave = [[IN_WALL if y in (0, 9) or x in (0, 11) else (IN_DOOR if y == 9 and x in (5, 6) else IN_FLOOR) for x in range(12)] for y in range(10)]
    # Block north exit with rocks message via NPC
    write_layout("IronIsland_1F_Stub", 12, 10, "gTileset_General", "gTileset_Cave", pack(cave))
    write_map(
        "IronIsland_1F_Stub",
        {
            "id": "MAP_IRON_ISLAND_1F_STUB",
            "name": "IronIsland_1F_Stub",
            "layout": "LAYOUT_IRON_ISLAND_1F_STUB",
            "music": "MUS_PETALBURG_WOODS",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_202",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_UNDERGROUND",
            "allow_cycling": False,
            "allow_escaping": True,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [
                obj("OBJ_EVENT_GFX_WORKER_M", 6, 3, "IronIsland_1F_Stub_EventScript_Blocked")
            ],
            "warp_events": [
                warp(5, 9, "MAP_IRON_ISLAND", 1),
                warp(6, 9, "MAP_IRON_ISLAND", 1),
            ],
            "coord_events": [],
            "bg_events": [],
        },
        "IronIsland_1F_Stub_MapScripts::\n\t.byte 0\n\n"
        "IronIsland_1F_Stub_EventScript_Blocked::\n"
        "\tmsgbox IronIsland_1F_Stub_Text_Blocked, MSGBOX_NPC\n\tend\n\n"
        'IronIsland_1F_Stub_Text_Blocked:\n\t.string "Cave-ins sealed the lower floors.\\n"\n'
        '\t.string "Come back after the Mine Badge shines brighter.$"\n',
    )

    build_gym()
    update_jubilife_gate()
    build_canalave_gate()

    # Fix gym exit warp id to Canalave gym door (warp 0)
    # Already set.

    # Map groups + event scripts
    outdoor = ["Route218", "CanalaveCity", "IronIsland"]
    indoor_names = [
        "Route218_CanalaveGate",
        "CanalaveCity_Gym",
        "CanalaveCity_PokemonCenter_1F",
        "CanalaveCity_Mart",
        "CanalaveCity_Library",
        "CanalaveCity_House1",
        "IronIsland_House",
        "IronIsland_1F_Stub",
    ]
    g = json.loads(GROUPS.read_text())
    g.setdefault("gMapGroup_TownsAndRoutes", [])
    for n in outdoor:
        if n not in g["gMapGroup_TownsAndRoutes"]:
            g["gMapGroup_TownsAndRoutes"].append(n)
    g.setdefault("gMapGroup_IndoorM23", [])
    for n in indoor_names:
        if n not in g["gMapGroup_IndoorM23"]:
            g["gMapGroup_IndoorM23"].append(n)
    if "group_order" in g and "gMapGroup_IndoorM23" not in g["group_order"]:
        g["group_order"].append("gMapGroup_IndoorM23")
    GROUPS.write_text(json.dumps(g, indent=2) + "\n")

    es = EVENT_SCRIPTS.read_text()
    for n in outdoor + indoor_names:
        inc = f'\t.include "data/maps/{n}/scripts.inc"'
        if inc not in es:
            es = es.rstrip() + "\n" + inc + "\n"
    EVENT_SCRIPTS.write_text(es)

    # ASCII scrub M23 scripts only
    for n in outdoor + indoor_names + ["Route218_JubilifeGate"]:
        p = MAPS / n / "scripts.inc"
        if not p.exists():
            continue
        t = p.read_text()
        if any(ord(c) > 127 for c in t):
            p.write_text("".join(c if ord(c) < 128 else "-" for c in t))

    print("M23 build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
