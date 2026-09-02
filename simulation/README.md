# Simulation

Design-time analysis: models that predict behaviour before or instead of measuring it. The measured
counterpart lives in [`measurement/`](../measurement/) — see
[`doqs/docs/architecture.md`](../doqs/docs/architecture.md) for the distinction.

| Case | Tool | Question |
| --- | --- | --- |
| [`housing-vibrations`](cases/housing-vibrations/) | Octave (`control`) | How do stage, housing, base and reaction masses respond to feed-driven acceleration? |
| [`mass-system`](cases/mass-system/) | Octave (`symbolic`) | Symbolic equivalent mass of the coupled two-mass system |
| [`pwm-rc-filter`](cases/pwm-rc-filter/) | Python | What PWM resolution and RC corner give the best torque-command ENOB? |
| [`short-stroke-actuator-concepts`](cases/short-stroke-actuator-concepts/) | Python | Can a two-sided 200 N / 0.1 mm / > 10 Hz actuator fit 50 × 50 × 20 mm under 100 EUR? |

Results summaries belong in `results/<case-slug>/summary.md`. Heavy outputs
(`results/<case>/exports/`) are gitignored.

## Running

```bash
octave simulation/cases/housing-vibrations/housing_vibrations.m
python simulation/cases/pwm-rc-filter/pwm_filter_optimizer.py
python3 simulation/cases/short-stroke-actuator-concepts/size_concepts.py
```

Octave cases need `pkg load control` and `pkg load symbolic`.
