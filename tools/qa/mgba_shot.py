#!/usr/bin/env python3
"""Headless mGBA screenshots at an exact map position (QA only, local only).

Needs a tool-only QA ROM: the boot/warp hooks live in tools/qa/mgba_shot/qa_shot_hooks.patch
and are never committed to src/.  Build it in a scratch worktree:
    git worktree add --detach /tmp/qashot HEAD && cd /tmp/qashot
    git apply tools/qa/mgba_shot/qa_shot_hooks.patch
    sed -i '1i #define QA_SHOT 1' src/new_game.c src/intro.c && make -j8
(boot skips intro/title; the new game warps to gQaShotTarget, patched below).  This wrapper copies
the ROM to a temp file, patches the 8 bytes after the "QASHOTv1" marker with
(group, num, x, y), runs tools/qa/mgba_shot/mgba_shot and converts PPM -> PNG.

  python3 tools/qa/mgba_shot.py ROM MAP_CONST X Y SCRIPT OUTDIR
SCRIPT lines: wait N | hold KEYS N | shot NAME | peek16 ADDR    (NAME without ext)
The ROM and screenshots are machine-local artefacts: never commit them.
"""
from __future__ import annotations

import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
HARNESS = REPO / "tools/qa/mgba_shot/mgba_shot"


def map_group_num(const: str, roots: list[Path]) -> tuple[int, int]:
    """(group, num) from the generated include/constants/map_groups.h."""
    hdr = next((r / "include/constants/map_groups.h" for r in roots if (r / "include/constants/map_groups.h").exists()), None)
    if hdr is None:
        raise SystemExit("include/constants/map_groups.h not generated (build the ROM first)")
    m = re.search(rf"\b{const}\s*=\s*\((\d+)\s*\|\s*\((\d+)\s*<<\s*8\)\)", hdr.read_text())
    if not m:
        raise SystemExit(f"{const} not in map_groups.h")
    return int(m.group(2)), int(m.group(1))


def build_harness() -> None:
    src = HARNESS.with_suffix(".c")
    if not HARNESS.exists() or HARNESS.stat().st_mtime < src.stat().st_mtime:
        subprocess.check_call(["gcc", "-O2", "-o", str(HARNESS), str(src), "-lmgba"])


def run(rom: Path, const: str, x: int, y: int, script: str, outdir: Path) -> str:
    build_harness()
    data = bytearray(rom.read_bytes())
    i = data.find(b"QASHOTv1")
    if i < 0:
        raise SystemExit("ROM was not built with QA_SHOT")
    g, n = map_group_num(const, [REPO, rom.resolve().parent])
    struct.pack_into("<4H", data, i + 8, g, n, x, y)
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        trom = Path(td) / "qa.gba"
        trom.write_bytes(data)
        lines = []
        for ln in script.strip().splitlines():
            p = ln.split()
            if p and p[0] == "shot":
                p[1] = str(Path(td) / (p[1] + ".ppm"))
            lines.append(" ".join(p))
        sp = Path(td) / "s.txt"
        sp.write_text("\n".join(lines) + "\n")
        out = subprocess.run([str(HARNESS), str(trom), str(sp)], capture_output=True, text=True, cwd=td, timeout=600)
        for ppm in Path(td).glob("*.ppm"):
            Image.open(ppm).save(outdir / (ppm.stem + ".png"))
    return out.stdout + out.stderr


if __name__ == "__main__":
    if len(sys.argv) != 7:
        raise SystemExit(__doc__)
    rom, const, x, y, script, outdir = sys.argv[1:]
    s = Path(script).read_text() if ("\n" not in script and ";" not in script and Path(script).is_file()) else script.replace(";", "\n")
    print(run(Path(rom), const, int(x), int(y), s, Path(outdir)))
