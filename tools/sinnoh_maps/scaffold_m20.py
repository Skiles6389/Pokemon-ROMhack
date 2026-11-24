#!/usr/bin/env python3
"""Scaffold M20 Pastoria corridor: Route 214, Valor Lakefront, Route 213,
Pastoria City + interiors, Barry rival, Crasher Wake gym, Galactic chase.

Story flow
----------
1. Barry waits outside Pastoria Gym (VAR_PASTORIA_CITY_STATE 0).  Battle him
   (TRAINER_BARRY_4_* via VAR_ROUTE201_BARRY_MON).  Hide Barry, state -> 1.
2. Challenge Crasher Wake.  Fen Badge + TM Brine.  State -> 2, un-hide the
   Galactic grunt near the Great Marsh gate (and Wake cameo).
3. Coord triggers near the Great Marsh (state 2): grunt hints at a device near
   Lake Valor, flees east.  Hide grunt, set FLAG_PASTORIA_GALACTIC_CHASE, state -> 3.

All patches are idempotent: running the script twice leaves the tree unchanged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data" / "maps"


# --------------------------------------------------------------------------- helpers
def obj(gfx, x, y, script, trainer="TRAINER_TYPE_NONE", sight="0", flag="0", movement="MOVEMENT_TYPE_FACE_DOWN", local_id=None, range_x=0, range_y=0):
    o = {
        "graphics_id": gfx,
        "x": x,
        "y": y,
        "elevation": 3,
        "movement_type": movement,
        "movement_range_x": range_x,
        "movement_range_y": range_y,
        "trainer_type": trainer,
        "trainer_sight_or_berry_tree_id": str(sight),
        "script": script,
        "flag": flag,
    }
    if local_id:
        o["local_id"] = local_id
    return o


def warp(x, y, dest, wid, elev=0):
    return {"x": x, "y": y, "elevation": elev, "dest_map": dest, "dest_warp_id": str(wid)}


def trigger(x, y, script, var="VAR_TEMP_0", val="0"):
    return {"type": "trigger", "x": x, "y": y, "elevation": 0, "var": var, "var_value": val, "script": script}


def sign(x, y, script):
    return {"type": "sign", "x": x, "y": y, "elevation": 0, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": script}


def conn(direction, map_id, offset=0):
    return {"map": map_id, "offset": offset, "direction": direction}


def write_map(name: str, data: dict, scripts: str):
    folder = MAPS / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "map.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (folder / "scripts.inc").write_text(scripts, encoding="utf-8")
    print("wrote", name)


def outdoor_base(map_id, name, layout, music="MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT", mapsec="MAPSEC_PASTORIA_CITY", map_type="MAP_TYPE_CITY"):
    return {
        "id": map_id,
        "name": name,
        "layout": layout,
        "music": music,
        "night_music": night,
        "region": "REGION_HOENN",
        "region_map_section": mapsec,
        "requires_flash": False,
        "weather": "WEATHER_SUNNY",
        "map_type": map_type,
        "allow_cycling": True,
        "allow_escaping": False,
        "allow_running": True,
        "show_map_name": True,
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": [],
        "object_events": [],
        "warp_events": [],
        "coord_events": [],
        "bg_events": [],
    }


def indoor_base(map_id, name, layout, music, mapsec="MAPSEC_PASTORIA_CITY", night=None, show_name=False, battle="MAP_BATTLE_SCENE_NORMAL"):
    d = {
        "id": map_id,
        "name": name,
        "layout": layout,
        "music": music,
        "region": "REGION_HOENN",
        "region_map_section": mapsec,
        "requires_flash": False,
        "weather": "WEATHER_NONE",
        "map_type": "MAP_TYPE_INDOOR",
        "allow_cycling": False,
        "allow_escaping": False,
        "allow_running": False,
        "show_map_name": show_name,
        "battle_scene": battle,
        "connections": None,
        "object_events": [],
        "warp_events": [],
        "coord_events": [],
        "bg_events": [],
    }
    if night:
        d["night_music"] = night
    return d


def house_base(map_id, name, layout="LAYOUT_HOUSE1", mapsec="MAPSEC_PASTORIA_CITY"):
    return indoor_base(map_id, name, layout, "MUS_PL_JUBILIFE", mapsec=mapsec, night="MUS_PL_JUBILIFE_NIGHT")


class Scr:
    """Small builder for scripts.inc content.

    Script bodies are written with 4-space indentation and converted to tabs; the token
    %P% expands to the map prefix.  Text blocks take one string per .string line; the
    final line receives the '$' terminator.
    """

    def __init__(self, prefix: str):
        self.p = prefix
        self.chunks: list[str] = []

    def raw(self, s: str):
        s = s.strip("\n").replace("%P%", self.p)
        s = re.sub(r"(?m)^    ", "\t", s)
        self.chunks.append(s + "\n")

    def text(self, name: str, *lines: str):
        body = "".join(f'\t.string "{ln}"\n' for ln in lines[:-1]) + f'\t.string "{lines[-1]}$"\n'
        self.chunks.append(f"{self.p}_Text_{name}:\n{body}")

    def npc(self, name: str, *lines: str):
        self.chunks.append(f"{self.p}_EventScript_{name}::\n\tmsgbox {self.p}_Text_{name}, MSGBOX_NPC\n\tend\n")
        self.text(name, *lines)

    def sign(self, name: str, *lines: str):
        self.chunks.append(f"{self.p}_EventScript_{name}::\n\tmsgbox {self.p}_Text_{name}, MSGBOX_SIGN\n\tend\n")
        self.text(name, *lines)

    def trainer(self, name: str, trainer: str, intro, defeat, after):
        self.chunks.append(
            f"{self.p}_EventScript_{name}::\n"
            f"\ttrainerbattle_single {trainer}, {self.p}_Text_{name}Intro, {self.p}_Text_{name}Defeat\n"
            f"\tmsgbox {self.p}_Text_{name}After, MSGBOX_AUTOCLOSE\n\tend\n"
        )
        self.text(f"{name}Intro", *intro)
        self.text(f"{name}Defeat", *defeat)
        self.text(f"{name}After", *after)

    def render(self) -> str:
        return "\n".join(self.chunks)


def map_scripts(prefix: str, transition: str | None = None, extra: str = "") -> str:
    lines = [f"{prefix}_MapScripts::"]
    if transition:
        lines.append(f"\tmap_script MAP_SCRIPT_ON_TRANSITION, {transition}")
    if extra:
        lines.append(extra)
    lines.append("\t.byte 0")
    return "\n".join(lines)


def land_entry(map_id, label, mons, rate=30):
    """mons: list of (species, level) length 12."""
    return {
        "map": map_id,
        "base_label": label,
        "land_mons": {
            "encounter_rate": rate,
            "mons": [{"min_level": lv, "max_level": lv, "species": sp} for sp, lv in mons],
        },
    }


# --------------------------------------------------------------------------- Route 214
def scaffold_route214():
    p = "Route214"
    data = outdoor_base("MAP_ROUTE214", p, "LAYOUT_ROUTE214",
                        music="MUS_PL_ROUTE203", night="MUS_PL_ROUTE203_NIGHT",
                        mapsec="MAPSEC_ROUTE_214", map_type="MAP_TYPE_ROUTE")
    data["connections"] = [
        conn("down", "MAP_VALOR_LAKEFRONT", -32),
    ]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_PSYCHIC_M", 27, 54, f"{p}_EventScript_Mitchell", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_LASS", 17, 20, f"{p}_EventScript_Abigail", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_MAN_3", 27, 79, f"{p}_EventScript_Douglas", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_MAN_3", 25, 45, f"{p}_EventScript_Brady", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_MAN_3", 15, 61, f"{p}_EventScript_Jamal", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_MANIAC", 10, 51, f"{p}_EventScript_Bryan", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_MANIAC", 17, 69, f"{p}_EventScript_Ronald", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_BEAUTY", 27, 48, f"{p}_EventScript_Devon", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_GENTLEMAN", 22, 36, f"{p}_EventScript_Carlos", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_DOWN"),
    ]
    data["warp_events"] = [
        warp(14, 5, "MAP_VEILSTONE_CITY_ROUTE214_GATE", 2),  # 0
        warp(15, 5, "MAP_VEILSTONE_CITY_ROUTE214_GATE", 3),  # 1
    ]
    data["coord_events"] = [
        trigger(9, 30, f"{p}_EventScript_CaveComingSoon"),
        trigger(9, 31, f"{p}_EventScript_CaveComingSoon"),
        trigger(10, 30, f"{p}_EventScript_CaveComingSoon"),
    ]
    data["bg_events"] = [
        sign(16, 8, f"{p}_EventScript_RouteSign"),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.trainer("Mitchell", "TRAINER_PSYCHIC_MITCHELL_R214",
              [r"Quiet your thoughts.\n", r"My POKéMON already know yours."],
              [r"Your will cut through mine..."],
              [r"Meditation helps on long roads.\n", r"Try it before the next Gym."])
    s.trainer("Abigail", "TRAINER_PSYCHIC_ABIGAIL_R214",
              [r"I foresaw a strong Trainer\n", r"walking this ridge. Was it you?"],
              [r"Ah... the vision was incomplete."],
              [r"Pastoria's marsh muddles focus.\n", r"Stay sharp down south!"])
    s.trainer("Douglas", "TRAINER_COLLECTOR_DOUGLAS_R214",
              [r"Rare specimens roam this trail!\n", r"I'll catalog yours in battle!"],
              [r"Noted... under “formidable.”"],
              [r"Collectors never stop looking.\n", r"Every route has a prize."])
    s.trainer("Brady", "TRAINER_COLLECTOR_BRADY_R214",
              [r"Hold still! I need one more\n", r"entry for my binder!"],
              [r"Page torn... metaphorically."],
              [r"A good collection needs guts,\n", r"not just luck."])
    s.trainer("Jamal", "TRAINER_COLLECTOR_JAMAL_R214",
              [r"Trade you a story for a fight?\n", r"No? Fine--battle it is!"],
              [r"That chapter ended too fast..."],
              [r"I'll write you as the rival who\n", r"kept walking south."])
    s.trainer("Bryan", "TRAINER_RUIN_MANIAC_BRYAN_R214",
              [r"Ruins whisper under these cliffs!\n", r"Spar with me while I listen!"],
              [r"The stones... went quiet."],
              [r"Ruin Maniac Cave is sealed for\n", r"now. Dig later, train today!"])
    s.trainer("Ronald", "TRAINER_RUIN_MANIAC_RONALD_R214",
              [r"Ancient paths fork every which\n", r"way. Pick mine--and lose!"],
              [r"History favors the bold..."],
              [r"Spring Path can wait. Pastoria\n", r"won't."])
    s.trainer("Devon", "TRAINER_BEAUTY_DEVON_R214",
              [r"Don't scuff the scenery!\n", r"Battle pretty, or not at all."],
              [r"Oh! You look good winning..."],
              [r"Valor Lakefront has the best\n", r"sunsets. Don't miss them!"])
    s.trainer("Carlos", "TRAINER_GENTLEMAN_CARLOS_R214",
              [r"A discreet investigation, hmm?\n", r"Let's call this a field test."],
              [r"Case closed--for me, that is."],
              [r"Keep notes on odd footprints.\n", r"Someone's stirring near the lake."])
    s.raw("""
