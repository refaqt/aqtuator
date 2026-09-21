# 2026-09-21 — Bought parts move out of this repository

**Role(s):** engineering

## Goal

Stop storing supplier files in this repository. Move the rail, the blocks and
the linear motor into the shared parts library, and keep both X-axis assemblies
working.

## Work Done

- Added the shared parts library
  [STOQ](https://github.com/refaqt/stoq) as a submodule at `modules/stoq/`.
- Recorded nine bought parts there, under two brands: HIWIN for the linear
  guide, MAXWELL for the linear motor. Each part now carries its part number,
  its mass, the figures you choose it by, the address it came from and a
  checksum. See
  [refaqt/stoq#2](https://github.com/refaqt/stoq/pull/2).
- Deleted `cad/suppliers/` and five folders under `cad/parts/`: the guide block,
  the X guide rail, the linear motor forcer, and both magnet tracks.
- Pointed the two assemblies at the library instead. The X linear guide now
  links the HIWIN rail and block out of `modules/stoq/`, and the X axis links
  the MAXWELL magnet track the same way.
- Renamed the three moved models after the part number you order by, so a
  library document is no longer called after the job it happens to do in this
  machine. `guide-rail-x` became `HGR15R418H`.
- Updated the CAD guide, the module list and the architecture overview.
- Fixed the geometry check in the shared toolkit and updated to it, then
  measured all five models for the first time. The check asked every shape for
  its centre of mass using a property that FreeCAD does not offer on a shape
  made of several pieces, which is what almost every object in a real model is.
  See [refaqt/doqs#32](https://github.com/refaqt/doqs/pull/32).

## Decisions Made

- `cad/parts/` now holds only parts we make ourselves. A bought part goes in the
  library, where its part number and specification sit beside the model.
- Both brands are marked as files we may share, so the assemblies keep opening
  for anyone who clones this repository. That reading of their terms is
  recorded in the library, in
  [its first decision record](https://github.com/refaqt/stoq/blob/main/docs/decisions/2026-09-21_committing-supplier-cad.md).
- The assemblies stay where they are. Turning the X linear guide into a role
  module, so that swapping brand touches one line of text, is a separate piece
  of work and is not started here.

## Next Steps

- [ ] Raise a second point against the shared toolkit. A machine is supposed to
      skip the parts library's own checks, and the model check does. The parts
      check does not: it walks into `modules/stoq/` and compares every supplier
      checksum again. The build server now fetches those files so the checks
      pass, but the work should not be repeated here at all.
- [ ] Consider making the X linear guide a role module, so that changing rail
      brand is one line of text and one re-placement.
- [ ] Confirm the MK24 mover mass with MAXWELL. Their catalogue prints 1.9 kg
      where the shorter movers suggest about 4.4 kg.
- [ ] Confirm who makes the WJM050-3 forcer. It has a model and nothing else:
      no catalogue, no datasheet and no download address.

<details>
<summary>Checks</summary>

Both assemblies were opened headless in FreeCAD 1.1.1 after the move. Every
external link resolves, every joint recomputes, and no object is left invalid
or touched.

Geometry was compared against the version before the move, for all 17 solids in
the two assemblies. Volume, centre of mass and bounding box are identical to
five decimal places. Nothing moved.

`bash doqs.sh check`: every gate passes on the build server. The geometry gate
was failing on ten documents before this work and now measures the five that
remain, with 48 objects between them and no errors. That needed a fix in the
shared toolkit, which this branch also updates to.

The build server needs two extra lines to see the real CAD files. It fetches
large files for this repository only, never for a submodule, so the parts
library arrived as placeholders and every checksum comparison failed. The
workflow now fetches them for the library as well.

One further failure appears only on a local machine and not on the build
server: a leftover `software/` folder at the repository root, holding nothing
but Python cache files from before the software moved into the stage family.
Delete it and the failure goes.

</details>
