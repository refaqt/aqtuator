# 2026-09-29 — HIWIN, Delta and Kollmorgen follow-up

**Role(s):** engineering, hardware, purchasing

## Goal

We will not build our own drive yet. So the STMBL drive and a position loop on our own STM32 or
TI board are off the table for now. Triamec is left out because it sells into the ultra-precision
market and will be too expensive. This entry answers three questions:

1. Do the HIWIN and Delta catalogs and manuals give the position loop rate, or anything else
   that helps?
2. What does a single axis Kollmorgen AKD2G with a 1 Vpp input cost?
3. Is the AKD2G position loop really 8 kHz?

The earlier searches are in
[Drives from non-Israeli suppliers with an open control loop](2026-09-29_non-israeli-drives-with-open-control-loops.md)
and [Drives below 800 euro per axis](2026-09-29_drives-below-800-euro-per-axis.md).

## Work Done

### Short answer

- **The Kollmorgen AKD2G does not meet the 8 kHz requirement.** Its installation manual (June 2023
  edition) gives a position loop update period of 250 µs, so 4 kHz. The velocity loop runs at
  62.5 µs, so 16 kHz. The earlier entries said 8 kHz. That number came from trade articles, and it
  was wrong.
- **A single axis AKD2G with the 1 Vpp option costs CHF 1,050 excluding VAT** (Oxni, Switzerland).
  The part number is AKD2G-SPE-6V03S-A1F3-0000-A. So it is also above the budget.
- **HIWIN and Delta do not publish their position loop rate.** Not in the catalogs, and not in
  the full user manuals. Both drives use a standard layout: a position loop with one gain, a
  velocity loop with a gain and an integral time, and filters on the torque command. The filters
  are notch filters and low-pass filters. Neither drive offers a general biquad filter.
- **No drive in any of the searches is now confirmed to meet all requirements within the
  budget.** The only way forward without our own hardware is to ask HIWIN and Delta directly.

### HIWIN

The catalog we received is the HIWIN GmbH catalog for the **ED1** drive (edition 2410). It does
not cover the E2 drive from the earlier searches.

| Item | ED1, 400 W, 230 VAC, fieldbus version | Source |
| --- | --- | --- |
| Current | 2.5 Arms continuous, 10 Arms peak | Catalog p. 11 and 13 |
| Supply | 1 phase 200 to 240 VAC (also 100 to 120 VAC) | Catalog p. 13 |
| PWM frequency | 16 kHz | Catalog p. 13 |
| Fieldbus | EtherCAT CoE or PROFINET | Catalog p. 12 |
| Motor types | Rotary, linear and torque motors (motor type code "0") | Catalog p. 12 |
| 1 Vpp input | **Only through the external ESC box** (ESC-SS-S02, item 80050247): sin/cos up to 1 MHz, ×4096 | Catalog p. 10 and 26 |
| Loop rates | Not given. Only "speed response 3.2 kHz" | Catalog p. 9 |
| Filters | Automatic tuning, filter adjustment and vibration suppression. No details | Catalog p. 9 |
| Safety | Safe torque off (STO) built in | Catalog p. 7 |

The E2 user manual (V1.6) shows the same control layout as the ED1. The position loop gain is
Pt102, the velocity loop gain is Pt100, the velocity integral time is Pt101, and the torque
command filter is Pt401. There are five notch filters, each with a free frequency, width and
depth. The manual does not give a loop period anywhere. The E2 "Advanced" has the 1 Vpp input
built in, so it needs no ESC box.

### Delta

The catalog covers the ASDA-A3 drive with Delta's own rotary motors.

- **The catalog does not mention linear motors or the 1 Vpp converter box.** Its connector for a
  linear scale (CN5) takes digital A, B and Z signals only. The user manual has a full chapter on
  linear motors and third-party motors (chapter 11), and describes the ASD-IF-EN0A20 box for
  1 Vpp encoders.
- **Loop rates are not given.** The catalog gives a speed loop bandwidth of 3.1 kHz. The user
  manual (more than 1,000 pages) explains the position loop gain as a bandwidth in Hz, but does
  not give the update period.
- **Filters:** five notch filters up to 5,000 Hz with free width and depth, one low-pass filter
  against resonance, and smoothing filters on the commands. No general biquad.
- **Tools:** Bode plots of the speed loop and of the machine, an FFT, and a scope with up to
  20 kHz sampling on 4 channels.
- **The EtherCAT version ("E")** has full-closed loop control and STO.
- The ASD-A3-0421-E gives 2.65 Arms continuous and 10.61 Arms peak, from 1 or 3 phase 200 to
  230 VAC.

### Kollmorgen AKD2G

The part number for our use is **AKD2G-SPE-6V03S-A1F3-0000-A**:

