# 2026-11-23 — Copley manuals: control loops, filters and Bode plots, after the Eltrex call

**Role(s):** engineering, purchasing

## Goal

Read the Copley manuals after the call with Eltrex on 2026-11-23. Check the control loop block
diagrams, the filters and the frequency analysis tool in the CME setup software. Say which open
questions from the call they answer, and what we still must ask Copley.

The three documents are now in the parts library, under `modules/copley/docs/datasheets/` in
`refaqt/stoq`:

- CME User Guide 16-01157 Rev 05 (July 2026)
- Xenus Plus User Guide 16-01344 Rev 08 (October 2024)
- Xenus Plus XEL datasheet 16-01637 Rev 02

All three describe the **XEL** (Xenus Plus, the drive we asked a quote for). Eltrex offered the
**XEC-230-09** (Xenus Plus Compact). We do not have the XEC datasheet yet. Everything below is
true for the XEL. It is probably true for the XEC, because both are "Plus" drives that use the same
CME software, but Copley must confirm it.

## Work Done

### Short answer

- **Yes, CME can make an open loop Bode plot.** It measures gain and phase with a sine sweep and
  saves the result as a .csv file. For the velocity loop it measures the open loop directly, while
  the loop stays closed. For the position loop it measures the plant while the loop stays closed.
  We then multiply by the position controller ourselves to get the open loop. A mode with the
  position loop fully open also exists, but it is risky on our stage. The modes for the position
  loop need drive firmware 4.92 or later.
