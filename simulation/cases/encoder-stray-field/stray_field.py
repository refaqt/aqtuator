"""Stray magnetic field of the MAXWELL MK2 magnet track at the encoder read head.

Python 3 with magpylib and magpylib-material-response:

    pip install magpylib magpylib-material-response
    python3 simulation/cases/encoder-stray-field/stray_field.py

The X axis is driven by an MK21 iron core mover on two MK2-180 magnet tracks.
A magnetic linear encoder reads a scale about 30 mm beside the motor. This case
answers two questions:

  1. How strong is the motor's field at the read head?
  2. How much does a thin steel plate between the magnet track and the read
     head lower it?

Model
-----
The magnet track is 12 magnets of alternating polarity, 30 mm pole pitch, two
MK2-180 tracks placed end to end. The magnet sizes are NOT known: the STEP
files are not downloaded and the catalogue gives no magnet sizes. The values
below are a deliberate worst case (thick, wide, strong magnets). They give a
surface field of about 390 mT, which is at the high end for this kind of track.

The steel back plate of the track is handled with a mirror image: each magnet
is modelled twice as thick, which is what a flat plate of very soft iron
behind it does. The mover and the guide rail are NOT in the model.

The shield plates are split into small cells. Each cell is magnetised by the
field of the magnets and of all other cells (a moment method). The steel is
treated as linear: it never saturates. The script prints the highest flux
density in any plate so the reader can see when that assumption fails.
Ferritic stainless (403, 430) saturates near 1.5 T, low carbon steel near 2 T.

Uncertainty: the magnet sizes alone can move the answer by about 50 %.
Measure with a gaussmeter before ordering parts.
"""
import logging

import magpylib as magpy
import numpy as np
from magpylib_material_response.demag import apply_demag
from magpylib_material_response.meshing import mesh_Cuboid

logging.disable(logging.CRITICAL)
MM = 1e-3

# Magnet track, worst case (all in mm unless named)
BR = 1.42          # remanence, T (N42-class NdFeB)
TAU = 30.0         # pole pitch
N_POLES = 12       # two MK2-180 tracks end to end
TRACK_L = N_POLES * TAU
MAG_ALONG = 27.0   # magnet length along the travel
MAG_ACROSS = 80.0  # magnet width across the track
MAG_T = 6.0        # magnet thickness
TRACK_EDGE = 43.0  # half of the 86 mm track width

# Read head: distance out from the track edge, and heights above the magnets
HEAD_OUT = 30.0
HEAD_UP = (10.0, 20.0)
KEEP_OFF_END = 60.0  # "middle of stroke" means at least this far from a track end

# Steel: relative permeability (linear model)
MU_FERRITIC = 300    # 403 / 430 stainless, annealed
MU_LOW_CARBON = 1000  # S235, DC01, 1010

CELL = 6.0  # shield mesh size


def magnet_track():
    track = magpy.Collection()
    for i in range(N_POLES):
        x = -TRACK_L / 2 + TAU / 2 + i * TAU
        sign = 1 if i % 2 == 0 else -1
        magnet = magpy.magnet.Cuboid(
            polarization=(0, 0, sign * BR),
            # twice as thick: magnet plus its mirror image in the back plate
            dimension=(MAG_ALONG * MM, MAG_ACROSS * MM, 2 * MAG_T * MM),
            position=(x * MM, 0, 0),
        )
        magnet.susceptibility = 0.05
        track.add(magnet)
    return track


def plate(mu_r, thickness, gap, top, overhang=20.0, bottom=-MAG_T):
    """Steel plate parallel to the track, `gap` mm out from the track edge.

    `top` is the plate top in mm above the magnet surface. The plate runs
    `overhang` mm past each end of the track.
    """
    length = TRACK_L + 2 * overhang
    height = MAG_T + top - bottom
    body = magpy.magnet.Cuboid(
        polarization=(0, 0, 0),
        dimension=(length * MM, thickness * MM, height * MM),
        position=(0, (TRACK_EDGE + gap + thickness / 2) * MM, (bottom + MAG_T + top) / 2 * MM),
    )
    cells = mesh_Cuboid(body, (int(length / CELL), 2, max(2, int(height / CELL))))
    for cell in cells.sources_all:
        cell.susceptibility = mu_r - 1
    return cells


def field_at_head(system):
    xs = np.linspace(-TRACK_L / 2 - 60, 0, 241)  # from past one end to the middle
    rows = []
    for up in HEAD_UP:
        points = np.c_[xs, np.full_like(xs, TRACK_EDGE + HEAD_OUT), np.full_like(xs, MAG_T + up)]
        b = np.linalg.norm(system.getB(points * MM), axis=1) * 1e3
        middle = b[xs > -TRACK_L / 2 + KEEP_OFF_END].max()
        rows.append((up, middle, b.max()))
    return rows


def peak_in_steel(system):
    return max(
        (np.linalg.norm(s.polarization) for s in system.sources_all if getattr(s, "susceptibility", 0) > 1),
        default=0.0,
    )


CASES = [
    ("No shield", []),
    ("One plate, ferritic stainless, 2 mm", [(MU_FERRITIC, 2, 3, 20)]),
    ("One plate, ferritic stainless, 3 mm", [(MU_FERRITIC, 3, 3, 20)]),
    ("One plate, low carbon steel, 3 mm", [(MU_LOW_CARBON, 3, 3, 20)]),
    ("One plate, low carbon steel, 3 mm, 35 mm tall", [(MU_LOW_CARBON, 3, 3, 35)]),
    ("Two plates, low carbon steel, 2 + 2 mm, 4 mm air gap", [(MU_LOW_CARBON, 2, 3, 20), (MU_LOW_CARBON, 2, 9, 25)]),
]


def main():
    surface = np.linalg.norm(magnet_track().getB(np.array([-TRACK_L / 2 + TAU / 2, 0, MAG_T + 1]) * MM)) * 1e3
    print(f"Magnet surface field (1 mm above a pole): {surface:.0f} mT")
    print(f"Read head {HEAD_OUT:.0f} mm out from the track edge. Values in mT.")
    print(f"'middle' = at least {KEEP_OFF_END:.0f} mm from a track end; 'end' = worst point near a track end.\n")
    header = f"{'Case':54s}" + "".join(f" | {u:.0f} mm up: middle   end" for u in HEAD_UP) + " | peak B in steel"
    print(header)
    print("-" * len(header))
    for name, plates in CASES:
        system = magnet_track()
        for p in plates:
            system.add(plate(*p))
        if plates:
            system = apply_demag(system)
        cols = "".join(f" |          {m:5.2f}  {e:5.2f}" for _, m, e in field_at_head(system))
        steel = f"{peak_in_steel(system):.2f} T" if plates else "-"
        print(f"{name:54s}{cols} | {steel}", flush=True)


if __name__ == "__main__":
    main()
