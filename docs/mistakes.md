# Mistakes

## Used bash-style `&&` in PowerShell — 2026-03-25
**What happened:** I tried to chain commands with `&&` while running a PowerShell command, which failed with a parser error.
**Root cause:** Assumed bash-style chaining works in the current shell without checking (`powershell` uses `;` or `|` for chaining).
**Fix applied:** Re-ran the command using PowerShell separators (`;`).
**Prevention rule:** When running shell commands on Windows, avoid `&&` unless explicitly using `cmd.exe`; default to PowerShell-safe separators.
**Affected files:** `docs/mistakes.md`

**WARNING (repeated mistake):** I later repeated a similar shell-syntax mistake by trying to use a bash-style heredoc (`<<`) in PowerShell. Treat all bash-only shell idioms as unsafe in this repo unless we explicitly switch shells.

## Used bash-style heredoc `<<` in PowerShell — 2026-03-25
**What happened:** I tried to run `python - <<'PY' ... PY` in PowerShell; PowerShell parsed `<<`/`<` as redirection/operators and the command failed.\n**Root cause:** Muscle memory from bash heredoc usage; didn’t adapt the command to PowerShell.\n**Fix applied:** Re-ran the spot-check using a PowerShell-safe `python -c \"...\"` invocation.\n**Prevention rule:** On Windows PowerShell, never use bash heredocs (`<<EOF`). Use `python -c`, a `.py` temp file, or explicitly run through `cmd.exe`/Git Bash.\n**Affected files:** `docs/mistakes.md`

## Used bash heredoc for `git commit -m` in PowerShell — 2026-03-27
**What happened:** I attempted to pass a multi-line commit message via a bash-style heredoc (`<<EOF`) inside `git commit -m ...` and PowerShell rejected it with a parser/redirection error.
**Root cause:** Reused a bash-only commit-message pattern without adapting to the current shell (PowerShell).
**Fix applied:** Re-ran the commit using PowerShell-safe `git commit -m "..." -m "..."` (or a temporary message file).
**Prevention rule:** In this repo on Windows, assume PowerShell unless proven otherwise; avoid bash heredocs and `&&` entirely for git commands.
**Affected files:** `docs/mistakes.md`

## Double-counted integrator input in torque summing — 2026-03-26
**What happened:** The first integrator attempt computed `torque_unclamped = y_in + (i1 + y_in)` which equals `i1 + 2*y_in` (double-counting the current sample) instead of a pure-integrated output.
**Root cause:** Mixed two different control output conventions (PI-style `y + I` vs pure-integrated `I`) without explicitly defining what the integrator state represents.
**Fix applied:** Switched to pure-integrated output: `i_candidate = i1 + u_in`, `torque_cmd = clamp(i_candidate)`, and freeze `i1` whenever clamped (hold-on-saturation).
**Prevention rule:** Before implementing discrete integrators, write the exact discrete equations and define whether the integrator state is the output or is summed with a proportional path; then translate equations into code 1:1.
**Affected files:** `src/controllino/spindle-controller/spindle-controller.ino`, `docs/mistakes.md`

## Treated `analogWrite()` ISR unsafety as settled too early — 2026-03-31
**What happened:** I initially treated "do not use `analogWrite()` in `timerISR()`" as a settled rule and moved directly to a low-level RP2040 PWM compare-write solution.
**Root cause:** I generalized from timing/determinism concerns before checking the current arduino-pico implementation details and before adding hardware-visible debug instrumentation.
**Fix applied:** Re-checked the core sources, confirmed the mutex path is ISR-aware, and added runtime-selectable PWM strategies plus detailed PWM status instrumentation so hardware behavior can be compared directly.
**Prevention rule:** For embedded timing decisions, distinguish "not ideal for deterministic ISR use" from "proven unsafe," and add observability before locking in one hardware-control strategy.
**Affected files:** `src/controllino/main-controllino/main-controllino.ino`, `docs/mistakes.md`, `docs/skills.md`, `docs/decisions.md`, `docs/architecture.md`

## Mistake logging template
## [Short description] — [Date]
**What happened:** [One or two sentences]
**Root cause:** [Why did this happen?]
**Fix applied:** [What was done to correct it?]
**Prevention rule:** [One concrete rule to avoid this in the future]
**Affected files:** [List of files involved]


