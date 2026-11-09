# 2026-11-09 — Parametric cooling block with Festo fittings, new cable clamps, screws in the assembly

**Role(s):** cad, engineering, purchasing

## Goal

Rework the forcer water cooling of the compact stage after review by Niels Bosmans: a fully
parametric cooling block that runs to the side face, screwed-in Festo fittings, four screws on the
centre line, small cable clamps under carriage-top, and the bought parts in the parts library, the
supplier list and the assembly.

## Short answer

- **The cooling block is now parametric.** It is a chain of FreeCAD features. Every sketch is
  fully constrained, and every size comes from the module parameters. Its pocket in
  carriage-bottom uses the same outline function, so the two always fit.
- **Two Festo NPQH-D-M5-Q4-P10 fittings** screw into M5 threads tapped in a head outside the side
  face. Each thread has 2 mm of resin around it. The hoses push into the fittings.
- **Four M2.5 screws** hold the block, all on its centre line. They are Fasteners workbench screws
  in the assembly, held by plain fixed joints to the hole edges.
- **Two new cable clamps** replace the side clamp. The old clamp is gone from the files and the
  assembly.
- **The parts are in the library and the supplier list.** The two O-rings, the fitting and the
  hose are in stoq (refaqt/stoq#28). ERIKS, Festo, Aqua Computer and RS Components are in maqers.
- **The rule "build parts from features" is now shared**, in refaqt/refaqt-agents#19 and
  refaqt/doqs#52.

## Work Done

### Cooling block (`cad/parts/cooling-block/`)

- `cooling_outline.py`: the outline of the block and of its pocket (eight lines, eight fillets),
  the passage paths, rounded rectangles and circles. Every sketch is fully constrained by
  relations and by expressions on `Params`.
- `build_model.py`: Pad of the outline (4.9 mm), Pad of the head (9 × 20 mm, 9 mm high), two
  O-ring grooves and risers, two passages swept along their paths, an M5 thread Hole for each
  fitting (5 mm), and an M2.5 thread Hole for each screw (4 mm).
- Frames: `IF_carriage`, `IF_fitting_a/b` (on the head end face, Z along the fitting) and
  `IF_oring_a/b`.
- Thinnest resin wall: 0.9 mm over and under the passages near the ports, 1.35 mm beside them in
  the arm, 1.5 mm to the screw holes, 2 mm around the M5 threads.

### carriage-bottom (edited in FreeCAD)

| Feature | What it does |
| --- | --- |
| `CoolingPocketSketch` / `CoolingPocket` (new) | One smooth pocket, 5 mm deep, for the block. Replaces `Pocket024` and the hose slot `Pocket027`. |
| `Sk_Hole006`, `Sk_Hole007` (changed) | The two screws in the wide part move from y = 89 to y = 89.5, the centre line. |
| `Sk_HoleCD` / `HoleCD`, `RecessCD` (new) | Two countersunk M2.5 screws near the side face, with a 0.3 mm recess for the heads. |
| `CableDipSketch` / `CableDip` (new) | The motor cable slot is 5 mm deeper in the first 45° of its bend. |
| `MotorClampPocket`, `ReadHeadClampPocket` (new) | Pockets for the two cable clamps, with frames `IF_motor_cable_clamp` and `IF_read_head_cable_clamp`. |
| `Sketch043` / `Hole008`, frame `IF_cable_clamp` (removed) | The holes and frame of the old side clamp. |

The new parameters are in `cad/params/default.csv`, and the barb parameters are gone.

### Cable clamps (`cad/parts/motor-cable-clamp/`, `cad/parts/read-head-cable-clamp/`)

Two printed halves each. Motor cable clamp: 10 × 10.7 mm, stack 9.9 mm in a 9.7 mm pocket.
Read head cable clamp: 10 × 6.1 mm, stack 5.3 mm in a 5.1 mm pocket. Each half has 0.1 mm of
room to its pocket on every side.

### Assembly

New: both clamps, two 5 × 1.5 O-rings, two fittings, two 20 mm hose stubs, and four ISO 10642
M2.5 screws (2 × M2.5 × 6, 2 × M2.5 × 8). Removed: the old cable clamp and its joint. A check of
every new part against its neighbours finds only the overlaps that are meant: the fitting threads
in their tapped holes, the screws in their tapped holes, the O-rings before they are pressed, and
the 0.2 mm squeeze of the motor cable clamp under carriage-top.

The 90 × 2 O-ring is in the bill of materials, but not in the assembly. In its groove it takes a
rounded rectangle shape, which a round model cannot show.

### Purchasing

- stoq (merged): `generic/o-ring-metric` (90X2-NBR70, 5X1.5-NBR70), `festo/npqh`
  (NPQH-D-M5-Q4-P10), `festo/pun-h` (197383 = PUN-H-4X0,75-BL). Each part has its own parametric
  model.
- maqers (on `main`): ERIKS for both O-rings, Festo for the fitting and the hose, Aqua Computer and
  RS Components as other hose sources.
- ERIKS has the 5 × 1.5 ring in stock. The 90 × 2 ring was not in stock on 2026-11-09 (delivery
  2026-12-01).
- Conrad was searched in Chrome and by web search. It has no listing for these two O-ring sizes,
  so it is not in maqers.
- The Festo hose has an inside diameter of 2.6 mm, not 2.5 mm. `hose_id` is corrected.

### Sources read in Chrome

- Festo NPQH catalogue 2025, page 5: M5, thread length 4 mm, overall length 21.5 mm, hex 9 mm.
- Festo data sheet 578334: water up to 0.6 MPa at 0–50 °C, insertion depth 13 mm, 1 Nm,
  internal hex 2.5 mm.
- Festo product page 197383: 4 × 2.6 mm.
- ERIKS product pages 10028005 (90 × 2) and 10028062 (5 × 1.5).

## Open Questions

- **The motor cable must lie low under the block** in its bend. Check it with the real cable.
- **The screws near the side face** have 2.3 mm of thread in the resin. Test the pull-out on the
  first print.
- **The fitting model** has two estimated lengths (hex and release ring). Measure a real fitting.
- **Headless builds** do not run with FreeCAD 1.1.4: it loads the script the same way an import
  does, so the doqs build helper skips the build. The builds in this change ran through a small
  wrapper. This needs a fix in doqs.
- **New mounting frames** with an angle only turn after a second recompute. Also a doqs fix.

## Next Steps

1. Niels reviews the design in FreeCAD.
2. Print the block and the clamps. Leak test the block at 2 bar for 1 hour before the motor is
   powered.

## Review fixes (same day)

Niels Bosmans reviewed the design and found five problems. All are fixed.

- **Parts did not load.** The assembly uses the new parts from the parts library, but the new
  library version was not recorded in this repository. The session start put the library folder
  back on the old version, which does not have them. The new version is now recorded, and all six
  parts load.
- **Flat print base.** The top of the block and its head is now one flat face. The head hangs
  down, and the M5 threads moved 2.6 mm down. A short drop in each passage joins them.
- **Screws near the side face.** The two countersunk holes there became one, at x = 198 mm. The
  block has three screws now.
- **Cable clamps.** The clamps now sit in the existing cable slots, flush with the side face, with
  square corners and 0.1 mm of room on each side. The extra clamp pockets are gone. I had read
  "0.1 mm of space on each side of the cable pocket" as a new, wider pocket. That was wrong.
- **Cable dip.** The deeper part of the motor cable slot had straight ends with sharp corners
  that no mill can cut. Its ends are now half circles of the slot width. It starts 5° into the
  bend, so its end stays 2.8 mm away from the step in the underside.

The rule "design for the process: corner radii for milling, tool access, a flat print face, take
sizes from the existing slot" is now in the shared FreeCAD skill (refaqt/refaqt-agents#20).

