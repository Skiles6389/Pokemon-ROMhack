#!/usr/bin/env python3
"""
M25: Snowpoint City, Candice (Icicle Badge), Lake Acuity.

Land IDs:
  SnowpointCity     [[104], [105]]                 32x64 origin (352, 192)
  AcuityLakefront   [[100, 101], [102, 103]]       64x64 origin (288, 192)
  LakeAcuity        [[553, 554], [555, 556]]       64x64 local dungeon

Emerald tilesets only. Original dialogue. Trainer IVs 0.
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
TMS = REPO / "include" / "constants" / "tms_hms.h"

MT_GRASS, MT_TALL, MT_WATER, MT_SAND = 0x001, 0x00D, 0x170, 0x121
MT_TREE = (0x1D4, 0x1D5, 0x1DC, 0x1DD)
MT_ROCK, MT_LEDGE_A, MT_LEDGE_B = 0x079, 0x0D5, 0x0D6
MT_SNOW = 0x121
IN_FLOOR, IN_WALL, IN_DOOR = 0x201, 0x21A, 0x20E

SNOWPOINT = [[104], [105]]
ACUITY_LF = [[100, 101], [102, 103]]
LAKE_ACUITY = [[553, 554], [555, 556]]

GFX = {
    "OBJ_EVENT_GFX_ACE_TRAINER_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_ACE_TRAINER_F": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_SKIER_M": "OBJ_EVENT_GFX_MAN_5",
    "OBJ_EVENT_GFX_SKIER_F": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_HIKER": "OBJ_EVENT_GFX_HIKER",
    "OBJ_EVENT_GFX_NINJA_BOY": "OBJ_EVENT_GFX_NINJA_BOY",
    "OBJ_EVENT_GFX_GALACTIC_GRUNT_M": "OBJ_EVENT_GFX_AQUA_MEMBER_M",
    "OBJ_EVENT_GFX_GALACTIC_GRUNT_F": "OBJ_EVENT_GFX_AQUA_MEMBER_F",
    "OBJ_EVENT_GFX_COMMANDER_JUPITER": "OBJ_EVENT_GFX_ARCHIE",
}


def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]


def attr_to_mt(v, x, y, snow=False):
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
    return MT_SNOW if snow else MT_GRASS


def stitch(chunks):
    rows, cols = len(chunks), len(chunks[0])
    out = [[0] * (cols * 32) for _ in range(rows * 32)]
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    out[cy * 32 + ly][cx * 32 + lx] = attrs[ly * 32 + lx]
    return out


def pack(grid):
    h, w = len(grid), len(grid[0])
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            struct.pack_into("<H", out, (y * w + x) * 2, grid[y][x] & 0x3FF)
    return bytes(out)


def open_path(grid, pts, mt=MT_SNOW):
    blocked = set(MT_TREE) | {MT_ROCK, IN_WALL}
    for x, y in pts:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = mt
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] in blocked:
                    grid[ny][nx] = mt


def paint_water(grid, chunks):
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    x, y = cx * 32 + lx, cy * 32 + ly
                    beh = attrs[ly * 32 + lx] & 0xFF
                    if beh in (0x10, 0x15) or 0x11 <= beh <= 0x17:
                        grid[y][x] = MT_WATER


def write_layout(name, w, h, primary, secondary, blob, lid=None):
    folder = LAYOUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.bin").write_bytes(blob)
    src = LAYOUTS / "Route203" / "border.bin"
    (folder / "border.bin").write_bytes(src.read_bytes() if src.exists() else bytes(8))
    if lid is None:
        lid = "LAYOUT_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_")
    meta = json.loads(LAYOUTS_JSON.read_text())
    entry = {
        "id": lid,
        "name": f"{name}_Layout",
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
        if L.get("id") == lid or L.get("name") == entry["name"]:
            layouts[i] = entry
            break
    else:
        layouts.append(entry)
    LAYOUTS_JSON.write_text(json.dumps(meta, indent=2) + "\n")
    print("layout", name, w, h, lid)
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


def ensure_flag(name, value_hex, comment):
    text = FLAGS.read_text()
    if name in text:
        return
    anchor = "FLAG_DEFEATED_SATURN_LAKE_VALOR"
    needle = f"#define {anchor}" if anchor in text else "#define FLAG_RECEIVED_CANALAVE_GYM_TM"
    if needle.split()[-1] in text or needle in text:
        text = text.replace(needle, f"#define {name}  {value_hex} // {comment}\n{needle}", 1)
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
            f"#define {tid}                    {nid} // Sinnoh M25\n\n#define TRAINERS_COUNT_EMERALD",
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
        "Gender: Female" if "CANDICE" in tid else "Gender: Male",
        "Music: Female" if "CANDICE" in tid else "Music: Male",
        "Double Battle: No",
        "AI: Basic Trainer",
        "",
    ]
    for sp, lv in mons:
        lines += [sp, f"Level: {lv}", "IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe", "- Tackle", ""]
    PARTY.write_text(PARTY.read_text().rstrip() + "\n\n" + "\n".join(lines) + "\n")


def party_for(tid, level):
    u = tid.upper()
    if "SKIER" in u or "NINJA" in u:
        return "Ninja Boy", "Ninja Boy", [("Snover", level), ("Sneasel", level - 1)]
    if "ACE" in u:
        return "Cooltrainer", "Cooltrainer M", [("Snorunt", level), ("Piloswine", level)]
    if "GALACTIC" in u or "JUPITER" in u:
        return "Team Aqua", "Aqua Grunt M", [("Zubat", level), ("Bronzor", level)]
    return "Youngster", "Youngster", [("Snover", level), ("Swinub", level)]


def face(d):
    return {
        "DIR_NORTH": "MOVEMENT_TYPE_FACE_UP",
        "DIR_SOUTH": "MOVEMENT_TYPE_FACE_DOWN",
        "DIR_WEST": "MOVEMENT_TYPE_FACE_LEFT",
        "DIR_EAST": "MOVEMENT_TYPE_FACE_RIGHT",
    }.get(d or "", "MOVEMENT_TYPE_FACE_DOWN")


def place_all(em, plat, origin, wmax, hmax, level):
    pe = json.loads((PLAT_MAPS / plat / "events.json").read_text())
    ox, oz = origin
    objs, scripts = [], f"{em}_MapScripts::\n\t.byte 0\n\n"
    occupied = set()
    n = 0
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"] - ox), int(po["z"] - oz)
        if not (0 <= lx < wmax and 0 <= ly < hmax) or (lx, ly) in occupied:
            continue
        tr = po.get("trainer") or {}
        tid_plat = tr.get("id")
        if tid_plat:
            tid = tid_plat if str(tid_plat).startswith("TRAINER_") else f"TRAINER_{tid_plat}"
            cls, pic, mons = party_for(tid, level)
            ensure_trainer(tid, level, cls, pic, mons)
            short = tid.replace("TRAINER_", "").title().replace("_", "")
            label = f"{em}_EventScript_{short}_{n}"
            gfx = GFX.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_MAN_5")
            objs.append(
                obj(gfx, lx, ly, label, trainer="TRAINER_TYPE_NORMAL", sight=str(tr.get("sight_range") or 2), movement=face(po.get("initial_dir")))
            )
            scripts += (
                f"{label}::\n\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
                f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n\tend\n\n"
                f"{label}_Intro:\n\t.string \"Snowpoint winters forge strong teams!\\n\"\n\t.string \"Show me yours!$\"\n\n"
                f"{label}_Defeat:\n\t.string \"Thawed out.$\"\n\n"
                f"{label}_After:\n\t.string \"Candice waits in the Gym.\\n\"\n\t.string \"Ice types hate Fire and Fighting.$\"\n\n"
            )
            n += 1
        else:
            label = f"{em}_EventScript_PlatNpc{n}"
            gfx = GFX.get(po.get("graphics_id") or "", "OBJ_EVENT_GFX_GIRL_1")
            objs.append(obj(gfx, lx, ly, label, movement="MOVEMENT_TYPE_LOOK_AROUND"))
            scripts += (
                f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
                f"{label}_Text:\n\t.string \"Snowpoint never fully thaws.\\n\"\n\t.string \"The Gym mirrors that chill.$\"\n\n"
            )
            n += 1
        occupied.add((lx, ly))
    return objs, scripts, pe


def stamp_door(grid, x, y):
    for dy, row in enumerate([[0x210, 0x211, 0x212], [0x218, 0x219, 0x21A], [0x222, 0x230, 0x221]]):
        for dx, mt in enumerate(row):
            sx, sy = x - 1 + dx, y - 2 + dy
            if 0 <= sy < len(grid) and 0 <= sx < len(grid[0]) and not (sx == x and sy == y):
                grid[sy][sx] = mt
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x] = MT_GRASS


def write_map(name, data, scripts):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("map", name)


def indoor(name, mid, mapsec, exit_map, exit_wid, label, text, gfx="OBJ_EVENT_GFX_OLD_WOMAN"):
    grid = [
        [IN_WALL if y in (0, 7) or x in (0, 9) else (IN_DOOR if y == 7 and x in (4, 5) else IN_FLOOR) for x in range(10)]
        for y in range(8)
    ]
    lid = write_layout(name, 10, 8, "gTileset_Building", "gTileset_GenericBuilding", pack(grid))
    write_map(
        name,
        {
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
            "object_events": [obj(gfx, 4, 3, label)],
            "warp_events": [warp(4, 7, exit_map, exit_wid), warp(5, 7, exit_map, exit_wid)],
            "coord_events": [],
            "bg_events": [],
        },
        f"{name}_MapScripts::\n\t.byte 0\n\n{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n{label}_Text:\n\t.string \"{text}\"\n",
    )


def scrub(names):
    for n in names:
        p = MAPS / n / "scripts.inc"
        if p.exists():
            t = p.read_text()
            if any(ord(c) > 127 for c in t):
                p.write_text("".join(c if ord(c) < 128 else "-" for c in t))


def ensure_avalanche_tm():
    t = TMS.read_text()
    if "F(AVALANCHE)" not in t:
        t = t.replace("F(FLASH_CANNON)", "F(FLASH_CANNON) \\\n    F(AVALANCHE)")
        TMS.write_text(t)
        print("added AVALANCHE TM")


def build_gym():
    ensure_flag("FLAG_RECEIVED_SNOWPOINT_GYM_TM", "0x2AE", "Sinnoh M25 Candice TM")
    ensure_trainer(
        "TRAINER_LEADER_CANDICE",
        40,
        "Leader",
        "Leader Winona",
        [("Sneasel", 38), ("Medicham", 38), ("Abomasnow", 40), ("Froslass", 40)],
        display_name="Candice",
    )
    ensure_trainer("TRAINER_SKIER_SNOWPOINT_A", 35, "Ninja Boy", "Ninja Boy", [("Snorunt", 35)], "Mia")
    ensure_trainer("TRAINER_ACE_SNOWPOINT_B", 36, "Cooltrainer", "Cooltrainer F", [("Sneasel", 36)], "Trina")
    data = {
        "id": "MAP_SNOWPOINT_CITY_GYM",
        "name": "SnowpointCity_Gym",
        "layout": "LAYOUT_PASTORIA_CITY_GYM",
        "music": "MUS_GYM",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_210",
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
            obj("OBJ_EVENT_GFX_WOMAN_5", 12, 4, "SnowpointCity_Gym_EventScript_Candice"),
            obj("OBJ_EVENT_GFX_MAN_2", 8, 34, "SnowpointCity_Gym_EventScript_GymGuide"),
            obj("OBJ_EVENT_GFX_WOMAN_2", 4, 18, "SnowpointCity_Gym_EventScript_Mia", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_RIGHT"),
            obj("OBJ_EVENT_GFX_WOMAN_5", 19, 18, "SnowpointCity_Gym_EventScript_Trina", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        ],
        "warp_events": [warp(12, 39, "MAP_SNOWPOINT_CITY", 0), warp(13, 39, "MAP_SNOWPOINT_CITY", 0)],
        "coord_events": [],
        "bg_events": [
            {"type": "sign", "x": 10, "y": 36, "elevation": 0, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": "SnowpointCity_Gym_EventScript_Statue"},
            {"type": "sign", "x": 13, "y": 36, "elevation": 0, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": "SnowpointCity_Gym_EventScript_Statue"},
        ],
    }
    scripts = r"""SnowpointCity_Gym_MapScripts::
	.byte 0

