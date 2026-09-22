# Mistakes

Incidents worth not repeating, one file per incident, per the doqs convention
`docs/mistakes/YYYY-MM-DD_topic.md`. **Read these before starting work** — the nine entries
hold only two classes of error, and both have repeated.

- **Four** are bash syntax used in PowerShell.
- **Three** are a number or a conclusion reported before the source was opened: the
  `analogWrite` entry, the force density entry, and the fatigue life entry. The rule from
  the force density entry was written too narrowly to catch the next one. It now reads:
  open a supplier data sheet or a standard for the actual material, in the actual size,
  before quoting any number that describes how a real part behaves.

Entry format: [`.agents/skills/mistake-log/SKILL.md`](../../.agents/skills/mistake-log/SKILL.md).

| Date | Entry |
| ---- | ----- |
| 2026-03-25 | [Used bash-style `&&` in PowerShell](2026-03-25_powershell-bash-ampersand.md) |
| 2026-03-25 | [Used bash-style heredoc `<<` in PowerShell](2026-03-25_powershell-bash-heredoc.md) |
| 2026-03-26 | [Double-counted integrator input in torque summing](2026-03-26_double-counted-integrator-input-in-torque-summing.md) |
| 2026-03-27 | [Used bash heredoc for `git commit -m` in PowerShell](2026-03-27_powershell-heredoc-git-commit.md) |
| 2026-03-31 | [Treated `analogWrite()` ISR unsafety as settled too early](2026-03-31_analogwrite-isr-conclusion-premature.md) |
| 2026-04-17 | [Used `&&` and `cd /d` in PowerShell again](2026-04-17_powershell-ampersand-and-cd-again.md) |
| 2026-09-02 | [Treated pole-face Maxwell stress as packaged force density](2026-09-02_maxwell-stress-as-device-force-density.md) |
| 2026-09-17 | [Downloads fail on this network, and the error hides it](2026-09-17_uv-download-certificate.md) |
| 2026-09-22 | [Gave a fatigue life from textbook constants, and got it wrong twice](2026-09-22_fatigue-estimate-without-a-datasheet.md) |
