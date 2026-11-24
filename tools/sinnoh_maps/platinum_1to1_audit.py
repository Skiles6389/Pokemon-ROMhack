#!/usr/bin/env python3
"""Platinum 1:1 geometry + event audit for Twinleaf→Pastoria demo outdoor maps."""
from __future__ import annotations
import json, re, struct, math
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
import os
PLAT_ROOT = Path(os.environ.get("POKEPLATINUM_REF", "/tmp/pokeplatinum-ref"))
PLAT_MAPS = PLAT_ROOT / "res/field/maps"
PLAT_DATA = PLAT_ROOT / "res/field/mapmodels/data"
MAPS = REPO / "data/maps"
LAYOUTS = REPO / "data/layouts"
LAYOUTS_JSON = json.loads((LAYOUTS / "layouts.json").read_text())["layouts"]

# LAND_TABLE from post_m20_qa_audit.py
LAND_TABLE: dict[str, list[list[int | None]]] = {
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
    "Route204_South": [[21]],
    "Route204_North": [[31]],
    "RavagedPath": [[435], [436]],
    "FloaromaTown": [[33], [32]],
    "FloaromaMeadow": [[437, 438], [439, 440]],
    "Route205_South": [[37], [35], [34]],
    "ValleyWindworks_Exterior": [[36]],
    "EternaForest": [[338, 339, 340], [341, 342, 343], [344, 345, 346]],
    "Route205_North": [[43]],
    "EternaCity": [[44, 46], [45, None]],
    "Route206": [[30], [29], [28], [27]],
    "Route207": [[25, 26]],
    "MtCoronet_1F_South": [[351]],
    "Route208": [[55, 56]],
    "HearthomeCity": [[57, 58], [59, 60]],
    "Route209": [[None, 74], [76, 75]],
    "SolaceonTown": [[72, 73]],
    "Route210_South": [[66], [67], [68]],
    "Route215": [[69, 70, 71]],
    "VeilstoneCity": [[77, 78], [79, 80]],
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
    # M29 Elite Four + Canalave Gym real layout
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

}

# Documented world origins (tile). Missing entries derived from warp fit.
DOCUMENTED_ORIGIN = {
    "TwinleafTown": (96, 864),          # verified via warp fit
    "Route204_South": (160, 704),
    "Route204_North": (160, 672),
    "FloaromaTown": (160, 608),
    "Route205_South": (192, 576),
    "ValleyWindworks_Exterior": (224, 640),
    "Route209": (16 * 32, 21 * 32),     # c16,r21
    "SolaceonTown": (17 * 32, 20 * 32),
    "Route210_South": (17 * 32, 17 * 32),
    "Route215": (18 * 32, 18 * 32),
    "VeilstoneCity": (21 * 32, 18 * 32),
    "Route214": (22 * 32, 20 * 32),
    "ValorLakefront": (21 * 32, 23 * 32),
    "Route213": (20 * 32, 25 * 32),
    "PastoriaCity": (18 * 32, 25 * 32),
    "Route212_North": (14 * 32, 23 * 32),
    "Route212_South": (14 * 32, 26 * 32),
    "GreatMarsh": (0, 0),  # GreatMarsh_DP local matrix
    "Route210_North": (15 * 32, 16 * 32),
    "CelesticTown": (14 * 32, 16 * 32),
    "Route218": (2 * 32, 23 * 32),
    "CanalaveCity": (1 * 32, 22 * 32),
    "IronIsland": (3 * 32, 15 * 32),
    "Route211_East": (13 * 32, 16 * 32),
    "Route216": (9 * 32, 12 * 32),
    "Route217": (9 * 32, 8 * 32),
    "LakeValor_Drained": (0, 0),
    "SnowpointCity": (11 * 32, 6 * 32),
    "AcuityLakefront": (9 * 32, 6 * 32),
    "LakeAcuity": (0, 0),
    "SpearPillar": (0, 0),
    "Route222": (736, 768),
    "SunyshoreCity": (832, 736),
    "SpearPillar_Distorted": (0, 0),
    "DistortionWorld_1F": (0, 0),
    "DistortionWorld_B1F": (0, 0),
    "DistortionWorld_B2F": (0, 0),
    "DistortionWorld_B3F": (0, 0),
    "DistortionWorld_B4F": (0, 0),
    "DistortionWorld_B5F": (0, 0),
    "DistortionWorld_B6F": (0, 0),
    "DistortionWorld_B7F": (0, 0),
    "DistortionWorld_GiratinaRoom": (0, 0),
    "DistortionWorld_TurnbackCaveRoom": (0, 0),
    "Route223": (832, 608),
    "PokemonLeague_Exterior": (832, 544),
    "VictoryRoad_Sinnoh_1F": (0, 0),
    "VictoryRoad_Sinnoh_2F": (0, 0),
    "VictoryRoad_Sinnoh_B1F": (0, 0),
    "PokemonLeague_AaronsRoom": (0, 0),
    "PokemonLeague_BerthasRoom": (0, 0),
    "PokemonLeague_FlintsRoom": (0, 0),
    "PokemonLeague_LuciansRoom": (0, 0),
    "PokemonLeague_Elevator_ToAaron": (0, 0),
    "PokemonLeague_Elevator_ToBertha": (0, 0),
    "PokemonLeague_Elevator_ToFlint": (0, 0),
    "PokemonLeague_Elevator_ToLucian": (0, 0),
    "PokemonLeague_Elevator_ToCynthia": (0, 0),
    "CanalaveCity_Gym": (0, 0),
    "PokemonLeague_Sinnoh_CynthiasRoom": (0, 0),
    "PokemonLeague_Sinnoh_HallOfFame": (0, 0),
    "PokemonLeague_Sinnoh_HallwayToHoF": (0, 0),

    "Route206": (288, 576),
    "Route207": (288, 704),
    "JubilifeCity": (128, 736),
    "OreburghCity": (256, 736),
    "EternaCity": (288, 512),
    "HearthomeCity": (448, 672),
    "SandgemTown": (160, 832),
    "Route203": (192, 736),
    "Route208": (384, 704),

}

