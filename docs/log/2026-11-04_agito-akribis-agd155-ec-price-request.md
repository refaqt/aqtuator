# 2026-11-04 — Agito Akribis AGD155-EC checked, and a price request for the comparison

**Role(s):** engineering, purchasing

## Goal

The user wants to know what the Agito Akribis AGD155-EC costs, so the drive comparison has one
more price to compare against. Agito Akribis stays excluded under the rule of 2026-10-06: we do not
buy from Israeli suppliers. This entry checks the drive against the drive requirements and gives a
draft email that asks for a quotation and for the technical points that are still open.

## Work Done

### Short answer

- **The AGD155-EC stays excluded.** We ask for a price only to compare. Its own product manual
  says the drive is "designed by Agito Akribis Systems Ltd. in Israel", and Akribis Systems Pte Ltd
  in Singapore sells it under licence.
- **On paper, the AGD155-EC-2A06 meets all ten hard requirements.** Two points need the maker's
  answer: the Bode plot tool is described in the catalogue, not in a software manual, and the type
  of the motor thermal sensor is still unknown.
- **It is strong where the other candidates are weak.** All loops run at 16 kHz (62.5 µs). That is
  four times faster than the 4 kHz of the Kollmorgen AKD and the Copley Xenus Plus, so it also meets
  the 8 kHz preference (DRV-P3). The sine and cosine (1 Vpp) input accepts 250 kHz. We need 150 kHz.
- **The smallest AGD155-EC is too big for our motor.** It gives 6 A continuous and 18 A peak. The
  MK21 needs 2.0 A and 5.9 A. A drive this size measures small currents less finely. The catalogue
  also lists a smaller model, the AGD156-EC-2A03 (3 A continuous, 9 A peak), which fits the MK21
  better. It has no web page, data sheet or manual, so we cannot check it. We ask for it in the
  email.
- **No price is published.** A web search found no shop or dealer price.

### The AGD155-EC-2A06 against the requirements

Sources: the AGD155 data sheet Rev.3.4, the AGD155 product manual Rev.3.4, the AGD155-EC EtherCAT
reference manual Rev.1.3, and the Agito catalogue 26.5.2. All are Agito Akribis documents. Links
are in the closed block at the end.

| Req. | Needed | AGD155-EC-2A06 | Result |
| --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | 6 A rms | Pass. Three times more than needed |
| DRV-02 | 5.9 A rms for 1 s | 18 A rms for 1.5 s | Pass |
| DRV-03 | Peak current limit and a motor thermal model | Settable maximum motor current and motor rated current. The drive has an I2t thermal fault | Pass |
| DRV-04 | DC bus 320 V to 600 V | 1 phase 110 to 240 VAC. Highest allowed bus 390 VDC | Pass, no margin at low mains voltage. Same as the other 230 VAC drives |
| DRV-05 | Linear motor, finds the commutation angle without Hall sensors | Linear motors allowed. "Auto-phasing" for sine and cosine encoders | Pass |
| DRV-06 | Reads the motor thermal sensor | One input for PT100, PT1000 or a thermostat | Pass, if the MK21 sensor fits one of these. The MK21 sensor type is still unknown |
| DRV-07 | EtherCAT with CiA 402 | EtherCAT (CoE), CiA 402, cyclic synchronous position mode | Pass |
| DRV-08 | Reads 1 Vpp up to 150 kHz, with no converter box | Main encoder port: sine and cosine, "1V pkp @2.5V", up to 250 kHz, 120 Ω termination. Also EnDat 2.2 and BiSS-C | Pass |
| DRV-09 | Position loop 4 kHz or faster | 16 kHz for position, velocity and current (catalogue). The EtherCAT manual gives the position loop cycle as 62.5 µs | Pass |
| DRV-10 | Bode plots in the setup software | PCSuite: frequency domain plant identification. "User can inspect the plant bode, open loop, closed loop". Bode and Nichols charts | Pass, from the catalogue. No software manual in English found |
| DRV-P1 | Free second-order filters | Auto-tuning designs "gains and filters". An application note shows notch filters | Not confirmed. The filter types are not published |
| DRV-P2 | Block diagram of the loop | Not found | Not confirmed |
| DRV-P3 | Position loop 8 kHz or faster | 16 kHz | Pass |

### What the order code means

From the data sheet: AGD155-xx-2Ayy. "EC" is the EtherCAT model. "AF" is the standard model
without EtherCAT. "06" is 6 A rms continuous and 18 A rms peak. "10" is 10 A rms and 30 A rms. The
catalogue order table gives 20 A rms peak for the "10" model. The data sheet and the web page say
30 A rms. We only ask for the "06" model, so this does not matter for us.

### Draft email

To: agito.info@akribis-sys.com

Subject: Request for quotation: AGD155-EC-2A06 and AGD156-EC-2A03 servo drives

