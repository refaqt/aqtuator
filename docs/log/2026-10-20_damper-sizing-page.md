# 2026-10-20 — A web page to size the end dampers of the compact stage

**Role(s):** engineering, simulation

## Goal

The compact stage needs a damper at each end. Build a web page, like the strip seal designer, that
takes the moving mass, the acceleration stroke and the maximum force, finds the impact speed, sizes
the damper, and shows how the energy goes into the damper along its stroke.

## Work Done

- Built the page in [`simulation/cases/damper-sizing/`](../../simulation/cases/damper-sizing/).
  The user can set the stage, the motor and drive, the damper stroke, the damper force law
  F = c·vⁿ (n = 1 or 2), the speed allowed at the end of the stroke, and the catalog rating.
- The motor model uses the drive voltage, the back voltage, the resistance and the inductance of
  the MAXWELL MK21. So the speed levels off near the no-load speed, as it does in the real motor.
- A check script tests the model against exact formulas. CI runs it, and the Pages workflow
  publishes the page at <https://refaqt.github.io/aqtuator/damper/>.

Results at the defaults (5.0 kg, 218 mm, 670 N, 310 V bus, hot coil, 15 mm damper):

- **Impact speed 3.80 m/s, 36.1 J.** That is 61 % of the 59 J rating of the Misumi two-stage M20
  damper. The Misumi numbers come from search results and still need checking on the Misumi page.
- **A damper with one fixed orifice brakes far too hard at first.** Its peak force is 17.5 kN. An
  even-force damper with the same stroke needs only 2.4 kN. Choose a catalog shock absorber with
  several orifices, or an adjustable one.
- **If the motor keeps pushing, a damper alone cannot stop the carriage.** The limit switches must
  switch the drive off before the impact (safe torque off, or the drive's limit inputs).

Open points:

- Check the Misumi energy rating, return spring force, body length and lowest equivalent mass.
- 218 mm of travel leaves only 1 mm at each end before the blocks hit. A 15 mm damper does not fit.
  Choose between less travel, a longer base, or slow end zones.
