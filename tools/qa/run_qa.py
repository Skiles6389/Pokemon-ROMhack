#!/usr/bin/env python3
"""Run the full Sinnoh visual + playtest QA pipeline.

Writes artifacts under --out (default /tmp/sinnoh_qa). Large PNGs are for
CI artifacts / PR description — do not commit them.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# Priority maps Chris cares about for visual review + PR screenshots
PRIORITY = [
    "TwinleafTown", "Route201", "SandgemTown", "Route202",
    "JubilifeCity", "Route203", "OreburghCity", "LakeVerity",
]


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=REPO).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa"))
    ap.add_argument("--skip-mgba", action="store_true")
    ap.add_argument("--skip-renders", action="store_true")
    ap.add_argument("--priority-only", action="store_true",
                    help="Only render PRIORITY early-game maps (faster)")
    ap.add_argument("--copy-artifacts", type=Path, default=Path("/opt/cursor/artifacts"),
                    help="Copy key contact sheets / playtest shots here for the PR")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    rc = 0
    only = PRIORITY if args.priority_only else None

    if not args.skip_renders:
        cmd = [sys.executable, str(HERE / "render_maps.py"), "--out", str(args.out / "renders")]
        if only:
            cmd += ["--only", *only]
        rc |= run(cmd)

        cmd = [sys.executable, str(HERE / "platinum_ref.py"), "--out", str(args.out / "platinum_ref")]
        if only:
            cmd += ["--only", *[n for n in only if n != "LakeVerity"]]
        rc |= run(cmd)

        cmd = [
            sys.executable, str(HERE / "contact_sheets.py"),
            "--renders", str(args.out / "renders"),
            "--plat", str(args.out / "platinum_ref"),
            "--out", str(args.out / "contact"),
        ]
        if only:
            cmd += ["--only", *[n for n in only if n != "LakeVerity"]]
        rc |= run(cmd)

    rc |= run([sys.executable, str(HERE / "auto_review.py"), "--out", str(args.out / "auto_review.json")])
    rc |= run([sys.executable, str(HERE / "early_game_playtest.py"), "--out", str(args.out / "playtest")])

    mgba_rep = None
    if not args.skip_mgba:
        code = run([
            sys.executable, str(HERE / "mgba_smoke.py"),
            "--out", str(args.out / "mgba_smoke.json"),
            "--skip-tests",  # full make check is slow; run catch verify via playtest
        ])
        # Also re-run catch_tutorial_verify explicitly
        verify = REPO / "tools/sinnoh_maps/catch_tutorial_verify.py"
        if verify.exists():
            run([sys.executable, str(verify)])
        rc |= code
        if (args.out / "mgba_smoke.json").exists():
            mgba_rep = json.loads((args.out / "mgba_smoke.json").read_text())

    auto = {}
    if (args.out / "auto_review.json").exists():
        auto = json.loads((args.out / "auto_review.json").read_text())
    play = {}
    if (args.out / "playtest/playtest_report.json").exists():
        play = json.loads((args.out / "playtest/playtest_report.json").read_text())

    summary = {
        "auto_review_fail": auto.get("total_fail", -1),
        "playtest_fail": play.get("fail", -1),
        "playtest_pass": play.get("pass", -1),
        "playtest_issues": play.get("issues", []),
        "mgba": mgba_rep,
        "out": str(args.out),
        "priority_maps": PRIORITY,
    }
    (args.out / "report.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Copy key artifacts for the PR description
    if args.copy_artifacts:
        args.copy_artifacts.mkdir(parents=True, exist_ok=True)
        for src_name, dst_name in [
            ("contact/early_game_montage.png", "qa_early_game_montage.png"),
            ("contact/JubilifeCity_contact.png", "qa_jubilife_contact.png"),
            ("contact/TwinleafTown_contact.png", "qa_twinleaf_contact.png"),
            ("playtest/jubilife.png", "qa_playtest_jubilife.png"),
            ("playtest/twinleaf_new_game_twinleaf.png", "qa_playtest_twinleaf.png"),
            ("report.json", "qa_report.json"),
        ]:
            # playtest labels use label field
            pass
        copies = [
            (args.out / "contact/early_game_montage.png", "qa_early_game_montage.png"),
            (args.out / "contact/JubilifeCity_contact.png", "qa_jubilife_contact.png"),
            (args.out / "contact/TwinleafTown_contact.png", "qa_twinleaf_contact.png"),
            (args.out / "playtest/jubilife.png", "qa_playtest_jubilife.png"),
            (args.out / "playtest/new_game_twinleaf.png", "qa_playtest_twinleaf.png"),
            (args.out / "playtest/sandgem.png", "qa_playtest_sandgem.png"),
            (args.out / "playtest/oreburgh.png", "qa_playtest_oreburgh.png"),
            (args.out / "report.json", "qa_report.json"),
        ]
        for src, dst in copies:
            if src.exists():
                shutil.copy2(src, args.copy_artifacts / dst)
                print("copied", dst)

    print(json.dumps({k: summary[k] for k in (
        "auto_review_fail", "playtest_fail", "playtest_pass"
    )}, indent=2))
    return 1 if summary["auto_review_fail"] or summary["playtest_fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
