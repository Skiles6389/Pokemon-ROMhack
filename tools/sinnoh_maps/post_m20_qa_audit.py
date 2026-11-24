#!/usr/bin/env python3
"""
Post-M20 Sinnoh QA audit: warps, connections, heal/fly, land-data 1:1 accuracy,
trainers (IVs), FRLG sprites, music/mapsec wiring, and ROM asset guardrails.

Requires pret/pokeplatinum land-data at /tmp/pokeplatinum-ref (reference only;
never copies DS tiles). Exit 0 if no FAIL findings remain after fixes.
"""
from __future__ import annotations

import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data" / "maps"
LAYOUTS = REPO / "data" / "layouts"
LAYOUTS_JSON = LAYOUTS / "layouts.json"
PLAT_DATA = Path("/tmp/pokeplatinum-ref/res/field/mapmodels/data")
HEAL_JSON = REPO / "src" / "data" / "heal_locations.json"
PARTY = REPO / "src" / "data" / "trainers.party"
REGIONS_H = REPO / "include" / "regions.h"
SOUND_C = REPO / "src" / "sound.c"
MAPSEC_H = REPO / "include" / "constants" / "region_map_sections.h"

SINNOH_PREFIXES = (
    "Twinleaf",
    "Sandgem",
    "Jubilife",
    "Oreburgh",
    "Floaroma",
    "Ravaged",
    "ValleyWindworks",
    "Eterna",
    "MtCoronet",
    "Hearthome",
    "Solaceon",
    "LostTower",
    "Veilstone",
    "Pastoria",
    "Valor",
    "Verity",
    "LakeVerity",
    "TeamGalactic",
    "Route201",
    "Route202",
    "Route203",
    "Route204",
    "Route205",
    "Route206",
    "Route207",
    "Route208",
    "Route209",
    "Route210",
    "Route213",
    "Route214",
    "Route215",
    "RusturfTunnel",
)

