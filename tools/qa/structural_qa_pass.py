#!/usr/bin/env python3
"""One structural QA pass: render + run all audits + optional remediations.

Usage:
  python3 tools/qa/structural_qa_pass.py --pass 1 --fix
  python3 tools/qa/structural_qa_pass.py --pass 2 --focus pass2 --fix
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SINNOH = REPO / "tools/sinnoh_maps"

AUDITS = [
    ("building_integrity_audit.py", "building"),
    ("visual_object_audit.py", "visual"),
    ("collision_audit.py", "collision"),
    ("city_door_warp_audit.py", "city_door_warp"),
    ("script_npc_exit_audit.py", "npc_exit"),
    ("structural_extra_audit.py", "structural_extra"),
]

REMEDIATIONS_PASS = {
    1: [
        ["remediate_structural_pass1.py"],
        ["rebuild_twinleaf_and_water.py"],
        ["rebuild_jubilife_city.py"],
        ["remediate_structural_pass1.py"],  # door-mat coll after rebuilds
    ],
    2: [
        ["remediate_paths.py"],
        ["remediate_map_collision_visual.py"],
        ["remediate_structural_pass1.py"],
    ],
    3: [
        ["remediate_visual_water.py"],
        ["remediate_structural_pass1.py"],
    ],
    4: [
        ["remediate_city_doors.py"],
        ["remediate_building_stamps.py"],
        ["remediate_structural_pass1.py"],
    ],
    5: [
        ["remediate_visual_water.py"],
        ["remediate_building_stamps.py"],
        ["rebuild_twinleaf_and_water.py"],
        ["rebuild_jubilife_city.py"],
        ["remediate_structural_pass1.py"],
    ],
}


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, **kw)


def run_audit(script: str, extra: list[str] | None = None) -> dict:
    path = SINNOH / script
    cmd = [sys.executable, str(path)] + (extra or [])
    r = run(cmd)
    # Find report
    report = path.with_name(path.stem + "_report.json")
    if script == "city_door_warp_audit.py":
        report = SINNOH / "city_door_warp_audit_report.json"
    if script == "script_npc_exit_audit.py":
        report = SINNOH / "script_npc_exit_audit_report.json"
    data = json.loads(report.read_text()) if report.exists() else {}
    fail = data.get("fail", 0)
    warn = data.get("warn", data.get("skip", 0))
    passed = data.get("pass", 0)
    if "results" in data and fail == 0 and passed == 0:
        fail = sum(1 for x in data["results"] if x.get("status") == "FAIL")
        passed = sum(1 for x in data["results"] if x.get("status") == "PASS")
        warn = sum(1 for x in data["results"] if x.get("status") in ("WARN", "SKIP"))
    fails = [x for x in data.get("results", []) if x.get("status") == "FAIL"]
    print(f"  {script}: FAIL={fail} PASS={passed} WARN/SKIP={warn} exit={r.returncode}")
    if r.stderr and r.returncode:
        print(r.stderr[-500:])
    return {
        "script": script,
        "fail": fail,
        "pass": passed,
        "warn": warn,
        "exit": r.returncode,
        "fails": [
            {"name": f.get("name"), "issues": (f.get("issues") or [])[:6]}
            for f in fails[:30]
        ],
        "stdout_tail": (r.stdout or "")[-800:],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_n", type=int, required=True)
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--skip-render", action="store_true")
    ap.add_argument("--focus", default="all", help="structural_extra focus")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    out = args.out or (REPO / f"tools/qa/out/structural_pass_{args.pass_n}.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    remediations_run = []
    if args.fix:
        for rem in REMEDIATIONS_PASS.get(args.pass_n, []):
            script = SINNOH / rem[0]
            if not script.exists():
                print(f"skip missing remediator {script}")
                continue
            r = run([sys.executable, str(script)] + rem[1:])
            remediations_run.append({
                "script": rem[0],
                "exit": r.returncode,
                "stdout_tail": (r.stdout or "")[-600:],
            })
            print(f"remediate {rem[0]} exit={r.returncode}")
            if r.stdout:
                print(r.stdout[-400:])

    if not args.skip_render:
        r = run([sys.executable, str(HERE / "render_maps.py"), "--out", str(out.parent / "renders")])
        print(f"render exit={r.returncode}")
        print((r.stdout or "")[-300:])

    audit_results = []
    for script, _key in AUDITS:
        extra = []
        if script == "structural_extra_audit.py":
            extra = ["--focus", args.focus]
        audit_results.append(run_audit(script, extra))

    total_fail = sum(a["fail"] for a in audit_results)
    summary = {
        "pass": args.pass_n,
        "focus": args.focus,
        "total_fail": total_fail,
        "audits": audit_results,
        "remediations": remediations_run,
        "counts": {a["script"]: {"fail": a["fail"], "pass": a["pass"], "warn": a["warn"]} for a in audit_results},
    }
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"=== structural QA pass {args.pass_n}/5: total_fail={total_fail} → {out} ===")
    return 0  # always 0 so the driver can commit; fail counts live in JSON


if __name__ == "__main__":
    raise SystemExit(main())
