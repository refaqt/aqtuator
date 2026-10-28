"""Plots of the strip model for the 0.15 mm strip in the real carriage."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# model and OUT come from run.py
C = dict(clash='#d62728', roller='#1f5fa8')
fig, axs = plt.subplots(1, 3, figsize=(17, 5.6))
ax = axs[0]
fr = model['free']
ax.plot([r['T'] for r in fr], [r['arch'] for r in fr], 'o-', color=C['roller'])
ax.axhline(model['ceilingGap'], color=C['clash'], lw=1)
ax.text(260, model['ceilingGap'] + 0.15, f"room under the ceiling: {model['ceilingGap']:.2f} mm", color=C['clash'], fontsize=8)
ax.axhline(1.3, color='0.4', lw=0.8, ls='--')
ax.text(260, 1.38, '1.3 mm', color='0.3', fontsize=8)
ax.axvline(125, color='0.4', lw=0.8, ls=':')
ax.set_xlabel('pull in the strip [N]'); ax.set_ylabel('bow above the bottom roller tops [mm]')
ax.set_title('A. How high the strip bows between the bottom\nrollers, with nothing above it', fontsize=10)
ax.set_ylim(0, 8.5); ax.grid(alpha=.3)

ax = axs[1]
for raise_, c in [('0', C['clash']), ('0.5', '#e8833a'), ('1', '#b39b2c'), ('1.5', '#5a9a5a'), ('2', C['roller'])]:
    rows = model['raised'][raise_]
    ax.plot([r['T'] for r in rows], [r['contact'] for r in rows], 'o-', color=c, ms=3,
            label=f'ceiling as drawn' if raise_ == '0' else f'ceiling {raise_} mm higher')
ax.axvline(125, color='0.4', lw=0.8, ls=':')
ax.set_xlabel('pull in the strip [N]'); ax.set_ylabel('force of the strip on carriage-top [N]')
ax.set_title('B. How hard the strip presses on carriage-top\n(both carriage ends together)', fontsize=10)
ax.legend(fontsize=8); ax.grid(alpha=.3)

ax = axs[2]
for raise_, c in [('0', C['clash']), ('1', '#b39b2c'), ('2', C['roller'])]:
    rows = model['raised'][raise_]
    ax.plot([r['du'] for r in rows], [r['T'] for r in rows], 'o-', color=c, ms=3,
            label=f'ceiling as drawn' if raise_ == '0' else f'ceiling {raise_} mm higher')
ax.axhline(125, color='0.4', lw=0.8, ls=':')
ax.set_xlabel('travel of both strip ends together, from the 125 N point [mm]')
ax.set_ylabel('pull in the strip [N]')
ax.set_title('C. Pull against travel: 0.1 mm of travel\nchanges the pull by 50 to 100 N', fontsize=10)
ax.legend(fontsize=8); ax.grid(alpha=.3)
fig.suptitle(f"Strip model: 0.15 mm strip, {model['W']} mm wide, real carriage layout, bottom rollers 1.5 mm proud, "
             'top rollers raised to touch the strip', fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'strip_model.png'), dpi=110)
