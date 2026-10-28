"""Build the strip end clamp, check that it fits, and draw the sketches.

Run from the repository root:
    python modules/compact-stage/simulation/cases/strip-end-clamp/run.py
Needs: cadquery-ocp, numpy, matplotlib, shapely. Does not need FreeCAD.
"""
import os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from clamp import *  # noqa: E402

base = placed('base', 'base')
top = cut(placed('carriage-top', 'carriage_top'), pocket_cut())
sc = scraper()
sc_cut = step_cut()
base2 = cut(base, sc_cut)
st = strip()
br = bars()
pn = pins()
sw = screws()
envelope = box(0, 0, 0, 440, 210, 40)
inside = common(sc_cut, envelope)
new = br + pn + sw


def overlap(a, b):
    return sum(vol(common(x, y)) for x in a for y in b)


checks = [
    # (name, value, rule): rule 'zero' fails above 0, 'pos' fails at or below 0, None only reports
    ('steps and holes outside the base material [mm3]', vol(inside) - vol(common(inside, base)), 'zero'),
    ('strip overlaps the base [mm3]', vol(common(st, base2)), 'zero'),
    ('bars overlap the base [mm3]', overlap(br, [base2]), 'zero'),
    ('bars and pins overlap the strip [mm3]', overlap(br + pn, [st]), 'zero'),
    ('screw heads and shanks overlap the strip [mm3]', overlap(sw, [st]), 'zero'),
    ('bar to the strip tab [mm]', min(dist(b, st) for b in br), 'pos'),
    ('new parts past the base end face (x < 0) [mm3]', overlap(new + [st], [box(-20, -10, 0, 0, 220, 60)]), 'zero'),
    ('new parts above the top of the base (z > 40) [mm3]', overlap(new, [box(-20, -10, Z_WALL, 60, 220, 60)]), 'zero'),
    ('bar can move down before it hits the step floor [mm]', BAR_Z[0] - STEP_FLOOR, 'pos'),
    ('bar can move up before a screw head reaches z = 40 [mm]', Z_WALL - BAR_Z[1] - HEAD_H, 'pos'),
]
for label, dx in CARRIAGE_END_X.items():
    d = dx - X0
    t, s = shift(top, d), shift(sc, d)
    checks += [
        (f'{label}: carriage-top overlaps strip or clamp [mm3]', overlap([t], [st] + new), 'zero'),
        (f'{label}: scraper overlaps strip or clamp [mm3]', overlap([s], [st] + new), 'zero'),
        (f'{label}: scraper lip to strip [mm]', dist(s, st), None),
        (f'{label}: top rollers overlap the base [mm3]', overlap(roller_cyls(d), [base2]), None),
        (f'{label}: top rollers overlap the flat strip [mm3]', overlap(roller_cyls(d), [st]), None),
    ]
fail = []
for name, value, rule in checks:
    print(f'{name:75s} {value:9.3f}')
    if (rule == 'zero' and value > 1e-6) or (rule == 'pos' and value <= 0):
        fail.append(name)
for f in ('fig_sections.py', 'fig_top_view.py', 'fig_strip.py'):
    runpy.run_path(os.path.join(HERE, f), init_globals=dict(base2=base2, top=top, sc=sc, st=st, br=br, pn=pn, sw=sw))
print('figures written to', os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'strip-end-clamp')))
if fail:
    raise SystemExit('FAILED: ' + '; '.join(fail))
