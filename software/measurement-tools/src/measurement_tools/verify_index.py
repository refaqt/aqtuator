"""Verify measurement data against the committed manifest.

Checks that every file the manifest describes is present at the data root and
still hashes to the recorded sha256. Use it after a storage migration, before
relying on an archive you have not touched in a while, or to find out what a
local copy is missing.

Usage:
    python -m measurement_tools.verify_index [--index measurement/data-index.csv]
                                             [--root DIR] [--quick] [--campaign SLUG]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .build_index import sha256_of
from .data_root import data_root


def verify(index: Path, root: Path, quick: bool = False, campaign: str | None = None) -> int:
    rows = list(csv.DictReader(index.open(encoding="utf-8")))
    if campaign:
        rows = [r for r in rows if r["campaign"] == campaign]
    if not rows:
        print("no rows to verify", file=sys.stderr)
        return 1

    missing, wrong_size, wrong_hash = [], [], []
    for i, row in enumerate(rows, 1):
        if i % 100 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr, flush=True)
        path = root / row["relpath"]
        if not path.is_file():
            missing.append(row["relpath"])
            continue
        if path.stat().st_size != int(row["bytes"]):
            wrong_size.append(row["relpath"])
            continue
        if not quick and sha256_of(path) != row["sha256"]:
            wrong_hash.append(row["relpath"])

    ok = len(rows) - len(missing) - len(wrong_size) - len(wrong_hash)
    print(f"\nchecked  : {len(rows)} rows against {root}")
    print(f"ok       : {ok}")
    print(f"missing  : {len(missing)}")
    print(f"bad size : {len(wrong_size)}")
    print(f"bad hash : {'skipped (--quick)' if quick else len(wrong_hash)}")

    for label, items in (("MISSING", missing), ("SIZE", wrong_size), ("HASH", wrong_hash)):
        for rel in items[:20]:
            print(f"  {label}: {rel}", file=sys.stderr)
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more {label}", file=sys.stderr)

    return 0 if not (missing or wrong_size or wrong_hash) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--index", type=Path, default=Path("measurement/data-index.csv"))
    ap.add_argument("--root", type=Path, default=None, help="defaults to $AQTUATOR_DATA_ROOT")
    ap.add_argument("--quick", action="store_true", help="check presence and size only, skip hashing")
    ap.add_argument("--campaign", default=None, help="verify a single campaign slug")
    args = ap.parse_args(argv)

    if not args.index.is_file():
        ap.error(f"manifest not found: {args.index} (run from the repo root)")
    return verify(args.index, args.root or data_root(), args.quick, args.campaign)


if __name__ == "__main__":
    raise SystemExit(main())
