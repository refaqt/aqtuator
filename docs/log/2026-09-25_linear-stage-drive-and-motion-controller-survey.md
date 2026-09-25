# 2026-09-25 — Drives and a motion controller for the MK21 linear stages

**Role(s):** engineering, hardware, software, purchasing

## Goal

Find affordable servo drives for the linear stages, and a motion controller that runs our own
control laws. Each stage uses a MAXWELL MK21 iron core linear motor and a 1 Vpp linear
incremental encoder (an encoder that gives analog sine and cosine signals of 1 V peak to peak).
Also answer whether LinuxCNC can be the motion controller and the EtherCAT master.

## Work Done

### Short answer

- **48 VDC is too low for full force at 10 000 mm/min.** At that speed a 48 V drive gives about
  120 to 170 N, depending on coil temperature. The continuous force is 181 N. Pick a drive
  that accepts 80 to 95 VDC. The peak force of 512 N needs a mains voltage drive.
- **No affordable drive meets every requirement.** The Elmo Gold line comes closest. The ACS
  UDMnt meets more of the list, but it only works with an ACS controller.
- **Two requirements cannot be met by any low voltage drive we found.** No drive sends data over
  EtherCAT faster than its own position loop runs. And no drive lets you load any transfer
  function into its loop. Both are met by closing the loop in the PC, as described below.
- **LinuxCNC can be the EtherCAT master.** People run it at 1 to 4 kHz. 8 kHz is not proven.
  For the fast loop, a small real-time program on the same PC is safer.

### What the MK21 needs from a drive

All motor values come from the MAXWELL data sheet in the parts library
([`maxwell-mk2-iron-core-linear-motor.pdf`](../../modules/stoq/modules/maxwell/docs/datasheets/maxwell-mk2-iron-core-linear-motor.pdf)).

| MK21 value | Data sheet |
| --- | ---: |
| Continuous force, current | 181 N, 2.0 Arms |
| Peak force, current (1 s) | 512 N, 5.9 Arms |
| Force constant | 92.5 N/Arms |
| Back EMF constant, line to line | 53.4 V per m/s |
| Resistance, line to line, 25 °C / 120 °C | 13.8 Ω / 19.0 Ω |
| Inductance, line to line | 64.0 mH |
| Highest allowed bus voltage | 600 VDC |

At 10 000 mm/min (0.167 m/s) the back EMF is small, about 9 Vrms line to line. The coil
resistance sets the voltage. The bus voltage needed for a given force is:

| Force at 10 000 mm/min | Coil at 25 °C | Coil at 120 °C |
| --- | ---: | ---: |
| 181 N, continuous | 51 V | 65 V |
| 512 N, peak | 119 V | 158 V |

The other way round, this is the force a given bus voltage allows:

| Bus voltage | Standing still, 25 °C / 120 °C | At 10 000 mm/min, 25 °C / 120 °C |
| ---: | ---: | ---: |
| 48 V | 236 / 172 N | 168 / 122 N |
| 60 V | 296 / 215 N | 227 / 165 N |
| 80 V | 394 / 286 N | 325 / 236 N |

This is a hand calculation, not a measurement. It assumes a sine commutated drive that uses
90 % of the bus voltage, and a magnet period of 30 mm. The drive current must be at least
2 Arms continuous and about 6 Arms peak. Many drives rate current as a peak value: 2 Arms is
2.8 A peak, and 5.9 Arms is 8.3 A peak.

### The drives we checked

