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

## Mistake logging template
## [Short description] — [Date]
**What happened:** [One or two sentences]
**Root cause:** [Why did this happen?]
**Fix applied:** [What was done to correct it?]
**Prevention rule:** [One concrete rule to avoid this in the future]
**Affected files:** [List of files involved]


