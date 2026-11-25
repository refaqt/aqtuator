# 2026-11-25 — Kollmorgen manuals read: buy the AKD2G, not the AKD. What to buy with it, and what to still ask

**Role(s):** engineering, purchasing

## Goal

We must choose between Kollmorgen and Copley this week. Read the Kollmorgen AKD and AKD2G
manuals and online help. Compare with what Eltrex told us about the Copley XEC-230-09 (emails of
4 to 23 November and the Notion notes of the call on 23 November). Check the draft email to
DynamicDrives, and list what we still must ask. Also check a new optional requirement: can we set
up the drive with a script from a laptop, over a serial link? Check the filters of the Kollmorgen
control loop, where the drive comes from, and which accessories we need, including a mains
filter and a brake resistor.

## Work Done

### Short answer

- **Choose the AKD2G, not the AKD.** Since 1 October 2026, the Safe Torque Off of the AKD rests on
  a Kollmorgen self-assessment, not on a certificate from a testing body. Our requirement DRV-12
  asks for a certified STO, so the AKD now fails it. The AKD also has no EU Declaration of
  Conformity on the Kollmorgen page (only a UK one), calls its BiSS-C input "Renishaw", has
  one STO channel, and needs an external brake resistor. The AKD2G has a TÜV NORD certificate
  (SIL 2, PL d, valid until 29 January 2030), two STO channels and an EU Declaration.
- **The AKD2G has a brake resistor inside: 15 Ω, 100 W.** The 2021 catalogue said it had none,
  and our log of this morning copied that. The installation manual of March 2024 says every
  AKD2G model has one. For 40 kg at 2 m/s (80 J), about 57 J goes into it. That is fine for one
  hard stop every 0.6 s or more. **An external brake resistor is not needed.**
- **A mains filter is needed** for the AKD2G and for the AKD. Neither has one inside. Kollmorgen
  names the Schaffner FN2090 for single phase. With a shielded motor cable under 10 m, the drive
  then meets EMC category C2.
- **The quote's "-A" leaves out two plugs we need:** the motor plug X1 (AKD2G-CON-X1/X2) and a
  15-pin high-density D-sub plug for the encoder on X23. Without them we cannot connect the motor
  or the encoder.
- **Setup by script (new DRV-P7): both drives can be set up over the EtherCAT cable.** Every
  AKD2G parameter we checked has a CANopen over EtherCAT object (CoE), so the EtherCAT master can
  write it. The AKD2G also has a separate Ethernet service port (text commands on port 23, Modbus
  TCP), which works while EtherCAT runs. The Copley CME software can connect through the EtherCAT
  port, and Copley drives map their parameters to CoE objects. Copley's second route is its
  RS-232 port. One limit for both: an EtherCAT network has one master, so a script on the
  EtherCAT cable runs on the LinuxCNC PC, or on a laptop while LinuxCNC is off.
- **The RSF encoder uses the same BiSS-C frame as the Renishaw RESOLUTE** that Kollmorgen names:
  position bits, an error bit and a warning bit (both active low), and a 6-bit check sum with the
  same polynomial (0x43), sent inverted. Renishaw also sells a 32-bit version. So the AKD2G should
  read the RSF encoder with `FB3.BITS = 32` and a step of 100 nm. We should still ask Kollmorgen to
  confirm it.
- **Filters: Kollmorgen is as good as Copley or better.** Four free biquad filters in the velocity
  loop, an observer, a position command filter, and a cogging compensation table. That table is
  useful for the iron-core MK21.
- **Origin.** The legal manufacturer is Kollmorgen Corporation in Radford, Virginia, USA. The
  manuals also name sites in Brno (Czech Republic), Shanghai and Tianjin. Niels said the origin is
  not important, so we do not ask about it.
- **The draft email to DynamicDrives misses four points:** a confirmation that the AKD2G reads
  our RSF encoder (the draft describes the encoder but asks nothing about it), the motor
  temperature pins with BiSS-C, the two missing plugs, and the internal brake resistor (the draft
  says there is none). The full list is under Open Questions.

### What Eltrex told us about Copley, and what is still open

From the emails (4, 9, 16, 18, 19 and 23 November) and the Notion notes of the calls (16 and
23 November):

