#!/usr/bin/env python3
"""Platinum-shape mapgrid compiler (General + Mauville metatiles).

Used for .grid files that declare ``@compiler platinum``. The grids only hold
derived shapes (one character per tile); every metatile comes from Emerald's
own General / Mauville tilesets.

Characters
  T tree (2x2 autotiled)      . grass        , tall grass    f flowers
  = path (3x3 autotiled)      ~ water (shore autotiled, surfable)
  L south ledge   < west ledge   > east ledge   F wooden fence
  b fenced flower bed (solid) S sign/mailbox (bg sign, @sign order)
  W walk-in forest exit warp (dark tile, @warp order)
  # R solid (becomes tree, or ledge corner beside a ledge)
  stamp letters: building door anchors declared with @stamp

Outputs: data/layouts/<Map>/map.bin + border.bin, the layouts.json entry,
and map.json connections / warp_events / sign bg_events (object events,
coord events and non-sign bg events such as hidden items are preserved).
"""
from __future__ import annotations

import heapq
import json
import struct
import sys
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

GRASS = 0x001
TALL = 0x00D
FLOWER = 0x004
SIGN = 0x003
SAND = 0x121
EXIT_DARK = 0x2D3        # Mauville dark doorway, MB_NON_ANIMATED_DOOR (walk-in warp)
FENCE_H = 0x291
FENCE_L = 0x288          # post on the left half (left side of an enclosure)
FENCE_R = 0x28A          # post on the right half (right side of an enclosure)
BED = (0x20A, 0x20C, 0x20B, 0x20D, 0x20E, 0x20F)
SHORE_S = 0x002
SHRUB = 0x016          # solid round shrub (beside buildings)
TREE_BORDER = (0x1D4, 0x1D5, 0x1DC, 0x1DD)


def cell(mt: int, coll: int, elev: int = 3) -> int:
    return (mt & 0x3FF) | ((coll & 3) << 10) | ((elev & 0xF) << 12)


sys.path.insert(0, str(REPO))
from tools.sinnoh_maps import emerald_building_stamps as _ebs  # noqa: E402


def _from_catalog(st: dict) -> dict:
    return dict(dx=st["door_dx"], dy=st["door_dy"], door=st["door_mt"], t=st["tiles"])


STAMPS = {
    "GEN_HOUSE4": _from_catalog(_ebs.GENERAL_HOUSE_4),
    "GEN_HOUSE5T": _from_catalog(_ebs.GENERAL_HOUSE_5T),
    "MAUVILLE_HOUSE4": _from_catalog(_ebs.MAUVILLE_HOUSE_4),
    "MAUVILLE_HOUSE5T": _from_catalog(_ebs.MAUVILLE_HOUSE_5T),
    "VERDANTURF_HOUSE4": _from_catalog(_ebs.VERDANTURF_HOUSE_4),
    # Rock mound with a cave mouth (door 0x0A7, MB_NON_ANIMATED_DOOR), General primary
    "CAVE_MOUND": dict(dx=3, dy=4, door=0x0A7, t=[
        [0x068, 0x069, 0x069, 0x069, 0x069, 0x069, 0x06A],
        [0x070, 0x071, 0x071, 0x071, 0x071, 0x071, 0x072],
        [0x070, 0x071, 0x071, 0x071, 0x071, 0x071, 0x072],
        [0x070, 0x07B, 0x07C, 0x07C, 0x07C, 0x07D, 0x072],
        [0x078, 0x079, 0x079, 0x0A7, 0x079, 0x079, 0x07A]]),
}

WALKABLE = set(".,=f:W")


def parse(path: Path):
    hdr = {"stamps": [], "warps": [], "signs": [], "conns": []}
    rows: list[str] = []
    ingrid = False
    for line in Path(path).read_text().splitlines():
        if ingrid:
            if line.strip():
                rows.append(line.rstrip("\n"))
            continue
        if not line.startswith("@"):
            continue
        p = line[1:].split("#")[0].split()
        k = p[0].lower()
        if k == "grid":
            ingrid = True
        elif k == "stamp":
            hdr["stamps"].append(dict(char=p[1], stamp=p[2], dest=p[3], wid=p[4]))
        elif k == "warp":
            hdr["warps"].append(dict(dest=p[1], wid=p[2]))
        elif k == "sign":
            hdr["signs"].append(p[1])
        elif k == "connection":
            hdr["conns"].append(dict(direction=p[1], map=p[2], offset=int(p[3])))
        else:
            hdr[k] = p[1]
    return hdr, rows