# Emerald map folder -> Platinum maps/ folder
PLAT_NAME = {
    "TwinleafTown": "twinleaf_town",
    "Route201": "route_201",
    "SandgemTown": "sandgem_town",
    "Route202": "route_202",
    "JubilifeCity": "jubilife_city",
    "Route203": "route_203",
    "OreburghCity": "oreburgh_city",
    "OreburghGate_1F": "oreburgh_gate_1f",
    "OreburghGate_B1F": "oreburgh_gate_b1f",
    "OreburghMine_B1F": "oreburgh_mine_b1f",
    "OreburghMine_B2F": "oreburgh_mine_b2f",
    "Route204_South": "route_204_south",  # may be route_204
    "Route204_North": "route_204_north",
    "RavagedPath": "ravaged_path",
    "FloaromaTown": "floaroma_town",
    "FloaromaMeadow": "floaroma_meadow",
    "Route205_South": "route_205_south",
    "ValleyWindworks_Exterior": "valley_windworks_outside",
    "EternaForest": "eterna_forest",
    "Route205_North": "route_205_north",
    "EternaCity": "eterna_city",
    "Route206": "route_206",
    "Route207": "route_207",
    "MtCoronet_1F_South": "mt_coronet_1f_south",
    "Route208": "route_208",
    "HearthomeCity": "hearthome_city",
    "Route209": "route_209",
    "SolaceonTown": "solaceon_town",
    "Route210_South": "route_210",  # platinum may be single map
    "Route215": "route_215",
    "VeilstoneCity": "veilstone_city",
    "Route214": "route_214",
    "ValorLakefront": "valor_lakefront",
    "Route213": "route_213",
    "PastoriaCity": "pastoria_city",
    "Route212_North": "route_212_north",
    "Route212_South": "route_212_south",
    "Route210_North": "route_210_north",
    "CelesticTown": "celestic_town",
    "Route218": "route_218",
    "CanalaveCity": "canalave_city",
    "IronIsland": "iron_island",
    "Route211_East": "route_211_east",
    "Route216": "route_216",
    "Route217": "route_217",
    "LakeValor_Drained": "lake_valor_drained",
    "SnowpointCity": "snowpoint_city",
    "AcuityLakefront": "acuity_lakefront",
    "LakeAcuity": "lake_acuity",
    "SpearPillar": "spear_pillar",
    "Route222": "route_222",
    "SunyshoreCity": "sunyshore_city",
    "SpearPillar_Distorted": "spear_pillar_distorted",
    "DistortionWorld_1F": "distortion_world_1f",
    "DistortionWorld_B1F": "distortion_world_b1f",
    "DistortionWorld_B2F": "distortion_world_b2f",
    "DistortionWorld_B3F": "distortion_world_b3f",
    "DistortionWorld_B4F": "distortion_world_b4f",
    "DistortionWorld_B5F": "distortion_world_b5f",
    "DistortionWorld_B6F": "distortion_world_b6f",
    "DistortionWorld_B7F": "distortion_world_b7f",
    "DistortionWorld_GiratinaRoom": "distortion_world_giratina_room",
    "DistortionWorld_TurnbackCaveRoom": "distortion_world_turnback_cave_room",
    "Route223": "route_223",
    "PokemonLeague_Exterior": "pokemon_league",
    "VictoryRoad_Sinnoh_1F": "victory_road_1f",
    "VictoryRoad_Sinnoh_2F": "victory_road_2f",
    "VictoryRoad_Sinnoh_B1F": "victory_road_b1f",
    "PokemonLeague_AaronsRoom": "pokemon_league_aaron_room",
    "PokemonLeague_BerthasRoom": "pokemon_league_bertha_room",
    "PokemonLeague_FlintsRoom": "pokemon_league_flint_room",
    "PokemonLeague_LuciansRoom": "pokemon_league_lucian_room",
    "PokemonLeague_Elevator_ToAaron": "pokemon_league_elevator_to_aaron_room",
    "PokemonLeague_Elevator_ToBertha": "pokemon_league_elevator_to_bertha_room",
    "PokemonLeague_Elevator_ToFlint": "pokemon_league_elevator_to_flint_room",
    "PokemonLeague_Elevator_ToLucian": "pokemon_league_elevator_to_lucian_room",
    "PokemonLeague_Elevator_ToCynthia": "pokemon_league_elevator_to_champion_room",
    "CanalaveCity_Gym": "canalave_city_gym",
    "PokemonLeague_Sinnoh_CynthiasRoom": "pokemon_league_champion_room",
    "PokemonLeague_Sinnoh_HallOfFame": "pokemon_league_hall_of_fame",
    "PokemonLeague_Sinnoh_HallwayToHoF": "pokemon_league_hallway_to_hall_of_fame",

    "GreatMarsh": "great_marsh_1",  # events sample; geometry from GreatMarsh_DP lands
    "VerityLakefront": "verity_lakefront",
    "LakeVerity": "lake_verity_low_water",  # guess; resolve later
}

