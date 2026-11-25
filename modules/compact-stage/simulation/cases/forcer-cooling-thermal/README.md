<!-- SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# forcer-cooling-thermal

How hot does the compact stage get when the MAXWELL MK21 linear motor (the forcer) runs all the
time at its rated current of 2.0 A, with 20 °C water in the cooling channel? This case answers:

- How hot do the coil, the forcer mounting face, carriage-bottom, carriage-top, the base, the rails
  and the guide blocks get? How much does the water warm up?
- Does the printed cooling block get hot enough to deform? How do SLA resins and FDM filaments
  compare with their heat limits?
- Which common, affordable pump gives enough flow when one manifold feeds six axes and a spindle in
  parallel, and what flow reaches one axis?
- How much does the stage grow and tilt from the heat, and how much does it move the top face
  against the encoder read head?

Results: [`results/forcer-cooling-thermal/summary.md`](../../results/forcer-cooling-thermal/summary.md).
Interactive results page, with the 3D temperature and growth, all inputs and the checks:
<https://refaqt.github.io/aqtuator/thermal/> (folder
[`simulation/cases/forcer-cooling-thermal-results/`](../../../../../simulation/cases/forcer-cooling-thermal-results/)).

## Tools

FreeCAD 1.1 with Gmsh, and numpy, scipy and pyamg in the FreeCAD Python. The heat and growth
solves use the small finite element code in `fem.py` (10-node tetrahedra), not CalculiX: the parts
are meshed one by one and joined in the solver, with their own contact conductance at each joint.

- **Linux, and the cloud environment:** run `bash setup-fem.sh` from the repository root once. It
  installs FreeCAD 1.1, Gmsh, CalculiX, scipy and pyamg into `/opt/freecad`.
- **Windows:** the FreeCAD installer brings Gmsh, numpy and scipy. Without pyamg the solver falls
  back to a direct solve, which needs much more memory and time. Install pyamg into the FreeCAD
  Python if you can.

The part files are in Git LFS. Run `git lfs pull` first if `base.FCStd` is only a small text file.

## Run it

From the repository root:

```bash
freecadcmd modules/compact-stage/simulation/cases/forcer-cooling-thermal/build_geometry.py
```

```bash
freecadcmd modules/compact-stage/simulation/cases/forcer-cooling-thermal/run_thermal.py
```

```bash
THERMAL_MESH_SCALE=0.75 freecadcmd modules/compact-stage/simulation/cases/forcer-cooling-thermal/run_thermal.py
```

```bash
freecadcmd modules/compact-stage/simulation/cases/forcer-cooling-thermal/export_web.py
```

```bash
node simulation/cases/forcer-cooling-thermal-results/check_data.mjs
```

`build_geometry.py` takes about 3 minutes. `run_thermal.py` takes about an hour on four cores: the
main case, about 25 sweep cases, the warm-up and two growth solves. The third command is the mesh
check (a finer mesh, main case only). `export_web.py` writes the data of the page.

## Files

| File | What it does |
| --- | --- |
| `case.toml` | Every input, with its source |
| `print_materials.toml` | Heat limits of the printing materials, from the maker data sheets |
| `build_geometry.py` | Solids from the CAD on their assembly positions; blocks for the bought parts; the water volume |
| `meshing.py` | Gmsh mesh of each part |
| `fem.py` | Element code: heat conduction, films, joints, elasticity |
| `hydraulics.py` | Pressure loss, film coefficient, pump operating point |
| `run_thermal.py` | The heat and growth model, sweeps, warm-up; writes `thermal.json` |
| `export_web.py` | Data of the results page |

## How the model works

**Geometry.** Base, carriage-bottom, carriage-top and the printed cooling block are the real solids
from their part files, placed where the assembly `compact-stage.FCStd` has them. Screw holes,
threads and drill tips are filled: they do not change heat flow or growth, and Gmsh cannot mesh some
thread faces. The bought parts are in the stoq library as Git LFS files that were not reachable, so
they are blocks with the sizes from the stoq parts tables and the maker data sheets:

