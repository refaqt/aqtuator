# 2026-09-29 — Drives below 800 euro per axis, from maker forums and open source

**Role(s):** engineering, hardware, purchasing

## Goal

The drives in [Drives from non-Israeli suppliers with an open control loop](2026-09-29_non-israeli-drives-with-open-control-loops.md)
cost 800 to 1,400 euro per axis. That is too much. Find what makers use on a budget: look in
maker forums, at open source drives, and at cheap Chinese and used drives. The requirements stay
the same: 230 VAC (a DC bus of at least about 170 V), 2.0 Arms continuous and 5.9 Arms peak, a
1 Vpp encoder, a position loop of at least 8 kHz, an open control loop with free filters, and no
Israeli suppliers.

## Work Done

### Short answer

- **No ready-made drive below 800 euro meets every requirement on paper.** The cheap drives that
  read a 1 Vpp encoder do not publish their position loop rate, or they run it at 2.5 to 5 kHz.
- **LinuxCNC on a PC cannot run the position loop at 8 kHz reliably.** The engineer of Mesa (the
  maker of the LinuxCNC interface cards) writes that 4 to 6 kHz is the usual limit. Forum users
  report 4 to 6.7 kHz with Mesa cards. One user ran 8 kHz over EtherCAT on a fast desktop PC. So
  the fast loop must run in the drive, or in a small extra board next to the drive.
- **Two cheap routes give an open control loop:**
  1. **The STMBL drive, about 250 euro per axis.** This is an open source servo drive made for
     LinuxCNC. It reads a 1 Vpp encoder directly and runs from 230 VAC rectified. All the code is
     open, so we can add any filter. Its position loop runs at 5 kHz today. Raising it to 8 kHz
     is a code change that nobody has documented.
  2. **A used drive in current mode, plus our own position loop on a small board: about 400 to
     500 euro per axis.** The drive only controls the motor current. A microcontroller board
     (about 20 to 70 euro) reads the encoder and runs our position loop and filters at 10 to
     20 kHz. A used Copley Xenus XSL-230-18 costs about USD 305 to 405.
- **Two cheap commercial drives need an answer from the maker:** the HIWIN E2 "Advanced" and the
  Delta ASDA-A3 with its 1 Vpp converter box. Both read 1 Vpp and run from 230 VAC. Neither
  publishes its position loop rate or the price of the missing part.

### Route 1: the STMBL open source drive

| Item | STMBL v4.3 |
| --- | --- |
| Bus voltage | 30 to 350 VDC typical, 380 V maximum. 230 VAC rectified gives about 325 V |
| Current | 17 A continuous, 25 A peak. Much more than the MK21 needs |
| 1 Vpp input | Yes, read directly. The processor counts whole periods and its analog input finds the position inside each period |
| Loop rates | Current loop 20 kHz. Position and velocity loop 5 kHz (a setting in the code, `RT_FREQ 5000`) |
| Openness | Open source (GPLv3). The loops are small blocks of C code, so we can add a biquad filter block |
| Link to LinuxCNC | Mesa smart serial, step and direction, or analog |
| Protection | Overcurrent, over and under voltage, temperature, position error. Power and logic are isolated (2.5 kV). No safe torque off (STO) found |
| Price | 250 euro assembled and tested (brdmaker.com, four in stock on 29 September 2026) |

The risks:

- **Nobody has run it at 8 kHz.** The processor may have spare time. The drive reports its own
  loop timing, so we can measure this on one unit.
- **The project is quiet.** The last change to the main code was in March 2022. The power module
  (IRAM256) is no longer made. A newer version 5, with a different power module, is a prototype.
  Its maintainer says the parts cost less than USD 200.
- **Current resolution.** The drive is sized for 25 A. At 2 A the current measurement may be
  noisy. This is our own concern, not a forum report. Test it before buying more.
- **Safety.** There is no safe torque off. A contactor in the motor or supply line must stop the
  motor.

### Route 2: a drive in current mode and our own fast position loop

The drive runs only the current loop. We close the position loop ourselves on a small real-time
board. LinuxCNC sends the planned path to that board at 1 to 4 kHz. The board smooths the path
and runs the position loop at 10 to 20 kHz. We write every gain and filter ourselves, so we know
exactly how the loop works. The project already did something similar with the ODrive in torque
mode.