%P%_EventScript_CaveComingSoon::
    lockall
    msgbox %P%_Text_CaveComingSoon, MSGBOX_DEFAULT
    closemessage
    applymovement OBJ_EVENT_ID_PLAYER, %P%_Movement_PushSouth
    waitmovement 0
    releaseall
    end

%P%_Movement_PushSouth:
    walk_down
    step_end
""")
    s.text("CaveComingSoon",
           r"Ruin Maniac Cave and Spring Path\n",
           r"coming in a later milestone!")
    s.sign("RouteSign",
           r"ROUTE 214\n",
           r"Veilstone City - Valor Lakefront")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Valor Lakefront
def scaffold_valor_lakefront():
    p = "ValorLakefront"
    data = outdoor_base("MAP_VALOR_LAKEFRONT", p, "LAYOUT_VALOR_LAKEFRONT",
                        music="MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT",
                        mapsec="MAPSEC_VALOR_LAKEFRONT", map_type="MAP_TYPE_ROUTE")
    data["connections"] = [
        conn("up", "MAP_ROUTE214", 32),
        conn("down", "MAP_ROUTE213", -32),
    ]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_WORKER_M", 52, 53, f"{p}_EventScript_EastWorker", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 36, 50, f"{p}_EventScript_Tourist", movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=2, range_y=1),
        obj("OBJ_EVENT_GFX_MAN_1", 28, 46, f"{p}_EventScript_ResortMan", movement="MOVEMENT_TYPE_LOOK_AROUND"),
        obj("OBJ_EVENT_GFX_LITTLE_GIRL", 41, 42, f"{p}_EventScript_Kid", movement="MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT", range_x=2),
        obj("OBJ_EVENT_GFX_OLD_WOMAN", 20, 52, f"{p}_EventScript_OldWoman", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_COOK", 33, 55, f"{p}_EventScript_CookOutside", movement="MOVEMENT_TYPE_FACE_DOWN"),
    ]
    data["warp_events"] = [
        warp(34, 54, "MAP_VALOR_LAKEFRONT_RESTAURANT", 0),       # 0
        warp(43, 45, "MAP_VALOR_LAKEFRONT_EAST_COTTAGE", 0),     # 1
        warp(18, 55, "MAP_VALOR_LAKEFRONT_WEST_COTTAGE", 0),     # 2
        warp(40, 40, "MAP_VALOR_LAKEFRONT_HOTEL_LOBBY", 0),      # 3
    ]
    data["coord_events"] = [
        trigger(45, 24, f"{p}_EventScript_LakeComingSoon"),
        trigger(45, 25, f"{p}_EventScript_LakeComingSoon"),
        trigger(44, 24, f"{p}_EventScript_LakeComingSoon"),
        trigger(46, 24, f"{p}_EventScript_LakeComingSoon"),
    ]
    data["bg_events"] = [
        sign(30, 48, f"{p}_EventScript_ResortSign"),
        sign(40, 41, f"{p}_EventScript_HotelSign"),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_LakeComingSoon::
    lockall
    msgbox %P%_Text_LakeComingSoon, MSGBOX_DEFAULT
    closemessage
    applymovement OBJ_EVENT_ID_PLAYER, %P%_Movement_PushSouth
    waitmovement 0
    releaseall
    end

%P%_Movement_PushSouth:
    walk_down
    step_end
""")
    s.text("LakeComingSoon",
           r"Lake Valor and the Galactic\n",
           r"storyline coming in a later\l",
           r"milestone!")
    s.npc("EastWorker",
          r"Route 222 and Sunyshore City\n",
          r"coming in a later milestone!\p",
          r"For now, the east path is closed.")
    s.npc("Tourist",
          r"The lakefront breeze is perfect!\n",
          r"I could sit here all afternoon.")
    s.npc("ResortMan",
          r"Hotel, restaurant, cottages...\n",
          r"This strip is Sinnoh's quiet gem.")
    s.npc("Kid",
          r"I stamped my travel notebook at\n",
          r"the hotel desk. Collect them all!")
    s.npc("OldWoman",
          r"Years ago the lake shook once.\n",
          r"Folks still talk about it softly.")
    s.npc("CookOutside",
          r"Fresh catch special today!\n",
          r"Come inside if you're hungry.")
    s.sign("ResortSign",
           r"VALOR LAKEFRONT\n",
           r"A calm resort by the lake")
    s.sign("HotelSign",
           r"VALOR LAKEFRONT HOTEL\n",
           r"Stamp your journey here!")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Route 213
