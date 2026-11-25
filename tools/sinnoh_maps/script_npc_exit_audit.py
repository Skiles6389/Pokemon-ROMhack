#!/usr/bin/env python3
"""Script audit: every Platinum story NPC that gets removed must exit in our scripts.

Source of truth: tools/sinnoh_maps/platinum_story_npc_exits.json
(built from pret/pokeplatinum RemoveObject + FLAG_HIDE_* on story maps).

For each non-deferred exit entry, require in data/maps/<map>/scripts.inc:
  - setflag <flag>
  - removeobject <local_id>  (unless path_blocker cleared only via remote setflag)
  - applymovement <local_id> when walk=true

Also checks story_npc_appear_too_early.json: Galactic/commander objects must not
be visible before their story beat (hide flag on objects + set on new game, and
a later clearflag — or the map itself gated by a story flag).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "data" / "maps"
CATALOG = REPO / "tools" / "sinnoh_maps" / "platinum_story_npc_exits.json"
APPEAR_CATALOG = REPO / "tools" / "sinnoh_maps" / "story_npc_appear_too_early.json"
NEW_GAME = REPO / "data" / "scripts" / "new_game.inc"


def load_catalog() -> list[dict]:
    return json.loads(CATALOG.read_text())["exits"]


def script_text(map_name: str) -> str | None:
    p = MAPS / map_name / "scripts.inc"
    return p.read_text() if p.exists() else None


def map_has_local_id(map_name: str, local_id: str) -> bool:
    mj = MAPS / map_name / "map.json"
    if not mj.exists():
        return False
    objs = json.loads(mj.read_text()).get("object_events") or []
    if any(o.get("local_id") == local_id for o in objs):
        return True
    # Some maps use .equ in scripts.inc instead of map.json local_id
    text = script_text(map_name) or ""
    return bool(re.search(rf"\.equ\s+{re.escape(local_id)}\b|LOCALID_\w*{re.escape(local_id.split('_')[-1])}", text))


def audit_exit(entry: dict) -> dict | None:
    if entry.get("deferred"):
        return {
            "map": entry["map"],
            "role": entry.get("role"),
            "flag": entry.get("flag"),
            "status": "DEFERRED",
            "reason": entry.get("reason") or "stub map",
        }

    map_name = entry["map"]
    flag = entry["flag"]
    local_id = entry.get("local_id")
    walk = bool(entry.get("walk"))
    role = entry.get("role") or ""
    text = script_text(map_name)
    if text is None:
        return {
            "map": map_name,
            "role": role,
            "flag": flag,
            "local_id": local_id,
            "status": "FAIL",
            "issue": "missing scripts.inc",
        }

    issues = []
    if f"setflag {flag}" not in text:
        # Path blockers / remote clears: allow setflag in any Sinnoh scripts.inc
        if role == "path_blocker" or entry.get("note"):
            found_elsewhere = False
            for folder in MAPS.iterdir():
                sc = folder / "scripts.inc"
                if sc.exists() and f"setflag {flag}" in sc.read_text():
                    found_elsewhere = True
                    break
            if not found_elsewhere:
                issues.append(f"missing setflag {flag}")
        else:
            issues.append(f"missing setflag {flag}")

    if local_id:
        if f"removeobject {local_id}" not in text:
            if role == "path_blocker":
                pass  # remote flag hide is enough
            else:
                issues.append(f"missing removeobject {local_id}")
        if walk and f"applymovement {local_id}" not in text:
            issues.append(f"missing applymovement walk-off for {local_id}")
        if not entry.get("optional_local_id") and not map_has_local_id(map_name, local_id):
            # Still OK if scripts reference the symbol (map.json or .equ)
            if local_id not in text:
                issues.append(f"local_id {local_id} not present in map/scripts")

    if issues:
        return {
            "map": map_name,
            "role": role,
            "flag": flag,
            "local_id": local_id,
            "status": "FAIL",
            "issue": "; ".join(issues),
        }
    return {
        "map": map_name,
        "role": role,
        "flag": flag,
        "local_id": local_id,
        "status": "PASS",
    }


def _all_scripts_text() -> str:
    chunks = [NEW_GAME.read_text() if NEW_GAME.exists() else ""]
    for folder in MAPS.iterdir():
        sc = folder / "scripts.inc"
        if sc.exists():
            chunks.append(sc.read_text())
    return "\n".join(chunks)


def _matching_objects(map_name: str, entry: dict) -> list[dict]:
    mj = MAPS / map_name / "map.json"
    if not mj.exists():
        return []
    objs = json.loads(mj.read_text()).get("object_events") or []
    gfx_set = set(entry.get("graphics") or [])
    substrs = [s.upper() for s in (entry.get("script_substr") or [])]
    out = []
    for obj in objs:
        gfx = obj.get("graphics_id") or ""
        script = (obj.get("script") or "").upper()
        if gfx_set and gfx in gfx_set:
            out.append(obj)
            continue
        if substrs and any(s in script for s in substrs):
            out.append(obj)
    return out


def audit_appear_too_early(entry: dict) -> dict:
    """Fail if Galactic/story NPCs can show before their beat."""
    map_name = entry["map"]
    role = entry.get("role") or ""
    hide_flag = entry.get("hide_flag")
    issues: list[str] = []

    objs = _matching_objects(map_name, entry)
    if not objs and hide_flag:
        # Map may not have Mars yet — still require new-game hide + clearflag wiring
        pass

    new_game_text = NEW_GAME.read_text() if NEW_GAME.exists() else ""
    all_scripts = _all_scripts_text()

    if hide_flag:
        for obj in objs:
            flag = obj.get("flag") or "0"
            if flag in ("0", 0, "", None):
                issues.append(
                    f"object {obj.get('script') or obj.get('graphics_id')} has flag 0; "
                    f"need {hide_flag}"
                )
            elif flag != hide_flag:
                issues.append(
                    f"object {obj.get('script') or obj.get('graphics_id')} uses {flag}; "
                    f"expected {hide_flag}"
                )
        if f"setflag {hide_flag}" not in new_game_text:
            issues.append(f"new_game.inc missing setflag {hide_flag}")
        appear_clear = entry.get("appear_after_clearflag") or hide_flag
        if f"clearflag {appear_clear}" not in all_scripts:
            issues.append(f"no clearflag {appear_clear} to reveal NPC later")

    gated = entry.get("map_gated_by")
    if gated:
        if f"setflag {gated}" not in all_scripts:
            issues.append(f"map gate {gated} never setflag'd")
        # Exit hide flags (optional): ensure set after defeat so they don't linger forever
        for ef in entry.get("exit_hide_flags") or []:
            if f"setflag {ef}" not in all_scripts:
                issues.append(f"exit hide {ef} never setflag'd")

    # Sweep: any MAGMA/AQUA/MAXIE/ARCHIE on this map with flag 0 when hide_flag expected
    if hide_flag and map_name in ("LakeVerity", "LakeAcuity"):
        mj = MAPS / map_name / "map.json"
        if mj.exists():
            galactic_gfx = {
                "OBJ_EVENT_GFX_MAGMA_MEMBER_M",
                "OBJ_EVENT_GFX_MAGMA_MEMBER_F",
                "OBJ_EVENT_GFX_AQUA_MEMBER_M",
                "OBJ_EVENT_GFX_AQUA_MEMBER_F",
                "OBJ_EVENT_GFX_MAXIE",
                "OBJ_EVENT_GFX_ARCHIE",
            }
            for obj in json.loads(mj.read_text()).get("object_events") or []:
                if obj.get("graphics_id") in galactic_gfx and (obj.get("flag") or "0") in (
                    "0",
                    0,
                    "",
                    None,
                ):
                    issues.append(
                        f"ungated Galactic gfx {obj.get('graphics_id')} "
                        f"script={obj.get('script')} (appears too early)"
                    )

    status = "FAIL" if issues else "PASS"
    return {
        "map": map_name,
        "role": role,
        "check": "appears_too_early",
        "hide_flag": hide_flag,
        "status": status,
        "issue": "; ".join(issues) if issues else None,
    }


def load_appear_catalog() -> list[dict]:
    if not APPEAR_CATALOG.exists():
        return []
    return json.loads(APPEAR_CATALOG.read_text()).get("entries") or []


def main() -> int:
    results = [audit_exit(e) for e in load_catalog()]
    results = [r for r in results if r]
    appear_results = [audit_appear_too_early(e) for e in load_appear_catalog()]
    results.extend(appear_results)

    fails = [r for r in results if r["status"] == "FAIL"]
    deferred = [r for r in results if r["status"] == "DEFERRED"]
    passed = [r for r in results if r["status"] == "PASS"]
    out = REPO / "tools/sinnoh_maps/script_npc_exit_audit_report.json"
    out.write_text(
        json.dumps(
            {
                "results": results,
                "pass": len(passed),
                "fail": len(fails),
                "deferred": len(deferred),
                "count_fail": len(fails),
                "appear_too_early_pass": sum(
                    1 for r in appear_results if r["status"] == "PASS"
                ),
                "appear_too_early_fail": sum(
                    1 for r in appear_results if r["status"] == "FAIL"
                ),
            },
            indent=2,
        )
        + "\n"
    )
    for r in fails:
        kind = r.get("check") or "exit"
        print(
            f"FAIL [{kind}] {r['map']}: {r.get('local_id') or r.get('role')} "
            f"({r.get('flag') or r.get('hide_flag')}) — {r['issue']}"
        )
    for r in deferred:
        print(f"DEFER {r['map']}: {r.get('role')} — {r.get('reason')}")
    print(
        f"=== script NPC exit audit: {len(fails)} FAIL / {len(passed)} PASS / "
        f"{len(deferred)} DEFERRED "
        f"(appear-too-early {sum(1 for r in appear_results if r['status'] == 'PASS')}/"
        f"{len(appear_results)} PASS) → {out} ==="
    )
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
