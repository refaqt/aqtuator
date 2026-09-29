# 2026-09-29 — Drives from non-Israeli suppliers with an open control loop

**Role(s):** engineering, hardware, purchasing

## Goal

Search again for affordable servo drives for the MK21 linear stages. The requirements are the
same as in the [drive survey](2026-09-25_linear-stage-drive-and-motion-controller-survey.md),
with one change: the position loop must run at 8 kHz or faster. Leave out Israeli suppliers, so
no Elmo, no Servotronix (STXI) and no ACS.

Two wishes on top of that:

- We want to know how the control loop works: a published block diagram, and what each gain does.
- We want to add filters freely. For example: set the gain, then set a general second order
  filter (a biquad) with any numerator and denominator. Aerotech controllers allow this.

The hard requirements, in short: 230 VAC single phase supply (a DC bus of at least about 170 V),
at least 2.0 Arms continuous and 5.9 Arms peak, a 1 Vpp sine and cosine encoder input, EtherCAT
for the LinuxCNC PC, and a position loop of at least 8 kHz.

## Work Done

### Short answer

- **Three drives meet every hard requirement and let you set filters freely:**
  1. **Triamec TSD350 with the TP350 supply** (Switzerland). This is the best technical fit.
     The position loop runs at 100 kHz. It has five second order filters. In "Advanced" mode you
     set the numerator and denominator frequency and damping freely, as you did with Aerotech.
     You can also run your own C# program inside the drive at 10 kHz. No price was found.
  2. **Kollmorgen AKD2G with the F3 connector option** (USA). The position loop runs at 8 kHz.
     It has four biquad filters with free numerator and denominator frequency and Q. A two axis
     drive of 2 × 3 A costs about CHF 1,600 without the F3 option.
  3. **ADVANCED Motion Controls DPEANIU-015S400** (USA). The position loop runs at 10 kHz. The
     manual documents the loop structure. The price is USD 1,508. The weak point: only one free
     biquad can be active at a time.
- **Aerotech itself also fits, but not with LinuxCNC.** The Automation1 iXC4e runs from 230 VAC,
  has a 1 Vpp option and a 20 kHz servo loop, and has 16 fully free second order filters per
  axis. It is a controller with its own software. Its EtherCAT link only exchanges variables
  every 1 ms, so LinuxCNC cannot drive it as a normal servo axis. No price was found.
- **Omron Delta Tau Power Brick AC is the most open controller.** You can write the whole servo
  loop yourself in C. But the fastest servo rate is not published, the unit has four axes, and
  dealer prices are about USD 8,000 to 8,700 without the 1 Vpp option.
- **Two suppliers have Israeli links and are left out:** Agito Akribis (its research centre is in
  Kfar-Saba, Israel) and the Googol GSHD drives (made by a joint venture with Servotronix).

### What "free filters" means in each drive

| Drive | How you set a filter | Number of filters |
| --- | --- | --- |
| Aerotech Automation1 | Raw coefficients N0, N1, N2, D1, D2. You can calculate them outside the software | 16 per axis |
| Triamec TSD350 | Numerator and denominator frequency and damping, or ready types (low-pass, notch) | 5 in the position loop, 1 after the current loop, plus a feedforward filter |
| Kollmorgen AKD2G | Numerator and denominator frequency and Q. The drive turns them into a digital filter | 4: 2 in the forward path, 2 in the feedback path |
| AMC DigiFlex Performance | One custom biquad, placed at a chosen point in the loop | 1 at a time |
| KEBA ServoOne junior | Raw coefficients of a 4th order filter, or an assistant for notch and low-pass | 1 (4th order) in the velocity loop |
| Power Brick AC | Raw coefficients, up to 7th order, or your own C code | 6 at fixed places |
| HIWIN E2, Delta A3 | Notch filters with frequency, width and depth. No general biquad | 5 notches |
| Beckhoff AX8000 | Ready types only: low-pass, phase correction, notch | Not a free biquad |

### Drives that meet the hard requirements