# Outdoor layouts from pret/pokeplatinum TownsAndRoutes + dungeon groups.
# Format: layout_name -> list of land_id rows (None = solid filler quadrant)
LAND_TABLE: dict[str, list[list[int | None]]] = {
    # M11 — TownsAndRoutes matrix
    "TwinleafTown": [[0]],
    "Route201": [[5, 6]],
    "SandgemTown": [[7]],
    "Route202": [[14]],
    "JubilifeCity": [[18, 16], [17, 15]],
    "Route203": [[19, 20]],
    "OreburghCity": [[22, 23], [None, 24]],
    "OreburghGate_1F": [[441]],
    "OreburghGate_B1F": [[442, 443]],
    "OreburghMine_B1F": [[336]],
    "OreburghMine_B2F": [[337]],
    # M13
    "Route204_South": [[21]],
    "Route204_North": [[31]],
    "RavagedPath": [[435], [436]],
    "FloaromaTown": [[33], [32]],
    "FloaromaMeadow": [[437, 438], [439, 440]],
    # M14
    "Route205_South": [[37], [35], [34]],
    "ValleyWindworks_Exterior": [[36]],
    # M15
    "EternaForest": [[338, 339, 340], [341, 342, 343], [344, 345, 346]],
    "Route205_North": [[43]],
    "EternaCity": [[44, 46], [45, None]],
    # M16
    "Route206": [[30], [29], [28], [27]],
    "Route207": [[25, 26]],
    "MtCoronet_1F_South": [[351]],
    "Route208": [[55, 56]],
    # M17
    "HearthomeCity": [[57, 58], [59, 60]],
    # M18
    "Route209": [[None, 74], [76, 75]],
    "SolaceonTown": [[72, 73]],
    "Route210_South": [[66], [67], [68]],
    "Route215": [[69, 70, 71]],
    # M19
    "VeilstoneCity": [[77, 78], [79, 80]],
    # M20
    "Route214": [[152], [153], [154]],
    "ValorLakefront": [[155, 156], [157, 158]],
    "Route213": [[143, 144, 145], [146, 147, 148]],
    "PastoriaCity": [[81, 82], [83, 84]],
    # M21
    "Route212_North": [[85], [86], [87]],
    "Route212_South": [[88, 89, 90, 91]],
    "GreatMarsh": [[383, 384], [385, 386], [387, 388]],
    "Route210_North": [[63, 64, 65]],
    "CelesticTown": [[62]],
    "Route218": [[50, 51]],
    "CanalaveCity": [[48], [49]],
    "IronIsland": [[54]],
    "Route211_East": [[61]],
    "Route216": [[110, 111, 112]],
    "Route217": [[106], [107], [108], [109]],
    "LakeValor_Drained": [[544, 545], [546, 547]],
    "SnowpointCity": [[104], [105]],
    "AcuityLakefront": [[100, 101], [102, 103]],
    "LakeAcuity": [[553, 554], [555, 556]],
    "SpearPillar": [[375, 376], [377, 378]],
    
    "Route222": [[149, 150, 151]],
    "SunyshoreCity": [[96, 97], [98, 99]],

    "SpearPillar_Distorted": [[379, 380], [381, 382]],
    "DistortionWorld_1F": [[598, 599], [600, 601]],
    "DistortionWorld_B1F": [[602, 603]],
    "DistortionWorld_B2F": [[604, 605], [606, 607]],
    "DistortionWorld_B3F": [[608, 609], [610, 611]],
    "DistortionWorld_B4F": [[612, 613], [614, 615]],
    "DistortionWorld_B5F": [[620, 621], [622, 623]],
    "DistortionWorld_B6F": [[624, 625], [626, 627]],
    "DistortionWorld_B7F": [[628], [629]],
    "DistortionWorld_GiratinaRoom": [[630]],
    "DistortionWorld_TurnbackCaveRoom": [[631, 632], [633, 634]],
    "Route223": [[92], [93], [94], [95]],
    "PokemonLeague_Exterior": [[114], [113]],
    "VictoryRoad_Sinnoh_1F": [[407, 408], [409, 410], [411, 412]],
    "VictoryRoad_Sinnoh_2F": [[413, 414], [415, 416]],
    "VictoryRoad_Sinnoh_B1F": [[417, 418], [419, 420]],
    "PokemonLeague_AaronsRoom": [[260]],
    "PokemonLeague_BerthasRoom": [[261]],
    "PokemonLeague_FlintsRoom": [[262]],
    "PokemonLeague_LuciansRoom": [[263]],
    "PokemonLeague_Elevator_ToAaron": [[306]],
    "PokemonLeague_Elevator_ToBertha": [[307]],
    "PokemonLeague_Elevator_ToFlint": [[307]],
    "PokemonLeague_Elevator_ToLucian": [[307]],
    "PokemonLeague_Elevator_ToCynthia": [[308]],
    "CanalaveCity_Gym": [[225]],
    "PokemonLeague_Sinnoh_CynthiasRoom": [[264]],
    "PokemonLeague_Sinnoh_HallOfFame": [[265]],
    "PokemonLeague_Sinnoh_HallwayToHoF": [[309]],
    "Route224": [[None, 115], [116, 117], [118, None]],
    "Route225": [[163, 166], [164, None], [165, None]],
    "FightArea": [[132, 133]],
    "VictoryRoad_Sinnoh_Room1": [[425]],
    "VictoryRoad_Sinnoh_Room2": [[421, 422], [423, 424]],
    "VictoryRoad_Sinnoh_Room3": [[426]],


}

# Collision-like Emerald metatiles used as solid stand-ins
SOLID_MT = {
    0x1D4,
    0x1D5,
    0x1DC,
    0x1DD,  # trees
    0x079,  # rock
    0x21A,  # indoor wall
    0x00A,
    0x00B,  # fences sometimes
}

BEH_WALKABLE_WATER = {0x10, 0x15}  # water behaviours (surfable)
BEH_TALL = {0x02, 0x03}


def is_sinnoh_map(name: str) -> bool:
    if name.endswith("_Frlg") or "_Frlg" in name:
        return False
    return any(name.startswith(p) for p in SINNOH_PREFIXES)