> Dear Sir or Madam,
>
> We are building a linear motor stage. We are now comparing servo drives for it, and we would
> like a quotation for your EtherCAT drives.
>
> The motor is a MAXWELL MK21 iron core linear motor. It needs 2.0 A rms continuous and 5.9 A rms
> for 1 s. The encoder gives 1 Vpp sine and cosine signals, with a 20 µm signal period, up to
> 150 kHz. The EtherCAT master is a PC with LinuxCNC.
>
> **Quotation**
>
> 1. The price and delivery time of the AGD155-EC-2A06, for 1 drive and for 2 drives.
> 2. The price and delivery time of the AGD156-EC-2A03 (3 A rms continuous, 9 A rms peak), for 1
>    and for 2 drives. Is this model available in Europe? Please send its data sheet and product
>    manual. We could not find them on your web site.
> 3. The price of the connector kit and of the encoder, Hall and interface cables for each model.
> 4. Is the PCSuite software free? If not, what does it cost? Are the frequency response tools
>    and the auto-tuning included?
> 5. Shipping cost to Belgium, and the payment terms.
>
> **Technical questions**
>
> 6. Does the AGD156-EC-2A03 read a 1 Vpp sine and cosine encoder? If yes, up to which signal
>    frequency, and with which interpolation?
> 7. Please confirm in writing: in cyclic synchronous position mode over EtherCAT, the position
>    loop runs every 62.5 µs (16 kHz). Is this the same for the AGD156-EC?
> 8. The data sheet gives the sine and cosine input as "1V pkp @2.5V". Is this the standard 1 Vpp
>    signal, as from a Heidenhain or Renishaw encoder?
> 9. Which filters can we set in the position and velocity loops? Can we set a general
>    second-order filter (a biquad) with a free numerator and a free denominator? How many filters
>    can be active at the same time?
> 10. Do you publish a block diagram of the control loops, with the place of each gain and each
>     filter?
> 11. Does PCSuite measure the frequency response on the real machine and show it as a Bode plot,
>     with gain and phase? For which loops: the plant, the open loop and the closed loop? Is there
>     a user manual for PCSuite in English?
> 12. The MK21 has a thermal sensor that MAXWELL describes as "3 PNC SNM120 in series". We expect
>     three PTC thermistors in series. Can the thermostat input read this, and at which resistance
>     does it trip?
> 13. Our motor needs only 2.0 A rms continuous. What is the current measurement resolution of the
>     AGD155-EC-2A06? Can we limit the peak current to 5.9 A rms and set the thermal (I2t) model
>     for 2.0 A rms?
> 14. Do you know of customers who use the AGD155-EC with LinuxCNC (EtherCAT master through
>     IgH EtherLab)? Are there known limits?
>
> Thank you in advance. Please send the quotation as a PDF.
>
> Kind regards,
>
> Niels
> AQTUATOR project
> niels@thinkler.be

## Decisions Made

- **Agito Akribis stays excluded.** The rule of 2026-10-06 does not change. See the
  [decision record](../decisions/2026-10-06_kollmorgen-akd-and-copley-xenus-plus-as-candidates.md).
- **We ask Agito Akribis for a price only for the comparison.** The answer goes in the drive
  comparison page as a reference price. It does not make the drive a candidate.

## Open Questions

- The price of the AGD155-EC-2A06 and of the AGD156-EC-2A03.
- Every technical question in the email above. The most important ones are the filter types
  (question 9), the Bode plot tool (question 11) and the thermal sensor (question 12).

## Next Steps

- Send the email above.
- When Agito Akribis answers, add the price to the
  [servo drive selection page](../servo-drive-selection.md), next to the Kollmorgen and Copley
  prices.

<details>
<summary>Sources and details</summary>

Agito Akribis documents, all read on 2026-11-04:

- Product page: <https://agito-akribis.com/agd155-ec/>
- Data sheet Rev.3.4: <https://agito-akribis.com/wp-content/uploads/2026/10/Agito-AGD155-Datasheet-Rev.3.4.pdf>.
  Current, supply, encoder ports (sine and cosine 250 kHz, 13-bit interpolation, 120 Ω), PT100,
  PT1000 and thermostat input.
- Product manual Rev.3.4: <https://agito-akribis.com/wp-content/uploads/2026/10/Agito-AGD155-Product-Manual-Rev.3.4.pdf>.
  Page 2: "designed by Agito Akribis Systems Ltd. in Israel". Page 20: highest DC bus 390 VDC,
  brake resistor starts at 370 VDC.
- EtherCAT reference manual Rev.1.3: <https://agito-akribis.com/wp-content/uploads/2026/10/Agito-EtherCAT-Reference-Manual-Rev.1.3.pdf>.
  Section 3.9: EtherCAT cycle times from 62.5 µs in powers of two. Section 4.3: "The AGD155-EC has
  a cycle time of 62.5 µs", and the drive interpolates the target "to N internal position
  commands" per EtherCAT cycle. Objects 6073h (maximum current) and 6075h (motor rated current).
  Error 0x2350: "Load level fault (I2t, thermal state)".
- Catalogue 26.5.2: <https://agito-akribis.com/wp-content/uploads/2026/04/Agito-Motion-Controls-and-DrivesEN-26.5.2-1.pdf>.
  AGD155-EC page: "Control Sampling Rate 16kHz (Profiler, Position, Velocity, Optional Force,
  Current)". AGD156-EC-2A03: 3 A rms, 9 A rms peak, one encoder port, 16 kHz. PCSuite pages:
  plant identification, Bode and Nichols charts of the plant, open loop and closed loop.
- Application note on disturbance rejection (UPM), Rev.1.1: <https://agito-akribis.com/wp-content/uploads/2026/10/Agito-AN-UPM-Disturbance-Rejection-Rev.1.1.pdf>.
  Shows a notch filter at 1,500 Hz.
- Contact address from <https://agito-akribis.com/contact/>.

</details>
