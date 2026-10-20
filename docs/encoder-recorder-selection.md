# Encoder recorder selection

This page lists systems that can read three or more position encoders at the same time and record
each position against time. The encoders send 1 Vpp sine and cosine signals, or an absolute
position over EnDat 2.2 or BiSS-C. The recorded data must be exported to a PC file. The research
is in [the log entry](log/2026-10-20_encoder-recorder-search.md). If a number here differs from
the maker's own data sheet, the data sheet wins. Tell us, and we fix this page.

Last updated: 2026-10-20.

## Short answer

No single box reads all three signal types, records them, and exports a file with no
programming, on numbers we read in a data sheet. Three routes come close. Which one is best
depends on the encoders you use.

1. **Beckhoff EtherCAT terminals on a PC with TwinCAT.** This is the most flexible route. You can
   mix terminals for each signal type in one row: EL5021 for 1 Vpp (one encoder per terminal),
   EL5032 or EL5031-0011 for EnDat 2.2, and EL5042 for BiSS-C (two encoders per terminal). A
   shared clock (EtherCAT distributed clocks) makes all terminals read their encoder at the same
   moment. TwinCAT Scope View records the positions and exports CSV, TDMS or DAT. The rate is
   about 10 kHz: the EL5021 data sheet gives a shortest cycle of 80 µs, the EL5042 100 µs. The
   EL5031-0011 can take up to 50 EnDat readings per cycle, 25 µs apart (40 kHz). The terminals
   cost about 300 to 400 US dollars each at resellers. Beckhoff publishes no list price.
2. **HEIDENHAIN EIB 741 (mains power) or EIB 742 (24 V).** This is a ready box for measurement.
   It reads four encoders, each one 1 Vpp or EnDat 2.1/2.2. One trigger captures all four axes at
   the same moment, up to 50,000 times per second. It connects to the PC over Ethernet. It does
   **not** read BiSS-C. HEIDENHAIN gives drivers for Windows, Linux and LabVIEW, and a sample
   program. A CSV export is not listed, so you need a small program of your own (for example in
   Python or MATLAB) to save the data. Price: ask HEIDENHAIN. We read a 2013 product sheet and the
   user manual. The newer sheet could not be opened, so check the numbers in it before you buy.
3. **A National Instruments CompactRIO with S.E.A. modules.** S.E.A. is a German maker. The
   S.E.A. 9510 reads three EnDat 2.2 encoders, and the S.E.A. 9521 reads three BiSS-C encoders,
   all three at the same time. The rates are 23 kHz (EnDat) and 20 kHz (BiSS-C) per channel,
   higher with newer drivers. List prices are about 1,600 to 1,700 euro per module, plus the
   CompactRIO. You must write the recording program yourself in LabVIEW FPGA.

For **1 Vpp only**, the **imc HRENC-4** module (in imc CRONOSflex, CRONOS-XT or CRONOScompact) is
a ready data logger. It reads four 1 Vpp encoders with interpolation inside the module, samples
all channels at the same moment, and records up to 50 kHz per channel. The export formats and
the price are not published.

Our advice: decide first which encoder signal you will use. If it is 1 Vpp or EnDat, ask for
quotes for the HEIDENHAIN EIB 741 and the Beckhoff set. If BiSS-C is needed, the Beckhoff set is
the simplest route.

## What the system must do

These are the needs from the request. They are not yet requirements in the SysML model.

| Short name | Need |
| --- | --- |
| REC-01 | Reads at least 3 encoders |
| REC-02 | Reads 1 Vpp sine and cosine, or EnDat 2.2, or BiSS-C |
| REC-03 | Reads all encoders at the same moment, or gives each reading a time stamp |
| REC-04 | Records position against time |
| REC-05 | Exports the record to a file on a PC |

The sample rate is not fixed yet. For a 1 Vpp encoder, the signal frequency is the speed divided
by the signal period. A 20 µm period at 100 mm/s gives 5 kHz. The interface must handle that
input frequency. The record rate only needs to be as fast as the motion you want to see.

## How to read the table

- "n/c" means not confirmed. The number is not in the maker's own data sheet, or we could not
  open it.
