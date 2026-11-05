# 2026-11-05 — The MK21 thermal sensor is now known

**Role(s):** electrical engineering

## What changed

We now know the heat sensor in the MK21 linear motor. It is three PTC thermistors in series. A
PTC thermistor is a resistor whose resistance rises steeply when it gets too hot. MAXWELL sent a
table with its resistance values.

- At 25 °C it reads 300 Ω or less.
- 5 °C below its switch point it reads 1 650 Ω or less.
- 5 °C above its switch point it reads 3 990 Ω or more.
- It must never see more than 30 V.

The switch point (rated response temperature) is very likely 120 °C. The sensor name "SNM120"
points to it, but MAXWELL has not said it in writing yet.

The drive requirement for the motor heat sensor (DRV-06) now uses these values. It no longer says
"type not known". The two drives that were waiting for the sensor type now pass this
requirement: the Servotronix CDHD2S and the Delta ASDA-A3. Both have a PTC input.

## Why it matters

Before, every drive check had to say "pass, if MAXWELL confirms the sensor type". Now a drive can
be checked directly. Any drive with a PTC input and a trip point between 1 650 Ω and 3 990 Ω fits.
A drive that only reads KTY, PT100 or PT1000 sensors does not fit, because those sensors measure
the temperature in a straight line. This matters for the Akribis AGD155 offer: its input reads
PT100, PT1000 or an on/off thermostat, so ask Akribis if the thermostat mode accepts a PTC.

## Next Steps

- Ask MAXWELL to confirm in writing that the switch point is 120 °C.
- Ask Akribis if the AGD155 thermostat input works with three PTC thermistors in series.
- Move the STOQ parts library pin in this repository once the STOQ change is merged. Until then
  the link to the sensor page in the drive selection page opens nothing.

<details>
<summary>Technical notes</summary>

- `modules/compact-stage/architecture/motor-drive.sysml`: `MaxwellMK21` has new attributes for
  the sensor (`thermalSensorResponseTemperature`, `thermalSensorResistanceAt25C`,
  `thermalSensorResistanceCold`, `thermalSensorResistanceBelowTk`,
  `thermalSensorResistanceAboveTk`, `thermalSensorResistanceHot`, `thermalSensorMaxVoltage`,
  `thermalSensorResponseTime`). `thermalSensor` now reads "3 PTC SNM120 in series". The DRV-06
  text says the type is known and gives the pass rule.
- `docs/servo-drive-selection.md`: DRV-06 row, the CDHD2S and ASDA-A3 cells, and a link to the
  sensor page.
- The full table is in STOQ at
  `modules/maxwell/modules/mk2-mover/docs/mk21-thermal-sensor.md`, on branch
  `claude/compassionate-albattani-7vu2yu`, not yet merged.
- Older log entries still say the type is unknown. They are history and stay as they were.
- `bash doqs.sh check` passes. The number of warnings did not change.

</details>
