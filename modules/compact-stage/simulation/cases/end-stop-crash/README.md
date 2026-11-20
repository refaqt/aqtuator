# end-stop-crash

What happens when the carriage of the compact stage runs into its end stops at full motor force?
A wrong position command makes the drive push with 670 N. The drive speed clamp holds the carriage
at 2 m/s until it hits the two TA17-7 bumpers at the end. This case answers:

- How high is the stress in the base end wall, and does it deform for good (plastic deformation)?
- How high are the peak loads on the guide blocks, against the HIWIN ratings, and what does a crash
  do to their life?
- How hard is the read head shaken, against the RSF shock rating?
- Which screw joints slip, and can parts shift?
- What else breaks?

It runs for no payload, 1 kg, a second stage on top in cross configuration, and a table of payload
(0 to 20 kg) against the height of its centre of mass (20 to 200 mm above the carriage top).

Results: [`results/end-stop-crash/summary.md`](../../results/end-stop-crash/summary.md).
Interactive results page, with the 3D stress and the checks:
<https://refaqt.github.io/aqtuator/crash/>. `export_web_crash.py` and `export_web_fem.py` make its
data (see [its README](../../../../../simulation/cases/end-stop-crash-results/README.md)).

## Tools

FreeCAD 1.1 with Gmsh and CalculiX for the stress analysis. numpy and matplotlib for the crash
model. FreeCAD's own Python has both.

- **Windows:** the FreeCAD installer brings Gmsh and CalculiX. Nothing else to install.
- **Linux, and the cloud environment:** run `bash setup-fem.sh` from the repository root once. It
  installs FreeCAD 1.1, Gmsh and CalculiX from conda-forge into `/opt/freecad`.

The part files are in Git LFS. Run `git lfs pull` first if `base.FCStd` is only a small text file.

## Run it

From the repository root:

```bash
freecadcmd modules/compact-stage/simulation/cases/end-stop-crash/run_fem.py
```

```bash
freecadcmd modules/compact-stage/simulation/cases/end-stop-crash/evaluate.py
```

On Windows, use `"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe"` in place of `freecadcmd`.

`run_fem.py` takes about an hour on four cores, because CalculiX solves with its built-in SPOOLES
solver. It writes `fem.json`. `evaluate.py` takes a few minutes. It needs `fem.json`, and writes
`results.json`, `payload-table.csv` and the figures.

## How the model works

**Two parts.** A stress analysis of the base (`run_fem.py`), and a model of the moving carriage
(`crash_model.py`, run by `evaluate.py`). The stress analysis gives the force against deformation of
the end wall. The carriage model uses that curve as the stiffness of the wall it hits.

**The carriage.** One rigid body: carriage-bottom, carriage-top, forcer, guide blocks, read head and
the payload. Each part has its mass at its own centre of mass from the CAD. The body sits on four
springs, one for each guide block. Each spring takes forces up/down and sideways (115 N/µm, HIWIN
QE15 at ZA preload). Along the travel the blocks roll freely. The magnetic pull of the forcer
(963 N) and gravity preload the springs.

**The end stop, in three stages.**

1. **The bumpers.** Two ACE TUBUS TA17-7 at the leading end. Their force follows the ACE TA curve over
   the 7 mm stroke, scaled so that each one takes its 6 J catalogue energy at full stroke. This is the
   same curve as the [damper sizing page](../../../../../simulation/cases/damper-sizing/). Moving
   back, a bumper gives back 35 % of the work (ACE: 58 to 73 % is turned into heat).
2. **The flat tube.** Past 7 mm, the tube is pressed flat. ACE publishes nothing for this part. The
   model uses a steep spring, 3.6 kN/mm per bumper: a solid ring of co-polyester (Shore 55D), about
   160 mm² and 9 mm high. It is in series with the pocket wall of the base.
3. **Metal on metal.** 2 mm further, the end face of carriage-bottom meets the inner face of the
   base end wall. The base side follows the force against displacement curve from the stress
   analysis, plastic part included. The carriage end is taken as rigid. Moving back, the wall springs
   back with its elastic stiffness, so the plastic part stays as a dent.

**The motor.** In the main case the drive keeps pushing with 670 N through the whole crash. This is
the worst case in STG-15. The spread section also runs it with the motor off, and at the 2.2 m/s
overspeed trip.

**The base stress.** Only the start end of the base (x = 0 to 100 mm) is meshed. The far half carries
nothing in this crash. The two bottom strips that touch the machine table are held fixed. Two load
cases:

- **pocket:** the bumper force as pressure on the back faces of the two pockets;
- **band:** the metal hit as pressure on the inner face of the end wall, from z = 24 to 40 mm.

The material is EN AW-7075-T651 plate, 25 to 50 mm thick: E = 71 GPa, Rp0.2 = 460 MPa,
Rm = 530 MPa, A50 = 5 % (minimum values to EN 485-2). Past the yield point the stress rises in a
straight line to Rm at 4.5 % plastic strain.

**The checks.**

- **Guide blocks:** the equivalent load on each block, radial plus lateral plus its own moments
  scaled by C0/M0, is compared with C0. HIWIN asks for C0/P of at least 3 to 5 under shock (Table
  2.1). Below 1 the balls leave lasting marks in the tracks (brinelling).
- **Read head:** the acceleration at the head position is compared with the RSF rating,
  1000 m/s² for 6 ms (half sine, EN 60068-2-27).
- **Screw joints:** for each joint, the side load is compared with the friction the clamp force can
  hold. The clamp force comes from the tightening torque, with the VDI 2230 torque formula. The
  joint friction is 0.10 to 0.15, aluminium on aluminium, dry.

## Inputs that are not known

These change the numbers. The summary gives the spread for each of them.

| Input | Value used | Why it is not known |
| --- | --- | --- |
| Force of the bumper past its 7 mm stroke | 3.6 kN/mm, swept 1.8 to 9 kN/mm | ACE gives no data. Ask ACE for the static and dynamic curve of the TA17-7 |
| Bumper speed and temperature effect | ×1.0, swept 0.7 to 1.3 | Elastomers get stiffer when fast or cold |
| Tightening torques | Class 8.8 table values, VDI 2230:2014 at friction 0.12 | No torques in the repository yet |
| Moving mass | 4.24 kg | Estimate in the CE assessment. Weigh the first carriage |
| Alloy of the carriage | taken as rigid at the metal hit | Not chosen yet |
| Payload shape | a block 120 × 120 mm, twice as high as its centre of mass | Only its own inertia depends on this |
| Upper stage in cross configuration | 10.95 kg, centre of mass 84 mm above the base bottom, built from the CAD and catalogue masses | No stage has been weighed |

## Limits of this model

- **The carriage is rigid.** The real carriage bends a little. That lowers the peaks a little.
- **The force on the base is spread evenly** over the contact face. A tilted carriage first touches
  on one edge, where the local stress is higher.
- **The pocket and the band cases are separate stress runs.** In a crash with a metal hit, both act
  at the same time on the same wall. The summary reads both at their own peak force.
- **The top carriage must clear the screw heads.** In the CAD of 2026-11-10, carriage-top hits the
  heads of the seal strip corner screws about 7 mm before the bumpers touch. This is known and open
  (log of 2026-10-29). The crash model assumes the planned relief in carriage-top is made.
