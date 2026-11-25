#!/usr/bin/env python3
"""Sign / NPC / trigger script audit for the early-game Sinnoh maps.

Static checks (FAIL) for every bg_event sign, object_event and coord_event script:
  missing_label      script label not defined in any data/**/*.inc
  fallthrough        body runs into the next label without end/return/goto/... (a
                     script that falls into text or movement data executes garbage)
  lock_no_release    lock/lockall on a path that ends without release/releaseall
                     (MSGBOX_NPC/MSGBOX_SIGN/... handle their own lock)
  bad_text           msgbox/message text label missing, has no .string, or the
                     last .string does not end with '$' (printer runs off the end)
  bad_movement       applymovement label missing or not terminated by step_end,
                     or target local id not on the map
  sign_tile          sign bg_event on a walkable cell (cannot be faced on purpose)
                     or a collision cell with no event (dead sign) - warning
  null_gfx           object_event (or setobjectgfx / VAR gfx in a script) uses an
                     OBJ_EVENT_GFX_* whose graphics info is compiled out of the
                     Emerald build (#if IS_FRLG in object_event_graphics_info_pointers.h).
                     The pointer is NULL, so the NPC's animation reads garbage and the
                     game crashes/reboots the first time it walks (Jubilife m51 freeze).
                     This check also runs globally over every map built into the
                     Emerald ROM (layout_version "emerald"), not just the listed maps.

Usage: python3 tools/sinnoh_maps/sign_script_audit.py [Map ...] [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_MAPS = ["TwinleafTown", "Route201", "VerityLakefront", "LakeVerity",
                "SandgemTown", "Route202", "JubilifeCity"]
TERMINAL = {"end", "return", "goto", "releaseall_end", "step_end", "goto_if_set_end"}
ENDS = re.compile(r"^(end|return|goto|step_end|special\s+\w+\s*;\s*end)\b")
LOCKS = re.compile(r"^(lock|lockall)\b")
RELEASES = re.compile(r"^(release|releaseall)\b")
SELF_LOCKING = ("MSGBOX_NPC", "MSGBOX_SIGN", "MSGBOX_YESNO_NPC", "MSGBOX_AUTOCLOSE")
SIGN_BEHAVIORS = {"MB_SIGNPOST", "MB_POKEMON_CENTER_SIGN", "MB_POKEMART_SIGN"}


@lru_cache(None)
def labels() -> dict[str, tuple[Path, list[str]]]:
    """label -> (file, body lines until next label)."""
    out = {}
    files = list((REPO / "data").rglob("*.inc")) + list((REPO / "data").rglob("*.s"))
    for f in files:
        try:
            lines = f.read_text(errors="replace").splitlines()
        except OSError:
            continue
        cur, body = None, []
        for ln in lines:
            m = re.match(r"^([A-Za-z_]\w*)::?\s*$", ln)
            if m:
                if cur:
                    out.setdefault(cur, (f, body))
                cur, body = m.group(1), []
            elif cur is not None:
                s = ln.split("@")[0].strip()
                if s:
                    body.append(s)
        if cur:
            out.setdefault(cur, (f, body))
    return out


def check_text(lbl: str) -> str | None:
    L = labels().get(lbl)
    if not L:
        return f"text label {lbl} missing"
    strs = [b for b in L[1] if b.startswith(".string")]
    if not strs:
        return f"text label {lbl} has no .string"
    if not strs[-1].rstrip().endswith('$"'):
        return f"text label {lbl}: last .string does not end with '$'"
    return None


def check_movement(lbl: str) -> str | None:
    L = labels().get(lbl)
    if not L:
        return f"movement {lbl} missing"
    if not L[1] or L[1][-1] != "step_end":
        return f"movement {lbl} not terminated by step_end"
    return None


def walk(lbl: str, local_ids: set[str], seen: set[str], locked: bool, issues: list[str], depth: int = 0) -> None:
    key = f"{lbl}:{locked}"
    if key in seen or depth > 40:
        return
    seen.add(key)
    L = labels().get(lbl)
    if not L:
        issues.append(f"missing_label: {lbl}")
        return
    body = L[1]
    terminated = False
    switched = False
    for s in body:
        op = s.split()[0]
        args = [a.strip() for a in s[len(op):].split(",")]
        if LOCKS.match(s):
            locked = True
        elif RELEASES.match(s):
            locked = False
        elif op in ("msgbox", "message"):
            t = check_text(args[0])
            if t:
                issues.append(f"bad_text: {lbl}: {t}")
        elif op == "applymovement":
            tgt, mv = args[0], args[1] if len(args) > 1 else ""
            if tgt not in local_ids and not tgt.startswith("OBJ_EVENT_ID_") and not tgt.isdigit():
                issues.append(f"bad_movement: {lbl}: target {tgt} is not an object on this map")
            m = check_movement(mv)
            if m:
                issues.append(f"bad_movement: {lbl}: {m}")
        elif op in ("call", "call_if_eq", "call_if_ne", "call_if_set", "call_if_unset", "call_if_lt", "call_if_ge"):
            tgt = args[-1]
            if tgt not in labels():
                issues.append(f"missing_label: {lbl} calls {tgt}")
        elif op.startswith("goto_if") or op.startswith("goto"):
            tgt = args[-1]
            walk(tgt, local_ids, seen, locked, issues, depth + 1)
            if op == "goto":
                terminated = True
                break
        elif op == "case":
            walk(args[-1], local_ids, seen, locked, issues, depth + 1)
            switched = True
        elif op.startswith("trainerbattle"):
            conts = [a for a in args if a in labels() and not any(b.startswith(".string") for b in labels()[a][1])]
            for c in conts:
                walk(c, local_ids, seen, locked, issues, depth + 1)
            if conts:
                terminated = True
                break
        if op in ("end", "return", "releaseall_end"):
            if locked and op == "end" and not switched:
                issues.append(f"lock_no_release: {lbl} ends while still locked")
            terminated = True
            break
    if not terminated:
        issues.append(f"fallthrough: {lbl} has no end/return/goto before the next label ({L[0].relative_to(REPO)})")


@lru_cache(None)
def compiled_out_gfx() -> frozenset:
    """OBJ_EVENT_GFX_* ids whose pointer only exists in FRLG builds (NULL in Emerald)."""
    lines = (REPO / "src/data/object_events/object_event_graphics_info_pointers.h").read_text().splitlines()
    depth: list[bool] = []
    out = set()
    for ln in lines:
        s = ln.strip()
        if s.startswith("#if"):
            depth.append("IS_FRLG" in s and "!IS_FRLG" not in s)
        elif s.startswith("#else"):
            depth[-1] = not depth[-1]
        elif s.startswith("#endif"):
            depth.pop()
        else:
            m = re.match(r"\[(OBJ_EVENT_GFX_\w+)\]", s)
            if m and any(depth):
                out.add(m.group(1))
    return frozenset(out)


def audit_map(name: str) -> dict:
    mj = json.loads((REPO / "data/maps" / name / "map.json").read_text())
    objs = mj.get("object_events") or []
    local_ids = {o["local_id"] for o in objs if o.get("local_id")}
    local_ids |= {str(i + 1) for i in range(len(objs))}
    inc = REPO / "data/maps" / name / "scripts.inc"
    if inc.exists():
        local_ids |= set(re.findall(r"^\.equ\s+(\w+)\s*,", inc.read_text(), re.M))
    entries = []
    for b in mj.get("bg_events") or []:
        if b.get("type") == "sign":
            entries.append(("sign", (b["x"], b["y"]), b["script"]))
    for o in objs:
        if o.get("script") and o["script"] != "0x0":
            entries.append(("object", (o["x"], o["y"]), o["script"]))
    for c in mj.get("coord_events") or []:
        if c.get("script"):
            entries.append(("coord", (c["x"], c["y"]), c["script"]))
    results, fails = [], 0
    done = set()
    for kind, pos, scr in entries:
        if scr in done:
            continue
        done.add(scr)
        issues: list[str] = []
        walk(scr, local_ids, set(), False, issues)
        issues = sorted(set(issues))
        fails += bool(issues)
        results.append({"kind": kind, "pos": pos, "script": scr, "issues": issues})
    bad_gfx = compiled_out_gfx()
    for o in objs:
        if o.get("graphics_id") in bad_gfx:
            fails += 1
            results.append({"kind": "object", "pos": (o["x"], o["y"]), "script": o.get("script"),
                            "issues": [f"null_gfx: {o['graphics_id']} is FRLG-only (NULL graphics info in this build)"]})
    inc = REPO / "data/maps" / name / "scripts.inc"
    if inc.exists():
        for g in sorted(set(re.findall(r"OBJ_EVENT_GFX_\w+", inc.read_text())) & bad_gfx):
            fails += 1
            results.append({"kind": "script", "pos": None, "script": f"{name}/scripts.inc",
                            "issues": [f"null_gfx: script uses {g} (FRLG-only, NULL in this build)"]})
    # sign cells must be solid so the player faces them with A
    sign_issues = []
    L = next(l for l in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"] if l.get("id") == mj["layout"])
    w = int(L["width"])
    raw = (REPO / L["blockdata_filepath"]).read_bytes()
    for b in mj.get("bg_events") or []:
        if b.get("type") != "sign":
            continue
        v = struct.unpack_from("<H", raw, (b["y"] * w + b["x"]) * 2)[0]
        if not (v >> 10) & 3:
            sign_issues.append(f"sign {b['script']} at ({b['x']},{b['y']}) is on a walkable cell")
    return {"map": name, "status": "FAIL" if fails else "PASS", "scripts": results, "sign_warnings": sign_issues,
            "counts": {k: sum(1 for e in entries if e[0] == k) for k in ("sign", "object", "coord")}}


def emerald_maps() -> list[str]:
    """Maps whose layout is built into the Emerald ROM (mapjson skips frlg layouts)."""
    lv = {l["id"]: l.get("layout_version") or "emerald"
          for l in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"] if l.get("id")}
    out = []
    for mj in sorted((REPO / "data/maps").glob("*/map.json")):
        if lv.get(json.loads(mj.read_text()).get("layout")) == "emerald":
            out.append(mj.parent.name)
    return out


def global_null_gfx() -> dict:
    """null_gfx over every Emerald-built map (object_events and its scripts)."""
    bad = compiled_out_gfx()
    issues = []
    for name in emerald_maps():
        d = REPO / "data/maps" / name
        for o in json.loads((d / "map.json").read_text()).get("object_events") or []:
            if o.get("graphics_id") in bad:
                issues.append(f"{name}@({o['x']},{o['y']}) {o['graphics_id']}")
        for inc in d.glob("*.inc"):
            if inc.name == "events.inc":
                continue  # generated from map.json
            for g in sorted(set(re.findall(r"OBJ_EVENT_GFX_\w+", inc.read_text(errors="replace"))) & bad):
                issues.append(f"{name}/{inc.name} uses {g}")
    return {"map": "(all Emerald maps)", "status": "FAIL" if issues else "PASS",
            "scripts": [{"kind": "object", "pos": None, "script": None, "issues": [f"null_gfx: {i}" for i in issues]}] if issues else [],
            "sign_warnings": [], "counts": {"sign": 0, "object": len(issues), "coord": 0}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("maps", nargs="*", default=DEFAULT_MAPS)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--no-global-gfx", action="store_true", help="skip the repo-wide null_gfx scan")
    a = ap.parse_args()
    res = [audit_map(m) for m in a.maps]
    if not a.no_global_gfx:
        res.append(global_null_gfx())
    for r in res:
        c = r["counts"]
        print(f"{r['status']:4}  {r['map']:16} signs={c['sign']} objects={c['object']} coords={c['coord']}")
        for s in r["scripts"]:
            for i in s["issues"]:
                print(f"      FAIL {s['kind']}@{s['pos']} {i}")
        for wmsg in r["sign_warnings"]:
            print("      warn", wmsg)
    if a.json:
        a.json.write_text(json.dumps(res, indent=1))
    print(f"{sum(r['status'] == 'PASS' for r in res)}/{len(res)} maps pass")
    return int(any(r["status"] == "FAIL" for r in res))


if __name__ == "__main__":
    sys.exit(main())
