# 2026-10-19 — DGSMARTWIN SA32 absolute encoder: what to order and what to ask

**Role(s):** engineering, purchasing

## Goal

The user supplied the DGSMARTWIN "Servo Driver and Encoder" catalog (2026 edition). Choose an
absolute linear encoder from it. EnDat is allowed. Name the read head, the scale tape and the
mounting parts. List the product numbers and the questions for the supplier.

## Work Done

### Short answer

- **Encoder: SA32, optical, absolute, EnDat 2.2.** It is the only absolute linear encoder in the
  catalog with EnDat. The CA26 magnetic encoder (BiSS-C) has a 1 µm step and fails ENC-01. The
  SAR23 is a ring for a rotary axis.
- **The catalog lists no scale applicator, no end clamps and no other mounting parts.** We must ask
  DGSMARTWIN for them.
- **All numbers come from a sales catalog.** Under our rule for a pass or a fail, the SA32 stays
  "not confirmed" until we have the full data sheet.

### What to order

| Item | Product number | Meaning |
| --- | --- | --- |
| Read head | **SA32EH05A-MC** | EnDat 2.2, 0.05 µm step, 0.5 m cable, 9-pin D-sub plug |
| Read head, other option | SA32EY05A-MC | Same, with a 0.1 µm step. Also passes ENC-01 |
| Scale tape | **SA32-L300-MC** | 300 mm. The catalog shows only "L500 = 500 mm", so the code for 300 mm needs confirmation |
| Extension cable (AKS drive only) | E-FN09-26-L05-TC1 | 9-pin D-sub socket to the 26-pin feedback plug, 5 m. Other lengths: 03, 08, 10, 12, 15, 20 |
| Drive (if the AKS is used) | AKS-…2A-EC-**AB** | Only the "-AB" version reads EnDat 2.2. See the [AKS log entry](2026-10-19_dgsmartwin-aks-drive-for-mk21-with-endat.md) |

- **Why 300 mm of tape:** 200 mm of travel, plus the 36 mm head, plus room at both ends for the
  end fixing. The [encoder price log](2026-10-06_linear-encoder-choice-and-prices.md) uses the same
  length.
- **The TC1 cable matches the SA32 plug.** Data, clock, 5 V and 0 V are on the same pins at both
  ends. The TA1 cable carries sine and cosine signals and is the wrong cable for this head.

### The SA32 against the encoder requirements

| Req. | Needed | SA32 (catalog) | Result |
| --- | --- | --- | --- |
| ENC-01 | Step < 0.2 µm | 0.05 µm (H) or 0.1 µm (Y) | Pass |
| ENC-02 | ±5 µm over 200 mm, no error table | ±2.5 µm/m "after 25° position compensation" | Not confirmed. The condition is not clear |
| ENC-03 | > 3 m/s | 10 m/s, step size not stated | Pass on paper |
| ENC-04 | The drive reads the output | EnDat 2.2 | Depends on the drive. See below |
| ENC-05 | Periodic error ≤ ±0.3 µm | Not given | Not confirmed |
| ENC-06 | Head width < 15 mm | 14.8 mm, but the drawing also shows (15.8) mm | Not confirmed |
| ENC-07 | Head height < 18 mm | 13.5 mm | Pass |
| ENC-08 | Head length < 40 mm | 36 mm | Pass |
| ENC-09 | Scale height < 1 mm | Not given | Not confirmed |
| ENC-10 | Scale width < 12 mm | Not given | Not confirmed |
| ENC-11 | Head angles | ±20 mrad (±1.15°) for roll, pitch and yaw | Pass on paper. The stage values are still open |

Other catalog values: 5 V +10 %, 200 mA. Gap between head and scale 0.55 mm, ±0.2 mm. Side offset
±0.5 mm. Longest measuring length 10 m. Scale expansion 10.1 µm/m/°C. Working range 0 °C to 65 °C.

**About ENC-04:** the old rule allowed only 1 Vpp and BiSS-C. Commit `775f38e` changes the encoder
and drive rules so that any protocol the chosen drive reads is allowed, EnDat 2.2 included. That
commit is on branch `claude/nifty-hamilton-4fn6hx` and is not merged yet. This entry does not
change the rules again.

### Questions for DGSMARTWIN

Scale and mounting:

1. What is the scale: steel tape, glass or another material? What are its width and its
   thickness, with the adhesive?
2. Does the tape have adhesive on the back? Do you sell a tool to apply the tape? Product number?
3. Do you sell end clamps or an end-fixing kit? Product numbers? Or do you fix the tape ends with
   glue? Which glue?
4. Does the tape float on the base, or is it fixed along its full length? The tape expands
   10.1 µm/m/°C. Our aluminium base expands about 23 µm/m/°C. How do you handle this?
5. Do you sell a spacer or gauge to set the 0.55 mm gap?
6. Can we order any length in millimetres, for example 300 mm? What is the shortest length?

Accuracy and signal:

7. What does "±2.5 µm/m after 25° position compensation" mean? Is it at 25 °C? Is the correction
   stored in the head, or must the drive or the controller do it?
8. What is the error within one signal period? What is the signal period of the scale?
9. What is the top speed at 0.05 µm and at 0.1 µm?
10. How many bits does the position word have? Is it pure EnDat 2.2 ("EnDat22"), or EnDat 2.2 with
    extra 1 Vpp signals? Is it licensed by Heidenhain? With which EnDat masters was it tested?
11. Which clock rates does the head support? What is the longest cable at that clock rate?

Electrical:

12. Does the head accept 5 V −5 %, or only 5 V to +10 %? Does it have sense lines for the voltage
    drop in long cables?
13. Which cable lengths are there besides 0.5 m? Which extension cable fits a drive that is not an
    AKS, with open wire ends?

Documents and commercial:

14. Please send the full data sheet, the installation manual, the 3D CAD model, and an accuracy
    certificate for each scale.
15. What is the price for 1 and for 10 sets? What is the delivery time? The catalog gives a
    12-month warranty. Is a test sample available?

## Decisions Made

No purchase decision. The SA32EH05A-MC with an SA32-L300-MC tape goes on the short list as
"not confirmed".

## Open Questions

- All 15 supplier questions above.
- Is the drive for the stage able to read EnDat 2.2? This decides ENC-04.

## Next Steps

1. Send the questions to DGSMARTWIN (win@dgsmartwin.com), together with the drive questions from
   the AKS log entry.
2. Merge the rule change in commit `775f38e`, or decide against it, before the SA32 is judged on
   ENC-04.
3. When the data sheet arrives, add the SA32 to the
   [Linear encoder selection](../linear-encoder-selection.md) page.

<details>
<summary>Sources</summary>

- DGSMARTWIN "Servo Driver and Encoder" 2026 product catalog, supplied by the user: encoder
  support table of the AKS drive (page 05), encoder overview (page 27), SA32 order code and data
  (page 32), SA32 drawing and pin table (page 33), CA26 data (page 36), extension cables TC1 and
  TA1 (page 42).
- Requirements:
  [`modules/compact-stage/architecture/linear-encoder.sysml`](../../modules/compact-stage/architecture/linear-encoder.sysml).

</details>
