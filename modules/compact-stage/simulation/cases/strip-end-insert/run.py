"""Check the strip end concept of Niels Bosmans against the CAD, with a corner pocket in carriage-top
and a spring end, run the membrane model of the strip, and draw the figures.

Run from the repository root:
    python modules/compact-stage/simulation/cases/strip-end-insert/run.py
Needs: cadquery-ocp, numpy, scipy, matplotlib, shapely, pillow. Does not need FreeCAD.
"""
import json, math, os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from insert import *  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'strip-end-insert'))
os.makedirs(OUT, exist_ok=True)
base = placed('base', 'base')
top = cut(placed('carriage-top', 'carriage_top'), pocket_cut())   # with the scraper pocket
bot = placed('carriage-bottom', 'carriage_bottom001')
sc = scraper()
tops = {'no corner pocket': top}
for k, L in CORNER_L.items():
    tops[f'corner pocket {L:g} mm'] = cut(top, corner_pocket_cut(L))


def overlap(a, b):
    return sum(vol(common(x, y)) for x in a for y in b)


def hollow_dist(cut_shape):
    """Thinnest wall between a new cut and an existing hollow of the base."""
    return dist(cut_shape, cut(box(-1, -1, 0, 60, 100, 40), base))


rows, fail = [], []


def check(name, value, rule=None):
    rows.append((name, round(value, 3)))
    print(f'{name:86s} {value:9.3f}')
    if (rule == 'zero' and value > 1e-6) or (rule == 'pos' and value <= 0):
        fail.append(name)


# Fixed end: insert in a groove, pulled by the countersunk screw (as drawn)
gc = groove_cut()
inside = common(gc, box(0, 0, 0, 440, 210, 40))
base_fixed = cut(base, gc)
ins, ins_loose, scr = insert(), insert(dx=TRAVEL), screw()
top_z = floor_z() + INS_H
sw = fuse(ins, swept(top_z))
check('fixed end: groove, tapped hole and magnet pockets outside solid base material [mm3]',
      vol(inside) - vol(common(inside, base)), 'zero')
check('fixed end: insert overlaps the base, set and loose [mm3]', overlap([ins, ins_loose], [base_fixed]), 'zero')
check('fixed end: insert overlaps the strip, set and loose [mm3]',
      overlap([ins], [strip()]) + overlap([ins_loose], [strip(TRAVEL)]), 'zero')
check('fixed end: screw overlaps the strip or the insert [mm3]', overlap([scr], [strip(), ins]), 'zero')
r_g = GROOVE_W / 2
check('fixed end: thinnest wall from the groove and its tapped hole to a hollow of the base [mm]',
      hollow_dist(fuse(box(XC - 3, YC - r_g, floor_z(), XC + 3, YC + r_g, Z_WALL + 1),
                       cyl(XC, YC, floor_z() - TAP_DEPTH, 0.8, TAP_DEPTH + 0.1))), 'pos')
for i, (mx, my) in enumerate(MAGNETS):
    check(f'magnet pocket {i + 1}: thinnest wall to a hollow of the base [mm]',
          hollow_dist(cyl(mx, my, Z_WALL - MAG_H - 0.2, MAG_D / 2 + 0.1, MAG_H + 1.2)), 'pos')
check('insert top above the strip top [mm]', top_z - Z_STRIP)
# The carriage comes from the stage middle: check against the insert drawn out towards the base end
for label, xe in CARRIAGE_END_X.items():
    d = xe - X0
    crash = label.startswith('dampers')
    for tname, t in tops.items():
        # the long pocket must clear in every case, the normal one up to the first damper touch
        must = 'zero' if (f'{CORNER_L["crash"]:g} mm' in tname or
                          (f'{CORNER_L["normal"]:g} mm' in tname and not crash)) else None
        check(f'{label}: carriage-top, {tname}, passes over the insert, overlap [mm3]', overlap([shift(t, d)], [sw]), must)
    check(f'{label}: scraper lips as they are, pass over the insert, overlap [mm3]', overlap([shift(sc, d)], [sw]))
    check(f'{label}: carriage-bottom overlaps insert [mm3]', overlap([shift(bot, d)], [sw]), 'zero')
    check(f'{label}: top rollers overlap insert [mm3]', overlap(roller_cyls(d), [sw]), 'zero')
    check(f'{label}: scraper lips must step back to this distance from the end face [mm]', XC + INS_D / 2 + CLEAR - xe)
