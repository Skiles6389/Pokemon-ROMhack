#!/usr/bin/env python3
"""Report free trailing 0xFF bytes in the built pokeemerald.gba ROM."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_ROM = REPO / "pokeemerald.gba"
RESERVE_BYTES = 1_500_000  # 1.5 MiB never-spend reserve (see docs/rom_budget.md)


def free_trailing_ff(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    n = 0
    for b in reversed(data):
        if b != 0xFF:
            break
        n += 1
    return len(data), n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rom", nargs="?", type=Path, default=DEFAULT_ROM)
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    ap.add_argument(
        "--require-reserve",
        action="store_true",
        help=f"Exit 1 if free space drops below {RESERVE_BYTES} bytes",
    )
    args = ap.parse_args()
    if not args.rom.is_file():
        print(f"ROM not found: {args.rom}", file=sys.stderr)
        return 2
    size, free = free_trailing_ff(args.rom)
    spendable = max(0, free - RESERVE_BYTES)
    if args.json:
        import json

        print(
            json.dumps(
                {
                    "rom": str(args.rom),
                    "size_bytes": size,
                    "free_ff_bytes": free,
                    "free_ff_mib": round(free / 1024 / 1024, 3),
                    "reserve_bytes": RESERVE_BYTES,
                    "spendable_bytes": spendable,
                    "spendable_mib": round(spendable / 1024 / 1024, 3),
                },
                indent=2,
            )
        )
    else:
        print(f"ROM:       {args.rom}")
        print(f"Size:      {size:,} bytes ({size / 1024 / 1024:.2f} MiB)")
        print(f"Free 0xFF: {free:,} bytes ({free / 1024 / 1024:.3f} MiB)")
        print(f"Reserve:   {RESERVE_BYTES:,} bytes (1.50 MiB) — never spend")
        print(f"Spendable: {spendable:,} bytes ({spendable / 1024 / 1024:.3f} MiB)")
    if args.require_reserve and free < RESERVE_BYTES:
        print(
            f"ERROR: free {free} < reserve {RESERVE_BYTES}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
