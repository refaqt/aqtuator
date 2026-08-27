# 2026-01-29 — Stepper driver survey

**Role(s):** engineering

- Stepper motor drivers:

  - [<u>https://www.analog.com/en/products/TMCM-1617.html</u>](https://www.analog.com/en/products/TMCM-1617.html)

**ODrive enable from PlanetCNC**

There is 1 output available, currently being used to drive the spindle in reverse, that we could send to the ODrive to enable the control loop or to send to the Controllino to enable the loop. Perhaps it could be a state machine even that changes state when it gets a transition from low to high.

**Damping of compliant structures**

You're asking about plastics with a \*\*damping coefficient (or damping ratio) of at least 4% (0.04)\*\*, which is relatively high for polymers. This means the material dissipates at least 4% of vibrational energy per cycle, a useful property for vibration control and noise reduction.

\### Understanding the damping coefficient in plastics

\- The \*\*damping ratio\*\* \\ \zeta \\ or \*\*loss factor\*\* (tan δ) around 0.04 or 4% is considered moderate to high damping for plastics.

\- Most common rigid plastics like PLA, ABS, or polycarbonate have lower damping ratios (~0.01–0.03).

\- Elastomers and rubber-like materials generally have much higher damping.

\### Common plastics with damping ≥ 4%

Here are some \*\*commonly available plastics or polymer materials\*\* with damping coefficient (damping ratio or loss factor) around or above 4%:

1\. \*\*Thermoplastic Elastomers (TPEs) and Rubber-like Polymers\*\*

\- These materials combine rubbery elasticity with thermoplastic processability.

\- Typical damping ratios can be \*\*0.05 to 0.2 (5% to 20%)\*\*, much higher than rigid plastics.

\- Examples: Styrene-Butadiene-Styrene (SBS), Styrene-Ethylene-Butylene-Styrene (SEBS), or TPU (Thermoplastic Polyurethane).

2\. \*\*Polyvinyl Chloride (PVC), especially flexible grades\*\*

\- Flexible PVC formulations with plasticizers can have damping ratios around \*\*4% or higher\*\*.

\- Used in vibration damping mats, tubing, and flexible applications.

3\. \*\*Acrylic-based Polymers (PMMA) with additives\*\*

\- Pure PMMA is relatively stiff with low damping (~1-2%), but modified or blended acrylics can reach higher damping.

4\. \*\*Polyurethane (PU)\*\*

\- Depending on formulation, PU elastomers can have damping ratios from \*\*4% up to 30%\*\*.

\- Commonly used in vibration isolators, wheels, and damping pads.

5\. \*\*Nitrile Rubber (NBR) and other synthetic rubbers\*\*

\- Though technically rubbers, they are widely available and used for damping.

\- Damping ratios typically well above 4%.

---

\### Summary

\| Material Type \| Typical Damping Ratio (Loss Factor) \| Notes \|

\|----------------------------\|------------------------------------\|-----------------------------------\|

\| Rigid plastics (PLA, ABS) \| 0.01 – 0.03 (1-3%) \| Low damping \|

\| Flexible PVC \| ~0.04 (4%) \| Plasticized, flexible grades \|

\| Thermoplastic Elastomers \| 0.05 – 0.2 (5-20%) \| High damping, rubber-like \|

\| Polyurethane Elastomers \| 0.04 – 0.3 (4-30%) \| Very high damping, versatile \|

\| Synthetic Rubbers (NBR) \| \>0.1 (10% or more) \| Very high damping, elastomeric \|

---

\### Practical implications

\- If you need \*\*plastic materials with damping ≥ 4%\*\*, look toward \*\*flexible or elastomeric polymers\*\* rather than rigid plastics.

\- These materials are widely available commercially and used in applications for vibration isolation, noise reduction, and impact damping.

\- For example, TPU filaments for 3D printing or flexible PVC sheets can be good starting points.
