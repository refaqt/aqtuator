# 2026-04-17 — Used `&&` and `cd /d` in PowerShell again

**What happened:** I ran a PowerShell command using bash/cmd idioms (`&&` chaining and `cd /d`), causing a parser error / invalid parameter error before the intended commands executed in the correct directory.
**Root cause:** Muscle memory from bash/cmd command patterns; didn’t adapt to PowerShell syntax (`;` chaining and `Set-Location`/`cd` without `/d`).
**Fix applied:** Re-ran with PowerShell-safe separators and directory changes using `Set-Location`.
**Prevention rule:** When running shell commands on Windows PowerShell, never use `&&` or `cd /d`; use `;` and `Set-Location` (or `cd` without flags).
**Affected files:** `docs/mistakes.md`
