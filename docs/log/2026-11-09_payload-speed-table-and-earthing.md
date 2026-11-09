# 2026-11-09 — Payload against speed table, damper overload, and earthing of the carriage

**Role(s):** engineering, safety

## Goal

Niels asked three things about the CE assessment of the compact stage: a table of largest payload
against top speed (he will set and lock the speed in the drive), what happens when the dampers are
overloaded, and whether the carriage can be earthed through the forcer.

## Short answer

- **Speed table:** with no payload the speed limit is about 2.3 m/s. With 5 kg it is about
  1.5 m/s, with 20 kg about 1.0 m/s. 3 m/s is not possible with today's dampers.
- **Overload:** mainly damage to the stage. A small danger from thrown parts, mainly a payload
  that is not fixed well.
- **Earthing:** yes, through the forcer and the earth wire of the motor cable, if the contact
  faces are bare metal. The guide blocks do not count. MAXWELL must confirm that the earth wire
  connects to the forcer body.
- New drive preference DRV-P6: settings locked with a password.
- Full text: [the CE assessment](../compact-stage-ce-assessment.md).

## Next Steps

1. Weigh the first carriage and correct the 4.2 kg estimate.
2. Ask MAXWELL (through Saho) for the MK21 cable wiring and the earth connection.
3. Decide whether the bottom carriage is anodised. If so, plan bare contact faces or an earth
   wire.
4. Check the drives on the list against DRV-P6.

<details>
<summary>Technical notes</summary>

- Formula and inputs are in the technical notes of the CE assessment.
- Changed: `docs/compact-stage-ce-assessment.md`, `compact-stage.sysml` (STG-15 text),
  `motor-drive.sysml` (DRV-P6 and one attribute), `docs/servo-drive-selection.md`,
  `modules/compact-stage/README.md`.

</details>
