# 2026-03-26 — Runtime control-mode prompt with step/dir gating

**Context:** Operators need to quickly choose between torque and position controller modes at runtime, but the torque-command path should not start while `axis0.config.enable_step_dir` is active.
**Decision:** In `main_sequential.py`, prompt for mode using `t`/`p` with default `p` (position). At startup force `odrv0.axis0.config.enable_step_dir = False`, and after identification/cleanup restore `enable_step_dir = True`.
**Alternatives considered:** Keep control mode hard-coded to position; leave step/dir always enabled; move mode selection to source-code constant only.
**Consequences:** Safer and faster operator workflow without code edits between runs; reduced risk of blocked torque-command behavior during acquisition; cleanup path now explicitly restores step/dir state.