| Topic | What we know | Still open |
| --- | --- | --- |
| Drive | XEC-230-09, about € 1,175 for 1 to 2 pieces, from stock in about 5 weeks. Standard lead time 25 to 26 weeks, 20 weeks for 10 to 25 pieces | Lead time for 1 sample. Prices for 10 and 50 pieces |
| Current | Eltrex: 2.12 A rms is enough. Peak for "about 3 seconds" (datasheet: 1 s) | None |
| Encoder | All drives read BiSS-C directly and give 5 V. Han checks the 32-bit position | Full 32 bits, CRC, clock, top speed at 0.1 µm |
| Bode plots | Eltrex said "no Bode plot for the position loop". The CME manual says yes, with firmware 4.92 | Which firmware is on the stock units. The XEC page offers 4.60 |
| Temperature sensor | Eltrex said a separate module is needed. The XEC datasheet shows input IN11 made for our PTC values | None. Told Eltrex on 23 November |
| Brake resistor | Inside: 60 Ω, 20 W, 248 J | None |
| EMC | Eltrex: a filter is usually not needed. EC Declaration: category C3 | A filter is needed for C2 |
| Accessories | Asked on 23 November: connector kit (CK) and serial cable | Price of both |
| Data recording | Han checks if position and torque can be recorded for our own frequency sweep | Answer |
| Linear guide | Asked on 23 November for a drop-in for the HIWIN EGR15 and QEH15 | Answer |

No answer has come in since 23 November.

### The new optional requirement DRV-P7: setup by script

Added to `modules/compact-stage/architecture/motor-drive.sysml` and the
[servo drive selection page](../servo-drive-selection.md). Niels first asked for a serial link.
Because the EtherCAT cable is already there, the requirement now accepts the EtherCAT cable
first, then an Ethernet service port, then a serial port. What counts is that a script can reach
every setup parameter.

| | Copley XEC-230-09 | Kollmorgen AKD2G-SPE-6V03S |
| --- | --- | --- |
| Over the EtherCAT cable, parameters | Copley maps its parameters to CoE objects. The CME guide points to the "Parameter Dictionary" and the "CANopen and EtherCAT Programmer's Manual" for the list. We do not have those two documents: NC | Every command page we checked lists a CoE index, for example `FB3.BITS` 3502h:06, `AXIS1.VL.ARTYPE1` 5011h:0C, `AXIS1.MOTOR.TEMPFAULT` 500Bh:1D, `AXIS1.BODE.INJECTPOINT` 5001h:01. A full check of all parameters: NC |
| Over the EtherCAT cable, setup software | CME connects "over EtherCAT" with a laptop network adapter for that network (CME guide 2.1.6, 3.4.3) | WorkBench connects through Ethernet over EtherCAT (EoE), if the master supports it. Kollmorgen shows it with TwinCAT only |
| Separate Ethernet port | None. A standard Ethernet mode (UDP, TCP/IP, Modbus TCP) exists, but needs other firmware and switches EtherCAT off (CME guide 9.5) | X20, works next to EtherCAT. Telnet on port 23 (the WorkBench terminal commands, such as `AXIS1.VL.KP`), Modbus TCP on port 502 |
| Serial port | RS-232 on J8, 9,600 to 115,200 baud, Copley ASCII commands. Cable SER-CK or SER-USB-RJ11 (USB). Works while EtherCAT runs | None |
| Frequency sweep by script | Not checked | `AXIS#.BODE.*` commands set the excitation (PRB, sine, noise, chirp) |
| DRV-P7 | **Pass, if all parameters are CoE objects** (ask) | **Pass, if all parameters are CoE objects** (ask) |

One limit for both drives: an EtherCAT network has one master. A script that uses the EtherCAT
cable runs on the LinuxCNC PC (for example with the `ethercat` command line tool of the IgH
master), or on a laptop that is the master while LinuxCNC is off. To work from a laptop while
LinuxCNC runs, use the AKD2G service port X20, or the Copley RS-232 port.

### The RSF encoder against the Renishaw BiSS-C frame

Kollmorgen's BiSS-C example is a Renishaw RESOLUTE RA26B (26 bits), and the AKD calls its BiSS-C
type "Renishaw". The AKD2G sets a linear BiSS-C encoder with two values only: `FB#.BITS` (0 to
64 position bits, default 26) and `FB#.LINEPITCH` (the step in nm). There is no setting for the
status bits or the check sum. So the drive expects the Renishaw frame. We compared it with the
RSF frame.

