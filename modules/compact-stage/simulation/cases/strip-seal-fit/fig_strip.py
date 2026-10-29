"""Plot the seal strip of the chosen fit in the channel between the carriage halves.

Run from the repository root after fit.mjs:
    python modules/compact-stage/simulation/cases/strip-seal-fit/fig_strip.py
"""
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = Path(__file__).resolve().parents[2] / "results" / "strip-seal-fit"
fit = json.loads((RES / "fit.json").read_text())
drop, pull = fit["pick"]["drop"], fit["pick"]["T"]
rows = list(csv.DictReader(open(RES / "profile.csv")))
x = [float(r["x_from_roller1_mm"]) for r in rows]
z = [float(r["z_centre_mm"]) for r in rows]
t = 0.15
a, b = 155.603 - 118.77, 112.0
tan = math.tan(math.radians(19.44))
x4 = 2 * a + b
xs = a - 8.45                      # end of the sloped ceiling of carriage-top
top = [(0, 40.5), (xs, 40.5 + tan * xs), (xs, 53.5), (x4 - xs, 53.5), (x4 - xs, 40.5 + tan * xs), (x4, 40.5)]
bot = [(a - 34, 39.5), (a, 51.5), (a + b, 51.5), (a + b + 34, 39.5)]
rollers = [(0, 45.0), (a, 47.0 - drop), (a + b, 47.0 - drop), (x4, 45.0)]

fig, axes = plt.subplots(2, 1, figsize=(11, 7))
for ax, lim in ((axes[0], (-40, x4 + 40)), (axes[1], (a - 25, a + 25))):
    ax.plot(*zip(*top), color="0.4", lw=1.5, label="carriage-top")
    ax.plot(*zip(*bot), color="0.6", lw=1.5, label="carriage-bottom")
    ax.axhline(40.0, color="0.8", lw=1, label="top of the base")
    for xc, zc in rollers:
        ax.add_patch(plt.Circle((xc, zc), 5, fill=False, color="tab:blue"))
    ax.plot(x, [v + t / 2 for v in z], color="tab:red", lw=1)
    ax.plot(x, [v - t / 2 for v in z], color="tab:red", lw=1, label="seal strip, 0.15 mm")
    ax.set_xlim(*lim)
    ax.set_aspect("equal" if ax is axes[1] else "auto")
    ax.set_xlabel("x from roller 1 (mm)")
    ax.set_ylabel("z (mm)")
axes[1].set_ylim(44, 55)
axes[0].legend(loc="upper right", fontsize=8)
axes[0].set_title(f"Seal strip at {pull} N, rollers 2 and 3 {drop} mm lower, no plastic strip")
axes[1].set_title("Close-up at roller 2")
fig.tight_layout()
fig.savefig(RES / "strip_fit.png", dpi=130)
print("wrote", RES / "strip_fit.png")
