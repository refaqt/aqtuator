# 2026-11-06 — Forcer water cooling: O-ring seal, printed cooling block, hose route, cable clamp

**Role(s):** cad, engineering, purchasing

## Goal

Finish the water cooling of the forcer (the moving coil part of the MAXWELL MK21 linear motor).
The cooling channel in carriage-bottom existed, but it had no seal, no connection to hoses and
no hose route. Niels Bosmans asked for standard parts where possible, a closed rubber seal, a
compact connector on top of carriage-bottom, hoses that leave the carriage at the side with the
motor cable, and a printed clamp that closes the side exit. All cavities must be possible to
CNC mill.

## Short answer

- **Seal around the channel:** one standard O-ring, 90 × 2 NBR 70, in a groove with rounded
  corners in the forcer pocket ceiling. No printed seal.
- **Connector:** a small printed block (SLA resin) in a 5 mm pocket on top of carriage-bottom.
  Two 5 × 1.5 O-rings seal its ports. Two hose barbs are part of the print.
- **Hoses:** PU 4 × 2.5. They push over the barbs, cross over the motor cable in the cable
  opening, and run in their own slot to the side exit, beside the motor cable.
- **Cable clamp:** two printed halves just outside the side face. They close the exit around
  the hoses, the motor cable and the read head cable, and hold the hoses.
- **This is a first version for review.** Nothing is committed. The bought parts are not in stoq
  and not in the BOM yet.

## Work Done

### Choice of layout

Three layouts were drawn and shown as 3D views (see the
[decision record](../decisions/2026-11-06_forcer-cooling-sealed-with-standard-o-rings.md)).
Niels chose the printed block, asked to put it in the middle of the carriage, and drew the hose
route over the motor cable to the side.

Facts that decided it:

- Over the forcer, carriage-bottom has only 7.5 mm of aluminium, and the seal strip runs 1 mm
  above the top face.