| Part of the frame | Renishaw RESOLUTE (L-9709-9005-05-A) | RSF MC 15 B (doc. 10794027) | Same? |
| --- | --- | --- | --- |
| Mode | BiSS C, unidirectional, RS485 | BiSS C, unidirectional, RS485 | Yes |
| Position | 18, 26, 32 or 36 bits, binary, MSB first | 32 bits, binary | Yes, with `FB3.BITS = 32`. MSB first is not written by RSF |
| Status | Error bit, then warning bit, both active low | 2 bits, "error and warning, active LOW" | Yes |
| Check sum (CRC) | 6 bits, x⁶ + x + 1 (0x43), start value 0, sent inverted | 6 bits, polynomial 0x43, sent inverted | Yes. RSF does not give the start value |
| Clock | 0.25 to 10 MHz | 0.1 to 10 MHz, tested at 1 MHz | Yes. The AKD2G clock is at most 1 MHz |
| Supply | 5 V ±10 % | 3.6 to 14 V | The AKD2G gives 5.1 V: fine |

With a 1 MHz clock, one read of 32 + 10 bits takes about 45 µs plus up to 16 µs of start delay.
That fits inside the 62.5 µs of the velocity loop. The drive is made to read 36-bit Renishaw
encoders too, which take longer. Result: the RSF encoder should work. We ask Kollmorgen only to
confirm it, and RSF to confirm the CRC start value and the bit order.

### Filters in the Kollmorgen control loop

Source: AKD2G online help (Tuning, Anti-Resonance Filters, command reference). The AKD has the
same set (AKD User Guide chapter 14).

| Where | What | Settings |
| --- | --- | --- |
| Velocity loop, forward path | Two biquads, AR1 and AR2 | Each: low-pass, notch or resonator, lead/lag, or a free biquad (zero frequency and Q, pole frequency and Q) |
| Velocity loop, feedback path | Two biquads, AR3 and AR4 | Same types. Meant for sensor noise, without lag in the command |
| Velocity loop | Luenberger observer | Gain and bandwidth. For resonances and quantisation |
| Position command | Moving average filter | 2 kHz down to 1.95 Hz, in steps of 2 |
| Current loop | Gain scheduling against current | 256-point table, filled from the motor saturation data |
| Current loop | Cogging compensation | A table taught by a slow move. Works on position. Also removes repeatable errors of bearings |
| Feedforward | Velocity, acceleration, friction, gravity offset | `VL.KVFF`, `IL.KACCFF`, `IL.KVFF`, `IL.FRICTION`, `IL.OFFSET` |

The frequency response tool in WorkBench measures the plant, the closed loop, the current loop, or
a pair of signals we choose. It samples at up to 8 kHz. It computes the open loop from the
measured plant and the controller, and it exports CSV. It does not list a direct measurement of
the open position loop. This matches the answer of DynamicDrives on 30 October.

Compared with Copley (two velocity loop filters and one current loop filter, all can be free
biquads): Kollmorgen has more filters at the same time, plus an observer and a cogging table.
Copley has gain scheduling on the position loop gains and input shaping. Kollmorgen schedules only
the current loop gain.

### Requirements check after reading the manuals

Only the rows that changed since the comparison of this morning. **NC** means not confirmed.

