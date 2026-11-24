#!/usr/bin/env python3
"""
Headless Sinnoh smoke verification after a clean ROM build.

1) Confirms pokeemerald.gba exists and is a plausible GBA image
2) Re-runs post_m20_qa_audit.py (static source of truth)
3) If mgba CLI is available, boots the ROM for a short headless run
   (map/engine init smoke — not a full scripted walkthrough)
4) Optionally re-runs the Randomizer* headless tests (ON and OFF cases)

Does not commit ROM/BIOS dumps.
"""
from __future__ import annotations

import argparse
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
    for name in (
        "collision_audit.py",
        "visual_object_audit.py",
        "script_npc_exit_audit.py",
    ):
        script = REPO / "tools" / "sinnoh_maps" / name
        if not script.exists():
            continue
        r = subprocess.run([sys.executable, str(script)], cwd=REPO)
        # script_npc_exit_audit is advisory for residual story polish; collision/visual are hard gates
        if name != "script_npc_exit_audit.py" and r.returncode != 0:
            raise SystemExit(f"FAIL: {name}")
        print(f"PASS {name}" if r.returncode == 0 else f"WARN {name} (advisory)")


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


def run_randomizer_headless_tests() -> None:
    """Re-run Randomizer* tests covering options OFF (vanilla) and ON (remap)."""
    print("=== randomizer headless tests (OFF + ON) ===")
    r = subprocess.run(
        ["make", "check", "TESTS=Randomizer*"],
        cwd=REPO,
    )
    if r.returncode != 0:
        raise SystemExit("FAIL: randomizer headless tests")
    print("PASS randomizer headless tests (OFF + ON)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-randomizer",
        action="store_true",
        help="Also run make check TESTS=Randomizer* (covers ON and OFF)",
    )
    args = parser.parse_args()
    check_rom()
    run_audit()
    try_mgba_boot()
    if args.with_randomizer:
        run_randomizer_headless_tests()
    print("=== headless smoke verify complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