SnowpointCity_Gym_EventScript_Candice::
	lock
	faceplayer
	trainerbattle_single TRAINER_LEADER_CANDICE, SnowpointCity_Gym_Text_CandiceIntro, SnowpointCity_Gym_Text_CandiceDefeat, SnowpointCity_Gym_EventScript_CandiceDefeated, NO_MUSIC
	goto_if_unset FLAG_RECEIVED_SNOWPOINT_GYM_TM, SnowpointCity_Gym_EventScript_GiveTM
	msgbox SnowpointCity_Gym_Text_CandiceAfter, MSGBOX_DEFAULT
	release
	end

SnowpointCity_Gym_EventScript_CandiceDefeated::
	message SnowpointCity_Gym_Text_ReceivedIcicleBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox SnowpointCity_Gym_Text_IcicleBadgeInfo, MSGBOX_DEFAULT
	setflag FLAG_BADGE07_GET
	goto SnowpointCity_Gym_EventScript_GiveTM
	end

SnowpointCity_Gym_EventScript_GiveTM::
	giveitem ITEM_TM_AVALANCHE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_SNOWPOINT_GYM_TM
	msgbox SnowpointCity_Gym_Text_ExplainTM, MSGBOX_DEFAULT
	release
	end

SnowpointCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_BADGE07_GET, SnowpointCity_Gym_EventScript_GuideVictory
	msgbox SnowpointCity_Gym_Text_GuideAdvice, MSGBOX_DEFAULT
	release
	end