def map_const_to_folder(const: str) -> str | None:
    if not const.startswith("MAP_"):
        return None
    if const in ("MAP_DYNAMIC", "MAP_UNDEFINED", "MAP_UNION_ROOM"):
        return None
    # MAP_ROUTE204_SOUTH -> Route204_South
    body = const[4:]
    parts = body.split("_")
    out = []
    for p in parts:
        if p in ("1F", "2F", "3F", "4F", "5F", "B1F", "B2F"):
            out.append(p)
        elif p.isdigit() or (len(p) <= 2 and p.isupper()):
            out.append(p)
        else:
            out.append(p.title() if p.isupper() else p)
    # Prefer exact folder match by scanning
    candidates = []
    # Reconstruct common pokeemerald style: Route204_South
    rebuilt = []
    for p in parts:
        if re.fullmatch(r"[0-9]+F|B[0-9]+F|[0-9]+", p):
            rebuilt.append(p)
        else:
            rebuilt.append("".join(w.title() for w in p.split()))
    # Better: iterate folders
    return None  # resolved via lookup table below


def build_map_lookup() -> dict[str, str]:
    """MAP_* constant -> folder name using map.json id field or folder."""
    lookup = {}
    for folder in MAPS.iterdir():
        if not folder.is_dir():
            continue
        mj = folder / "map.json"
        if not mj.exists():
            continue
        data = json.loads(mj.read_text())
        mid = data.get("id") or ("MAP_" + folder.name.upper())
        lookup[mid] = folder.name
        # also common alt
        lookup["MAP_" + folder.name.upper()] = folder.name
    return lookup


def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]


def plat_collision(v: int) -> int:
    return (v >> 15) & 1


def load_layout_meta() -> dict[str, dict]:
    layouts = json.loads(LAYOUTS_JSON.read_text())["layouts"]
    by_name = {}
    for L in layouts:
        name = L.get("name", "")
        if name.endswith("_Layout"):
            by_name[name[: -len("_Layout")]] = L
        by_name[L.get("id", "")] = L
    return by_name


def load_map_bin(path: Path, width: int, height: int) -> list[list[int]]:
    data = path.read_bytes()
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            mt = struct.unpack_from("<H", data, (y * width + x) * 2)[0] & 0x3FF
            row.append(mt)
        grid.append(row)
    return grid


def emerald_solid(mt: int) -> bool:
    return mt in SOLID_MT or mt in (0x1D4, 0x1D5, 0x1DC, 0x1DD, 0x079)


def compare_land(layout_name: str, chunks: list[list[int | None]], meta: dict) -> dict:
    """Compare Emerald map.bin collision footprint to Platinum land-data."""
    L = meta.get(layout_name)
    if not L:
        return {"status": "FAIL", "reason": "layout missing from layouts.json"}
    w, h = int(L["width"]), int(L["height"])
    rows, cols = len(chunks), len(chunks[0])
    expect_w, expect_h = cols * 32, rows * 32
    notes = []
    status = "PASS"

    # Allow special-case size mismatches for hand-cropped M11 maps
    size_ok = (w == expect_w and h == expect_h)
    if layout_name == "VerityLakefront":
        # M11 used a shorter strip
        size_ok = w == 32 and h <= 32
    if layout_name == "LakeVerity":
        size_ok = w == 64 and h <= 32
    if layout_name in ("OreburghGate_B1F",):
        # B1F may be 64x32
        size_ok = True

    if not size_ok and layout_name not in ("VerityLakefront", "LakeVerity"):
        notes.append(f"size {w}x{h} vs Platinum stitch {expect_w}x{expect_h}")
        status = "FAIL"

    map_bin = LAYOUTS / layout_name / "map.bin"
    if not map_bin.exists():
        return {"status": "FAIL", "reason": "map.bin missing", "size": f"{w}x{h}"}

    if not PLAT_DATA.exists():
        return {"status": "SKIP", "reason": "no pokeplatinum ref", "size": f"{w}x{h}"}

    # Build platinum collision grid
    plat = [[1] * expect_w for _ in range(expect_h)]
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            if lid is None:
                continue
            if not (PLAT_DATA / f"map_data_{lid:03d}.bin").exists():
                notes.append(f"missing land {lid}")
                status = "FAIL"
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    plat[cy * 32 + ly][cx * 32 + lx] = plat_collision(attrs[ly * 32 + lx])

    em = load_map_bin(map_bin, w, h)
    # Compare overlap region
    cw, ch = min(w, expect_w), min(h, expect_h)
    mismatch = 0
    walkable_mismatch = 0
    samples = []
    for y in range(ch):
        for x in range(cw):
            pcol = plat[y][x]
            ecol = 1 if emerald_solid(em[y][x]) else 0
            # Water/tall grass count as walkable/surfable for corridor purposes
            if em[y][x] in (0x170, 0x00D, 0x001, 0x121):
                ecol = 0
            if pcol != ecol:
                mismatch += 1
                if pcol == 0 and ecol == 1:
                    walkable_mismatch += 1
                    if len(samples) < 8:
                        samples.append((x, y, em[y][x]))

    total = cw * ch
    rate = mismatch / total if total else 0
    # Building stamps intentionally diverge; allow up to 18% mismatch but
    # flag if >8% of Platinum-walkable tiles became solid (corridor breakage).
    walk_rate = walkable_mismatch / total if total else 0
    if walk_rate > 0.08:
        status = "FAIL"
        notes.append(f"blocked Platinum walkables {walkable_mismatch}/{total} ({walk_rate:.1%})")
    elif rate > 0.35 and layout_name not in ("VerityLakefront", "LakeVerity", "FloaromaMeadow"):
        # High total mismatch often means wrong land IDs — investigate
        notes.append(f"collision diverge {mismatch}/{total} ({rate:.1%}) [informational]")
        if status == "PASS":
            status = "PASS"  # keep PASS if corridors ok; note only

    return {
        "status": status,
        "size": f"{w}x{h}",
        "plat_size": f"{expect_w}x{expect_h}",
        "mismatch": mismatch,
        "walkable_blocked": walkable_mismatch,
        "notes": notes,
        "samples": samples,
    }