- The smallest water-rated Festo push-in fitting for 4 mm hose, NPQH-D-M5-Q4-P10, has a 9 mm hex
  ([Festo data sheet](https://ftp.festo.com/public/PNEUMATIC/SOFTWARE_SERVICE/DataSheet/EN_GB/578334.pdf):
  water up to 0.6 MPa at 0–50 °C). The Festo QSM and NPQM mini fittings are rated for air only.
- An O-ring socket for the hose needs a block head about 8.5 mm tall. It could only hang in the
  cable opening, right where the motor cable comes up. Niels chose printed hose barbs instead.
- ERIKS Belgium has the metric O-rings in stock (NBR 70, compound 36624, checked 2026-11-06):
  90 × 2 (30 136 pieces), 85 × 2, 95 × 2, 5 × 1.5 (39 429).

### carriage-bottom

| Feature | What it does |
| --- | --- |
| `Sketch019` / `Pocket008` (changed) | Cooling channel. Tool 4 → 3 mm, pitch 5.2 → 4.1 mm, outer radius 4.5 → 3.5 mm. Still 8 passes, now 31.7 mm wide instead of 40.4 mm. Turned 180° about the channel centre, so both ends are on the +x side, at y = 90 (the middle of the carriage). |
| `Sketch036` / `Pocket023` (new) | Port lead: pass 1 goes on 5.5 mm past its end, so the two ports are 10.8 mm apart. |
| `Sketch035` / `Pocket022` (new) | O-ring groove in the pocket ceiling: 2.8 mm wide, 1.5 mm deep. Centre line 37.2 × 112.2 mm, corner radius 6 mm, length 288.5 mm. |
| `Pocket019` (changed) | Encoder slot 6 → 5 mm deep, so it keeps 1 mm over the groove. The read head cable is 3.7 mm. |
| `Sketch037` / `Pocket024` (new) | Pocket for the cooling block, 5 mm deep, corner radius 3 mm. It runs from over the ports to the motor cable opening. |
| `Sketch039` / `Pocket026` (new) | Two Ø2.5 mm ports from the block pocket floor into the channel. |
| `Hole006`, `Hole007` (new) | Two M2.5 screw holes from below for the block, both countersunk (ISO 10642). |
| `Sketch042` / `Pocket028` (new) | A 0.3 mm deep recess under both screw heads, so the heads stay clear of the forcer face. |
| `Sketch025` / `Pocket014` (changed) | Motor cable slot. The bend starts 5 mm later, towards the read head slot. Its radius on the cable centre line is now 35 mm (was 40 mm). Named `cable_bend_r` and `cable_rise_l`. |
| `Sketch041` / `Pocket027` (new) | Hose slot on the inner side of the cable bend, from the opening to the side face. 7.5 mm deep. It keeps 2.85 mm of wall to the carriage-top joint screw hole at y = 90. |
| `Sketch043` / `Hole008` (new) | Two tapped M3 holes, 8 mm deep, in the side face for the cable clamp. |
| `IF_cooling_block`, `IF_cable_clamp` (new frames) | For the block and the clamp in the assembly. |

All new pocket corners that a cutter must make have a radius of 3 mm or more (6 mm end mill).
The groove has corner radii of 4.6 mm (inside) and 7.4 mm (outside) and needs a cutter of
2.8 mm or less.

### Printed cooling block (new part)

`modules/compact-stage/cad/parts/cooling-block/build_model.py` builds it from the module
parameters (`port_*`, `barb_*`, `hose_*`, `cooling_*` in `cad/params/default.csv`).

- Arm: 38.5 × 21.7 × 4.9 mm in the pocket, 0.15 mm room on each side.
- Two 5 × 1.5 O-ring grooves in the bottom face (8 mm outside, 2 mm wide, 1.1 mm deep).
- Two Ø2 mm passages, each in one straight line from its port to its barb. The thinnest wall
  is 0.7 mm (under the barb rings).
- Two hose barbs, 8 mm long, three rings from Ø2.8 to Ø3.4 mm, bore Ø1.4 mm. They point into
  the motor cable opening.
- Two M2.5 holes, tapped in the resin, 4 mm deep.

### Printed cable clamp (new part)

`modules/compact-stage/cad/parts/cable-clamp/build_model.py`, two bodies:

- Lower half with a tower at each end. Two countersunk M3 screws go sideways through the towers
  into `Hole008`.
- Upper half. Two countersunk M3 screws come up through both halves into hex nuts in the top.
- Channels 0.2–0.3 mm smaller than what they hold: hoses Ø3.8, motor cable Ø8.0, read head cable
  Ø3.5. A 0.3 mm gap between the halves lets the screws press them.
- It sits outside the side face, 12 mm long, z = 16.6–31 mm. Over the base wall, carriage-bottom
  has only 9 mm of height, too little to wrap the 8.3 mm motor cable.

### Assembly

The block and the clamp are in `compact-stage.FCStd`, each with a fixed joint on its frame.
Nothing overlaps. The block is 1.1 mm under the seal strip. The clamp is 0.6 mm above the base
and 0.1 mm from the side faces of both carriage halves.

## Open Questions

- **The motor cable must stay low where the hoses cross it** in the opening (top of the cable
  below z ≈ 23 mm), then climb about 4 mm to the slot floor. Niels should check this with the
  real cable.
- **Cable bend radius.** The MK21 data sheet gives 69 mm as the smallest bend radius. The slot
  had 40 mm and now has 35 mm. That is fine only if 69 mm is the value for a moving cable.
- **Printed barbs** are 0.7 mm thick under the rings. Test a print: push a hose on and off a few
  times, and leak test at 2 bar.
- **O-ring sizes.** The groove centre line is 0.2 % shorter than the 90 × 2 ring. That is a
  light push-in, which is normal.
- **The channel has 35 % less wetted area** (2 312 mm² instead of 3 546 mm²). Expected to be
  fine, not checked by calculation.

## Next Steps

1. Niels reviews the design in FreeCAD.
2. After approval: add the O-rings, hose and screws to stoq (own PR, merged first), then to the
   BOM.
3. Print the block, then leak test it at 2 bar for 1 hour before the motor is powered.