def tile_trees(ch, W, H):
    """Most-constrained-first 2x2 tiling of T cells.

    Blocks may only extend past the map edge where the off-map half matches the
    layout border (2x2 tree border: left/top halves sit on even coordinates),
    so the forest continues seamlessly into the border.
    """
    def is_t(x, y):
        return ch[y][x] == "T"

    owner: dict[tuple[int, int], tuple[str, str]] = {}

    def block_ok(bx, by):
        for a in (0, 1):
            for b in (0, 1):
                X, Y = bx + b, by + a
                if 0 <= X < W and 0 <= Y < H:
                    if not is_t(X, Y) or (X, Y) in owner:
                        return False
                else:
                    # off-map: must match border parity
                    if (X & 1) != b or (Y & 1) != a:
                        return False
                    if not (-1 <= X <= W and -1 <= Y <= H):
                        return False
        return True

    def options(x, y):
        return [(bx, by) for bx in (x - 1, x) for by in (y - 1, y) if block_ok(bx, by)]

    heap = [(len(options(x, y)), y, x) for y in range(H) for x in range(W) if is_t(x, y)]
    heapq.heapify(heap)
    while heap:
        sc, y, x = heapq.heappop(heap)
        if (x, y) in owner:
            continue
        opts = options(x, y)
        if len(opts) != sc:
            if opts:
                heapq.heappush(heap, (len(opts), y, x))
            continue
        if not opts:
            continue

        def cost(b):
            bx, by = b
            return sum(len(options(bx + bb, by + a)) for a in (0, 1) for bb in (0, 1)
                       if 0 <= bx + bb < W and 0 <= by + a < H)

        bx, by = min(opts, key=cost)
        for a, part in ((0, "T"), (1, "B")):
            for b, side in ((0, "L"), (1, "R")):
                X, Y = bx + b, by + a
                if 0 <= X < W and 0 <= Y < H:
                    owner[(X, Y)] = (side, part)
        for a in range(-1, 3):
            for bb in range(-1, 3):
                X2, Y2 = bx + bb, by + a
                if 0 <= X2 < W and 0 <= Y2 < H and is_t(X2, Y2) and (X2, Y2) not in owner:
                    heapq.heappush(heap, (len(options(X2, Y2)), Y2, X2))
    tree = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if is_t(x, y):
                tree[y][x] = owner.get((x, y), "S")
    return tree


