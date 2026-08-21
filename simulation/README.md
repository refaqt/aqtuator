# Simulation

Design-time analysis: models that predict behaviour before or instead of measuring it. The measured
counterpart lives in [`measurement/`](../measurement/) — see
[`doqs/docs/architecture.md`](../doqs/docs/architecture.md) for the distinction.

| Case | Tool | Question |
| --- | --- | --- |
| [`housing-vibrations`](cases/housing-vibrations/) | Octave (`control`) | How do stage, housing, base and reaction masses respond to feed-driven acceleration? |
| [`mass-system`](cases/mass-system/) | Octave (`symbolic`) | Symbolic equivalent mass of the coupled two-mass system |
| [`pwm-rc-filter`](cases/pwm-rc-filter/) | Python | What PWM resolution and RC corner give the best torque-command ENOB? |

Results summaries belong in `results/<case-slug>/summary.md`. Heavy outputs
(`results/<case>/exports/`) are gitignored.

## Running

```bash
octave simulation/cases/housing-vibrations/housing_vibrations.m
python simulation/cases/pwm-rc-filter/pwm_filter_optimizer.py
```

Octave cases need `pkg load control` and `pkg load symbolic`.
