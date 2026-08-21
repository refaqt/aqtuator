# Development log

Chronological record of work on this project. Entries follow the doqs dev-log
convention: `YYYY-MM-DD_topic.md`, newest listed last.

These 71 entries were converted from the original `log.docx` (itself an export of
the *AQTUATOR - project log* Google Doc). **Git is the source of truth from here on** —
the Google Doc is retained as a historical archive and is no longer edited.

To add an entry, see [`.claude/skills/dev-log/SKILL.md`](../../.claude/skills/dev-log/SKILL.md);
the template is [`doqs/templates/dev-log-entry.md`](../../doqs/templates/dev-log-entry.md).

| Date | Topic | Images |
| ---- | ----- | -----: |
| 2025-06-26 | [Chatter mass-spring-damper model](2025-06-26_chatter-mass-spring-damper-model.md) |  |
| 2025-06-27 | [High-Z axis Z-plate modification](2025-06-27_high-z-axis-z-plate-modification.md) |  |
| 2025-08-14 | [Z motor range PlanetCNC](2025-08-14_z-motor-range-planetcnc.md) |  |
| 2025-08-28 | [Accelerometer selection IEPE](2025-08-28_accelerometer-selection-iepe.md) |  |
| 2025-09-09 | [Xcos Coselica mass-spring-damper model](2025-09-09_xcos-coselica-mass-spring-damper.md) | 2 |
| 2025-09-22 | [Actuator power requirement](2025-09-22_actuator-power-requirement.md) |  |
| 2025-09-24 | [Chatter intuitive model](2025-09-24_chatter-intuitive-model.md) |  |
| 2025-09-25 | [Laplace domain system diagram](2025-09-25_laplace-domain-system-diagram.md) |  |
| 2025-09-30 | [Milling parameters cutting stability](2025-09-30_milling-parameters-cutting-stability.md) |  |
| 2025-10-06 | [Experiment parameters tool stickout](2025-10-06_experiment-parameters-tool-stickout.md) |  |
| 2025-10-08 | [Inertia matching research](2025-10-08_inertia-matching-research.md) |  |
| 2025-10-09 | [Maximum cutting depth vs damping and stiffness](2025-10-09_max-cutting-depth-damping-stiffness.md) | 2 |
| 2025-10-10 | [Tool experiments](2025-10-10_tool-experiments.md) |  |
| 2025-10-14 | [Rotary encoder for commutation](2025-10-14_rotary-encoder-for-commutation.md) |  |
| 2025-10-16 | [Spindle speed verification](2025-10-16_spindle-speed-verification.md) |  |
| 2025-10-17 | [Meeting notes](2025-10-17_meeting-notes.md) |  |
| 2025-10-21 | [Shaft coupling selection](2025-10-21_shaft-coupling-selection.md) |  |
| 2025-11-03 | [Opta A0602 analog outputs](2025-11-03_opta-a0602-analog-outputs.md) |  |
| 2025-11-04 | [Servo motor setup](2025-11-04_servo-motor-setup.md) | 5 |
| 2025-11-05 | [Brake resistor and analog mapping](2025-11-05_brake-resistor-and-analog-mapping.md) |  |
| 2025-11-12 | [Thesis meeting](2025-11-12_thesis-meeting.md) |  |
| 2025-11-14 | [Opta analog bandwidth limit](2025-11-14_opta-analog-bandwidth-limit.md) |  |
| 2025-11-20 | [Arduino Giga system identification](2025-11-20_arduino-giga-system-identification.md) |  |
| 2025-11-24 | [Dampers and stops](2025-11-24_dampers-and-stops.md) |  |
| 2025-11-26 | [ODrive analog input stuck at 4 V](2025-11-26_odrive-analog-input-stuck-4v.md) |  |
| 2025-11-27 | [Stepper drive pulse/direction control](2025-11-27_stepper-drive-pulse-direction.md) | 1 |
| 2025-12-01 | [High speed circular motion steppers](2025-12-01_high-speed-circular-motion-steppers.md) |  |
| 2025-12-03 | [Linear encoder design](2025-12-03_linear-encoder-design.md) | 1 |
| 2025-12-10 | [NUCLEO ODrive CAN connection](2025-12-10_nucleo-odrive-can-connection.md) | 2 |
| 2025-12-18 | [Controllino CAN timing](2025-12-18_controllino-can-timing.md) |  |
| 2025-12-19 | [Stepper motor stiffness](2025-12-19_stepper-motor-stiffness.md) |  |
| 2026-01-06 | [Controllino ODrive CAN communication](2026-01-06_controllino-odrive-can-communication.md) | 1 |
| 2026-01-07 | [Multisine upload CAN torque](2026-01-07_multisine-upload-can-torque.md) |  |
| 2026-01-08 | [Controllino analog inputs](2026-01-08_controllino-analog-inputs.md) |  |
| 2026-01-09 | [Thesis meeting](2026-01-09_thesis-meeting.md) |  |
| 2026-01-12 | [ODrive limitations](2026-01-12_odrive-limitations.md) |  |
| 2026-01-15 | [E-stop design](2026-01-15_e-stop-design.md) |  |
| 2026-01-19 | [Thesis meeting](2026-01-19_thesis-meeting.md) |  |
| 2026-01-22 | [Z-axis accelerometer redesign](2026-01-22_z-axis-accelerometer-redesign.md) | 1 |
| 2026-01-27 | [Machine stiffness measurement](2026-01-27_machine-stiffness-measurement.md) |  |
| 2026-01-28 | [Controllino MCP analog scaling](2026-01-28_controllino-mcp-analog-scaling.md) |  |
| 2026-01-29 | [Stepper driver survey](2026-01-29_stepper-driver-survey.md) |  |
| 2026-02-02 | [Stability testing aluminium](2026-02-02_stability-testing-aluminium.md) |  |
| 2026-02-04 | [Steel cutting settings](2026-02-04_steel-cutting-settings.md) |  |
| 2026-02-05 | [Nanotec driver evaluation](2026-02-05_nanotec-driver-evaluation.md) |  |
| 2026-02-06 | [Controllino digital input shortage](2026-02-06_controllino-digital-input-shortage.md) |  |
| 2026-02-09 | [ODrive servo identification](2026-02-09_odrive-servo-identification.md) |  |
| 2026-02-12 | [Thesis meeting](2026-02-12_thesis-meeting.md) |  |
| 2026-02-24 | [Electrical cabinet electronics](2026-02-24_electrical-cabinet-electronics.md) | 1 |
| 2026-03-04 | [PlanetCNC step/dir/enable signals](2026-03-04_planetcnc-step-dir-enable.md) | 5 |
| 2026-03-05 | [RS-422 to TTL line receiver](2026-03-05_rs422-to-ttl-line-receiver.md) |  |
| 2026-03-10 | [ODrive motor noise on accelerometers](2026-03-10_odrive-motor-noise-on-accelerometers.md) | 2 |
| 2026-03-19 | [ODrive GUI configuration](2026-03-19_odrive-gui-configuration.md) | 7 |
| 2026-03-20 | [Stepper eigenfrequency](2026-03-20_stepper-eigenfrequency.md) |  |
| 2026-03-25 | [ODrive analog torque input](2026-03-25_odrive-analog-torque-input.md) | 9 |
| 2026-03-26 | [ODrive analog input mapping](2026-03-26_odrive-analog-input-mapping.md) |  |
| 2026-03-30 | [ODrive motor thermistor](2026-03-30_odrive-motor-thermistor.md) |  |
| 2026-03-31 | [Multisine identification](2026-03-31_multisine-identification.md) | 6 |
| 2026-04-01 | [Accelerometer system identification](2026-04-01_accelerometer-system-identification.md) | 5 |
| 2026-04-03 | [System non linearities](2026-04-03_system-non-linearities.md) | 4 |
| 2026-04-13 | [ODrive linear encoder integration](2026-04-13_odrive-linear-encoder-integration.md) | 1 |
| 2026-04-15 | [Meeting Joppe](2026-04-15_meeting-joppe.md) | 1 |
| 2026-04-16 | [Stability with flexibility](2026-04-16_stability-with-flexibility.md) | 4 |
| 2026-04-17 | [CAN cyclic identification](2026-04-17_can-cyclic-identification.md) |  |
| 2026-04-21 | [Linear motor suppliers](2026-04-21_linear-motor-suppliers.md) |  |
| 2026-04-22 | [FRF: flexible suspension vs stepper](2026-04-22_frf-flexible-vs-stepper.md) | 3 |
| 2026-04-24 | [Tap test reciprocating motion](2026-04-24_tap-test-reciprocating-motion.md) | 4 |
| 2026-04-29 | [Revert to stepper motors](2026-04-29_revert-to-stepper-motors.md) |  |
| 2026-05-07 | [FRF and compliance measurements](2026-05-07_frf-and-compliance-measurements.md) | 9 |
| 2026-05-20 | [Results so far](2026-05-20_results-so-far.md) |  |
| 2026-08-21 | [New ideas](2026-08-21_new-ideas.md) |  |
| 2026-08-21 | [doqs restructure](2026-08-21_doqs-restructure.md) |  |