def compile_grid(path: Path):
    hdr, rows = parse(path)
    H = len(rows)
    W = len(rows[0])
    assert all(len(r) == W for r in rows), f"{path}: ragged rows"
    assert int(hdr.get("width", W)) == W and int(hdr.get("height", H)) == H, f"{path}: size mismatch"
    ch = [list(r) for r in rows]
    M = [[GRASS] * W for _ in range(H)]
    C = [[0] * W for _ in range(H)]
    E = [[3] * W for _ in range(H)]
    done = [[False] * W for _ in range(H)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    warps = []
    # 1) building / cave stamps (door on the anchor letter)
    for s in hdr["stamps"]:
        st = STAMPS[s["stamp"]]
        found = 0
        for y in range(H):
            for x in range(W):
                if ch[y][x] != s["char"]:
                    continue
                found += 1
                tx, ty = x - st["dx"], y - st["dy"]
                for sy, r in enumerate(st["t"]):
                    for sx, mt in enumerate(r):
                        X, Y = tx + sx, ty + sy
                        assert inb(X, Y), (path, s, X, Y)
                        door = (sx, sy) == (st["dx"], st["dy"])
                        M[Y][X] = mt
                        C[Y][X] = 0 if door else 1
                        E[Y][X] = 0 if door else 3
                        done[Y][X] = True
                        ch[Y][X] = "@" if not door else "%"
                warps.append(dict(x=x, y=y, elevation=0, dest_map=s["dest"], dest_warp_id=str(s["wid"])))
        assert found == 1, f"{path}: stamp {s['char']} found {found} times"
    # leftover solids: ledge corner beside a ledge, dark forest beside a walk-in
    # exit, shrub beside a building, else tree
    for y in range(H):
        for x in range(W):
            if ch[y][x] in "#R":
                near = lambda chars, d: any(inb(x + a, y + b) and ch[y + b][x + a] in chars for a, b in d)
                if near("L", ((-1, 0), (1, 0))):
                    ch[y][x] = "L"
                elif near("W", ((0, -1), (0, 1))):
                    ch[y][x] = "X"
                elif near("@%", ((-1, 0), (1, 0), (0, -1), (0, 1))):
                    ch[y][x] = "K"
                else:
                    ch[y][x] = "T"
    # 2) trees
    tree = tile_trees(ch, W, H)

    def tt(x, y):
        if not inb(x, y):
            return "OOB"
        return tree[y][x]

    singles = 0
    for y in range(H):
        for x in range(W):
            k = tree[y][x]
            if k is None:
                continue
            C[y][x] = 1
            done[y][x] = True
            if k == "S":
                singles += 1
                M[y][x] = 0x0C6 if tt(x, y + 1) is not None else 0x016
                continue
            side, part = k
            open_side = (tt(x - 1, y) is None) if side == "L" else (tt(x + 1, y) is None)
            if part == "T":
                M[y][x] = (0x1D6 if open_side else 0x1D4) if side == "L" else (0x1D7 if open_side else 0x1D5)
            else:
                below_open = tt(x, y + 1) is None
                if side == "L":
                    M[y][x] = (0x1E6 if open_side else 0x1E4) if below_open else (0x1DE if open_side else 0x1DC)
                else:
                    M[y][x] = (0x1E7 if open_side else 0x1E5) if below_open else (0x1DF if open_side else 0x1DD)

    # 3) terrain
    def water(x, y):
        return (not inb(x, y)) or ch[y][x] == "~"

    def pathc(x, y):
        return inb(x, y) and ch[y][x] == "="

    for y in range(H):
        for x in range(W):
            if done[y][x]:
                continue
            c = ch[y][x]
            if c in ". ":
                M[y][x] = GRASS
            elif c == "W":
                M[y][x] = EXIT_DARK
            elif c == "X":
                M[y][x] = EXIT_DARK
                C[y][x] = 1
            elif c == "K":
                M[y][x] = SHRUB
                C[y][x] = 1
            elif c == ",":
                M[y][x] = TALL
            elif c == "f":
                M[y][x] = FLOWER
            elif c == ":":
                M[y][x] = SAND
            elif c == "S":
                M[y][x] = SIGN
                C[y][x] = 1
            elif c == "b":
                M[y][x] = BED[(x + 3 * y) % 6]
                C[y][x] = 1
            elif c == "F":
                horiz = (inb(x - 1, y) and ch[y][x - 1] == "F") or (inb(x + 1, y) and ch[y][x + 1] == "F")
                if horiz:
                    M[y][x] = FENCE_H
                else:
                    inside_left = inb(x - 1, y) and ch[y][x - 1] == "b"
                    M[y][x] = FENCE_R if inside_left else FENCE_L
                C[y][x] = 1
            elif c == "=":
                n, s_, w, e = pathc(x, y - 1), pathc(x, y + 1), pathc(x - 1, y), pathc(x + 1, y)
                row = 0 if not n else (2 if not s_ else 1)
                col = 0 if not w else (2 if not e else 1)
                if not n and not s_:
                    row = 1
                if not w and not e:
                    col = 1
                M[y][x] = [[0x118, 0x119, 0x11A], [0x120, 0x121, 0x122], [0x128, 0x129, 0x12A]][row][col]
            elif c == "L":
                left = inb(x - 1, y) and ch[y][x - 1] == "L"
                right = inb(x + 1, y) and ch[y][x + 1] == "L"
                M[y][x] = 0x087 if (left and right) else (0x0D5 if right else (0x0D6 if left else 0x087))
                C[y][x] = 1
            elif c in "<>":
                up = inb(x, y - 1) and ch[y - 1][x] == c
                M[y][x] = (0x085 if up else 0x0FE) if c == "<" else (0x086 if up else 0x0FF)
                C[y][x] = 1
            elif c == "~":
                E[y][x] = 1
                n, s_, w, e = water(x, y - 1), water(x, y + 1), water(x - 1, y), water(x + 1, y)
                if not n and not w:
                    mt = 0x0B0
                elif not n and not e:
                    mt = 0x0B2
                elif not n:
                    mt = 0x0B1
                elif not w:
                    mt = 0x0B8
                elif not e:
                    mt = 0x0BA
                elif not water(x - 1, y - 1):
                    mt = 0x0C0
                elif not water(x + 1, y - 1):
                    mt = 0x0C2
                else:
                    mt = 0x0A1
                M[y][x] = mt
            else:
                raise SystemExit(f"{path}: unknown char {c!r} at {x},{y}")
            done[y][x] = True

    # 4) tree caps on grass above canopies, water-over-tree shores, grass shore below water
    caps = 0
    for y in range(H):
        for x in range(W):
            k = tree[y][x]
            if isinstance(k, tuple) and k[1] == "T" and inb(x, y - 1):
                if ch[y - 1][x] == "." and M[y - 1][x] == GRASS:
                    M[y - 1][x] = 0x1CE if k[0] == "L" else 0x1CF
                    caps += 1
                if ch[y - 1][x] == "~" and M[y - 1][x] in (0x0A1, 0x0C0, 0x0C2):
                    M[y - 1][x] = 0x1FE if k[0] == "L" else 0x1FF
                    M[y][x] = 0x1FC if k[0] == "L" else 0x1FD
            if ch[y][x] == "~" and inb(x, y + 1) and ch[y + 1][x] == "." and M[y + 1][x] == GRASS:
                M[y + 1][x] = SHORE_S

    # 5) warps (row-major W after stamps) and signs (row-major S)
    wi = 0
    signs = []
    for y in range(H):
        for x in range(W):
            if ch[y][x] == "W":
                d = hdr["warps"][wi]
                wi += 1
                warps.append(dict(x=x, y=y, elevation=0, dest_map=d["dest"], dest_warp_id=str(d["wid"])))
            elif ch[y][x] == "S":
                signs.append((x, y))
    assert wi == len(hdr["warps"]), f"{path}: {wi} W tiles vs {len(hdr['warps'])} @warp lines"
    assert len(signs) == len(hdr["signs"]), f"{path}: {len(signs)} S tiles vs {len(hdr['signs'])} @sign lines"
    bg = [dict(type="sign", x=x, y=y, elevation=0, player_facing_dir="BG_EVENT_PLAYER_FACING_ANY", script=s)
          for (x, y), s in zip(signs, hdr["signs"])]
    grid = [[cell(M[y][x], C[y][x], E[y][x]) for x in range(W)] for y in range(H)]
    walk = [[ch[y][x] in WALKABLE or ch[y][x] == "%" for x in range(W)] for y in range(H)]
    return dict(hdr=hdr, W=W, H=H, grid=grid, warps=warps, signs=bg, walk=walk,
                stats=dict(singles=singles, caps=caps))


def validate(res) -> list[str]:
    W, H, walk, grid = res["W"], res["H"], res["walk"], res["grid"]
    fails = []
    for y in range(H):
        for x in range(W):
            if grid[y][x] & 0x3FF == 0:
                fails.append(f"void metatile at {x},{y}")
    for w in res["warps"]:
        if not walk[w["y"]][w["x"]]:
            fails.append(f"warp at {w['x']},{w['y']} not walkable")
    if res["stats"]["singles"]:
        fails.append(f"{res['stats']['singles']} single tree tiles (bush fallback)")
    # every walkable tile reachable from a warp or a connection edge
    seeds = [(w["x"], w["y"]) for w in res["warps"]]
    for c in res["hdr"]["conns"]:
        d = c["direction"]
        for i in range(max(W, H)):
            pt = {"up": (i, 0), "down": (i, H - 1), "left": (0, i), "right": (W - 1, i)}[d]
            if 0 <= pt[0] < W and 0 <= pt[1] < H and walk[pt[1]][pt[0]]:
                seeds.append(pt)
    seen = set(seeds)
    q = deque(seeds)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            X, Y = x + dx, y + dy
            if 0 <= X < W and 0 <= Y < H and walk[Y][X] and (X, Y) not in seen:
                seen.add((X, Y))
                q.append((X, Y))
    # ledges are one-way; count tiles past a ledge as reachable by jumping
    changed = True
    while changed:
        changed = False
        for y in range(H):
            for x in range(W):
                if (x, y) in seen:
                    continue
                if not walk[y][x]:
                    continue
                for dx, dy in ((0, 2), (2, 0), (-2, 0), (0, -2)):
                    if (x - dx, y - dy) in seen:
                        seen.add((x, y))
                        q.append((x, y))
                        changed = True
                        break
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                X, Y = x + dx, y + dy
                if 0 <= X < W and 0 <= Y < H and walk[Y][X] and (X, Y) not in seen:
                    seen.add((X, Y))
                    q.append((X, Y))
    res["unreachable"] = sorted((x, y) for y in range(H) for x in range(W) if walk[y][x] and (x, y) not in seen)
    return fails


def write(res) -> None:
    hdr, W, H, grid = res["hdr"], res["W"], res["H"], res["grid"]
    name = hdr["name"]
    out = REPO / "data/layouts" / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "map.bin").write_bytes(b"".join(struct.pack("<H", v) for r in grid for v in r))
    (out / "border.bin").write_bytes(b"".join(struct.pack("<H", cell(m, 1)) for m in TREE_BORDER))
    lj = REPO / "data/layouts/layouts.json"
    J = json.loads(lj.read_text())
    ent = next((L for L in J["layouts"] if L.get("id") == hdr["layout"]), None)
    if ent is None:
        ent = dict(id=hdr["layout"], name=name + "_Layout", layout_version="emerald")
        J["layouts"].append(ent)
    ent.update(width=W, height=H, primary_tileset=hdr.get("primary", "gTileset_General"),
               secondary_tileset=hdr.get("secondary", "gTileset_Mauville"),
               border_filepath=f"data/layouts/{name}/border.bin",
               blockdata_filepath=f"data/layouts/{name}/map.bin")
    lj.write_text(json.dumps(J, indent=2) + "\n")
    mj = REPO / "data/maps" / name / "map.json"
    m = json.loads(mj.read_text())
    m["layout"] = hdr["layout"]
    if hdr["conns"]:
        m["connections"] = [dict(map=c["map"], offset=c["offset"], direction=c["direction"]) for c in hdr["conns"]]
    else:
        m["connections"] = None
    m["warp_events"] = res["warps"]
    m["bg_events"] = [e for e in (m.get("bg_events") or []) if e.get("type") != "sign"] + res["signs"]
    mj.write_text(json.dumps(m, indent=2) + "\n")


def compile_one(path: Path, check_only: bool = False) -> int:
    res = compile_grid(path)
    fails = validate(res)
    name = res["hdr"]["name"]
    if fails:
        print(f"FAIL {name}:")
        for f in fails:
            print(" -", f)
        return 1
    if not check_only:
        write(res)
    note = f" surf/one-way-only tiles={len(res['unreachable'])}" if res["unreachable"] else ""
    print(f"OK {name} {res['W']}x{res['H']} warps={len(res['warps'])} signs={len(res['signs'])} "
          f"caps={res['stats']['caps']}{note}")
    return 0


if __name__ == "__main__":
    rc = 0
    check = "--check" in sys.argv
    for p in [a for a in sys.argv[1:] if a != "--check"]:
        rc |= compile_one(Path(p), check)
    raise SystemExit(rc)
