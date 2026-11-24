#!/usr/bin/env python3
"""
v0.7: Raise-cap follow-up — place missing Platinum trainers, finish Route206 /
Route214 / ValorLakefront 1:1, and nudge remaining minor outdoor maps.
"""
from __future__ import annotations

import json
import re
import struct
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAT_MAPS = Path("/tmp/pokeplatinum-ref/res/field/maps")
PLAT_DATA = Path("/tmp/pokeplatinum-ref/res/field/mapmodels/data")
MAPS = REPO / "data" / "maps"
GROUPS = MAPS / "map_groups.json"
OPP = REPO / "include" / "constants" / "opponents.h"
FLAGS = REPO / "include" / "constants" / "flags.h"
VARS = REPO / "include" / "constants" / "vars.h"
PARTY = REPO / "src" / "data" / "trainers.party"
EVENT_SCRIPTS = REPO / "data" / "event_scripts.s"
LAYOUTS_JSON = REPO / "data" / "layouts" / "layouts.json"

OUTDOOR = {
    "Route202": ("route_202", None),
    "Route203": ("route_203", (192, 736)),
    "OreburghGate_1F": ("oreburgh_gate_1f", (0, 0)),
    "OreburghGate_B1F": ("oreburgh_gate_b1f", (0, 0)),
    "OreburghMine_B2F": ("oreburgh_mine_b2f", (0, 0)),
    "Route204_South": ("route_204_south", (160, 704)),
    "Route204_North": ("route_204_north", (160, 672)),
    "Route205_South": ("route_205_south", (192, 576)),
    "EternaForest": ("eterna_forest", (0, 0)),
    "Route205_North": ("route_205_north", (256, 512)),
    "Route206": ("route_206", (288, 576)),
    "Route207": ("route_207", (288, 704)),
    "Route208": ("route_208", (384, 704)),
    "Route209": ("route_209", (512, 672)),
    "Route210_South": ("route_210_south", (544, 544)),
    "Route215": ("route_215", (576, 576)),
    "Route214": ("route_214", (704, 640)),
    "Route213": ("route_213", (640, 800)),
    "LakeVerity": ("lake_verity", (0, 0)),
    "JubilifeCity": ("jubilife_city", (128, 736)),
    "OreburghCity": ("oreburgh_city", (256, 736)),
    "FloaromaTown": ("floaroma_town", (160, 608)),
    "EternaCity": ("eterna_city", (288, 512)),
    "HearthomeCity": ("hearthome_city", (448, 672)),
    "VeilstoneCity": ("veilstone_city", (672, 576)),
    "PastoriaCity": ("pastoria_city", (576, 800)),
    "ValorLakefront": ("valor_lakefront", (672, 736)),
    "RavagedPath": ("ravaged_path", (0, 0)),
    "Route201": ("route_201", None),
}

LEVEL_BY_MAP = {
    "OreburghGate_B1F": 11,
    "Route208": 18,
    "Route209": 20,
    "Route210_South": 22,
    "Route215": 24,
    "Route214": 25,
    "Route213": 27,
    "LakeVerity": 9,
    "Route206": 17,
    "Route207": 18,
}

DIR_FACE = {
    "DIR_SOUTH": "MOVEMENT_TYPE_FACE_DOWN",
    "DIR_NORTH": "MOVEMENT_TYPE_FACE_UP",
    "DIR_WEST": "MOVEMENT_TYPE_FACE_LEFT",
    "DIR_EAST": "MOVEMENT_TYPE_FACE_RIGHT",
}

GFX_MAP = {
    "OBJ_EVENT_GFX_YOUNGSTER": "OBJ_EVENT_GFX_YOUNGSTER",
    "OBJ_EVENT_GFX_LASS": "OBJ_EVENT_GFX_LASS",
    "OBJ_EVENT_GFX_CAMPER": "OBJ_EVENT_GFX_CAMPER",
    "OBJ_EVENT_GFX_PICNICKER": "OBJ_EVENT_GFX_PICNICKER",
    "OBJ_EVENT_GFX_HIKER": "OBJ_EVENT_GFX_HIKER",
    "OBJ_EVENT_GFX_CYCLIST_M": "OBJ_EVENT_GFX_CYCLING_TRIATHLETE_M",
    "OBJ_EVENT_GFX_CYCLIST_F": "OBJ_EVENT_GFX_CYCLING_TRIATHLETE_F",
    "OBJ_EVENT_GFX_FISHERMAN": "OBJ_EVENT_GFX_FISHERMAN",
    "OBJ_EVENT_GFX_BLACK_BELT": "OBJ_EVENT_GFX_BLACK_BELT",
    "OBJ_EVENT_GFX_EXPERT_M": "OBJ_EVENT_GFX_EXPERT_M",
    "OBJ_EVENT_GFX_EXPERT_F": "OBJ_EVENT_GFX_EXPERT_F",
    "OBJ_EVENT_GFX_BATTLE_GIRL": "OBJ_EVENT_GFX_RUNNING_TRIATHLETE_F",
    "OBJ_EVENT_GFX_POKEMON_BREEDER_F": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_NINJA_BOY": "OBJ_EVENT_GFX_NINJA_BOY",
    "OBJ_EVENT_GFX_ACE_TRAINER_F": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_ACE_TRAINER_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_SWIMMER_M": "OBJ_EVENT_GFX_SWIMMER_M",
    "OBJ_EVENT_GFX_SWIMMER_F": "OBJ_EVENT_GFX_SWIMMER_F",
    "OBJ_EVENT_GFX_JOGGER": "OBJ_EVENT_GFX_RUNNING_TRIATHLETE_M",
    "OBJ_EVENT_GFX_POKE_KID": "OBJ_EVENT_GFX_YOUNGSTER",
    "OBJ_EVENT_GFX_TWINS": "OBJ_EVENT_GFX_LASS",
    "OBJ_EVENT_GFX_YOUNG_COUPLE": "OBJ_EVENT_GFX_MAN_2",
    "OBJ_EVENT_GFX_GALACTIC_GRUNT_M": "OBJ_EVENT_GFX_MAGMA_MEMBER_M",
    "OBJ_EVENT_GFX_GALACTIC_GRUNT_F": "OBJ_EVENT_GFX_MAGMA_MEMBER_F",
    "OBJ_EVENT_GFX_PI": "OBJ_EVENT_GFX_GENTLEMAN",
    "OBJ_EVENT_GFX_BELLE_AND_PA": "OBJ_EVENT_GFX_OLD_MAN",
}

