# 2026-09-02 — Treated pole-face Maxwell stress as packaged actuator force density

## What happened

The short-stroke reluctance concept was marked PASS at 204 N in 50 × 50 × 20 mm
(4.1 N/cm³) from `F = 2 B0 b A / μ0` on an assumed 20 × 20 mm pole. Fluxthor Atlas,
a commercial reluctance line that advertises the highest electromagnetic force
density, is 0.25–0.41 N/cm³ packaged continuous force (~20 N in our volume).

## Why it went wrong

The lumped formula is magnetic pressure on a pole face, at an assumed B, with no
housing, flexure, thermal rating, leakage, or second air gap in Ampère's law. That
number was compared to (and then used as) a device spec. A first-order model was
treated as the answer before a catalog check — the same class of error as settling
an ISR conclusion before looking at the implementation.

## Prevention rule

When quoting actuator force density, name the quantity: pole-face Maxwell stress,
unsaturated magnetic force, or packaged continuous force. Check at least one
commercial catalog (or a measured part) before treating a lumped Maxwell number as
a spec. If the catalog is ~10× lower, assume the gap is definitional until FEA or
a prototype says otherwise.

## Related

- [2026-09-02 Fluxthor check](../log/2026-09-02_fluxthor-reluctance-force-density.md)
- [short-stroke-actuator-concepts](../../simulation/cases/short-stroke-actuator-concepts/)
- [Treated analogWrite ISR unsafety as settled too early](2026-03-31_analogwrite-isr-conclusion-premature.md)