SnowpointCity_Gym_EventScript_GuideVictory::
	msgbox SnowpointCity_Gym_Text_GuideVictory, MSGBOX_DEFAULT
	release
	end

SnowpointCity_Gym_EventScript_Statue::
	lockall
	goto_if_set FLAG_BADGE07_GET, SnowpointCity_Gym_EventScript_StatueWon
	msgbox SnowpointCity_Gym_Text_Statue, MSGBOX_DEFAULT
	releaseall
	end

SnowpointCity_Gym_EventScript_StatueWon::
	msgbox SnowpointCity_Gym_Text_StatueWon, MSGBOX_DEFAULT
	releaseall
	end

SnowpointCity_Gym_EventScript_Mia::
	trainerbattle_single TRAINER_SKIER_SNOWPOINT_A, SnowpointCity_Gym_Text_MiaIntro, SnowpointCity_Gym_Text_MiaDefeat
	msgbox SnowpointCity_Gym_Text_MiaAfter, MSGBOX_AUTOCLOSE
	end

SnowpointCity_Gym_EventScript_Trina::
	trainerbattle_single TRAINER_ACE_SNOWPOINT_B, SnowpointCity_Gym_Text_TrinaIntro, SnowpointCity_Gym_Text_TrinaDefeat
	msgbox SnowpointCity_Gym_Text_TrinaAfter, MSGBOX_AUTOCLOSE
	end