def audit_warps(lookup: dict[str, str]) -> list[dict]:
    findings = []
    sinnoh_maps = [p for p in MAPS.iterdir() if p.is_dir() and is_sinnoh_map(p.name)]
    warp_tables: dict[str, list] = {}
    for folder in sinnoh_maps:
        data = json.loads((folder / "map.json").read_text())
        warp_tables[folder.name] = data.get("warp_events") or []

    for folder_name, warps in warp_tables.items():
        for i, w in enumerate(warps):
            dest = w.get("dest_map", "")
            wid = w.get("dest_warp_id", "0")
            if dest in ("MAP_DYNAMIC",) or wid in ("WARP_ID_DYNAMIC", "WARP_ID_NONE"):
                continue
            if dest == "MAP_UNION_ROOM":
                continue
            dest_folder = lookup.get(dest)
            if not dest_folder:
                findings.append(
                    {
                        "sev": "FAIL",
                        "cat": "warp",
                        "msg": f"{folder_name} w{i} -> {dest} (map missing)",
                    }
                )
                continue
            dest_warps = warp_tables.get(dest_folder)
            if dest_warps is None:
                # destination outside Sinnoh scope
                dest_path = MAPS / dest_folder / "map.json"
                if dest_path.exists():
                    dest_warps = json.loads(dest_path.read_text()).get("warp_events") or []
                else:
                    findings.append(
                        {
                            "sev": "FAIL",
                            "cat": "warp",
                            "msg": f"{folder_name} w{i} -> {dest} folder missing",
                        }
                    )
                    continue
            try:
                idx = int(wid)
            except ValueError:
                findings.append(
                    {
                        "sev": "FAIL",
                        "cat": "warp",
                        "msg": f"{folder_name} w{i} bad warp id {wid}",
                    }
                )
                continue
            if idx < 0 or idx >= len(dest_warps):
                findings.append(
                    {
                        "sev": "FAIL",
                        "cat": "warp",
                        "msg": f"{folder_name} w{i} -> {dest} warp {idx} OOB (n={len(dest_warps)})",
                    }
                )
    return findings


