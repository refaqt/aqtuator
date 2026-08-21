# 2026-03-27 — Used bash heredoc for `git commit -m` in PowerShell

**What happened:** I attempted to pass a multi-line commit message via a bash-style heredoc (`<<EOF`) inside `git commit -m ...` and PowerShell rejected it with a parser/redirection error.
**Root cause:** Reused a bash-only commit-message pattern without adapting to the current shell (PowerShell).
**Fix applied:** Re-ran the commit using PowerShell-safe `git commit -m "..." -m "..."` (or a temporary message file).
**Prevention rule:** In this repo on Windows, assume PowerShell unless proven otherwise; avoid bash heredocs and `&&` entirely for git commands.
**Affected files:** `docs/mistakes.md`