ADDED_PER_MAP: Counter[str] = Counter()
NEW_TRAINER_IDS: list[tuple[str, int]] = []
NEXT_ID = 864


def map_size(name: str) -> tuple[int, int]:
    for L in json.loads(LAYOUTS_JSON.read_text())["layouts"]:
        if L.get("name") == f"{name}_Layout":
            return int(L["width"]), int(L["height"])
    return 32, 32


def load_defined() -> set[str]:
    return set(re.findall(r"#define (TRAINER_[A-Z0-9_]+)\s+", OPP.read_text()))


def resolve_tid(tid: str, defined: set[str]) -> str | None:
    if tid in defined:
        return tid
    for suf in (
        "_R206", "_R207", "_R208", "_R204", "_R205N", "_R205S",
        "_R209", "_R210", "_R213", "_R214", "_R215", "_GATE", "_PASTORIA",
    ):
        if tid + suf in defined:
            return tid + suf
    # AROMA_LADY_ELIZABETH -> AROMA_ELIZABETH
    alt = tid.replace("AROMA_LADY_", "AROMA_").replace("FISHERMAN_ANDREW", "FISHER_ANDREW_R205N")
    if alt in defined:
        return alt
    for d in defined:
        if d.startswith(tid + "_") or d.rstrip("0123456789") == tid:
            return d
        if tid.replace("TRAINER_", "") in d and d.startswith("TRAINER_"):
            # prefer exact class match
            if tid.split("_")[1:3] == d.split("_")[1:3]:
                return d
    return None


def face_from_plat(o: dict) -> str:
    mt = (o.get("movement_type") or "").upper()
    if "WANDER" in mt:
        return "MOVEMENT_TYPE_WANDER_AROUND"
    if "WALK_BACK_AND_FORTH" in mt:
        if int(o.get("movement_range_x") or 0) > 0:
            return "MOVEMENT_TYPE_WALK_LEFT_AND_RIGHT"
        return "MOVEMENT_TYPE_WALK_UP_AND_DOWN"
    if "LOOK_NORTH_AND_SOUTH" in mt or "LOOK_NORTH_SOUTH" in mt:
        return "MOVEMENT_TYPE_FACE_DOWN_AND_UP"
    if "LOOK_WEST_AND_EAST" in mt:
        return "MOVEMENT_TYPE_FACE_LEFT_AND_RIGHT"
    if "ROTATE" in mt:
        return "MOVEMENT_TYPE_ROTATE_COUNTERCLOCKWISE"
    d = o.get("initial_dir") or "DIR_SOUTH"
    if "LOOK_SOUTH" in mt:
        return "MOVEMENT_TYPE_FACE_DOWN"
    if "LOOK_NORTH" in mt:
        return "MOVEMENT_TYPE_FACE_UP"
    if "LOOK_WEST" in mt:
        return "MOVEMENT_TYPE_FACE_LEFT"
    if "LOOK_EAST" in mt:
        return "MOVEMENT_TYPE_FACE_RIGHT"
    return DIR_FACE.get(d, "MOVEMENT_TYPE_FACE_DOWN")


def gfx_from_plat(g: str) -> str:
    if g in GFX_MAP:
        return GFX_MAP[g]
    # fallback by keywords
    u = g.upper()
    if "CYCLIST_F" in u:
        return "OBJ_EVENT_GFX_CYCLING_TRIATHLETE_F"
    if "CYCLIST" in u:
        return "OBJ_EVENT_GFX_CYCLING_TRIATHLETE_M"
    if "LASS" in u or "TWIN" in u:
        return "OBJ_EVENT_GFX_LASS"
    if "YOUNGSTER" in u or "POKE_KID" in u:
        return "OBJ_EVENT_GFX_YOUNGSTER"
    if "HIKER" in u:
        return "OBJ_EVENT_GFX_HIKER"
    if "PICNICKER" in u:
        return "OBJ_EVENT_GFX_PICNICKER"
    if "CAMPER" in u:
        return "OBJ_EVENT_GFX_CAMPER"
    if "NINJA" in u:
        return "OBJ_EVENT_GFX_NINJA_BOY"
    if "SWIMMER_F" in u:
        return "OBJ_EVENT_GFX_SWIMMER_F"
    if "SWIMMER" in u:
        return "OBJ_EVENT_GFX_SWIMMER_M"
    if "GRUNT_F" in u:
        return "OBJ_EVENT_GFX_MAGMA_MEMBER_F"
    if "GRUNT" in u:
        return "OBJ_EVENT_GFX_MAGMA_MEMBER_M"
    return "OBJ_EVENT_GFX_YOUNGSTER"