# Emerald metatile classifiers (stand-ins from gen scripts)
SOLID_TREE = {0x1D4, 0x1D5, 0x1DC, 0x1DD}
SOLID_ROCK = {0x079}
SOLID_WALL = {0x21A}
WATER_MT = {0x170, 0x171, 0x172, 0x173, 0x00A}  # outdoor water stand-ins
TALL_GRASS_MT = {0x00D, 0x00E, 0x003}
SAND_MT = {0x121}
LEDGE_MT = {0x0D5, 0x0D6, 0x0D4, 0x0D7, 0x0D8, 0x0D9}
# Building facade tiles commonly stamped
BUILDING_MT = {0x248, 0x249, 0x24A, 0x24B, 0x24C, 0x24D, 0x24E, 0x24F,
               0x250, 0x251, 0x252, 0x253, 0x254, 0x255, 0x256, 0x257,
               0x258, 0x259, 0x25A, 0x25B, 0x25C, 0x25D, 0x25E, 0x25F,
               0x260, 0x261, 0x262, 0x263, 0x264, 0x265, 0x266, 0x267,
               0x268, 0x269, 0x26A, 0x26B, 0x26C, 0x26D, 0x26E, 0x26F,
               0x270, 0x271, 0x272, 0x273, 0x274, 0x275, 0x276, 0x277,
               0x278, 0x279, 0x27A, 0x27B, 0x27C, 0x27D, 0x27E, 0x27F,
               0x280, 0x281, 0x282, 0x283, 0x284, 0x285, 0x286, 0x287,
               0x288, 0x289, 0x28A, 0x28B, 0x28C, 0x28D, 0x28E, 0x28F,
               0x290, 0x291, 0x292, 0x293, 0x294, 0x295, 0x296, 0x297,
               0x002, 0x538}  # door-ish / roof stamps seen in samples

# Platinum behavior bytes of interest (from gen_m20)
BEH_TALL = {0x02, 0x03}
BEH_WATER = {0x10, 0x15, 0x11, 0x12, 0x13, 0x14, 0x16, 0x17}
BEH_SAND = {0x21}
BEH_LEDGE = {0x38, 0x39, 0x3A, 0x3B}

meta = {}
for L in LAYOUTS_JSON:
    name = L.get("name", "")
    if name.endswith("_Layout"):
        meta[name[:-7]] = L

def load_attrs(land_id: int) -> list[int]:
    data = (PLAT_DATA / f"map_data_{land_id:03d}.bin").read_bytes()
    return [struct.unpack_from("<H", data, 0x10 + i * 2)[0] for i in range(32 * 32)]

