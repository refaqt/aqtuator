# encoder-stray-field

How strong is the field of the X-axis linear motor at the magnetic encoder read head, and
can a thin steel plate bring it below 1 mT?

The X axis uses a MAXWELL MK21 iron core mover on two MK2-180 magnet tracks. The read head
sits about 30 mm beside the mover. The encoder must stay below 1 mT.

**Tool:** Python 3 with `magpylib` and `magpylib-material-response`.

```bash
pip install magpylib magpylib-material-response
python3 simulation/cases/encoder-stray-field/stray_field.py
```

The run takes under a minute and needs about 2 GB of memory.

Results: [`simulation/results/encoder-stray-field/summary.md`](../../results/encoder-stray-field/summary.md).
Log: [2026-09-23](../../../docs/log/2026-09-23_encoder-stray-field-shield.md).

## What the model includes

- Twelve magnets of alternating polarity with a 30 mm pole pitch, as two MK2-180 tracks
  placed end to end.
- The steel back plate of the track, as a mirror image of each magnet.
- One or two steel plates beside the track, split into small cells, each magnetised by
  everything around it.

## What the model leaves out

- **The real magnet sizes.** The STEP files in the parts library are not downloaded, and
  the catalogue does not give magnet sizes. The script uses a deliberate worst case: magnets
  27 × 80 × 6 mm, remanence 1.42 T, about 390 mT at the surface.
- **The mover, the guide rail and the coil current.** The coil ends add an estimated 1 to
  3 mT at peak current, and less than 1 mT at continuous current. That estimate is a hand
  calculation, not part of the script.
- **Saturation.** The steel is linear. The script prints the highest flux density in any
  plate, so you can see where this stops being true. That value sits in the corner cell
  nearest the magnets and depends on the cell size, so read it as a warning, not a figure.

Expect the real values to be up to 50 % higher or lower. Measure with a gaussmeter before
ordering parts.