| Requirement | AKD2G-SPE-6V03S-A1F3-0000-A | AKD-P00306-NDCC-E000 |
| --- | --- | --- |
| DRV-06: reads the 3 PTC sensor | Probably. `MOTOR.RTYPE 0` (single PTC), trip level `MOTOR.TEMPFAULT` in ohm, free to set. The manuals disagree whether pins 8 and 9 of X23 work with BiSS-C: NC | Same. Pins 8 and 9 of X10: NC |
| DRV-08: reads the RSF BiSS-C encoder | Probably pass. BiSS-C on X23, clock up to 1 MHz, 5.1 V up to 350 mA (the RSF needs about 0.2 A). The RSF frame is the same as the Renishaw frame the drive is made for. Third-party encoders "should be tested in advance": confirm | BiSS-C is called "BiSS Mode C Renishaw". 32 bits possible. RSF: NC |
| DRV-11: CE | Pass. EU Declaration, signed in August 2024. C2 with filter and motor cable under 10 m | **Fail for now.** Only a UK declaration on the page |
| DRV-12: certified STO | **Pass.** TÜV NORD SEBS-A.095714/15 V2.0, SIL 2, PL d, two channels | **Fail.** Self-assessed since 1 October 2026, one channel |
| DRV-13: stops on errors and limits | Pass: following error (`PL.ERRFTHRESH`), feedback faults, software limits (`SWLS`) | Pass |
| Motor inductance | 2.4 mH to 240 mH. The MK21 has 64 mH: pass | 2.5 mH to 250 mH: pass |
| P1: free biquads | Pass: four | Pass: four |
| P7: setup by script | Pass if all parameters are CoE objects. Also Telnet and Modbus TCP on X20 | Same, service port X11 |
| Brake resistor | Inside, 15 Ω, 100 W | None. External 33 Ω needed |

### Accessories for the AKD2G

Sources: AKD2G installation manual FS1 Rev G (pages 27, 28, 41, 53, 82, 95), accessories guide
Europe (August 2021, pages 19, 22, 26, 33, 48), online help (Regeneration).

| Item | Kollmorgen part | Needed? | Why |
| --- | --- | --- | --- |
| Drive with plugs | AKD2G-SPE-6V03S-A1F3-0000-A | Yes | "-A" adds the plugs for X3 (mains), X10 (24 V) and X21 (I/O and STO) |
| Motor plug X1 | AKD2G-CON-X1/X2 | **Yes** | Not in "-A". We make our own motor cable |
| Encoder plug X23 | 15-pin high-density D-sub male with housing. No Kollmorgen part number | **Yes** | Not in "-A". Buy from a cable shop, or ask DynamicDrives |
| Mains filter | FN2090-6 (DE-202203) or FN2090-12 (DE-202204) | **Yes** | No filter inside. Needed for industrial use and for C2. Size to confirm. Shielded cable from filter to drive |
| 24 VDC supply | Not sold by Kollmorgen | Yes | PELV, ±10 %, at least 1 A for the drive |
| Ethernet cable for setup | Any Cat 5, or ENCP-xxxx | Yes | Laptop to X20. There is no USB port |
| EtherCAT cable | ENCP-xxxx, or any Cat 5 | Yes | Drive to the LinuxCNC PC |
| Shield clamp | SK14, DE-108248 | Optional | 360° shield contact for the motor cable |
| External brake resistor | BAR(U) 500-15, DE-201439 (15 Ω, 500 W) | **No** | Only for hard stops more often than every 0.6 s. The online help lists 33 Ω resistors for this drive, the manual says 15 Ω: ask |
| Setup software | WorkBench | Free download | Version 2.20 on the product page |

For the AKD (if we would still buy it): AKD-X9+X10-Kit for the encoder plug, a 33 Ω external
resistor (for example BAFP(U) 200-33, DE-201438) with a 10 A fuse, and a 1NF-10 (DE-201565)
mains filter. Motor, mains and 24 V plugs come with the drive.

### Motor and encoder cables for the AKD2G

Source: Kollmorgen 2G Cable Guide (cable part number scheme, page 34), AKD2G manual pages 69
and 76, RSF AK MC 15 mounting instructions section 8.1, Saho Robot MK21 wiring sheet.

- Kollmorgen has no standard AKD2G motor cable with an open end. The motor end is always a
  Kollmorgen motor plug (M23 SpeedTec or M15 ytec). Open ends (flying leads `UF`, blunt cut `UB`)
  are listed only for feedback cables. A motor cable with an open end is a special order.
- Best route: ask Saho Robot for the MK21 with an open cable end. U, V, W and PE go into the X1
  plug (AKD2G-CON-X1/X2, spring clamps). No Kollmorgen motor cable is needed.
- If the stage needs a plug: an M15 ytec receptacle on the MK21, and the Kollmorgen standard cable
  `P1-21-015-C1-00-003000` (AKD2G plug to M15 ytec, 1.5 mm², 3 m).