- forcer MK21: 118 × 86 × 23.7 mm, in the middle of the forcer pocket, with the 3 mm step along
  one long edge where carriage-bottom has two pads (0.25 mm narrower on each side, so it touches
  carriage-bottom only with its mounting face);
- magnet track: two MK2-180 end to end, 86 × 9.6 mm, under the forcer;
- rails: EGR15, 15 × 12.5 × 418 mm, on their assembly positions;
- guide blocks: QEH15SA steel body, 34 mm wide, 23.1 mm long, from 4 mm to 24 mm above the rail
  bottom, with a slot as wide as the rail.

**Water.** The water is the volume that the channel, port lead and port features of
carriage-bottom and the riser, passage and drop features of the cooling block take out of their
parts. It is meshed only to find the wetted faces and the distance along the path. On the wetted
faces, a film coefficient from the flow (Gnielinski, with his laminar-turbulent blend between
Re 2 300 and 10 000) links the wall to the local water temperature. The water temperature rises
along the path by the heat it takes up.

**Joints.** Each outer face of each part is sorted: wetted, touching another part (gap below
0.05 mm: contact conductance of that joint type), facing another part across a thin air gap (up to
1 mm: air conduction k/gap), on the machine table, or open to the air (still-air convection by face
direction, plus radiation). Parts have separate meshes; a joint links each node of one face to the
closest point of the other face, half from each side.

**Forcer.** The copper loss 1.5 · R(T) · I² is spread evenly over the forcer block. The resistance
is a straight line from 13.8 Ω at 25 °C to 19.0 Ω at 120 °C, taken at the hottest coil point. The
conductivity of the block is set so that its hottest point is 0.87 K/W above its mounting face
when that face is held at one temperature: the data sheet thermal resistance.

**Growth.** Linear elasticity on the same mesh, with the steady temperatures relative to 20 °C.
Bolted joints are tied with stiff penalty springs. Between rail and guide block, only the motion
along the face normal is tied, with the ball stiffness of the QE15 at ZA preload; the block rolls
freely along the rail. The base bottom stays on the table; main case: free to grow in its plane,
held at one point; variant: the whole bottom clamped.

**Pump.** `hydraulics.py` finds where the pump curve meets the curve of seven parallel branches
(six axes and the spindle) between two manifolds. Only the maximum pressure and maximum flow of each
pump come from the maker; the curve between is assumed.

## Checks

- `fem.py` gives the exact answer on a test block: a heated slab, the free growth of a uniformly
  heated block (no stress), and a block cooled by a film.
- The heat balance of every case closes within 0.5 %.
- The water warm-up equals the heat into the water divided by ṁ c.
- The mesh check runs the main case on a finer mesh.

## Inputs that are not known

| Input | Value used | Sweep |
| --- | --- | --- |
| Contact conductance, forcer face | 3 000 W/(m² K) | 1 000 to 10 000 |
| Contact conductance, bolted metal joints | 3 000 W/(m² K) | 1 000 to 10 000 |
| Contact conductance, printed block on its pocket floor | 500 W/(m² K) | 200 to 2 000 |
| Contact conductance, rail to guide block (balls) | 800 W/(m² K) | 300 to 3 000 |
| Contact conductance, base on the table | 1 000 W/(m² K) | 300 to 3 000 |
| Film coefficient in the water | Gnielinski | × 0.5 and × 2 |
| Air temperature | 20 °C | 15 to 30 °C |
| Surfaces | bare metal, emissivity 0.10 | anodised, 0.80 |
| Pump | TEYU CW-5200, 4 bar option | the other candidates |
| What R<sub>TH</sub> 0.87 K/W is measured to | coil hot spot to mounting face | ask MAXWELL |