check('corner pocket removes from carriage-top, normal length [mm3]', vol(common(top, corner_pocket_cut(CORNER_L['normal']))))
# Stepped scraper lips, carried by a scraper that grows into a deeper corner pocket
top_st = cut(tops[f'corner pocket {CORNER_L["normal"]:g} mm'], scraper_pocket_corner_cut())
sc_st = scraper_stepped()
check('stepped scraper overlaps carriage-top with its corner pockets [mm3]', overlap([sc_st], [top_st]), 'zero')
check('stepped scraper overlaps the top rollers [mm3]', overlap([sc_st], roller_cyls(0)), 'zero')
check('deeper corner pocket to the top roller pockets and the slope opening [mm]',
      dist(scraper_pocket_corner_cut(), cut(box(X0 + 7, 15.2, Z_TOP_UNDER, X0 + 25, 60, Z_TOP_UNDER + P_DEPTH + 1), top)))
for label in ('usable travel end', 'first damper touch'):
    d = CARRIAGE_END_X[label] - X0
    check(f'{label}: stepped scraper passes over the insert, overlap [mm3]', overlap([shift(sc_st, d)], [sw]), 'zero')
    check(f'{label}: carriage-top with deeper corner pocket passes over the insert, overlap [mm3]',
          overlap([shift(top_st, d)], [sw]), 'zero')
d = CARRIAGE_END_X['dampers fully pressed'] - X0
check('dampers fully pressed: stepped scraper passes over the insert, overlap [mm3]', overlap([shift(sc_st, d)], [sw]))

# Spring end
spc = spring_pocket_cut()
inside = common(spc, box(0, 0, 0, 440, 210, 40))
base_spring = cut(base, spc)
sl, hd, spg = slider(), hold_down(), spring()
ins_s, scr_s = insert(z0=SLIDER_TOP), screw()
check('spring end: spring pocket and tapped hole outside solid base material [mm3]', vol(inside) - vol(common(inside, base)), 'zero')
check('spring end: thinnest wall from the spring pocket to a hollow of the base [mm]', hollow_dist(spc), 'pos')
check('spring end: slider, spring, screws overlap the base [mm3]', overlap([sl, spg, ins_s], [base_spring]), 'zero')
check('spring end: slider overlaps spring, insert or hold-down screw [mm3]', overlap([sl], [spg, ins_s, hd]), 'zero')
check('spring end: strip overlaps the slider, spring or insert [mm3]', overlap([strip(spring_end=True)], [sl, spg, ins_s]), 'zero')
check('spring end: pocket length along the travel [mm]', spring_seat_x() - SP_POCKET_X0)

# Spring numbers (textbook formulas; wire values typical, to be taken from the maker's catalogue)
k = spring_rate()
c = SPRING_D_MEAN / SPRING_D_WIRE
wahl = (4 * c - 1) / (4 * c - 4) + 0.615 / c
tau = 8 * PULL_PER_INSERT * SPRING_D_MEAN / (math.pi * SPRING_D_WIRE ** 3) * wahl
solid = (SPRING_N + 2) * SPRING_D_WIRE
work = SPRING_FREE - PULL_PER_INSERT / k
k_end = 2 * k
arch = (500.0, 1000.0)                             # N/mm, from the strip-pull case
k_series = [1 / (1 / k_end + 1 / a) for a in arch]
spring_numbers = dict(
    rate_N_per_mm=k, compression_mm=PULL_PER_INSERT / k, working_length_mm=work, solid_length_mm=solid,
    reserve_to_solid_N=(work - solid) * k, shear_stress_MPa=tau, index=c,
    pull_change_per_0p1mm_N=[0.1 * ks for ks in k_series],
    pull_change_per_0p1mm_without_spring_N=[0.1 * a for a in arch],
    thermal_mm_per_10K=7e-6 * 430 * 10,
)
for kk, v in spring_numbers.items():
    print(f'spring: {kk:40s} {v}')
with open(os.path.join(OUT, 'fit_checks.json'), 'w') as f:
    json.dump(dict(checks=rows, spring=spring_numbers), f, indent=1)

g = dict(OUT=OUT, top=top, tops=tops, top_st=top_st, sc_st=sc_st, sw=sw, bot=bot, sc=sc, base_fixed=base_fixed, base_spring=base_spring,
         parts=dict(insert=ins, screw=scr, insert_s=ins_s, slider=sl, hold=hd, spring=spg))
for f in ('membrane.py', 'fig_sections.py', 'fig_overlay.py', 'fig_spring.py'):
    runpy.run_path(os.path.join(HERE, f), init_globals=g)
print('results written to', OUT)
if fail:
    raise SystemExit('FAILED: ' + '; '.join(fail))
