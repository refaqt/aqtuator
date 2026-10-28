"""The spring end: plan view and section, from the CAD geometry and the modelled parts."""
import json
from fig_common import *  # noqa: F401,F403

# OUT, base_spring, parts come from run.py
sp = json.load(open(os.path.join(OUT, 'fit_checks.json')))['spring']
fig, axs = plt.subplots(2, 1, figsize=(14, 11), gridspec_kw=dict(height_ratios=[1, 1.05]))
ax = axs[0]
for sgm in section(base_spring, (0, 0, 39.95), (0, 0, 1), 24):
    ax.plot([p[0] for p in sgm], [p[1] for p in sgm], color='k', lw=0.8)
for shp, c, z in [(parts['slider'], '#9fb7d9', 38.0), (parts['spring'], '#7a7a7a', SPRING_AXIS_Z),
                  (parts['hold'], C['screw'], 38.6), (parts['insert_s'], C['insert'], 40.3)]:
    draw(ax, poly(shp, (0, 0, z), (0, 0, 1), 0, 1), c)
draw(ax, poly(strip(spring_end=True), (0, 0, Z_WALL + T / 2), (0, 0, 1), 0, 1), (0.2, 0.8, 0.9, 0.25), lw=0.8)
ax.set_xlim(-2, 50); ax.set_ylim(30, -2); ax.set_aspect('equal'); ax.grid(alpha=.25)
ax.set_xlabel('x from the base end [mm]'); ax.set_ylabel('y from the base side [mm]')
ax.set_title('A. Spring end from above. The strip ear (blue) covers the spring pocket.', fontsize=10)
note(ax, 'slider, steel', (8, 6), (1, 26))
note(ax, 'insert and M2 screw', (XC, YC - 2.5), (12, 0.5))
note(ax, 'spring', (27, YC), (32, 24))
note(ax, 'pocket milled from the top,\n8.5 x 30 mm, 8.5 mm deep', (34, 5.5), (36, 1))
note(ax, 'M2 hold-down with sleeve', (HOLD_X, YC + 1.5), (1, 19))

ax = axs[1]
for shp, c in [(base_spring, C['base']), (parts['slider'], '#9fb7d9'), (parts['spring'], '#7a7a7a'),
               (parts['hold'], C['screw']), (parts['insert_s'], C['insert']), (screw(), C['screw'])]:
    draw(ax, poly(shp, (0, YC, 0), (0, 1, 0), 0, 2), c)
draw(ax, poly(strip(spring_end=True), (0, YC, 0), (0, 1, 0), 0, 2), C['strip'], lw=1.0)
ax.set_xlim(-2, 50); ax.set_ylim(29, 43); ax.set_aspect('equal'); ax.grid(alpha=.25)
ax.set_xlabel('x from the base end [mm]'); ax.set_ylabel('z [mm]')
ax.set_title(f'B. Section through the insert and the spring (y = {YC} mm)', fontsize=10)
note(ax, 'strip pulls this way', (XC + 4, 40.5), (24, 42))
ax.annotate('', xy=(XC + 8, 40.6), xytext=(XC + 3, 40.6), arrowprops=dict(arrowstyle='->', lw=1))
note(ax, 'spring pushes the slider\ntowards the base end', (28, SPRING_AXIS_Z), (36, 31))
txt = (f"Spring: stainless spring wire Ø{SPRING_D_WIRE} mm, mean Ø{SPRING_D_MEAN} mm, {SPRING_N} active turns, free length "
       f"{SPRING_FREE:g} mm.\nRate {sp['rate_N_per_mm']:.1f} N/mm, {PULL_PER_INSERT:g} N at {sp['compression_mm']:.1f} mm compression, "
       f"shear stress about {sp['shear_stress_MPa']:.0f} MPa,\n{sp['reserve_to_solid_N']:.0f} N more before it is solid. "
       f"Two springs at one end: 0.1 mm of travel changes the pull by about {sp['pull_change_per_0p1mm_N'][0]:.1f} N\n"
       f"instead of {sp['pull_change_per_0p1mm_without_spring_N'][0]:.0f} to {sp['pull_change_per_0p1mm_without_spring_N'][1]:.0f} N without a spring. "
       "Wire values are typical: take the real spring from a catalogue.")
fig.text(0.06, 0.01, txt, fontsize=9, va='bottom')
fig.suptitle('Spring end: the inserts sit on sliders that springs push towards the base end', fontsize=11)
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(os.path.join(OUT, 'spring_end.png'), dpi=110)
