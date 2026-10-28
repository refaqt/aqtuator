"""Build the scraper, check that it fits, and draw the figures.

Run from the repository root:
    python modules/compact-stage/simulation/cases/scraper-fit/run.py
Needs: cadquery-ocp, numpy, matplotlib, shapely. Does not need FreeCAD.
"""
import os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scraper import *  # noqa: E402  (unzips the CAD files)

top = placed('carriage-top', 'carriage_top')
bot = placed('carriage-bottom', 'carriage_bottom001')
base = placed('base', 'base')
sc = scraper()
top2 = cut(top, pocket_cut())
strip = box(0, 12, 40, 440, 198, Z_STRIP_TOP)
checks = [
    ('scraper overlaps carriage-top with pocket [mm3]', vol(common(sc, top2)), 0.0),
    ('scraper overlaps carriage-bottom [mm3]', vol(common(sc, bot)), 0.0),
    ('scraper overlaps base [mm3]', vol(common(sc, base)), 0.0),
    ('scraper to carriage-bottom [mm]', dist(sc, bot), None),
    ('scraper to base [mm]', dist(sc, base), None),
    ('lip tip to strip [mm]', dist(sc, strip), None),
    ('screw head to strip [mm]', min(dist(s, strip) for s in screws()), None),
    ('rollers overlap carriage-top (roller model check) [mm3]', sum(vol(common(r, top)) for r in rollers()), 0.0),
    ('roller to carriage-bottom (log of 2026-10-22: 0.32) [mm]', min(dist(r, bot) for r in rollers()), None),
    ('scraper overlaps the rollers [mm3]', sum(vol(common(sc, r)) for r in rollers()), 0.0),
    ('scraper to the rollers [mm]', min(dist(sc, r) for r in rollers()), None),
    ('screws to the rollers [mm]', min(dist(s, r) for s in screws() for r in rollers()), None),
]
for name, value, must in checks:
    print(f'{name:50s} {value:8.3f}')
    if must is not None and value > 1e-6:
        raise SystemExit(f'FAILED: {name}')
for f in ('fig_sections.py', 'fig_drawing.py', 'fig_3d.py'):
    runpy.run_path(os.path.join(HERE, f))
print('figures written to', os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'scraper-fit')))
