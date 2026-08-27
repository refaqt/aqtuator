---
name: measurement-data
description: Answer questions about the AQTUATOR measurement archive - which tests exist, at what spindle speed, material, axis or machine position, and where a given capture lives. Also covers fetching a specific data file from Google Drive and adding a new campaign. Use for any question about tap tests, stability tests, FRF measurements, WDH or CSV captures, or "what data do we have".
---

# Querying the measurement archive

1 659 files, 1.88 GB, on the `3 - Projects` Google Drive shared drive. **None of it is in git.**

The whole point of the manifest is that you can answer most questions **without downloading
anything**. Read [`measurement/data-index.csv`](../../../measurement/data-index.csv) first; only fetch
an actual file if the question genuinely needs the samples.

## The manifest

One row per file. Columns:

| Column | Notes |
| --- | --- |
| `campaign` | `tap-tests`, `stability-tests`, `old-tests`, `servo-configurations` |
| `relpath` | Path relative to the storage root |
| `tier` | `raw` = DATAQ WinDaq `.WDH` original; `export` = `.CSV` selection cut from a `.WDH`; `derived` = analysis output |
| `bytes`, `sha256` | Integrity |
| `recorded_utc`, `recorded_local` | When it was captured |
| `run` | Dated run folder, e.g. `2026-05-07_001_tap_tests_stepper` |
| `axis`, `pos_x`, `pos_y`, `pos_z` | Axis under test and machine position |
| `material`, `spindle_rpm`, `feed`, `ae_mm`, `ap_mm`, `tool` | Cutting conditions |
| `repeat`, `tap`, `sample_rate_hz`, `descriptor` | Run detail |

Blank means the filename did not encode that field — **not** that the value is zero. Most `derived`
rows are analysis outputs with generic names and little metadata.

## Querying

```python
import csv
rows = list(csv.DictReader(open("measurement/data-index.csv", encoding="utf-8")))

# Which tap tests ran on aluminium above 20 000 rpm?
[r for r in rows if r["material"] == "aluminium" and r["spindle_rpm"] and int(r["spindle_rpm"]) > 20000]

# What raw captures exist at X315 Y315 Z70?
[r for r in rows if r["tier"] == "raw" and (r["pos_x"], r["pos_y"], r["pos_z"]) == ("315", "315", "70")]
```

Report counts and the distinguishing columns, not walls of paths. Cite `relpath` when naming a
specific run so it can be found again.

## Fetching a file

```python
from measurement_tools.data_root import resolve
path = resolve(row["relpath"])   # quote it - the real path contains spaces
```

Never hardcode the absolute path; it differs per machine, and an older analysis config in the data
already references these folders under a different drive letter. `$AQTUATOR_DATA_ROOT` overrides the
default mount.

`.WDH` is a proprietary DATAQ format with **no reader in this repository** — only WinDaq opens it.
When a question needs sample values, use the `export` tier `.CSV` files instead: 5 header lines, then
`Time` plus 8 voltage channels. Note that the stability-test runs are `.WDH` only.

## Verifying

```bash
python -m measurement_tools.verify_index --quick    # presence and size
python -m measurement_tools.verify_index            # full re-hash
```

## Adding a campaign

1. Record to the shared drive under `Machine FRF and stability/<Campaign>/<run>/`, following the
   existing run-folder convention `YYYY-MM-DD_NNN[_variant]`.
2. Write `measurement/cases/<slug>/README.md` — protocol, channel map, configuration.
3. Rebuild the manifest (see [`software/measurement-tools/README.md`](../../../software/measurement-tools/README.md)).
4. If a new filename convention appears, extend the patterns in `build_index.py` rather than letting
   fields silently go blank.
