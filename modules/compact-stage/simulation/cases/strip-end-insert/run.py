"""Check the strip end concept of Niels Bosmans against the CAD, run the membrane model of the
strip end, and draw the figures.

Run from the repository root:
    python modules/compact-stage/simulation/cases/strip-end-insert/run.py
Needs: cadquery-ocp, numpy, scipy, matplotlib, shapely, pillow. Does not need FreeCAD.
"""
import json, os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from insert import *  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'strip-end-insert'))
os.makedirs(OUT, exist_ok=True)
base = placed('base', 'base')
top = cut(placed('carriage-top', 'carriage_top'), pocket_cut())   # with the scraper pocket
bot = placed('carriage-bottom', 'carriage_bottom001')
sc = scraper()


def overlap(a, b):
    return sum(vol(common(x, y)) for x in a for y in b)


rows, fail, shapes = [], [], {}
for variant in VARIANTS:
    gc = groove_cut(variant)
    inside = common(gc, box(0, 0, 0, 440, 210, 40))
    base2 = cut(base, gc)
    ins, ins_loose, scr = insert(variant), insert(variant, TRAVEL), screw(variant)
    shapes[variant] = dict(base2=base2, insert=ins, screw=scr)
    checks = [
        ('groove, tapped hole and magnet pockets outside solid base material [mm3]',
         vol(inside) - vol(common(inside, base)), 'zero'),
        ('insert overlaps the base, set and loose [mm3]', overlap([ins, ins_loose], [base2]), 'zero'),
        ('insert overlaps the strip, set and loose [mm3]', overlap([ins], [strip()]) + overlap([ins_loose], [strip(TRAVEL)]), 'zero'),
        ('screw overlaps the strip or the insert [mm3]', overlap([scr], [strip(), ins]), 'zero'),
        ('insert top above the strip top [mm]', floor_z(variant) + INS_H - Z_STRIP, None),
        ('groove to the half-round pocket in the corner [mm]', dist(gc, cut(box(4, 17, 10, 16, 29, 40), base)), None),
        ('magnet pocket to the damper pocket [mm]', dist(cyl(*MAGNETS[1], Z_WALL - 2.2, 3.1, 2.2), cut(box(3, 52.5, 17.5, 10, 76.5, 40), base)), None),
    ]
    for label, xe in CARRIAGE_END_X.items():
        d = xe - X0
        t, s, b = shift(top, d), shift(sc, d), shift(bot, d)
        # the insert as drawn stands proud and is expected to hit: those numbers are reported only
        report_only = label.startswith("dampers") or variant == "as drawn"
        checks += [
            (f'{label}: carriage-top overlaps insert or screw [mm3]', overlap([t], [ins, scr]), None if report_only else 'zero'),
            (f'{label}: scraper overlaps insert or screw [mm3]', overlap([s], [ins, scr]), None if report_only else 'zero'),
            (f'{label}: scraper lips to the insert [mm]', dist(s, ins), None),
            (f'{label}: carriage-bottom overlaps insert or screw [mm3]', overlap([b], [ins, scr]), None if report_only else 'zero'),
            (f'{label}: top rollers overlap insert or screw [mm3]', overlap(roller_cyls(d), [ins, scr]), None),
        ]
    for name, value, rule in checks:
        rows.append((variant, name, round(value, 3)))
        print(f'{variant:9s} {name:78s} {value:9.3f}')
        if (rule == 'zero' and value > 1e-6) or (rule == 'pos' and value <= 0):
            fail.append(f'{variant}: {name}')
with open(os.path.join(OUT, 'fit_checks.json'), 'w') as f:
    json.dump(rows, f, indent=1)

g = dict(OUT=OUT, top=top, bot=bot, sc=sc, shapes=shapes)
for f in ('membrane.py', 'fig_sections.py', 'fig_overlay.py'):
    runpy.run_path(os.path.join(HERE, f), init_globals=g)
print('results written to', OUT)
if fail:
    raise SystemExit('FAILED: ' + '; '.join(fail))
