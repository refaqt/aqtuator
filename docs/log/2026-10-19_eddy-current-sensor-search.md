# 2026-10-19 — Eddy current displacement sensors for the stage error motion test

**Role(s):** engineering, purchasing

## Goal

Find an affordable eddy current displacement sensor to measure the error motions of the linear
stages. The test is a reversal test: one sensor reads a steel straight-edge from 4 positions
(2 in X, 2 in Y) while the stage moves back and forth. The sensor and its driver must cost less
than 500 euro together. The sensor needs 1 µm resolution or finer, 0.5 mm range or more, and an
error below 1 µm inside any 0.1 mm part of the range.

## Work Done

We searched makers worldwide: European, Japanese and US brands, Chinese makers and shops, and the
used market. All candidates are in
[`displacement-sensor-selection.md`](../displacement-sensor-selection.md).

- No new set under 500 euro passes all requirements on a data sheet number.
- No data sheet gives the error inside a 0.1 mm window. Every sensor needs our own calibration on
  the straight-edge to show it.
- The short list: Miran ML33 1 mm (cheapest, shop data only), Baumer IPRM 12 (good repeatability,
  needs our own calibration), used Keyence EX-V01 + EX-305V and Panasonic GP-XC3SE + GP-X3S
  (good data sheets, about 600 to 700 euro used), and Micro-Epsilon DT3005 (best data sheet, no
  public price).
- The page also lists what to watch in the test: calibration on the straight-edge, the steel
  target, temperature, sag of the straight-edge and target size.

## Decisions Made

- The straight-edge is steel. You first chose aluminium, then went back to steel, because most
  sensors are factory calibrated on steel.
- The changing magnetic properties of steel do not spoil the stage result, because you read the
  same track in both reversal runs. The error then goes into the straight-edge result only.
- Used sensors are allowed. Contact gauges and capacitive sensors were left out.
- Unclear shop data counts as "not confirmed", not as a fail. A first draft ruled out the Miran
  ML33 because its shop page contradicts itself. You pointed out that it looks feasible, and it is
  now on the short list.

## Open Questions

- Miran: a real data sheet, the bandwidth for the 0.05 µm resolution, temperature drift,
  calibration target, and the price of the 1 mm set with 0–10 V output.
- Micro-Epsilon: a price quote for the DT3005-U1-M-C1.
- Do we buy a used Keyence or Panasonic set, a little over budget, as a known reference?
- Width and steel grade of the straight-edge. The face must be 3 to 4 times the probe diameter
  wide.
