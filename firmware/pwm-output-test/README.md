# pwm-output-test

Generates a PWM sine wave for validating the RC output stage without an ODrive attached — Stage A of
the two-stage debug procedure in
[`../torque-excitation/README.md`](../torque-excitation/README.md).

The sketch documents the f_pwm versus resolution versus ripple trade-off in a table. The numerical
version of that trade-off is [`simulation/cases/pwm-rc-filter`](../../simulation/cases/pwm-rc-filter/).