- SPE: position indexer with EtherCAT.
- 6V: 120 to 240 VAC, 1 or 3 phase.
- 03: 3 A. The 6 A model is 06.
- S: single axis.
- A1: hardware revision A, safe torque off (STO).
- F3: the extra X23 connector, which reads 1 Vpp sin/cos encoders.
- The "-A" at the end means that mating connectors are included.

| Part number | Price, CHF excl. VAT | Source |
| --- | ---: | --- |
| AKD2G-SPE-6V03S-A100-0000-A (no 1 Vpp) | 906.54 | Oxni |
| **AKD2G-SPE-6V03S-A1F3-0000-A** | **1,050.47** | Oxni, product page |
| AKD2G-SPE-6V06S-A1F3-0000-A (6 A) | 1,250.47 | Oxni, product page |
| AKD2G-SPE-6V03D-A1F3-0000-A (two axes) | 1,740.19 | Oxni |

Oxni quotes about four weeks delivery. The F3 option adds CHF 143.93. In the USA, one shop sells
the 3 A model without F3 for USD 2,260 new. We found no used single axis AKD2G with the F3 option.

Loop rates from the installation manual, June 2023 edition, p. 34:

| Loop | Update period | Maximum bandwidth (6V03 model) |
| --- | --- | --- |
| Current | 1.28 µs (the current command is updated every 62.5 µs) | 3,000 Hz |
| Velocity | 62.5 µs (16 kHz) | 750 Hz |
| Position | **250 µs (4 kHz)** | 350 Hz |

The four biquad filters of the AKD2G sit in the velocity loop, which runs at 16 kHz. Kollmorgen
has no cheaper single axis drive with a faster position loop. The first generation AKD also runs
its position loop at 250 µs.

## Decisions Made

No purchase decision. The Kollmorgen AKD2G is out on two counts: its position loop runs at 4 kHz,
and it costs more than the budget.

## Open Questions

- **What does the 8 kHz requirement cover?** In these drives the velocity loop resists the
  cutting force first, and it runs faster than the position loop (16 kHz in the AKD2G). If a fast
  velocity loop is enough, more drives come back into play. This needs a check in the simulation
  before we ask more suppliers.
- What are the position loop period and the price of the HIWIN E2 Advanced, and of the ED1 with
  the ESC box?
- What are the position loop period of the Delta ASDA-A3, and the price of the ASD-IF-EN0A20 box?
- Can Kollmorgen confirm the 250 µs position loop in writing? Trade articles on the two axis
  launch say 125 µs.

## Next Steps

1. Check in the simulation whether a 4 kHz position loop with a 16 kHz velocity loop is enough.
2. Send the questions above to HIWIN (hiwin.de) and to a Delta distributor.

<details>
<summary>Sources and remarks</summary>

- HIWIN ED1 catalog, ED1-03-0-EN-2410-K, supplied by the user. Page numbers as printed.
- Delta ASDA-A3 catalog, supplied by the user (a copy from deltaacdrives.com). Speed loop
  bandwidth p. 20, filters p. 6, Bode and scope p. 10, model table p. 19.
- HIWIN E2 user manual V1.6: <https://www.hiwin.com/wp-content/uploads/E2-Series-Servo-Drive-User-Manual-V1.6-EN.pdf>
- Delta ASDA-A3 user manual: <https://deltaacdrives.com/Delta-ASDA-A3-Servo-Drive-User-Manual.pdf>
- Kollmorgen AKD2G-S installation manual, June 2023, p. 34 (loop rates) and p. 28 (part number):
  <https://www.manualslib.com/manual/3154431/Kollmorgen-Akd-2g-S-Series.html?page=34>
- AKD2G-S installation manual, beta edition 2018, p. 29 and 34, with the same 250 µs:
  <https://servostar.ru/_uploads/offers/2c62531152/_pdf/AKD2G%20Installation%20Manual%20with%20FS1%20EN%20REV%20BETA.pdf>
- Oxni prices, seen on 29 September 2026: <https://shop.oxni.ch/en/store/drives/servo-drives/akd2g/AKD2G-SPE-6V03S-A1F3-0000-A>,
  <https://shop.oxni.ch/en/store/drives/servo-drives/akd2g/AKD2G-SPE-6V06S-A1F3-0000-A>,
  list page <https://shop.oxni.ch/en/store/drives/servo-drives/akd2g>
- USA price without F3: <https://www.nextdayautomation.com/products/new-kollmorgen-akd2g-spe-6v03s-a100-0000-servo-drive-120-240vac-1-3ph-3a-1kw>
- The trade article that gave 125 µs: <https://www.motioncontroltips.com/new-dual-axis-akd2g-servo-drive-from-kollmorgen/>

The user also meant to share the Kollmorgen catalog and installation manual, but those files did
not arrive. The installation manual above was read from a public copy instead.

</details>