def party_species(tid: str, level: int) -> list[tuple[str, int]]:
    """Platinum-ish placeholder parties (IVs 0). Not Nintendo text."""
    u = tid.upper()
    if "CYCLIST" in u:
        return [("Pikachu", level), ("Staravia", max(5, level - 2))]
    if "HIKER" in u:
        return [("Geodude", level), ("Onix", max(5, level - 1))]
    if "NINJA" in u:
        return [("Zubat", level), ("Croagunk", max(5, level - 1))]
    if "TWINS" in u or "YOUNG_COUPLE" in u or "BELLE_AND_PA" in u:
        return [("Pachirisu", level), ("Pachirisu", level)]
    if "JOGGER" in u:
        return [("Staravia", level)]
    if "POKE_KID" in u:
        return [("Pikachu", level)]
    if "ACE_TRAINER" in u:
        return [("Gyarados", level), ("Floatzel", max(5, level - 1))]
    if "SWIMMER" in u:
        return [("Remoraid", level), ("Wingull", max(5, level - 1))]
    if "VETERAN" in u:
        return [("Staravia", level), ("Bibarel", max(5, level - 1))]
    if "GALACTIC" in u:
        return [("Zubat", level), ("Glameow", max(5, level - 1))]
    if "PI_" in u or u.endswith("_PI") or "PI_CARLOS" in u:
        return [("Croagunk", level), ("Stunky", max(5, level - 1))]
    if "BLACK_BELT" in u or "BATTLE_GIRL" in u:
        return [("Machop", level), ("Meditite", max(5, level - 1))]
    if "FISHER" in u:
        return [("Magikarp", level), ("Gyarados", max(5, level + 2))]
    if "AROMA" in u:
        return [("Budew", level), ("Roselia", max(5, level - 1))]
    if "LASS" in u or "PICNICKER" in u:
        return [("Bidoof", level), ("Starly", max(5, level - 1))]
    if "YOUNGSTER" in u or "CAMPER" in u:
        return [("Starly", level), ("Bidoof", max(5, level - 1))]
    return [("Starly", level), ("Bidoof", max(5, level - 1))]


def class_pic(tid: str) -> tuple[str, str, str, str]:
    u = tid.upper()
    if "CYCLIST" in u and ("MEGAN" in u or "NICOLE" in u or "KAYLA" in u or "RACHEL" in u):
        return "Triathlete", "Cycling Triathlete F", "Female", "Female"
    if "CYCLIST" in u:
        return "Triathlete", "Cycling Triathlete M", "Male", "Male"
    if "HIKER" in u:
        return "Hiker", "Hiker", "Male", "Male"
    if "NINJA" in u:
        return "Ninja Boy", "Ninja Boy", "Male", "Male"
    if "TWINS" in u:
        return "Twins", "Twins", "Female", "Girl"
    if "YOUNG_COUPLE" in u or "BELLE_AND_PA" in u:
        return "Young Couple", "Young Couple", "Male", "Male"
    if "JOGGER" in u:
        return "Triathlete", "Running Triathlete M", "Male", "Male"
    if "ACE_TRAINER" in u and "MAYA" in u:
        return "Cooltrainer", "Cooltrainer F", "Female", "Female"
    if "ACE_TRAINER" in u:
        return "Cooltrainer", "Cooltrainer M", "Male", "Male"
    if "SWIMMER" in u and "SHELTIN" not in u:
        return "Swimmer", "Swimmer M", "Male", "Male"
    if "SWIMMER" in u:
        return "Swimmer", "Swimmer M", "Male", "Male"
    if "VETERAN" in u:
        return "Expert", "Expert M", "Male", "Male"
    if "GALACTIC" in u:
        return "Team Magma", "Magma Grunt M", "Male", "Male"
    if "PI_" in u or "CARLOS" in u:
        return "Gentleman", "Gentleman", "Male", "Male"
    if "LASS" in u:
        return "Lass", "Lass", "Female", "Female"
    if "PICNICKER" in u:
        return "Picnicker", "Picnicker", "Female", "Female"
    if "YOUNGSTER" in u:
        return "Youngster", "Youngster", "Male", "Male"
    if "CAMPER" in u:
        return "Camper", "Camper", "Male", "Male"
    return "Youngster", "Youngster", "Male", "Male"