- The MK21 PTC runs in the motor cable, but the AKD2G reads the PTC on X23 pins 8 and 9, the
  encoder connector. So the PTC pair is soldered into the X23 plug. Whether pins 8 and 9 work
  with BiSS-C is question 3.
- The RSF head ends in a standard 15-pin D-sub (male). X23 is a 15-pin high-density D-sub
  (female). We make a short adapter cable. Kollmorgen sells no cable for a third-party BiSS-C
  encoder. Pin map: MA+ 8→2, MA− 15→3, SLO+ 5→6, SLO− 13→7, UP 4→10, 0 V 2→11, sense UP 12→4,
  sense 0 V 10→5.
- A page with the wiring figures and the shopping list:
  [MK21 to AKD2G Cabling](../akd2g-mk21-cabling.html), also published as a private page on
  claude.ai.

### Brake resistor calculation for the AKD2G

| Value | Number | Source |
| --- | --- | --- |
| Moving energy, 40 kg at 2 m/s | 80 J | Our estimate |
| Energy the bus capacitors take at 240 VAC | 23 J (±20 %) | Manual page 41 |
| Energy into the brake resistor | about 57 J, less with motor losses | 80 − 23 |
| Internal resistor | 15 Ω, 100 W, 9 kW for 0.5 s | Manual page 41 |
| Shortest time between two such stops | about 0.6 s | 57 J ÷ 100 W |
| Same at 3 m/s (180 J) | about 1.6 s | 157 J ÷ 100 W |

Using the internal resistor lowers the rated ambient temperature from 50 °C to 40 °C (manual page
33).

## Decisions Made

- DRV-P7 (setup by script, best over the EtherCAT cable, with every parameter reachable) is a
  new preferred requirement.
- Proposal, not yet decided by Niels: ask DynamicDrives for a quote for the AKD2G only, with the
  accessories above. Drop the AKD because of DRV-11 and DRV-12.

## Open Questions

Questions for DynamicDrives (Kollmorgen). The first four are already in the draft email of today.
The rest are new.

1. (In the draft) New quote for the AKD2G-SPE-6V03S-A1F3-0000-A. Confirm that the 3 A drive is
   large enough for 2.0 A rms continuous and 5.9 A rms for 1 s.
2. (In the draft) Can X23 read three PTC in series (trip between 1,650 Ω and 3,990 Ω), and can we
   set the trip level?
3. (In the draft) Can we set the continuous current, the peak current and the peak time in the
   thermal model?
4. (In the draft, but change it) Mains filter: which FN2090 size for the 6V03S on single phase,
   and does the drive then meet C2? Drop the brake resistor from the list: the AKD2G has one
   inside.
5. **Encoder.** The RSF AK MC 15 B sends the same BiSS-C frame as a Renishaw RESOLUTE with
   32 bits: 32 position bits, error and warning bits (active low), 6-bit CRC with polynomial 0x43,
   sent inverted. Please confirm that X23 reads it with `FB3.BITS = 32` and
   `FB3.LINEPITCH = 100` nm, and checks the CRC. Which clock does the drive use?
6. **Temperature pins with BiSS-C.** The FS1 manual shows pins 8 and 9 of X23 as unused for
   BiSS-C, the FS2 manual shows the thermal input there. Which is right?
7. **Plugs.** The "-A" version leaves out X1 and X23. Please quote AKD2G-CON-X1/X2 and a
   matching plug or a cable with an open end for X23.
8. **Brake resistor.** The manual of 2024 says the 6V03S has a 15 Ω, 100 W resistor inside, the
   catalogue of 2021 says it has none. Please confirm. The online help lists 33 Ω external
   resistors for the 6V03S, the manual says 15 Ω recommended and 10 Ω minimum. Which is right?
9. **Setup by script.** Can every drive parameter be read and written as a CoE object over
   EtherCAT? Is there a list of parameters that are not? Does Ethernet over EtherCAT (EoE) work
   with the IgH EtherCAT master under LinuxCNC, not only with TwinCAT? Is a user script with
   terminal commands on port 23 of X20 supported while EtherCAT runs?
10. **Bode plot of the position loop.** Can WorkBench measure the open loop of the position loop,
    or only compute it from the plant? Is WorkBench free for all functions?
11. **Cogging compensation.** Does the cogging table (`IL.COMPTABLE`) work with a linear motor and
    a linear encoder, over a stroke of about 400 mm?
