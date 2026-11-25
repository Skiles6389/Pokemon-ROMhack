#!/usr/bin/env python3
"""Headless mGBA probe: read every sign on a map from every walkable side, then walk away.

For each sign bg_event and each walkable neighbour cell, the QA_SHOT ROM spawns the
player there, turns toward the sign, presses A, closes the text, walks INTO the
sign for 1 s (walk-into signpost trigger), closes again, then tries to step in
every direction.  CRASH = the vblank counter stopped (hard crash / reboot loop);
STUCK = alive but the player could not move at all (script lock / softlock).

  python3 tools/qa/sign_freeze_probe.py ROM MAP_DIR_NAME MAP_CONST [--shots DIR]
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from tools.qa.mgba_shot import run  # noqa: E402

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
AWAY = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}


def symbols(rom: Path) -> dict[str, int]:
    mp = rom.with_suffix(".map")
    out = {}
    for name in ("gMain", "gObjectEvents"):
        m = re.search(rf"^\s+(0x[0-9a-f]+)\s+{name}$", mp.read_text(), re.M)
        out[name] = int(m.group(1), 16)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", type=Path)
    ap.add_argument("map")
    ap.add_argument("const")
    ap.add_argument("--shots", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    sym = symbols(a.rom)
    vbl = sym["gMain"] + 0x20
    px, py = sym["gObjectEvents"] + 0x10, sym["gObjectEvents"] + 0x12
    mj = json.loads((REPO / "data/maps" / a.map / "map.json").read_text())
    lay = next(l for l in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"] if l.get("id") == mj["layout"])
    w, h = int(lay["width"]), int(lay["height"])
    raw = (REPO / lay["blockdata_filepath"]).read_bytes()
    solid = lambda x, y: not (0 <= x < w and 0 <= y < h) or bool((struct.unpack_from("<H", raw, (y * w + x) * 2)[0] >> 10) & 3)
    objs = {(o["x"], o["y"]) for o in mj.get("object_events") or []}
    results = []
    for b in mj.get("bg_events") or []:
        if b.get("type") != "sign":
            continue
        for dname, (dx, dy) in DIRS.items():
            sx, sy = b["x"] - dx, b["y"] - dy          # stand here, face dname
            if solid(sx, sy) or (sx, sy) in objs:
                continue
            away = AWAY[dname]
            tag = f"{b['script'].split('_')[-1]}_{dname}"
            shot = f"shot {tag}" if a.shots else ""
            closes = "\n".join(["hold B 4", "wait 25"] * 6)
            moves = "\n".join(f"hold {d} 20\nwait 20\npeek16 {px}\npeek16 {py}" for d in (away, "UP", "DOWN", "LEFT", "RIGHT"))
            walk_into = f"hold {dname} 60\nwait 60\n{shot}_walkinto\n{closes}" if a.shots else f"hold {dname} 60\nwait 60\n{closes}"
            script = f"""wait 700
peek16 {px}
peek16 {py}
hold {dname} 6
wait 20
hold A 4
wait 90
{shot}_text
{closes}
peek16 {vbl}
{walk_into}
{moves}
wait 30
peek16 {vbl}
{shot}_after"""
            out = run(a.rom, a.const, sx, sy, script, a.shots or Path("/tmp/sign_probe"))
            v = [int(x, 16) for x in re.findall(r"= (0x[0-9a-f]+)", out)]
            x0, y0, vb1 = v[0], v[1], v[2]
            pos = [(v[i], v[i + 1]) for i in range(3, 13, 2)]
            vb2 = v[13]
            alive = vb2 != vb1
            moved = any(p_ != (x0, y0) for p_ in pos)
            status = "OK" if alive and moved else ("CRASH" if not alive else "STUCK")
            results.append({"sign": b["script"], "at": (b["x"], b["y"]), "stand": (sx, sy), "face": dname,
                            "status": status, "pos": [(x0 - 7, y0 - 7)] + [(x - 7, y - 7) for x, y in pos],
                            "vblank": [vb1, vb2]})
            print(f"{status:5} {b['script']:40} stand={sx},{sy} face={dname:5} pos={results[-1]['pos']}")
    if a.json:
        a.json.write_text(json.dumps(results, indent=1))
    bad = [r for r in results if r["status"] != "OK"]
    print(f"{len(results) - len(bad)}/{len(results)} sign interactions OK")
    return int(bool(bad))


if __name__ == "__main__":
    sys.exit(main())
