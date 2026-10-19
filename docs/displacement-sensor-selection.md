# Displacement sensor selection

This page shows every eddy current displacement sensor we looked at for the error motion test of
the linear stages. Error motions are the small sideways shifts and tilts of the carriage while it
moves. The research is in [the log entry](log/2026-10-19_eddy-current-sensor-search.md). If a
number here differs from the maker's own data sheet, the data sheet wins. Tell us, and we fix
this page.

Last updated: 2026-10-19. The ACTUSTECH rows were added the same day, from the maker's own
manuals.

## Short answer

**Best on paper: ACTUSTECH E202 controller with the EU1S probe.** It is the only sensor in the
search that passes DS-01, DS-02 and DS-03 on numbers from the maker's own manual. The resolution
is 0.02 µm, and the error over the full 1 mm range is below ±1 µm. So the error inside any
0.1 mm window is below 1 µm too. The price is not published. Ask ACTUSTECH for a quote. One blog
post estimates 5,000 to 15,000 yuan (about 600 to 1,800 euro), but that post has no source and
may be paid promotion.

No other new sensor set under 500 euro passes all four requirements on a number from a data
sheet. For the other sensors, the error inside a 0.1 mm window (DS-03) is not in the data sheet.
They need our own calibration on the straight-edge to reach it.

The other sensors on the short list, cheapest first:

1. **Shenzhen Miran ML33-A-V2, 1 mm range.** On paper it is as good as the Japanese sets, for
   US$90 to 390. The numbers come from a shop page, not a data sheet, and the page contradicts
   itself in places. Temperature drift and calibration target are not given. Ask Miran for a data
   sheet and the price of the 1 mm set. Because it is cheap, buying one and testing it against
   gauge blocks is the fastest way to know.
2. **Baumer IPRM 12I9505/S14.** The only new sensor under budget with a real µm data sheet. The
   resolution and repeatability are very good, but the output is not straightened (±60 µm over
   2 mm) and it moves ±10 µm with temperature. It works only with our own calibration and a
   stable room.
3. **Keyence EX-V01 amplifier with EX-305V head, used or grey market.** Good data sheet, calibrated
   on steel. About 600 to 700 euro on eBay, so a little over budget.
4. **Panasonic GP-XC3SE controller with GP-X3S head, used.** Same class as Keyence. We found no
   used price yet.
5. **Micro-Epsilon DT3005-U1-M-C1.** The best data sheet in the list. No public price. Ask for a
   quote. It is probably over budget (not confirmed).

## What the sensor must do

Every error value is a half band: "1 µm" means "within +/- 1 µm".

| Short name | Requirement |
| --- | --- |
| DS-01 | Resolution 1 µm or finer |
| DS-02 | Measuring range 0.5 mm or more |
| DS-03 | Error within any 0.1 mm part of the range below 1 µm (linearity and other errors) |
| DS-04 | Sensor and driver together below 500 euro. Used sets are allowed |

The target is a steel straight-edge. One sensor is placed in 4 positions (2 in X, 2 in Y), and the
stage moves back and forth (a reversal test).

## How to read the table

- "n/c" means not confirmed. The number is not in a data sheet, or we could not open it.
- "(calc)" is our own conversion from a percentage of the full range (FS) to µm.
- Linearity is the largest error over the full range, as the maker states it.
- Resolution values are only comparable at the same bandwidth or averaging. The condition is in
  brackets.
- Prices are snapshots from 19 October 2026. Many shop and eBay pages blocked direct reading, so
  several prices come from search results. Check them before you buy.
- "Fails" lists only requirements that fail on a number. DS-03 is "n/c" for a row when the data
  sheet does not give the error inside 0.1 mm. It passes only when the full-range error is
  already below ±1 µm.

## The table

### Short list

