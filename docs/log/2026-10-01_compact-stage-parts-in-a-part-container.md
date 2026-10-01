# 2026-10-01 — The compact stage parts now sit in a Part container

**Role(s):** cad

## What happened

The new shared CAD rules say that the top object of a part file must be a Part container
(`App::Part`), with the Body inside it. The five compact stage parts had a bare Body on top, so the
CAD check failed on all five.

Each part file now has a Part container on top, named after the part. The existing Body moved into
it. The Body is now called `Body`, which is the name the shared build helper looks for. The
assembly links now point at the Part containers, not at the Bodies. All six links keep their
position. The bodies are still empty, so no geometry changed.

The CAD check now passes for all six files. The full project check still fails on one item that was
already failing before: the `software/LICENSE` file is missing.

## Decisions

- **The Part takes the part name, the Body takes the name `Body`.** These are the names the shared
  build helper uses. A later build script will find both and will not make a second Body.

## Open Questions

- None.

## Next Steps

- Add the missing `software/LICENSE` file, so the full project check passes again.

<details>
<summary>Technical notes</summary>

- The fix ran headless in FreeCAD 1.1.1 with `part(doc)` and `body(doc)` from
  `doqs/scripts/cad_build.py`, then `cad_fingerprint.write()`.
- The Bodies had the part name as their label (for example `base`), not `Body`. A plain
  `body(doc)` call did not find them and made a new, second Body. The script first renamed the
  label to `Body`.
- The `document` field in each fingerprint changed (for example `Base` to `base`). FreeCAD takes
  the internal document name from the file name when it opens a file. Only the file digests and this
  field changed.

</details>