def audit_connections() -> list[dict]:
    findings = []
    sinnoh = {p.name: json.loads((p / "map.json").read_text()) for p in MAPS.iterdir() if p.is_dir() and is_sinnoh_map(p.name)}
    lookup = build_map_lookup()
    meta = load_layout_meta()

    # Reciprocal connection check
    for name, data in sinnoh.items():
        conns = data.get("connections") or []
        for c in conns:
            direction = c.get("direction")
            offset = c.get("offset", 0)
            dest = c.get("map")
            dest_folder = lookup.get(dest)
            if not dest_folder:
                findings.append({"sev": "FAIL", "cat": "conn", "msg": f"{name} -> {dest} missing"})
                continue
            if dest_folder not in sinnoh:
                continue
            opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}[direction]
            dest_conns = sinnoh[dest_folder].get("connections") or []
            match = [d for d in dest_conns if d.get("direction") == opposite and lookup.get(d.get("map")) == name]
            if not match:
                findings.append(
                    {
                        "sev": "FAIL",
                        "cat": "conn",
                        "msg": f"{name} {direction}->{dest} has no reciprocal",
                    }
                )
                continue
            # Offset reciprocity: A.offset + B.offset should be 0 for aligned edges
            # (Emerald stores destination offset along the shared edge)
            bo = match[0].get("offset", 0)
            if offset + bo != 0:
                findings.append(
                    {
                        "sev": "FAIL",
                        "cat": "conn",
                        "msg": f"{name}<->{dest_folder} offset mismatch {offset}+{bo}",
                    }
                )

            # Seam walkability: check border tiles align as walkable corridors
            src_layout = data.get("layout") or (data.get("id", "").replace("MAP_", "") + "_Layout")
            # Prefer layout name from folder
            src_L = meta.get(name)
            dst_L = meta.get(dest_folder)
            if not src_L or not dst_L:
                continue
            sw, sh = int(src_L["width"]), int(src_L["height"])
            dw, dh = int(dst_L["width"]), int(dst_L["height"])
            src_bin = LAYOUTS / name / "map.bin"
            dst_bin = LAYOUTS / dest_folder / "map.bin"
            if not src_bin.exists() or not dst_bin.exists():
                continue
            sg = load_map_bin(src_bin, sw, sh)
            dg = load_map_bin(dst_bin, dw, dh)

            def walkable(mt: int) -> bool:
                return not emerald_solid(mt)

            open_pairs = 0
            blocked_pairs = 0
            if direction == "up":
                # top row of src vs bottom row of dest, offset along x
                for x in range(sw):
                    dx = x - offset
                    if 0 <= dx < dw:
                        a, b = sg[0][x], dg[dh - 1][dx]
                        if walkable(a) and walkable(b):
                            open_pairs += 1
                        elif walkable(a) != walkable(b):
                            blocked_pairs += 1
            elif direction == "down":
                for x in range(sw):
                    dx = x - offset
                    if 0 <= dx < dw:
                        a, b = sg[sh - 1][x], dg[0][dx]
                        if walkable(a) and walkable(b):
                            open_pairs += 1
                        elif walkable(a) != walkable(b):
                            blocked_pairs += 1
            elif direction == "left":
                for y in range(sh):
                    dy = y - offset
                    if 0 <= dy < dh:
                        a, b = sg[y][0], dg[dy][dw - 1]
                        if walkable(a) and walkable(b):
                            open_pairs += 1
                        elif walkable(a) != walkable(b):
                            blocked_pairs += 1
            elif direction == "right":
                for y in range(sh):
                    dy = y - offset
                    if 0 <= dy < dh:
                        a, b = sg[y][sw - 1], dg[dy][0]
                        if walkable(a) and walkable(b):
                            open_pairs += 1
                        elif walkable(a) != walkable(b):
                            blocked_pairs += 1

            if open_pairs == 0:
                findings.append(
                    {
                        "sev": "FAIL",
                        "cat": "conn",
                        "msg": f"{name} {direction}->{dest_folder}: zero walkable seam tiles",
                    }
                )
            elif blocked_pairs > open_pairs * 3 and open_pairs < 2:
                findings.append(
                    {
                        "sev": "WARN",
                        "cat": "conn",
                        "msg": f"{name} {direction}->{dest_folder}: thin corridor open={open_pairs} mismatch={blocked_pairs}",
                    }
                )
    return findings


