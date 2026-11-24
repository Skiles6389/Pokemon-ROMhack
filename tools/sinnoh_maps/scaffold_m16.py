#!/usr/bin/env python3
"""Scaffold M16 map.json/scripts.inc, constants, wilds, trainers, groups."""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data" / "maps"
TRAINERS = json.loads(Path("/tmp/m16_trainers.json").read_text())

# Emerald-friendly string cleanup
def e_str(s: str) -> str:
    s = s.replace("Pokémon", "POKéMON").replace("Pokédex", "POKéDEX")
    s = s.replace("Pokétch", "POKéDEX").replace("’", "'").replace("–", "-").replace("—", "-")
    s = s.replace("…", "...").replace("é", "e")  # keep POKeMON already fixed
    # undo over-aggressive e on POKeMON
    s = s.replace("POKeMON", "POKéMON").replace("POKeDEX", "POKéDEX").replace("POKe BALL", "POKé BALL")
    return s


def asm_string(label: str, text: str) -> str:
    text = e_str(text).strip("\n")
    # Split into lines for .string with \n and \p
    paragraphs = [p for p in re.split(r"\n\n+", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]
    parts = []
    for pi, para in enumerate(paragraphs):
        lines = para.split("\n")
        for i, line in enumerate(lines):
            line = line.replace('"', "'")
            if i < len(lines) - 1:
                parts.append(line + "\\n")
            else:
                if pi < len(paragraphs) - 1:
                    parts.append(line + "\\p")
                else:
                    parts.append(line + "$")
    # Build .string blocks - join with quotes carefully
    out = [f"{label}:"]
    # Rebuild as single .string with \n/\p
    buf = ""
    for p in parts:
        buf += p
    # Split long strings at \p boundaries for readability
    chunks = buf.split("\\p")
    for i, chunk in enumerate(chunks):
        if i < len(chunks) - 1:
            chunk = chunk + "\\p"
        # further split by \n into .string lines of max ~2 lines
        out.append(f'\t.string "{chunk}"')
    return "\n".join(out)


def obj(gfx, x, y, script, trainer="TRAINER_TYPE_NONE", sight="0", flag="0", movement="MOVEMENT_TYPE_FACE_DOWN", local_id=None):
    o = {
        "graphics_id": gfx,
        "x": x,
        "y": y,
        "elevation": 3,
        "movement_type": movement,
        "movement_range_x": 0,
        "movement_range_y": 0,
        "trainer_type": trainer,
        "trainer_sight_or_berry_tree_id": str(sight),
        "script": script,
        "flag": flag,
    }
    if local_id:
        o["local_id"] = local_id
    return o


def warp(x, y, dest, wid):
    return {"x": x, "y": y, "elevation": 0, "dest_map": dest, "dest_warp_id": str(wid)}


def trigger(x, y, script, var="VAR_TEMP_0", val="0"):
    return {"type": "trigger", "x": x, "y": y, "elevation": 0, "var": var, "var_value": val, "script": script}


def sign(x, y, script):
    return {"type": "sign", "x": x, "y": y, "elevation": 0, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": script}


def write_map(name: str, data: dict, scripts: str):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n")
    (folder / "scripts.inc").write_text(scripts)
    print("wrote", name)


# ---------- Trainer slot mapping ----------
SLOT_MAP = [
    # (new_name, old_name, id, key_in_trainers_json, class, pic, gender, music)
    ("TRAINER_CYCLIST_AXEL_R206", "TRAINER_BROOKE_4", 103, "cyclist_axel", "Triathlete", "Cycling Triathlete M", "Male", "Male"),
    ("TRAINER_CYCLIST_MEGAN_R206", "TRAINER_BROOKE_5", 104, "cyclist_megan", "Triathlete", "Cycling Triathlete F", "Female", "Female"),
    ("TRAINER_CYCLIST_JAMES_R206", "TRAINER_VALERIE_2", 110, "cyclist_james", "Triathlete", "Cycling Triathlete M", "Male", "Male"),
    ("TRAINER_CYCLIST_NICOLE_R206", "TRAINER_VALERIE_3", 111, "cyclist_nicole", "Triathlete", "Cycling Triathlete F", "Female", "Female"),
    ("TRAINER_CYCLIST_JOHN_R206", "TRAINER_VALERIE_4", 112, "cyclist_john", "Triathlete", "Cycling Triathlete M", "Male", "Male"),
    ("TRAINER_CYCLIST_KAYLA_R206", "TRAINER_VALERIE_5", 113, "cyclist_kayla", "Triathlete", "Cycling Triathlete F", "Female", "Female"),
    ("TRAINER_CYCLIST_RYAN_R206", "TRAINER_CINDY_6", 123, "cyclist_ryan", "Triathlete", "Cycling Triathlete M", "Male", "Male"),
    ("TRAINER_CYCLIST_RACHEL_R206", "TRAINER_WINSTON_2", 139, "cyclist_rachel", "Triathlete", "Cycling Triathlete F", "Female", "Female"),
    ("TRAINER_HIKER_THEODORE_R206", "TRAINER_WINSTON_3", 140, "hiker_theodore", "Hiker", "Hiker", "Male", "Hiker"),
    ("TRAINER_CAMPER_ANTHONY_R207", "TRAINER_WINSTON_4", 141, "camper_anthony", "Camper", "Camper", "Male", "Male"),
    ("TRAINER_PICNICKER_LAUREN_R207", "TRAINER_WINSTON_5", 142, "picnicker_lauren", "Picnicker", "Picnicker", "Female", "Female"),
    ("TRAINER_YOUNGSTER_AUSTIN_R207", "TRAINER_STEVE_2", 147, "youngster_austin", "Youngster", "Youngster", "Male", "Male"),
    ("TRAINER_HIKER_JUSTIN_R207", "TRAINER_STEVE_3", 148, "hiker_justin", "Hiker", "Hiker", "Male", "Hiker"),
    ("TRAINER_HIKER_KEVIN_R207", "TRAINER_STEVE_4", 149, "hiker_kevin", "Hiker", "Hiker", "Male", "Hiker"),
    ("TRAINER_BATTLE_GIRL_HELEN_R207", "TRAINER_STEVE_5", 150, "battle_girl_helen", "Battle Girl", "Battle Girl", "Female", "Female"),
    ("TRAINER_HIKER_ROBERT_R208", "TRAINER_TONY_2", 175, "hiker_robert", "Hiker", "Hiker", "Male", "Hiker"),
    ("TRAINER_HIKER_JONATHAN_R208", "TRAINER_TONY_3", 176, "hiker_jonathan", "Hiker", "Hiker", "Male", "Hiker"),
    ("TRAINER_BLACK_BELT_KYLE_R208", "TRAINER_TONY_4", 177, "black_belt_kyle", "Black Belt", "Black Belt", "Male", "Intense"),
    ("TRAINER_FISHERMAN_CODY_R208", "TRAINER_TONY_5", 178, "fisherman_cody", "Fisherman", "Fisherman", "Male", "Male"),
    ("TRAINER_AROMA_LADY_HANNAH_R208", "TRAINER_NOB_2", 184, "aroma_lady_hannah", "Aroma Lady", "Aroma Lady", "Female", "Female"),
    ("TRAINER_ARTIST_WILLIAM_R208", "TRAINER_NOB_3", 185, "artist_william", "Artist", "Artist", "Male", "Male"),
]


def species_short(sp: str) -> str:
    return sp.replace("SPECIES_", "").replace("_", " ").title().replace("Jr", "Jr.")


def patch_opponents():
    path = REPO / "include/constants/opponents.h"
    text = path.read_text()
    for new, old, num, *_ in SLOT_MAP:
        # Replace `#define OLD  num` with new + alias
        pat = rf"#define {old}\s+{num}\b"
        repl = f"#define {new}                    {num} // Sinnoh M16: was {old}\n#define {old} {new}"
        if new in text:
            continue
        text2, n = re.subn(pat, repl, text, count=1)
        if n != 1:
            raise SystemExit(f"Failed to patch opponent {old}={num}")
        text = text2
    path.write_text(text)
    print("patched opponents.h")


def patch_trainers_party():
    path = REPO / "src/data/trainers.party"
    text = path.read_text()
    for new, old, num, key, cls, pic, gender, music in SLOT_MAP:
        t = TRAINERS[key]
        # Find === OLD === block and replace through next ===
        pat = rf"=== {old} ===.*?(?=\n=== |\Z)"
        party_lines = []
        for mon in t["party"]:
            name = species_short(mon["species"])
            # Mime Jr. / specials
            name = name.replace("Mime Jr.", "Mime Jr").replace("Pachirisu", "Pachirisu")
            if name == "Mime Jr":
                name = "Mime Jr"
            party_lines.append(f"{name}\nLevel: {mon['level']}\nIVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe\n")
        block = (
            f"=== {new} ===\n"
            f"Name: {t['name'].upper()}\n"
            f"Class: {cls}\n"
            f"Pic: {pic}\n"
            f"Gender: {gender}\n"
            f"Music: {music}\n"
            f"Double Battle: No\n"
            f"AI: Basic Trainer\n\n"
            + "\n".join(party_lines)
            + "\n"
        )
        text2, n = re.subn(pat, block, text, count=1, flags=re.S)
        if n != 1:
            # Some rematch trainers may share header names differently - append if missing
            if f"=== {new} ===" not in text and f"=== {old} ===" not in text:
                text = text.rstrip() + "\n\n" + block
                print("appended party for", new)
                continue
            raise SystemExit(f"Failed to patch party for {old} -> {new} (matches={n})")
        text = text2
    path.write_text(text)
    print("patched trainers.party")


def land_entry(map_id, label, mons, rate=30):
    return {
        "map": map_id,
        "base_label": label,
        "land_mons": {
            "encounter_rate": rate,
            "mons": [{"min_level": lv, "max_level": lv, "species": sp} for sp, lv in mons],
        },
    }


def patch_wilds():
    path = REPO / "src/data/wild_encounters.json"
    data = json.loads(path.read_text())
    # wild_encounter_groups[0].encounters
    groups = data["wild_encounter_groups"]
    encs = groups[0]["encounters"]
    # Remove any prior M16 entries
    drop = {"MAP_ROUTE206", "MAP_ROUTE207", "MAP_ROUTE208", "MAP_MT_CORONET_1F_SOUTH"}
    encs[:] = [e for e in encs if e.get("map") not in drop]

    r206 = [
        ("SPECIES_PONYTA", 16), ("SPECIES_GEODUDE", 16), ("SPECIES_GLIGAR", 18), ("SPECIES_KRICKETUNE", 17),
        ("SPECIES_GLIGAR", 16), ("SPECIES_MACHOP", 17), ("SPECIES_MACHOP", 18), ("SPECIES_GEODUDE", 18),
        ("SPECIES_MACHOP", 19), ("SPECIES_GEODUDE", 18), ("SPECIES_MACHOP", 19), ("SPECIES_GEODUDE", 18),
    ]
    r206_night = list(r206)
    r206_night[2] = ("SPECIES_KRICKETUNE", 18)
    r206_night[4] = ("SPECIES_ZUBAT", 16)

    r207 = [
        ("SPECIES_MACHOP", 7), ("SPECIES_GEODUDE", 5), ("SPECIES_PONYTA", 6), ("SPECIES_KRICKETOT", 5),
        ("SPECIES_PONYTA", 5), ("SPECIES_MACHOP", 6), ("SPECIES_MACHOP", 8), ("SPECIES_GEODUDE", 6),
        ("SPECIES_PONYTA", 7), ("SPECIES_GEODUDE", 7), ("SPECIES_PONYTA", 7), ("SPECIES_GEODUDE", 7),
    ]
    r207_night = list(r207)
    r207_night[2] = ("SPECIES_KRICKETOT", 6)
    r207_night[4] = ("SPECIES_ZUBAT", 5)

    r208 = [
        ("SPECIES_BUDEW", 18), ("SPECIES_BIDOOF", 18), ("SPECIES_BUDEW", 19), ("SPECIES_RALTS", 17),
        ("SPECIES_ROSELIA", 19), ("SPECIES_BIBAREL", 18), ("SPECIES_RALTS", 18), ("SPECIES_BIBAREL", 19),
        ("SPECIES_ROSELIA", 20), ("SPECIES_BIBAREL", 20), ("SPECIES_ROSELIA", 20), ("SPECIES_BIBAREL", 20),
    ]
    r208_night = list(r208)
    r208_night[0] = ("SPECIES_ZUBAT", 18)
    r208_night[2] = ("SPECIES_ZUBAT", 19)

    mt = [
        ("SPECIES_ZUBAT", 19), ("SPECIES_GEODUDE", 19), ("SPECIES_MEDITITE", 18), ("SPECIES_CLEFAIRY", 17),
        ("SPECIES_MACHOP", 20), ("SPECIES_MEDITITE", 20), ("SPECIES_CHINGLING", 17), ("SPECIES_GEODUDE", 18),
        ("SPECIES_ZUBAT", 19), ("SPECIES_CHINGLING", 19), ("SPECIES_ZUBAT", 19), ("SPECIES_CHINGLING", 19),
    ]
    # Prefer user-facing mix: include Cleffa-ish via Clefairy; Bronzor appears in Platinum slot1 -
    # keep authentic platinum but swap first to Bronzor as data says, also list Zubat as user asked
    mt_plat = [
        ("SPECIES_BRONZOR", 18), ("SPECIES_GEODUDE", 19), ("SPECIES_MEDITITE", 18), ("SPECIES_CLEFAIRY", 17),
        ("SPECIES_MACHOP", 20), ("SPECIES_MEDITITE", 20), ("SPECIES_CHINGLING", 17), ("SPECIES_NOSEPASS", 18),
        ("SPECIES_ZUBAT", 19), ("SPECIES_CHINGLING", 19), ("SPECIES_ZUBAT", 19), ("SPECIES_CHINGLING", 19),
    ]

    new_entries = []
    for base, day, night, mid, rate in [
        (r206, r206, r206_night, "MAP_ROUTE206", 30),
        (r207, r207, r207_night, "MAP_ROUTE207", 30),
        (r208, r208, r208_night, "MAP_ROUTE208", 30),
        (mt_plat, mt_plat, mt_plat, "MAP_MT_CORONET_1F_SOUTH", 10),
    ]:
        short = mid.replace("MAP_", "").title().replace("_", "")
        # labels like gRoute206
        label = "g" + mid.replace("MAP_", "").replace("_", "")
        # prettier: gRoute206 / gMtCoronet1FSouth
        label = "g" + "".join(p.capitalize() if not p.isdigit() else p for p in mid.replace("MAP_", "").split("_"))
        # Fix known ones
        label_map = {
            "MAP_ROUTE206": "gRoute206",
            "MAP_ROUTE207": "gRoute207",
            "MAP_ROUTE208": "gRoute208",
            "MAP_MT_CORONET_1F_SOUTH": "gMtCoronet_1F_South",
        }
        label = label_map[mid]
        new_entries.append(land_entry(mid, label, base, rate))
        new_entries.append(land_entry(mid, label + "_Day", day, rate))
        new_entries.append(land_entry(mid, label + "_Night", night, rate))

    # Insert before Battle Pyramid if present, else append
    insert_at = len(encs)
    for i, e in enumerate(encs):
        if "BATTLE_PYRAMID" in e.get("map", "") or "BattlePyramid" in e.get("base_label", ""):
            insert_at = i
            break
    for j, e in enumerate(new_entries):
        encs.insert(insert_at + j, e)
    path.write_text(json.dumps(data, indent=2) + "\n")
    print("patched wild_encounters.json")


def patch_mapsecs():
    path = REPO / "src/data/region_map/region_map_sections.json"
    data = json.loads(path.read_text())
    sections = data["sections"] if "sections" in data else data
    # file structure: list under key?
    if isinstance(data, dict) and "regions" in data:
        # find last region list
        for region in data["regions"]:
            sections = region["map_sections"]
    # Our file from earlier read was a flat {"section_data":?}. Re-read shape.
    # From earlier: it's a list at end inside a parent. Check:
    pass


def patch_region_map_sections():
    path = REPO / "src/data/region_map/region_map_sections.json"
    text = path.read_text()
    if "MAPSEC_ROUTE_206" in text:
        print("MAPSEC already present")
        return
    addition = """    ,
    {
      "id": "MAPSEC_ROUTE_206",
      "name": "ROUTE 206"
    },
    {
      "id": "MAPSEC_WAYWARD_CAVE",
      "name": "WAYWARD CAVE"
    },
    {
      "id": "MAPSEC_ROUTE_207",
      "name": "ROUTE 207"
    },
    {
      "id": "MAPSEC_MT_CORONET",
      "name": "MT. CORONET"
    },
    {
      "id": "MAPSEC_ROUTE_208",
      "name": "ROUTE 208"
    },
    {
      "id": "MAPSEC_HEARTHOME_GATE",
      "name": "HEARTHOME GATE"
    }
"""
    # Insert before final closing of sections array
    # File ends with MAPSEC_GALACTIC_ETERNA block then ] }
    needle = """    {
      "id": "MAPSEC_GALACTIC_ETERNA",
      "name": "GALACTIC ETERNA BLDG."
    }
  ]
}"""
    if needle not in text:
        raise SystemExit("region_map_sections.json unexpected format")
    text = text.replace(
        needle,
        """    {
      "id": "MAPSEC_GALACTIC_ETERNA",
      "name": "GALACTIC ETERNA BLDG."
    },
    {
      "id": "MAPSEC_ROUTE_206",
      "name": "ROUTE 206"
    },
    {
      "id": "MAPSEC_WAYWARD_CAVE",
      "name": "WAYWARD CAVE"
    },
    {
      "id": "MAPSEC_ROUTE_207",
      "name": "ROUTE 207"
    },
    {
      "id": "MAPSEC_MT_CORONET",
      "name": "MT. CORONET"
    },
    {
      "id": "MAPSEC_ROUTE_208",
      "name": "ROUTE 208"
    },
    {
      "id": "MAPSEC_HEARTHOME_GATE",
      "name": "HEARTHOME GATE"
    }
  ]
}""",
    )
    path.write_text(text)
    print("patched region_map_sections.json")


def patch_map_name_popup():
    path = REPO / "src/map_name_popup.c"
    text = path.read_text()
    if "MAPSEC_ROUTE_206" in text:
        print("map_name_popup already patched")
        return
    block_a = """    [MAPSEC_GALACTIC_ETERNA - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,
};"""
    repl_a = """    [MAPSEC_GALACTIC_ETERNA - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,
    [MAPSEC_ROUTE_206 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,
    [MAPSEC_WAYWARD_CAVE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_STONE,
    [MAPSEC_ROUTE_207 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,
    [MAPSEC_MT_CORONET - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_STONE,
    [MAPSEC_ROUTE_208 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,
    [MAPSEC_HEARTHOME_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_WOOD,
};"""
    # First table only once - there are two tables (gen3 and BW)
    text2 = text.replace(block_a, repl_a, 1)
    block_b = """    [MAPSEC_GALACTIC_ETERNA - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,
};"""
    repl_b = """    [MAPSEC_GALACTIC_ETERNA - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,
    [MAPSEC_ROUTE_206 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,
    [MAPSEC_WAYWARD_CAVE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,
    [MAPSEC_ROUTE_207 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,
    [MAPSEC_MT_CORONET - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,
    [MAPSEC_ROUTE_208 - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,
    [MAPSEC_HEARTHOME_GATE - KANTO_MAPSEC_COUNT] = MAPPOPUP_THEME_BW_DEFAULT,
};"""
    if block_b not in text2:
        # try finding BW table differently
        raise SystemExit("BW map popup table not found")
    text2 = text2.replace(block_b, repl_b, 1)
    path.write_text(text2)
    print("patched map_name_popup.c")


def patch_regions_h():
    path = REPO / "include/regions.h"
    text = path.read_text()
    text = text.replace(
        "sectionId >= MAPSEC_TWINLEAF_TOWN && sectionId <= MAPSEC_GALACTIC_ETERNA;",
        "sectionId >= MAPSEC_TWINLEAF_TOWN && sectionId <= MAPSEC_HEARTHOME_GATE;",
    )
    path.write_text(text)
    print("patched regions.h")


def patch_flags_vars_newgame():
    flags = REPO / "include/constants/flags.h"
    text = flags.read_text()
    block = """#define FLAG_ITEM_ROUTE205_NORTH_POTION  0x27B // Sinnoh M15
#define FLAG_UNUSED_0x27C  0x27C // Unused Flag
#define FLAG_UNUSED_0x27D  0x27D // Unused Flag
#define FLAG_UNUSED_0x27E  0x27E // Unused Flag
#define FLAG_UNUSED_0x27F  0x27F // Unused Flag
#define FLAG_UNUSED_0x280  0x280 // Unused Flag
#define FLAG_UNUSED_0x281  0x281 // Unused Flag
#define FLAG_UNUSED_0x282  0x282 // Unused Flag
#define FLAG_UNUSED_0x283  0x283 // Unused Flag
#define FLAG_UNUSED_0x284  0x284 // Unused Flag
#define FLAG_UNUSED_0x285  0x285 // Unused Flag
#define FLAG_UNUSED_0x286  0x286 // Unused Flag
#define FLAG_UNUSED_0x287  0x287 // Unused Flag
"""
    repl = """#define FLAG_ITEM_ROUTE205_NORTH_POTION  0x27B // Sinnoh M15
#define FLAG_GOT_VS_SEEKER_SINNOH  0x27C // Sinnoh M16: Vs. Seeker from Dawn/Lucas
#define FLAG_HIDE_ROUTE207_COUNTERPART  0x27D // Sinnoh M16
#define FLAG_HIDE_MT_CORONET_CYRUS  0x27E // Sinnoh M16; set by default until scene
#define FLAG_MT_CORONET_CYRUS_DONE  0x27F // Sinnoh M16
#define FLAG_GOT_ODD_KEYSTONE_R208  0x280 // Sinnoh M16
#define FLAG_ITEM_ROUTE206_POISON_BARB  0x281 // Sinnoh M16
#define FLAG_ITEM_ROUTE206_PP_UP  0x282 // Sinnoh M16
#define FLAG_ITEM_ROUTE207_POKE_BALL  0x283 // Sinnoh M16
#define FLAG_ITEM_ROUTE208_ETHER  0x284 // Sinnoh M16
#define FLAG_ITEM_MT_CORONET_PROTEIN  0x285 // Sinnoh M16
#define FLAG_UNUSED_0x286  0x286 // Unused Flag
#define FLAG_UNUSED_0x287  0x287 // Unused Flag
"""
    if "FLAG_GOT_VS_SEEKER_SINNOH" not in text:
        if block not in text:
            raise SystemExit("flags block not found")
        text = text.replace(block, repl)
        # Also fix stub FLAG_GOT_VS_SEEKER = 0 to alias
        text = text.replace(
            "#define FLAG_GOT_VS_SEEKER                               0\n",
            "#define FLAG_GOT_VS_SEEKER                               FLAG_GOT_VS_SEEKER_SINNOH\n",
        )
        flags.write_text(text)
        print("patched flags.h")
    else:
        print("flags already patched")

    vars_path = REPO / "include/constants/vars.h"
    vtext = vars_path.read_text()
    if "VAR_ROUTE207_STATE" not in vtext:
        vtext = vtext.replace(
            "#define VAR_UNUSED_0x40F7                                0x40F7 // Unused Var\n"
            "#define VAR_UNUSED_0x40F8                                0x40F8 // Unused Var\n",
            "#define VAR_ROUTE207_STATE                               0x40F7 // Sinnoh M16: 0 = Dawn/Lucas pending, 1 = done\n"
            "#define VAR_MT_CORONET_SOUTH_STATE                       0x40F8 // Sinnoh M16: 0 = Cyrus pending, 1 = done\n",
        )
        vars_path.write_text(vtext)
        print("patched vars.h")

    ng = REPO / "data/scripts/new_game.inc"
    ngt = ng.read_text()
    if "FLAG_HIDE_MT_CORONET_CYRUS" not in ngt:
        ngt = ngt.replace(
            "\tsetflag FLAG_HIDE_LAKE_VERITY_CYRUS\n",
            "\tsetflag FLAG_HIDE_LAKE_VERITY_CYRUS\n"
            "\tsetflag FLAG_HIDE_MT_CORONET_CYRUS\n",
        )
        # Route 207 Dawn/Lucas starts visible; hide flag set after Vs. Seeker scene.
        ng.write_text(ngt)
        print("patched new_game.inc")


def patch_map_groups():
    path = REPO / "data/maps/map_groups.json"
    data = json.loads(path.read_text())
    towns = data["gMapGroup_TownsAndRoutes"]
    for name in ["Route206", "Route207", "Route208"]:
        if name not in towns:
            towns.append(name)
    dungeons = data["gMapGroup_Dungeons"]
    if "MtCoronet_1F_South" not in dungeons:
        # after RavagedPath if present
        if "RavagedPath" in dungeons:
            i = dungeons.index("RavagedPath") + 1
            dungeons.insert(i, "MtCoronet_1F_South")
        else:
            dungeons.append("MtCoronet_1F_South")
    # indoor group
    if "gMapGroup_IndoorM16" not in data:
        data["group_order"].append("gMapGroup_IndoorM16")
        data["gMapGroup_IndoorM16"] = [
            "Route206_CyclingRoadNorthGate",
            "Route206_CyclingRoadSouthGate",
            "Route208_BerryMastersHouse",
            "Route208_HearthomeGate",
        ]
    else:
        for n in [
            "Route206_CyclingRoadNorthGate",
            "Route206_CyclingRoadSouthGate",
            "Route208_BerryMastersHouse",
            "Route208_HearthomeGate",
        ]:
            if n not in data["gMapGroup_IndoorM16"]:
                data["gMapGroup_IndoorM16"].append(n)
    path.write_text(json.dumps(data, indent=2) + "\n")
    print("patched map_groups.json")


def trainer_script(map_prefix: str, script_name: str, trainer_const: str, key: str) -> str:
    t = TRAINERS[key]
    intro = e_str(t["msgs"].get("TRMSG_PRE_BATTLE", "Let's battle!$"))
    defeat = e_str(t["msgs"].get("TRMSG_DEFEAT", "...$"))
    after = e_str(t["msgs"].get("TRMSG_POST_BATTLE", "...$"))
    if not intro.endswith("$"):
        intro = intro.rstrip() + "$"
    if not defeat.endswith("$"):
        defeat = defeat.rstrip() + "$"
    if not after.endswith("$"):
        after = after.rstrip() + "$"

    def q(s):
        # Convert newlines to \n / \p heuristically
        lines = [ln for ln in s.replace("$", "").split("\n") if ln != ""]
        if not lines:
            return '\t.string "$"'
        out = []
        for i, ln in enumerate(lines):
            ln = ln.replace('"', "'")
            if i < len(lines) - 1:
                # use \p every other line for dialogue feel
                sep = "\\n" if i % 2 == 0 else "\\p"
                out.append(f'\t.string "{ln}{sep}"')
            else:
                out.append(f'\t.string "{ln}$"')
        return "\n".join(out)

    return f"""{map_prefix}_EventScript_{script_name}::
	trainerbattle_single {trainer_const}, {map_prefix}_Text_{script_name}Intro, {map_prefix}_Text_{script_name}Defeat
	msgbox {map_prefix}_Text_{script_name}After, MSGBOX_AUTOCLOSE
	end

{map_prefix}_Text_{script_name}Intro:
{q(intro)}

{map_prefix}_Text_{script_name}Defeat:
{q(defeat)}

{map_prefix}_Text_{script_name}After:
{q(after)}
"""


if __name__ == "__main__":
    patch_opponents()
    patch_trainers_party()
    patch_wilds()
    patch_region_map_sections()
    patch_map_name_popup()
    patch_regions_h()
    patch_flags_vars_newgame()
    patch_map_groups()
    print("core patches done")