SnowpointCity_Gym_Text_CandiceIntro:
	.string "I'm CANDICE, Snowpoint's Gym Leader!\n"
	.string "Ice types shine when the pressure peaks.\p"
	.string "Let's see if your fire can melt this ice!$"

SnowpointCity_Gym_Text_CandiceDefeat:
	.string "You melted right through...$"

SnowpointCity_Gym_Text_CandiceAfter:
	.string "Lake Acuity still holds Galactic's shadow.\n"
	.string "Stay sharp out there.$"

SnowpointCity_Gym_Text_ReceivedIcicleBadge:
	.string "{PLAYER} received the ICICLE BADGE\n"
	.string "from CANDICE.$"

SnowpointCity_Gym_Text_IcicleBadgeInfo:
	.string "With the ICICLE BADGE, more machines\n"
	.string "answer your POKéMON's strength.$"

SnowpointCity_Gym_Text_ExplainTM:
	.string "That TM is AVALANCHE.\n"
	.string "It hits harder if you took damage first.$"

SnowpointCity_Gym_Text_GuideAdvice:
	.string "CANDICE loves Ice types.\n"
	.string "Fire, Fighting, Rock, and Steel crack ice.$"

SnowpointCity_Gym_Text_GuideVictory:
	.string "You earned the Icicle Badge!\n"
	.string "Snowpoint is proud of that fight.$"

SnowpointCity_Gym_Text_Statue:
	.string "SNOWPOINT CITY POKéMON GYM$"

SnowpointCity_Gym_Text_StatueWon:
	.string "SNOWPOINT CITY POKéMON GYM\p"
	.string "CANDICE'S CERTIFIED TRAINERS:\n"
	.string "{PLAYER}$"

SnowpointCity_Gym_Text_MiaIntro:
	.string "Ski trails lead straight into battle!$"

SnowpointCity_Gym_Text_MiaDefeat:
	.string "Wiped out on the slope...$"

SnowpointCity_Gym_Text_MiaAfter:
	.string "CANDICE trains harder than any blizzard.$"

SnowpointCity_Gym_Text_TrinaIntro:
	.string "Cool strategy beats cold feet!$"

SnowpointCity_Gym_Text_TrinaDefeat:
	.string "Frostbitten pride...$"

SnowpointCity_Gym_Text_TrinaAfter:
	.string "Keep your Fire moves ready for CANDICE.$"
