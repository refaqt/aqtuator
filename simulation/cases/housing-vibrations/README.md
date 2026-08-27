# housing-vibrations

Lumped-mass model of the machine structure: stage, housing, base and reaction masses coupled by
stiffnesses, excited by the acceleration that a given feed speed and corner radius impose.

Used to reason about where a reaction-mass actuator should couple in, and which modes it can
influence. The measured equivalent is [`measurement/cases/tap-tests`](../../../measurement/cases/tap-tests/).

**Tool:** Octave with `pkg load control`.

```bash
octave housing_vibrations.m
```

Model parameters are set at the top of the script. Related reasoning is in the dev-log entries
[2025-06-26](../../../docs/log/2025-06-26_chatter-mass-spring-damper-model.md) and
[2025-09-09](../../../docs/log/2025-09-09_xcos-coselica-mass-spring-damper.md).
