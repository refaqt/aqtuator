# Simulation

Design-time analysis: models that predict behaviour before or instead of measuring it. The measured
counterpart lives in [`modules/flexure-ball-screw-servo-stage/measurement/`](../modules/flexure-ball-screw-servo-stage/measurement/) — see
[`doqs/docs/architecture.md`](../doqs/docs/architecture.md) for the distinction.

| Case | Tool | Question |
| --- | --- | --- |
| [`encoder-stray-field`](cases/encoder-stray-field/) | Python (`magpylib`) | How strong is the linear motor field at the encoder read head, and how much does a steel plate lower it? (Magnet sizes are a worst-case guess; measure before ordering.) |
| [`housing-vibrations`](cases/housing-vibrations/) | Octave (`control`) | How do stage, housing, base and reaction masses respond to feed-driven acceleration? |
| [`mass-system`](cases/mass-system/) | Octave (`symbolic`) | Symbolic equivalent mass of the coupled two-mass system |
| [`pwm-rc-filter`](cases/pwm-rc-filter/) | Python | What PWM resolution and RC corner give the best torque-command ENOB? |
| [`short-stroke-actuator-concepts`](cases/short-stroke-actuator-concepts/) | Python | Can a two-sided 0.1 mm / > 10 Hz actuator fit 50 × 50 × 20 mm under 100 EUR? (200 N reluctance is pole-face Maxwell, not packaged continuous — Fluxthor catalog check in the case README.) |
| [`strip-seal-fatigue`](cases/strip-seal-fatigue/) | Python | Which strip material and roller size does the seal need, and how should its life be stated? (Fatigue values are measured supplier data, and they hold for dry air only.) |
| [`strip-seal-preload`](cases/strip-seal-preload/) | Python (`numpy`, `scipy`) | Which radius does a 0.25 mm strip really take over 10 mm rollers, how does the pull change it, and can 304 replace 301? (Layout read off a sketch; confirm against CAD.) |

Results summaries belong in `results/<case-slug>/summary.md`. Heavy outputs
(`results/<case>/exports/`) are gitignored.

## Running

```bash
octave simulation/cases/housing-vibrations/housing_vibrations.m
python simulation/cases/pwm-rc-filter/pwm_filter_optimizer.py
python3 simulation/cases/short-stroke-actuator-concepts/size_concepts.py
python3 simulation/cases/encoder-stray-field/stray_field.py
python3 simulation/cases/strip-seal-preload/strip_seal_preload.py
```

Octave cases need `pkg load control` and `pkg load symbolic`.