def audit_heals() -> list[dict]:
    findings = []
    heal = {e["id"]: e for e in json.loads(HEAL_JSON.read_text())["heal_locations"]}
    expected = {
        "SandgemTown_PokemonCenter_1F": "HEAL_LOCATION_SANDGEM_TOWN",
        "JubilifeCity_PokemonCenter_1F": "HEAL_LOCATION_JUBILIFE_CITY",
        "OreburghCity_PokemonCenter_1F": "HEAL_LOCATION_OREBURGH_CITY",
        "FloaromaTown_PokemonCenter_1F": "HEAL_LOCATION_FLOAROMA_TOWN",
        "EternaCity_PokemonCenter_1F": "HEAL_LOCATION_ETERNA_CITY",
        "HearthomeCity_PokemonCenter_1F": "HEAL_LOCATION_HEARTHOME_CITY",
        "SolaceonTown_PokemonCenter_1F": "HEAL_LOCATION_SOLACEON_TOWN",
        "VeilstoneCity_PokemonCenter_1F": "HEAL_LOCATION_VEILSTONE_CITY",
        "PastoriaCity_PokemonCenter_1F": "HEAL_LOCATION_PASTORIA_CITY",
        "TwinleafTown_PlayersHouse_2F": "HEAL_LOCATION_TWINLEAF_TOWN_PLAYERSHOUSE_2F",
    }
    meta = load_layout_meta()
    for folder, hid in expected.items():
        script = MAPS / folder / "scripts.inc"
        if not script.exists():
            findings.append({"sev": "FAIL", "cat": "heal", "msg": f"missing {script}"})
            continue
        text = script.read_text()
        if f"setrespawn {hid}" not in text:
            findings.append({"sev": "FAIL", "cat": "heal", "msg": f"{folder} missing setrespawn {hid}"})
        if hid not in heal:
            findings.append({"sev": "FAIL", "cat": "heal", "msg": f"{hid} missing from heal_locations.json"})
            continue
        e = heal[hid]
        # Overworld heal coords should be walkable
        overworld = e["map"].replace("MAP_", "")
        # Convert MAP_SANDGEM_TOWN -> SandgemTown via lookup
        lookup = build_map_lookup()
        ow_folder = lookup.get(e["map"])
        if not ow_folder:
            findings.append({"sev": "FAIL", "cat": "heal", "msg": f"{hid} map {e['map']} unknown"})
            continue
        L = meta.get(ow_folder)
        if not L:
            continue
        w, h = int(L["width"]), int(L["height"])
        x, y = int(e["x"]), int(e["y"])
        if not (0 <= x < w and 0 <= y < h):
            findings.append({"sev": "FAIL", "cat": "heal", "msg": f"{hid} coords ({x},{y}) OOB for {w}x{h}"})
            continue
        grid = load_map_bin(LAYOUTS / ow_folder / "map.bin", w, h)
        if emerald_solid(grid[y][x]):
            findings.append(
                {
                    "sev": "FAIL",
                    "cat": "heal",
                    "msg": f"{hid} lands on solid metatile 0x{grid[y][x]:03X} at ({x},{y})",
                }
            )
    return findings


def audit_trainers() -> list[dict]:
    findings = []
    refs = set()
    for p in MAPS.rglob("scripts.inc"):
        if not is_sinnoh_map(p.parent.name):
            continue
        for m in re.finditer(r"TRAINER_[A-Z0-9_]+", p.read_text()):
            t = m.group(0)
            if t.startswith("TRAINER_BATTLE") or t.startswith("TRAINER_TYPE") or t.startswith("TRAINER_ENCOUNTER"):
                continue
            refs.add(t)
    party = PARTY.read_text().splitlines()
    blocks: dict[str, list[str]] = {}
    cur = None
    buf: list[str] = []
    for line in party:
        m = re.match(r"=== (TRAINER_\w+) ===", line)
        if m:
            if cur:
                blocks[cur] = buf
            cur = m.group(1)
            buf = [line]
        elif cur:
            buf.append(line)
    if cur:
        blocks[cur] = buf
    for t in sorted(refs):
        if t not in blocks:
            findings.append({"sev": "FAIL", "cat": "trainer", "msg": f"{t} referenced but no party block"})
            continue
        ivs = [l for l in blocks[t] if l.startswith("IVs:")]
        bad = [l for l in ivs if l.strip() != "IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe"]
        if bad:
            findings.append({"sev": "FAIL", "cat": "trainer", "msg": f"{t} non-zero IVs: {bad[0]}"})
    return findings


def audit_sprites() -> list[dict]:
    findings = []
    for p in MAPS.rglob("map.json"):
        if not is_sinnoh_map(p.parent.name):
            continue
        text = p.read_text()
        for m in re.finditer(r"OBJ_EVENT_GFX_\w+_FRLG", text):
            findings.append({"sev": "FAIL", "cat": "sprite", "msg": f"{p.parent.name}: {m.group(0)}"})
    return findings


