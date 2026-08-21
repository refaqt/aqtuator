# Measurement

Physical test campaigns on the Mekanika Pro milling machine: tap tests, stability (chatter) tests,
and servo identification runs. See [`doqs/docs/architecture.md`](../doqs/docs/architecture.md)
(Measurement section) for the folder convention.

`simulation/` predicts; `measurement/` records what the machine actually did.

## Where the data lives

Raw measurement data is **not in Git**. 1.88 GB across 1 659 files today, growing with every
campaign — too large for the repository and well past the GitHub LFS free tier, which bills
bandwidth as well as storage.

| | |
| --- | --- |
| **Storage** | Google Drive, shared drive `3 - Projects` |
| **Root** | `H:\Shared drives\3 - Projects\2025-03 AQTUATOR\Development\7. Testing` |
| **Override** | `$AQTUATOR_DATA_ROOT` |
| **Access** | Google Drive for Desktop, or request access from the project owner |

Every path in `data-index.csv` is relative to that root, so the manifest stays valid if the drive
letter, mount point or backend ever changes. Never hardcode the absolute path — resolve it:

```python
from measurement_tools.data_root import data_root
path = data_root() / relpath          # quote it: the real path contains spaces
```

## The manifest

[`data-index.csv`](data-index.csv) has one row per file — 1 659 rows describing 1.88 GB.
It is what makes the archive usable without downloading it: you can answer *"which tap tests ran on
aluminium above 20 000 rpm?"* from a committed CSV, and the checksums let you verify any file you
do fetch.

Columns are the seven doqs-standard ones (`campaign`, `relpath`, `tier`, `bytes`, `sha256`,
`recorded_utc`, `notes`) followed by metadata parsed from this project's filename conventions:
`run`, `recorded_local`, `axis`, `pos_x/y/z`, `material`, `spindle_rpm`, `feed`, `ae_mm`, `ap_mm`,
`tool`, `repeat`, `tap`, `sample_rate_hz`, `descriptor`.

**Tiers** reflect what each file actually is — the `.CSV`/`.csv` case split is semantic, not accidental:

| Tier | What | Count |
| --- | --- | --: |
| `raw` | DATAQ WinDaq HiRes `.WDH` — the instrument original | 167 |
| `export` | Uppercase `.CSV` — a windowed selection exported from a `.WDH` | 158 |
| `derived` | Lowercase `.csv`, `.png` — analysis output (FRF curves, figures, tables) | 1 324 |

## Campaigns

| Campaign | Runs | What |
| --- | --- | --- |
| [`tap-tests`](cases/tap-tests/) | 6 | Impact hammer FRF at tool and spindle, various suspensions |
| [`stability-tests`](cases/stability-tests/) | 3 | Cutting trials in aluminium and S235JR steel, stepper vs servo |
| `old-tests` | — | Pre-2026 captures kept for reference; superseded by the campaigns above |

## Rebuilding the manifest

After adding a campaign to the shared drive:

```bash
python -m measurement_tools.build_index \
  --source "$AQTUATOR_DATA_ROOT/Machine FRF and stability" \
  --relative-to "$AQTUATOR_DATA_ROOT" \
  --out measurement/data-index.csv
```

Verify a local copy against the manifest with `python -m measurement_tools.verify_index`.

## Instrumentation

Accelerometers and an impact hammer sampled by a DATAQ WinDaq unit at 20 kHz aggregate
(8 channels). Channel assignment is per campaign — see each `cases/<slug>/README.md`. Older
captures in `old-tests` used 80 kHz aggregate / 10 kHz per channel.

`.WDH` is a proprietary DATAQ format with no reader in this repository; the `.CSV` exports are the
machine-readable path. Servo controller gains for the two feedback configurations are recorded in
[`servo-configurations/`](servo-configurations/).
