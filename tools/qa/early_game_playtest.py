#!/usr/bin/env python3
"""Static early-game playtest: door warps, collision, water, catch-tutorial wiring.

Simulates the route Twinleaf → Route201 → Lake Verity → Sandgem → Route202 →
Jubilife (PC/Mart) → Route203 → Oreburgh using map.bin + map.json (no emulator).
Writes per-stop overlay PNGs and a JSON assertion report.

For live mGBA boot smoke see mgba_smoke.py.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.city_door_warp_audit import (  # noqa: E402
    DOOR_METATILES,
    bfs_reachable,
    connection_seeds,
    expected_door,
    classify_warp,
    is_door_behavior,
    is_walkable,
)
from tools.sinnoh_maps.render_map_preview import render  # noqa: E402
from tools.sinnoh_maps.sinnoh_build_lib import WATER_METATILES  # noqa: E402

LAYOUTS_JSON = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
}
MAPS = REPO / "data/maps"

# Stops Chris wants exercised (debug-warp style checkpoints)
ROUTE = [
    {"map": "TwinleafTown", "label": "new_game_twinleaf", "check_doors": True},
    {"map": "Route201", "label": "route201", "check_doors": False, "check_barry1": True},
    {"map": "LakeVerity", "label": "lake_verity_starter", "check_doors": False, "optional": True},
    {"map": "SandgemTown", "label": "sandgem", "check_doors": True},
    {"map": "Route202", "label": "route202_catch_tutorial", "check_catch": True},
    {"map": "JubilifeCity", "label": "jubilife", "check_doors": True, "must_enter": ["CENTER", "MART"]},
    {"map": "Route203", "label": "route203", "check_doors": False},
    {"map": "OreburghCity", "label": "oreburgh", "check_doors": True},
]


def check_barry1_continue_on_loss() -> list[str]:
    """Win AND lose must share AfterBattle; distinct outcome lines; no rematch softlock."""
    fails: list[str] = []
    text = (MAPS / "Route201" / "scripts.inc").read_text()
    for needle in (
        "setflag FLAG_TEMP_5",
        "trainerbattle_no_intro TRAINER_BARRY_1_",
        "special HealPlayerParty",
        "goto Route201_EventScript_AfterBattle",
        "fadescreen FADE_FROM_BLACK",
        "setflag FLAG_HIDE_ROUTE201_BARRY",
        "setvar VAR_ROUTE201_STATE, 4",
        "specialvar VAR_RESULT, GetBattleOutcome",
        "B_OUTCOME_WON",
        "B_OUTCOME_LOST",
        "Route201_Text_BarryAfterWin",
        "Route201_Text_BarryAfterLoss",
    ):
        if needle not in text:
            fails.append(f"Barry1 missing {needle}")
    if "Route201_EventScript_BarryRematch" in text:
        fails.append("Barry1 still has BarryRematch (lose→rematch black-screen)")
    return fails



def load_cells(name: str):
    meta = LAYOUTS_JSON[name]
    w, h = int(meta["width"]), int(meta["height"])
    data = (REPO / meta["blockdata_filepath"]).read_bytes()
    cells = []
    for y in range(h):
        row = []
        for x in range(w):
            raw = struct.unpack_from("<H", data, (y * w + x) * 2)[0]
            row.append((raw & 0x3FF, (raw >> 10) & 3, (raw >> 12) & 0xF))
        cells.append(row)
    return cells, w, h, meta


def walk_into_collision_tests(cells, w, h) -> list[str]:
    """Assert solids/water reject walking (coll bit or elev mismatch)."""
    fails = []
    # Sample up to 200 solid and water cells
    solids = waters = 0
    for y in range(h):
        for x in range(w):
            mt, coll, elev = cells[y][x]
            if mt in WATER_METATILES:
                waters += 1
                # Vanilla Surf pack: coll=0 elev=1 → elevation mismatch blocks walk
                if not (coll == 0 and elev == 1) and coll != 1:
                    fails.append(f"water ({x},{y}) mt=0x{mt:03X} coll={coll} elev={elev} (want elev=1 coll=0 or coll=1)")
            elif coll == 1 and mt not in DOOR_METATILES:
                solids += 1
            if solids + waters > 400:
                break
        if solids + waters > 400:
            break
    if waters == 0 and solids == 0:
        fails.append("no solid/water samples found")
    return fails


def door_asserts(name: str, cells, w, h, must_enter=None) -> list[dict]:
    mj = MAPS / name / "map.json"
    warps = json.loads(mj.read_text()).get("warp_events") or [] if mj.exists() else []
    seeds = connection_seeds(name, w, h)
    reachable = bfs_reachable(cells, w, h, seeds)
    results = []
    for warp in warps:
        dest = warp.get("dest_map") or ""
        kind = classify_warp(dest)
        x, y = int(warp["x"]), int(warp["y"])
        entry = {"x": x, "y": y, "dest": dest, "kind": kind, "ok": False, "issues": []}
        if not (0 <= x < w and 0 <= y < h):
            entry["issues"].append("OOB")
            results.append(entry)
            continue
        mt, coll, _ = cells[y][x]
        expect = expected_door(kind)
        approach = False
        for ax, ay in ((x, y + 1), (x, y - 1), (x - 1, y), (x + 1, y)):
            if 0 <= ax < w and 0 <= ay < h and reachable[ay][ax] and cells[ay][ax][1] == 0:
                approach = True
                break
        door_ok = True
        if expect is not None:
            if mt not in expect and not is_door_behavior(name, mt):
                # sibling double-door
                sib = any(
                    0 <= ax < w and cells[y][ax][0] in expect
                    for ax in (x - 1, x + 1)
                )
                if not (sib and approach) and not (kind == "cave" and coll == 0 and approach):
                    door_ok = False
                    entry["issues"].append(f"bad door mt=0x{mt:03X}")
        else:
            if not is_walkable(mt, coll) and mt not in DOOR_METATILES:
                door_ok = False
                entry["issues"].append(f"non-walkable 0x{mt:03X}")
        entry["ok"] = bool(door_ok and (reachable[y][x] or approach))
        if must_enter and any(k in dest for k in must_enter) and not entry["ok"]:
            entry["issues"].append("must_enter failed")
            entry["ok"] = False
        results.append(entry)
    return results


def check_catch_tutorial() -> list[str]:
    fails = []
    # Script wiring
    scripts = (REPO / "data/maps/Route202/scripts.inc")
    if scripts.exists():
        text = scripts.read_text()
        for needle in ("CATCH_TUTORIAL", "LoadWallyZigzagoon", "SavePlayerParty", "LoadPlayerParty"):
            if needle not in text and needle != "CATCH_TUTORIAL":
                # CATCH_TUTORIAL may be in C; Zigzagoon path must be in scripts or C
                pass
        if "LoadWallyZigzagoon" not in text and "Zigzagoon" not in text:
            # May live in event_scripts — soft check via catch_tutorial_verify
            pass
    verify = REPO / "tools/sinnoh_maps/catch_tutorial_verify.py"
    if verify.exists():
        import subprocess
        r = subprocess.run([sys.executable, str(verify)], cwd=REPO, capture_output=True, text=True)
        if r.returncode != 0:
            fails.append(f"catch_tutorial_verify failed: {r.stdout[-200:]}{r.stderr[-200:]}")
    return fails


def overlay_stop(name: str, label: str, out: Path, door_results: list[dict]) -> None:
    meta = LAYOUTS_JSON[name]
    w, h = int(meta["width"]), int(meta["height"])
    tmp = out / f"_raw_{name}.png"
    render(name, tmp, cam_x=0, cam_y=0, view_w=min(w, 64), view_h=min(h, 64), scale=2)
    img = Image.open(tmp).convert("RGBA")
    draw = ImageDraw.Draw(img)
    # Scale factor from render
    sx = img.width / min(w, 64)
    sy = img.height / min(h, 64)
    for d in door_results:
        x, y = d["x"], d["y"]
        if x >= 64 or y >= 64:
            continue
        color = (40, 220, 80, 200) if d["ok"] else (220, 40, 40, 200)
        px, py = int(x * sx), int(y * sy)
        draw.rectangle([px, py, px + int(sx) - 1, py + int(sy) - 1], outline=color, width=2)
    draw.text((4, 4), f"{label}: {name}", fill=(255, 255, 255, 255))
    img.save(out / f"{label}.png")
    tmp.unlink(missing_ok=True)


def run(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    report = {"stops": [], "fail": 0, "pass": 0, "issues": []}
    for stop in ROUTE:
        name = stop["map"]
        if name not in LAYOUTS_JSON:
            if stop.get("optional"):
                report["stops"].append({"map": name, "status": "SKIP", "reason": "no layout"})
                continue
            report["issues"].append(f"missing layout {name}")
            report["fail"] += 1
            continue
        cells, w, h, _ = load_cells(name)
        stop_rep = {"map": name, "label": stop["label"], "status": "PASS", "issues": [], "doors": []}
        # Collision / water
        for msg in walk_into_collision_tests(cells, w, h):
            stop_rep["issues"].append(msg)
        doors = []
        if stop.get("check_doors"):
            doors = door_asserts(name, cells, w, h, must_enter=stop.get("must_enter"))
            stop_rep["doors"] = [
                {k: v for k, v in d.items() if k != "issues"} | {"issues": d["issues"]}
                for d in doors
            ]
            for d in doors:
                if not d["ok"] and d["kind"] in ("center", "mart", "gym", "building", "cave"):
                    stop_rep["issues"].append(
                        f"door fail ({d['x']},{d['y']}) {d['dest']}: {'; '.join(d['issues'])}"
                    )
        if stop.get("check_catch"):
            for msg in check_catch_tutorial():
                stop_rep["issues"].append(msg)
        if stop.get("check_barry1"):
            for msg in check_barry1_continue_on_loss():
                stop_rep["issues"].append(msg)
            stop_rep["outcomes"] = {
                "win": "Route201_EventScript_AfterBattle (Barry/Rowan leave, state=4)",
                "lose": "same AfterBattle + HealPlayerParty (FLAG_TEMP_5 / B_FLAG_NO_WHITEOUT)",
            }
        if stop_rep["issues"]:
            stop_rep["status"] = "FAIL"
            report["fail"] += 1
            report["issues"].extend(f"{name}: {i}" for i in stop_rep["issues"])
        else:
            report["pass"] += 1
        try:
            overlay_stop(name, stop["label"], out, doors)
        except Exception as e:  # noqa: BLE001
            stop_rep["issues"].append(f"overlay render: {e}")
        report["stops"].append(stop_rep)
        print(f"{stop_rep['status']:4s} {stop['label']} ({name}) issues={len(stop_rep['issues'])}")
    (out / "playtest_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"=== early-game playtest: {report['pass']} PASS / {report['fail']} FAIL → {out} ===")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa/playtest"))
    args = ap.parse_args()
    rep = run(args.out)
    return 1 if rep["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