def load_em_grid(name: str):
    L = meta[name]
    w, h = int(L["width"]), int(L["height"])
    data = (LAYOUTS / name / "map.bin").read_bytes()
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            row.append(struct.unpack_from("<H", data, (y * w + x) * 2)[0] & 0x3FF)
        grid.append(row)
    return grid, w, h

def plat_grid(chunks):
    rows, cols = len(chunks), len(chunks[0])
    W, H = cols * 32, rows * 32
    col = [[1] * W for _ in range(H)]
    beh = [[0] * W for _ in range(H)]
    for cy, row in enumerate(chunks):
        for cx, lid in enumerate(row):
            if lid is None:
                continue
            attrs = load_attrs(lid)
            for ly in range(32):
                for lx in range(32):
                    v = attrs[ly * 32 + lx]
                    col[cy * 32 + ly][cx * 32 + lx] = (v >> 15) & 1
                    beh[cy * 32 + ly][cx * 32 + lx] = v & 0xFF
    return col, beh, W, H

def em_solid(mt: int) -> bool:
    if mt in SOLID_TREE or mt in SOLID_ROCK or mt in SOLID_WALL:
        return True
    # Many building facade tiles are solid stand-ins
    if mt >= 0x200 and mt not in WATER_MT and mt not in {0x201}:  # indoor/outdoor building range heuristic
        # Too aggressive for outdoor — only treat known tree/rock/wall
        pass
    if mt in BUILDING_MT and mt != 0x538:
        return True
    return False

def em_class(mt: int) -> str:
    if mt in WATER_MT:
        return "water"
    if mt in TALL_GRASS_MT:
        return "tall"
    if mt in LEDGE_MT:
        return "ledge"
    if mt in SAND_MT:
        return "sand"
    if mt in SOLID_TREE:
        return "tree"
    if mt in SOLID_ROCK:
        return "rock"
    if mt in BUILDING_MT or (0x240 <= mt <= 0x2FF):
        return "building"
    if em_solid(mt):
        return "solid"
    return "walk"

def plat_class(col: int, beh: int) -> str:
    if col:
        return "solid"
    if beh in BEH_WATER:
        return "water"
    if beh in BEH_TALL:
        return "tall"
    if beh in BEH_LEDGE:
        return "ledge"
    if beh in BEH_SAND:
        return "sand"
    return "walk"

def resolve_plat_folder(em_name: str) -> Path | None:
    cand = PLAT_NAME.get(em_name)
    if cand and (PLAT_MAPS / cand).exists():
        return PLAT_MAPS / cand
    # fuzzy
    snake = re.sub(r'(?<!^)(?=[A-Z0-9])', '_', em_name).lower().strip('_')
    # try variants
    for c in [snake, snake.replace('_1_f', '_1f').replace('_b_1_f', '_b1f'),
              snake.replace('players_house', 'player_house'),
              snake.replace('valley_windworks_exterior', 'valley_windworks_outside'),
              'route_204' if 'route_204' in snake else None,
              'route_205' if 'route_205' in snake else None,
              'route_210' if 'route_210' in snake else None]:
        if c and (PLAT_MAPS / c).exists():
            return PLAT_MAPS / c
    # list match
    for p in PLAT_MAPS.iterdir():
        if not p.is_dir():
            continue
        if p.name.replace('_', '') == snake.replace('_', ''):
            return p
    return None

def fit_origin(plat_warps, em_warps, map_w, map_h):
    """Find origin that best maps platinum world warps onto emerald local warps."""
    if not plat_warps or not em_warps:
        return None, None
    # Try pairing by sorted x then z/y
    best = None
    # Brute: for each plat warp as anchor against each em warp
    for pw in plat_warps:
        for ew in em_warps:
            ox = pw["x"] - ew["x"]
            oz = pw["z"] - ew["y"]
            # score: how many plat warps land on an em warp within tol 1
            hits = 0
            dists = []
            for p2 in plat_warps:
                lx, ly = p2["x"] - ox, p2["z"] - oz
                if not (0 <= lx < map_w and 0 <= ly < map_h):
                    dists.append(999)
                    continue
                best_d = min((abs(lx - e["x"]) + abs(ly - e["y"])) for e in em_warps)
                dists.append(best_d)
                if best_d <= 1:
                    hits += 1
            score = (hits, -sum(d for d in dists if d < 999), -sum(dists))
            if best is None or score > best[0]:
                best = (score, (ox, oz), hits, dists)
    if best is None:
        return None, None
    return best[1], best

