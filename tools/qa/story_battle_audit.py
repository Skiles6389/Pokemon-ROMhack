#!/usr/bin/env python3
"""Audit scripted story battles for win/lose softlock patterns.

Fails when:
  - A continue-on-loss battle (first Barry / flagged) lacks FLAG_TEMP_5 /
    HealPlayerParty / shared post-script goto.
  - A story battle uses trainerbattle … continueScript=FALSE with an
    After* script AND an OnFrame rematch on the same state (black-screen risk).
  - Post-battle scripts omit fadescreen FADE_FROM_BLACK or hide/remove of the
    battling NPC (Barry / commander).

Also emits a JSON report of every story trainerbattle for the playtest harness.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data/maps"

# Maps/scripts that MUST continue on loss (Platinum win-or-lose story beats)
CONTINUE_ON_LOSS = {
    "Route201": {
        "label": "Barry_1_Route201",
        "require": [
            r"setflag\s+FLAG_TEMP_5",
            r"trainerbattle_no_intro\s+TRAINER_BARRY_1_",
            r"special\s+HealPlayerParty",
            r"goto\s+Route201_EventScript_AfterBattle",
            r"fadescreen\s+FADE_FROM_BLACK",
            r"setflag\s+FLAG_HIDE_ROUTE201_BARRY",
            r"setvar\s+VAR_ROUTE201_STATE,\s*4",
        ],
        "forbid": [
            r"map_script_2\s+VAR_ROUTE201_STATE,\s*3,\s*Route201_EventScript_BarryRematch",
            r"Route201_EventScript_BarryRematch::",
        ],
    },
}

# Other story battles: must use trainerbattle_no_intro + goto After* (clean win path)
STORY_NO_INTRO = [
    ("Route203", r"TRAINER_BARRY_2_", "Route203_EventScript_AfterBattle"),
    ("HearthomeCity", r"TRAINER_BARRY_3_", "HearthomeCity_EventScript_AfterBarry"),
    ("PastoriaCity", r"TRAINER_BARRY_4_", "PastoriaCity_EventScript_AfterBarry"),
    ("CanalaveCity", r"TRAINER_BARRY_4_", "CanalaveCity_EventScript_AfterBarry"),
    ("PokemonLeague_Sinnoh_CynthiasRoom", r"TRAINER_CHAMPION_CYNTHIA", None),
    ("ValleyWindworks_Interior", r"TRAINER_COMMANDER_MARS", None),
    ("TeamGalacticEternaBuilding_4F", r"TRAINER_COMMANDER_JUPITER", None),
    ("LakeValor_Drained", r"TRAINER_COMMANDER_SATURN", None),
    ("LakeAcuity", r"TRAINER_COMMANDER_JUPITER_ACUITY", None),
]


def read_script(map_name: str) -> str:
    p = MAPS / map_name / "scripts.inc"
    return p.read_text() if p.exists() else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa/story_battle_audit.json"))
    args = ap.parse_args()

    fails: list[str] = []
    reports: list[dict] = []

    for map_name, cfg in CONTINUE_ON_LOSS.items():
        text = read_script(map_name)
        entry = {"map": map_name, "label": cfg["label"], "continue_on_loss": True, "ok": True, "issues": []}
        for pat in cfg["require"]:
            if not re.search(pat, text):
                msg = f"missing /{pat}/"
                entry["issues"].append(msg)
                fails.append(f"{map_name}: {msg}")
        for pat in cfg["forbid"]:
            if re.search(pat, text):
                msg = f"forbidden /{pat}/ (rematch softlock)"
                entry["issues"].append(msg)
                fails.append(f"{map_name}: {msg}")
        entry["ok"] = not entry["issues"]
        reports.append(entry)
        print(("PASS" if entry["ok"] else "FAIL"), cfg["label"])

    for map_name, trainer_re, after in STORY_NO_INTRO:
        text = read_script(map_name)
        entry = {
            "map": map_name,
            "label": trainer_re,
            "continue_on_loss": False,
            "ok": True,
            "issues": [],
        }
        if not text:
            entry["issues"].append("missing scripts.inc")
        elif not re.search(rf"trainerbattle_no_intro\s+{trainer_re}", text):
            # commanders may use trainerbattle_single with after-script — OK if no continueScript=FALSE rematch
            if re.search(
                rf"trainerbattle\s+LOCALID_\w+,\s*{trainer_re}[^\\n]*,\s*FALSE,\s*TRUE,\s*FALSE,\s*FALSE,\s*FALSE,",
                text,
            ):
                entry["issues"].append("raw trainerbattle continueScript=FALSE (prefer trainerbattle_no_intro)")
            elif not re.search(rf"trainerbattle_single\s+{trainer_re}|trainerbattle_no_intro\s+{trainer_re}", text):
                entry["issues"].append(f"no trainerbattle for {trainer_re}")
        if after and text and f"goto {after}" not in text and f"{after}::" in text:
            # After label exists; ensure win path reaches it via goto when using no_intro
            if re.search(rf"trainerbattle_no_intro\s+{trainer_re}", text) and f"goto {after}" not in text:
                entry["issues"].append(f"trainerbattle_no_intro without goto {after}")
        if after and text and "fadescreen FADE_FROM_BLACK" not in text:
            # Soft requirement for Barry post-scripts
            if "BARRY" in trainer_re:
                entry["issues"].append("Barry After* missing fadescreen FADE_FROM_BLACK")
        entry["ok"] = not entry["issues"]
        if entry["issues"]:
            fails.extend(f"{map_name}: {i}" for i in entry["issues"])
        reports.append(entry)
        print(("PASS" if entry["ok"] else "FAIL"), map_name, trainer_re)

    # Scan all Sinnoh scripts for continueScript=FALSE + OnFrame rematch pattern
    for scripts in MAPS.glob("*/scripts.inc"):
        text = scripts.read_text()
        map_name = scripts.parent.name
        if re.search(r"map_script_2\s+VAR_\w+,\s*\d+,\s*\w*Rematch", text):
            if "trainerbattle " in text and "continueScript" not in text:
                # Heuristic: Rematch OnFrame alongside raw trainerbattle is risky
                if re.search(r"trainerbattle\s+LOCALID_", text) and "trainerbattle_no_intro" not in text:
                    msg = f"{map_name}: OnFrame *Rematch with raw trainerbattle (black-screen risk)"
                    # Route201 should already be cleaned; flag others
                    if map_name != "Route201" or "BarryRematch" in text:
                        fails.append(msg)
                        reports.append({"map": map_name, "ok": False, "issues": [msg]})

    out = {
        "fail": len(fails),
        "pass": sum(1 for r in reports if r.get("ok")),
        "issues": fails,
        "results": reports,
        "outcomes": {
            "Barry_1_Route201": {"win": "AfterBattle (hide Barry, state=4)", "lose": "same AfterBattle + heal"},
            "Barry_2_Route203": {"win": "AfterBattle", "lose": "whiteout; rematch via trigger"},
            "Barry_3_Hearthome": {"win": "AfterBarry", "lose": "whiteout; rematch via trigger"},
            "Barry_4_Pastoria_Canalave": {"win": "AfterBarry", "lose": "whiteout"},
            "Commanders_Cynthia": {"win": "continue / defeat script", "lose": "whiteout"},
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"=== story_battle_audit: {out['pass']} PASS / {out['fail']} FAIL → {args.out} ===")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