- **This does not match what Eltrex said in the call** ("Copley has no Bode plot for the position
  loop"). The manual of July 2026 says it can. Copley must confirm it for the XEC-230-09 and for the
  firmware on the units in stock.
- **The filters are good enough.** The velocity loop has an input filter and an output filter.
  Each can be a free second-order filter (biquad) with our own coefficients. CME also offers
  notch, low-pass, high-pass and band-pass filters, a current loop filter, and input shaping.
- **Copley also has gain scheduling.** In the call this was named as an Elmo advantage. Copley can
  change Pp, Vp, Vi and a current offset from a table of up to 1000 rows. The table key can be the
  actual position.
- **The drive can read the MK21 temperature sensor itself.** This is new. On 2026-11-18 we wrote
  that we need a separate module. The XEL has a motor temperature input that works with a PTC
  (posistor) sensor. Copley must confirm the same input on the XEC.
- **The XEL needs an external brake resistor** for braking energy that the drive cannot store.
  How much energy the XEC can store is not in our documents.

### The control loops

Source: CME User Guide sections 2.3.1, 12.4 and 12.6, and Xenus Plus User Guide section 2.2.

The drive has three nested loops. The trajectory generator feeds the position loop. The position
loop feeds the velocity loop. The velocity loop feeds the current loop.

| Loop | Rate | Controller | Filters |
| --- | --- | --- | --- |
| Position | 4 kHz (250 µs) | Pp, Pi, Pd and Pi drain. Velocity feedforward (Vff) and acceleration feedforward (Aff). A gain multiplier after the sum | None named in the manuals |
| Velocity | 4 kHz (250 µs) | Vp and Vi, with Vi drain. A "gains shift" gives finer steps for linear motors with sub-micrometre encoders | One input filter and one output filter. Each is a 1-pole or 2-pole low-pass, or a custom biquad |
| Current | 16 kHz (62.5 µs) | Cp and Ci. Auto tune in CME | One current loop filter |

The velocity loop always uses the motor encoder, also when a second encoder sits on the load.

The block diagrams in the manuals are simple. They show the order of the blocks and where the
limits and filters sit. They do not give the discrete-time equations, the sample time of each
filter, or the number format.

### The filters

Source: CME User Guide chapter 17.

- **Where:** analog input, velocity loop (input and output), current loop, input shaping, and
  separate motor and load velocity filters. The last two only change the velocity that is shown
  and reported. They do not change the servo loops.
- **Types:** low-pass, high-pass, notch (band stop), band-pass and custom biquad.
- **Families:** Butterworth, Chebyshev and elliptic.
- **Custom biquad:** two poles and two zeros. We enter the coefficients as decimal numbers. The
  drive rounds them, because it stores them in a fixed-point format.
- **Decimation:** a filter can run every N servo cycles instead of every cycle.
- **Input shaping:** zero vibration (ZV), ZVD, negative ZV, negative ZVD, or custom times and
  amplitudes. It shapes the command so a known mechanical resonance is not excited.
- **Default:** "Default" sets a 200 Hz low-pass as the first velocity loop output filter.

Not in the manuals: how many filters sit in series at each place, the rate at which each filter
runs, and the fixed-point format of the coefficients.

### The frequency analysis tool

Source: CME User Guide chapter 18.

CME runs a sine sweep, from 0.1 Hz to 10 kHz, with 2 to 100 points spread equally over each
decade. It plots magnitude and phase. It can show the -3 dB line and the -180° line, and has
cursors to read the gain margin and the phase margin. **File > Save Current Plot** writes a .csv
file that we can open in our own tools.

The manual uses three words:

- **Closed loop:** controller and plant, with feedback.
- **Open loop:** controller and plant, without feedback.
- **Plant:** the motor and load, with the inner loops closed, without the controller of the outer
  loop. For the position loop, the plant is the motor and load with the velocity loop and the
  current loop closed.

The twelve modes:

| Mode | Outer loop during the test | What we get |
| --- | --- | --- |
| 1. Current closed loop | Closed | Current loop bandwidth |
| 2. Velocity closed loop | Closed | Velocity loop bandwidth |
| 3, 4. Velocity open loop (HF, LF – Servo) | Closed | **Open loop of the velocity loop.** Gain and phase margin |
| 5, 6. Velocity plant (HF, LF – Servo) | Closed | The plant of the velocity loop: motor, load and current loop |
| 7, 8. Position plant (HF, LF – Servo) | Closed | The plant of the position loop: motor, load, velocity loop and current loop |
| 9. Velocity open loop | Open | Open loop of the velocity loop, for a system that is not tuned yet |
| 10. Velocity plant | Open | Velocity plant, for a system that is not tuned yet |
| 11. Position open loop | Open | **Open loop of the position loop**, measured directly |
| 12. Position plant | Open | Position plant, for a system that is not tuned yet |

"HF" and "LF" are two ways to measure: one is better at high frequencies, the other at low
frequencies. The manual says: run both and join the two curves where they meet.

Modes 1 and 2 need firmware 2.28 or later. The open loop modes and the position modes need
firmware 4.92 or later, and CME 8.1 Beta 26 or later.

### So: can we make an open loop Bode plot of the position loop?

Yes, in two ways.

1. **Mode 11, position open loop.** This measures the open loop directly. But the position loop is
   open during the test. The axis is then held only by the software position limits and the
   velocity limit. When a limit is reached, the drive stops pushing current but does not brake the
   axis. The manual warns that the axis can coast through the limit. With 15 to 40 kg on a short
   stroke, this is a real risk. We would need homing first, wide soft limits and end stops.
2. **Modes 7 and 8, position plant with the loop closed.** This is the safer way. We save the
   plant as .csv, and multiply it by the position controller (Pp, Pi, Pd, the gain multiplier and
   the 250 µs delay) in our own script. The result is the open loop of the position loop. For this
   we need the exact equation the drive uses for the position controller, with units. That is a
   question for Copley.

For the velocity loop it is simpler: modes 3 and 4 measure the open loop directly, with the loop
closed.

### Other points from the manuals

- **Gain scheduling** (CME chapter 22). The drive changes Pp, Vp, Vi and a current offset (in A)
  along a table, with linear interpolation between rows. The key can be the commanded or actual
  velocity, the commanded or actual position, or a value our controller writes over EtherCAT
  (index 0x2371). A table of current offset against actual position could cancel the cogging of
  the iron-core MK21. The manual does not name this use. Ask Copley.
- **Encoder correction tables** (CME chapter 21). The drive adds a stored 16-bit offset to each
  encoder position. Firmware 2.24 or later. Details are in Copley application note AN126.
- **Motor temperature** (XEL datasheet, J10 pin 7, input AIN3 "Motemp"). The input has a 4.99 kΩ
  pull-up to +5 V and a 12-bit converter. The drive faults when the voltage passes a level we set.
  With the three PTC of the MK21 in series:

  | PTC state | Resistance | Voltage on the input |
  | --- | --- | --- |
  | Cold, 25 °C | 300 Ω or less | about 0.28 V |
  | Must not trip (Tk − 5 K) | 1650 Ω or less | about 1.24 V |
  | Must trip (Tk + 5 K) | 3990 Ω or more | about 2.22 V |

  A fault level of about 1.5 V lies between the two. The input never sees more than 5 V, and the
  MK21 sensor allows 30 V. The voltages ignore the small extra load of the input circuit, so
  Copley must confirm the level. This matches what Eltrex said in the call: we can use an input of
  the drive and trigger a stop.
- **Brake resistor** (Xenus Plus User Guide 2.13.1, XEL datasheet). The XEL has a switch for an
  external resistor, but no resistor inside. The switch turns on above 390 V on the bus. The
  matching Copley resistor for the XEL-230-18 is the XTL-RA-03 (30 W). The manuals give no energy
  that the XEL bus capacitors can take. For scale: 40 kg at 1 m/s holds 20 J, at 2 m/s 80 J.
- **Encoder** (XEL datasheet). BiSS (B and C) and SSI. The drive reads the encoder at the current
  loop rate, 16 kHz. The number of data bits is programmable. The maximum number of bits and the
  clock frequency are not given. Two +5 V outputs of 400 mA each.
- **Safe Torque Off.** In 2019 the XEL datasheet changed the name "Safe Torque Off" to "Motor
  Torque Off". No STO certificate is named for the XEL. Eltrex says the XEC has STO.

### Open questions from the call, after reading

| Question in the meeting notes | Status now |
| --- | --- |
| 8. Brake resistor inside or outside? | XEL: outside, there is no resistor inside. XEC: still open |
| 10. Full 32-bit BiSS-C, status bits, CRC, clock | Partly. BiSS-C is supported and read at 16 kHz. Bits and clock still open |
| 11. Encoder supply | Answered for the XEL: 400 mA at 5 V. Check the RSF encoder current at 5 V |
| 12. Filters and block diagram | **Answered.** Free biquads, notch and more. Block diagrams in CME. Filter rates and count still open |
| 13. Feedforward | **Answered.** Vff and Aff, plus Pi and Pd in the position loop, plus gain scheduling |
| 14. Open loop and closed loop Bode, export | **Answered by the manual: yes, with .csv export.** Copley must confirm for the XEC and the firmware in stock |
| 22. Temperature sensor | **Answered for the XEL:** the drive reads the PTC on AIN3. Confirm for the XEC |
| Eltrex action: can we record position and torque data? | Partly. The CME scope records traces, and the frequency analysis saves .csv. Sample rate and length still open |

### Questions for Copley

1. Please send the XEC-230-09 datasheet. Does the XEC have the same CME features as the XEL: the
   twelve frequency analysis modes, the filters, gain scheduling and encoder correction tables?
2. Which firmware is on the XEC-230-09 units in stock? We need 4.92 or later for the open loop and
   position modes. Can we update it ourselves, for free?
3. Do the position plant (Servo) modes and the position open loop mode work with a linear motor
   and a BiSS-C encoder? Is there a mode that measures the open loop of the position loop while the
   loop stays closed, like modes 3 and 4 for the velocity loop?
4. What are the exact equations of the position loop and the velocity loop, with units and scaling
   of Pp, Pi, Pd, Vp, Vi, Vff, Aff and the gain multiplier? We want to compute the open loop from
   the measured plant.
5. Filters: how many filters sit in series at each place? At which rate does each filter run
   (4 kHz or 16 kHz)? What fixed-point format do the biquad coefficients use? Can we write them over
   EtherCAT, and with which objects?
6. Can gain scheduling with the actual position as key and the current offset as output be used
   to cancel motor cogging? What position step and table size are possible? Is there a better
   feature for cogging?
7. BiSS-C: does the XEC read 32 position bits, the 2 status bits and the 6-bit CRC? Which clock
   frequency does it use? What is the top speed with a 0.1 µm step?
8. Motor temperature on the XEC: is the input the same as AIN3 on the XEL (4.99 kΩ to +5 V)? Is a
   fault level of 1.5 V right for three PTC in series that must trip between 1650 Ω and 3990 Ω?
9. Does the XEC-230-09 have a brake resistor inside? How much energy (in J) can its bus capacitors
   take at 230 VAC before the resistor switches on?
10. Can the CME scope or the drive record position, velocity and current at 4 kHz or 16 kHz, for
    how long, and can we read the data over EtherCAT for our own frequency sweep?

### Update: the XEC documents (same day)

The Copley product page of the Xenus Plus Compact has the XEC datasheet (16-01435 Rev 04), the
user guide (16-01552 Rev 02), the STO manual, the EC Declaration of Conformity and the firmware.
They are now in the parts library, in `modules/copley/`. They answer three points for the
XEC-230-09:

- **Temperature sensor: yes.** Input IN11 is a digital input with a 4.99 kΩ pull-up to +5 V. The
  datasheet says it works with PTC thermistors to BS 4999 Part 111, with 1650 Ω at 95 °C and
  3990 Ω at 105 °C. Those are exactly the MK21 values. The input switches on above 3.15 V, which is
  about 8.5 kΩ, so it trips a few kelvin above the 3990 Ω point. No separate module is needed.
- **Brake resistor: inside.** 60 Ω, 20 W continuous, 2500 W for 100 ms, 248 J at most. The bus
  (940 µF) takes 34 J at 200 VAC and 17 J at 240 VAC first. For 40 kg at 2 m/s (80 J), about 55 J
  goes into the resistor. That is fine for single stops. Frequent hard stops are limited by the
  20 W. An external resistor is optional.
- **BiSS-C: supported (B and C), 4-wire, clock from the drive.** The number of bits and the clock
  frequency are not given. This stays a question.

Two new points:

- **Firmware.** The Copley page offers XEC firmware 4.36 and 4.60. The CME guide asks for 4.92 or
  later for the open loop and position frequency analysis modes. So the position loop Bode plot
  may not work on the XEC with the published firmware. This is now the most important question.
- **Safety and CE are documented.** STO is certified by UL (ISO 13849-1, IEC 61508,
  IEC 61800-5-2), and the STO manual shows a SIL 3, Cat. 3, PL d example. The EC Declaration of
  Conformity names EMC to IEC 61800-3 category C3. This answers meeting question 19 and most of 18.

## Results

- The three Copley documents are in the parts library, with a record for the XEL family.
- The question "can we make a Bode plot of the position loop with Copley?" now has a sourced
  answer: yes, with two methods, if the firmware is 4.92 or later.
- Three earlier statements need a correction: the position loop Bode plot (Eltrex in the call),
  the temperature sensor (the comparison of 2026-11-18), and gain scheduling as an Elmo-only
  advantage.

## Open Questions

- Everything in the list of questions for Copley above.
- The safety points stay open: the STO level and certificate, the EU Declaration of Conformity and
  the EMC category.

## Next Steps

- Send the questions to Copley, through Eltrex or directly.
- Ask Eltrex for the XEC-230-09 datasheet with the quote.
- When the answers come in, update the Copley row in
  [`servo-drive-selection.md`](../servo-drive-selection.md).