def compare_geometry(name: str):
    chunks = LAND_TABLE[name]
    pcol, pbeh, pw, ph = plat_grid(chunks)
    em, ew, eh = load_em_grid(name)
    size_match = (ew == pw and eh == ph)
    cw, ch = min(ew, pw), min(eh, ph)

    # Collision
    coll_mismatch = 0
    walk_blocked = 0  # plat walkable, em solid
    solid_opened = 0  # plat solid, em walkable
    # Behavior-class mismatches (among tiles both consider non-building-stamp)
    class_mismatch = defaultdict(int)
    water_miss = tall_miss = ledge_miss = 0
    water_plat = tall_plat = ledge_plat = 0
    water_em = tall_em = ledge_em = tree_em = rock_em = building_em = 0

    for y in range(ch):
        for x in range(cw):
            pc = pcol[y][x]
            pb = pbeh[y][x]
            mt = em[y][x]
            ec = 1 if em_solid(mt) else 0
            # Treat water/tall as walkable for collision compare (matches audit)
            if mt in WATER_MT or mt in TALL_GRASS_MT or mt in SAND_MT or mt in {0x001, 0x121}:
                ec = 0
            if pc != ec:
                coll_mismatch += 1
                if pc == 0 and ec == 1:
                    walk_blocked += 1
                if pc == 1 and ec == 0:
                    solid_opened += 1

            pcls = plat_class(pc, pb)
            ecls = em_class(mt)
            if pcls == "water":
                water_plat += 1
            if pcls == "tall":
                tall_plat += 1
            if pcls == "ledge":
                ledge_plat += 1
            if ecls == "water":
                water_em += 1
            if ecls == "tall":
                tall_em += 1
            if ecls == "ledge":
                ledge_em += 1
            if ecls == "tree":
                tree_em += 1
            if ecls == "rock":
                rock_em += 1
            if ecls == "building":
                building_em += 1

            # Class agreement ignoring solid↔tree/rock/building (emerald stand-ins)
            if pcls == "water" and ecls != "water":
                water_miss += 1
            if pcls == "tall" and ecls not in ("tall", "walk"):  # tall may be approximated
                tall_miss += 1
            if pcls == "ledge" and ecls != "ledge":
                ledge_miss += 1

    total = cw * ch
    return {
        "size_em": f"{ew}x{eh}",
        "size_plat": f"{pw}x{ph}",
        "size_match": size_match,
        "coll_mismatch": coll_mismatch,
        "coll_rate": coll_mismatch / total if total else 0,
        "walk_blocked": walk_blocked,
        "walk_block_rate": walk_blocked / total if total else 0,
        "solid_opened": solid_opened,
        "water_plat": water_plat,
        "water_em": water_em,
        "water_miss": water_miss,
        "tall_plat": tall_plat,
        "tall_em": tall_em,
        "ledge_plat": ledge_plat,
        "ledge_em": ledge_em,
        "ledge_miss": ledge_miss,
        "building_em": building_em,
        "tree_em": tree_em,
        "rock_em": rock_em,
        "total": total,
    }

def dest_kind(dest: str) -> str:
    d = dest.upper()
    for key in ("GYM", "POKEMON_CENTER", "MART", "GATE", "HOUSE", "SHOP", "MINE",
                "BUILDING", "WAREHOUSE", "DEPARTMENT", "HOTEL", "RESTAURANT",
                "COTTAGE", "CAVE", "FOREST", "TOWER", "LAB", "SCHOOL", "CONDO",
                "MEADOW", "WINDWORKS", "FOOTSTEP", "DAY_CARE", "DAYCARE",
                "FAN_CLUB", "CONTEST", "GAME_CORNER", "PRIZE", "MASSAGE",
                "HERB", "BIKE", "POFFIN", "FOREIGN", "AMITY", "MARSH",
                "OBSERVATORY", "MOVE_REMINDER", "NEWS", "PRESS"):
        if key in d:
            return key
    # outdoor map links
    if "ROUTE" in d or "CITY" in d or "TOWN" in d or "LAKE" in d:
        return "OVERWORLD"
    return "OTHER"