| Drive | Bus voltage | 1 Vpp input | Position loop | Shortest EtherCAT cycle | Bode and tuning tool | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Elmo Gold Solo Whistle 5/100, Gold Twitter | 12 to 95 V | Yes, up to ×8192 | 12.5 kHz | 250 µs in the 2013 guide; newer pages say 100 µs | Yes, with plant identification | **Best fit** |
| ACS UDMnt, sin/cos option | 12 to 80 V | Yes, up to ×16 384 | 20 kHz (current loop) | Set by the ACS master | Yes, in the ACS master | Strong, but needs an ACS master |
| Servotronix CDHD2-LV-003 | 20 to 90 V | Yes, up to ×16 384 | 4 kHz (velocity 8 kHz) | 250 µs | Not found | Position loop too slow |
| Technosoft iPOS8010 BX-CAT | 12 to 80 V | Yes | 1 kHz by default | 200 µs | Not found | Loop too slow |
| Novanta (Ingenia) Everest, Capitan, Denali | 7 to 80 V | **No** | 25 kHz | 250 µs | Yes | Rejected |
| Synapticon Circulo | 14 to 58 V | **No** | Not checked | 250 µs | Not checked | Rejected |
| Beckhoff ELM7211 | 8 to 48 V | **No**, only Beckhoff motor encoders | 16 kHz (velocity) | Not checked | Not checked | Rejected |
| Beckhoff AX8108 with the 1 Vpp option | 100 to 480 VAC | Yes | Current loop at 62.5 µs | 62.5 µs, with up to 128 samples per cycle | Yes | Meets almost everything, but mains voltage and a high price |
| HIWIN D2T, HIWIN E1 | 200 to 240 VAC | E1 only with an external box | 16 kHz (D2T) | Not checked | Yes | Mains voltage only |

We found no public prices, except for one Beckhoff encoder terminal. Ask for quotes before
you choose. Chinese low voltage EtherCAT drives (Kinco, Leadshine, Inovance, Googol) may
exist with a 1 Vpp input, but we found no data sheet that confirms it.

### Elmo Gold against the requirement list

| Requirement | Elmo Gold |
| --- | --- |
| Voltage and current | Yes. Gold Solo Whistle 5/100: 3.5 Arms continuous, 7 Arms peak, up to 95 V |
| 1 Vpp encoder | Yes. Up to 500 kHz, ×8192, with automatic offset, gain and phase correction |
| Limit switches, digital inputs | 6 programmable digital inputs. The limit switch function was not checked |
| Analog input, reference follows it | Yes. One ±10 V input can be the motion command |
| Position, velocity, current control | Yes |
| Bode tuning software | Yes. The EASII software identifies the plant and shows Bode plots |
| EtherCAT | Yes |
| Data faster than the loop rate | **No.** The EtherCAT cycle is slower than the 12.5 kHz loop |
| Loop rate of at least 8 kHz | Yes. Current 25 kHz, velocity and position 12.5 kHz |
| Homing | Yes, the CiA 402 methods. The method list was not checked |
| Feedforward | Not stated clearly in the data sheet. Ask Elmo |
| Low-pass and notch filters | Yes. Also general second order filters and gain scheduling |
| Any transfer function in the drive | **No.** Only the built-in filters, and user programs at a slower rate |
| Identification and loop shaping | Yes, in EASII |
| Position error table | Only in the Elmo master controller, not in the drive |

### Why "faster than the loop rate" does not work

EtherCAT sends one frame per cycle. The low voltage drives accept cycles of 100 to 250 µs, so
4 to 10 kHz. Their own loops run faster than that. You cannot read every loop sample over
EtherCAT. Two ways exist to see the fast data:

- Record inside the drive. Elmo, Novanta and ACS drives have a recorder for this.
- Oversampling, which means several samples packed into one frame. Of the drives we checked,
  only the Beckhoff AX8000 does this, with up to 128 samples per cycle.

### Our own control laws: close the loop in the PC

To run any transfer function, put the drive in torque mode (cyclic synchronous torque, CiA 402).
The drive then only controls the current. The PC reads the position, runs our controller, and
sends the force command every cycle. Two limits come with this:

- **The loop rate is the EtherCAT cycle.** With these drives that is 4 to 10 kHz, not more.
- **There is a delay of about two cycles** from the moment the drive samples the position to
  the moment the new force is applied. At 125 µs that is about 250 µs. This delay limits the
  control bandwidth, so include it in every controller design.

