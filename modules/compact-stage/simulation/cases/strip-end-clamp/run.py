"""Build the strip end clamp (version 3, insert and countersunk screw), check that it fits, run
the strip model for the 0.15 mm strip, and draw the sketches.

Run from the repository root:
    python modules/compact-stage/simulation/cases/strip-end-clamp/run.py
Needs: cadquery-ocp, numpy, matplotlib, shapely, and Node 18 or newer. Does not need FreeCAD.
"""
import json, os, runpy, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from clamp import *  # noqa: E402

base = placed('base', 'base')
top = cut(placed('carriage-top', 'carriage_top'), pocket_cut())
top_long = cut(top, long_pocket_cut())
sc = scraper_v3()
gc = groove_cut()
base2 = cut(base, gc)
envelope = box(0, 0, 0, 440, 210, 40)
inside = common(gc, envelope)
set_parts = dict(strip=strip(), insert=insert(), nut=nut(), screw=screw())
loose = [strip(TRAVEL), insert(TRAVEL), nut(TRAVEL)]
clamp_parts = [set_parts['insert'], set_parts['nut'], set_parts['screw']]


def overlap(a, b):
    return sum(vol(common(x, y)) for x in a for y in b)


checks = [
    # (name, value, rule): rule 'zero' fails above 0, 'pos' fails at or below 0, None only reports
    ('groove and hole outside the base material [mm3]', vol(inside) - vol(common(inside, base)), 'zero'),
    ('strip, insert, nut overlap the base, set and loose [mm3]',
     overlap([set_parts['strip'], set_parts['insert'], set_parts['nut']] + loose, [base2]), 'zero'),
    ('insert overlaps strip or nut [mm3]', overlap([set_parts['insert']], [set_parts['strip'], set_parts['nut']]), 'zero'),
    ('screw overlaps strip or nut [mm3]', overlap([set_parts['screw']], [set_parts['strip'], set_parts['nut']]), 'zero'),
    ('nut to the base (groove walls and floor) [mm]', dist(set_parts['nut'], base2), 'pos'),
    ('new parts past the base end face (x < 0) [mm3]',
     overlap(clamp_parts + loose + [set_parts['strip']], [box(-20, -10, 0, 0, 220, 60)]), 'zero'),
    ('flange top above the strip [mm]', FLANGE_H, None),
]
for label, dx in CARRIAGE_END_X.items():
    d = dx - X0
    t, tl, s = shift(top, d), shift(top_long, d), shift(sc, d)
    crash = label.startswith('dampers')
    checks += [
        (f'{label}: scraper overlaps strip or clamp [mm3]', overlap([s], [set_parts['strip']] + clamp_parts),
         None if crash else 'zero'),
        (f'{label}: scraper to the insert [mm]', dist(s, set_parts['insert']), None if crash else 'pos'),
        (f'{label}: carriage-top overlaps strip or clamp [mm3]', overlap([t], [set_parts['strip']] + clamp_parts),
         None if crash else 'zero'),
        (f'{label}: same, carriage-top with the longer pocket [mm3]', overlap([tl], [set_parts['strip']] + clamp_parts), 'zero'),
        (f'{label}: top rollers overlap the clamp [mm3]', overlap(roller_cyls(d), clamp_parts), 'zero'),
    ]
fail = []
lines = []
for name, value, rule in checks:
    lines.append(f'{name:75s} {value:9.3f}')
    if (rule == 'zero' and value > 1e-6) or (rule == 'pos' and value <= 0):
        fail.append(name)
print('\n'.join(lines))

# Strip model for the 0.15 mm strip in the real carriage (Node)
model = json.loads(subprocess.run(['node', os.path.join(HERE, 'strip_pull.mjs')], check=True,
                                  capture_output=True, text=True).stdout)
with open(os.path.join(HERE, '..', '..', 'results', 'strip-end-clamp', 'strip_pull.json'), 'w') as f:
    json.dump(model, f, indent=1)

g = dict(base2=base2, top=top, top_long=top_long, sc=sc, parts=set_parts, model=model)
for f in ('fig_sections.py', 'fig_top_view.py', 'fig_strip_model.py'):
    runpy.run_path(os.path.join(HERE, f), init_globals=g)
print('figures written to', os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'strip-end-clamp')))
if fail:
    raise SystemExit('FAILED: ' + '; '.join(fail))