def compare_events(em_name: str, origin):
    plat_dir = resolve_plat_folder(em_name)
    em = json.loads((MAPS / em_name / "map.json").read_text())
    result = {
        "plat_folder": plat_dir.name if plat_dir else None,
        "origin": origin,
        "origin_source": None,
    }
    if not plat_dir or not (plat_dir / "events.json").exists():
        result["status"] = "NO_PLAT_EVENTS"
        return result
    pe = json.loads((plat_dir / "events.json").read_text())
    L = meta[em_name]
    w, h = int(L["width"]), int(L["height"])

    em_warps = em.get("warp_events") or []
    plat_warps = pe.get("warp_events") or []
    em_objs = em.get("object_events") or []
    plat_objs = pe.get("object_events") or []
    em_bg = em.get("bg_events") or []
    plat_bg = pe.get("bg_events") or []
    em_coord = em.get("coord_events") or []
    plat_coord = pe.get("coord_events") or []
    em_conns = em.get("connections") or []

    # Origin
    if origin is None:
        fitted, info = fit_origin(plat_warps, em_warps, w, h)
        origin = fitted
        result["origin"] = origin
        result["origin_source"] = "warp_fit"
        result["warp_fit_hits"] = info[2] if info else 0
    else:
        result["origin_source"] = "documented"
        # also compute hits
        if plat_warps and em_warps:
            hits = 0
            for pw in plat_warps:
                lx, ly = pw["x"] - origin[0], pw["z"] - origin[1]
                if any(abs(lx - e["x"]) + abs(ly - e["y"]) <= 1 for e in em_warps):
                    hits += 1
            result["warp_fit_hits"] = hits

    result["counts"] = {
        "warps": (len(em_warps), len(plat_warps)),
        "objects": (len(em_objs), len(plat_objs)),
        "bg": (len(em_bg), len(plat_bg)),
        "coord": (len(em_coord), len(plat_coord)),
        "trainers_em": sum(1 for o in em_objs if o.get("trainer_type") not in (None, "0", "TRAINER_TYPE_NONE")),
        "trainers_plat": sum(1 for o in plat_objs if o.get("trainer_type") not in (None, "0", "TRAINER_TYPE_NONE")),
        "items_em": sum(1 for o in em_objs if "ITEM" in (o.get("graphics_id") or "")),
        "items_plat": sum(1 for o in plat_objs if "ITEM" in (o.get("graphics_id") or "") or "BALL" in (o.get("graphics_id") or "")),
    }

    # Warp position deltas
    warp_deltas = []
    unmatched_plat = []
    unmatched_em = list(range(len(em_warps)))
    if origin:
        ox, oz = origin
        used_em = set()
        for i, pw in enumerate(plat_warps):
            lx, ly = pw["x"] - ox, pw["z"] - oz
            # find nearest em warp
            best_j, best_d = None, 999
            for j, ew in enumerate(em_warps):
                if j in used_em:
                    continue
                d = abs(lx - ew["x"]) + abs(ly - ew["y"])
                if d < best_d:
                    best_d, best_j = d, j
            if best_j is None or best_d > 3:
                unmatched_plat.append({
                    "plat": (pw["x"], pw["z"]),
                    "local": (lx, ly),
                    "id": pw.get("id"),
                    "dest": pw.get("dest_header_id"),
                    "kind": dest_kind(pw.get("dest_header_id", "")),
                })
            else:
                used_em.add(best_j)
                ew = em_warps[best_j]
                warp_deltas.append({
                    "plat_id": pw.get("id"),
                    "plat_local": (lx, ly),
                    "em": (ew["x"], ew["y"]),
                    "delta": (ew["x"] - lx, ew["y"] - ly),
                    "manhattan": best_d,
                    "em_dest": ew.get("dest_map"),
                    "plat_dest": pw.get("dest_header_id"),
                    "kind": dest_kind(pw.get("dest_header_id", "")),
                })
        unmatched_em = [j for j in range(len(em_warps)) if j not in used_em]

    result["warp_exact"] = sum(1 for d in warp_deltas if d["manhattan"] == 0)
    result["warp_near"] = sum(1 for d in warp_deltas if 1 <= d["manhattan"] <= 2)
    result["warp_far"] = sum(1 for d in warp_deltas if d["manhattan"] > 2)
    result["warp_unmatched_plat"] = unmatched_plat
    result["warp_unmatched_em"] = [
        {"em": (em_warps[j]["x"], em_warps[j]["y"]), "dest": em_warps[j].get("dest_map")}
        for j in unmatched_em
    ]
    result["warp_deltas_sample"] = [d for d in warp_deltas if d["manhattan"] > 0][:8]

    # Object position proximity (trainers/items/npcs) — count within 2 tiles of a plat object of similar class
    def obj_class(gfx, trainer_type, script=""):
        g = (gfx or "").upper()
        if "ITEM" in g or "BALL" in g:
            return "item"
        if trainer_type not in (None, "0", "TRAINER_TYPE_NONE"):
            return "trainer"
        if any(x in g for x in ("CUTTABLE", "BREAKABLE", "BOULDER", "ROCK_SMASH")):
            return "field"
        return "npc"

    plat_local_objs = []
    if origin:
        ox, oz = origin
        for o in plat_objs:
            lx, ly = o["x"] - ox, o["z"] - oz
            if 0 <= lx < w and 0 <= ly < h:
                plat_local_objs.append((lx, ly, obj_class(o.get("graphics_id"), o.get("trainer_type"))))

    em_classified = [(o["x"], o["y"], obj_class(o.get("graphics_id"), o.get("trainer_type"))) for o in em_objs]
    matched_objs = 0
    for lx, ly, cls in plat_local_objs:
        if any(c == cls and abs(lx - ex) + abs(ly - ey) <= 2 for ex, ey, c in em_classified):
            matched_objs += 1
    result["obj_plat_in_bounds"] = len(plat_local_objs)
    result["obj_matched_near"] = matched_objs
    result["obj_match_rate"] = matched_objs / len(plat_local_objs) if plat_local_objs else None

    # Connections: Emerald only (Platinum uses overworld matrix — no per-map connection list)
    result["em_connections"] = [
        {"dir": c.get("direction"), "map": c.get("map"), "offset": c.get("offset", 0)}
        for c in em_conns
    ]
    return result

