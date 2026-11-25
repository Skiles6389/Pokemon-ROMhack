#!/usr/bin/env python3
"""Verify Route 202 Dawn/Lucas catch tutorial mirrors Emerald Wally / FRLG Old Man.

Checks (static script + source trace — no ROM required):
  1. Route202 DoCatch saves party, loads Wally Zigzagoon, starts CATCH_TUTORIAL, restores party
  2. StartRoute202CatchTutorial sets BATTLE_TYPE_CATCH_TUTORIAL and fixed Bidoof (no wild remap)
  3. Wally controller skips pre-ball attacks when IsRoute202CatchTutorial()
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> int:
    route = (REPO / "data/maps/Route202/scripts.inc").read_text()
    setup = (REPO / "src/battle_setup.c").read_text()
    wally = (REPO / "src/battle_controller_wally.c").read_text()

    # --- script sequence ---
    m = re.search(
        r"Route202_EventScript_DoCatch::(.*?)(?:Route202_EventScript_\w+::|\Z)",
        route,
        re.S,
    )
    if not m:
        fail("Route202_EventScript_DoCatch missing")
    block = m.group(1)
    for token in (
        "special SavePlayerParty",
        "special LoadWallyZigzagoon",
        "special StartRoute202CatchTutorial",
        "special LoadPlayerParty",
    ):
        if token not in block:
            fail(f"DoCatch missing `{token}` (Wally-style temp party required)")
    order = [block.find(t) for t in (
        "special SavePlayerParty",
        "special LoadWallyZigzagoon",
        "special StartRoute202CatchTutorial",
        "special LoadPlayerParty",
    )]
    if order != sorted(order):
        fail("DoCatch specials out of order (need Save → Zigzagoon → Tutorial → Load)")

    # --- C battle start ---
    fn = re.search(r"void StartRoute202CatchTutorial\(void\)\s*\{(.*?)^\}", setup, re.S | re.M)
    if not fn:
        fail("StartRoute202CatchTutorial missing")
    body = fn.group(1)
    if "BATTLE_TYPE_CATCH_TUTORIAL" not in body:
        fail("StartRoute202CatchTutorial must set BATTLE_TYPE_CATCH_TUTORIAL")
    if "SPECIES_BIDOOF" not in body:
        fail("StartRoute202CatchTutorial must create fixed SPECIES_BIDOOF (not wild table)")
    if "CreateMaleMon" not in body and "CreateRandomMon" not in body:
        fail("StartRoute202CatchTutorial must create opponent mon directly")
    if "Randomizer_Remap" in body:
        fail("catch tutorial must not call wild randomizer remap")

    # --- controller skips KO attacks ---
    if "IsRoute202CatchTutorial()" not in wally:
        fail("Wally controller must branch on IsRoute202CatchTutorial to skip Tackle KO")
    if "wallyBattleState = 3" not in wally and "wallyBattleState=3" not in wally:
        fail("Route 202 path must jump to ball-throw state (skip USE_MOVE attacks)")

    # Always-catch path still present
    scripts2 = (REPO / "data/battle_scripts_2.s").read_text()
    if "BattleScript_WallyBallThrow" not in scripts2:
        fail("BattleScript_WallyBallThrow missing")
    cmds = (REPO / "src/battle_script_commands.c").read_text()
    if "BATTLE_TYPE_CATCH_TUTORIAL" not in cmds or "BALL_3_SHAKES_SUCCESS" not in cmds:
        fail("CATCH_TUTORIAL must force successful ball shake")

    print("PASS catch_tutorial_verify: Route202 Wally/Old-Man style always-catch wired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