| Drive | Supply | Current, continuous / peak | 1 Vpp input | Loop rate (position) | Filters and code | Price found |
| --- | --- | --- | --- | --- | --- | --- |
| **Triamec TSD350-10 + TP350** | TP350: 1 phase 44 to 230 VAC, gives 325 VDC | 10 Arms / 20 A for 2 s, two axes | Yes, ×65 536, 500 kHz | 100 kHz. No separate velocity loop | 5 free biquads. C# code at 10 kHz | Not found |
| **Kollmorgen AKD2G, F3 option** | 1 or 3 phase 120 to 240 VAC | 3 A / 9 A for 5 s. A 6 A model exists | Yes, with option F3 | 8 kHz (velocity 16 kHz) | 4 free biquads. No code in the drive found | About CHF 1,600 for 2 × 3 A without F3 |
| **AMC DPEANIU-015S400** | 1 phase 100 to 240 VAC | 7.5 A / 15 A peak of sine (5.3 / 10.6 Arms) | Yes, ×2048, 200 kHz | 10 kHz (current 20 kHz) | 1 free biquad. No code in the drive found | USD 1,508 |
| Rexroth ctrlX DRIVE XCS2-W0010F | 1 or 3 phase 100 to 240 VAC | 2.4 A / 10 A (data sheet still preliminary) | Yes, with the multi-encoder option | 8 kHz | Filter details not found | Not found |
| Parker PSD1-S (PSD1SW1300) | 1 or 3 phase 230 VAC | 5 A / 15 A for 2 s | Yes, feedback code 2, 400 kHz | 8 kHz, only from a search result | "Notch filtering". Details not found | Not found |
| KEBA ServoOne junior SO22.006 | 1 phase 230 VAC | 5.9 / 11.8 A | Yes | 8 kHz | Free 4th order filter. Product may no longer be sold | Not found |

The SO22.003 model of KEBA gives only 6 A peak, just above the 5.9 A we need.

### Controllers with their own software, not driven from LinuxCNC

| Product | Supply | Current | 1 Vpp input | Loop rate | Filters and code | Price found |
| --- | --- | --- | --- | --- | --- | --- |
| **Aerotech Automation1 iXC4e-10** | 1 phase up to 240 VAC | 3.5 / 7.1 Arms | Yes, MX2 or MX3 option, ×65 536 | 20 kHz | 16 free biquads, frequency response tool | Not found |
| Aerotech iXA4, 2 axes | 1 phase up to 240 VAC | 5 A / 10 A peak | Yes, MX1 option | 10 kHz | 16 free biquads | Not found |
| Omron Delta Tau Power Brick AC, 4 axes | 90 to 250 VAC | 5 / 10 Arms per axis | Yes, ×16 384 or ×65 536 | Set by the user. Maximum not published | Own servo code in C | USD 8,000 to 8,700 in dealer search results, without 1 Vpp |
| ETEL AccurET Modular 300 | 1 phase 71 to 240 VAC | 4 A / 7.5 A, two axes | Yes, 500 kHz | 20 kHz | "Advanced second order filters", manuals not public. EtherCAT only in position mode, 500 µs cycle | Only grey market prices |

### Drives that fail, or that we must ask about

- **The position loop is too slow (4 kHz):** Kollmorgen AKD (the first generation), Copley Xenus
  Plus, Rexroth IndraDrive, Kinco FD5P.
- **No usable 1 Vpp input:** LinMot C1450, Inovance SV660N and SV680, Leadshine EL7-EC,
  Panasonic MINAS A6L, Sanyo Denki R 3E, HIWIN D2T, Beckhoff AX1000.
- **Wrong bus or voltage:** B&R ACOPOS P3 (POWERLINK, not EtherCAT), Aerotech XL5e and Power Brick
  LV (low voltage), LinMot C1250 (72 VDC), Kollmorgen AKD-N (needs 400 VAC and a bus above the
  motor limit), Galil DMC-40x0 (needs an extra 230 VAC amplifier and has fixed filters).
- **Loop rate not published, so ask the maker:** HIWIN E2 "Advanced" ED2F-E0-003-1-C-00 (it has a
  built-in 1 Vpp input), Delta ASD-A3-0421-E with the ASD-IF-EN0A20 converter, Yaskawa Sigma-7
  with a JZDP converter, Beckhoff AX8108-0120.
- **MAXWELL does not name a drive** for its motors. It asks customers to let its engineers choose.

### A note on current resolution

The Triamec TSD350-10 is rated 10 Arms, five times the continuous current of the MK21. A large
drive measures a small current with less resolution. Triamec says the TSD350 has improved
current resolution, but we did not check the noise at 2 A. Ask Triamec before buying.

## Decisions Made

No purchase decision. For quotes we will ask, in this order:

1. Triamec, for one TSD350-10 and one TP350.
2. Kollmorgen, for the AKD2G with the F3 option, 3 A or 6 A.
3. ADVANCED Motion Controls, for the DPEANIU-015S400, as the low cost choice.

Aerotech stays an option only if we drop LinuxCNC as the motion controller.

Later the same day these prices proved too high. See
[Drives below 800 euro per axis](2026-09-29_drives-below-800-euro-per-axis.md).

## Open Questions

- What do the Triamec TSD350-10 and TP350 cost? How much current noise is there at 2 A?
- Does the Triamec EtherCAT link at 125 µs work with the IgH master in LinuxCNC? Triamec shows
  a non-Beckhoff master in one application note, but not IgH.
- Does the Kollmorgen AKD2G really close the position loop at 125 µs? The number comes from a
  trade article and a catalogue, because the Kollmorgen web site blocked downloads.
- Can the AKD2G filters be entered as raw coefficients, or only as frequency and Q?
- Can the AMC drive run more than one custom biquad?
- What is the position loop rate of the HIWIN E2 and the Delta A3 with a linear motor?
- Does the Omron Power Brick AC run its servo loop at 8 kHz or faster on the ARM processor?

## Next Steps

1. Send quote requests to Triamec, Kollmorgen and ADVANCED Motion Controls, with the open
   questions above.
2. Send one written question to HIWIN and Delta: "What is the position loop period with EtherCAT
   CSP and a linear motor with 1 Vpp feedback?"
3. Update the [drive survey](2026-09-25_linear-stage-drive-and-motion-controller-survey.md)
   choice when the prices are known.

<details>
<summary>Sources and remarks</summary>

Numbers come from primary data sheets and manuals unless the text says otherwise. Page numbers are
PDF pages.

Triamec:

- TSD350 data sheet, p. 1 to 2: <https://triamec.com/files/medien/documents/datasheets/HWTSD350_0-2_Datasheet_EP005.pdf>
- TP350 data sheet, p. 2: <https://triamec.com/files/medien/documents/datasheets/HWTP50-TP350_E_Datasheet_EP003.pdf>
- TP hardware manual, single phase wiring, p. 8 and 14: <https://triamec.com/files/medien/documents/manuals/HWTP50-TP350_E_HardwareManual_EP012.pdf>
- Servo drive setup guide EP030, controllers and filters p. 57 to 69, frequency response p. 35 to 37: <https://triamec.com/files/medien/documents/manuals/ServoDrive-SetupGuide_EP030.pdf>
- Tama user guide, p. 6: <https://triamec.com/files/medien/documents/manuals/SWTAMA_UserGuide_EP005.pdf>
- EtherCAT guide EP021, 125 µs cycle from firmware 4.28.0, p. 4 and 11 to 14: <https://triamec.com/files/medien/documents/manuals/SWTC_TwinCAT-UserGuideEcat_EP021.pdf>
- Application note AN154, Omron PMAC as EtherCAT master: <https://triamec.com/files/medien/documents/AppNotes/AN154_Omron-PMAC-EtherCAT-Setup-Guide_EP001.pdf>

Kollmorgen (kollmorgen.com blocked downloads, so the loop rates come from secondary copies):

- AKD2G loop rates 62.5 µs and 125 µs: <https://www.motioncontroltips.com/new-dual-axis-akd2g-servo-drive-from-kollmorgen/> and the Kollmorgen catalogue, p. 31: <https://acsotomasyon.com/doc_uploads/Kollmorgen-Katalog.pdf>
- Custom biquad filter: <https://webhelp.kollmorgen.com/AKD2G/English/Content/Tuning/Tuning-Fundamentals/Filter-Types-Custom-Biquad.htm>
- AKD position loop 250 µs: <https://www.kollmorgen.com/en-us/developer-network/position-loop-update-rate/>
- AKD2G price: <https://shop.oxni.ch/en/store/drives/servo-drives/akd2g/AKD2G-SPE-6V03D-A100-0000-A>

ADVANCED Motion Controls:

- DPEANIU-015S400 data sheet, p. 1 and 3: <https://servo.a-m-c.com/hubfs/Datasheets/Servo-Drives/DigiFlex-Performance/AMC_Datasheet_DPEANIU-015S400.pdf>
- DriveWare manual, loop architecture in appendix C: <https://servo.a-m-c.com/hubfs/Software-Files/AMC_SW_Manual_DriveWare.pdf>
- Price: <https://www.electromate.com/dpeaniu-015s400/>