def scaffold_route213():
    p = "Route213"
    data = outdoor_base("MAP_ROUTE213", p, "LAYOUT_ROUTE213",
                        music="MUS_PL_ROUTE203", night="MUS_PL_ROUTE203_NIGHT",
                        mapsec="MAPSEC_ROUTE_213", map_type="MAP_TYPE_ROUTE")
    data["connections"] = [
        conn("up", "MAP_VALOR_LAKEFRONT", 32),
        conn("left", "MAP_PASTORIA_CITY", 0),
    ]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_TUBER_M", 63, 32, f"{p}_EventScript_Jared", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_TUBER_F", 64, 27, f"{p}_EventScript_Chelsea", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_SWIMMER_M", 51, 58, f"{p}_EventScript_Shelton", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_WALK_LEFT_AND_RIGHT", range_x=3),
        obj("OBJ_EVENT_GFX_SWIMMER_M", 85, 42, f"{p}_EventScript_Evan", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_SWIMMER_F", 90, 42, f"{p}_EventScript_Mary", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_SWIMMER_F", 62, 51, f"{p}_EventScript_Haley", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_UP"),
        obj("OBJ_EVENT_GFX_BEAUTY", 28, 27, f"{p}_EventScript_Cyndy", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_FISHERMAN", 25, 45, f"{p}_EventScript_Kenneth", trainer="TRAINER_TYPE_NORMAL", sight="2", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_SAILOR", 77, 54, f"{p}_EventScript_Paul", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 68, 20, f"{p}_EventScript_Beachgoer", movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=2, range_y=1),
    ]
    data["warp_events"] = [
        warp(23, 34, "MAP_ROUTE213_DR_FOOTSTEP_HOUSE", 0),  # 0
        warp(66, 18, "MAP_ROUTE213_HOTEL_LOBBY", 0),         # 1
    ]
    data["bg_events"] = [
        sign(10, 14, f"{p}_EventScript_RouteSign"),
        sign(66, 19, f"{p}_EventScript_HotelSign"),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.trainer("Jared", "TRAINER_TUBER_JARED_R213",
              [r"Cannonball contest! Loser buys\n", r"juice--winner gets bragging!"],
              [r"Splash... you win the splash!"],
              [r"The tide's friendly today.\n", r"Perfect for a rematch later!"])
    s.trainer("Chelsea", "TRAINER_TUBER_CHELSEA_R213",
              [r"Sand in my shoes, salt in my\n", r"hair--and a battle for fun!"],
              [r"Aww, wiped out..."],
              [r"Pastoria's marsh is muddy, but\n", r"this beach is pure sparkle!"])
    s.trainer("Shelton", "TRAINER_SWIMMER_SHELTON_R213",
              [r"Laps before lunch!\n", r"You're my warm-up partner!"],
              [r"Pulled a muscle in my pride..."],
              [r"Keep kicking. Endurance wins\n", r"long fights."])
    s.trainer("Evan", "TRAINER_SWIMMER_EVAN_R213",
              [r"Deep water, deep strategy!\n", r"Let's dive into a match!"],
              [r"I sank under that pressure..."],
              [r"Floatzel love this coastline.\n", r"Watch the shallows!"])
    s.trainer("Mary", "TRAINER_SWIMMER_MARY_R213",
              [r"Sun, surf, and a sharp Trainer!\n", r"Don't make me chase you!"],
              [r"You rode that wave perfectly..."],
              [r"Hotel guests cheer from the\n", r"balcony. Put on a show!"])
    s.trainer("Haley", "TRAINER_SWIMMER_HALEY_R213",
              [r"I timed my strokes for this!\n", r"Ready when you are!"],
              [r"Off-beat... nice tempo."],
              [r"Cool down before the Gym.\n", r"Wake hits hard and wet."])
    s.trainer("Cyndy", "TRAINER_BEAUTY_CYNDY_R213",
              [r"Beach fashion meets battle\n", r"fashion. Strike a pose--then go!"],
              [r"My look survived. My team didn't."],
              [r"Dr. Footstep studies tracks in\n", r"the sand. Say hello if you visit."])
    s.trainer("Kenneth", "TRAINER_FISHERMAN_KENNETH_R213",
              [r"Hook, line, and a challenger!\n", r"Let's see who flops first!"],
              [r"Reeled in--and tossed back."],
              [r"Patience on the pier beats\n", r"hurrying into Pastoria."])
    s.trainer("Paul", "TRAINER_SAILOR_PAUL_R213",
              [r"Shore leave means sparring!\n", r"Permission to engage?"],
              [r"Aye... permission granted to you."],
              [r"Ships watch this coast for\n", r"weather. Stay weather-ready!"])
    s.npc("Beachgoer",
          r"The hotel pool is nice, but the\n",
          r"real ocean is right here!")
    s.sign("RouteSign",
           r"ROUTE 213\n",
           r"Pastoria City - Valor Lakefront")
    s.sign("HotelSign",
           r"ROUTE 213 HOTEL\n",
           r"Ocean views and soft pillows")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Pastoria City
BARRY_TRIGGER_TILES = [(12, 28), (13, 28), (14, 28), (13, 29), (12, 29), (14, 29)]
CHASE_TRIGGER_TILES = [(x, y) for x in range(34, 37) for y in range(10, 13)]


def scaffold_pastoria_city():
    p = "PastoriaCity"
    data = outdoor_base("MAP_PASTORIA_CITY", p, "LAYOUT_PASTORIA_CITY",
                        music="MUS_PL_JUBILIFE", night="MUS_PL_JUBILIFE_NIGHT",
                        mapsec="MAPSEC_PASTORIA_CITY", map_type="MAP_TYPE_CITY")
    data["connections"] = [
        conn("right", "MAP_ROUTE213", 0),
    ]
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_WALLY", 13, 28, f"{p}_EventScript_Barry",
            flag="FLAG_HIDE_PASTORIA_BARRY", local_id="LOCALID_PASTORIA_BARRY",
            movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_MAGMA_MEMBER_M", 38, 10, f"{p}_EventScript_GalacticGrunt",
            flag="FLAG_HIDE_PASTORIA_GALACTIC_GRUNT", local_id="LOCALID_PASTORIA_GRUNT",
            movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_SAILOR", 15, 28, f"{p}_EventScript_WakeCameo",
            flag="FLAG_HIDE_PASTORIA_WAKE_CAMEO", local_id="LOCALID_PASTORIA_WAKE",
            movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_WORKER_M", 2, 46, f"{p}_EventScript_WestWorker",
            movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_WOMAN_2", 28, 30, f"{p}_EventScript_Woman",
            movement="MOVEMENT_TYPE_WANDER_AROUND", range_x=2, range_y=1),
        obj("OBJ_EVENT_GFX_BOY_1", 20, 40, f"{p}_EventScript_Boy",
            movement="MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT", range_x=2),
        obj("OBJ_EVENT_GFX_OLD_MAN", 40, 20, f"{p}_EventScript_OldMan",
            movement="MOVEMENT_TYPE_LOOK_AROUND"),
        obj("OBJ_EVENT_GFX_GIRL_1", 30, 18, f"{p}_EventScript_Girl",
            movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_FISHERMAN", 42, 40, f"{p}_EventScript_Fisherman",
            movement="MOVEMENT_TYPE_FACE_DOWN"),
    ]
    data["warp_events"] = [
        warp(13, 27, "MAP_PASTORIA_CITY_GYM", 0),                    # 0 Gym
        warp(24, 15, "MAP_PASTORIA_CITY_POKEMON_CENTER_1F", 0),       # 1 Center
        warp(25, 44, "MAP_PASTORIA_CITY_MART", 0),                    # 2 Mart
        warp(25, 35, "MAP_PASTORIA_CITY_MOVE_REMINDER_HOUSE", 0),     # 3 Move Reminder
        warp(24, 24, "MAP_PASTORIA_CITY_NORTH_HOUSE", 0),             # 4 North
        warp(35, 35, "MAP_PASTORIA_CITY_EAST_HOUSE", 0),              # 5 East
        warp(48, 19, "MAP_PASTORIA_CITY_NORTHEAST_HOUSE", 0),         # 6 NE
        warp(13, 44, "MAP_PASTORIA_CITY_SOUTHWEST_HOUSE", 0),         # 7 SW
        warp(34, 9, "MAP_PASTORIA_CITY_GREAT_MARSH_GATE", 0),         # 8 Marsh gate
    ]
    coords = []
    for x, y in BARRY_TRIGGER_TILES:
        coords.append(trigger(x, y, f"{p}_EventScript_BarryTrigger", "VAR_PASTORIA_CITY_STATE", "0"))
    for x, y in CHASE_TRIGGER_TILES:
        coords.append(trigger(x, y, f"{p}_EventScript_GalacticChase", "VAR_PASTORIA_CITY_STATE", "2"))
    data["coord_events"] = coords
    data["bg_events"] = [
        sign(12, 28, f"{p}_EventScript_GymSign"),
        sign(22, 18, f"{p}_EventScript_CitySign"),
        sign(34, 10, f"{p}_EventScript_MarshSign"),
    ]

    s = Scr(p)
    s.raw(map_scripts(p, f"{p}_OnTransition"))
    s.raw("""
%P%_OnTransition:
    setflag FLAG_VISITED_PASTORIA_CITY
    end
""")
    # Barry battle (Hearthome pattern)
    s.raw("""
%P%_EventScript_BarryTrigger::
    lockall
    goto_if_set FLAG_HIDE_PASTORIA_BARRY, %P%_EventScript_BarryAlreadyDone
    playse SE_PIN
    applymovement LOCALID_PASTORIA_BARRY, Common_Movement_ExclamationMark
    waitmovement 0
    applymovement LOCALID_PASTORIA_BARRY, Common_Movement_FacePlayer
    waitmovement 0
    applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_FaceUp
    waitmovement 0
    msgbox %P%_Text_BarryIntro, MSGBOX_DEFAULT
    switch VAR_ROUTE201_BARRY_MON
    case 0, %P%_EventScript_BattleChimchar
    case 1, %P%_EventScript_BattlePiplup
    case 2, %P%_EventScript_BattleTurtwig
    end

%P%_EventScript_BarryAlreadyDone::
    releaseall
    end

%P%_EventScript_BattleChimchar::
    trainerbattle LOCALID_PASTORIA_BARRY, TRAINER_BARRY_4_CHIMCHAR, %P%_Text_BarryChallenge, %P%_Text_BarryDefeat, %P%_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
    end

%P%_EventScript_BattlePiplup::
    trainerbattle LOCALID_PASTORIA_BARRY, TRAINER_BARRY_4_PIPLUP, %P%_Text_BarryChallenge, %P%_Text_BarryDefeat, %P%_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
    end

%P%_EventScript_BattleTurtwig::
    trainerbattle LOCALID_PASTORIA_BARRY, TRAINER_BARRY_4_TURTWIG, %P%_Text_BarryChallenge, %P%_Text_BarryDefeat, %P%_EventScript_AfterBarry, LOCALID_NONE, TRAINER_NONE, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
    end

%P%_EventScript_AfterBarry::
    msgbox %P%_Text_BarryAfter, MSGBOX_DEFAULT
    closemessage
    applymovement LOCALID_PASTORIA_BARRY, %P%_Movement_BarryLeave
    waitmovement 0
    removeobject LOCALID_PASTORIA_BARRY
    setflag FLAG_HIDE_PASTORIA_BARRY
    setvar VAR_PASTORIA_CITY_STATE, 1
    releaseall
    end

%P%_Movement_BarryLeave:
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_up
    walk_fast_up
    walk_fast_up
    step_end

%P%_EventScript_Barry::
    msgbox %P%_Text_BarryWait, MSGBOX_NPC
    end
""")
    s.text("BarryIntro",
           r"BARRY: {PLAYER}!! I beat you here\n",
           r"fair and square--mostly!\p",
           r"Pastoria's Gym Leader uses Water\n",
           r"types that hit like tidal waves!\p",
           r"But first, you and me. Right now.\n",
           r"No warm-ups. Full power!")
    s.text("BarryChallenge",
           r"BARRY: Don't blink!\n",
           r"My team's been training nonstop!")
    s.text("BarryDefeat",
           r"What?! Even here you pull ahead?!")
    s.text("BarryAfter",
           r"BARRY: Fine! You earned the first\n",
           r"shot at CRASHER WAKE!\p",
           r"I'll scout the Great Marsh while\n",
           r"you wring out that Fen Badge.\p",
           r"Don't you dare lose--I'd never\n",
           r"hear the end of it from myself!")
    s.text("BarryWait",
           r"BARRY: Quit stalling!\n",
           r"Step up and battle already!")

    # Galactic chase
    s.raw("""
%P%_EventScript_GalacticChase::
    lockall
    playse SE_PIN
    applymovement LOCALID_PASTORIA_GRUNT, Common_Movement_ExclamationMark
    waitmovement 0
    applymovement LOCALID_PASTORIA_GRUNT, Common_Movement_FacePlayer
    waitmovement 0
    msgbox %P%_Text_GruntChase, MSGBOX_DEFAULT
    closemessage
    applymovement LOCALID_PASTORIA_GRUNT, %P%_Movement_GruntFlee
    waitmovement 0
    removeobject LOCALID_PASTORIA_GRUNT
    setflag FLAG_HIDE_PASTORIA_GALACTIC_GRUNT
    setflag FLAG_PASTORIA_GALACTIC_CHASE
    setvar VAR_PASTORIA_CITY_STATE, 3
    msgbox %P%_Text_ChaseAftermath, MSGBOX_DEFAULT
    closemessage
    releaseall
    end

%P%_Movement_GruntFlee:
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    walk_fast_right
    step_end

%P%_EventScript_GalacticGrunt::
    lock
    faceplayer
    msgbox %P%_Text_GruntIdle, MSGBOX_DEFAULT
    release
    end
""")
    s.text("GruntChase",
           r"GRUNT: You again?! Stay out of\n",
           r"TEAM GALACTIC's business!\p",
           r"The device by Lake Valor is none\n",
           r"of your concern. We're already\l",
           r"ahead of schedule!\p",
           r"Tell that loud Gym Leader to keep\n",
           r"his waves to himself--I'm gone!")
    s.text("ChaseAftermath",
           r"He bolted east toward the lake\n",
           r"road. Whatever they're building,\l",
           r"Lake Valor is the next stop.")
    s.text("GruntIdle",
           r"Buzz off. I'm waiting for a\n",
           r"signal--and you're not it.")

    s.raw("""
%P%_EventScript_WakeCameo::
    lock
    faceplayer
    goto_if_set FLAG_PASTORIA_GALACTIC_CHASE, %P%_EventScript_WakeAfterChase
    msgbox %P%_Text_WakeCameo, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_WakeAfterChase::
    msgbox %P%_Text_WakeAfterChase, MSGBOX_DEFAULT
    release
    end
""")
    s.text("WakeCameo",
           r"CRASHER WAKE: That badge looks\n",
           r"good on you!\p",
           r"I spotted a Galactic goon near the\n",
           r"marsh gate. Sniff around if you're\l",
           r"curious--just don't get soaked!")
    s.text("WakeAfterChase",
           r"CRASHER WAKE: He ran for the lake?\n",
           r"Hah! Waves always push troublemakers\l",
           r"where the current wants them.\p",
           r"When the road opens, ride it!")

    s.npc("WestWorker",
          r"Route 212 and the Trophy Garden\n",
          r"coming in the next milestone!\p",
          r"This gate stays shut for now.")
    s.npc("Woman",
          r"Pastoria sits between marsh mist\n",
          r"and ocean spray. Pack an extra\l",
          r"pair of socks!")
    s.npc("Boy",
          r"I want to tour the Great Marsh,\n",
          r"but the desk says “coming soon.”")
    s.npc("OldMan",
          r"CRASHER WAKE crashes waves and\n",
          r"Trainers alike. Bring Electric or\l",
          r"Grass if you value dry shoes.")
    s.npc("Girl",
          r"The Move Reminder in the middle\n",
          r"house loves Heart Scales. Save\l",
          r"yours from the beach!")
    s.npc("Fisherman",
          r"Marsh, lake, sea--Pastoria's a\n",
          r"angler paradise. Cast wisely.")
    s.sign("GymSign",
           r"PASTORIA CITY POKéMON GYM\n",
           r"LEADER: CRASHER WAKE\l",
           r"A Man Who Swims with the Tides!")
    s.sign("CitySign",
           r"PASTORIA CITY\n",
           r"The moist, marshy city of water")
    s.sign("MarshSign",
           r"GREAT MARSH GATE\n",
           r"Safari tours temporarily closed")
    write_map(p, data, s.render())

# --------------------------------------------------------------------------- Pokemon Center
def scaffold_center():
    p = "PastoriaCity_PokemonCenter_1F"
    data = indoor_base("MAP_PASTORIA_CITY_POKEMON_CENTER_1F", p, "LAYOUT_POKEMON_CENTER_1F",
                       "MUS_PL_POKE_CENTER", night="MUS_PL_POKE_CENTER_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_NURSE", 7, 2, f"{p}_EventScript_Nurse", local_id="LOCALID_PASTORIA_NURSE"),
        obj("OBJ_EVENT_GFX_FISHERMAN", 2, 3, f"{p}_EventScript_Fisherman"),
        obj("OBJ_EVENT_GFX_GIRL_2", 11, 5, f"{p}_EventScript_Girl"),
    ]
    data["warp_events"] = [
        warp(7, 8, "MAP_PASTORIA_CITY", 1, 3),
        warp(6, 8, "MAP_PASTORIA_CITY", 1, 3),
        warp(1, 6, "MAP_PASTORIA_CITY_POKEMON_CENTER_2F", 0, 4),
    ]
    s = Scr(p)
    s.raw(f"""
%P%_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, %P%_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

%P%_OnTransition:
    setrespawn HEAL_LOCATION_PASTORIA_CITY
    end

%P%_EventScript_Nurse::
    setvar VAR_0x800B, LOCALID_PASTORIA_NURSE
    call Common_EventScript_PkmnCenterNurse
    waitmessage
    waitbuttonpress
    release
    end
""")
    s.npc("Fisherman",
          r"I healed my team after a marsh\n",
          r"mud bath. The nurse didn't blink.")
    s.npc("Girl",
          r"CRASHER WAKE's Gym is soaked!\n",
          r"Pack towels and Thunderbolts.")
    write_map(p, data, s.render())

    p2 = "PastoriaCity_PokemonCenter_2F"
    data2 = indoor_base("MAP_PASTORIA_CITY_POKEMON_CENTER_2F", p2, "LAYOUT_POKEMON_CENTER_2F",
                        "MUS_PL_POKE_CENTER", night="MUS_PL_POKE_CENTER_NIGHT")
    data2["warp_events"] = [warp(1, 6, "MAP_PASTORIA_CITY_POKEMON_CENTER_1F", 2, 4)]
    write_map(p2, data2, f"{p2}_MapScripts::\n\t.byte 0\n")


