# 2026-09-25 — Drives and a motion controller for the MK21 linear stages

**Role(s):** engineering, hardware, software, purchasing

## Goal

Find affordable servo drives for the linear stages, and a motion controller that runs our own
control laws. Each stage uses a MAXWELL MK21 iron core linear motor and a 1 Vpp linear
incremental encoder (an encoder that gives analog sine and cosine signals of 1 V peak to peak).
Also answer whether LinuxCNC can be the motion controller and the EtherCAT master.

## Work Done

### Short answer, after the requirements changed

Later the same day the requirements changed. The peak force of 512 N is needed at
10 000 mm/min, and the drive position loop only needs 4 kHz. The stages use an optical linear
encoder. This changes the answer:

- **A drive fed from 230 VAC is needed.** The peak force at full speed needs about 160 V on the
  drive's internal DC bus. A 230 VAC drive has about 325 V.
- **The best fit is now the Elmo Gold Oboe 6/230.** The Servotronix CDHD2-003 is the second
  choice, and now meets the 4 kHz loop requirement.
- **A small DIN rail PC can run LinuxCNC at 4 kHz,** if it has an Intel network chip and a tuned
  real-time kernel. Measured worst case delays on such PCs are 22 to 70 µs.
- **The user interface can run in a browser on a laptop.** A small server on the LinuxCNC PC
  connects the browser to LinuxCNC.

The sections below the first survey give the details. The first survey is kept as it was.

### First short answer

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

### Update: peak force at full speed needs a 230 VAC drive

**What "mains voltage" means.** The drive plugs into 230 VAC, single phase. Inside, it
rectifies this to a DC bus of about 325 V (230 V × 1.414). The drive then switches that bus
into three phase outputs for the motor coils. The output voltage can go from 0 V up to about the
input voltage, so up to about 220 to 230 Vrms line to line. The output frequency follows the
motor speed. The drive only uses as much voltage as the motor needs.

The MK21 allows up to 600 VDC, so 325 V is safe for the motor. A bus of 170 V or more already
gives the full peak force at 10 000 mm/min, even with a hot coil. At 325 V there is a large
margin.

| Drive | Supply | Current, continuous / peak | 1 Vpp input | Position loop | Result |
| --- | --- | --- | --- | --- | --- |
| Elmo Gold Oboe 6/230 | 1 or 3 phase, 50 to 270 VAC | 4.2 / 8.5 Arms | Yes | 10 kHz | **First choice** |
| Elmo Gold Solo Whistle 6/200, Gold Twitter 6/200 | 12 to 195 VDC | 4.2 / 8.4 Arms | Yes | 10 kHz | Good, but needs a 170 to 195 VDC supply |
| Servotronix CDHD2-003 | 1 phase, 120 to 240 VAC | 3 / 9 Arms for 2 s | Yes, up to ×16 384 | 4 kHz | **Second choice.** Has a 1000 point error table in the drive. Bode tool not confirmed |
| Beckhoff AX8620 supply + AX8108 with the 1 Vpp option | 1 phase 230 VAC gives only 5 to 7 A DC | 8 A / 20 A | Yes | Not checked | Premium choice, with up to 128 samples per EtherCAT cycle |
| ACS UDMpm-005 | 1 phase, 85 to 265 VAC | 3.6 / 7.1 Arms | Yes, up to ×4096 | 20 kHz | Needs an ACS master, so it does not fit with LinuxCNC |
| HIWIN D2T-LM | 1 or 3 phase, 200 to 240 VAC | 2.5 / 7.5 Arms | **No**, only digital A/B signals | 16 kHz | Rejected |

The 3 A models of Elmo and the 1.5 A model of Servotronix have too little peak current.

### Update: can a small DIN rail PC run LinuxCNC with low jitter?

Yes, if it has the right network chip and is tuned. Jitter here means how late the real-time
thread starts in the worst case. Published worst case values on small industrial PCs with a
real-time kernel:

| CPU | Worst case delay | Source |
| --- | ---: | --- |
| Intel Atom x6425RE | 29 to 31 µs | OSADL test farm |
| Intel Atom x6425E | 66 µs | OSADL test farm |
| Intel Core i3-8145UE | 31 µs | OSADL test farm |
| Intel Core i3-12100E | 22 µs | OSADL test farm |
| Intel N100 | 34 µs after BIOS tuning, 43 µs without | LinuxCNC forum |

At 4 kHz the cycle is 250 µs. The EtherCAT drives keep their own clocks in step with each other
to well below 1 µs (distributed clocks). The PC jitter does not reach the motor directly. It only
has to stay small enough that each frame reaches the drives before their next sync moment. A
worst case of 30 µs uses about 12 % of a 250 µs cycle. That should work, but it is our estimate
and must be measured on the chosen PC.

What the PC needs:

- An Intel network chip that the EtherCAT master drives directly: i210 or i211, or i225 or i226.
  Use one port only for EtherCAT, and a second port for the laptop.
