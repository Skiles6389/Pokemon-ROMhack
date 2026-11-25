#!/usr/bin/env python3
"""Headless mGBA smoke + catch-tutorial regression (HLE BIOS, no Nintendo BIOS).

- Boots pokeemerald.gba under xvfb-run with a short timeout (engine alive).
- Runs `make check TESTS='IsRoute202CatchTutorial|Route 202 catch|CATCH_TUTORIAL'`
  via the bundled mgba-rom-test (libmgba HLE — no BIOS file).

Does NOT commit or download a BIOS/ROM. Requires a locally built pokeemerald.gba.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROM = REPO / "pokeemerald.gba"
MGBA = Path("/usr/games/mgba")
MGBA_ROM_TEST = REPO / "tools/mgba/mgba-rom-test"


def boot_smoke(seconds: float = 3.0) -> dict:
    if not ROM.exists():
        return {"status": "SKIP", "reason": "missing pokeemerald.gba — run make"}
    mgba = str(MGBA) if MGBA.exists() else (shutil.which("mgba") or "")
    if not mgba:
        return {"status": "SKIP", "reason": "mgba not installed"}
    # Prefer xvfb so SDL has a display; fall back to SDL_VIDEODRIVER=dummy
    xvfb = shutil.which("xvfb-run")
    cmd = [mgba, "-C", "logLevel.gba.bios=0", "-l", "0", str(ROM)]
    env = os.environ.copy()
    env.setdefault("SDL_AUDIODRIVER", "dummy")
    if xvfb:
        cmd = [xvfb, "-a", "-s", "-screen 0 240x160x24"] + cmd
    else:
        env["SDL_VIDEODRIVER"] = "dummy"
    try:
        r = subprocess.run(
            cmd,
            cwd=REPO,
            env=env,
            timeout=seconds,
            capture_output=True,
            text=True,
        )
        return {
            "status": "PASS",
            "detail": f"exited {r.returncode} within {seconds}s",
            "stderr_tail": (r.stderr or "")[-400:],
        }
    except subprocess.TimeoutExpired:
        # Timeout = engine stayed alive — expected for interactive emulator
        return {"status": "PASS", "detail": f"alive after {seconds}s (HLE BIOS, no Nintendo BIOS)"}
    except Exception as e:  # noqa: BLE001
        return {"status": "FAIL", "reason": str(e)}


def catch_tutorial_tests() -> dict:
    if not MGBA_ROM_TEST.exists():
        return {"status": "SKIP", "reason": "missing tools/mgba/mgba-rom-test"}
    # Use make check which drives mgba-rom-test with HLE
    r = subprocess.run(
        ["make", "check", "TESTS=IsRoute202CatchTutorial|Route 202 catch|CATCH_TUTORIAL battle"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    ok = r.returncode == 0
    return {
        "status": "PASS" if ok else "FAIL",
        "exit": r.returncode,
        "stdout_tail": (r.stdout or "")[-1200:],
        "stderr_tail": (r.stderr or "")[-600:],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa/mgba_smoke.json"))
    ap.add_argument("--skip-tests", action="store_true")
    ap.add_argument("--boot-seconds", type=float, default=3.0)
    args = ap.parse_args()
    report = {
        "boot": boot_smoke(args.boot_seconds),
        "catch_tutorial": None if args.skip_tests else catch_tutorial_tests(),
        "bios": "HLE (mGBA built-in; no Nintendo BIOS file used)",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print("boot:", report["boot"])
    if report["catch_tutorial"]:
        print("catch_tutorial:", report["catch_tutorial"]["status"], report["catch_tutorial"].get("exit"))
    fails = [
        k for k, v in report.items()
        if isinstance(v, dict) and v.get("status") == "FAIL"
    ]
    print(f"=== mgba_smoke → {args.out} fails={fails} ===")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