# --------------------------------------------------------------------------- Mart
def scaffold_mart():
    p = "PastoriaCity_Mart"
    data = indoor_base("MAP_PASTORIA_CITY_MART", p, "LAYOUT_MART", "MUS_PL_POKE_MART")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 1, 3, f"{p}_EventScript_Clerk"),
        obj("OBJ_EVENT_GFX_MAN_1", 7, 2, f"{p}_EventScript_Customer"),
    ]
    data["warp_events"] = [
        warp(3, 7, "MAP_PASTORIA_CITY", 2),
        warp(4, 7, "MAP_PASTORIA_CITY", 2),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_Clerk::
    lock
    faceplayer
    msgbox %P%_Text_ClerkAsk, MSGBOX_DEFAULT
    pokemart %P%_Pokemart
    msgbox %P%_Text_ClerkFarewell, MSGBOX_DEFAULT
    release
    end

    .align 2
%P%_Pokemart:
    .2byte ITEM_POKE_BALL
    .2byte ITEM_GREAT_BALL
    .2byte ITEM_POTION
    .2byte ITEM_SUPER_POTION
    .2byte ITEM_ANTIDOTE
    .2byte ITEM_PARALYZE_HEAL
    .2byte ITEM_AWAKENING
    .2byte ITEM_BURN_HEAL
    .2byte ITEM_ESCAPE_ROPE
    .2byte ITEM_REPEL
    .2byte ITEM_NONE
    release
    end
""")
    s.text("ClerkAsk",
           r"Welcome to Pastoria Mart!\n",
           r"Need supplies for the marsh?")
    s.text("ClerkFarewell",
           r"Stay dry out there!")
    s.npc("Customer",
          r"Great Balls and Super Potions--\n",
          r"that's my marsh kit.")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Gym
def scaffold_gym():
    p = "PastoriaCity_Gym"
    data = indoor_base("MAP_PASTORIA_CITY_GYM", p, "LAYOUT_PASTORIA_CITY_GYM", "MUS_PL_GYM",
                       mapsec="MAPSEC_PASTORIA_GYM", show_name=True, battle="MAP_BATTLE_SCENE_GYM")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_SAILOR", 12, 4, f"{p}_EventScript_CrasherWake", local_id="LOCALID_PASTORIA_GYM_WAKE"),
        obj("OBJ_EVENT_GFX_TUBER_M", 4, 10, f"{p}_EventScript_Jacky", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_TUBER_F", 19, 10, f"{p}_EventScript_Caitlyn", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_SAILOR", 4, 18, f"{p}_EventScript_Damian", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_SAILOR", 19, 18, f"{p}_EventScript_Samson", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_FISHERMAN", 4, 26, f"{p}_EventScript_Erick", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_RIGHT"),
        obj("OBJ_EVENT_GFX_FISHERMAN", 19, 26, f"{p}_EventScript_Walter", trainer="TRAINER_TYPE_NORMAL", sight="3", movement="MOVEMENT_TYPE_FACE_LEFT"),
        obj("OBJ_EVENT_GFX_MAN_2", 8, 34, f"{p}_EventScript_GymGuide"),
    ]
    data["warp_events"] = [
        warp(11, 39, "MAP_PASTORIA_CITY", 0),
        warp(12, 39, "MAP_PASTORIA_CITY", 0),
    ]
    data["bg_events"] = [
        sign(10, 36, f"{p}_EventScript_Statue"),
        sign(13, 36, f"{p}_EventScript_Statue"),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_CrasherWake::
    lock
    faceplayer
    goto_if_eq VAR_PASTORIA_CITY_STATE, 0, %P%_EventScript_WakeWaitBarry
    trainerbattle_single TRAINER_LEADER_CRASHER_WAKE, %P%_Text_WakeIntro, %P%_Text_WakeDefeat, %P%_EventScript_WakeDefeated, NO_MUSIC
    goto_if_unset FLAG_RECEIVED_PASTORIA_GYM_TM, %P%_EventScript_GiveTM
    msgbox %P%_Text_WakeAfter, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_WakeWaitBarry::
    msgbox %P%_Text_WakeWaitBarry, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_WakeDefeated::
    message %P%_Text_ReceivedFenBadge
    waitmessage
    call Common_EventScript_PlayGymBadgeFanfare
    msgbox %P%_Text_FenBadgeInfo, MSGBOX_DEFAULT
    setflag FLAG_BADGE05_GET
    setvar VAR_PASTORIA_CITY_STATE, 2
    clearflag FLAG_HIDE_PASTORIA_GALACTIC_GRUNT
    clearflag FLAG_HIDE_PASTORIA_WAKE_CAMEO
    goto %P%_EventScript_GiveTM
    end

%P%_EventScript_GiveTM::
    giveitem ITEM_TM_BRINE
    goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
    setflag FLAG_RECEIVED_PASTORIA_GYM_TM
    msgbox %P%_Text_ExplainTM, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_GymGuide::
    lock
    faceplayer
    goto_if_set FLAG_BADGE05_GET, %P%_EventScript_GuideVictory
    msgbox %P%_Text_GuideAdvice, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_GuideVictory::
    msgbox %P%_Text_GuideVictory, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_Statue::
    lockall
    goto_if_set FLAG_BADGE05_GET, %P%_EventScript_StatueWon
    msgbox %P%_Text_Statue, MSGBOX_DEFAULT
    releaseall
    end

%P%_EventScript_StatueWon::
    msgbox %P%_Text_StatueWon, MSGBOX_DEFAULT
    releaseall
    end
""")
    s.trainer("Jacky", "TRAINER_TUBER_JACKY_PASTORIA",
              [r"Cannonball into battle!\n", r"Water types make the biggest splash!"],
              [r"I wiped out..."],
              [r"Keep your footing on the bridges.\n", r"One slip and you're soaked!"])
    s.trainer("Caitlyn", "TRAINER_TUBER_CAITLYN_PASTORIA",
              [r"Don't drip on my turf!\n", r"I'll wash you out myself!"],
              [r"Totally drenched..."],
              [r"WAKE loves a fair fight.\n", r"Bring your best tide."])
    s.trainer("Damian", "TRAINER_SAILOR_DAMIAN_PASTORIA",
              [r"All hands on deck!\n", r"This Gym runs on sea discipline!"],
              [r"Permission to recover granted..."],
              [r"Watch the side lanes. Trainers\n", r"hide where the water laps."])
    s.trainer("Samson", "TRAINER_SAILOR_SAMSON_PASTORIA",
              [r"I've sailed rougher than this.\n", r"Show me your sea legs!"],
              [r"Capsized by a landlubber..."],
              [r"Electric moves sting Water hard.\n", r"Pack a shock if you can."])
    s.trainer("Erick", "TRAINER_FISHERMAN_ERICK_PASTORIA",
              [r"Hooked a challenger!\n", r"Let's see who gets reeled in!"],
              [r"Line snapped..."],
              [r"Patience wins long battles.\n", r"Don't rush the Leader."])
    s.trainer("Walter", "TRAINER_FISHERMAN_WALTER_PASTORIA",
              [r"Quiet waters before the storm.\n", r"You're the storm, aren't you?"],
              [r"The catch got away..."],
              [r"WAKE's Floatzel is lightning in\n", r"the water. Brace yourself!"])
    s.text("WakeWaitBarry",
           r"CRASHER WAKE: There's a bouncing\n",
           r"kid outside who wants you first!\p",
           r"Settle that rivalry, then crash\n",
           r"through my doors for real.")
    s.text("GuideAdvice",
           r"Yo! Ready to get soaked?\p",
           r"CRASHER WAKE rides Water-types.\n",
           r"Grass and Electric moves drain\l",
           r"the pool fast!\p",
           r"Tubers, Sailors, and Fishermen\n",
           r"guard the bridges. Meet their\l",
           r"eyes and they'll charge!")
    s.text("GuideVictory",
           r"Fen Badge secured! Nice surfing!\p",
           r"I saw a shady character near the\n",
           r"Great Marsh gate. Worth a look.")
    s.text("Statue",
           r"PASTORIA CITY POKéMON GYM\n",
           r"LEADER: CRASHER WAKE")
    s.text("StatueWon",
           r"PASTORIA CITY POKéMON GYM\n",
           r"LEADER: CRASHER WAKE\p",
           r"Certified Trainers:\n",
           r"{PLAYER}")
    s.text("WakeIntro",
           r"CRASHER WAKE: Crash! Splash!\n",
           r"I'm CRASHER WAKE!\p",
           r"I surf every wave Sinnoh throws,\n",
           r"and my POKéMON ride right with me!\p",
           r"You want the Fen Badge? Then\n",
           r"bring a storm of your own!\p",
           r"Let's make a tidal roar!")
    s.text("WakeDefeat",
           r"Whoa! You smashed right through\n",
           r"my breakers! Outstanding!")
    s.text("ReceivedFenBadge",
           r"{PLAYER} received the FEN BADGE\n",
           r"from CRASHER WAKE!")
    s.text("FenBadgeInfo",
           r"With the FEN BADGE, POKéMON up to\n",
           r"Lv. 50 will obey you without fuss.\p",
           r"And take this--my favorite rainy-\n",
           r"day technique!")
    s.text("ExplainTM",
           r"That TM contains BRINE!\p",
           r"It hits harder when the foe's HP\n",
           r"is half or less. Finish strong!\p",
           r"Crash onward, champ!")
    s.text("WakeAfter",
           r"CRASHER WAKE: Keep riding those\n",
           r"highs! If TEAM GALACTIC stirs the\l",
           r"lake, give them a proper dunking!")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Great Marsh Gate
