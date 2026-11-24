#!/usr/bin/env python3
"""Script audit: story NPCs that should leave must removeobject + set hide flag.

Heuristic for Sinnoh maps:
  - object_events with FLAG_HIDE_* that are cleared during story must later
    setflag the same hide flag and removeobject the local id
  - Scripts that end story scenes with only msgbox/release and leave a named
    rival/assistant/grunt/cynthia/looker on the map are flagged
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data" / "maps"

# Sinnoh outdoor + key story maps (from map_groups towns/routes + known indoors)
SINNOH_HINTS = (
    "Twinleaf", "Sandgem", "Jubilife", "Oreburgh", "Floaroma", "Eterna",
    "Hearthome", "Solaceon", "Veilstone", "Pastoria", "Canalave", "Snowpoint",
    "Sunyshore", "FightArea", "Survival", "Resort", "Celestic", "Valor",
    "Acuity", "SpearPillar", "Distortion", "Galactic", "Lake", "Route20",
    "Route21", "Route22", "IronIsland", "VictoryRoad_Sinnoh", "PokemonLeague",
    "Stark", "GreatMarsh", "ValleyWindworks", "Ravaged", "MtCoronet",
)

STORY_GFX = (
    "RIVAL", "BARRY", "ASSISTANT", "ROWAN", "CYNTHIA", "LOOKER",
    "GALACTIC", "GRUNT", "MARS", "JUPITER", "SATURN", "CYRUS",
    "GARDENIA", "WAKE", "FANTINA", "MAYLENE", "BYRON", "CANDICE", "VOLKNER",
)


def is_sinnoh(name: str) -> bool:
    return any(h in name for h in SINNOH_HINTS)


def audit_map(folder: Path) -> list[dict]:
    issues = []
    scripts = folder / "scripts.inc"
    mj = folder / "map.json"
    if not scripts.exists() or not mj.exists():
        return issues
    text = scripts.read_text()
    data = json.loads(mj.read_text())
    objs = data.get("object_events") or []

    # Map local object index → flag / script / gfx
    for idx, obj in enumerate(objs):
        flag = str(obj.get("flag") or "0")
        script = obj.get("script") or ""
        gfx = obj.get("graphics_id") or ""
        if "ITEM_BALL" in gfx.upper() or "POKEBALL" in gfx.upper():
            continue  # item pickups use item flags, not NPC exits
        if flag in ("0", "") and not any(s in gfx.upper() for s in STORY_GFX):
            continue
        if not script or script == "NULL":
            continue
        # Find script body (rough)
        m = re.search(rf"^{re.escape(script)}::\n(.*?)(?=^\w|\Z)", text, re.M | re.S)
        body = m.group(1) if m else ""
        if not body:
            continue
        # Permanent town NPCs that only talk — not exits
        if "applymovement" not in body and "trainerbattle" not in body:
            continue
        # Story-ish if it sets vars/flags or has movement
        storyish = bool(re.search(r"setflag |setvar |applymovement |trainerbattle", body))
        if not storyish:
            continue
        has_remove = "removeobject" in body
        hide_sets = re.findall(r"setflag (FLAG_HIDE_\w+)", body)
        # Whole-map script may remove this LOCALID even if talk script doesn't
        if has_remove or (flag.startswith("FLAG_HIDE_") and f"setflag {flag}" in text):
            continue
        if flag.startswith("FLAG_HIDE_") and flag not in hide_sets:
            if f"clearflag {flag}" in text or "applymovement" in body:
                issues.append({
                    "map": folder.name,
                    "object_index": idx,
                    "script": script,
                    "flag": flag,
                    "gfx": gfx,
                    "issue": "story script lacks setflag hide + removeobject for this NPC",
                })
        elif any(s in gfx.upper() for s in STORY_GFX) and "applymovement" in body and not has_remove:
            issues.append({
                "map": folder.name,
                "object_index": idx,
                "script": script,
                "flag": flag,
                "gfx": gfx,
                "issue": "story NPC movement without removeobject",
            })
    return issues


def main() -> int:
    all_issues = []
    for folder in sorted(MAPS.iterdir()):
        if not folder.is_dir() or not is_sinnoh(folder.name):
            continue
        all_issues.extend(audit_map(folder))
    out = REPO / "tools/sinnoh_maps/script_npc_exit_audit_report.json"
    out.write_text(json.dumps({"issues": all_issues, "count": len(all_issues)}, indent=2) + "\n")
    for i in all_issues[:60]:
        print(f"FAIL {i['map']}: {i['script']} ({i['gfx']}) — {i['issue']}")
    if len(all_issues) > 60:
        print(f"... {len(all_issues) - 60} more")
    print(f"=== script NPC exit audit: {len(all_issues)} issues → {out} ===")
    return 1 if all_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