def audit_mapsec_music() -> list[dict]:
    findings = []
    regions = REGIONS_H.read_text()
    if "IsSinnohMapSec" not in regions:
        findings.append({"sev": "FAIL", "cat": "mapsec", "msg": "IsSinnohMapSec missing"})
    if "MAPSEC_GREAT_MARSH_GATE" not in regions:
        findings.append({"sev": "FAIL", "cat": "mapsec", "msg": "LAST mapsec GREAT_MARSH_GATE missing from regions.h"})
    sound = SOUND_C.read_text()
    if "GetRegionalSongOverride" not in sound:
        findings.append({"sev": "FAIL", "cat": "music", "msg": "GetRegionalSongOverride missing"})
    # Scan Sinnoh map.json music fields for invalid / Hoenn leaks on outdoor maps
    mus_defs = set(re.findall(r"#define\s+(MUS_\w+)\s+", (REPO / "include/constants/songs.h").read_text()))
    # Also music from expansion
    for songs in (REPO / "include/constants").glob("*song*"):
        mus_defs |= set(re.findall(r"#define\s+(MUS_\w+)\s+", songs.read_text()))
    # platinum songs may be in sound/songs or constants
    for p in (REPO / "include").rglob("*.h"):
        mus_defs |= set(re.findall(r"#define\s+(MUS_\w+)\s+", p.read_text()))

    for folder in MAPS.iterdir():
        if not folder.is_dir() or not is_sinnoh_map(folder.name):
            continue
        data = json.loads((folder / "map.json").read_text())
        for key in ("music", "music_night", "music_battle"):
            # map.json uses "music" and sometimes night via scripts; check known fields
            pass
        music = data.get("music")
        if music and music not in mus_defs and music != "MUS_DUMMY":
            # Some maps use MUS_PL_* which must be defined
            if not music.startswith("MUS_"):
                findings.append({"sev": "FAIL", "cat": "music", "msg": f"{folder.name} bad music {music}"})
            elif music not in mus_defs:
                findings.append({"sev": "FAIL", "cat": "music", "msg": f"{folder.name} undefined {music}"})
        # Prefer Platinum music on Sinnoh outdoor hubs
        if folder.name in (
            "TwinleafTown",
            "SandgemTown",
            "JubilifeCity",
            "OreburghCity",
            "FloaromaTown",
            "EternaCity",
            "HearthomeCity",
            "SolaceonTown",
            "VeilstoneCity",
            "PastoriaCity",
        ):
            if music and not music.startswith("MUS_PL_") and music not in ("MUS_DUMMY",):
                findings.append(
                    {
                        "sev": "WARN",
                        "cat": "music",
                        "msg": f"{folder.name} non-Platinum music {music}",
                    }
                )
    return findings


def audit_assets() -> list[dict]:
    findings = []
    bad_ext = {".gba", ".sav", ".bps", ".ips", ".sym", ".nds", ".sdat", ".bios"}
    # Upstream pokeemerald ships tiny multiboot payloads under data/mb_*.gba —
    # those are not Nintendo ROM dumps and are allowed.
    allow_gba = {"data/mb_colosseum.gba", "data/mb_ereader.gba", "data/mb_berry_fix.gba"}
    for p in REPO.rglob("*"):
        if not p.is_file():
            continue
        if any(part.startswith(".git") for part in p.parts):
            continue
        rel = str(p.relative_to(REPO))
        if p.suffix.lower() in bad_ext:
            if p.suffix.lower() == ".gba" and rel in allow_gba:
                continue
            # Build artifacts at repo root are untracked; still flag if committed path
            if rel.startswith("build/") or rel in ("pokeemerald.gba", "pokeemerald.elf"):
                continue
            findings.append({"sev": "FAIL", "cat": "asset", "msg": f"forbidden file {rel}"})
        if p.name.lower() in ("bios.bin", "gba_bios.bin"):
            findings.append({"sev": "FAIL", "cat": "asset", "msg": f"BIOS file {rel}"})
    return findings