- "Same moment" means that one clock or one trigger starts the reading of all channels.
- Prices from resellers or shops are marked as such. They are not maker list prices.
- Israeli suppliers are left out (for example ACS Motion Control and Netzer). The ODrive is left
  out too.

## The table

| Maker and product | Kind | Encoders per unit | 1 Vpp | EnDat 2.2 | BiSS-C | Rate | Same moment | Record and export | Price | Data sheet |
|---|---|---|---|---|---|---|---|---|---|---|
| Beckhoff EL5021 | EtherCAT terminal | 1 | yes, up to 13 bit per period, 250 kHz input at 10 bit | no | no | shortest cycle 80 µs (12.5 kHz) | yes, distributed clocks | TwinCAT Scope View: CSV, TDMS, DAT | about 290 to 370 US dollars (resellers) | [PDF](https://download.beckhoff.com/download/document/io/ethercat-terminals/el5021_en.pdf) |
| Beckhoff EL5032 | EtherCAT terminal | 2 | no | yes | no | shortest cycle n/c (default 100 µs) | yes, distributed clocks | as above | about 340 US dollars (reseller) | [PDF](https://download.beckhoff.com/download/document/io/ethercat-terminals/el5032_en.pdf) |
| Beckhoff EL5031-0011 | EtherCAT terminal | 1 | no | yes | no | up to 50 readings per cycle, 25 µs apart (40 kHz) | yes, distributed clocks | as above | n/c | [page](https://www.beckhoff.com/it-it/products/i-o/ethercat-terminals/el-ed5xxx-position-measurement/el5031-0011.html) |
| Beckhoff EL5042 | EtherCAT terminal | 2 | no | no | yes (one-way) | 100 µs cycle with one channel at 10 MHz; with two channels n/c | yes, distributed clocks | as above | about 340 US dollars (used, eBay) | [PDF](https://download.beckhoff.com/download/document/io/ethercat-terminals/el5042_en.pdf) |
| HEIDENHAIN EIB 741 / EIB 742 | measurement box | 4; more boxes on one trigger chain | yes, 4096-fold, 500 kHz input | yes (also 2.1) | no | 50 kHz (recording or streaming) | yes, one trigger for all axes | drivers and sample program; CSV n/c | ask maker | [2013 sheet](https://www.atechauthority.com/storage/img/pdocuments/EIB_741_Brochure_en.pdf), [manual](https://www.manualslib.com/manual/1359446/Heidenhain-Eib-741.html) |
| S.E.A. 9510 in NI CompactRIO | measurement module | 3 | no | yes | no | 23 kHz per channel (201 kHz with newer driver and cRIO-904x/905x) | yes, 3 axes in parallel | own LabVIEW program | from 1,576 euro excl. VAT (shop) | [manual](https://shop.sea-gmbh.com/media/1f/45/6d/1721898645/SEA%209510%20Hardware%20Manual.pdf?ts=1721898645) |
| S.E.A. 9521 in NI CompactRIO | measurement module | 3 | no | no | yes (one-way) | 20 kHz per channel with 3 encoders | yes, 3 ports in parallel | own LabVIEW program | 1,679 euro excl. VAT (shop) | [manual](https://shop.sea-gmbh.com/media/ce/1a/fe/1739962223/SEA%209521%20Hardware%20Manual.pdf?ts=1739962223) |
| imc HRENC-4 (CRONOSflex, CRONOS-XT, CRONOScompact) | data logger | 4; more modules on one bus | yes, analog interpolation | no | no | up to 50 kHz per channel | yes | imc STUDIO, FAMOS; formats n/c | ask maker | [PDF](https://www.imc-tm.com/fileadmin/Public/Downloads/Datasheets/imc_CRONOSflex/TD_CRONOSflex-HRENC-4_eng.pdf) |
| ADDI-DATA APCIe-1711 | PCIe card | up to 8 EnDat, 4 sine/cosine, BiSS on each module | yes, with EM-SINCOS module | yes | yes | n/c | n/c | drivers only | ask maker | [PDF](https://www.addi-data.com/wp-content/uploads/datasheet/english/04_PCI-Express/APCIe-1711-datasheet.pdf) |
| Omron (Delta Tau) CK3M with CK3W-AX2323 | motion controller | 4 | yes, up to 2 MHz | n/c | n/c | servo cycle, n/c | yes, one servo clock | Power PMAC gather to text file (n/c) | ask maker | [PDF](https://assets.omron.com/m/1f0f18821e0338a5/original/CK3W-AX-Datasheet.pdf) |
| Aerotech Automation1 (XC4e, iXC4e, XR3) | motion controller and drives | 1 per axis | option | yes | yes | absolute encoder read at 20 kHz; data collection up to 20 kHz on drives | yes, one controller clock | Automation1 Studio, .dat file, Python API | ask maker | [help](https://help.aerotech.com/automation1/Content/Parameters/PrimaryFeedbackType.htm) |
| B&R ACOPOS P3 with 8EAC0150 | servo drive card | 3 | no | yes | yes | n/c | n/c | Automation Studio trace (n/c) | ask maker | [PDF](https://docs.rs-online.com/e6a0/A700000015082156.pdf) |
| Siemens SINAMICS CU320-2 with SMC20 or SMC40 | drive system | SMC20: 1, SMC40: 2 | SMC20: yes | SMC20: 2.1 only; SMC40: yes | no | n/c | n/c | Startdrive trace (n/c) | ask maker | [SMC40 note](https://cache.industry.siemens.com/dl/files/687/109477687/att_849858/v1/SMC40_Usage_V21.pdf) |
| TI AM243x / AM64x with Motor Control SDK | processor (own board) | 3 per PRU-ICSSG | no | yes, 3 at once | yes, 3 at once | set by own firmware | yes, concurrent mode | own firmware | evaluation board, ask TI | [EnDat guide](https://software-dl.ti.com/processor-industrial-sw/esd/motor_control_sdk/am243x/latest/docs/api_guide_am243x/ENDAT.html) |
| Fast analog inputs (Dewesoft SIRIUS HS, NI 9223, NI 9215, Spectrum M2p.59xx) | analog recorder | 2 channels per encoder | raw signals, position computed in software | no | no | 100 kS/s to 125 MS/s | yes | DewesoftX (MAT, CSV), NI TDMS, Spectrum SBench | NI 9215 from 1,178 US dollars, NI 9223 from 2,033 US dollars (ni.com) | [SIRIUS](https://dewesoft.com/products/sirius/tech-specs) |

## Not suitable

These products came up in the search but fail a need.

- Dewesoft counter inputs, HBK QuantumX MX460B, NI 9411 and NI 9361, Siemens ET 200SP TM
  PosInput: digital pulse or SSI inputs only. No 1 Vpp interpolation, no EnDat, no BiSS-C.
- iC-Haus MB3U, MB5U and MB8U: one BiSS line per adapter. Three encoders on one line need a data
  input on each encoder, which most encoders do not have. Several adapters do not share a clock.
- RLS E201: one BiSS-C encoder, 500 Hz, no shared clock between units.
- HEIDENHAIN PWM 21 with ATS: one encoder, a test tool.
- HEIDENHAIN GAGE-CHEK ND 2108G: a gauge display, not a time recorder.
- HEIDENHAIN EIB 1500 and EIB 2391S: signal converters, they do not record.
- Kollmorgen AKD, Copley Xenus Plus, PI C-891, Galil, Trio: each drive or controller reads one or
  two encoders, and we found no shared clock for three units in a data sheet. One Galil
  controller can read several BiSS encoders, but not 1 Vpp or EnDat.

## Raw 1 Vpp on analog inputs

You can also record the raw sine and cosine signals on fast analog inputs that sample all
channels at the same moment. Then a program computes the position: the angle inside each signal
period (arctan), plus a count of whole periods. Three encoders need six differential channels.

- Take at least 4 samples per signal period, better 10. At 5 kHz signal frequency, that is
  20 to 50 kS/s.
- The data grows fast: 6 channels at 1 MS/s is about 12 MB/s.
- You must write and test the arctan and counting code yourself.
- The NI 9223 and NI 9215 have a ±10 V range only, so a 1 Vpp signal uses only a small part of it.
  The Dewesoft SIRIUS HS has a ±0.5 V range, which fits better.

## Sources

- [Activity log, 2026-10-20](log/2026-10-20_encoder-recorder-search.md)
