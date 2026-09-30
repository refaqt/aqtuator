# 2026-09-30 — Tonghang drives checked against the drive requirements

**Role(s):** engineering, purchasing

## Goal

Check whether Zhejiang Tonghang E-Drive Technology (web site tonghangedrive.com) sells a servo drive
that meets the requirements in [`architecture/motor-drive.sysml`](../../architecture/motor-drive.sysml).
If not, say by how much each drive misses.

## Work Done

### Short answer

- **No Tonghang drive meets the requirements.** Every drive fails at least three hard requirements.
- **The closest drive is the T6DE (or T6E) EtherCAT drive, 220 V version.** It has the right supply
  voltage, EtherCAT with the CiA 402 drive profile, and very likely enough current. But it is made
  for Tonghang's own rotary motors. It does not read a 1 Vpp encoder, no document says it can run a
  linear motor, and the position loop rate is not published.
- **The only Tonghang drive that reads a sine and cosine encoder is the S3a spindle drive.** It has
  no EtherCAT, it needs 380 VAC, and its smallest size is ten times too strong for the MK21.
- Tonghang publishes no manuals. The download centres on both of their web sites are empty. One
  manual for a sister drive (T3D) is on a third-party site. It confirms a simple drive for rotary
  motors: the motor pole pair setting only allows 4 or 5, and the only loop filters are simple time
  constants.

### Tonghang T6DE / T6E, 220 V (the closest drive)

| Req. | Needed | T6DE / T6E | Result | Gap |
| --- | --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | The smallest size (L15) runs Tonghang motors of up to 3.5 A rated | Likely pass. No drive rating found | Not confirmed |
| DRV-02 | 5.9 A rms for 1 s | Same motors with an overload ratio of 3, so about 10 A | Likely pass | Not confirmed |
| DRV-03 | Peak current limit and a motor thermal model | Overload protection and a torque limit parameter on the sister drives. No thermal model described | Not confirmed | Thermal model not documented |
| DRV-04 | DC bus 160 V to 600 V | 220 VAC input, about 310 V bus | Pass | None |
| DRV-05 | Linear synchronous motor, 30 mm period, finds the commutation angle | Not mentioned. Motors are identified from Tonghang's own encoder | Fail on paper | No linear motor mode found at all |
| DRV-06 | Reads the motor thermal sensor, or stops on an input | Only two digital inputs, both taken (servo on, alarm reset) | Not confirmed | No free stop input shown |
| DRV-07 | EtherCAT with CiA 402 | EtherCAT, CoE, CiA 402, with cyclic synchronous position, velocity and torque modes | Pass | None |
| DRV-08 | 1 Vpp sine and cosine at 8.3 kHz | Tonghang 17 or 23 bit serial absolute encoder, or incremental A/B pulses | Fail | No analog input. A 1 Vpp to A/B converter would be needed |
| DRV-09 | Position loop 4 kHz or faster | Not published. Only "velocity frequency response ≥1.6 kHz" on sister drives | Not confirmed | Ask Tonghang |
| DRV-P1 | Free second order filters | Sister drive manual: first order torque filter only, no notch filter | Fail | No biquad and no notch |
| DRV-P2 | Published loop diagram | None | Fail | Not published |

### Tonghang S3a spindle drive (the only one with sine and cosine input)

| Req. | Needed | S3a | Result |
| --- | --- | --- | --- |
| DRV-01 / DRV-02 | 2.0 A and 5.9 A rms | Smallest size gives 20 A rms maximum | Passes, but it is 3.4 times the MK21 peak. The current limit must then be set very low |
| DRV-04 | 160 V to 600 V | 380 VAC three phase, about 540 V bus | Pass, but needs a three phase supply |
| DRV-07 | EtherCAT | RS485, analog and pulse commands only | Fail |
| DRV-08 | 1 Vpp | "Sine-cosine encoder" is listed. The signal level is not stated | Not confirmed |
| DRV-05 | Linear motor | Made for spindle motors | Fail on paper |

### Other Tonghang drives

The T3a, T3L, T3D, T3DF, C30G, T3M, T3G, T3C and T5a drives take pulse or analog commands. They
fail DRV-07. The T5ML and T6M use Tonghang bus types, not EtherCAT. The T3DC uses CANopen. None of
them reads a 1 Vpp encoder. The "showroom" pages on the site list parts from other brands, not
Tonghang products.

## Decisions Made

No Tonghang drive goes onto the short list.

## Open Questions

None that change the answer. Even if Tonghang confirms a fast position loop, the T6DE still has no
1 Vpp input and no documented linear motor mode.

## Next Steps

None for Tonghang, unless they offer a custom firmware for linear motors. Their product pages say
they make custom versions. That would be worth one e-mail only if no other drive works.

<details>
<summary>Sources</summary>

- Product pages, read on 2026-09-30: https://www.tonghangedrive.com/servo-driver-series/ and each
  series page below it, in particular `t6e-t6de-ethercat-bus-universal-servo-driver/` and
  `s3a-series-spindle-servo-driver/`.
- T6DE model code image on the T6E/T6DE page: feedback type A is a serial absolute encoder,
  F is an incremental pulse encoder. Power stages L15, L20, L30 at 220 V, H at 380 V.
- T6DE wiring diagram image: two digital inputs (SON, ACLR), two outputs (RDY, BRK).
- Current: motor adaptation table on the T5a page (L15 drives motors up to 3.5 A rated, overload
  ratio 3). This is a motor table, not a drive rating.
- "Velocity frequency response ≥1.6 kHz": T3D and T5a spec tables.
- T3D commissioning manual V1.3, hosted by a third party:
  https://www.cncdrive.com/downloads/T3D_servodrive.pdf (P-201 pole pairs 4 or 5; P-007 torque
  filter time; no notch filter).
- Download centres on tonghangedrive.com and thservodrive.com were empty.

</details>
