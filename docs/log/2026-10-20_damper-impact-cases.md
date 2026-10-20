# 2026-10-20 — When can the carriage hit the end damper hard?

**Role(s):** engineering

## Goal

The damper sizing page assumes a runaway: the motor pushes with full force over the whole travel,
and the carriage hits the damper at 3.80 m/s while the motor still pushes. The user asked whether
this case can really happen. If the encoder is lost, the drive should switch off. If the encoder
works, the drive measures the speed and can limit it. Find the cases that really give a hard
impact, and the energy the damper must take in each.

## Work Done

### Short answer

- **The user is right about the full runaway.** It needs a drive that keeps the motor turning on
  correctly, so it needs a working encoder. With a working encoder, an overspeed trip in the drive
  stops it. Only a drive whose own limits fail, or are set wrong, can give it.
- **But a speed limit saves less than it seems.** The stage must reach 3 m/s in normal use
  (STG-09). The runaway speed is 3.80 m/s, only 27 % more. At 3 m/s the carriage still brings
  22.5 J, against 36.1 J for the runaway.
- **The real gains are elsewhere.** First, the motor must not push during the impact. Second, the
  carriage should move slowly near the ends. Third, check whether the stage really needs 3 m/s.
- **Proposed design case:** impact at the overspeed trip speed (about 3.3 m/s, 27 J), motor off.
  With slow end zones and an absolute encoder, this drops to a few joules.

### Why a linear synchronous motor cannot run away on its own

The MK21 is a synchronous motor. It pushes only when the drive turns the current in step with the
position of the carriage, every 30 mm. The drive needs the encoder for this.

- **No encoder signal:** the drive cannot turn the current in step. A fixed current pulls the
  carriage to the nearest magnet pole and holds it there. It does not speed up the carriage.
- **A broken power transistor in the drive:** the same. A fixed current gives a holding force that
  changes direction every half pole, not a steady push.

So a steady push to 3.80 m/s needs a working encoder and a drive that ignores the speed it
measures.

### The cases one by one

| Case | Speed at impact | Motor pushes at impact? | What stops it |
| --- | --- | --- | --- |
| Encoder cable off or encoder broken | The speed at that moment, at most 3 m/s | No, the drive trips and the carriage rolls on | Feedback fault in the drive |
| Power cut or emergency stop | The speed at that moment, at most 3 m/s | No | Nothing. The carriage rolls on |
| Encoder works, but the position is wrong (lost counts, read head loose, wrong homing, wrong software limits) | Up to 3 m/s | **Yes, full force.** The control loop "thinks" it has room left | Only a limit switch that cuts the motor power |
| Wrong commutation (wrong angle after the start-up search, wrong phase order, wrong encoder direction) | About 3 m/s plus 0.13 m/s per millisecond of delay | Short, until the trip | Following error trip and overspeed trip |
| Wrong command from LinuxCNC, or the EtherCAT link drops | Up to 3 m/s | No, if the drive limits act | Position and speed limits in the drive |
| Unstable control loop during tuning | Grows until a trip | Short, until the trip | Overspeed or following error trip |
| Drive firmware fault, or speed limit switched off | 3.80 m/s (the runaway on the page) | Yes | Only a limit switch that cuts the motor power |

Two cases matter most:

1. **Rolling on after a trip.** The motor is off. The damper takes the kinetic energy only.
2. **Wrong position with a working encoder.** This is the dangerous one. The speed limit still
   works, but the motor pushes with full force into the damper. The page shows that a damper
   alone cannot stop a motor that keeps pushing. The limit switches must cut the motor power (safe
   torque off, STO) before the impact. An absolute encoder (EnDat 2.2, as in the DGSMARTWIN
   choice) removes lost counts and most homing errors.

### Energy at each speed (motor off, 5.0 kg, 15 mm damper)

Calculated with the model of the damper sizing page.