def scaffold_marsh_gate():
    p = "PastoriaCity_GreatMarshGate"
    data = indoor_base("MAP_PASTORIA_CITY_GREAT_MARSH_GATE", p, "LAYOUT_PASTORIA_CITY_GREAT_MARSH_GATE",
                       "MUS_PL_JUBILIFE", mapsec="MAPSEC_GREAT_MARSH_GATE", night="MUS_PL_JUBILIFE_NIGHT",
                       show_name=True)
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 4, 4, f"{p}_EventScript_Reception", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_CAMPER", 10, 7, f"{p}_EventScript_Camper", movement="MOVEMENT_TYPE_LOOK_AROUND"),
    ]
    data["warp_events"] = [
        warp(6, 11, "MAP_PASTORIA_CITY", 8),
        warp(7, 11, "MAP_PASTORIA_CITY", 8),
    ]
    data["coord_events"] = [
        trigger(6, 3, f"{p}_EventScript_SafariComingSoon"),
        trigger(7, 3, f"{p}_EventScript_SafariComingSoon"),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_Reception::
    lock
    faceplayer
    msgbox %P%_Text_Reception, MSGBOX_DEFAULT
    release
    end

%P%_EventScript_SafariComingSoon::
    lockall
    msgbox %P%_Text_SafariComingSoon, MSGBOX_DEFAULT
    closemessage
    applymovement OBJ_EVENT_ID_PLAYER, %P%_Movement_PushSouth
    waitmovement 0
    releaseall
    end

%P%_Movement_PushSouth:
    walk_down
    step_end
""")
    s.text("Reception",
           r"Welcome to the Great Marsh desk!\p",
           r"Safari tours aren't running yet,\n",
           r"but grab a map and dream big.\p",
           r"When the board opens, we'll hand\n",
           r"out trail tips--and maybe a tidy\l",
           r"field move for clearing fog.")
    s.text("SafariComingSoon",
           r"Safari coming later!\n",
           r"The marsh trails stay closed.")
    s.npc("Camper",
          r"I packed binoculars for rare\n",
          r"sightings. Patience is half the\l",
          r"adventure!")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Houses / Move Reminder
def scaffold_pastoria_houses():
    # Move Reminder
    p = "PastoriaCity_MoveReminderHouse"
    data = house_base("MAP_PASTORIA_CITY_MOVE_REMINDER_HOUSE", p)
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_OLD_MAN", 4, 4, f"{p}_EventScript_MoveReminder"),
        obj("OBJ_EVENT_GFX_LITTLE_GIRL", 7, 5, f"{p}_EventScript_Child"),
    ]
    data["warp_events"] = [warp(3, 7, "MAP_PASTORIA_CITY", 3), warp(4, 7, "MAP_PASTORIA_CITY", 3)]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_MoveReminder::
    lock
    faceplayer
    msgbox %P%_Text_MoveReminderIntro, MSGBOX_DEFAULT
    goto Common_EventScript_MoveRelearner
""")
    s.text("MoveReminderIntro",
           r"I help POKéMON remember moves\n",
           r"they've grown past.\p",
           r"Pick a partner and we'll dig\n",
           r"through their memories!")
    s.npc("Child",
          r"Grandpa's stories are longer than\n",
          r"the marsh boardwalk!")
    write_map(p, data, s.render())

    houses = [
        ("PastoriaCity_NorthHouse", "MAP_PASTORIA_CITY_NORTH_HOUSE", 4,
         "OBJ_EVENT_GFX_WOMAN_3",
         [r"Marsh mornings are foggy, but the\n", r"birds still sing on time."]),
        ("PastoriaCity_EastHouse", "MAP_PASTORIA_CITY_EAST_HOUSE", 5,
         "OBJ_EVENT_GFX_MAN_2",
         [r"I dry my nets on the east fence.\n", r"Ocean salt sticks longer than mud."]),
        ("PastoriaCity_NortheastHouse", "MAP_PASTORIA_CITY_NORTHEAST_HOUSE", 6,
         "OBJ_EVENT_GFX_POKEFAN_F",
         [r"My kids beg for Safari tickets.\n", r"Soon, I hope!"]),
        ("PastoriaCity_SouthwestHouse", "MAP_PASTORIA_CITY_SOUTHWEST_HOUSE", 7,
         "OBJ_EVENT_GFX_OLD_WOMAN",
         [r"Route 212 west of here leads to\n", r"gardens someday. For now, rest."]),
    ]
    for name, map_id, wid, gfx, lines in houses:
        data = house_base(map_id, name)
        data["object_events"] = [obj(gfx, 4, 4, f"{name}_EventScript_Resident")]
        data["warp_events"] = [warp(3, 7, "MAP_PASTORIA_CITY", wid), warp(4, 7, "MAP_PASTORIA_CITY", wid)]
        s = Scr(name)
        s.raw(map_scripts(name))
        s.npc("Resident", *lines)
        write_map(name, data, s.render())


# --------------------------------------------------------------------------- Valor interiors
def scaffold_valor_interiors():
    specs = [
        ("ValorLakefront_Restaurant", "MAP_VALOR_LAKEFRONT_RESTAURANT", 0, "LAYOUT_HOUSE1",
         "OBJ_EVENT_GFX_COOK", "Chef",
         [r"Today's special is lake stew!\n", r"Sit anywhere--the view is free."]),
        ("ValorLakefront_EastCottage", "MAP_VALOR_LAKEFRONT_EAST_COTTAGE", 1, "LAYOUT_HOUSE1",
         "OBJ_EVENT_GFX_WOMAN_2", "Resident",
         [r"We rented this cottage for the\n", r"week. The lake lulls us to sleep."]),
        ("ValorLakefront_WestCottage", "MAP_VALOR_LAKEFRONT_WEST_COTTAGE", 2, "LAYOUT_HOUSE1",
         "OBJ_EVENT_GFX_MAN_1", "Resident",
         [r"Quiet nights, bright stars.\n", r"Don't wake the neighbors late!"]),
    ]
    for name, mid, wid, layout, gfx, npc, lines in specs:
        data = house_base(mid, name, layout=layout, mapsec="MAPSEC_VALOR_LAKEFRONT")
        data["object_events"] = [obj(gfx, 4, 4, f"{name}_EventScript_{npc}")]
        data["warp_events"] = [warp(3, 7, "MAP_VALOR_LAKEFRONT", wid), warp(4, 7, "MAP_VALOR_LAKEFRONT", wid)]
        s = Scr(name)
        s.raw(map_scripts(name))
        s.npc(npc, *lines)
        write_map(name, data, s.render())

    # Hotel lobby (motel layout)
    p = "ValorLakefront_HotelLobby"
    data = indoor_base("MAP_VALOR_LAKEFRONT_HOTEL_LOBBY", p, "LAYOUT_LILYCOVE_CITY_COVE_LILY_MOTEL_1F",
                       "MUS_PL_JUBILIFE", mapsec="MAPSEC_VALOR_LAKEFRONT", night="MUS_PL_JUBILIFE_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 4, 2, f"{p}_EventScript_Clerk", movement="MOVEMENT_TYPE_FACE_DOWN"),
        obj("OBJ_EVENT_GFX_BEAUTY", 9, 5, f"{p}_EventScript_Guest"),
    ]
    data["warp_events"] = [
        warp(5, 8, "MAP_VALOR_LAKEFRONT", 3),
        warp(6, 8, "MAP_VALOR_LAKEFRONT", 3),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.npc("Clerk",
          r"Welcome to Valor Lakefront Hotel!\p",
          r"Stamp your travel log at the desk\n",
          r"and enjoy the lake breeze.")
    s.npc("Guest",
          r"I collected stamps from every\n",
          r"Sinnoh stop so far. This one's\l",
          r"my favorite ink color!")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Route 213 interiors
def scaffold_route213_interiors():
    p = "Route213_DrFootstepHouse"
    data = house_base("MAP_ROUTE213_DR_FOOTSTEP_HOUSE", p, mapsec="MAPSEC_ROUTE_213")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_SCIENTIST_1", 4, 4, f"{p}_EventScript_DrFootstep"),
    ]
    data["warp_events"] = [warp(3, 7, "MAP_ROUTE213", 0), warp(4, 7, "MAP_ROUTE213", 0)]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_DrFootstep::
    lock
    faceplayer
    msgbox %P%_Text_DrFootstep, MSGBOX_DEFAULT
    release
    end
""")
    s.text("DrFootstep",
           r"DR. FOOTSTEP: Footprints tell\n",
           r"stories sand can't keep secret.\p",
           r"A happy POKéMON leaves a light,\n",
           r"bouncy track. A worried one digs\l",
           r"deeper prints.\p",
           r"Walk together often--friendship\n",
           r"shows in every step!")
    write_map(p, data, s.render())

    p = "Route213_HotelLobby"
    data = indoor_base("MAP_ROUTE213_HOTEL_LOBBY", p, "LAYOUT_LILYCOVE_CITY_COVE_LILY_MOTEL_1F",
                       "MUS_PL_JUBILIFE", mapsec="MAPSEC_ROUTE_213", night="MUS_PL_JUBILIFE_NIGHT")
    data["object_events"] = [
        obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 4, 2, f"{p}_EventScript_Clerk"),
        obj("OBJ_EVENT_GFX_SAILOR", 9, 5, f"{p}_EventScript_Sailor"),
    ]
    data["warp_events"] = [
        warp(5, 8, "MAP_ROUTE213", 1),
        warp(6, 8, "MAP_ROUTE213", 1),
    ]
    s = Scr(p)
    s.raw(map_scripts(p))
    s.npc("Clerk",
          r"Route 213 Hotel--ocean on three\n",
          r"sides and pillows on the fourth!")
    s.npc("Sailor",
          r"Shore leave never lasts long.\n",
          r"I'll catch one more sunrise.")
    write_map(p, data, s.render())


# --------------------------------------------------------------------------- Open Route 214 gate
def patch_route214_gate():
    p = "VeilstoneCity_Route214Gate"
    data = indoor_base("MAP_VEILSTONE_CITY_ROUTE214_GATE", p, "LAYOUT_ROUTE110_SEASIDE_CYCLING_ROAD_ENTRANCE",
                       "MUS_PL_JUBILIFE", mapsec="MAPSEC_VEILSTONE_CITY", night="MUS_PL_JUBILIFE_NIGHT")
    data["allow_cycling"] = True
    data["allow_running"] = True
    data["object_events"] = [obj("OBJ_EVENT_GFX_MART_EMPLOYEE", 7, 2, f"{p}_EventScript_Guard")]
    data["warp_events"] = [
        warp(1, 5, "MAP_VEILSTONE_CITY", 13),
        warp(2, 5, "MAP_VEILSTONE_CITY", 14),
        warp(12, 5, "MAP_ROUTE214", 0),
        warp(13, 5, "MAP_ROUTE214", 1),
    ]
    data["coord_events"] = []
    s = Scr(p)
    s.raw(map_scripts(p))
    s.raw("""
%P%_EventScript_Guard::
    msgbox %P%_Text_Guard, MSGBOX_NPC
    end