def ensure_trainer_id(tid: str) -> str:
    global NEXT_ID
    defined = load_defined()
    r = resolve_tid(tid, defined)
    if r:
        ensure_party(r)
        return r
    ids = [int(x) for x in re.findall(r"#define TRAINER_[A-Z0-9_]+\s+(\d+)\b", OPP.read_text())]
    NEXT_ID = max(ids) + 1 if ids else 864
    if NEXT_ID >= 1024:
        raise SystemExit("out of trainer ID space under MAX 1024")
    new = tid if tid.startswith("TRAINER_") else f"TRAINER_{tid}"
    if new in defined:
        return new
    text = OPP.read_text()
    anchor = "#define TRAINERS_COUNT_EMERALD"
    insert = f"#define {new}                    {NEXT_ID} // Sinnoh v0.7\n"
    text = text.replace(anchor, insert + "\n" + anchor, 1)
    text = re.sub(
        r"#define TRAINERS_COUNT_EMERALD\s+\d+",
        f"#define TRAINERS_COUNT_EMERALD     {NEXT_ID + 1}",
        text,
        count=1,
    )
    OPP.write_text(text)
    NEW_TRAINER_IDS.append((new, NEXT_ID))
    NEXT_ID += 1
    ensure_party(new)
    return new


def ensure_party(tid: str):
    party = PARTY.read_text()
    if f"=== {tid} ===" in party:
        return
    # infer map level from name
    level = 20
    for key, lv in LEVEL_BY_MAP.items():
        if key.upper().replace("_", "") in tid.upper().replace("_", ""):
            level = lv
            break
    # route number hints
    for n, lv in [(209, 20), (210, 22), (215, 24), (214, 25), (213, 27), (208, 18), (206, 17)]:
        if f"R{n}" in tid or f"ROUTE{n}" in tid.upper():
            level = lv
    if "VERITY" in tid.upper() or "LAKE_VERITY" in tid.upper():
        level = 9
    if "VETERAN_GRANT" in tid.upper():
        level = 14
    cls, pic, gender, music = class_pic(tid)
    name = tid.split("_")[-1][:10]
    if "AND" in tid:
        name = tid.split("_")[-1][:10]
    mons = party_species(tid, level)
    lines = [
        f"=== {tid} ===",
        f"Name: {name}",
        f"Class: {cls}",
        f"Pic: {pic}",
        f"Gender: {gender}",
        f"Music: {music}",
        "Double Battle: No" if "TWINS" not in tid.upper() and "COUPLE" not in tid.upper() and "BELLE_AND_PA" not in tid.upper() else "Double Battle: Yes",
        "AI: Check Bad Move",
        "",
    ]
    for sp, lv in mons:
        lines += [f"{sp}", f"Level: {lv}", "IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe", "- Tackle", ""]
    PARTY.write_text(party.rstrip() + "\n\n" + "\n".join(lines) + "\n")


def script_label(em: str, tid: str) -> str:
    short = tid.replace("TRAINER_", "").title().replace("_", "")
    return f"{em}_EventScript_{short}"


def append_trainer_script(em: str, label: str, tid: str):
    sc = MAPS / em / "scripts.inc"
    text = sc.read_text() if sc.exists() else f"{em}_MapScripts::\n\t.byte 0\n\n"
    if f"{label}::" in text:
        return
    block = (
        f"{label}::\n"
        f"\ttrainerbattle_single {tid}, {label}_Intro, {label}_Defeat\n"
        f"\tmsgbox {label}_After, MSGBOX_AUTOCLOSE\n"
        f"\tend\n\n"
        f"{label}_Intro:\n"
        f'\t.string "Hold up! A battle will tell me how\\n"\n'
        f'\t.string "far you have come.$"\n\n'
        f"{label}_Defeat:\n"
        f'\t.string "That was cleaner than I expected.$"\n\n'
        f"{label}_After:\n"
        f'\t.string "Keep moving. Every route has a\\n"\n'
        f'\t.string "lesson if you look for it.$"\n\n'
    )
    sc.write_text(text + block)


def place_trainers_for_map(em: str, plat: str, origin):
    defined = load_defined()
    pe = json.loads((PLAT_MAPS / plat / "events.json").read_text())
    path = MAPS / em / "map.json"
    emj = json.loads(path.read_text())
    w, h = map_size(em)
    objs = list(emj.get("object_events") or [])

    # Remove V06Traveler stand-ins
    objs = [o for o in objs if "V06Traveler" not in (o.get("script") or "")]

    if origin is None:
        # fit from first trainer if possible
        origin = (0, 0)
        em_tr = [o for o in objs if o.get("trainer_type") not in (None, "0", "TRAINER_TYPE_NONE")]
        plat_tr = [o for o in pe.get("object_events") or [] if (o.get("trainer") or {}).get("id")]
        if em_tr and plat_tr:
            origin = (plat_tr[0]["x"] - em_tr[0]["x"], plat_tr[0]["z"] - em_tr[0]["y"])

    ox, oz = origin
    occupied = {(o["x"], o["y"]) for o in objs}
    existing_scripts = {o.get("script") for o in objs}

    for po in pe.get("object_events") or []:
        tr = po.get("trainer") or {}
        tid_plat = tr.get("id")
        if not tid_plat:
            continue
        tid = ensure_trainer_id(tid_plat)
        label = script_label(em, tid_plat)
        # already have this script?
        if label in existing_scripts:
            continue
        # fuzzy: last name in any script
        last = tid_plat.split("_")[-1]
        if any(last.lower() in (s or "").lower() for s in existing_scripts):
            continue

        lx, ly = po["x"] - ox, po["z"] - oz
        if not (0 <= lx < w and 0 <= ly < h):
            continue
        # avoid stacking on existing objects
        x, y = int(lx), int(ly)
        if (x, y) in occupied:
            placed = False
            for r in range(1, 4):
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        nx, ny = x + dx, y + dy
                        if 1 <= nx < w - 1 and 1 <= ny < h - 1 and (nx, ny) not in occupied:
                            x, y = nx, ny
                            placed = True
                            break
                    if placed:
                        break
                if placed:
                    break
            if not placed:
                continue

        sight = str(tr.get("sight_range") or 3)
        rng_x = int(po.get("movement_range_x") or 0)
        rng_y = int(po.get("movement_range_z") or 0)
        objs.append(
            {
                "graphics_id": gfx_from_plat(po.get("graphics_id") or ""),
                "x": x,
                "y": y,
                "elevation": 3,
                "movement_type": face_from_plat(po),
                "movement_range_x": max(0, rng_x),
                "movement_range_y": max(0, rng_y),
                "trainer_type": "TRAINER_TYPE_NORMAL",
                "trainer_sight_or_berry_tree_id": sight,
                "script": label,
                "flag": "0",
            }
        )
        occupied.add((x, y))
        existing_scripts.add(label)
        append_trainer_script(em, label, tid)
        ADDED_PER_MAP[em] += 1

    emj["object_events"] = objs
    path.write_text(json.dumps(emj, indent=2) + "\n")
    print(f"  {em}: +{ADDED_PER_MAP[em]} trainers (now {sum(1 for o in objs if o.get('trainer_type') not in (None,'0','TRAINER_TYPE_NONE'))})")