def verdict(geo, ev):
    """exact | minor | significant"""
    reasons = []
    # Size
    if not geo["size_match"]:
        reasons.append(f"size {geo['size_em']} vs Platinum {geo['size_plat']}")
        sev = "significant"
    else:
        sev = "exact"

    # Collision corridors
    if geo["walk_block_rate"] > 0.08:
        reasons.append(f"blocked Platinum walkables {geo['walk_block_rate']:.1%}")
        sev = "significant"
    elif geo["walk_blocked"] > 0:
        reasons.append(f"{geo['walk_blocked']} Platinum-walkable tiles blocked")
        if sev == "exact":
            sev = "minor"

    # Overall collision diverge (building stamps inflate this)
    if geo["coll_rate"] > 0.35:
        reasons.append(f"collision diverge {geo['coll_rate']:.1%} (often building stamps)")
        if sev == "exact":
            sev = "minor"  # cities expected
        # caves with high diverge and no buildings → more significant
        if geo["building_em"] < 20 and geo["coll_rate"] > 0.55:
            sev = "significant"
            reasons.append("high cave/interior collision diverge without building stamps")

    # Water / ledge fidelity
    if geo["water_plat"] > 20:
        ratio = geo["water_em"] / geo["water_plat"] if geo["water_plat"] else 1
        if ratio < 0.5 or ratio > 2.0:
            reasons.append(f"water tile count em={geo['water_em']} plat_beh={geo['water_plat']} (ratio {ratio:.2f})")
            if sev == "exact":
                sev = "minor"
    if geo["ledge_plat"] > 5 and geo["ledge_em"] == 0:
        reasons.append(f"Platinum has {geo['ledge_plat']} ledge behaviors; Emerald has 0 ledge metatiles")
        if sev == "exact":
            sev = "minor"
        elif geo["ledge_plat"] > 30:
            sev = "significant"

    # Events
    if ev.get("status") == "NO_PLAT_EVENTS":
        reasons.append("no Platinum events.json resolved")
    else:
        ew, pw = ev["counts"]["warps"]
        if pw and ew == 0:
            reasons.append(f"missing all {pw} Platinum warps")
            sev = "significant"
        elif pw and abs(ew - pw) > max(2, pw * 0.4):
            reasons.append(f"warp count em={ew} plat={pw}")
            if sev == "exact":
                sev = "minor"
        # position fidelity
        if pw and ev.get("origin"):
            exact = ev.get("warp_exact", 0)
            if exact == pw and not ev.get("warp_unmatched_plat") and not ev.get("warp_unmatched_em"):
                pass  # perfect warps
            elif exact + ev.get("warp_near", 0) >= pw * 0.8:
                if exact < pw:
                    reasons.append(f"warps: {exact}/{pw} exact, {ev.get('warp_near',0)} within 2")
                    if sev == "exact":
                        sev = "minor"
            else:
                reasons.append(
                    f"warps poorly aligned: {exact}/{pw} exact; "
                    f"{len(ev.get('warp_unmatched_plat') or [])} unmatched Platinum"
                )
                sev = "significant"
        eo, po = ev["counts"]["objects"]
        if po and eo < po * 0.4:
            reasons.append(f"object count sparse em={eo} plat={po}")
            if sev == "exact":
                sev = "minor"
        mr = ev.get("obj_match_rate")
        if mr is not None and po >= 5 and mr < 0.35:
            reasons.append(f"object position match rate {mr:.0%} vs Platinum")
            if sev == "exact":
                sev = "minor"

    if not reasons and sev == "exact":
        reasons.append("size match; collision corridors OK; warps align")
    return sev, reasons

