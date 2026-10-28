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
rc = recess_cut()
base2 = cut(base, rc)
st = strip()
pl = plates()
sw = screws()
envelope = box(0, 0, 0, 440, 210, 40)
inside = common(rc, envelope)

checks = [
    # (name, value, rule): rule 'zero' fails above 0, 'pos' fails at or below 0, None only reports
    ('recess and holes outside the base material [mm3]', vol(inside) - vol(common(inside, base)), 'zero'),
    ('strip overlaps the base [mm3]', vol(common(st, base2)), 'zero'),
    ('plates overlap the base [mm3]', sum(vol(common(p, base2)) for p in pl), 'zero'),
    ('plates overlap the strip [mm3]', sum(vol(common(p, st)) for p in pl), 'zero'),
    ('screws overlap the strip [mm3]', sum(vol(common(s, st)) for s in sw), 'zero'),
    ('lowest x of strip, plates and screws (base end face = 0) [mm]',
     min(bbox(s)[0] for s in [st] + pl + sw), 'pos'),
    ('screw tip to the inside face of the end wall (x = 10) [mm]', 10 - max(bbox(s)[3] for s in sw), 'pos'),
]
for label, dx in CARRIAGE_END_X.items():
    d = dx - X0
    t, s = shift(top, d), shift(sc, d)
    checks += [
        (f'{label}: carriage-top overlaps strip, plates, screws [mm3]',
         sum(vol(common(t, p)) for p in [st] + pl + sw), 'zero'),
        (f'{label}: scraper overlaps strip, plates, screws [mm3]',
         sum(vol(common(s, p)) for p in [st] + pl + sw), 'zero'),
        (f'{label}: scraper lip to strip [mm]', dist(s, st), None),
        (f'{label}: top rollers overlap the base [mm3]', sum(vol(common(r, base2)) for r in roller_cyls(d)), None),
        (f'{label}: top rollers overlap the flat strip [mm3]', sum(vol(common(r, st)) for r in roller_cyls(d)), None),
    ]
fail = []
for name, value, rule in checks:
    print(f'{name:75s} {value:9.3f}')
    if (rule == 'zero' and value > 1e-6) or (rule == 'pos' and value <= 0):
        fail.append(name)
for f in ('fig_sections.py', 'fig_end_view.py', 'fig_strip.py'):
    runpy.run_path(os.path.join(HERE, f), init_globals=dict(base2=base2, top=top, sc=sc, st=st, pl=pl, sw=sw))
print('figures written to', os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'strip-end-clamp')))
if fail:
    raise SystemExit('FAILED: ' + '; '.join(fail))