| Brand | Model (head + driver) | Data sheet | Range (mm) | DS-01 Resolution | Linearity | Temp. drift | Calibration target | Output | DS-04 Price | Fails | Not confirmed | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Miran (Shenzhen) | ML33-A-V2, 1 mm, probe Φ5 or Φ8 + converter | [Shop page](https://miranyuki.en.made-in-china.com/product/zNlJLqVYhoWu/China-Miran-High-Precision-IP67-Protection-Eddy-Current-Linear-Displacement-Sensor.html) | 1 | 0.05 µm (bandwidth not stated) | ±0.25 % FS = ±2.5 µm (calc) | n/c ("according to the output signal") | n/c | 0–5 V, 0–10 V, 4–20 mA, RS485 | US$90–390, one piece, not tied to a range | none | DS-03, drift, target, exact price | Repeatability 0.1 µm. The page highlights say 0.05 % linearity and 0.01 mm repeatability, which contradict the table. We judge on the table |
| Miran (Shenzhen) | ML33-A-V2, 2 mm, probe Φ8 + converter | same | 2 | 0.1 µm (bandwidth not stated) | ±0.25 % FS = ±5 µm (calc) | n/c | n/c | same | same | none | same | Repeatability 0.2 µm |
| Baumer | IPRM 12I9505/S14 (M12, electronics inside) | [PDF](https://media.baumer.com/mamfile_1968762.pdf) | 0–2 | < 0.012 µm static (10 Hz); < 0.065 µm at 520 Hz | ±60 µm, not straightened | ±10 µm over the temperature range | Steel | 0–20 mA, 15–30 V | €369 net, [sparepartsnow.de](https://www.sparepartsnow.de/produkte/baumer-inductive-sensor-iprm-12i9505s14-dckk8r) (out of stock). US$789–1,136 elsewhere | none | DS-03 | Repeatability < 1 µm. Needs our own polynomial calibration and a stable temperature |
| Keyence | EX-305V head + EX-V01 (NPN) or EX-V01P (PNP) amplifier | [Specs](https://www.keyence.com/products/measure/inductive/ex-v/specs/) | 0–1 | 0.4 µm (64 averages) | ±0.3 % FS = ±3 µm (calc) | 0.07 % FS/°C = 0.7 µm/K (calc) | Iron S45C, SS400 | ±5 V, 24 V | eBay: amplifier £494 new (about €564), US$557 used; head US$94–156 | DS-04 (about €600–700) | DS-03 | Grey market sellers. Check that head and amplifier match |
| Keyence | EX-110V head + EX-V02 amplifier | same | 0–2 | 1 µm (64 averages, to be checked) | ±0.3 % FS = ±6 µm (calc) | 0.07 % FS/°C | Iron S45C, SS400 | ±5 V, 24 V | eBay: amplifier about US$406–428, head about US$194 + shipping | DS-04 (about €530–560) | DS-03 | The Keyence page does not clearly map each resolution to each head |
| Panasonic | GP-X3S head + GP-XC3SE(-P) controller | [Page](https://industry.panasonic.com/global/en/products/fasys/measurement/measurement/number/gp-xc3se-p), [PDF](https://fs-ep-eu-p-industry-pim.wd.pisceu.panasonic.eu/storage/download-files/import/ds_gpx_en.pdf) | 0–0.8 | 0.32 µm (64 averages) | ±0.3 % FS = ±2.4 µm (calc) | 0.07 % FS/°C = 0.56 µm/K (calc) | SUS304 or SPCC | ±5 V, 24 V | n/c (no used offer found) | none | DS-03, DS-04 | Same class as Keyence |
| Panasonic | GP-X5SE head + GP-XC5SE(-P) controller | same | 0–1 | 0.4 µm (64 averages) | ±0.3 % FS = ±3 µm (calc) | 0.07 % FS/°C | SUS304 or iron | ±5 V, 24 V | n/c | none | DS-03, DS-04 | |
| Micro-Epsilon | DT3005-U1-M-C1 (sensor, cable and controller as one set) | [PDF](https://cdn.bestech.com.au/wp-content/uploads/2019/05/eddyNCDT-3005-ID-628.pdf) | 1 (offset 0.1) | 0.5 µm RMS at 5 kHz | ±0.25 % FS = ±2.5 µm | 0.025 % FS/°C = 0.25 µm/K | Steel ("-M") | 0.5–9.5 V, 12–32 V | n/c (ask for a quote) | none | DS-03, DS-04 | Repeatability 0.5 µm. The 2 mm version (S2-M) has 1 µm resolution |

### ACTUSTECH (Anhui Actus Technology, Hefei, China)

These rows were read from the maker's own manuals on 19 October 2026. You asked to judge
ACTUSTECH on resolution only, so the range is shown for information and is not judged. The
resolution is the RMS noise at the middle of the range. The factory calibrates on 6061 aluminium
and Q235 steel, unless the row says otherwise. ACTUSTECH publishes no prices. The website only
offers a quote (phone 0551-65656245, e-mail actusservice@actustech.com). We found no shop
listing on Taobao, 1688, JD.com or eBay.

| Model (probe + controller) | Manual | Range (mm) | DS-01 Resolution | Linearity | Temp. drift | Calibration target | Output | DS-04 Price | Fails | Not confirmed | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EU1S probe + E202 controller | [PDF](https://www.actustech.com/upload/2026-03/177304840565539700.pdf) | 1 (offset 0.1) | 0.02 µm (20 Hz); 0.05 µm (10 kHz) | < ±1 µm | < 0.2 µm/°C | 6061 aluminium, Q235 steel | 0.5–9.5 V and RS422; 12–24 V, 0.8 W | n/c, quote only | none | DS-04 | **Best on paper.** M6 probe, face Φ5.3 mm, so the straight-edge face should be about 16 mm wide or more. DS-03 passes because the full-range error is below ±1 µm |
| EU3S probe + E202 | same | 3 (offset 0.3) | 0.06 µm (20 Hz); 0.15 µm (10 kHz) | < ±3 µm | < 0.6 µm/°C | same | same | n/c, quote only | none | DS-03, DS-04 | M10 probe |
| EU6S probe + E202 | same | 6 (offset 0.6) | 0.12 µm (20 Hz); 0.3 µm (10 kHz) | < ±6 µm | < 1.2 µm/°C | same | same | n/c, quote only | none | DS-03, DS-04 | M18 probe |
| EU8S probe + E202 | same | 8 (offset 0.8) | 0.16 µm (20 Hz); 0.4 µm (10 kHz) | < ±8 µm | < 1.6 µm/°C | same | same | n/c, quote only | none | DS-03, DS-04 | M24 probe |
| EU probes + E281 controller | [PDF](https://www.actustech.com/upload/2026-08/178574863331656100.pdf) | as E202 | as E202, but 5 kHz instead of 10 kHz | as E202 | as E202 | same | ±4 V and RS422; 9–24 V, 3.2 W | n/c, quote only | none | DS-04 | Up to 8 channels in one box. Only useful if we later want several sensors at once |
| ET202, Φ8 probe (industrial) | [PDF](https://www.actustech.com/upload/2026-04/177657538399711700.pdf) | 2 (0.2–2.2) | ≤ 0.005 % FSO = 0.1 µm (calc) | ≤ ±0.1 % FSO = ±2 µm (calc) | ≤ 0.4 µm/K | 45# steel | n/c | n/c, quote only | none | DS-03, DS-04 | Repeatability ≤ 0.1 µm. Made for large rotating machines (API 670) |
| E102SGS (spindle growth sensor) | [PDF](https://www.actustech.com/upload/2026-06/178209130844892400.pdf) | 0.5 (offset 0.1) | 0.5 µm (10 kHz) | < ±2 µm | 0.25 µm/°C | 6061 aluminium, Q235 steel | 0.5–9.5 V and Modbus RTU; 12–24 V | n/c, quote only | none | DS-03, DS-04 | Made to fit inside a machine spindle |
| E302-0.2, -0.5, -0.8 (differential) | [PDF](https://www.actustech.com/upload/2026-06/178210872516783900.pdf) | ±0.2, ±0.5, ±0.8 | < 0.002 to 0.003 % FSO at the zero point | < ±1 % FSO | < ±0.005 % FSO/°C at the zero point | ferromagnetic and non-ferromagnetic | −5 to +5 V; 12–24 V | n/c, quote only | none | DS-03, DS-04 | **Not usable for this test.** It needs a probe on each side of a thin target, so it cannot read one face of a straight-edge |
| ET202H (high temperature) | [Page](https://www.actustech.com/display.php?id=285) | n/c | n/c | "< 1 % FSO typical" | n/c | n/c | n/c | n/c, quote only | none | DS-01 to DS-04 | Up to 600 °C, at least 200 kHz. The manual was not read |
| E101 (electronics in the probe) | [PDF](https://www.actustech.com/upload/2025-08/175645749889048500.pdf) | 4 (offset 0.4) | < 2 µm RMS | < ±0.5 % | < 1 µm/°C | n/c | 0.5–9.5 V; 12–18 V | n/c, quote only | DS-01 | DS-04 | Resolution too coarse |

### Ruled out

| Brand | Model | Range (mm) | Why it fails |
|---|---|---|---|
| Micro-Epsilon | DT3001-U2M-SA, U4M | 2, 4 | Resolution 4 µm (DS-01) |
| Micro-Epsilon | DT3060, DT3061 | 0.4–8 | Over budget new. One used DT3060 seen at €545 ex VAT, out of stock |
| Omron | ZX-ED01T or ZX-EDR5T + ZX-EDA11/41 | 1 or 0.5 | Amplifier about €1,324 (DS-04) |
| Omron | E2C-EDR6-F or E2C-ED01 + E2C-EDA11 | 0.6 or 1 | Switching outputs only, no analog output, no linearity given |
| SICK | IMA08-04BE3ZC0K | 0–4 | Repeatability ±10 µm |
| Contrinex | DW-AD-509-M8, -M12 | 0–4, 0–6 | Repeatability ±10 µm |
| Turck, ifm, Balluff | BI1.5-EG08-LU, IF6028, BAW000W | 1–2 | Error in the 5 to 60 µm class |
| Bently Nevada | 3300 XL 8 mm + 330180 Proximitor | 0.25–2.3 | Straight-line error about ±25 µm (n/c), needs −24 V |
| Chinese 3300-style copies | Yangzhou Xiyuan CWY-D0-401/402, Wuxi Baiyida BYDCWY002, Shanghai Yuanben ECDS-3001 | 1–2 | Linearity ±7.5 to ±30 µm |
| Lion Precision, Kaman | ECL101, ECL110, KD-2306 | various | Far over budget (n/c, no public price) |
| Yoyik | DWQZ series | 0–1.5 | Not confirmed: claims nm resolution with no data sheet |

## Things to watch in the test

- **Calibrate on the straight-edge.** A smooth ±3 µm error over the full range can still change
  the local slope by about 1 %. That is about 1 µm over 0.1 mm. Calibrate the sensor on the steel
  straight-edge itself, with gauge blocks or a micrometer stage, and fit a polynomial. This is the
  only way to show DS-03.
- **Steel target.** Most sets are factory calibrated on iron or steel, so steel fits them. On
  hardened steel, an eddy current sensor also reads small changes in the magnetic properties as
  false distance. Lion Precision measured 5.9 µm of false profile on a hardened steel shaft
  ([article](https://www.lionprecision.com/wp-content/uploads/2019/08/article-PI-electrical-runout-ASPE.pdf)).
  This error moves with the straight-edge. If the sensor reads exactly the same track in both
  reversal runs, the error goes into the straight-edge result and stays out of the stage result.
  The sensor reads a spot about 3 times its own diameter, so a sideways shift of the track breaks
  this. Demagnetizing the straight-edge is still good practice.
- **Temperature.** A drift of 0.07 % FS/°C on a 1 mm range is 0.7 µm per degree. Let the sensor
  warm up, keep the gap near the middle of the range, and run back and forth so a linear drift
  can be fitted out.
- **Sag.** Gravity bends the straight-edge the same way in both reversal runs. For the vertical
  direction the sag therefore ends up in the stage result. Support the straight-edge at the Bessel
  points (0.559 × its length apart) and correct for the calculated sag.
- **Target size.** The face of the straight-edge should be at least 3 to 4 times the probe
  diameter wide. Keep the spot away from chamfers and edges.

## Sources

- Keyence EX-V specifications: https://www.keyence.com/products/measure/inductive/ex-v/specs/
- Panasonic GP-X data sheet: https://fs-ep-eu-p-industry-pim.wd.pisceu.panasonic.eu/storage/download-files/import/ds_gpx_en.pdf
- Micro-Epsilon eddyNCDT 3005: https://cdn.bestech.com.au/wp-content/uploads/2019/05/eddyNCDT-3005-ID-628.pdf
- Micro-Epsilon eddyNCDT 3001: https://cdn.bestech.com.au/wp-content/uploads/2019/05/eddyNCDT-3001-ID-627.pdf
- Baumer IPRM 12 data sheet: https://media.baumer.com/mamfile_1968762.pdf
- Miran ML33 shop page: https://miranyuki.en.made-in-china.com/product/zNlJLqVYhoWu/China-Miran-High-Precision-IP67-Protection-Eddy-Current-Linear-Displacement-Sensor.html
- Omron E2C-EDA data sheet: https://assets.omron.com/m/059ee85f2ae65dc6/original/E2C_EDA_datasheet_en_201403_D814E02-pdf.pdf
- SICK IMA08 data sheet: https://motionworld.com/assets/SICK-IMA08_04BE3ZC0K-Datasheet.pdf
- Contrinex DW-AD-509-M8: https://www.automatyka24.pl/file/30638,DW-AD-509-M8.pdf
- Yangzhou Xiyuan CWY-D0: https://yzxiyuan.en.made-in-china.com/product/wEfYFTvChRkt/China-Cwy-D0-410-25-Linear-Sensor-Factory-Eddy-Current-Sensor-Motion-Displacement-Sensor.html
- Wuxi Baiyida BYDCWY002: https://wxbaiyida.en.made-in-china.com/product/vtXUendlrFhi/China-Bydcwy002-Linear-Range-0-5-2-5mm-Non-Contact-Eddy-Current-Displacement-Sensor.html
- ACTUSTECH product pages: https://www.actustech.com/ (manuals linked in the ACTUSTECH table)
- Blog post with the only ACTUSTECH price estimate (the platform marks it as possible paid
  promotion; it also gives a wrong range for the E202): https://www.cnblogs.com/techexpert/articles/20370490
- Lion Precision, capacitive and eddy current sensors compared: https://www.lionprecision.com/comparing-capacitive-and-eddy-current-sensors
- Lion Precision, target size: https://www.lionprecision.com/customer-supplied-eddy-current-targets/
- Evans, Hocken, Estler, "Self-Calibration: Reversal, Redundancy, Error Separation, and Absolute
  Testing", CIRP Annals 45(2), 1996: https://www.nist.gov/node/744211