def main():
    # Resolve plat folder aliases that failed
    # Fix Route204 naming in platinum
    for alt in PLAT_MAPS.iterdir():
        if alt.name.startswith("route_204"):
            print("plat route204 variants:", alt.name)
        if alt.name.startswith("route_205"):
            print("plat route205 variants:", alt.name)
        if alt.name.startswith("route_210"):
            print("plat route210 variants:", alt.name)
        if alt.name.startswith("valley_wind"):
            print("plat windworks:", alt.name)
        if alt.name.startswith("oreburgh_gate"):
            print("plat oreburgh_gate:", alt.name)
        if alt.name.startswith("mt_coronet"):
            print("plat coronet:", alt.name)

    reports = []
    for name in LAND_TABLE:
        geo = compare_geometry(name)
        origin = DOCUMENTED_ORIGIN.get(name)
        # Always try fit if no documented; also verify documented
        plat_dir = resolve_plat_folder(name)
        if origin is None and plat_dir:
            em = json.loads((MAPS / name / "map.json").read_text())
            pe = json.loads((plat_dir / "events.json").read_text())
            L = meta[name]
            fitted, info = fit_origin(pe.get("warp_events") or [], em.get("warp_events") or [],
                                      int(L["width"]), int(L["height"]))
            origin = fitted
        ev = compare_events(name, origin)
        sev, reasons = verdict(geo, ev)
        rec = {
            "map": name,
            "verdict": sev,
            "reasons": reasons,
            "geometry": geo,
            "events": {k: v for k, v in ev.items() if k not in ("warp_deltas_sample",) or v},
            "warp_deltas_sample": ev.get("warp_deltas_sample"),
            "suggested_fix": None,
        }
        # Suggested fixes
        fixes = []
        if not geo["size_match"]:
            fixes.append(f"Regenerate layout from LAND_TABLE chunks to {geo['size_plat']}")
        if geo["walk_block_rate"] > 0.05:
            fixes.append("Clear Emerald solids on Platinum-walkable corridor tiles (re-run land stitch / punch doors)")
        if geo["coll_rate"] > 0.35 and geo["building_em"] > 50:
            fixes.append("Expected city diverge from Emerald building stamps; tighten door footprints to Platinum warp tiles only")
        if geo["coll_rate"] > 0.55 and geo["building_em"] < 20:
            fixes.append("Re-stitch cave land-data; collision stand-ins diverge heavily from Platinum")
        if geo["ledge_plat"] > 5 and geo["ledge_em"] == 0:
            fixes.append("Paint Emerald ledge metatiles (0x0D5/0x0D6) on Platinum ledge behavior tiles")
        if ev.get("warp_unmatched_plat"):
            kinds = sorted({u["kind"] for u in ev["warp_unmatched_plat"]})
            fixes.append(f"Add/move warps for missing Platinum doors: {', '.join(kinds[:8])}")
        if ev.get("warp_far") or (ev.get("warp_near") and ev.get("warp_exact", 0) < (ev["counts"]["warps"][1] or 0)):
            fixes.append("Nudge Emerald warp/door stamps to Platinum local coords (world - origin)")
        if ev.get("obj_match_rate") is not None and ev["obj_match_rate"] < 0.5 and ev["counts"]["objects"][1] > 5:
            fixes.append("Reposition NPCs/trainers/items toward Platinum local coords; add missing trainers/items")
        if ev.get("counts") and abs(ev["counts"]["warps"][0] - ev["counts"]["warps"][1]) > 2:
            fixes.append("Reconcile warp count with Platinum events.json")
        rec["suggested_fix"] = "; ".join(fixes) if fixes else "No geometry fix required (stand-in tiles OK)"
        reports.append(rec)

        print(f"[{sev.upper():12}] {name:28} size={geo['size_em']} coll={geo['coll_rate']:.1%} "
              f"block={geo['walk_blocked']} warps={ev.get('counts',{}).get('warps')} "
              f"origin={ev.get('origin')} hits={ev.get('warp_fit_hits')}")
        for r in reasons[:4]:
            print(f"             - {r}")

    out = Path("/tmp/qa-audit/platinum_1to1_report.json")
    out.write_text(json.dumps(reports, indent=2) + "\n")
    # Summary counts
    from collections import Counter
    c = Counter(r["verdict"] for r in reports)
    print(f"\n=== SUMMARY: {dict(c)} / {len(reports)} outdoor LAND_TABLE maps ===")
    print(f"Wrote {out}")
    return reports

if __name__ == "__main__":
    main()
