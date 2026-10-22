# 2026-10-22 — Cheap inductive limit switches with a plug, and their cables

**Role(s):** engineering, purchasing

## Goal

Find cheap limit switches for the compact stage. They must work without contact (inductive), be
small, and have a plug in the sensor body instead of a fixed cable. The matching cables must be
ready-made, so we can plug them in and route them through the axis. Everything must be bought in
euros from a European web shop.

## Short answer

- **Sensor: autosen AI052.** M8 thread, 2 mm sensing distance, face level with the metal around it
  (flush). PNP output, normally closed (NC), 10 to 30 V DC, built-in 3-pin M8 plug. About €18.95
  before VAT at [autosen](https://autosen.com/en/Position-Sensors/Inductive-sensors/Inductive-sensor-Standard-Class-IP67-AI052).
- **Cable: autosen AA068.** 2 m, PVC, straight 3-pin M8 socket to open wire ends, rated for drag
  chains (cable carriers). About €4.45 to €4.68 before VAT at
  [autosen](https://autosen.com/en/Sensor-cable-M8-3P-PVC-2m-IP67-AA068).
- **One limit switch with its cable costs about €23.40 before VAT**, plus shipping. Both parts come
  from one shop.
- Both parts are now in the parts list of the compact stage, two of each:
  [`modules/compact-stage/bom/bom.csv`](../../modules/compact-stage/bom/bom.csv). Prices stay in
  this log, because the parts list holds no prices.

## Why normally closed

A normally closed sensor opens its signal when it sees the target, and also when the cable breaks.
The drive then sees a broken wire as "end of travel" and stops. That is the safe reaction for a
limit switch.

## Sensors compared

All prices were read on 2026-10-22 from shop pages and search results. They can change.

| Sensor | Shop | Price per piece | Range | Plug | Comment |
| --- | --- | --- | --- | --- | --- |
| autosen AI052 | autosen | €18.95 before VAT | 2 mm flush | M8 | **Chosen.** More than 50 in stock. |
| autosen AI053 | autosen | about the same | 4 mm non-flush | M8 | Use it if the target must be further away. |
| Omron E2B-S08LS01-MC-B2 | [Sorotec](https://www.sorotec.de/shop/Inductive-switch-M8-24-V-1-mm-PNP-NC-9175.html?language=en) | €16.80 with VAT | 1 mm | M8 | Cheapest, but half the range. |
| autosen AI024 | autosen | about €38 before VAT | 2 mm flush | M8 | Heavy-duty version. Too expensive. |
| Sick IME08-02BPOZT0S | TME | about $37.60 | 2 mm | M8 | Out of stock. TME showed only dollar prices. |
| Telemecanique XS108B3PBM8 | TME | about $66 | 2.5 mm | M8 | Too expensive. |
| Lanbao LR08BF15DPC-E2 | TME | about €20 before VAT | 1.5 mm | M12 | Wrong plug. |
| LJ8A3 and other cheap sensors | marketplaces | €5 to €15 | — | none | Fixed cable. Does not meet the need. |

We chose the AI052 over the Omron. It costs about €2 more, but it senses 2 mm instead of 1 mm. That
leaves more room for mounting errors.

## Cables compared

| Cable | Shop | Price | Head | Rated for drag chains |
| --- | --- | --- | --- | --- |
| autosen AA068, 2 m, PVC | autosen | €4.45 to €4.68 before VAT | Straight | Yes. **Chosen.** |
| autosen AA069, 5 m, PVC | [autosen](https://autosen.com/en/Sensor-cable-M8-3P-PVC-5m-IP67-AA069) | €6.13 before VAT | Straight | Yes |
| autosen AA058, 2 m, PUR | [autosen](https://autosen.com/en/Sensor-cable-M8-3P-PUR-2m-IP67-AA058) | €6.54 to €6.74 before VAT | Angled | Not stated. The page also lists an M12 plug in one place. |
| Phoenix Contact, 2 m, PUR | [stex24](https://stex24.com/911723-m8-sensor-cable-pur-3-pole-socket-angled-drag-chain-capable-a-coding.-length-2.0-metres-911723) | €16.44 to €18.45 | Angled | Yes |
| Phoenix Contact, 2 m, PUR, with LED | [voelkner](https://www.voelkner.de/products/13041207/M8-Sensorleitung-PUR-mit-LED-3-polig-Buchse-gewinkelt-schleppkettenfaehig-A-Kodierung-Laenge-2-0-Meter-schwarzgrau-RAL.html) | €27.70 with VAT | Angled | Yes |

If a straight cable head does not fit behind the sensor, use the angled Phoenix Contact cable. It
costs about €12 more per cable.

## Open Questions

- Do the limit inputs of the chosen drive accept a 24 V PNP signal?
- Is there room behind the sensor for the plug and a straight cable head? This needs a check in
  CAD.
- What is the shipping cost to Belgium from autosen?
- The mass of the sensor and the cable is not yet in the parts list. Read it from the datasheets.

## Next Steps

- Place the two sensors and a steel target on the carriage in the compact stage CAD model.
- Order two AI052 and two AA068 from autosen.