| Impact speed | Energy | Part of the 59 J rating | Even braking force | Deceleration |
| --- | --- | --- | --- | --- |
| 3.80 m/s (runaway) | 36.1 J | 61 % | 2.41 kN | 49 g |
| 3.3 m/s (trip at 10 % over 3 m/s) | 27.2 J | 46 % | 1.81 kN | 37 g |
| 3.0 m/s (STG-09) | 22.5 J | 38 % | 1.50 kN | 31 g |
| 2.0 m/s | 10.0 J | 17 % | 0.67 kN | 14 g |
| 1.0 m/s | 2.5 J | 4 % | 0.17 kN | 3 g |
| 0.5 m/s | 0.6 J | 1 % | 0.04 kN | 1 g |

The energy grows with the square of the speed. So the speed near the ends matters much more than
the top speed in the middle.

### Three ways to make the damper smaller

1. **Slow end zones.** Limit the speed in the last part of the travel, for example to 1 m/s. A
   carriage at 3 m/s needs about 34 mm to brake at full force (134 m/s²). This only helps if the
   position is right, so it works best with an absolute encoder.
2. **Short-circuit braking after a trip.** Some drives short the motor phases when they switch
   off (dynamic braking). The moving magnets then brake the carriage. For the MK21 the model gives
   about 160 N to 200 N between 3 m/s and 1 m/s. From 3 m/s the carriage slows to 0.1 m/s in about
   120 mm. That is more than half of the 218 mm travel, so it helps only in part. Check whether
   the chosen drive does this.
3. **A lower top speed.** If the chatter tests never need 3 m/s, a lower STG-09 lowers the energy
   with the square of the speed. 2 m/s gives 10 J instead of 22.5 J.

## Decisions Made

- **The stage needs 2 m/s, not 3 m/s.** The user decided this after reading the cases above. The
  damper sizing page now has a speed limit of the drive, set to 2 m/s by default. At 2 m/s the
  damper takes 10.0 J, 17 % of the 59 J rating. Set the limit to 0 to see the full runaway again.
- The stage requirement STG-09 still says 3 m/s. It is not changed yet, because the encoder and
  drive requirements follow from it.

## Open Questions

- What does the chosen drive do when the encoder signal is lost: switch off, short the phases, or
  brake under control? Read this in the drive manual. Do not assume it.
- Does the drive have a true overspeed trip that also acts in torque mode? A speed limit that only
  clamps the speed command does not act when LinuxCNC sends a force command.
- How fast does the drive react to an overspeed or a limit switch? Each millisecond at full force
  adds 0.13 m/s.
- Where do the limit switches sit? They must cut the motor power far enough before the damper.

## Next Steps

- Lower STG-09 to 2 m/s, and update the requirements that follow from it: the encoder signal
  frequency (DRV-08, 150 kHz becomes 100 kHz), the encoder speed (ENC-03) and the bus voltage note
  (DRV-04).
- Decide the design case for the damper: speed at impact, motor on or off.
- Add slow end zones and the overspeed trip to the drive requirements in
  `modules/compact-stage/architecture/motor-drive.sysml` once the team agrees.

<details>
<summary>Technical notes</summary>

- Numbers from `simulation/cases/damper-sizing/damper_model.js` at its defaults (5.0 kg, 15 mm
  stroke, 0.1 m/s end speed). "Even braking force" is the energy spread evenly over the damper
  stroke. It is the lowest peak force a 15 mm damper can have.
- Speed gained per millisecond: 670 N / 5.0 kg = 134 m/s², so 0.13 m/s per ms.
- Short-circuit braking: per phase, I = E / √(R_p² + (ω·L_p)²), with E = Ke/√3·v,
  R_p = 9.5 Ω (hot), L_p = 32 mH, ω = 2π·v/30 mm. Braking force F = 3·I²·R_p / v. Stepped in time
  from 3 m/s down to 0.1 m/s: 123 mm.
- The motor-on case with a damper sized by the page gives very high peak forces near the speed
  where damper and motor forces are equal. It confirms the page: do not design for a pushing motor,
  cut the power.

</details>
