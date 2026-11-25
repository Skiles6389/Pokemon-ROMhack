#!/usr/bin/env python3
"""Run visual/collision/city-door audits and summarize issues for QA report."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

AUDITS = [
    ("visual_object_audit.py", "visual"),
    ("collision_audit.py", "collision"),
    ("city_door_warp_audit.py", "city_door_warp"),
]


def run_audit(script: str) -> dict:
    path = REPO / "tools/sinnoh_maps" / script
    r = subprocess.run([sys.executable, str(path)], cwd=REPO, capture_output=True, text=True)
    report_path = path.with_name(path.stem + "_report.json")
    # city_door uses city_door_warp_audit_report.json
    if script == "city_door_warp_audit.py":
        report_path = REPO / "tools/sinnoh_maps/city_door_warp_audit_report.json"
    data = {}
    if report_path.exists():
        data = json.loads(report_path.read_text())
    fails = [x for x in data.get("results", []) if x.get("status") == "FAIL"]
    return {
        "script": script,
        "exit": r.returncode,
        "fail": data.get("fail", len(fails)),
        "warn": data.get("warn", 0),
        "fails": fails[:40],
        "stdout_tail": (r.stdout or "")[-1500:],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("/tmp/sinnoh_qa/auto_review.json"))
    args = ap.parse_args()
    results = [run_audit(s) for s, _ in AUDITS]
    total_fail = sum(r["fail"] for r in results)
    out = {
        "results": results,
        "total_fail": total_fail,
        "ok": total_fail == 0,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    for r in results:
        print(f"{r['script']}: fail={r['fail']} warn={r.get('warn')} exit={r['exit']}")
    print(f"=== auto_review total_fail={total_fail} → {args.out} ===")
    return 1 if total_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