- A real-time Linux kernel (PREEMPT_RT). LinuxCNC ships one.
- BIOS settings: turn off sleep states (C-states), turbo, hyperthreading and power saving. On
  newer Intel Atom CPUs, turn on Intel TCC mode.
- Examples with an Intel i210 or i226 port: OnLogic Karbon 410 (Atom x6000, i210) and NEXCOM
  NISE110 (N97, i226). The chip of the NEXCOM was seen only on a shop listing. No prices were
  checked.

### Update: a user interface in a browser on a laptop

Yes, this is possible. LinuxCNC has two Python interfaces: one to send commands and read the
machine state, and one to read and set any signal inside LinuxCNC (HAL pins). Both only work on
the LinuxCNC PC itself. So the setup has two parts:

1. **A small server on the LinuxCNC PC.** It uses the Python interfaces and offers them over the
   network as a web page and a live data stream (WebSocket).
2. **A browser on the laptop.** It connects over a normal Ethernet cable to the PC's second
   network port. Nothing needs to be installed on the laptop.

To watch fast signals, a LinuxCNC block (`sampler`) stores the chosen signals every cycle in a
buffer. The server reads the buffer and sends the samples to the browser in batches. At 4 kHz
this is a small data stream.

Two open source projects already do part of this and could be a starting point:
[linuxcnc-ctrl](https://github.com/b0czek/linuxcnc-ctrl) (web streams of signals and a scope)
and [linuxcnc-grpc](https://github.com/dougcalobrisi/linuxcnc-grpc). Older web interfaces such as
Rockhopper have not been updated since 2018.

The emergency stop must stay a hardware circuit. The browser can show its state, but it must
never be the only way to stop the machine.

## Decisions Made

No purchase decision yet. The survey points to this setup:

1. One Elmo Gold Oboe 6/230 per axis, fed from 230 VAC. The second choice is the Servotronix
   CDHD2-003.
2. A separate DIN rail PC with LinuxCNC, a real-time kernel and an Intel i210 or i226 network
   chip, as the EtherCAT master. The drive position loop needs at least 4 kHz.
3. A web interface: a small server on the LinuxCNC PC, used from a browser on a laptop. This is
   future work.

The stages use an optical linear encoder, so the motor field limit from the
[encoder stray field study](2026-09-23_encoder-stray-field-shield.md) does not apply to them.

## Open Questions

- Does current Elmo Gold firmware accept a 250 µs EtherCAT cycle with LinuxCNC? Newer Elmo
  pages say cycles down to 100 µs.
- Does the Elmo drive have current feedforward and dedicated limit switch inputs?
- Does Servotronix ServoStudio 2 show a closed loop Bode plot?
- What do an Elmo Gold Oboe 6/230 and a Servotronix CDHD2-003 cost?
- Does the DIN rail PC keep the EtherCAT frame on time at 4 kHz? This needs a measurement.

## Next Steps

1. Ask Elmo and Servotronix for quotes and for answers to the open questions.
2. Buy one DIN rail PC. Install LinuxCNC and the EtherCAT driver. Run the latency test and watch
   the EtherCAT timing error at 4 kHz for several hours before any drive is bought.
3. Later: build the web interface, starting from one of the existing open source projects.

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

- Elmo Gold Oboe: <https://www.elmomc.com/product/gold-oboe/>
- Elmo Gold Solo Whistle guide, v1.509: <https://www.imajteknik.com.tr/uploads/man-g-solwhiig-ec.pdf>
- Elmo loop rates: <https://www.elmomc.com/capabilities/servo-technology/servo-tools/111-122-servo-control-topology/>
- Beckhoff AX8620: <https://www.beckhoff.com/en-us/products/motion/servo-drives/ax8000-multi-axis-servo-system/ax8620.html>
- ACS UDMpm: <https://acsmotioncontrol.com/products/udmpm>
- HIWIN LMSSA catalogue, D2T-LM encoder: <https://hiwin.sg/wp-content/uploads/2020/08/LMSSA-Catalogue.pdf>

PC and interface sources:

- OSADL latency plots: <https://www.osadl.org/Latency-plot-of-system-in-rack-e-slot.qa-latencyplot-res3.0.html?latencies=Show&showno=10>
- N100 on the LinuxCNC forum: <https://forum.linuxcnc.org/18-computer/51678-linuxcnc-2-9-2-live-on-the-intel-n100-cpu>
- LinuxCNC latency test and tuning: <https://linuxcnc.org/docs/stable/html/install/latency-test.html>
- Intel TCC mode: <https://ubuntu.com/real-time/docs/en/latest/tutorial/intel-tcc/tcc-mode/>
- OnLogic Karbon 410: <https://static.onlogic.com/resources/spec-sheets/OnLogic-K410-Spec-Sheet-V1.pdf>
- Beckhoff distributed clocks: <https://infosys.beckhoff.com/content/1033/ethercatsystem/2469118347.html>
- LinuxCNC Python interface: <https://linuxcnc.org/docs/stable/html/config/python-interface.html>
- LinuxCNC sampler: <https://linuxcnc.org/docs/stable/html/man/man9/sampler.9.html>

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