A mixed setup also works. The drive runs its own fast position loop with feedforward and
filters. The PC sends the position command and adds its own correction, for example from a
position error table. Most of the "desired" list is covered this way, even without a drive
table.

### Can LinuxCNC be the motion controller?

Yes. The LinuxCNC EtherCAT driver
([linuxcnc-ethercat](https://github.com/linuxcnc-ethercat/linuxcnc-ethercat)) uses the open
source IgH EtherLab master. It installs from a package source on Debian 11, 12 and 13. It
drives CiA 402 servo drives in position, velocity and torque mode, and supports distributed
clocks (the timing method that keeps all drives in step). Its own documents say the CiA 402
support is "still very young".

What people achieve:

- 1 kHz with the generic network driver.
- 2 to 4 kHz on a PC with a native network card driver (Intel igb, igc or e1000e, or Realtek
  r8169) and a real-time Linux kernel (PREEMPT_RT).
- One video claims 8 kHz. We could not check it.

Custom control code goes in a small C component (a HAL component, built with `halcompile`).
LinuxCNC already has a PID block with four feedforward terms, a second order filter block
(low-pass, notch or free coefficients) and a first order low-pass. You can run the EtherCAT
exchange and your controller in a fast thread, and the path planner in a slower thread. Users
do this, but the LinuxCNC documents do not describe it for EtherCAT.

Other masters for the fast loop:

| Master | Fastest cycle | Cost | How you write the controller |
| --- | --- | --- | --- |
| IgH EtherLab, with its Simulink target | Limited by the PC and network card | Free (GPL), plus MATLAB if you use Simulink | C, or a Simulink model |
| SOEM on real-time Linux | Limited by the PC and network card | Free (GPLv3) or commercial | C |
| EtherCrab (Rust) | Not published | Free (MIT or Apache) | Rust |
| Beckhoff TwinCAT 3 with the Simulink target | 50 µs | Paid licences, no public price | Simulink, C++ or PLC code on Windows |
| Speedgoat with Simulink Real-Time | Below 1 ms, no firm number | Paid, no public price | Simulink |

## Decisions Made

No purchase decision yet. The survey points to this setup:

1. A drive that accepts 80 to 95 VDC, with an 80 V supply. The first choice is the Elmo Gold
   Solo Whistle 5/100 or a Gold Twitter of the same rating.
2. A PC with an Intel network card and a real-time Linux kernel, as the EtherCAT master.
3. LinuxCNC for the machine functions and the path, and a fast real-time thread or a separate
   program for our own control laws.

## Open Questions

- Is 181 N at 10 000 mm/min enough, or is the peak force of 512 N needed at that speed? The
  peak force needs a mains voltage drive such as the Beckhoff AX8000.
- Does current Elmo Gold firmware accept a 100 µs or 125 µs EtherCAT cycle? The 2013 guide
  says 250 µs.
- Does the Elmo drive have current feedforward and dedicated limit switch inputs?
- What do an Elmo Gold drive, an ACS UDMnt with its master, and a Servotronix CDHD2-LV cost?
- Magnet period: the data sheet gives 2τ = 30 mm. The
  [encoder stray field study](2026-09-23_encoder-stray-field-shield.md) assumes that the
  magnets alternate every 30 mm, which is a 60 mm period. One of the two must be checked on a
  real magnet track. It hardly changes the voltage result above.

## Next Steps

1. Decide which force is needed at 10 000 mm/min.
2. Ask Elmo, ACS and Servotronix for quotes, the shortest EtherCAT cycle, and the open
   questions above.
3. Test LinuxCNC with the EtherCAT driver on the target PC. Measure the timing jitter at 4 and
   8 kHz before any drive is bought.

<details>
<summary>Calculation and sources</summary>

Voltage model, per phase in star: R = R_ll / 2, L = L_ll / 2, E = 53.4 × v / √3,
f = v / 0.030 m = 5.6 Hz, V_ph = √((E + I·R)² + (I·ωL)²), bus ≥ √6 · V_ph / 0.9. The current is
assumed in phase with the back EMF. The back EMF constant is taken as Vrms.

Drive sources:

- Elmo Gold Solo Whistle installation guide, MAN-G-SOLWHIIG-EC 1.403 (2013):
  <https://www.heason.com/contentfiles/product-datasheets/Heason_Elmo_C12_Gold-Solo-Whistle-Installation-Guide.pdf>
- Elmo Gold Twitter: <https://www.elmomc.com/product/gold-twitter/>
- Elmo plant identification: <https://www.elmomc.com/capabilities/servo-technology/servo-tools/plant-identification-methods/>
- Elmo error correction in the master: <https://www.elmomc.com/capabilities/motion-control/multi-axis-motion/2d-and-3d-error-correction-support/>
- ACS UDMnt installation guide 2.25: <https://api.p1.mks.com/medias/sys_master/images/images/hc1/h24/8797295149086/UDMnt-Installation-Guide.pdf>
- ACS FRF Analyzer: <https://acsmotioncontrol.com/posts/unlocking-precision-how-the-frf-analyzer-maximizes-motion-control-performance/>
- Servotronix CDHD2 user manual, firmware 2.38: <https://stxim.com/wp-content/uploads/2024/01/CDHD2_User_Manual_fw2.38.x_Rev_2.6-i.pdf>
- Technosoft iPOS80x0 BX: <https://technosoftmotion.com/wp-content/uploads/P091.029.iPOS80x0.BX_.UM_.0520.pdf>
- Technosoft slow loop period: <https://technosoftmotion.com/en/knowledge-base/the-relationship-between-the-speed-resolution-and-the-slow-loop-sampling-period-ii/>
- Novanta Everest XCR: <https://drives.novantamotion.com/eve-xcr/product-description>, feedback list <https://drives.novantamotion.com/summit/feedbacks>
- Synapticon Circulo: <https://doc.synapticon.com/circulo/technical_specs/tech_specs_circulo.html>
- Beckhoff ELM7211: <https://www.beckhoff.com/en-us/products/i-o/ethercat-terminals/el-elm7xxx-compact-drive-technology/elm7211-0010.html>
- Beckhoff AX8108 with 1 Vpp option: <https://www.beckhoff.com/en-us/products/motion/servo-drives/ax8000-multi-axis-servo-system/ax8108-0220-0000.html>
- Beckhoff AX8000 oversampling: <https://www.beckhoff.com/en-us/company/press/the-high-performance-ethercat-servo-drives-now-boast-multiple-samples-per-communication-cycle-on-top-of-rapid-control-cycles-2020-09.html>
- HIWIN D2 manual: <https://www.hiwin.it/images/download/documenti/azionamenti-serie-D2-manuale-assemblaggio.pdf>
- HIWIN E1 brochure: <https://www.hiwin.com/wp-content/uploads/E1-Servo-Drive_brochureEN1.pdf>

Master sources:

- linuxcnc-ethercat CiA 402 notes: <https://linuxcnc-ethercat.github.io/linuxcnc-ethercat/cia402.html>
- Distributed clocks: <https://raw.githubusercontent.com/linuxcnc-ethercat/linuxcnc-ethercat/master/documentation/distributed-clocks.md>
- Servo thread at 2 to 4 kHz: <https://forum.linuxcnc.org/ethercat/45749-ethercat-servo-period>
- Generic driver limit: <https://forum.linuxcnc.org/ethercat/51672-raspberry-pi-5-ethercat-master-servo-thread-period>
- IgH native drivers per kernel: <https://docs.etherlab.org/ethercat/1.6/doxygen/devicedrivers.html>
- LinuxCNC pid and biquad: <https://linuxcnc.org/docs/stable/html/man/man9/pid.9.html>, <https://linuxcnc.org/docs/stable/html/man/man9/biquad.9.html>
- TwinCAT cycle times: <https://infosys.beckhoff.com/content/1033/ethercatsystem/2469087755.html>
- Elmo EtherCAT cycle guidance: <https://www.elmomc.com/elmo_academy/ethercat-cycle-time-optimization/>

</details>
