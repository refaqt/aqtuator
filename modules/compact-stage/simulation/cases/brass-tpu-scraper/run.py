"""Builds the brass and TPU scraper in memory, runs the fit checks and draws the figures.
Run from the repository root:
    python modules/compact-stage/simulation/cases/brass-tpu-scraper/run.py
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, '..', '..', 'results', 'brass-tpu-scraper')
os.makedirs(OUT, exist_ok=True)
OUT = os.path.abspath(OUT)

import checks  # noqa: E402
import figs    # noqa: E402

values, failures = checks.run()
with open(os.path.join(OUT, 'fit_checks.json'), 'w') as f:
    json.dump(values, f, indent=1, ensure_ascii=False)
for k, v in values.items():
    print(f'{k}: {v}')

S = figs.build()
figs.fig_sections(S, os.path.join(OUT, 'sections.png'))
figs.fig_bottom(os.path.join(OUT, 'bottom_view.png'))
figs.fig_top(S, os.path.join(OUT, 'top_view.png'))
figs.fig_lips(S, os.path.join(OUT, 'tpu_lips.png'))
figs.fig_roller_zone(S, os.path.join(OUT, 'roller_zone.png'))
figs.fig_3d(S, os.path.join(OUT, '3d_from_below.png'), os.path.join(OUT, '3d_from_above.png'))
print('figures written to', OUT)

if failures:
    print('FAILED:', *failures, sep='\n  ')
    sys.exit(1)
print('all fit checks pass')