| Part | Option | Price found |
| --- | --- | --- |
| Current-mode drive | Copley Xenus XSL-230-18, used: 100 to 240 VAC, 4.2 Arms continuous, 12.7 Arms peak, current loop 15 kHz, reads sin/cos for commutation, ±10 V current command (12 bit) | USD 305 to 405 used, about USD 1,150 new (eBay, 29 September 2026) |
| Real-time board | NUCLEO-G474RE (STM32, fast analog inputs) | USD 20 |
| Real-time board | TI LaunchPad F28P55X or F28379D (C2000). TI has a library that reads 1 Vpp encoders on these chips | USD 36 to 66 |
| 1 Vpp to digital converter, if needed | Used Heidenhain IBV 610 or EXE boxes | USD 60 to 200 on eBay |

Things to solve:

- **Both the drive and our board need the encoder signal.** A 1 Vpp signal cannot simply be
  wired to two inputs. We need a small buffer board, or a converter that gives a digital signal
  to both.
- **The analog command has 12 bit resolution.** If we scale the ±10 V range to ±6 A, one step
  is about 3 mA. That is fine for the force, but check the noise.
- **No safe torque off** on the Copley XSL. Add a contactor.
- **Used parts come without support.** Buy one spare.

A Mesa 8I20 drive (USD 239) does not fit. It has no 1 Vpp input, it is out of stock, and the
PC cannot update it faster than 5 kHz.

### Route 3: build our own drive

A motor control evaluation board with a 400 V power stage and a processor, for example the
TI TIEVM-MTR-HVINV (USD 186, 3 Arms, 165 to 265 VAC), can become a fully open drive. The parts
cost about 250 to 350 euro per axis. But this is months of work. These boards have no
isolation between the processor and the 325 V bus, and no safe torque off. We do not recommend
it for a small team.

### Cheap commercial drives: what is known

| Drive | 1 Vpp | Position loop | Filters | Price found |
| --- | --- | --- | --- | --- |
| HIWIN E2 Advanced ED2F-E0-003-1-C-00 | Built in, ×4 to ×4096 | Not published. Speed bandwidth 3.2 kHz. Shortest EtherCAT cycle 250 µs | 5 notches with free frequency, Q and depth. Frequency analyser | Not found. Ask HIWIN |
| Delta ASD-A3-0421-E + ASD-IF-EN0A20 box | Through the box, ×4 to ×2048 | Not published. Speed bandwidth 3.1 kHz | 5 notches, Bode tool | Drive about USD 210 used. Box: price not found |
| Yaskawa SGD7S-2R8AA0A + JZDP-H003 | Through the converter | Not published | 5 notches, frequency analysis | Drive USD 378 used, converter 548 euro new. About 875 euro in total, over budget |
| Kollmorgen AKD, first generation, used | Built in | 4 kHz. Fails | Biquads | USD 250 to 400 used |
| Kollmorgen AKD2G, F3 option | Option F3 | 4 kHz (250 µs) in the installation manual. An earlier entry said 8 kHz, which was wrong | 4 free biquads | CHF 1,050 new, single axis. Over budget |

Left out:

- **No 1 Vpp input:** Estun ED3L, Dynamikwell DKHDE.
- **No document found with a 1 Vpp input for a linear motor:** Inovance SV680LN and HCFA Y7S.
  Leadshine, Kinco and Hans Motor are in the same group. This means "not found", not "no".
- **Israeli link:** the Dynamikwell manual is a word for word copy of the Servotronix CDHD
  manual, so it is very likely a Servotronix product.
- **Voltage too low for full force:** Granite Devices IONI, ODrive and moteus. Granite Devices
  Argon also drops out: it is no longer made.

### What the forums say

- No forum user reports a cheap drive that meets all our requirements at once.
- One forum user ran a first generation Kollmorgen AKD with a Renishaw 1 Vpp encoder and a
  linear motor on LinuxCNC over EtherCAT (2021).
- Several users close the position loop in LinuxCNC with the drive in torque mode, and use the
  LinuxCNC `biquad` block for notch filters. They reach 4 to 6.7 kHz.
- Users report sync errors between the Kollmorgen AKD2G and LinuxCNC over EtherCAT (2025).
- Reddit, CNCZone and eBay blocked the search tool, so some used prices come from search
  summaries without a date.

## Decisions Made

No purchase decision. The suggested order:

1. Buy one STMBL v4.3 (250 euro) while stock lasts. Test it on one stage: current noise at 2 A,
   and whether its position loop can run at 8 to 10 kHz.