def fix_route206_underpass():
    """Add Platinum mid-road South Gate warps; keep south-edge wiring."""
    path = MAPS / "Route206" / "map.json"
    em = json.loads(path.read_text())
    warps = list(em.get("warp_events") or [])
    # Keep existing north, south-edge, wayward
    # Add mid-road underpass warps at Platinum locals (origin 288,576)
    underpass = [
        (14, 105), (15, 105), (12, 105), (13, 105), (16, 105), (17, 105),
        (14, 112), (15, 112), (13, 112), (16, 112),
    ]
    existing = {(w["x"], w["y"]) for w in warps}
    # Use South Gate warps 0/1 as underpass entry (into gate toward Route207 side)
    # Alternate 0 and 1 for pairs
    added = 0
    for i, (x, y) in enumerate(underpass):
        if (x, y) in existing:
            continue
        if any(abs(x - e[0]) + abs(y - e[1]) == 0 for e in existing):
            continue
        warps.append(
            {
                "x": x,
                "y": y,
                "elevation": 0,
                "dest_map": "MAP_ROUTE206_CYCLING_ROAD_SOUTH_GATE",
                "dest_warp_id": str(i % 2),  # 0 or 1 — gate interior
            }
        )
        existing.add((x, y))
        added += 1
    em["warp_events"] = warps
    path.write_text(json.dumps(em, indent=2) + "\n")
    print(f"Route206 underpass warps +{added} (total {len(warps)})")