"""
    write_map("SnowpointCity_Gym", data, scripts)


def main():
    ensure_avalanche_tm()
    ensure_flag("FLAG_DEFEATED_JUPITER_LAKE_ACUITY", "0x2AF", "Sinnoh M25 Jupiter at Lake Acuity")
    ensure_flag("FLAG_RECEIVED_SNOWPOINT_GYM_TM", "0x2AE", "Sinnoh M25 Candice TM")

    # Open Route 217 north soft-close: remove blocker script message -> point to Snowpoint
    r217 = json.loads((MAPS / "Route217" / "map.json").read_text())
    # Add north connection to Snowpoint (offset so city sits east-ish)
    conns = r217.get("connections") or []
    conns = [c for c in conns if c.get("map") != "MAP_SNOWPOINT_CITY"]
    conns.append({"map": "MAP_SNOWPOINT_CITY", "offset": -32, "direction": "up"})
    r217["connections"] = conns
    # Remove closed NPC or retarget
    objs = []
    for o in r217.get("object_events") or []:
        if o.get("script") == "Route217_EventScript_SnowpointClosed":
            o["script"] = "Route217_EventScript_SnowpointOpen"
        objs.append(o)
    r217["object_events"] = objs
    (MAPS / "Route217" / "map.json").write_text(json.dumps(r217, indent=2) + "\n")
    sc = (MAPS / "Route217" / "scripts.inc").read_text()
    if "SnowpointOpen" not in sc:
        sc += (
            "\nRoute217_EventScript_SnowpointOpen::\n"
            "\tmsgbox Route217_Text_SnowpointOpen, MSGBOX_NPC\n\tend\n\n"
            'Route217_Text_SnowpointOpen:\n\t.string "The drift cleared!\\n"\n'
            '\t.string "Snowpoint City is just ahead.$"\n'
        )
        # Keep old closed label as alias to open
        sc = sc.replace(
            "Route217_EventScript_SnowpointClosed::\n\tmsgbox Route217_Text_SnowpointClosed, MSGBOX_NPC\n\tend",
            "Route217_EventScript_SnowpointClosed::\n\tgoto Route217_EventScript_SnowpointOpen\n\tend",
        )
        (MAPS / "Route217" / "scripts.inc").write_text(sc)

    # --- Snowpoint City ---
    attr = stitch(SNOWPOINT)
    grid = [[attr_to_mt(attr[y][x], x, y, snow=True) for x in range(32)] for y in range(64)]
    paint_water(grid, SNOWPOINT)
    open_path(grid, [(x, y) for x in range(6, 26) for y in range(8, 56)], mt=MT_SNOW)
    paint_water(grid, SNOWPOINT)
    pe = json.loads((PLAT_MAPS / "snowpoint_city" / "events.json").read_text())
    ox, oz = 352, 192
    door_map = []
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - ox), int(pw["z"] - oz)
        if 0 <= lx < 32 and 0 <= ly < 64:
            stamp_door(grid, lx, ly)
            door_map.append((lx, ly, pw.get("dest_header_id") or ""))
    write_layout("SnowpointCity", 32, 64, "gTileset_General", "gTileset_Fallarbor", pack(grid), "LAYOUT_SNOWPOINT_CITY")
    objs, scripts, _ = place_all("SnowpointCity", "snowpoint_city", (352, 192), 32, 64, 36)

    def find_door(sub, default):
        for lx, ly, dest in door_map:
            if sub in dest.upper():
                return lx, ly
        return default

    gx, gy = find_door("GYM", (15, 30))
    px, py = find_door("POKECENTER", (27, 41))
    mx, my = find_door("MART", (1, 40))
    hx, hy = find_door("WEST_HOUSE", (1, 16))
    ex, ey = find_door("EAST_HOUSE", (27, 16))
    tx, ty = find_door("TEMPLE", (14, 5))
    warps = [
        warp(gx, gy, "MAP_SNOWPOINT_CITY_GYM", 0),
        warp(px, py, "MAP_SNOWPOINT_CITY_POKEMON_CENTER_1F", 0),
        warp(mx, my, "MAP_SNOWPOINT_CITY_MART", 0),
        warp(hx, hy, "MAP_SNOWPOINT_CITY_HOUSE1", 0),
        warp(ex, ey, "MAP_SNOWPOINT_CITY_HOUSE2", 0),
        warp(tx, ty, "MAP_SNOWPOINT_TEMPLE_STUB", 0),
    ]
    snowpoint = {
        "id": "MAP_SNOWPOINT_CITY",
        "name": "SnowpointCity",
        "layout": "LAYOUT_SNOWPOINT_CITY",
        "music": "MUS_PL_JUBILIFE",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_210",
        "requires_flash": False,
        "weather": "WEATHER_SNOW",
        "map_type": "MAP_TYPE_CITY",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [
            {"map": "MAP_ROUTE217", "offset": 32, "direction": "down"},
            {"map": "MAP_ACUITY_LAKEFRONT", "offset": 0, "direction": "left"},
        ],
        "object_events": objs,
        "warp_events": warps,
        "coord_events": [],
        "bg_events": [],
    }
    write_map("SnowpointCity", snowpoint, scripts)

    # --- Acuity Lakefront ---
    attr = stitch(ACUITY_LF)
    grid = [[attr_to_mt(attr[y][x], x, y, snow=True) for x in range(64)] for y in range(64)]
    paint_water(grid, ACUITY_LF)
    open_path(grid, [(x, y) for x in range(8, 56) for y in range(8, 56)], mt=MT_SNOW)
    paint_water(grid, ACUITY_LF)
    write_layout("AcuityLakefront", 64, 64, "gTileset_General", "gTileset_Fallarbor", pack(grid), "LAYOUT_ACUITY_LAKEFRONT")
    objs, scripts, pe = place_all("AcuityLakefront", "acuity_lakefront", (288, 192), 64, 64, 35)
    # Lake entrance warps from platinum
    lake_warps = []
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"] - 288), int(pw["z"] - 192)
        if 0 <= lx < 64 and 0 <= ly < 64 and "LAKE_ACUITY" in (pw.get("dest_header_id") or "").upper():
            lake_warps.append(warp(lx, ly, "MAP_LAKE_ACUITY", 0))
    if len(lake_warps) < 2:
        lake_warps = [warp(20, 37, "MAP_LAKE_ACUITY", 0), warp(21, 37, "MAP_LAKE_ACUITY", 1)]
    acuity_lf = {
        "id": "MAP_ACUITY_LAKEFRONT",
        "name": "AcuityLakefront",
        "layout": "LAYOUT_ACUITY_LAKEFRONT",
        "music": "MUS_PL_ROUTE203",
        "region": "REGION_HOENN",
        "region_map_section": "MAPSEC_ROUTE_210",
        "requires_flash": False,
        "weather": "WEATHER_SNOW",
        "map_type": "MAP_TYPE_ROUTE",
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [
            {"map": "MAP_SNOWPOINT_CITY", "offset": 0, "direction": "right"},
        ],
        "object_events": objs,
        "warp_events": lake_warps[:4],
        "coord_events": [],
        "bg_events": [],
    }
    write_map("AcuityLakefront", acuity_lf, scripts)

    # --- Lake Acuity ---
    attr = stitch(LAKE_ACUITY)
    grid = [[attr_to_mt(attr[y][x], x, y) for x in range(64)] for y in range(64)]
    paint_water(grid, LAKE_ACUITY)
    open_path(grid, [(x, y) for x in range(16, 48) for y in range(16, 48)])
    paint_water(grid, LAKE_ACUITY)
    write_layout("LakeAcuity", 64, 64, "gTileset_General", "gTileset_Pacifidlog", pack(grid), "LAYOUT_LAKE_ACUITY")
    pe = json.loads((PLAT_MAPS / "lake_acuity" / "events.json").read_text())
    objs, scripts = [], "LakeAcuity_MapScripts::\n\t.byte 0\n\n"
    n = 0
    occupied = set()
    for po in pe.get("object_events") or []:
        lx, ly = int(po["x"]), int(po["z"])
        if not (0 <= lx < 64 and 0 <= ly < 64) or (lx, ly) in occupied:
            continue
        label = f"LakeAcuity_EventScript_Npc{n}"
        objs.append(obj("OBJ_EVENT_GFX_MAN_4", lx, ly, label))
        scripts += (
            f"{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n"
            f"{label}_Text:\n\t.string \"Galactic camps still scar the shore.\\n\"\n"
            f"\t.string \"Their Commander was spotted inland.$\"\n\n"
        )
        n += 1
        occupied.add((lx, ly))
    ensure_trainer(
        "TRAINER_COMMANDER_JUPITER_ACUITY",
        39,
        "Team Aqua",
        "Aqua Admin F",
        [("Tangela", 36), ("Skuntank", 38), ("Golbat", 39)],
        display_name="Jupiter",
    )
    objs.append(obj("OBJ_EVENT_GFX_ARCHIE", 32, 28, "LakeAcuity_EventScript_Jupiter"))
    scripts += (
        "LakeAcuity_EventScript_Jupiter::\n"
        "\tlock\n\tfaceplayer\n"
        "\tgoto_if_set FLAG_DEFEATED_JUPITER_LAKE_ACUITY, LakeAcuity_EventScript_JupiterAfter\n"
        "\ttrainerbattle_single TRAINER_COMMANDER_JUPITER_ACUITY, LakeAcuity_Text_JupiterIntro, LakeAcuity_Text_JupiterDefeat, LakeAcuity_EventScript_JupiterDefeated\n"
        "\trelease\n\tend\n\n"
        "LakeAcuity_EventScript_JupiterDefeated::\n"
        "\tsetflag FLAG_DEFEATED_JUPITER_LAKE_ACUITY\n"
        "\tmsgbox LakeAcuity_Text_JupiterAfter, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        "LakeAcuity_EventScript_JupiterAfter::\n"
        "\tmsgbox LakeAcuity_Text_JupiterAfter, MSGBOX_DEFAULT\n"
        "\trelease\n\tend\n\n"
        'LakeAcuity_Text_JupiterIntro:\n\t.string "JUPITER: Three lakes, three keys.\\n"\n'
        '\t.string "You will not halt the next phase.$"\n\n'
        'LakeAcuity_Text_JupiterDefeat:\n\t.string "Impossible...$"\n\n'
        'LakeAcuity_Text_JupiterAfter:\n\t.string "JUPITER: Headquarters will settle this.\\n"\n'
        '\t.string "Veilstone still answers to Galactic.$"\n\n'
    )
    warps = []
    for pw in pe.get("warp_events") or []:
        lx, ly = int(pw["x"]), int(pw["z"])
        dest = (pw.get("dest_header_id") or "").upper()
        if 0 <= lx < 64 and 0 <= ly < 64:
            if "CAVERN" in dest:
                warps.append(warp(lx, ly, "MAP_ACUITY_CAVERN_STUB", 0))
            else:
                warps.append(warp(lx, ly, "MAP_ACUITY_LAKEFRONT", 0))
    if len(warps) < 2:
        warps = [warp(11, 50, "MAP_ACUITY_LAKEFRONT", 0), warp(12, 50, "MAP_ACUITY_LAKEFRONT", 1)]
    write_map(
        "LakeAcuity",
        {
            "id": "MAP_LAKE_ACUITY",
            "name": "LakeAcuity",
            "layout": "LAYOUT_LAKE_ACUITY",
            "music": "MUS_PETALBURG_WOODS",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_210",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_ROUTE",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": objs,
            "warp_events": warps[:5],
            "coord_events": [],
            "bg_events": [],
        },
        scripts,
    )

    # Indoors
    build_gym()
    # Fix gym exit to gym door warp index 0
    indoor("SnowpointCity_House1", "MAP_SNOWPOINT_CITY_HOUSE1", "MAPSEC_ROUTE_210", "MAP_SNOWPOINT_CITY", 3, "SnowpointCity_House1_EventScript_Resident", "Temple climbers warm up here first.\\nDeeper floors stay sealed for now.$")
    indoor("SnowpointCity_House2", "MAP_SNOWPOINT_CITY_HOUSE2", "MAPSEC_ROUTE_210", "MAP_SNOWPOINT_CITY", 4, "SnowpointCity_House2_EventScript_Resident", "Candice trains at dawn on the ice.\\nBring Fire types if you challenge her.$")
    indoor("SnowpointCity_Mart", "MAP_SNOWPOINT_CITY_MART", "MAPSEC_ROUTE_210", "MAP_SNOWPOINT_CITY", 2, "SnowpointCity_Mart_EventScript_Clerk", "Stock healing items before Lake Acuity.\\nGalactic still prowls the shoreline.$", gfx="OBJ_EVENT_GFX_MART_EMPLOYEE")
    # PC
    pc_layout = "LAYOUT_POKEMON_CENTER_1F"
    for cand in ("LAYOUT_SOLACEON_TOWN_POKEMON_CENTER_1F", "LAYOUT_PASTORIA_CITY_POKEMON_CENTER_1F", "LAYOUT_POKEMON_CENTER_1F"):
        if any(L["id"] == cand for L in json.loads(LAYOUTS_JSON.read_text())["layouts"]):
            pc_layout = cand
            break
    write_map(
        "SnowpointCity_PokemonCenter_1F",
        {
            "id": "MAP_SNOWPOINT_CITY_POKEMON_CENTER_1F",
            "name": "SnowpointCity_PokemonCenter_1F",
            "layout": pc_layout,
            "music": "MUS_POKE_CENTER",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_210",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_INDOOR",
            "allow_cycling": False,
            "allow_escaping": False,
            "allow_running": True,
            "show_map_name": False,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [{**obj("OBJ_EVENT_GFX_NURSE", 7, 2, "SnowpointCity_PokemonCenter_1F_EventScript_Nurse"), "local_id": "LOCALID_NURSE"}],
            "warp_events": [warp(7, 8, "MAP_SNOWPOINT_CITY", 1), warp(6, 8, "MAP_SNOWPOINT_CITY", 1)],
            "coord_events": [],
            "bg_events": [],
        },
        "SnowpointCity_PokemonCenter_1F_MapScripts::\n"
        "\tmap_script MAP_SCRIPT_ON_TRANSITION, SnowpointCity_PokemonCenter_1F_OnTransition\n\t.byte 0\n\n"
        "SnowpointCity_PokemonCenter_1F_OnTransition::\n\tsetrespawn HEAL_LOCATION_JUBILIFE_CITY\n\tend\n\n"
        "SnowpointCity_PokemonCenter_1F_EventScript_Nurse::\n"
        "\tsetvar VAR_0x800B, LOCALID_NURSE\n\tcall Common_EventScript_PkmnCenterNurse\n"
        "\twaitmessage\n\twaitbuttonpress\n\trelease\n\tend\n",
    )
    # Temple + cavern stubs (closed beyond)
    cave = [[IN_WALL if y in (0, 9) or x in (0, 11) else (IN_DOOR if y == 9 and x in (5, 6) else IN_FLOOR) for x in range(12)] for y in range(10)]
    write_layout("SnowpointTemple_Stub", 12, 10, "gTileset_General", "gTileset_Cave", pack(cave), "LAYOUT_SNOWPOINT_TEMPLE_STUB")
    write_map(
        "SnowpointTemple_Stub",
        {
            "id": "MAP_SNOWPOINT_TEMPLE_STUB",
            "name": "SnowpointTemple_Stub",
            "layout": "LAYOUT_SNOWPOINT_TEMPLE_STUB",
            "music": "MUS_PETALBURG_WOODS",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_210",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_UNDERGROUND",
            "allow_cycling": False,
            "allow_escaping": True,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [obj("OBJ_EVENT_GFX_HIKER", 6, 3, "SnowpointTemple_Stub_EventScript_Blocked")],
            "warp_events": [warp(5, 9, "MAP_SNOWPOINT_CITY", 5), warp(6, 9, "MAP_SNOWPOINT_CITY", 5)],
            "coord_events": [],
            "bg_events": [],
        },
        "SnowpointTemple_Stub_MapScripts::\n\t.byte 0\n\n"
        "SnowpointTemple_Stub_EventScript_Blocked::\n\tmsgbox SnowpointTemple_Stub_Text, MSGBOX_NPC\n\tend\n\n"
        'SnowpointTemple_Stub_Text:\n\t.string "Lower temple floors stay iced shut.\\n"\n'
        '\t.string "Return after the larger crises pass.$"\n',
    )
    write_layout("AcuityCavern_Stub", 12, 10, "gTileset_General", "gTileset_Cave", pack(cave), "LAYOUT_ACUITY_CAVERN_STUB")
    write_map(
        "AcuityCavern_Stub",
        {
            "id": "MAP_ACUITY_CAVERN_STUB",
            "name": "AcuityCavern_Stub",
            "layout": "LAYOUT_ACUITY_CAVERN_STUB",
            "music": "MUS_PETALBURG_WOODS",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_210",
            "requires_flash": False,
            "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_UNDERGROUND",
            "allow_cycling": False,
            "allow_escaping": True,
            "allow_running": True,
            "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
            "connections": None,
            "object_events": [obj("OBJ_EVENT_GFX_AQUA_MEMBER_M", 6, 3, "AcuityCavern_Stub_EventScript_Blocked")],
            "warp_events": [warp(5, 9, "MAP_LAKE_ACUITY", 1), warp(6, 9, "MAP_LAKE_ACUITY", 1)],
            "coord_events": [],
            "bg_events": [],
        },
        "AcuityCavern_Stub_MapScripts::\n\t.byte 0\n\n"
        "AcuityCavern_Stub_EventScript_Blocked::\n\tmsgbox AcuityCavern_Stub_Text, MSGBOX_NPC\n\tend\n\n"
        'AcuityCavern_Stub_Text:\n\t.string "The cavern collapses further in.\\n"\n'
        '\t.string "Galactic already fled toward Veilstone.$"\n',
    )

    outdoor = ["SnowpointCity", "AcuityLakefront", "LakeAcuity"]
    indoor_names = [
        "SnowpointCity_Gym",
        "SnowpointCity_PokemonCenter_1F",
        "SnowpointCity_Mart",
        "SnowpointCity_House1",
        "SnowpointCity_House2",
        "SnowpointTemple_Stub",
        "AcuityCavern_Stub",
    ]
    g = json.loads(GROUPS.read_text())
    g.setdefault("gMapGroup_TownsAndRoutes", [])
    for n in outdoor:
        if n not in g["gMapGroup_TownsAndRoutes"]:
            g["gMapGroup_TownsAndRoutes"].append(n)
    g.setdefault("gMapGroup_IndoorM25", [])
    for n in indoor_names:
        if n not in g["gMapGroup_IndoorM25"]:
            g["gMapGroup_IndoorM25"].append(n)
    if "group_order" in g and "gMapGroup_IndoorM25" not in g["group_order"]:
        g["group_order"].append("gMapGroup_IndoorM25")
    GROUPS.write_text(json.dumps(g, indent=2) + "\n")

    es = EVENT_SCRIPTS.read_text()
    for n in outdoor + indoor_names + ["Route217"]:
        inc = f'\t.include "data/maps/{n}/scripts.inc"'
        if inc not in es:
            es = es.rstrip() + "\n" + inc + "\n"
    EVENT_SCRIPTS.write_text(es)
    scrub(outdoor + indoor_names + ["Route217"])
    print("M25 build done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
