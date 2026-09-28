# 2026-09-28 — The ball screw gets its axial stiffness, and loses most of its lead

**Role(s):** engineering, simulation, software

## Goal

The first ball-screw model treated the screw and the nut as rigid along the axis. That made the
ball screw look 10 to 20 times stiffer than the linear motor, and it was marked as an upper limit.
Add the real axial spring (screw shaft, nut and fixed bearing), with catalogue values, and see what
is left of that lead.

## Work Done

- The ball-screw drive on the cutting force page is now three masses in a chain: the motor rotor,
  the screw, and the stage. The coupling joins the rotor and the screw. The axial spring joins the
  screw and the stage.
- The axial spring is the screw shaft, the nut and the fixed bearing in series. The layout is a
  fixed bearing at the motor end and a supported far end, so only the shaft between the bearing and
  the nut carries the load. New inputs: screw root diameter, nut distance from the fixed bearing,
  nut stiffness, bearing stiffness, and a damping ratio for the axial spring.
- The defaults come from maker catalogues: root diameter 13.324 mm and nut stiffness 118 N/µm
  (HIWIN 16-5), bearing stiffness 104 N/µm (TBI Motion BK12). The sources are listed in the
  [case README](../../simulation/cases/cutting-force-rejection/README.md#sources-for-the-axial-stiffness).
- The tuning now also requires a stable closed loop. A random test found one very sharp resonance
  whose peak only just touched the limit, and no frequency grid could see it. The tuning also
  reuses the plant response while it searches, so it stays fast with the larger model.
- The mechanics diagram shows the fixed bearing, the support, the nut position and the axial
  spring.

Results at the defaults (nut 380 mm from the fixed bearing):

- **The axial spring is 32 N/µm**: shaft 76, nut 118, bearing 104 N/µm. The 2 kg stage bounces on
  it at 646 Hz.
- **The ball screw still moves less at 400 Hz, but it is no longer stiffer overall.** Vibration
  1.9 µm (motor encoder) and 3.3 µm (linear encoder), against 7.0 µm for the linear motor. The
  lowest stiffness is 3.9 and 4.8 N/µm, against 5.6 N/µm. With a rigid screw it was 64 and
  115 N/µm.
- **With the linear encoder, the stage mode limits the bandwidth to 127 Hz.** With the motor
  encoder it stays at 290 Hz, set by the coupling, but the stage then bounces with little help from
  the controller, and it stays 1.6 µm off under a 50 N mean force.
- **The nut position matters.** With the nut 100 mm from the fixed bearing, the vibration at
  400 Hz is 1.05 and 1.9 µm, and the lowest stiffness 5.3 and 7.6 N/µm.

## Decisions Made

- The HIWIN nut value is the default, because HIWIN states its condition (30 % of the dynamic load
  rating, no preload). TBI gives 314 N/µm for a similar nut but does not say at what load.
- The bearing value is used, but the sheet it comes from has an unclear column heading. The page
  says so next to the input.
- The axial damping ratio (0.05) is an estimate. No catalogue gives it.

## Open Questions

- Which nut, preload class and bearing would we buy? A preloaded nut and a closer nut position
  both help.
- At the small forces of a light cut, a nut without preload is softer than its catalogue value, and
  it can lose contact when the force changes sign. The model does not cover this.

## Next Steps

- [ ] Check the page on GitHub Pages after the merge.
- [ ] Measure the axial stiffness of the real drive, once it is built.
