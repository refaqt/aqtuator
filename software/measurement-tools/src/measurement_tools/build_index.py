"""Build measurement/data-index.csv from a measurement data tree.

Raw measurement data lives outside Git (see measurement/README.md). This tool
walks the storage root and writes one manifest row per file, so the archive can
be queried, verified and cited without downloading any of it.

Usage:
    python -m measurement_tools.build_index --source <dir> --out <csv>

The manifest keeps the seven doqs-standard columns as a stable prefix
(campaign, relpath, tier, bytes, sha256, recorded_utc, notes) and appends the
campaign-specific metadata this project encodes in its filenames.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# doqs manifest prefix, then project-specific columns.
COLUMNS = [
    "campaign", "relpath", "tier", "bytes", "sha256", "recorded_utc", "notes",
    "run", "recorded_local", "axis", "pos_x", "pos_y", "pos_z",
    "material", "spindle_rpm", "feed", "ae_mm", "ap_mm", "tool",
    "repeat", "tap", "sample_rate_hz", "descriptor",
]

# Folder name -> doqs campaign slug (kebab-case, names the study not the conditions).
# Matched against every path component, so a nested campaign folder is found
# regardless of which top-level area it sits under.
CAMPAIGN_SLUGS = {
    "tap tests": "tap-tests",
    "stability tests": "stability-tests",
    "old tests": "old-tests",
    "servo configurations": "servo-configurations",
    "system identification": "system-identification",
    "high-speed circular motion": "high-speed-circular-motion",
    "odrive setup": "odrive-setup",
    "controllino": "controllino",
    "freecad cam toolbits": "cam-toolbits",
}

# 2026-05-07_09-28-00_X315_Y315_Z60_x_<descriptor>_fs_20000[_tap10]
DATED = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})[_ ](?P<time>\d{2}-\d{2}-\d{2})"
    r"[_ ]X(?P<x>-?\d+)[-_]Y(?P<y>-?\d+)[-_]Z(?P<z>-?\d+)"
    r"(?:[_ ](?P<axis>[xyz]|Gx|Gy|spindle_ramp))?"
    r"(?P<rest>.*)$"
)
# Alu_x_S24000_F1800_1
CUTTING = re.compile(
    r"^(?P<material>[A-Za-z0-9]+)_(?P<axis>[xyz])_S(?P<rpm>\d+)_F(?P<feed>\d+)(?:_(?P<rep>\d+))?$"
)
FS = re.compile(r"_fs_(\d+)")
TAP = re.compile(r"_tap(\d+)")

# Cutting parameters, appended to the dated stem in the stability campaigns, e.g.
# ..._Ae0_25_Ap_0to10_F1200_S10000_steel_S235JR
SPINDLE = re.compile(r"_S(\d+)(?![\dA-Za-z])")   # capital S only; _fs_20000 must not match
FEED = re.compile(r"_F(\d+)(?![\dA-Za-z])")
AE = re.compile(r"_Ae[_]?(\d+(?:_\d+)?)")        # Ae0_25 -> 0.25 mm
AP = re.compile(r"_Ap[_]?(\d+(?:to\d+)?)")       # Ap_0to10 -> swept 0..10 mm
TOOL = re.compile(r"(Flat end mill[^_]*(?:_\d+)?)")
MATERIALS = [
    (re.compile(r"steel[_ ]?S235JR|St235JR|S235JR", re.I), "steel-S235JR"),
    (re.compile(r"\bAlu\w*", re.I), "aluminium"),
]


def tier_of(path: Path) -> str:
    """Classify a file. The .CSV/.csv case split is semantic, not accidental:
    uppercase is a raw DAQ export, lowercase is analysis output."""
    suffix = path.suffix
    if suffix.lower() in (".wdh", ".wdq"):
        return "raw"
    if suffix == ".CSV":
        return "export"
    if suffix == ".csv":
        return "derived"
    if suffix.lower() in (".png", ".json", ".jpg", ".svg", ".pdf"):
        return "derived"
    return "other"


def campaign_of(relpath: Path) -> str:
    for part in relpath.parts:
        slug = CAMPAIGN_SLUGS.get(part.lower())
        if slug:
            return slug
    return "unclassified"


def run_of(relpath: Path) -> str:
    """The dated run directory inside a campaign, e.g. 2026-05-07_001_tap_tests_stepper."""
    for part in relpath.parts:
        if re.match(r"^\d{4}-\d{2}-\d{2}_\d{3}", part):
            return part
    return ""


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def parse_name(stem: str) -> dict:
    """Pull whatever metadata the filename encodes. Unmatched fields stay blank."""
    meta = {k: "" for k in COLUMNS if k not in
            ("campaign", "relpath", "tier", "bytes", "sha256", "recorded_utc", "notes", "run")}

    # Fields that may appear in any naming style are pulled from the whole stem.
    if m := FS.search(stem):
        meta["sample_rate_hz"] = m.group(1)
    if m := TAP.search(stem):
        meta["tap"] = m.group(1)
    if m := SPINDLE.search(stem):
        meta["spindle_rpm"] = m.group(1)
    if m := FEED.search(stem):
        meta["feed"] = m.group(1)
    if m := AE.search(stem):
        meta["ae_mm"] = m.group(1).replace("_", ".")
    if m := AP.search(stem):
        meta["ap_mm"] = m.group(1).replace("to", "-")
    if m := TOOL.search(stem):
        meta["tool"] = m.group(1).strip("_ ")
    for pattern, name in MATERIALS:
        if pattern.search(stem):
            meta["material"] = name
            break

    if m := DATED.match(stem):
        meta["recorded_local"] = f"{m['date']}T{m['time'].replace('-', ':')}"
        meta["pos_x"], meta["pos_y"], meta["pos_z"] = m["x"], m["y"], m["z"]
        if m["axis"]:
            meta["axis"] = m["axis"]
        rest = FS.sub("", TAP.sub("", m["rest"] or "")).strip("_ ")
        meta["descriptor"] = rest
        return meta

    if m := CUTTING.match(stem):
        # Only fill what the whole-stem pass did not already resolve, so the
        # normalised material name from MATERIALS wins over the raw token.
        meta["axis"] = m["axis"]
        meta["repeat"] = m["rep"] or "1"
        meta["material"] = meta["material"] or m["material"]
        meta["spindle_rpm"] = meta["spindle_rpm"] or m["rpm"]
        meta["feed"] = meta["feed"] or m["feed"]
        return meta

    meta["descriptor"] = stem
    return meta


def build(source: Path, out: Path, quiet: bool = False, relative_to: Path | None = None) -> int:
    base = relative_to or source
    rows = []
    files = sorted(p for p in source.rglob("*") if p.is_file())
    total = len(files)
    for i, path in enumerate(files, 1):
        if not quiet and i % 50 == 0:
            print(f"  {i}/{total} hashed", file=sys.stderr, flush=True)
        rel = path.relative_to(base)
        stat = path.stat()
        row = {
            "campaign": campaign_of(rel),
            "relpath": rel.as_posix(),
            "tier": tier_of(path),
            "bytes": stat.st_size,
            "sha256": sha256_of(path),
            "recorded_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc)
                                    .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "notes": "",
            "run": run_of(rel),
        }
        row.update(parse_name(path.stem))
        rows.append(row)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    if not quiet:
        size = sum(r["bytes"] for r in rows)
        print(f"{len(rows)} files, {size / 1024**3:.2f} GB -> {out}", file=sys.stderr)
    return len(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path, help="directory to walk")
    ap.add_argument("--out", required=True, type=Path, help="manifest CSV to write")
    ap.add_argument("--relative-to", type=Path, default=None,
                    help="storage root that relpath is measured from (default: --source). "
                         "Set this when indexing one campaign folder inside a larger root, "
                         "so the manifest stays valid as more campaigns are added.")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if not args.source.is_dir():
        ap.error(f"source is not a directory: {args.source}")
    if args.relative_to and not args.relative_to.is_dir():
        ap.error(f"--relative-to is not a directory: {args.relative_to}")
    build(args.source, args.out, args.quiet, args.relative_to)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
