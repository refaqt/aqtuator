# 2026-09-29 — The cutting force page shows where chatter starts

**Role(s):** engineering, simulation, software

## Goal

Add chatter to the cutting force page. Show −1/min(Re G), with G the compliance at the stage,
for the three drives. Divide by the collocated ball screw, so no cutting stiffness is needed.
Check first that this is the right formula.

## Work Done

- The formula is right, with one point to make clear. For regenerative chatter in one direction
  the limit depth is a_lim = −1/(2·K·Re G) at the chatter frequency. The lowest value,
  −1/(2·K·min Re G), is stable at every spindle speed. So −1/min(Re G) does not change with the
  speed. The speed enters through the stability lobes: each lobe maps the phase of G to one
  spindle speed. The page shows the lobes, and the floor as a dashed line.
- The chatter chart uses the compliance for a true sine force. The compliance chart holds the force
  over each sample. That adds half a sample of lag and moves the real part by 10 to 25 %, so it is
  not used for chatter.
- The results table has a new row with the relative depth.
- The checks test the formula against the textbook result for one mass on a spring, and put each
  lobe point back into the loop equation.

Results at the defaults, depth before chatter at any speed:

| Drive | −1/min Re G | At | Relative |
| --- | --- | --- | --- |
| Linear motor | 7.54 N/µm | 365 Hz | 2.87 |
| Ball screw, motor encoder | 2.62 N/µm | 658 Hz | 1.00 |
| Ball screw, linear encoder | 4.16 N/µm | 660 Hz | 1.59 |

- The ball screw is weakest at the stage mode on the axial spring.
- The damping estimates decide the ratio. With damping 0.01 the linear motor is 5.9 times better.
  With 0.03 and 0.05 it is only 1.09 times better.

## Decisions Made

- Show the lobes and the floor, divided by the floor of the collocated ball screw.
- Use the compliance of a true sine force, not a held force, because chatter depends on the phase.

## Open Questions

- How soft are the tool and the spindle? They are in series with the stage. If they are softer,
  they set the chatter limit, and the three drives come closer together.
- What are the real damping ratios of the ball-screw drive?

## Next Steps

- [ ] Measure the frequency response of the ball-screw drive, and fit the damping.
- [ ] Add a tool and spindle compliance in series, from a tap test.
