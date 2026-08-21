# measurement-tools

Builds and verifies the manifest that indexes measurement data held outside Git. See
[`measurement/README.md`](../../measurement/README.md) for where the data lives and why.

```bash
pip install -e software/measurement-tools

# Rebuild the manifest after adding a campaign
python -m measurement_tools.build_index \
  --source "$AQTUATOR_DATA_ROOT" \
  --out measurement/data-index.csv

# Check a copy against the manifest
python -m measurement_tools.verify_index            # full, re-hashes every file
python -m measurement_tools.verify_index --quick    # presence and size only
```

| Module | Role |
| --- | --- |
| `build_index` | Walks a data tree, hashes every file, parses metadata out of the filename conventions |
| `verify_index` | Checks presence, size and sha256 against the manifest |
| `data_root` | Resolves `$AQTUATOR_DATA_ROOT`; nothing hardcodes the absolute path |

Adding a new filename convention means extending `DATED` / `CUTTING` or the whole-stem field
patterns in `build_index.py`. Unmatched fields are left blank rather than guessed.
