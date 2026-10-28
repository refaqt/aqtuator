"""Run the strip model for the 0.15 mm seal strip in the real carriage, and draw the figure.

Run from the repository root:
    python modules/compact-stage/simulation/cases/strip-pull/run.py
Needs: numpy, matplotlib, and Node 18 or newer.
"""
import json, os, runpy, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'strip-pull'))
os.makedirs(OUT, exist_ok=True)

model = json.loads(subprocess.run(['node', os.path.join(HERE, 'strip_pull.mjs')], check=True,
                                  capture_output=True, text=True).stdout)
with open(os.path.join(OUT, 'strip_pull.json'), 'w') as f:
    json.dump(model, f, indent=1)
runpy.run_path(os.path.join(HERE, 'fig_strip_model.py'), init_globals=dict(model=model, OUT=OUT))
print('results written to', OUT)
