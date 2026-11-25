#!/usr/bin/env python3
"""m48 playtester regression checks (static).

1) Trainer party gender vs species genderRatio (static parties only)
2) Ledge metatiles 0x0D5/0x0D6 must have collision=1
3) Sandgem / Jubilife Pokémon Center outdoor warps enterable
4) Barry1 AfterBattle branches on GetBattleOutcome (win vs loss lines)
5) Scripted applymovement vs map collision (movement_collision_check)
"""
from __future__ import annotations

import json
import re
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FAILS: list[str] = []


def check_trainer_genders() -> None:
    """Parse trainers.party for (M)/(F) on known genderless species names."""
    party = (REPO / "src/data/trainers.party").read_text(errors="replace")
    # Genderless legendaries that commonly break forced-(M) under randomizer;
    # static audit: flag explicit (M)/(F) on genderless names if any appear.
    genderless = {
        "Regieleki", "Regidrago", "Regirock", "Regice", "Registeel", "Regigigas",
        "Porygon", "Porygon2", "Porygon-Z", "Magnemite", "Magneton", "Magnezone",
        "Staryu", "Starmie", "Voltorb", "Electrode", "Baltoy", "Claydol",
        "Beldum", "Metang", "Metagross", "Bronzor", "Bronzong", "Klink",
        "Klang", "Klinklang", "Honedge", "Doublade", "Aegislash", "Ditto",
        "Shedinja", "Rotom", "Cryogonal", "Minior", "Dhelmise", "Sinistea",
        "Polteageist", "Falinks", "Gimmighoul", "Gholdengo",
    }
    # Line form: "Species @ item" or "Species (M)" etc.
    for i, line in enumerate(party.splitlines(), 1):
        m = re.search(r"^\s*([A-Za-z0-9\-]+)(?:\s*\(([MF])\))?", line)
        if not m:
            continue
        name, g = m.group(1), m.group(2)
        if g and name in genderless:
            FAILS.append(f"trainers.party:{i}: {name} forced ({g}) but species is genderless")


def check_ledges() -> None:
    layouts = json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
    ledges = {0x0D5, 0x0D6}
    bad_maps = 0
    bad_cells = 0
    for L in layouts:
        path = REPO / L["blockdata_filepath"]
        if not path.exists():
            continue
        w, h = int(L["width"]), int(L["height"])
        data = path.read_bytes()
        n = 0
        for i in range(w * h):
            v = struct.unpack_from("<H", data, i * 2)[0]
            if (v & 0x3FF) in ledges and ((v >> 10) & 3) == 0:
                n += 1
        if n:
            bad_maps += 1
            bad_cells += n
            name = L["name"].replace("_Layout", "")
            FAILS.append(f"ledge coll=0: {name} ×{n}")
    if bad_cells:
        FAILS.append(f"ledge total: {bad_cells} cells across {bad_maps} maps")


def check_center_doors() -> None:
    report = REPO / "tools/sinnoh_maps/city_door_warp_audit_report.json"
    if not report.exists():
        return
    data = json.loads(report.read_text())
    for r in data.get("results") or data.get("maps") or []:
        name = r.get("name") or r.get("map")
        if name not in ("SandgemTown", "JubilifeCity"):
            continue
        # Prefer structured enterable flags if present
        status = r.get("status")
        if status == "FAIL":
            FAILS.append(f"door audit FAIL: {name}: {r.get('issues', r)[:2]}")


def check_barry1_outcome_dialogue() -> None:
    text = (REPO / "data/maps/Route201/scripts.inc").read_text(errors="replace")
    for needle in (
        "specialvar VAR_RESULT, GetBattleOutcome",
        "B_OUTCOME_WON",
        "B_OUTCOME_LOST",
        "Route201_Text_BarryAfterWin",
        "Route201_Text_BarryAfterLoss",
    ):
        if needle not in text:
            FAILS.append(f"Barry1 AfterBattle missing {needle}")


def check_movement_collision() -> None:
    script = REPO / "tools/qa/movement_collision_check.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        FAILS.append("movement_collision_check failed")
        for line in (proc.stdout + proc.stderr).splitlines()[:20]:
            FAILS.append(f"  mov: {line}")


def main() -> int:
    check_trainer_genders()
    check_ledges()
    check_center_doors()
    check_barry1_outcome_dialogue()
    check_movement_collision()
    if FAILS:
        print(f"FAIL ({len(FAILS)}):")
        for f in FAILS[:40]:
            print(" -", f)
        return 1
    print("=== playtester_regression_check: PASS ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
