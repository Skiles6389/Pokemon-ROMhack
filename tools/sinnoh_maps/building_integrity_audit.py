#!/usr/bin/env python3
"""Audit that every outdoor building is a COMPLETE Emerald stamp with a door warp.

For each warp into a building (Center/Mart/Gym/House/civic), check:
  1) Door cell is an expected door metatile
  2) The stamp footprint around the door matches a known complete Emerald stamp
     (from emerald_building_stamps.py / extracted source layouts)
  3) No missing rows/columns vs that stamp (exact tile match)

Fails are hard gates for headless smoke / QA.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.sinnoh_maps.city_door_warp_audit import (  # noqa: E402
    OUTDOOR_SETTLEMENTS,
    classify_warp,
)
from tools.sinnoh_maps.emerald_building_stamps import ALL_STAMPS  # noqa: E402

LAYOUTS = {
    L["name"].replace("_Layout", ""): L
    for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"]
}
MAPS = REPO / "data/maps"

DOOR_MTS = {s["door_mt"] for s in ALL_STAMPS if s.get("door_mt")}
# Sibling double-door tiles
DOOR_MTS |= {0x062, 0x042}


def load_grid(name: str):
    meta = LAYOUTS[name]
    w, h = int(meta["width"]), int(meta["height"])
    data = (REPO / meta["blockdata_filepath"]).read_bytes()
    grid = [
        [struct.unpack_from("<H", data, (y * w + x) * 2)[0] & 0x3FF for x in range(w)]
        for y in range(h)
    ]
    return grid, w, h


def match_stamp(grid, w, h, door_x, door_y, stamp) -> tuple[int, list[str]]:
    """Return (mismatch_count, issue messages). Empty issues = perfect match."""
    tiles = stamp["tiles"]
    dx, dy = stamp["door_dx"], stamp["door_dy"]
    left, top = door_x - dx, door_y - dy
    issues: list[str] = []
    sh, sw = len(tiles), len(tiles[0])
    if left < 0 or top < 0 or left + sw > w or top + sh > h:
        return sw * sh, [f"stamp {stamp['name']} OOB at door ({door_x},{door_y})"]
    # Door tile must match
    expect_door = stamp["door_mt"]
    got_door = grid[door_y][door_x]
    door_penalty = 0
    if got_door != expect_door and not (
        expect_door in (0x061, 0x041) and got_door in (0x062, 0x042)
    ):
        # Allow matching a sibling stamp door on x+1 for double doors
        if not (door_x > 0 and grid[door_y][door_x - 1] == expect_door):
            door_penalty = 1
            issues.append(
                f"door mt 0x{got_door:03X} != stamp {stamp['name']} door 0x{expect_door:03X}"
            )
    mismatches = 0
    missing = 0
    for row_i, row in enumerate(tiles):
        for col_i, expect in enumerate(row):
            x, y = left + col_i, top + row_i
            got = grid[y][x]
            if got != expect:
                mismatches += 1
                # Truncation heuristic: grass/pave/tree where building body expected
                if got < 0x028 or got in (0x001, 0x00D, 0x2BB, 0x2C3) or got in (
                    0x1D4, 0x1D5, 0x1DC, 0x1DD,
                ):
                    missing += 1
    if mismatches:
        issues.append(
            f"stamp {stamp['name']}: {mismatches}/{sw*sh} tiles differ"
            + (f" ({missing} look truncated)" if missing else "")
        )
    return mismatches + door_penalty * 10, issues


def best_stamp_match(grid, w, h, door_x, door_y, kind: str) -> tuple[dict | None, list[str]]:
    """Try stamps appropriate for kind; return best (fewest tile mismatches)."""
    prefer = []
    if kind == "center":
        prefer = [s for s in ALL_STAMPS if "pc" in s["name"]]
    elif kind == "mart":
        prefer = [s for s in ALL_STAMPS if "mart" in s["name"]]
    elif kind == "gym":
        prefer = [s for s in ALL_STAMPS if "gym" in s["name"]]
    elif kind == "civic":
        prefer = [s for s in ALL_STAMPS if "civic" in s["name"] or s["name"] == "rustboro_house"]
    elif kind in ("building", "house"):
        prefer = [s for s in ALL_STAMPS if "house" in s["name"] or "civic" in s["name"]]
    else:
        prefer = [s for s in ALL_STAMPS if s.get("door_mt")]

    # Also try all door-bearing stamps as fallback
    candidates = prefer + [s for s in ALL_STAMPS if s.get("door_mt") and s not in prefer]
    best = None
    best_score = 10**9
    best_issues = ["no candidate stamp"]
    for stamp in candidates:
        score, issues = match_stamp(grid, w, h, door_x, door_y, stamp)
        # Try door at x-1 if this warp is right half of double door
        if score and door_x > 0:
            alt_score, alt = match_stamp(grid, w, h, door_x - 1, door_y, stamp)
            if alt_score < score:
                score, issues = alt_score, alt
        if score < best_score:
            best, best_score, best_issues = stamp, score, issues
        if score == 0:
            return stamp, []
    return best, best_issues


def audit_map(name: str) -> dict:
    if name not in LAYOUTS:
        return {"name": name, "status": "SKIP", "issues": ["no layout"]}
    grid, w, h = load_grid(name)
    mj = MAPS / name / "map.json"
    warps = json.loads(mj.read_text()).get("warp_events") or [] if mj.exists() else []
    issues = []
    checked = 0
    seen_doors: set[tuple[str, int, int]] = set()
    for warp in warps:
        dest = warp.get("dest_map") or ""
        kind = classify_warp(dest)
        if kind in ("cave", "gate", "other"):
            continue
        if kind in (None, "unknown"):
            # Still check house-like dests
            if not any(
                k in dest
                for k in (
                    "HOUSE", "CENTER", "MART", "GYM", "SCHOOL", "TV_", "POKETCH",
                    "CONDO", "TERMINAL", "LAB", "MUSEUM", "DEPT", "GAME", "HALL",
                    "GALACTIC", "HQ", "LIBRARY",
                )
            ):
                continue
            kind = "building"
        x, y = int(warp["x"]), int(warp["y"])
        if not (0 <= x < w and 0 <= y < h):
            issues.append(f"OOB warp ({x},{y}) {dest}")
            continue
        mt = grid[y][x]
        # Double-door: if this warp sits on the sibling half, audit from primary door
        door_x = x
        if mt in (0x062, 0x042) and x > 0 and grid[y][x - 1] in (0x061, 0x041):
            door_x = x - 1
        elif mt in (0x060, 0x266) and x + 1 < w and grid[y][x + 1] in (0x061, 0x041):
            door_x = x + 1
        key = (dest, door_x, y)
        if key in seen_doors:
            continue
        seen_doors.add(key)
        checked += 1
        door_mt = grid[y][door_x]
        if door_mt not in DOOR_MTS and not (
            door_x > 0 and grid[y][door_x - 1] in DOOR_MTS
        ) and not (door_x + 1 < w and grid[y][door_x + 1] in DOOR_MTS):
            issues.append(f"({x},{y}) {dest}: no door metatile (got 0x{mt:03X})")
            continue
        _stamp, stamp_issues = best_stamp_match(grid, w, h, door_x, y, kind or "building")
        for msg in stamp_issues:
            issues.append(f"({door_x},{y}) {dest}: {msg}")
    status = "FAIL" if issues else ("PASS" if checked else "SKIP")
    return {"name": name, "status": status, "checked": checked, "issues": issues}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "tools/sinnoh_maps/building_integrity_audit_report.json")
    ap.add_argument("--maps", nargs="*", help="Subset of maps (default: outdoor settlements)")
    args = ap.parse_args()
    names = args.maps or sorted(OUTDOOR_SETTLEMENTS)
    results = [audit_map(n) for n in names]
    fail = sum(1 for r in results if r["status"] == "FAIL")
    warn = sum(1 for r in results if r["status"] == "SKIP")
    passed = sum(1 for r in results if r["status"] == "PASS")
    for r in results:
        if r["status"] == "FAIL":
            print(f"FAIL {r['name']}: {len(r['issues'])} issues")
            for i in r["issues"][:8]:
                print(f"  - {i}")
        elif r["status"] == "PASS":
            print(f"PASS {r['name']} ({r['checked']} buildings)")
    out = {
        "fail": fail,
        "pass": passed,
        "skip": warn,
        "results": results,
        "stamp_catalog": [s["name"] for s in ALL_STAMPS],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"=== building_integrity_audit: {fail} FAIL / {passed} PASS / {warn} SKIP → {args.out} ===")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