12. **Lead time and price** for 1, 2 and 10 pieces, with the accessories.
13. **Motor cable with an open end.** Can Kollmorgen supply an AKD2G motor cable with the X1
    plug on one end and flying leads at the motor end (for example `P1-21-015` with a `UF` end,
    3 m)? It is not in the standard list, so it is a special: part number, price, lead time.
14. The AKD: we drop it, because its STO is self-assessed since 1 October 2026 and there is no EU
    Declaration of Conformity on the page. Only if DynamicDrives can show an EU Declaration and a
    third-party STO certificate would we look again.

Questions for Eltrex (Copley), still open from 23 November: firmware on the stock units, BiSS-C
32 bits and clock, data recording for our own sweep, the price of the connector kit and the
serial cable, and the lead time for one sample. New: can every CME parameter be read and written
as a CoE object over EtherCAT, and can you send the Parameter Dictionary and the CANopen and
EtherCAT Programmer's Manual?

Question for RSF: is the CRC start value 0, and are the position bits sent MSB first, as in the
Renishaw frame?

The email to DynamicDrives will have an informal part in Dutch and the technical questions in
English.

## Next Steps

- Write the email to DynamicDrives with questions 4 to 13, and send it. The draft in Gmail is ready (25 November).
- Remind Eltrex of the open Copley questions.
- When both answers are in, choose. On today's documents both the AKD2G and the Copley XEC pass
  all hard requirements that we could check. The AKD2G is about € 45 more per drive (quote of
  30 October, expired), has more current margin, a certified two-channel STO and more filters.
  The Copley XEC has a serial port next to EtherCAT, and stock delivery in about 5 weeks.
- The accessories add cost to both drives. Neither quote holds them yet.

<details>
<summary>Sources</summary>

- Kollmorgen documents, downloaded on 2026-11-25 and added to the parts library `refaqt/stoq`
  under `modules/kollmorgen/`: AKD2G-S Installation Manual FS1 Rev G (March 2024), FS2 Rev G (June
  2026, fetch-only), AKD2G EtherCAT and CANopen manual Rev A, part number scheme, EU Declaration
  of Conformity, TÜV NORD certificate SEBS-A.095714/15 V2.0, AKD Installation Manual Rev AG, AKD
  User Guide Rev N, AKD STO product notice of 2026-10-01, UKCA Declaration, accessories guide
  Europe (August 2021).
- AKD2G online help, read on 2026-11-25: webhelp.kollmorgen.com/AKD2G (Tuning View, Manual
  Tuning, Anti-Resonance Filters, filter types, Luenberger observer, Terminal, Available IP Ports,
  Service Interface X20, Motor Temperature, `AXIS#.MOTOR.RTYPE`, `AXIS#.MOTOR.TEMPFAULT`, X23
  BiSS-C, Regeneration, `AXIS#.BODE.MODE`, `AXIS#.PL.FILTER.FREQ`, Cogging Compensation).
- Copley XEC datasheet 16-01435 Rev 04 (RS-232 J8, ASCII interface, SER-CK) and Xenus Plus
  Compact User Guide 16-01552 Rev 02 (SER-USB-RJ11), in `refaqt/stoq` under `modules/copley/`.
- Eltrex emails of 4 to 23 November 2026, Notion meeting notes "Meeting Eltrex Motion" of 16 and
  23 November 2026.
- Draft email "Re: Offerte 26MW1026 – herziene specificaties en vragen", 25 November 2026.
- MK21 inductance 64 mH: Notion notes of 23 November.
- Renishaw data sheet "BiSS C-mode (unidirectional) for RESOLUTE and FORTiS encoders",
  L-9709-9005-05-A (June 2023), from renishaw.com. RSF "BiSS C-mode (unidirectional) for Absolute
  Linear Encoders MC15B, MCS15B, MCS16B", doc. 10794027, in `refaqt/stoq` under `modules/rsf/`.
- AKD2G online help: `FB#.BITS`, `FB#.LINEPITCH`, Commands Used for Each Feedback Type, Setup
  Ethernet over EtherCAT (EoE). CME User Guide 16-01157 Rev 05, sections 2.1.6, 3.4.3, 9.4 and 9.5.

</details>