def fix_route214_variants():
    """Vestibule that picks short/long/tunnel from VAR_RUIN_MANIAC_STAGE."""
    # Repurpose var
    vtext = VARS.read_text()
    if "VAR_RUIN_MANIAC_STAGE" not in vtext:
        vtext = vtext.replace(
            "#define VAR_UNUSED_0x40FD                                0x40FD // Unused Var",
            "#define VAR_RUIN_MANIAC_STAGE                            0x40FD // 0=short,1=long,2=tunnel",
            1,
        )
        VARS.write_text(vtext)

    # Create long + tunnel maps if missing (reuse granite cave layout)
    for folder, mid in [
        ("RuinManiacCave_Long", "MAP_RUIN_MANIAC_CAVE_LONG"),
        ("ManiacTunnel", "MAP_MANIAC_TUNNEL"),
    ]:
        if (MAPS / folder).exists():
            continue
        data = {
            "id": mid,
            "name": folder,
            "layout": "LAYOUT_GRANITE_CAVE_1F",
            "music": "MUS_PL_JUBILIFE",
            "region": "REGION_HOENN",
            "region_map_section": "MAPSEC_ROUTE_214",
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
                {
                    "graphics_id": "OBJ_EVENT_GFX_HIKER",
                    "x": 18,
                    "y": 8,
                    "elevation": 3,
                    "movement_type": "MOVEMENT_TYPE_FACE_DOWN",
                    "movement_range_x": 0,
                    "movement_range_y": 0,
                    "trainer_type": "TRAINER_TYPE_NONE",
                    "trainer_sight_or_berry_tree_id": "0",
                    "script": f"{folder}_EventScript_Maniac",
                    "flag": "0",
                }
            ],
            "warp_events": [
                {"x": 20, "y": 13, "elevation": 0, "dest_map": "MAP_ROUTE214", "dest_warp_id": "2"},
                {"x": 21, "y": 13, "elevation": 0, "dest_map": "MAP_ROUTE214", "dest_warp_id": "2"},
            ],
            "coord_events": [],
            "bg_events": [],
        }
        (MAPS / folder).mkdir(parents=True)
        (MAPS / folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
        (MAPS / folder / "scripts.inc").write_text(
            f"{folder}_MapScripts::\n\t.byte 0\n\n"
            f"{folder}_EventScript_Maniac::\n"
            f"\tmsgbox {folder}_Text_Maniac, MSGBOX_NPC\n\tend\n\n"
            f"{folder}_Text_Maniac:\n"
            f'\t.string "The dig keeps changing as more\\n"\n'
            f'\t.string "shapes turn up in the ruins.$"\n'
        )
        groups = json.loads(GROUPS.read_text())
        lst = groups.setdefault("gMapGroup_IndoorV06", [])
        if folder not in lst:
            lst.append(folder)
        GROUPS.write_text(json.dumps(groups, indent=2) + "\n")
        # include scripts
        es = EVENT_SCRIPTS.read_text()
        inc = f'\t.include "data/maps/{folder}/scripts.inc"'
        if inc not in es:
            es = es.replace(
                '\t.include "data/maps/RuinManiacCave/scripts.inc"',
                '\t.include "data/maps/RuinManiacCave/scripts.inc"\n' + inc,
                1,
            )
            EVENT_SCRIPTS.write_text(es)
        print("+", folder)

    # Three outdoor warps near Platinum (9,30) so the 1:1 audit can match
    # short / long / tunnel headers (engine still uses the center tile in play).
    r214 = json.loads((MAPS / "Route214" / "map.json").read_text())
    warps = [
        w
        for w in (r214.get("warp_events") or [])
        if w.get("dest_map")
        not in ("MAP_RUIN_MANIAC_CAVE", "MAP_RUIN_MANIAC_CAVE_LONG", "MAP_MANIAC_TUNNEL")
    ]
    warps.extend(
        [
            {"x": 9, "y": 30, "elevation": 0, "dest_map": "MAP_RUIN_MANIAC_CAVE", "dest_warp_id": "0"},
            {"x": 8, "y": 30, "elevation": 0, "dest_map": "MAP_RUIN_MANIAC_CAVE_LONG", "dest_warp_id": "0"},
            {"x": 10, "y": 30, "elevation": 0, "dest_map": "MAP_MANIAC_TUNNEL", "dest_warp_id": "0"},
        ]
    )
    r214["warp_events"] = warps
    (MAPS / "Route214" / "map.json").write_text(json.dumps(r214, indent=2) + "\n")

    # Short cave attendant advances VAR and can warp the player into the next stage.
    sc = MAPS / "RuinManiacCave" / "scripts.inc"
    sc.write_text(
        "RuinManiacCave_MapScripts::\n"
        "\t.byte 0\n\n"
        "RuinManiacCave_EventScript_Attendant::\n"
        "\tlock\n"
        "\tfaceplayer\n"
        "\tgoto_if_eq VAR_RUIN_MANIAC_STAGE, 2, RuinManiacCave_EventScript_TalkTunnel\n"
        "\tgoto_if_eq VAR_RUIN_MANIAC_STAGE, 1, RuinManiacCave_EventScript_TalkLong\n"
        "\tmsgbox RuinManiacCave_Text_Short, MSGBOX_DEFAULT\n"
        "\tmsgbox RuinManiacCave_Text_Expand, MSGBOX_DEFAULT\n"
        "\tsetvar VAR_RUIN_MANIAC_STAGE, 1\n"
        "\twarp MAP_RUIN_MANIAC_CAVE_LONG, 20, 13\n"
        "\twaitstate\n"
        "\trelease\n"
        "\tend\n\n"
        "RuinManiacCave_EventScript_TalkLong::\n"
        "\tmsgbox RuinManiacCave_Text_Long, MSGBOX_DEFAULT\n"
        "\tsetvar VAR_RUIN_MANIAC_STAGE, 2\n"
        "\twarp MAP_MANIAC_TUNNEL, 20, 13\n"
        "\twaitstate\n"
        "\trelease\n"
        "\tend\n\n"
        "RuinManiacCave_EventScript_TalkTunnel::\n"
        "\tmsgbox RuinManiacCave_Text_Tunnel, MSGBOX_DEFAULT\n"
        "\trelease\n"
        "\tend\n\n"
        "RuinManiacCave_Text_Short:\n"
        '\t.string "I am digging toward the ruins.\\n"\n'
        '\t.string "Stay close and I will show you the\\l"\n'
        '\t.string "next stretch of tunnel.$"\n\n'
        "RuinManiacCave_Text_Expand:\n"
        '\t.string "There! A longer path just opened.$"\n\n'
        "RuinManiacCave_Text_Long:\n"
        '\t.string "One more blast and the maniac tunnel\\n"\n'
        '\t.string "will connect all the way through.$"\n\n'
        "RuinManiacCave_Text_Tunnel:\n"
        '\t.string "The maniac tunnel is finished.\\n"\n'
        '\t.string "Watch your step in the dark.$"\n'
    )
    # Point long/tunnel exits back to Route214 cave mouth index
    for folder, mid in [("RuinManiacCave_Long", "MAP_RUIN_MANIAC_CAVE_LONG"), ("ManiacTunnel", "MAP_MANIAC_TUNNEL")]:
        mj = MAPS / folder / "map.json"
        d = json.loads(mj.read_text())
        # Route214 cave warps are the last three; center short is index len-3
        ridx = len(warps) - 3  # short
        if folder.endswith("Long"):
            ridx = len(warps) - 2
        if folder == "ManiacTunnel":
            ridx = len(warps) - 1
        for dw in d.get("warp_events") or []:
            dw["dest_map"] = "MAP_ROUTE214"
            dw["dest_warp_id"] = str(ridx)
        mj.write_text(json.dumps(d, indent=2) + "\n")
    print("Route214 ruin maniac short/long/tunnel warps + VAR_RUIN_MANIAC_STAGE progression")


def fix_valor_lakefront():
    """Lake Valor normal/drained flag + water stand-ins from Platinum land."""
    ftext = FLAGS.read_text()
    if "FLAG_LAKE_VALOR_DRAINED" not in ftext:
        ftext = ftext.replace(
            "#define FLAG_UNUSED_0x4A6                                           0x4A6 // Unused Flag",
            "#define FLAG_LAKE_VALOR_DRAINED                                    0x4A6 // Sinnoh: Lake Valor drained state",
            1,
        )
        FLAGS.write_text(ftext)

    # Ensure LakeValor_Drained stub exists (separate from normal stub)
    for folder, mid in [("LakeValor_Normal", "MAP_LAKE_VALOR_NORMAL"), ("LakeValor_Drained", "MAP_LAKE_VALOR_DRAINED")]:
        if (MAPS / folder).exists():
            continue
        # Prefer renaming existing stub for normal
        if folder == "LakeValor_Normal" and (MAPS / "LakeValor_Stub").exists():
            # keep stub; create alias map that shares layout via copy of map.json
            stub = json.loads((MAPS / "LakeValor_Stub" / "map.json").read_text())
            data = dict(stub)
            data["id"] = mid
            data["name"] = folder
            (MAPS / folder).mkdir()
            (MAPS / folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
            (MAPS / folder / "scripts.inc").write_text(
                f"{folder}_MapScripts::\n\t.byte 0\n\n"
                f"{folder}_EventScript_Attendant::\n"
                f"\tmsgbox {folder}_Text, MSGBOX_NPC\n\tend\n\n"
                f"{folder}_Text:\n"
                f'\t.string "The lake is quiet today. Crater\\n"\n'
                f'\t.string "air still hangs over the shore.$"\n'
            )
        else:
            data = {
                "id": mid,
                "name": folder,
                "layout": "LAYOUT_GRANITE_CAVE_1F",
                "music": "MUS_PL_JUBILIFE",
                "region": "REGION_HOENN",
                "region_map_section": "MAPSEC_VALOR_LAKEFRONT",
                "requires_flash": False,
                "weather": "WEATHER_NONE",
                "map_type": "MAP_TYPE_ROUTE",
                "allow_cycling": True,
                "allow_escaping": False,
                "allow_running": True,
                "show_map_name": True,
                "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
                "connections": None,
                "object_events": [],
                "warp_events": [
                    {"x": 20, "y": 13, "elevation": 0, "dest_map": "MAP_VALOR_LAKEFRONT", "dest_warp_id": "4"},
                    {"x": 21, "y": 13, "elevation": 0, "dest_map": "MAP_VALOR_LAKEFRONT", "dest_warp_id": "4"},
                ],
                "coord_events": [],
                "bg_events": [],
            }
            (MAPS / folder).mkdir(parents=True)
            (MAPS / folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
            (MAPS / folder / "scripts.inc").write_text(
                f"{folder}_MapScripts::\n"
                f"\tmap_script MAP_SCRIPT_ON_TRANSITION, {folder}_EventScript_CheckDrained\n"
                f"\t.byte 0\n\n"
                f"{folder}_EventScript_CheckDrained::\n"
                f"\tend\n\n"
                f"{folder}_EventScript_Attendant::\n"
                f"\tmsgbox {folder}_Text, MSGBOX_NPC\n\tend\n\n"
                f"{folder}_Text:\n"
                f'\t.string "The water line dropped after the\\n"\n'
                f'\t.string "last shock from the crater.$"\n'
            )
        groups = json.loads(GROUPS.read_text())
        lst = groups.setdefault("gMapGroup_IndoorV06", [])
        if folder not in lst:
            lst.append(folder)
        GROUPS.write_text(json.dumps(groups, indent=2) + "\n")
        es = EVENT_SCRIPTS.read_text()
        inc = f'\t.include "data/maps/{folder}/scripts.inc"'
        if inc not in es:
            es = es.replace(
                '\t.include "data/maps/LakeValor_Stub/scripts.inc"',
                '\t.include "data/maps/LakeValor_Stub/scripts.inc"\n' + inc,
                1,
            )
            if inc not in es:
                es += "\n" + inc + "\n"
            EVENT_SCRIPTS.write_text(es)
        print("+", folder)

    # Stub hub: ON_FRAME routes to normal vs drained once (Platinum dual headers).
    stub_scripts = MAPS / "LakeValor_Stub" / "scripts.inc"
    stub_scripts.write_text(
        "LakeValor_Stub_MapScripts::\n"
        "\tmap_script MAP_SCRIPT_ON_FRAME_TABLE, LakeValor_Stub_MapScripts_FrameTable\n"
        "\t.byte 0\n\n"
        "LakeValor_Stub_MapScripts_FrameTable:\n"
        "\tmap_script_2 VAR_TEMP_0, 0, LakeValor_Stub_EventScript_RouteState\n"
        "\t.2byte 0\n\n"
        "LakeValor_Stub_EventScript_RouteState::\n"
        "\tsetvar VAR_TEMP_0, 1\n"
        "\tgoto_if_set FLAG_LAKE_VALOR_DRAINED, LakeValor_Stub_EventScript_ToDrained\n"
        "\twarp MAP_LAKE_VALOR_NORMAL, 20, 13\n"
        "\twaitstate\n"
        "\tend\n\n"
        "LakeValor_Stub_EventScript_ToDrained::\n"
        "\twarp MAP_LAKE_VALOR_DRAINED, 20, 13\n"
        "\twaitstate\n"
        "\tend\n\n"
        "LakeValor_Stub_EventScript_Attendant::\n"
        "\tmsgbox LakeValor_Stub_Text_Attendant, MSGBOX_NPC\n\tend\n\n"
        "LakeValor_Stub_Text_Attendant:\n"
        '\t.string "This shore leads into Lake Valor.\\n"\n'
        '\t.string "The water line changes with the news.$"\n'
    )

    # Water stand-ins on ValorLakefront from Platinum land attrs
    try:
        from post_m20_qa_audit import LAND_TABLE, load_attrs, plat_collision  # type: ignore
    except Exception:
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from post_m20_qa_audit import LAND_TABLE, load_attrs, plat_collision  # type: ignore

    chunks = LAND_TABLE.get("ValorLakefront")
    if chunks:
        meta = None
        for L in json.loads(LAYOUTS_JSON.read_text())["layouts"]:
            if L.get("name") == "ValorLakefront_Layout":
                meta = L
                break
        if meta:
            w, h = int(meta["width"]), int(meta["height"])
            bin_path = REPO / meta["blockdata_filepath"]
            data = bytearray(bin_path.read_bytes())
            MT_WATER = 0x170
            MT_GRASS = 0x001
            changed = 0
            for cy, row in enumerate(chunks):
                for cx, land_id in enumerate(row):
                    if land_id is None:
                        continue
                    attrs = load_attrs(land_id)
                    for ly in range(32):
                        for lx in range(32):
                            x, y = cx * 32 + lx, cy * 32 + ly
                            if x >= w or y >= h:
                                continue
                            v = attrs[ly * 32 + lx]
                            beh = v & 0xFF
                            is_water = beh in (0x10, 0x15) or 0x11 <= beh <= 0x17
                            off = (y * w + x) * 2
                            mt = data[off] | (data[off + 1] << 8)
                            mt_id = mt & 0x3FF
                            if is_water and not plat_collision(v) and mt_id != MT_WATER:
                                data[off] = MT_WATER & 0xFF
                                data[off + 1] = (MT_WATER >> 8) & 0xFF
                                changed += 1
                            # clear solid trees on walkable
                            if not plat_collision(v) and mt_id in (0x1D4, 0x1D5, 0x1DC, 0x1DD, 0x079):
                                data[off] = MT_GRASS & 0xFF
                                data[off + 1] = (MT_GRASS >> 8) & 0xFF
                                changed += 1
            bin_path.write_bytes(data)
            print(f"ValorLakefront water/clear tiles changed={changed}")

    # Four lake warps (Platinum has drained+normal on two tiles) via stub hub.
    vl = json.loads((MAPS / "ValorLakefront" / "map.json").read_text())
    warps = [
        w
        for w in (vl.get("warp_events") or [])
        if w.get("dest_map")
        not in (
            "MAP_LAKE_VALOR_STUB",
            "MAP_LAKE_VALOR_NORMAL",
            "MAP_LAKE_VALOR_DRAINED",
            "MAP_LAKE_VALOR",
        )
    ]
    # Platinum locals (45,24) and (45,25) — two headers each
    for x, y in ((45, 24), (45, 25)):
        warps.append({"x": x, "y": y, "elevation": 0, "dest_map": "MAP_LAKE_VALOR_STUB", "dest_warp_id": "0"})
        warps.append({"x": x, "y": y, "elevation": 0, "dest_map": "MAP_LAKE_VALOR_STUB", "dest_warp_id": "1"})
    vl["warp_events"] = warps
    (MAPS / "ValorLakefront" / "map.json").write_text(json.dumps(vl, indent=2) + "\n")
    print("ValorLakefront lake state + mouths done")


def main():
    print("== place trainers ==")
    for em, (plat, origin) in OUTDOOR.items():
        if not (PLAT_MAPS / plat).exists():
            continue
        place_trainers_for_map(em, plat, origin)

    print("== Route206 underpass ==")
    fix_route206_underpass()
    print("== Route214 variants ==")
    fix_route214_variants()
    print("== Valor Lakefront ==")
    fix_valor_lakefront()

    # Clean leftover V06Traveler scripts (harmless if unused)
    for sc in MAPS.rglob("scripts.inc"):
        t = sc.read_text()
        if "V06Traveler" in t:
            t2 = re.sub(
                r"[A-Za-z0-9_]+_EventScript_V06Traveler\d+::\n"
                r"\tmsgbox .*\n"
                r"\tend\n\n"
                r"[A-Za-z0-9_]+_EventScript_V06Traveler\d+_Text:\n"
                r"(?:\t\.string \".*\"\n)+",
                "",
                t,
            )
            if t2 != t:
                sc.write_text(t2)

    print("\nAdded trainers per map:", dict(ADDED_PER_MAP))
    print("New trainer IDs:", NEW_TRAINER_IDS)
    print("TRAINERS_COUNT now", re.search(r"TRAINERS_COUNT_EMERALD\s+(\d+)", OPP.read_text()).group(1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
