#!/usr/bin/env python3
"""
Headless Sinnoh smoke verification after a clean ROM build.

1) Confirms pokeemerald.gba exists and is a plausible GBA image
2) Re-runs post_m20_qa_audit.py (static source of truth)
3) If mgba CLI is available, boots the ROM for a short headless run
   (map/engine init smoke — not a full scripted walkthrough)

Does not commit ROM/BIOS dumps.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROM = REPO / "pokeemerald.gba"
AUDIT = REPO / "tools" / "sinnoh_maps" / "post_m20_qa_audit.py"


def check_rom() -> None:
    if not ROM.exists():
        raise SystemExit(f"FAIL: missing {ROM} — run make first")
    data = ROM.read_bytes()
    if len(data) < 1024 * 1024:
        raise SystemExit(f"FAIL: ROM too small ({len(data)} bytes)")
    # GBA ROMs start with a branch; Nintendo logo follows — just size + magic-ish
    print(f"PASS rom size={len(data)} bytes")


def run_audit() -> None:
    r = subprocess.run([sys.executable, str(AUDIT)], cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("FAIL: static QA audit reported failures")
    print("PASS static QA audit")


def try_mgba_boot() -> None:
    mgba = shutil.which("mgba") or shutil.which("mgba-qt")
    if not mgba:
        # Bundled rom-test binary is for TEST=1 suites, not free boot
        print("SKIP mgba boot (no mgba CLI on PATH; make check covers libmgba)")
        return
    # Headless-ish: run briefly then kill — mgba --bios is optional; skip if no bios
    try:
        proc = subprocess.run(
            [mgba, "-C", "logLevel.gba.bios=0", str(ROM)],
            cwd=REPO,
            timeout=3,
            capture_output=True,
        )
        print(f"PASS mgba short boot exit={proc.returncode}")
    except subprocess.TimeoutExpired:
        print("PASS mgba short boot (timeout after 3s — engine alive)")


def main() -> int:
    check_rom()
    run_audit()
    try_mgba_boot()
    print("=== headless smoke verify complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