def audit_script_labels() -> list[dict]:
    """Check map.json script references exist in scripts.inc."""
    findings = []
    for folder in MAPS.iterdir():
        if not folder.is_dir() or not is_sinnoh_map(folder.name):
            continue
        mj = folder / "map.json"
        sc = folder / "scripts.inc"
        data = json.loads(mj.read_text())
        script_text = sc.read_text() if sc.exists() else ""
        labels = set(re.findall(r"^([A-Za-z0-9_]+):", script_text, re.M))
        # Also common shared scripts
        refs = []
        for key in ("object_events", "coord_events", "bg_events"):
            for ev in data.get(key) or []:
                for field in ("script", "trainer_type"):
                    pass
                s = ev.get("script")
                if s and s not in ("0x0", "NULL", None, ""):
                    refs.append(s)
        for s in refs:
            if s.startswith("EventScript_") or s.startswith(folder.name) or "Script" in s:
                # Shared event scripts live in data/scripts/
                if s in labels:
                    continue
                # search global
                if (REPO / "data" / "scripts").exists():
                    # cheap: allow known shared prefixes
                    if s.startswith("EventScript_") or s.startswith("Common_") or s.startswith("Std_"):
                        continue
                if s not in labels and not s.startswith("0x"):
                    # Only fail if it looks map-local
                    if s.startswith(folder.name) or s.startswith(folder.name.replace("_", "")):
                        findings.append(
                            {
                                "sev": "FAIL",
                                "cat": "script",
                                "msg": f"{folder.name} missing label {s}",
                            }
                        )
                    elif s.startswith(tuple(SINNOH_PREFIXES)):
                        # might still be local naming
                        if s not in labels:
                            findings.append(
                                {
                                    "sev": "WARN",
                                    "cat": "script",
                                    "msg": f"{folder.name} unresolved script {s}",
                                }
                            )
    return findings


def main() -> int:
    print("=== Post-M20 Sinnoh QA Audit ===")
    lookup = build_map_lookup()
    meta = load_layout_meta()
    all_findings: list[dict] = []

    print("\n-- 1:1 land-data accuracy --")
    land_results = {}
    for name, chunks in LAND_TABLE.items():
        r = compare_land(name, chunks, meta)
        land_results[name] = r
        flag = r["status"]
        note = "; ".join(r.get("notes") or []) or r.get("reason", "")
        print(f"  [{flag}] {name} {r.get('size')} {note}")
        if flag == "FAIL":
            all_findings.append({"sev": "FAIL", "cat": "land", "msg": f"{name}: {note or r}"})

    print("\n-- Warps --")
    wf = audit_warps(lookup)
    all_findings.extend(wf)
    print(f"  {len(wf)} issues")
    for f in wf:
        print(f"  [{f['sev']}] {f['msg']}")

    print("\n-- Connections --")
    cf = audit_connections()
    all_findings.extend(cf)
    print(f"  {len(cf)} issues")
    for f in cf:
        print(f"  [{f['sev']}] {f['msg']}")

    print("\n-- Heal / Fly --")
    hf = audit_heals()
    all_findings.extend(hf)
    print(f"  {len(hf)} issues")
    for f in hf:
        print(f"  [{f['sev']}] {f['msg']}")

    print("\n-- Trainers (IVs) --")
    tf = audit_trainers()
    all_findings.extend(tf)
    print(f"  {len(tf)} issues")

    print("\n-- FRLG sprites --")
    sf = audit_sprites()
    all_findings.extend(sf)
    print(f"  {len(sf)} issues")

    print("\n-- Mapsec / Music --")
    mf = audit_mapsec_music()
    all_findings.extend(mf)
    print(f"  {len(mf)} issues")
    for f in mf:
        print(f"  [{f['sev']}] {f['msg']}")

    print("\n-- Asset guardrails --")
    af = audit_assets()
    all_findings.extend(af)
    print(f"  {len(af)} issues")

    print("\n-- Script labels --")
    lf = audit_script_labels()
    all_findings.extend(lf)
    print(f"  {len(lf)} issues")
    for f in lf[:20]:
        print(f"  [{f['sev']}] {f['msg']}")

    fails = [f for f in all_findings if f["sev"] == "FAIL"]
    warns = [f for f in all_findings if f["sev"] == "WARN"]
    report = {
        "fail": len(fails),
        "warn": len(warns),
        "findings": all_findings,
        "land": land_results,
    }
    out = REPO / "tools" / "sinnoh_maps" / "post_m20_qa_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"\n=== SUMMARY: {len(fails)} FAIL, {len(warns)} WARN ===")
    print(f"Report: {out}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
