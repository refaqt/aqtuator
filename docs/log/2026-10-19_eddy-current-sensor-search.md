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

### Update: ACTUSTECH

You asked us to look at ACTUSTECH (Anhui Actus Technology, Hefei, China). We read the maker's own
manuals for all its eddy current sensors and added them to the page.

- The **E202 controller with the EU1S probe** is the best sensor on paper in the whole search.
  Resolution 0.02 µm, range 1 mm, error over the full range below ±1 µm, drift below 0.2 µm per
  degree. It passes every requirement except the price, which is not published.
- The E202 with larger probes, the ET202 and the E102SGS also pass on resolution. The E101 fails
  (2 µm). The E302 is a differential sensor and cannot read one face of a straight-edge.
- ACTUSTECH publishes no prices and has no shop listing we could find. One blog post estimates
  5,000 to 15,000 yuan (about 600 to 1,800 euro) for "same-spec" products, with no source.

## Decisions Made

- The straight-edge is steel. You first chose aluminium, then went back to steel, because most
  sensors are factory calibrated on steel.
- The changing magnetic properties of steel do not spoil the stage result, because you read the
  same track in both reversal runs. The error then goes into the straight-edge result only.
- Used sensors are allowed. Contact gauges and capacitive sensors were left out.
- Unclear shop data counts as "not confirmed", not as a fail. A first draft ruled out the Miran
  ML33 because its shop page contradicts itself. You pointed out that it looks feasible, and it is
  now on the short list.
- ACTUSTECH is judged on resolution only, as you asked. The range is shown for information.
- The page first listed the ACTUSTECH E202 as ruled out, with a range of only ±0.2 mm. That
  number came from a blog post and belongs to another model, the E302-0.2. The maker's manual
  shows E202 probes from 1 to 8 mm. The row is corrected.

## Open Questions

- ACTUSTECH: a quote for the E202 controller with an EU1S probe, 1 m or 3 m cable, analog
  0.5–9.5 V output, calibrated on our steel. Ask for the delivery time and the export terms.
- Miran: a real data sheet, the bandwidth for the 0.05 µm resolution, temperature drift,
  calibration target, and the price of the 1 mm set with 0–10 V output.
- Micro-Epsilon: a price quote for the DT3005-U1-M-C1.
- Do we buy a used Keyence or Panasonic set, a little over budget, as a known reference?
- Width and steel grade of the straight-edge. The face must be 3 to 4 times the probe diameter
  wide.