Aerotech:

- iXC4e data sheet, p. 2 to 4: <https://www.aerotech.com/wp-content/uploads/2026/05/Automation1-iXC4e-Data-Sheet-D20251002.pdf>
- iXA4 data sheet: <https://www.aerotech.com/wp-content/uploads/2024/01/Automation1-iXA4-Data-Sheet-D20240112-1.pdf>. The MX1 interpolation is ×4096 in the data sheet and ×16 384 on the web page. Confirm with Aerotech.
- Filters: <https://help.aerotech.com/automation1/Content/Parameters/ServoLoopFilterSetup.htm>, <https://help.aerotech.com/automation1/Content/Parameters/ServoLoopFilter00CoeffN0.htm>
- Servo loop diagram: <https://help.aerotech.com/automation1/Content/Block-Diagram_Servo-Loop_Full.htm>
- EtherCAT slave: <https://help.aerotech.com/automation1/Content/EtherCAT-Overview.htm>

Omron Delta Tau:

- Power Brick AC data sheet: <https://assets.omron.com/m/151c4acbc3cc59b4/original/Power-Brick-AC-Datasheet.pdf>
- Power PMAC user manual, servo diagram p. 322 to 323, user servo in C p. 803 to 805: <https://files.omron.eu/downloads/latest/manual/en/o014_power_pmac_users_manual_en.pdf>
- Prices from dealer search results only: <https://shop.fpeautomation.com/products/PBA4-AA0050-00000010>

Others:

- Rexroth ctrlX DRIVE product information, p. 2: <https://apps.boschrexroth.com/microsites/ctrlx-automation/files/ctrlx/Downloadable%20Assets/Product%20Information/ctrlX%20DRIVE/ctrlX_DRIVE_Product_information_servo_drives_EN_202312.pdf>
- Rexroth ctrlX DRIVE Cs, edition 02, p. 7 to 8 and 88 to 91: <https://ulpr.com/wp-content/uploads/documents/Rexroth/AE/Servo/R912009455_02_ctrlX%20DRIVE%20Cs,%20Drive%20systems%20en_US.pdf>
- Parker PSD1 installation guide, p. 9, 36, 38: <https://click2electro.com/wp-content/uploads/2025/02/Parker-PSD1-Servo-Drive-manual.pdf>
- KEBA ServoOne application manual, filter p. 39: <http://fs.gongkong.com/files/technicalData/200909/2009091609422000006.PDF>
- KEBA ServoOne catalogue 2013, p. 11 to 12: <https://www.mat.transtechnik.fr/LTI_Servo_One/documentation/S-One/SO8_Catalogue_EN.pdf>
- ETEL AccurET Modular 300 EtherCAT: <https://www.etel.ch/wp-content/uploads/2024/03/accuret-modular-300-ethercat-data.pdf>
- Beckhoff AX8000 operating manual: <https://download.beckhoff.com/download/document/motion/ax8000_ba_en.pdf>
- Copley Xenus Plus user guide, loop rates p. 67: <https://www.aoyamasteel.co.jp/wp-content/uploads/2024/11/AmpManual-XEL.pdf>
- HIWIN E2 user manual V1.6, 1 Vpp input p. 85, filters p. 386 to 387: <https://www.hiwin.com/wp-content/uploads/E2-Series-Servo-Drive-User-Manual-V1.6-EN.pdf>
- Delta ASDA-A3 user manual, EN0A20 converter p. 943: <https://deltaacdrives.com/Delta-ASDA-A3-Servo-Drive-User-Manual.pdf>
- Kinco FD5P manual, p. 10 to 11: <https://aiq-robotics.com/wp-content/uploads/2024/01/Kinco-FD5P-series-AC-servo-system-manual-EN-23125.pdf>
- Agito Akribis catalogue, Israeli research centre on the back cover: <https://agito-akribis.com/wp-content/uploads/2026/04/Agito-Motion-Controls-and-DrivesEN-26.5.2-1.pdf>
- Googol and Servotronix joint venture: <http://www.gongkong.com/news/201304/57284.html>
- Googol GSHD manual, EtherCAT model has no analog encoder input, p. 10: <https://www.googoltech.com.cn/Uploads/file/20260814/20260814112508_39012.pdf>

</details>
