# Servo drive selection

This page shows every servo drive we looked at for the MAXWELL MK21 linear motor stage, next to the
requirements. It is an overview. The research is in the log entries and decision records linked in
each row and in [Sources](#sources). If a number here differs from a log entry, the log entry and the
maker's own manual win. Tell us, and we fix this page.

Last updated: 2026-10-06. Prices were seen on 2026-09-29 and many are asking prices.

## Short answer

- **Chosen drive:** Servotronix **CDHD2S-0032AEC2** (order code of the CDHD2S-003 with EtherCAT). It
  passes every hard requirement on paper. See the
  [decision record](decisions/2026-09-30_try-the-servotronix-polynomial-velocity-controller.md).
- **Fallback drive:** Delta **ASD-A3-0421-E** with the Delta **ASD-IF-EN0A20** converter box. It is
  not confirmed. See the
  [decision record](decisions/2026-09-30_delta-asda-a3-as-fallback-drive.md).
- **New on 2026-10-06: the drive software must show Bode plots (DRV-10).** The chosen CDHD2S does
  not meet this as documented: its software shows a frequency response with gain only, no phase.
  The fallback Delta drive meets it. See [DRV-10 for each drive](#bode-plot-tuning-drv-10).
- **Two drives meet all ten hard requirements in the maker's manuals:** the Kollmorgen **AKD**
  (first generation, AKD-x00306 with EtherCAT) and the Copley **Xenus Plus XEL-230-18**. Both were
  left out earlier only because the loop limit was then 8 kHz. Their prices are not confirmed. See
  the [log entry](log/2026-10-06_drives-checked-for-bode-plot-tuning.md).
- **No other drive passes all hard requirements within the budget.** Most others fail on price,
  supply voltage, the encoder input, or a loop rate we cannot confirm.
- **Nothing is bought yet.** These points must be settled first:
  1. Servotronix must confirm that the CDHD2S has velocity controller mode 3 (our own controller in
     the drive) and give its number format.
  2. The CDHD2S gives a DC bus of about 325 V at 230 VAC. The requirement is at least 320 V. The
     decision record writes 220 VAC, which gives about 311 V. No log entry closes this point. Check
     it on the quote.
  3. Delta must confirm a position loop of 4 kHz or faster, and we must decide whether Delta's own
     converter box is allowed.
  4. MAXWELL must tell us whether the MK21 has Hall sensors and what type its thermal sensor is.
  5. Servotronix must tell us whether ServoStudio 2 can show the phase and a Bode plot (DRV-10).

## What the drive must do

The requirements are in
[`modules/compact-stage/architecture/motor-drive.sysml`](../modules/compact-stage/architecture/motor-drive.sysml).
That file is the source. This table is a copy for reading.

| Short name | Requirement | Kind |
| --- | --- | --- |
| DRV-01 | At least 2.0 A rms continuous | Hard |
| DRV-02 | At least 5.9 A rms for at least 1 s | Hard |
| DRV-03 | A settable peak current limit and a thermal model of the motor | Hard |
| DRV-04 | A DC bus of 320 V to 600 V. A drive on 230 VAC single phase has about 325 V | Hard |
| DRV-05 | Runs a linear synchronous motor with a 30 mm electrical period, and finds the commutation angle without Hall sensors | Hard |
| DRV-06 | Reads the motor thermal sensor (type not known yet), or stops on an input | Hard |
| DRV-07 | EtherCAT with the CiA 402 drive profile (the master is a PC with LinuxCNC) | Hard |
| DRV-08 | Reads the stage encoder directly, with no converter box. Today: 1 Vpp at up to 150 kHz (3 m/s divided by 20 µm) | Hard |
| DRV-09 | Position loop at 4 kHz or faster (250 µs or shorter), read in the maker's manual | Hard |
| DRV-10 | The maker's setup software has a tuning function that measures the axis and shows Bode plots (gain and phase against frequency) of the transfer function | Hard |
| DRV-P1 | Our own filters in the loop, best as a free second order filter (a biquad) | Preferred |
| DRV-P2 | A published block diagram of the control loop | Preferred |
| DRV-P3 | A position loop faster than 4 kHz. 8 kHz or more is clearly better | Preferred |

Buying rules that are not in the SysML file (they change with each search):

- About 500 euro per axis for drive and converter, earlier 800 euro.
- New units only. A used unit is fine only if a seller has a large stock of identical units.
- No drive that we build ourselves.
- Free filters in the loop are wanted. This is the same wish as DRV-P1.
- The searches of 2026-09-29 also left out Israeli suppliers. The chosen Servotronix drive comes from
  STXI Motion, an Israeli company, so the rule was not applied to it. The decision records do not
  say why. Confirm with the team before you rely on this rule.

The motor values behind DRV-01 to DRV-06 come from the MAXWELL data sheet: 181 N at 2.0 A rms
continuous, 512 N at 5.9 A rms for 1 s, 670 N at 9.8 A rms for 0.5 s, 30 mm pole pitch, 600 V
maximum bus.

## How to read the tables

- **Pass**, **Fail**: the maker's own document gives the number, and it meets or misses the
  requirement.
- **NC** (not confirmed): we could not read the deciding number in the maker's own document, or the
  maker does not publish it. By the
  [rule from the loop rate mistake](mistakes/2026-09-29_loop-rate-from-a-trade-article.md), NC is never
  counted as a pass.
- **NP**: the maker does not publish it. **Not in logs**: we did not check it.
- Currents are A rms, continuous / peak.
- The loop column is the **position** loop, not the current loop, the velocity loop or the EtherCAT
  cycle.
- The links in the Datasheet column go to the maker's document, or to a public copy of it when the
  maker's site blocked downloads.

## Chosen drive and fallback

| Brand | Model | Datasheet | Supply and bus (DRV-04) | Current (DRV-01, 02) | Linear motor and commutation (DRV-05) | Motor temperature input (DRV-06) | EtherCAT CiA 402 (DRV-07) | Encoder input (DRV-08) | Position loop (DRV-09, P3) | Filters and diagram (P1, P2) | Price | Status and notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servotronix (STXI Motion) | CDHD2S-003, order code CDHD2S-0032AEC2 | [Flyer](https://stxim.com/wp-content/uploads/2025/07/CDHD2S_EC_241220-EN-1.pdf), [manual v1.12](https://e-motors.tech/wp-content/uploads/2024/07/CDHD2S-Manual-V1.12-20231101-en.pdf) | 1 phase 120 to 240 VAC. About 325 V at 230 VAC. Pass, no margin | 3 / 9 A for 2 s. Pass | Yes. Pitch up to 100 000 mm. Phase Find without Hall sensors. Pass | PTC or NTC input. Pass if MAXWELL confirms the type | Yes (EC model). Pass | 1 Vpp up to 300 kHz, ×16 384. BiSS-C up to 26 bit. Pass | 4 kHz linear loop, 8 kHz HD loop. Pass. P3 only with the closed HD loop | Two free biquads and a free polynomial controller in mode 3: NC for the CDHD2S. Diagram: partly | NP. Error table of 1000 points in the drive | **Chosen** (2026-09-30). Order the EC2 version, never "RO" (rotary only). With our own controller the loop is 4 kHz. Mode 3 and its number format must be confirmed. [Log](log/2026-09-30_cdhd2s-velocity-loop-custom-filter.md) |
| Delta | ASD-A3-0421-E with ASD-IF-EN0A20 box | [Manual](https://deltaacdrives.com/Delta-ASDA-A3-Servo-Drive-User-Manual.pdf), [manual 2025 copy](https://www.damencnc.com/userdata/file/7617-5_Delta_ASDA_A3_Manual_English_2025.pdf) | 1 or 3 phase 200 to 230 VAC. About 300 to 325 V. Pass | 2.6 / 10.61 A. Pass | Yes. Pitch 1 to 500 mm. Finds the pole without Hall sensors. Pass | PTC or NTC. Pass if MAXWELL confirms the type | Yes. Pass | 1 Vpp only through the Delta box (500 kHz). **Fail as written** | NP. NC. (The 125 µs EtherCAT cycle is not the loop rate) | Five notch filters, no biquad. Diagrams published | Drive about USD 210 to 225 used. Box price not found. The simpler B3 model is 416.50 euro for 10 or more | **Fallback** (2026-09-30), not confirmed. BiSS-C may not work on units made from week 23 of 2022. [Log](log/2026-09-30_delta-asda-a3-checked-against-the-requirements.md) |

## Other drives checked against the requirements

These drives came from the searches. None is chosen. The last column says why.

| Brand | Model | Datasheet | Supply and bus (DRV-04) | Current (DRV-01, 02) | Linear motor and commutation (DRV-05) | Motor temperature input (DRV-06) | EtherCAT CiA 402 (DRV-07) | Encoder input (DRV-08) | Position loop (DRV-09, P3) | Filters and diagram (P1, P2) | Price | Status and notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servotronix (STXI Motion) | CDHD2-003 (legacy) | [Manual fw 2.38](https://stxim.com/wp-content/uploads/2024/01/CDHD2_User_Manual_fw2.38.x_Rev_2.6-i.pdf), [VarCom fw 2.15](https://stxim.com/wp-content/uploads/2024/01/CDHD2_DDHD_VarCom_fw2.15.x_Rev.1.3.pdf) | 1 phase 120 to 240 VAC. Pass | 3 / 9 A for 2 s. Pass | Yes | Not in logs | Yes | 1 Vpp, ×16 384. Pass | 4 kHz, HD 8 kHz. Pass | Mode 3 with free polynomials is described in this manual | NP | Legacy. Next to check if the CDHD2S has no mode 3. [Log](log/2026-09-29_servotronix-drives-with-a-faster-loop.md) |
| Elmo | Gold Oboe 6/230 | [Product page](https://www.elmomc.com/product/gold-oboe/) | 1 or 3 phase 50 to 270 VAC. Pass | 4.2 / 8.5 A. Pass | Not in logs | Not in logs | Yes | 1 Vpp. Pass | 10 kHz. Pass | Built-in filters only, no free transfer function. NC | Not found | First choice on 2026-09-25. Dropped on 2026-09-29: Israeli supplier. [Log](log/2026-09-25_linear-stage-drive-and-motion-controller-survey.md) |
| Triamec | TSD350-10 with TP350 supply | [TSD350](https://triamec.com/files/medien/documents/datasheets/HWTSD350_0-2_Datasheet_EP005.pdf), [TP350](https://triamec.com/files/medien/documents/datasheets/HWTP50-TP350_E_Datasheet_EP003.pdf) | TP350: 1 phase 44 to 230 VAC, gives 325 VDC. Pass | 10 / 20 A for 2 s. Pass | Not in logs | Not in logs | Yes. 125 µs cycle from firmware 4.28.0 | 1 Vpp, ×65 536, 500 kHz. Pass | 100 kHz. Pass | Five free biquads. C# code in the drive at 10 kHz. Published | Not found | Best technical fit. Left out: "will be too expensive" (ultra-precision market). Current noise at 2 A not checked. [Log](log/2026-09-29_non-israeli-drives-with-open-control-loops.md) |
| Kollmorgen | AKD2G-SPE-6V03S-A1F3-0000-A | [Installation manual](https://www.manualslib.com/manual/3154431/Kollmorgen-Akd-2g-S-Series.html?page=34) | 1 or 3 phase 120 to 240 VAC. Pass | 3 / 9 A for 5 s. Pass | Not in logs | Not in logs | Yes (SPE) | 1 Vpp with option F3. Pass | 250 µs (4 kHz). Pass for DRV-09, not P3. Velocity loop 16 kHz | Four free biquads | CHF 1,050.47 (Oxni) | Out: over budget. An earlier entry said 8 kHz from a trade article. That was wrong. [Log](log/2026-09-29_hiwin-delta-kollmorgen-follow-up.md) |
| Advanced Motion Controls | DPEANIU-015S400 | [Data sheet](https://servo.a-m-c.com/hubfs/Datasheets/Servo-Drives/DigiFlex-Performance/AMC_Datasheet_DPEANIU-015S400.pdf) | 1 phase 100 to 240 VAC. Pass | 5.3 / 10.6 A. Pass | Not in logs | Not in logs | Yes | 1 Vpp ×2048 up to 200 kHz, and BiSS-C. Pass | 10 kHz. Pass | One free biquad at a time. Loop documented | USD 1,508 | Out: over budget. [Log](log/2026-09-29_non-israeli-drives-with-open-control-loops.md) |
| KEBA (older name LTi) | ServoOne junior SO22.003 / SO22.006, EtherCAT version | [Brochure](https://www.controlinmotion.com/bm~doc/lt_servoone-ds.pdf), [operation manual](https://www.parkem.ch/fileadmin/user_upload/Website/6_Produkte/Servodrives/KEBA%20ServoOne/TEXT&CAD&CERT&MANU/Manual_KEBA_ServoONEjunior_en.pdf) | 1 phase 230 VAC. Pass | SO22.006: 5.9 / 11.8 A. SO22.003: 3 / 6 A for 10 s | Yes. Finds the phase itself | Not in logs | Yes (type code with 3 in the option place) | 1 Vpp direct on X7. KEBA must approve a third-party encoder | 8 kHz (family brochure). NC for the junior | Free 4th order filter | About 180 to 270 euro used. New price not published | No quote yet. First choice if KEBA quotes a good new price. May be end of life. [Log](log/2026-09-29_encoder-converter-and-ssi-biss-drives.md) |
| Metronix | smartServo BL 4104-C | [Product page](https://www.metronix.de/en/products/smartservo-bl-4000-c/smartservo-bl-4104-c), [manual](https://www.metronix.de/metronixweb/fileadmin/user_upload/Dokumente/Downloads/Handbuecher/P-HB_BL_4000-C_1P1_EN.pdf) | 1 phase 230 VAC. Pass | 4 / 12 A. Pass | Not in logs | Not in logs | Not in logs | 1 Vpp direct, and BiSS-C. Pass | About 128 µs (7.8 kHz). Pass for DRV-09 | Four band-stop filters | NP | No quote yet. Strong option. [Log](log/2026-09-29_encoder-converter-and-ssi-biss-drives.md) |
| HIWIN | E2 Advanced ED2F-E0-003-1-C-00 | [User manual V1.6](https://www.hiwin.com/wp-content/uploads/E2-Series-Servo-Drive-User-Manual-V1.6-EN.pdf) | 230 VAC | Not in logs | Not in logs | Not in logs | Yes. Shortest cycle 250 µs | 1 Vpp built in, ×4 to ×4096. BiSS-C and EnDat. Pass | NP. NC | Five notch filters, no biquad | NP | Never rejected, never answered. Question to HIWIN is open. [Log](log/2026-09-29_drives-below-800-euro-per-axis.md) |
| HIWIN | ED1 (400 W) | [Manual](https://www.hiwin.de/medias/sys_master/hiwinDocumentMedia/hiwinDocumentMedia/h60/h54/14712629493790/ED1-01-4-EN-2403-MA.pdf?attachment=true), [brochure](https://www.hiwin.com/wp-content/uploads/E1-Servo-Drive_brochureEN1.pdf) | 1 phase 200 to 240 VAC. Pass | 2.5 / 10 A. Pass | Yes (motor type 0) | Not in logs | Yes | 1 Vpp only with the ESC-SS-S02 box. **Fail as written** | NP. NC | Notch and low-pass. No details | NP | Replaced by the E2 Advanced. STO built in. [Log](log/2026-09-29_hiwin-delta-kollmorgen-follow-up.md) |
| HIWIN | D2T-LM | [LMSSA catalogue](https://hiwin.sg/wp-content/uploads/2020/08/LMSSA-Catalogue.pdf) | 1 or 3 phase 200 to 240 VAC. Pass | 2.5 / 7.5 A. Pass | Not in logs | Not in logs | Not in logs | A/B pulses only. **Fail** | 16 kHz | Not in logs | NP | Rejected: no 1 Vpp. [Log](log/2026-09-25_linear-stage-drive-and-motion-controller-survey.md) |
| Beckhoff | AX8108 with 1 Vpp option and AX8620 supply | [AX8000 manual](https://download.beckhoff.com/download/document/motion/ax8000_ba_en.pdf) | Mains voltage. 1 phase 230 VAC gives only 5 to 7 A DC | 8 / 20 A | Not in logs | Not in logs | EtherCAT. CiA 402 not stated in logs | 1 Vpp (option). Pass | NP (current loop 62.5 µs). NC | Ready filter types, no free biquad | High, not published | Out: price and mains supply. Up to 128 samples per EtherCAT cycle. [Log](log/2026-09-25_linear-stage-drive-and-motion-controller-survey.md) |
| Parker | PSD1-S, BiSS-C code PSD1SW1300B1300000 | [Manual](https://click2electro.com/wp-content/uploads/2025/02/Parker-PSD1-Servo-Drive-manual.pdf), [catalogue](https://dpbrowntech.com/files/Parker/Drives/PSD.pdf) | 1 or 3 phase 230 VAC. Pass | 5 / 15 A for 2 s (larger size). The 2 A model is the one priced | Not in logs | Not in logs | Yes | 1 Vpp (feedback code 2, 400 kHz). BiSS-C version needs a converter | 125 µs (8 kHz), from the catalogue | Notch, anti-resonance | About USD 1,189 (2 A model) | Out: over budget. [Log](log/2026-09-29_encoder-converter-and-ssi-biss-drives.md) |
| Bosch Rexroth | ctrlX DRIVE XCS2-W0010F | [Product information](https://apps.boschrexroth.com/microsites/ctrlx-automation/files/ctrlx/Downloadable%20Assets/Product%20Information/ctrlX%20DRIVE/ctrlX_DRIVE_Product_information_servo_drives_EN_202312.pdf) | 1 or 3 phase 100 to 240 VAC. Pass | 2.4 / 10 A (preliminary data sheet) | Not in logs | Not in logs | Not in logs | 1 Vpp with the multi-encoder option | 8 kHz | Not found | Not found | Not followed up. [Log](log/2026-09-29_non-israeli-drives-with-open-control-loops.md) |
| Yaskawa | Sigma-7 SGD7S-2R8AA0A with JZDP-H003 converter | [EtherCAT manual](https://sigma7.eu/wp-content/uploads/Verst%C3%A4rker/EtherCat/Documentations/Manual%20Sigma%207%20200V%20Single%20Axis%20EtherCat.pdf) | 200 V class | Not in logs | Not in logs | Not in logs | Yes | 1 Vpp only through the converter. **Fail as written** | NP | Five notch filters | About 875 euro in total (USD 378 used, converter 548 euro) | Out: over budget. [Log](log/2026-09-29_drives-below-800-euro-per-axis.md) |
| Inovance | SV680N, SV680LNS2R8I (linear) | [Order codes](https://www.manualslib.com/manual/3670582/Inovance-Sv680n-Series.html?page=14), [SV660N guide](https://www.inovance.eu/fileadmin/downloads/Servo_drives_and_motors/SV660N_Advanced_User_Guide.pdf) | Not in logs | Not in logs | Yes (maker web page) | Not in logs | Not in logs | BiSS-C, SSI, EnDat 2.2 through a converter. **Fail as written** | NP. NC | One biquad in the sister model. NC here | NP | Not followed up. SV660N has no third-party linear mode. [Log](log/2026-09-29_encoder-converter-and-ssi-biss-drives.md) |
| Metronix | ARS 2105, used | [ARS 2100 FS manual](https://www.metronix.de/fileadmin/user_upload/Dokumente/Downloads-EN/Manuals/Servo%20Drive%20ARS%202000%20FS/P-HB_ARS2100_FS_5p0_EN.pdf) | Not in logs | Not in logs | Yes | Not in logs | No built-in EtherCAT | Not in logs | NC (200 µs by default) | Speed filter only | 134.93 euro excl. VAT, used | Out: older model, no EtherCAT, 59 units only. [Log](log/2026-09-29_encoder-converter-and-ssi-biss-drives.md) |
| Tonghang | T6DE / T6E, 220 V | [Product pages](https://www.tonghangedrive.com/servo-driver-series/), [T3D manual (sister drive)](https://www.cncdrive.com/downloads/T3D_servodrive.pdf) | 220 VAC, about 310 V. Pass | Likely enough (not published) | No linear mode found. **Fail** | NC | Yes | No 1 Vpp. **Fail** | NP. NC | First order filter only | Not found | Out: fails three hard requirements. No manuals published. [Log](log/2026-09-30_tonghang-drives-checked-against-the-requirements.md) |
| Servotronix (Gaochuang) | CD3E-003 | [Quick start guide (Chinese)](https://28526507.s21i.faiusr.com/61/1/ABUIABA9GAAgjqvIwgYo-oP2iQY.pdf) | 1 phase 220 VAC. Pass | 3 / 9 A for 2 s | Not in logs | Not in logs | Not in logs | A/B pulses only. **Fail** | 8 kHz | No dual loop, no error table | NP | Out: no 1 Vpp. [Log](log/2026-09-29_servotronix-drives-with-a-faster-loop.md) |
| Servotronix (Gaochuang) | LDHD3-006 | [Flyer](https://www.servotronix.cn/en/download/1136) | 1 phase 200 to 240 VAC. Pass | 6 / 18 A | Not in logs | Not in logs | Not in logs | A/B, BiSS-C, Tamagawa. **Fail** | NP | Not in logs | NP | Out: no 1 Vpp. [Log](log/2026-09-29_servotronix-drives-with-a-faster-loop.md) |
| Kinco | FD5P | [Manual](https://aiq-robotics.com/wp-content/uploads/2024/01/Kinco-FD5P-series-AC-servo-system-manual-EN-23125.pdf) | Not in logs | Not in logs | Not in logs | Not in logs | Not in logs | Not in logs | 4 kHz | Not in logs | NP | Fails DRV-08: serial encoders only. See [the 4 kHz drives](#the-4-khz-drives-checked-again). [Log](log/2026-09-29_non-israeli-drives-with-open-control-loops.md) |

## Low voltage drives, and drives that need their own master

DRV-04 needs a bus of at least 320 V. Most drives below work from a low voltage supply, so they fail.
The two ACS drives are different: they need an ACS master controller. All are listed for completeness.

| Brand | Model | Datasheet | Bus voltage | Notes |
| --- | --- | --- | --- | --- |
| Elmo | Gold Solo Whistle 5/100, Gold Twitter | [Installation guide](https://www.heason.com/contentfiles/product-datasheets/Heason_Elmo_C12_Gold-Solo-Whistle-Installation-Guide.pdf) | 12 to 95 V | 3.5 / 7 A, 1 Vpp, 12.5 kHz. Best fit on 2026-09-25 before the voltage rule changed |
| Elmo | Gold Solo Whistle 6/200, Gold Twitter 6/200 | [Product page](https://www.elmomc.com/product/gold-twitter/) | 12 to 195 V | 4.2 / 8.4 A, 10 kHz. Needs a 170 to 195 VDC supply |
| ACS | UDMnt (sin/cos option) | [Installation guide](https://api.p1.mks.com/medias/sys_master/images/images/hc1/h24/8797295149086/UDMnt-Installation-Guide.pdf) | 12 to 80 V | Needs an ACS master controller, so it does not work with LinuxCNC |
| ACS | UDMpm-005 | [Product page](https://acsmotioncontrol.com/products/udmpm) | 1 phase 85 to 265 VAC | 3.6 / 7.1 A, 20 kHz. Needs an ACS master |
| Servotronix | CDHD2-LV | [Product page](https://stxim.com/product/cdhd2-lv-low-voltage-high-performance-servo-drives/) | 20 to 90 V | Up to 15 A, 1 Vpp. Same loops as the CDHD2 |
| Servotronix | LVD2, ZED 15 to 65, Rayon 70 and 300 | [ZED 65](https://stxim.com/wp-content/uploads/2026/07/Datasheet-ZED-65-Rev.1.15.pdf), [Rayon](https://stxim.com/wp-content/uploads/2024/01/Rayon-Harsh-Environment_Flyer_EN_2021_V1.pdf) | 12 to 60 V | ZED has no 1 Vpp input |
| Technosoft | iPOS8010 BX-CAT | [User manual](https://technosoftmotion.com/wp-content/uploads/P091.029.iPOS80x0.BX_.UM_.0520.pdf) | 12 to 80 V | 1 kHz loop by default |
| Novanta (Ingenia) | Everest, Capitan, Denali | [Everest](https://drives.novantamotion.com/eve-xcr/product-description) | 7 to 80 V | No 1 Vpp input. 25 kHz |
| Synapticon | Circulo | [Specifications](https://doc.synapticon.com/circulo/technical_specs/tech_specs_circulo.html) | 14 to 58 V | No 1 Vpp input |
| Beckhoff | ELM7211 | [Product page](https://www.beckhoff.com/en-us/products/i-o/ethercat-terminals/el-elm7xxx-compact-drive-technology/elm7211-0010.html) | 8 to 48 V | Only Beckhoff motor encoders |
| ODrive, moteus, Granite Devices IONI | | No link in logs | Low voltage | Voltage too low. Granite Argon is no longer made |

## Controllers with their own software, and build-it-yourself routes

These do not fit one of the rules: we use LinuxCNC as the master, and we do not build our own drive.

| Brand | Model | Datasheet | Supply | Current | Loop and filters | Price | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Aerotech | Automation1 iXC4e-10 | [Data sheet](https://www.aerotech.com/wp-content/uploads/2026/05/Automation1-iXC4e-Data-Sheet-D20251002.pdf) | 1 phase up to 240 VAC | 3.5 / 7.1 A | 20 kHz. 16 free biquads | Not found | Own controller software. EtherCAT exchanges variables every 1 ms only, so LinuxCNC cannot drive it as an axis |
| Aerotech | Automation1 iXA4 (2 axes) | [Data sheet](https://www.aerotech.com/wp-content/uploads/2024/01/Automation1-iXA4-Data-Sheet-D20240112-1.pdf) | 1 phase up to 240 VAC | 5 / 10 A peak | 10 kHz. 16 free biquads | Not found | Same as above |
| Omron (Delta Tau) | Power Brick AC (4 axes) | [Data sheet](https://assets.omron.com/m/151c4acbc3cc59b4/original/Power-Brick-AC-Datasheet.pdf) | 90 to 250 VAC | 5 / 10 A per axis | User sets the rate. Own servo code in C | USD 8,000 to 8,700 without 1 Vpp | Most open, but four axes and very expensive |
| ETEL | AccurET Modular 300 | [Data sheet](https://www.etel.ch/wp-content/uploads/2024/03/accuret-modular-300-ethercat-data.pdf) | 1 phase 71 to 240 VAC | 4 / 7.5 A, two axes | 20 kHz | Grey market only | EtherCAT in position mode only, 500 µs cycle |
| Agito Akribis, Googol GSHD | | [Agito catalogue](https://agito-akribis.com/wp-content/uploads/2026/04/Agito-Motion-Controls-and-DrivesEN-26.5.2-1.pdf), [Googol manual](https://www.googoltech.com.cn/Uploads/file/20260814/20260814112508_39012.pdf) | | | | | Left out for the Israeli link. Googol EtherCAT model has no analog encoder input |
| STMBL (open source) | v4.3 | [GitHub](https://github.com/rene-dev/stmbl) | 30 to 350 VDC | 17 A continuous (wiki) | 5 kHz position loop, open code | 250 euro | No EtherCAT (Mesa, step/dir or analog), no STO. Dropped: "we will not build our own drive yet" |
| Copley | Xenus XSL-230-18, used, with our own STM32 or C2000 board | [Data sheet](https://www.artisantg.com/info/Copley_Controls_Corp_XSL_230_40_Datasheet_2017315103716.pdf) | 100 to 240 VAC | 4.2 / 12.7 A | Current mode at 15 kHz. We write the position loop | USD 305 to 405 used | Dropped for the same reason. No STO. Used parts only |
| Texas Instruments | TIEVM-MTR-HVINV | [Tool page](https://www.ti.com/tool/TIEVM-MTR-HVINV) | 165 to 265 VAC | 3 A | Own firmware | USD 186 | Not recommended: months of work, no isolation, no STO |

## Also checked and left out

- **Position loop of 4 kHz, left out under the 8 kHz rule of 2026-09-29:** Kollmorgen AKD (first
  generation, USD 250 to 400 used), Copley Xenus Plus, Bosch Rexroth IndraDrive Cs, Schneider Lexium
  32. They were checked again on 2026-10-06. See [the 4 kHz drives](#the-4-khz-drives-checked-again).
- **No usable 1 Vpp input:** Novanta, LinMot C1450, Inovance SV660N, Leadshine EL7-EC, Panasonic MINAS
  A6, Sanyo Denki R 3E, Beckhoff AX1000, Estun ED3L, Dynamikwell DKHDE.
- **No SSI or BiSS-C input:** Mitsubishi MR-J5.
- **Wrong bus or voltage:** B&R ACOPOS P3 (POWERLINK), LinMot C1250 (72 VDC), Kollmorgen AKD-N (needs
  400 VAC), Galil DMC-40x0 (fixed filters, needs an extra amplifier), Beckhoff AX5000 (SoE, not CiA
  402), Delta ASD-A3-0743-E (400 V class, can exceed 600 V).
- **Too small:** Delta ASD-A3-0221-E fails DRV-01. The ASD-A3-0721-E works but is more than twice the
  MK21 current.
- **Israeli link:** Dynamikwell is a copy of the Servotronix CDHD manual.
- **Encoder converters**, for drives that read SSI or BiSS-C:
  [iC-Haus iC-NQC](https://img.ozdisan.com/ETicaret_Dosya/507359_163230.pdf) (board USD 87),
  [NiLAB NL-NQ6D](https://en.nilab.at/products/nl-nq6d-sin-cos-interpolator/) (price on request),
  [Heidenhain EIB 192](https://www.heidenhain.us/wp-content/uploads/2022/07/PI_EIB192_ID1106705_en.pdf) and
  [EIB 392](https://www.heidenhain.us/wp-content/uploads/2022/07/PI_EIB392_ID545817_en.pdf) (no SSI or BiSS).
  No box turns BiSS-C into SSI. Details in the
  [converter log](log/2026-09-29_encoder-converter-and-ssi-biss-drives.md).

## Bode plot tuning (DRV-10)

Checked on 2026-10-06 in the makers' own documents. Sources and pages are in the
[log entry](log/2026-10-06_drives-checked-for-bode-plot-tuning.md).

| Brand | Model | Software | DRV-10 | What it shows |
| --- | --- | --- | --- | --- |
| Servotronix | CDHD2S, CDHD2 | ServoStudio 2 | NC, leans to Fail | Gain of the current command only, no phase |
| Delta | ASDA-A3 | ASDA-Soft | Pass | Speed open loop Bode plot, and the plant |
| Kollmorgen | AKD (first generation) | WorkBench | Pass | Plant, open loop, closed loop |
| Kollmorgen | AKD2G | WorkBench | Pass (brochure only) | Same tool as the AKD |
| Copley | Xenus Plus XEL | CME | Pass | Sine sweep. Current, velocity and position loops, the plant |
| KEBA | ServoOne junior | DriveManager 5 | Pass | Speed loop and current loop, noise excitation |
| Triamec | TSD350 | TAM System Explorer | Pass | Measured open loop |
| Elmo | Gold Oboe | EASII | Pass (web page only) | Plant, open or closed loop |
| HIWIN | E2 Advanced | Thunder | Pass | Measured plant |
| Bosch Rexroth | ctrlX DRIVE | ctrlX DRIVE Engineering | Pass (application note only) | Plant and closed loops |
| Yaskawa | Sigma-7 | SigmaWin+ | Pass | Plant |
| Beckhoff | AX8000 | TwinCAT 3 Bode Plot (extra licence) | Pass | Open loop, closed loop, plant |
| Inovance | SV680N | InoDriverShop | Pass | Plant, speed open and closed loop |
| Metronix | smartServo BL 4104-C | ServoCommander | Fail | Oscilloscope only |
| Advanced Motion Controls | DPEANIU-015S400 | DriveWare 7 | Fail | Oscilloscope only |
| Parker | PSD1-S | PSD ServoManager | NC | Software help not public |
| Bosch Rexroth | IndraDrive Cs | IndraWorks Ds | NC | Not found |
| Schneider | Lexium 32 | SoMove | NC | Auto-tuning only in the drive manual |
| Kinco | FD5P | Kinco software | NC | Oscilloscope only in the manual |

The KEBA ServoOne Device Help also gives a position controller of 125 µs (8 kHz). This confirms
DRV-09 and DRV-P3 for the ServoOne family.

## The 4 kHz drives, checked again

The first searches asked for a position loop of 8 kHz. On 2026-09-29 the hard limit became 4 kHz
(DRV-09). On 2026-10-06 the five drives with a 4 kHz position loop were checked against DRV-01 to
DRV-10.

| Brand | Model | Result | Notes |
| --- | --- | --- | --- |
| Kollmorgen | AKD-x00306, EtherCAT version | **Passes all ten** | 3 / 9 A for 5 s. About 325 V on 230 VAC. Linear motors, Wake and Shake commutation without Hall sensors. 1 Vpp up to 250 kHz with termination resistors. Position loop 250 µs. Price not confirmed: USD 250 to 400 used, new price not found |
| Copley | Xenus Plus XEL-230-18 | **Passes all ten** | 4.24 / 12.7 A for 1 s. About 325 V on 230 VAC. Phasing without Hall sensors. 1 Vpp up to 230 kHz. Position loop 4 kHz. Price not found |
| Bosch Rexroth | IndraDrive Cs HCS01, 230 V model | NC | 250 µs only in "Advanced" performance, otherwise 500 µs. Peak current time, thermal model, CiA 402 and DRV-10 not confirmed |
| Schneider | Lexium 32M with encoder module | **Fail DRV-08** | 1 Vpp input up to 100 kHz only |
| Kinco | FD5P | **Fail DRV-08** | Serial encoders only, no 1 Vpp |

## Earlier drives, for the ball screw test bench

These were chosen for the Mekanika Pro test machine and the ball screw stage family. They are not
candidates for the MK21 stage.

- **ODrive** with a rotary servo motor, controlled over CAN and an analog torque input. Its limits are in
  [ODrive limitations](log/2026-01-12_odrive-limitations.md).
- **Nanotec C5-E and N5** stepper drives were checked and rejected, because the analog inputs and
  CANopen run at 1 kHz at most. See
  [Nanotec driver evaluation](log/2026-02-05_nanotec-driver-evaluation.md).
- **Stepper drives** and the return to steppers: [Stepper driver survey](log/2026-01-29_stepper-driver-survey.md),
  [Revert to stepper motors](log/2026-04-29_revert-to-stepper-motors.md).

## Sources

<details>
<summary>Log entries and decision records read for this page</summary>

Decision records:

- [Try the Servotronix polynomial velocity controller](decisions/2026-09-30_try-the-servotronix-polynomial-velocity-controller.md)
- [Delta ASDA-A3 is the fallback if the Servotronix drive does not work](decisions/2026-09-30_delta-asda-a3-as-fallback-drive.md)

Log entries, in date order:

- [Drives and a motion controller for the MK21 linear stages](log/2026-09-25_linear-stage-drive-and-motion-controller-survey.md)
- [Servotronix drives with a faster position loop](log/2026-09-29_servotronix-drives-with-a-faster-loop.md)
- [Drives from non-Israeli suppliers with an open control loop](log/2026-09-29_non-israeli-drives-with-open-control-loops.md)
- [Drives below 800 euro per axis](log/2026-09-29_drives-below-800-euro-per-axis.md)
- [HIWIN, Delta and Kollmorgen follow-up](log/2026-09-29_hiwin-delta-kollmorgen-follow-up.md)
- [Encoder converters and drives that read SSI or BiSS-C](log/2026-09-29_encoder-converter-and-ssi-biss-drives.md)
- [The motor drive requirements are now in the SysML model](log/2026-09-29_motor-drive-requirements-in-sysml.md)
- [Can the CDHD2S velocity loop run our own controller?](log/2026-09-30_cdhd2s-velocity-loop-custom-filter.md)
- [Tonghang drives checked against the drive requirements](log/2026-09-30_tonghang-drives-checked-against-the-requirements.md)
- [Delta ASDA-A3 drives checked against the drive requirements](log/2026-09-30_delta-asda-a3-checked-against-the-requirements.md)
- [Servo drives checked for a Bode plot tuning tool](log/2026-10-06_drives-checked-for-bode-plot-tuning.md)
- [Mistake: loop rate taken from a trade article](mistakes/2026-09-29_loop-rate-from-a-trade-article.md)

Every number in the tables was copied from these entries. Up to 2026-10-02 nothing was researched
again for this page. The sections on DRV-10 and on the 4 kHz drives come from the research of
2026-10-06, which opened the makers' documents. The log entries record which pages were read and
which blocked downloads.

</details>
