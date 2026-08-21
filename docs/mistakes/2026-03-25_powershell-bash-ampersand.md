# 2026-03-25 — Used bash-style `&&` in PowerShell

**What happened:** I tried to chain commands with `&&` while running a PowerShell command, which failed with a parser error.
**Root cause:** Assumed bash-style chaining works in the current shell without checking (`powershell` uses `;` or `|` for chaining).
**Fix applied:** Re-ran the command using PowerShell separators (`;`).
**Prevention rule:** When running shell commands on Windows, avoid `&&` unless explicitly using `cmd.exe`; default to PowerShell-safe separators.
**Affected files:** `docs/mistakes.md`

**WARNING (repeated mistake):** I later repeated a similar shell-syntax mistake by trying to use a bash-style heredoc (`<<`) in PowerShell. Treat all bash-only shell idioms as unsafe in this repo unless we explicitly switch shells.