""")
    s.text("Guard",
           r"Route 214 is open!\p",
           r"It runs south past Valor Lakefront\n",
           r"and on toward Pastoria City.\p",
           r"Watch for collectors and psychics\n",
           r"along the ridge.")
    write_map(p, data, s.render())
    print("patched VeilstoneCity_Route214Gate")


# --------------------------------------------------------------------------- Patches: map groups
M20_OUTDOOR = ["Route214", "ValorLakefront", "Route213", "PastoriaCity"]
M20_INDOOR = [
    "PastoriaCity_PokemonCenter_1F",
    "PastoriaCity_PokemonCenter_2F",
    "PastoriaCity_Mart",
    "PastoriaCity_Gym",
    "PastoriaCity_GreatMarshGate",
    "PastoriaCity_MoveReminderHouse",
    "PastoriaCity_NorthHouse",
    "PastoriaCity_EastHouse",
    "PastoriaCity_NortheastHouse",
    "PastoriaCity_SouthwestHouse",
    "ValorLakefront_Restaurant",
    "ValorLakefront_EastCottage",
    "ValorLakefront_WestCottage",
    "ValorLakefront_HotelLobby",
    "Route213_DrFootstepHouse",
    "Route213_HotelLobby",
]


def patch_map_groups():
    path = MAPS / "map_groups.json"
    groups = json.loads(path.read_text(encoding="utf-8"))
    towns = groups["gMapGroup_TownsAndRoutes"]
    if "VeilstoneCity" in towns:
        idx = towns.index("VeilstoneCity") + 1
    else:
        idx = len(towns)
    for name in M20_OUTDOOR:
        if name in towns:
            continue
        towns.insert(idx, name)
        idx += 1
    groups["gMapGroup_IndoorM20"] = M20_INDOOR
    order = groups["group_order"]
    if "gMapGroup_IndoorM20" not in order:
        anchor = "gMapGroup_IndoorVeilstone"
        order.insert(order.index(anchor) + 1 if anchor in order else len(order), "gMapGroup_IndoorM20")
    path.write_text(json.dumps(groups, indent=2) + "\n", encoding="utf-8")
    print("patched map_groups.json")


# --------------------------------------------------------------------------- Patches: region map sections
FLY_TOWNS = [
    ("MAPSEC_PASTORIA_CITY", "MAP_PASTORIA_CITY", "HEAL_LOCATION_PASTORIA_CITY", "FLAG_VISITED_PASTORIA_CITY", 26),
]

NEW_MAPSECS = [
    ("MAPSEC_ROUTE_214", "ROUTE 214"),
    ("MAPSEC_VALOR_LAKEFRONT", "VALOR LAKEFRONT"),
    ("MAPSEC_ROUTE_213", "ROUTE 213"),
    ("MAPSEC_PASTORIA_CITY", "PASTORIA CITY"),
    ("MAPSEC_PASTORIA_GYM", "PASTORIA GYM"),
    ("MAPSEC_GREAT_MARSH_GATE", "GREAT MARSH GATE"),
]
LAST_SINNOH_MAPSEC = "MAPSEC_GREAT_MARSH_GATE"


def patch_region_mapsecs():
    path = REPO / "src" / "data" / "region_map" / "region_map_sections.json"
    text = path.read_text(encoding="utf-8")

    missing = [(i, n) for i, n in NEW_MAPSECS if f'"id": "{i}"' not in text]
    if missing:
        tail = '''{
      "id": "MAPSEC_GALACTIC_WAREHOUSE",
      "name": "GALACTIC WAREHOUSE"
    }
  ]
}'''
        if tail not in text:
            raise SystemExit("region_map_sections.json: MAPSEC_GALACTIC_WAREHOUSE tail not found")
        extra = "".join(
            ',\n    {\n      "id": "%s",\n      "name": "%s"\n    }' % (i, n) for i, n in missing
        )
        text = text.replace(
            tail,
            '{\n      "id": "MAPSEC_GALACTIC_WAREHOUSE",\n      "name": "GALACTIC WAREHOUSE"\n    }' + extra + "\n  ]\n}",
        )
        print("patched region_map_sections.json (new sections)")
    else:
        print("region_map_sections already has M20 sections")

    for mapsec, _map, _heal, _flag, x in FLY_TOWNS:
        if re.search(r'"id": "%s",\n\s+"name": "[^"]*",\n\s+"x":' % mapsec, text):
            continue
        pat = re.compile(r'("id": "%s",\n\s+"name": "[^"]*")(\n(\s+)\})' % mapsec)
        m = pat.search(text)
        if not m:
            raise SystemExit(f"region_map_sections.json: {mapsec} block not found")
        ind = m.group(3) + "  "
        coords = f',\n{ind}"x": {x},\n{ind}"y": 0,\n{ind}"width": 1,\n{ind}"height": 1'
        text = text[: m.end(1)] + coords + text[m.end(1):]
        print(f"  placed {mapsec} at ({x}, 0)")
    path.write_text(text, encoding="utf-8")


def patch_regions_h():
    path = REPO / "include" / "regions.h"
    text = path.read_text(encoding="utf-8")
    if f"sectionId <= {LAST_SINNOH_MAPSEC};" in text:
        print("regions.h already extended")
        return
    new = re.sub(r"sectionId <= MAPSEC_\w+;", f"sectionId <= {LAST_SINNOH_MAPSEC};", text, count=1)
    if new == text:
        raise SystemExit("regions.h: IsSinnohMapSec bound not found")
    path.write_text(new, encoding="utf-8")
    print("patched regions.h")


def patch_map_name_popup():
    path = REPO / "src" / "map_name_popup.c"
    text = path.read_text(encoding="utf-8")
    if "MAPSEC_PASTORIA_CITY - KANTO_MAPSEC_COUNT" in text:
        print("map_name_popup already has M20")
        return
    for theme in ("MAPPOPUP_THEME_WOOD", "MAPPOPUP_THEME_BW_DEFAULT"):
        anchor = f"[MAPSEC_GALACTIC_WAREHOUSE - KANTO_MAPSEC_COUNT] = {theme},"
        if text.count(anchor) != 1:
            raise SystemExit(f"map_name_popup.c: anchor for {theme} not unique ({text.count(anchor)})")
        extra = "".join(f"\n    [{i} - KANTO_MAPSEC_COUNT] = {theme}," for i, _ in NEW_MAPSECS)
        text = text.replace(anchor, anchor + extra)
    path.write_text(text, encoding="utf-8")
    print("patched map_name_popup.c")


def patch_heal_locations():
    path = REPO / "src" / "data" / "heal_locations.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    locs = data["heal_locations"] if isinstance(data, dict) else data
    if any(L.get("id") == "HEAL_LOCATION_PASTORIA_CITY" for L in locs):
        print("heal_locations already has Pastoria")
        return
    locs.append({
        "id": "HEAL_LOCATION_PASTORIA_CITY",
        "map": "MAP_PASTORIA_CITY",
        "x": 24,
        "y": 16,
        "respawn_map": "MAP_PASTORIA_CITY_POKEMON_CENTER_1F",
        "respawn_npc": "LOCALID_PASTORIA_NURSE",
    })
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("patched heal_locations.json")


# --------------------------------------------------------------------------- Patches: flags / vars / new game
M20_FLAGS = [
    (0x2A5, "FLAG_RECEIVED_PASTORIA_GYM_TM", "Sinnoh M20"),
    (0x2A6, "FLAG_HIDE_PASTORIA_BARRY", "Sinnoh M20; set after rival battle"),
    (0x2A7, "FLAG_HIDE_PASTORIA_GALACTIC_GRUNT", "Sinnoh M20; cleared after Fen Badge"),
    (0x2A8, "FLAG_HIDE_PASTORIA_WAKE_CAMEO", "Sinnoh M20; cleared after Fen Badge"),
    (0x2A9, "FLAG_PASTORIA_GALACTIC_CHASE", "Sinnoh M20; set when grunt flees"),
    (0x2AA, "FLAG_VISITED_PASTORIA_CITY", "Sinnoh M20; Fly"),
    (0x2AB, "FLAG_GOT_PASTORIA_HM_DEFOG", "Sinnoh M20; reserved for Defog NPC"),
]


def patch_flags_vars():
    flags = REPO / "include" / "constants" / "flags.h"
    ft = flags.read_text(encoding="utf-8")
    changed = False
    for value, name, note in M20_FLAGS:
        if re.search(rf"^#define {name}\b", ft, re.M):
            continue
        old = f"#define FLAG_UNUSED_0x{value:X}  0x{value:X} // Unused Flag\n"
        if old not in ft:
            raise SystemExit(f"flags.h: expected placeholder for 0x{value:X} not found")
        ft = ft.replace(old, f"#define {name}  0x{value:X} // {note}\n")
        changed = True
    if changed:
        flags.write_text(ft, encoding="utf-8")
        print("patched flags.h")
    else:
        print("flags.h already has M20")

    vars_path = REPO / "include" / "constants" / "vars.h"
    vt = vars_path.read_text(encoding="utf-8")
    if "VAR_PASTORIA_CITY_STATE" not in vt:
        old = "#define VAR_UNUSED_0x40FC                                0x40FC // Unused Var\n"
        if old not in vt:
            raise SystemExit("vars.h: VAR_UNUSED_0x40FC placeholder not found")
        vt = vt.replace(
            old,
            "#define VAR_PASTORIA_CITY_STATE                          0x40FC // Sinnoh M20: 0 Barry, 1 gym open, 2 chase ready, 3 chase done\n",
        )
        vars_path.write_text(vt, encoding="utf-8")
        print("patched vars.h")
    else:
        print("vars.h already has VAR_PASTORIA_CITY_STATE")

    ng = REPO / "data" / "scripts" / "new_game.inc"
    nt = ng.read_text(encoding="utf-8")
    if "FLAG_HIDE_PASTORIA_GALACTIC_GRUNT" not in nt:
        anchor = "\tsetflag FLAG_HIDE_VEILSTONE_COUNTERPART\n"
        if anchor not in nt:
            raise SystemExit("new_game.inc: FLAG_HIDE_VEILSTONE_COUNTERPART anchor not found")
        nt = nt.replace(
            anchor,
            anchor
            + "\tsetflag FLAG_HIDE_PASTORIA_GALACTIC_GRUNT\n"
            + "\tsetflag FLAG_HIDE_PASTORIA_WAKE_CAMEO\n",
            1,
        )
        ng.write_text(nt, encoding="utf-8")
        print("patched new_game.inc")
    else:
        print("new_game.inc already hides Pastoria cameos")


# --------------------------------------------------------------------------- Patches: trainers
M20_TRAINERS = [
    ("TRAINER_KAREN_5", "TRAINER_LEADER_CRASHER_WAKE", "WAKE", "Leader", "Sailor", "Male", "Male", [
        ("Gyarados (M)", 33, ["Bite", "Twister", "Aqua Tail", "Ice Fang"]),
        ("Quagsire (M)", 34, ["Mud Shot", "Water Pulse", "Yawn", "Slam"]),
        ("Floatzel (M) @ Sitrus Berry", 37, ["Aqua Jet", "Pursuit", "Swift", "Brine"]),
    ]),
    ("TRAINER_ANNA_AND_MEG_2", "TRAINER_BARRY_4_CHIMCHAR", "BARRY", "Rival", "Youngster", "Male", "Male", [
        ("Staravia (M)", 26, ["Quick Attack", "Wing Attack", "Double Team", "Endeavor"]),
        ("Buizel (M)", 25, ["Aqua Jet", "Pursuit", "Swift", "Growl"]),
        ("Roselia (F)", 25, ["Mega Drain", "Stun Spore", "Magical Leaf", "Growth"]),
        ("Monferno (M)", 28, ["Mach Punch", "Flame Wheel", "Fury Swipes", "Torment"]),
    ]),
    ("TRAINER_ANNA_AND_MEG_3", "TRAINER_BARRY_4_PIPLUP", "BARRY", "Rival", "Youngster", "Male", "Male", [
        ("Staravia (M)", 26, ["Quick Attack", "Wing Attack", "Double Team", "Endeavor"]),
        ("Ponyta (M)", 25, ["Ember", "Stomp", "Tail Whip", "Growl"]),
        ("Roselia (F)", 25, ["Mega Drain", "Stun Spore", "Magical Leaf", "Growth"]),
        ("Prinplup (M)", 28, ["Bubble Beam", "Peck", "Metal Claw", "Growl"]),
    ]),
    ("TRAINER_ANNA_AND_MEG_4", "TRAINER_BARRY_4_TURTWIG", "BARRY", "Rival", "Youngster", "Male", "Male", [
        ("Staravia (M)", 26, ["Quick Attack", "Wing Attack", "Double Team", "Endeavor"]),
        ("Buizel (M)", 25, ["Aqua Jet", "Pursuit", "Swift", "Growl"]),
        ("Ponyta (M)", 25, ["Ember", "Stomp", "Tail Whip", "Growl"]),
        ("Grotle (M)", 28, ["Razor Leaf", "Bite", "Curse", "Absorb"]),
    ]),
    ("TRAINER_ANNA_AND_MEG_5", "TRAINER_PSYCHIC_MITCHELL_R214", "MITCHELL", "Psychic", "Psychic M", "Male", "Male", [
        ("Kadabra", 22, ["Confusion", "Disable", "Psybeam", "Reflect"]),
        ("Kadabra", 24, ["Confusion", "Psybeam", "Disable", "Recover"]),
    ]),
    ("TRAINER_MIGUEL_2", "TRAINER_PSYCHIC_ABIGAIL_R214", "ABIGAIL", "Psychic", "Psychic F", "Female", "Female", [
        ("Abra", 20, ["Teleport"]),
        ("Kadabra", 24, ["Confusion", "Psybeam", "Disable", "Flash"]),
    ]),
    ("TRAINER_MIGUEL_3", "TRAINER_COLLECTOR_DOUGLAS_R214", "DOUGLAS", "Collector", "Collector", "Male", "Suspicious", [
        ("Duskull", 22, ["Astonish", "Disable", "Pursuit", "Shadow Sneak"]),
        ("Haunter", 24, ["Night Shade", "Confuse Ray", "Curse", "Mean Look"]),
    ]),
    ("TRAINER_MIGUEL_4", "TRAINER_COLLECTOR_BRADY_R214", "BRADY", "Collector", "Collector", "Male", "Suspicious", [
        ("Duskull", 23, ["Astonish", "Pursuit", "Disable", "Shadow Sneak"]),
        ("Gastly", 23, ["Lick", "Confuse Ray", "Mean Look", "Curse"]),
    ]),
    ("TRAINER_MIGUEL_5", "TRAINER_COLLECTOR_JAMAL_R214", "JAMAL", "Collector", "Collector", "Male", "Suspicious", [
        ("Gastly", 22, ["Lick", "Confuse Ray", "Mean Look", "Curse"]),
        ("Duskull", 24, ["Astonish", "Pursuit", "Will O Wisp", "Shadow Sneak"]),
    ]),
    ("TRAINER_ISABEL_2", "TRAINER_RUIN_MANIAC_BRYAN_R214", "BRYAN", "Ruin Maniac", "Ruin Maniac", "Male", "Hiker", [
        ("Geodude", 22, ["Rock Throw", "Magnitude", "Defense Curl", "Mud Sport"]),
        ("Bronzor", 24, ["Confusion", "Confuse Ray", "Extrasensory", "Iron Defense"]),
    ]),
    ("TRAINER_ISABEL_3", "TRAINER_RUIN_MANIAC_RONALD_R214", "RONALD", "Ruin Maniac", "Ruin Maniac", "Male", "Hiker", [
        ("Geodude", 22, ["Rock Throw", "Magnitude", "Rollout", "Mud Sport"]),
        ("Geodude", 22, ["Rock Throw", "Magnitude", "Defense Curl", "Mud Sport"]),
        ("Bronzor", 24, ["Confusion", "Confuse Ray", "Extrasensory", "Iron Defense"]),
    ]),
    ("TRAINER_ISABEL_4", "TRAINER_BEAUTY_DEVON_R214", "DEVON", "Beauty", "Beauty", "Female", "Female", [
        ("Roselia", 23, ["Mega Drain", "Stun Spore", "Magical Leaf", "Growth"]),
        ("Beautifly", 24, ["Gust", "Mega Drain", "Stun Spore", "Morning Sun"]),
    ]),
    ("TRAINER_ISABEL_5", "TRAINER_GENTLEMAN_CARLOS_R214", "CARLOS", "Gentleman", "Gentleman", "Male", "Male", [
        ("Goldeen", 24, ["Horn Attack", "Water Pulse", "Peck", "Supersonic"]),
        ("Goldeen", 26, ["Water Pulse", "Horn Attack", "Aqua Tail", "Flail"]),
    ]),
    ("TRAINER_SHELBY_3", "TRAINER_TUBER_JARED_R213", "JARED", "Tuber M", "Tuber M", "Male", "Male", [
        ("Shellos", 23, ["Mud Bomb", "Water Pulse", "Mud Sport", "Harden"]),
        ("Shellos", 25, ["Mud Bomb", "Water Pulse", "Hidden Power", "Harden"]),
    ]),
    ("TRAINER_SHELBY_4", "TRAINER_TUBER_CHELSEA_R213", "CHELSEA", "Tuber F", "Tuber F", "Female", "Female", [
        ("Shellos", 24, ["Mud Bomb", "Water Pulse", "Mud Sport", "Harden"]),
        ("Buizel", 26, ["Aqua Jet", "Pursuit", "Swift", "Quick Attack"]),
    ]),
    ("TRAINER_SHELBY_5", "TRAINER_SWIMMER_SHELTON_R213", "SHELTON", "Swimmer M", "Swimmer M", "Male", "Swimmer", [
        ("Tentacool", 24, ["Bubble Beam", "Acid", "Wrap", "Supersonic"]),
        ("Tentacruel", 26, ["Bubble Beam", "Acid", "Wrap", "Barrier"]),
    ]),
    ("TRAINER_CALVIN_2", "TRAINER_SWIMMER_EVAN_R213", "EVAN", "Swimmer M", "Swimmer M", "Male", "Swimmer", [
        ("Goldeen", 24, ["Horn Attack", "Water Pulse", "Peck", "Supersonic"]),
        ("Golduck", 26, ["Water Pulse", "Confusion", "Fury Swipes", "Disable"]),
    ]),
    ("TRAINER_CALVIN_3", "TRAINER_SWIMMER_MARY_R213", "MARY", "Swimmer F", "Swimmer F", "Female", "Swimmer", [
        ("Wingull", 23, ["Wing Attack", "Water Gun", "Supersonic", "Quick Attack"]),
        ("Pelipper", 26, ["Wing Attack", "Water Pulse", "Supersonic", "Protect"]),
    ]),
    ("TRAINER_CALVIN_4", "TRAINER_SWIMMER_HALEY_R213", "HALEY", "Swimmer F", "Swimmer F", "Female", "Swimmer", [
        ("Psyduck", 23, ["Water Gun", "Confusion", "Disable", "Scratch"]),
        ("Psyduck", 25, ["Water Pulse", "Confusion", "Disable", "Fury Swipes"]),
        ("Psyduck", 27, ["Water Pulse", "Confusion", "Disable", "Screech"]),
    ]),
    ("TRAINER_CALVIN_5", "TRAINER_BEAUTY_CYNDY_R213", "CYNDY", "Beauty", "Beauty", "Female", "Female", [
        ("Glameow", 26, ["Fake Out", "Fury Swipes", "Hypnosis", "Feint Attack"]),
    ]),
    ("TRAINER_ELLIOT_2", "TRAINER_FISHERMAN_KENNETH_R213", "KENNETH", "Fisherman", "Fisherman", "Male", "Male", [
        ("Remoraid", 23, ["Water Gun", "Lock-On", "Psybeam", "Aurora Beam"]),
        ("Remoraid", 25, ["Water Gun", "Lock-On", "Bubble Beam", "Aurora Beam"]),
        ("Gyarados", 27, ["Bite", "Twister", "Aqua Tail", "Scary Face"]),
        ("Gyarados", 27, ["Bite", "Twister", "Ice Fang", "Thrash"]),
    ]),
    ("TRAINER_ELLIOT_3", "TRAINER_SAILOR_PAUL_R213", "PAUL", "Sailor", "Sailor", "Male", "Male", [
        ("Tentacool", 26, ["Bubble Beam", "Acid", "Wrap", "Barrier"]),
        ("Pelipper", 28, ["Wing Attack", "Water Pulse", "Supersonic", "Protect"]),
    ]),
    ("TRAINER_ELLIOT_4", "TRAINER_TUBER_JACKY_PASTORIA", "JACKY", "Tuber M", "Tuber M", "Male", "Male", [
        ("Shellos", 28, ["Mud Bomb", "Water Pulse", "Body Slam", "Hidden Power"]),
        ("Buizel", 30, ["Aqua Jet", "Pursuit", "Swift", "Sonic Boom"]),
    ]),
    ("TRAINER_ELLIOT_5", "TRAINER_TUBER_CAITLYN_PASTORIA", "CAITLYN", "Tuber F", "Tuber F", "Female", "Female", [
        ("Buizel", 29, ["Aqua Jet", "Pursuit", "Swift", "Quick Attack"]),
        ("Floatzel", 31, ["Aqua Jet", "Pursuit", "Swift", "Water Pulse"]),
    ]),
    ("TRAINER_DIANA_2", "TRAINER_SAILOR_DAMIAN_PASTORIA", "DAMIAN", "Sailor", "Sailor", "Male", "Male", [
        ("Wingull", 28, ["Wing Attack", "Water Gun", "Supersonic", "Quick Attack"]),
        ("Pelipper", 30, ["Wing Attack", "Water Pulse", "Supersonic", "Protect"]),
    ]),
    ("TRAINER_DIANA_3", "TRAINER_SAILOR_SAMSON_PASTORIA", "SAMSON", "Sailor", "Sailor", "Male", "Male", [
        ("Wingull", 28, ["Wing Attack", "Water Gun", "Supersonic", "Quick Attack"]),
        ("Wingull", 30, ["Wing Attack", "Water Pulse", "Supersonic", "Quick Attack"]),
        ("Pelipper", 32, ["Wing Attack", "Water Pulse", "Supersonic", "Protect"]),
    ]),
    ("TRAINER_DIANA_4", "TRAINER_FISHERMAN_ERICK_PASTORIA", "ERICK", "Fisherman", "Fisherman", "Male", "Male", [
        ("Magikarp", 26, ["Splash", "Tackle"]),
        ("Gyarados", 30, ["Bite", "Twister", "Aqua Tail", "Ice Fang"]),
        ("Gyarados", 32, ["Bite", "Twister", "Aqua Tail", "Scary Face"]),
    ]),
    ("TRAINER_DIANA_5", "TRAINER_FISHERMAN_WALTER_PASTORIA", "WALTER", "Fisherman", "Fisherman", "Male", "Male", [
        ("Magikarp", 27, ["Splash", "Tackle"]),
        ("Magikarp", 27, ["Splash", "Tackle"]),
        ("Magikarp", 27, ["Splash", "Tackle"]),
        ("Magikarp", 27, ["Splash", "Tackle"]),
        ("Magikarp", 27, ["Splash", "Tackle"]),
        ("Gyarados", 32, ["Bite", "Twister", "Aqua Tail", "Ice Fang"]),
    ]),
]


def _party_block(header, name, cls, pic, gender, music, mons):
    lines = [
        f"=== {header} ===",
        f"Name: {name}",
        f"Class: {cls}",
        f"Pic: {pic}",
        f"Gender: {gender}",
        f"Music: {music}",
        "Double Battle: No",
        "AI: Basic Trainer",
        "",
    ]
    for species, level, moves in mons:
        lines.append(species)
        lines.append(f"Level: {level}")
        lines.append("IVs: 0 HP / 0 Atk / 0 Def / 0 SpA / 0 SpD / 0 Spe")
        lines.extend(f"- {mv}" for mv in moves)
        lines.append("")
    return "\n".join(lines) + "\n"


def patch_opponents():
    path = REPO / "include" / "constants" / "opponents.h"
    text = path.read_text(encoding="utf-8")
    changed = False
    for old, new, *_ in M20_TRAINERS:
        if re.search(rf"^#define {new}\b", text, re.M):
            continue
        m = re.search(rf"^#define {old}(\s+)(\d+)[ \t]*\n", text, re.M)
        if not m:
            raise SystemExit(f"opponents.h: {old} not found")
        num = m.group(2)
        repl = (
            f"#define {new}                       {num} // Sinnoh M20: was {old}\n"
            f"#define {old} {new}\n"
        )
        text = text[: m.start()] + repl + text[m.end():]
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
        print("patched opponents.h")
    else:
        print("opponents.h already has M20")


def patch_trainers_party():
    path = REPO / "src" / "data" / "trainers.party"
    text = path.read_text(encoding="utf-8")
    changed = False
    for old, new, name, cls, pic, gender, music, mons in M20_TRAINERS:
        if f"=== {new} ===" in text:
            continue
        pattern = rf"=== {old} ===.*?(?=\n=== |\Z)"
        m = re.search(pattern, text, flags=re.S)
        if not m:
            raise SystemExit(f"trainers.party: {old} not found")
        block = _party_block(new, name, cls, pic, gender, music, mons)
        text = text[: m.start()] + block + text[m.end():]
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
        print("patched trainers.party")
    else:
        print("trainers.party already has M20")


# --------------------------------------------------------------------------- Patches: TM Brine
def patch_tms_hms():
    path = REPO / "include" / "constants" / "tms_hms.h"
    text = path.read_text(encoding="utf-8")
    if "F(BRINE)" in text:
        print("tms_hms.h already has BRINE")
        return
    if "    F(DRAIN_PUNCH)\n" not in text:
        raise SystemExit("tms_hms.h: F(DRAIN_PUNCH) anchor not found")
    text = text.replace("    F(DRAIN_PUNCH)\n", "    F(DRAIN_PUNCH) \\\n    F(BRINE)\n", 1)
    path.write_text(text, encoding="utf-8")
    print("patched tms_hms.h")


def patch_items_brine():
    path = REPO / "src" / "data" / "items.h"
    text = path.read_text(encoding="utf-8")
    if "[ITEM_TM_BRINE]" in text:
        print("items.h already has ITEM_TM_BRINE")
        return
    new = '''    [ITEM_TM_BRINE] =
    {
        .name = ITEM_NAME("TM55"),
        .price = 3000,
        .description = COMPOUND_STRING(
            "A Water move that\\n"
            "hits harder when\\n"
            "the foe has low HP."),
        .importance = I_REUSABLE_TMS,
        .pocket = POCKET_TM_HM,
        .type = ITEM_USE_PARTY_MENU,
        .fieldUseFunc = ItemUseOutOfBattle_TMHM,
    },'''
    # BRINE is the 53rd FOREACH_TM entry (after DRAIN_PUNCH=52)
    pattern = re.compile(r"    \[ITEM_TM53\] =\n    \{\n(?:        .*\n)*?    \},")
    m = pattern.search(text)
    if not m:
        # fall back to TM55 as requested if TM53 already claimed
        pattern = re.compile(r"    \[ITEM_TM55\] =\n    \{\n(?:        .*\n)*?    \},")
        m = pattern.search(text)
        if not m:
            raise SystemExit("items.h: [ITEM_TM53]/[ITEM_TM55] placeholder not found")
    text = text[: m.start()] + new + text[m.end():]
    path.write_text(text, encoding="utf-8")
    print("patched items.h for BRINE TM")


# --------------------------------------------------------------------------- Patches: Fly
def patch_region_map_fly():
    path = REPO / "src" / "region_map.c"
    text = path.read_text(encoding="utf-8")
    orig = text

    if "[MAPSEC_PASTORIA_CITY] = {" not in text:
        entries = "".join(
            f"    [{sec}] = {{MAP_GROUP({mp}), MAP_NUM({mp}), {heal}}},\n"
            for sec, mp, heal, _flag, _x in FLY_TOWNS
        )
        # insert after Veilstone entry
        anchor = "    [MAPSEC_VEILSTONE_CITY] = {MAP_GROUP(MAP_VEILSTONE_CITY), MAP_NUM(MAP_VEILSTONE_CITY), HEAL_LOCATION_VEILSTONE_CITY},\n"
        if anchor not in text:
            raise SystemExit("region_map.c: Veilstone heal location anchor not found")
        text = text.replace(anchor, anchor + entries, 1)

    if "case MAPSEC_PASTORIA_CITY:" not in text:
        cases = "".join(
            f"    case {sec}:\n"
            f"        return FlagGet({flag}) ? MAPSECTYPE_CITY_CANFLY : MAPSECTYPE_CITY_CANTFLY;\n"
            for sec, _mp, _heal, flag, _x in FLY_TOWNS
        )
        anchor = "    case MAPSEC_VEILSTONE_CITY:\n        return FlagGet(FLAG_VISITED_VEILSTONE_CITY) ? MAPSECTYPE_CITY_CANFLY : MAPSECTYPE_CITY_CANTFLY;\n"
        if anchor not in text:
            raise SystemExit("region_map.c: Veilstone fly case anchor not found")
        text = text.replace(anchor, anchor + cases, 1)

    if text != orig:
        path.write_text(text, encoding="utf-8")
        print("patched region_map.c (Pastoria fly)")
    else:
        print("region_map.c already has Pastoria fly")

    layout = REPO / "src" / "data" / "region_map" / "region_map_layout.h"
    lt = layout.read_text(encoding="utf-8")
    lines = lt.split("\n")
    row_idx = next(i for i, ln in enumerate(lines) if ln.lstrip().startswith("{MAPSEC_"))
    tokens = re.findall(r"MAPSEC_\w+", lines[row_idx])
    dirty = False
    for sec, _mp, _heal, _flag, x in FLY_TOWNS:
        if tokens[x] == sec:
            continue
        if tokens[x] != "MAPSEC_NONE":
            raise SystemExit(f"region_map_layout.h: cell ({x}, 0) already used by {tokens[x]}")
        tokens[x] = sec
        dirty = True
    if dirty:
        lines[row_idx] = "    {" + ", ".join(tokens) + "},"
        layout.write_text("\n".join(lines), encoding="utf-8")
        print("patched region_map_layout.h (Pastoria fly spot)")
    else:
        print("region_map_layout.h already has Pastoria fly spot")


# --------------------------------------------------------------------------- Patches: wild encounters
def _pad12(mons):
    out = list(mons)
    i = 0
    while len(out) < 12:
        out.append(mons[i % len(mons)])
        i += 1
    return out[:12]


def patch_wild_encounters():
    path = REPO / "src" / "data" / "wild_encounters.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    enc = data["wild_encounter_groups"][0]["encounters"]
    existing = {e.get("base_label") for e in enc}
    additions = []
    r214 = _pad12([
        ("SPECIES_PONYTA", 20), ("SPECIES_GEODUDE", 20), ("SPECIES_GRAVELER", 22),
        ("SPECIES_STUNKY", 21), ("SPECIES_RHYHORN", 22), ("SPECIES_HOUNDOUR", 21),
        ("SPECIES_PONYTA", 22), ("SPECIES_GEODUDE", 21), ("SPECIES_STUNKY", 23),
        ("SPECIES_RHYHORN", 24), ("SPECIES_HOUNDOUR", 22), ("SPECIES_GRAVELER", 24),
    ])
    r213 = _pad12([
        ("SPECIES_BUIZEL", 20), ("SPECIES_SHELLOS", 20), ("SPECIES_FLOATZEL", 24),
        ("SPECIES_WINGULL", 21), ("SPECIES_CHATOT", 22), ("SPECIES_BUIZEL", 22),
        ("SPECIES_SHELLOS", 21), ("SPECIES_WINGULL", 23), ("SPECIES_CHATOT", 24),
        ("SPECIES_BUIZEL", 23), ("SPECIES_SHELLOS", 22), ("SPECIES_FLOATZEL", 24),
    ])
    if "gRoute214" not in existing:
        additions.append(land_entry("MAP_ROUTE214", "gRoute214", r214))
    if "gRoute213" not in existing:
        additions.append(land_entry("MAP_ROUTE213", "gRoute213", r213))
    if not additions:
        print("wild_encounters already has M20")
        return
    enc.extend(additions)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("patched wild_encounters.json")


# --------------------------------------------------------------------------- Patches: event_scripts.s
def patch_event_scripts():
    path = REPO / "data" / "event_scripts.s"
    text = path.read_text(encoding="utf-8")
    marker = '\t.include "data/maps/VeilstoneCity_Route214Gate/scripts.inc"\n'
    names = M20_OUTDOOR + M20_INDOOR
    block = "".join(f'\t.include "data/maps/{n}/scripts.inc"\n' for n in names)
    if 'data/maps/PastoriaCity/scripts.inc' in text:
        print("event_scripts.s already has M20 includes")
        return
    if marker not in text:
        raise SystemExit("event_scripts.s: VeilstoneCity_Route214Gate include not found")
    path.write_text(text.replace(marker, marker + block, 1), encoding="utf-8")
    print("patched event_scripts.s")


# --------------------------------------------------------------------------- main
def main():
    scaffold_route214()
    scaffold_valor_lakefront()
    scaffold_route213()
    scaffold_pastoria_city()
    scaffold_center()
    scaffold_mart()
    scaffold_gym()
    scaffold_marsh_gate()
    scaffold_pastoria_houses()
    scaffold_valor_interiors()
    scaffold_route213_interiors()
    patch_route214_gate()
    patch_map_groups()
    patch_region_mapsecs()
    patch_regions_h()
    patch_map_name_popup()
    patch_heal_locations()
    patch_flags_vars()
    patch_opponents()
    patch_trainers_party()
    patch_tms_hms()
    patch_items_brine()
    patch_region_map_fly()
    patch_wild_encounters()
    patch_event_scripts()
    print("M20 scaffold complete.")


if __name__ == "__main__":
    main()
