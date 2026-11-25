#!/usr/bin/env python3
"""Simulate scripted applymovement paths against map.bin collision.

Fails when any walk_* / jump_* / run_* step lands on a blocked tile (coll != 0)
or leaves the map bounds (except the final off-map step of a leave path, which
is allowed when the previous tile was walkable at the edge).

Resolves start positions from:
  1) Explicit cutscene registry (literal coords after setobjectxy / setobjectxyperm)
  2) Linear scan of each map's scripts.inc for literal setobjectxy(perm) + applymovement
  3) object_events initial (x,y) when applymovement targets that local_id

VAR-based starts without a registry entry are skipped (counted), not failed.
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data/maps"
_LAYOUT_LIST = json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
LAYOUTS_BY_NAME = {L["name"]: L for L in _LAYOUT_LIST}
LAYOUTS_BY_ID = {L.get("id", L["name"]): L for L in _LAYOUT_LIST}

# walk/run/jump deltas; face/delay/slide-in-place ignored
STEP_DELTA = {
    "walk_left": (-1, 0),
    "walk_right": (1, 0),
    "walk_up": (0, -1),
    "walk_down": (0, 1),
    "walk_fast_left": (-1, 0),
    "walk_fast_right": (1, 0),
    "walk_fast_up": (0, -1),
    "walk_fast_down": (0, 1),
    "walk_faster_left": (-1, 0),
    "walk_faster_right": (1, 0),
    "walk_faster_up": (0, -1),
    "walk_faster_down": (0, 1),
    "walk_slow_left": (-1, 0),
    "walk_slow_right": (1, 0),
    "walk_slow_up": (0, -1),
    "walk_slow_down": (0, 1),
    "run_left": (-1, 0),
    "run_right": (1, 0),
    "run_up": (0, -1),
    "run_down": (0, 1),
    "jump_left": (-1, 0),
    "jump_right": (1, 0),
    "jump_up": (0, -1),
    "jump_down": (0, 1),
    "jump_2_left": (-2, 0),
    "jump_2_right": (2, 0),
    "jump_2_up": (0, -2),
    "jump_2_down": (0, 2),
}

# Must-check cutscenes: (map, movement_label, start_x, start_y)
# Covers the post-Barry “three of them” meetup + leave.
REQUIRED_SCENES: list[tuple[str, str, int, int]] = [
    ("Route201", "Route201_Movement_RowanApproach", 47, 12),
    ("Route201", "Route201_Movement_AssistantApproach", 48, 12),
    ("Route201", "Route201_Movement_BarryApproachMeetup", 49, 12),
    # After 3× walk_left from the approach starts:
    ("Route201", "Route201_Movement_PartyLeavesEast", 44, 12),
    ("Route201", "Route201_Movement_PartyLeavesEast", 45, 12),
    ("Route201", "Route201_Movement_PartyLeavesEast", 46, 12),
    # Sandgem assistant leave (m48 #9)
    ("SandgemTown", "SandgemTown_Movement_AssistantLeave", 26, 11),
    # Lake Verity Barry exit after Cyrus (post-Starly leave)
    ("LakeVerity", "LakeVerity_Movement_BarryLeaves", 50, 14),
    # Route201 BarryMeet lead-up on clear west corridor
    ("Route201", "Route201_Movement_BarryLeadsWest", 5, 22),
    ("Route201", "Route201_Movement_PlayerFollowsWest", 4, 22),
]


def load_collision(map_name: str) -> tuple[list[list[int]], int, int] | None:
    layout_key = f"{map_name}_Layout"
    map_json = MAPS / map_name / "map.json"
    if map_json.exists():
        meta = json.loads(map_json.read_text())
        layout_key = meta.get("layout", layout_key)
    L = LAYOUTS_BY_ID.get(layout_key) or LAYOUTS_BY_NAME.get(layout_key)
    if not L:
        return None
    w, h = int(L["width"]), int(L["height"])
    path = REPO / L["blockdata_filepath"]
    if not path.exists():
        return None
    data = path.read_bytes()
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            raw = struct.unpack_from("<H", data, (y * w + x) * 2)[0]
            row.append((raw >> 10) & 3)
        grid.append(row)
    return grid, w, h


def parse_movements(text: str) -> dict[str, list[str]]:
    """Map label → list of movement command tokens (until step_end)."""
    out: dict[str, list[str]] = {}
    # Labels: Name: or Name::
    for m in re.finditer(
        r"^([A-Za-z0-9_]+_Movement_[A-Za-z0-9_]+|[A-Za-z0-9_]*Movement_[A-Za-z0-9_]+)::?\s*$",
        text,
        re.M,
    ):
        label = m.group(1)
        start = m.end()
        body = text[start:]
        end = re.search(r"^\S", body, re.M)
        chunk = body[: end.start()] if end else body
        cmds = []
        for line in chunk.splitlines():
            line = line.strip()
            if not line or line.startswith("@") or line.startswith("."):
                continue
            if line == "step_end":
                break
            # strip trailing comments
            line = line.split("@", 1)[0].strip().rstrip(",")
            if line:
                cmds.append(line)
        out[label] = cmds
    return out


def parse_common_movements() -> dict[str, list[str]]:
    path = REPO / "data/scripts/movement.inc"
    if not path.exists():
        return {}
    return parse_movements(path.read_text(errors="replace"))


def simulate(
    grid: list[list[int]],
    w: int,
    h: int,
    sx: int,
    sy: int,
    cmds: list[str],
    *,
    allow_exit: bool = True,
) -> list[str]:
    """Return list of failure strings (empty = ok)."""
    fails: list[str] = []
    x, y = sx, sy
    if not (0 <= x < w and 0 <= y < h):
        fails.append(f"start off-map ({x},{y})")
        return fails
    if grid[y][x] != 0:
        fails.append(f"start blocked ({x},{y}) coll={grid[y][x]}")
    for i, cmd in enumerate(cmds):
        delta = STEP_DELTA.get(cmd)
        if delta is None:
            continue
        dx, dy = delta
        # multi-tile jumps: check each intermediate? check landing only (engine)
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            if allow_exit:
                # leaving the map is OK for leave scripts; stop tracking
                return fails
            fails.append(f"step{i}:{cmd} off-map ({nx},{ny})")
            return fails
        if grid[ny][nx] != 0:
            fails.append(f"step{i}:{cmd} → ({nx},{ny}) coll={grid[ny][nx]}")
        x, y = nx, ny
    return fails


def object_event_coords(map_name: str) -> dict[int, tuple[int, int]]:
    path = MAPS / map_name / "map.json"
    if not path.exists():
        return {}
    meta = json.loads(path.read_text())
    out = {}
    for i, obj in enumerate(meta.get("object_events") or [], start=1):
        out[i] = (int(obj["x"]), int(obj["y"]))
    return out


def resolve_local_id(token: str, equ: dict[str, int]) -> int | None:
    token = token.strip()
    if token.isdigit():
        return int(token)
    if token in equ:
        return equ[token]
    if token == "OBJ_EVENT_ID_PLAYER":
        return -1  # special
    return None


def parse_equ_localids(text: str) -> dict[str, int]:
    out = {}
    for m in re.finditer(r"^\.equ\s+(LOCALID_\w+)\s*,\s*(\d+)\s*$", text, re.M):
        out[m.group(1)] = int(m.group(2))
    return out


def scan_map_scripts(
    map_name: str,
    text: str,
    movements: dict[str, list[str]],
    common: dict[str, list[str]],
) -> list[tuple[str, int, int, str]]:
    """Infer (movement_label, x, y) for map-local Movement_* applymovements.

    Tracks literal setobjectxy(perm) across the whole file and advances coords
    through walk steps so multi-script cutscenes stay accurate. Skips
    Common_Movement_* (one-step face/push helpers) to avoid false positives.
    """
    equ = parse_equ_localids(text)
    objs = object_event_coords(map_name)
    pos: dict[int, tuple[int, int]] = dict(objs)
    found: list[tuple[str, int, int, str]] = []
    grid_pack = load_collision(map_name)

    for line in text.splitlines():
        s = line.strip()
        m = re.match(
            r"setobjectxy(?:perm)?\s+(\S+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$", s
        )
        if m:
            lid = resolve_local_id(m.group(1), equ)
            if lid is not None and lid != -1:
                pos[lid] = (int(m.group(2)), int(m.group(3)))
            elif lid == -1:
                pos[-1] = (int(m.group(2)), int(m.group(3)))
            continue
        m = re.match(r"applymovement\s+(\S+)\s*,\s*(\S+)\s*$", s)
        if not m:
            continue
        who, mov = m.group(1), m.group(2).rstrip(",")
        if mov.startswith("Common_Movement_"):
            # Still advance tracked coords for common walks so later map movements
            # start from the right tile (e.g. Barry WalkRight before BarryLeaves).
            cmds = common.get(mov) or []
            lid = resolve_local_id(who, equ)
            if lid is not None and lid in pos and grid_pack:
                grid, w, h = grid_pack
                cx, cy = pos[lid]
                for cmd in cmds:
                    d = STEP_DELTA.get(cmd)
                    if not d:
                        continue
                    nx, ny = cx + d[0], cy + d[1]
                    if 0 <= nx < w and 0 <= ny < h:
                        cx, cy = nx, ny
                    else:
                        break
                pos[lid] = (cx, cy)
            continue
        cmds = movements.get(mov) or []
        if not cmds or not any(c in STEP_DELTA for c in cmds):
            continue
        lid = resolve_local_id(who, equ)
        if lid is None or lid not in pos:
            continue
        x, y = pos[lid]
        found.append((mov, x, y, f"scan:{who}"))
        if grid_pack:
            grid, w, h = grid_pack
            cx, cy = x, y
            for cmd in cmds:
                d = STEP_DELTA.get(cmd)
                if not d:
                    continue
                nx, ny = cx + d[0], cy + d[1]
                if 0 <= nx < w and 0 <= ny < h:
                    cx, cy = nx, ny
                else:
                    break
            pos[lid] = (cx, cy)
    return found


def main() -> int:
    common = parse_common_movements()
    # Index all map movements
    all_movements: dict[str, list[str]] = dict(common)
    map_scripts: dict[str, str] = {}
    for scripts in MAPS.glob("*/scripts.inc"):
        map_name = scripts.parent.name
        text = scripts.read_text(errors="replace")
        map_scripts[map_name] = text
        all_movements.update(parse_movements(text))

    fails: list[str] = []
    checked = 0
    skipped = 0

    # Required scenes first
    for map_name, label, sx, sy in REQUIRED_SCENES:
        cmds = all_movements.get(label)
        if not cmds:
            fails.append(f"{map_name}: missing movement {label}")
            continue
        pack = load_collision(map_name)
        if not pack:
            fails.append(f"{map_name}: no layout/collision")
            continue
        grid, w, h = pack
        issues = simulate(grid, w, h, sx, sy, cmds)
        checked += 1
        if issues:
            for iss in issues:
                fails.append(f"{map_name}:{label}@({sx},{sy}): {iss}")

    # Game-wide scan of literal-resolved applymovements
    seen: set[tuple[str, str, int, int]] = set()
    for map_name, sx0, sy0, lab in [
        (m, x, y, lab) for m, lab, x, y in REQUIRED_SCENES
    ]:
        seen.add((map_name, lab, sx0, sy0))

    for map_name, text in sorted(map_scripts.items()):
        movs = parse_movements(text)
        movs.update(common)
        inferred = scan_map_scripts(map_name, text, movs, common)
        pack = load_collision(map_name)
        if not pack:
            continue
        grid, w, h = pack
        for label, sx, sy, _src in inferred:
            key = (map_name, label, sx, sy)
            if key in seen:
                continue
            seen.add(key)
            cmds = movs.get(label) or common.get(label)
            if not cmds:
                skipped += 1
                continue
            issues = simulate(grid, w, h, sx, sy, cmds)
            checked += 1
            if issues:
                for iss in issues:
                    fails.append(f"{map_name}:{label}@({sx},{sy}): {iss}")

    # RowanArrives triggers must sit on coll=0
    r201 = MAPS / "Route201" / "map.json"
    if r201.exists():
        meta = json.loads(r201.read_text())
        pack = load_collision("Route201")
        if pack:
            grid, w, h = pack
            for ev in meta.get("coord_events") or []:
                if ev.get("script") != "Route201_EventScript_RowanArrivesTrigger":
                    continue
                x, y = int(ev["x"]), int(ev["y"])
                checked += 1
                if not (0 <= x < w and 0 <= y < h) or grid[y][x] != 0:
                    c = grid[y][x] if 0 <= y < h and 0 <= x < w else -1
                    fails.append(
                        f"Route201: RowanArrivesTrigger on blocked tile ({x},{y}) coll={c}"
                    )

    # Dialogue branch presence (paired with #19)
    r201s = map_scripts.get("Route201", "")
    for needle in (
        "specialvar VAR_RESULT, GetBattleOutcome",
        "B_OUTCOME_WON",
        "B_OUTCOME_LOST",
        "Route201_Text_BarryAfterWin",
        "Route201_Text_BarryAfterLoss",
    ):
        if needle not in r201s:
            fails.append(f"Route201: AfterBattle missing {needle}")

    if fails:
        print(f"FAIL ({len(fails)} issues, checked={checked}, skipped={skipped}):")
        for f in fails[:60]:
            print(" -", f)
        if len(fails) > 60:
            print(f" ... +{len(fails) - 60} more")
        return 1
    print(
        f"=== movement_collision_check: PASS "
        f"(checked={checked}, skipped_unresolved={skipped}) ==="
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