2. In parallel, plan route 2 as the fallback: a used Copley XSL-230-18 and an STM32 or C2000
   board with our own position loop.
3. Ask HIWIN and Delta for the position loop period and the price of the E2 Advanced and the
   ASD-IF-EN0A20 box.

## Open Questions

- Can the STMBL run its position loop at 8 to 10 kHz on its STM32F4 processor?
- How noisy is the STMBL current measurement at 2 A?
- How do we share one 1 Vpp encoder signal between a drive and our own board without errors?
- What are the position loop period and price of the HIWIN E2 Advanced?
- What does the Delta ASD-IF-EN0A20 converter box cost?

## Next Steps

1. Decide whether to buy one STMBL now. Stock is low.
2. Send the questions to HIWIN and Delta.
3. Sketch route 2 in more detail: the board, the encoder buffer, and the safety stop.

<details>
<summary>Sources and remarks</summary>

Prices were seen on 29 September 2026. eBay prices are asking prices, not sold prices.

STMBL:

- Code and "Getting Started" document: <https://github.com/rene-dev/stmbl> (loop rates in `inc/hw/hw.h`, 1 Vpp reading in `src/comps/enc_fb.c`)
- Drive overview: <https://github.com/rene-dev/stmbl/wiki/servo-drives-overview>
- Assembled board: <https://brdmaker.com/product/stmbl-4-3/>
- Version 5: <https://github.com/freakontrol/stmbl>, <https://forum.linuxcnc.org/27-driver-boards/53752-new-update-on-stmbl>
- Parts shortage: <https://forum.linuxcnc.org/38-general-linuxcnc-questions/48987-trying-to-build-find-a-stmbl>

LinuxCNC loop rate limits:

- <https://forum.linuxcnc.org/27-driver-boards/34704-servo-thread-limit-for-mesa-card>
- <https://www.forum.linuxcnc.org/10-advanced-configuration/42708-what-is-the-fastest-possible-servo-thread-rate-and-how-would-one-achieve-that>
- <https://forum.linuxcnc.org/ethercat/53049-position-vs-velocity-mode?start=30>
- LinuxCNC biquad block: <https://linuxcnc.org/docs/devel/html/man/man9/biquad.9.html>

Current-mode route:

- Copley XSL data sheet: <https://www.artisantg.com/info/Copley_Controls_Corp_XSL_230_40_Datasheet_2017315103716.pdf>
- Copley XSL prices: <https://www.ebay.com/p/1426637040>
- Mesa 8I20 manual: <https://www.mesanet.com/pdf/motion/8i20man.pdf>
- TI 1 Vpp library for C2000: <https://www.ti.com/lit/SPRui54>
- TI TIEVM-MTR-HVINV: <https://www.ti.com/tool/TIEVM-MTR-HVINV>
- Heidenhain IBV prices: <https://www.ebay.com/p/1430702024>
- 1 Vpp converters on the forum: <https://forum.linuxcnc.org/27-driver-boards/34989-analog-linear-encoders>

Commercial drives:

- HIWIN E2 manual V1.6: <https://www.hiwin.com/wp-content/uploads/E2-Series-Servo-Drive-User-Manual-V1.6-EN.pdf>
- Delta A3 used price: <https://www.ebay.com/itm/145926524218>
- Yaskawa drive used price: <https://www.ebay.com/itm/376089319040>
- Yaskawa JZDP-H003 price: <https://www.aurremat.com/producto/jzdp-h003-000/>
- Yaskawa Sigma-7 EtherCAT manual: <https://sigma7.eu/wp-content/uploads/Verst%C3%A4rker/EtherCat/Documentations/Manual%20Sigma%207%20200V%20Single%20Axis%20EtherCat.pdf>
- Kollmorgen AKD loop rates: <https://www.kollmorgen.com/en-us/developer-network/akd-control-circuits>
- Kollmorgen AKD with a 1 Vpp linear encoder on LinuxCNC: <https://forum.linuxcnc.org/ethercat/41292-ethercat-axis-feedback-resolution-configuration-questions>
- AKD2G on LinuxCNC: <https://forum.linuxcnc.org/ethercat/55114-kollmorgen-akd2g-driver>
- Dynamikwell DKHDE manual: <https://www.dynamikwell.com/upload/honorgallery/2021-07/610280a233260.pdf>

The two research notes disagree on the STMBL current rating (17 A continuous in the wiki, 28 A
typical on the Getting Started page). The table uses the wiki.

</details>
