# 2026-09-22 — Put back the tooling update to get a clean working tree

## What happened

Agents kept ending a task by undoing the tooling update the same session had just
downloaded. The report looked like this, and it came back session after session:

> Only aqtuator's doqs gitlink is dirty — the one thing AGENTS.md says to leave
> uncommitted. I'll clear it without setting a new pin, by returning the submodule
> to its recorded commit.

The two tooling folders, [`.agents/`](../../.agents/) and [`doqs/`](../../doqs/),
follow the `main` branch of their own repositories. Every session moves them to the
newest version on purpose. Git reported that move as a modified file. The agent
treated it as mess left behind by its own work and removed it, which put the shared
rules, skills and checking scripts back to an older version without saying so.

## Why it went wrong

The instruction in [`AGENTS.md`](../../AGENTS.md) said to leave the two entries
uncommitted. An agent that wants a clean working tree has two ways to get one:
commit the change, or undo it. The instruction closed the first door and left the
second one open, so agents walked through it and believed they were following the
rule. Each one quoted the rule while breaking it.

This is a repeat of the pattern in
[the `analogWrite` entry](2026-03-31_analogwrite-isr-conclusion-premature.md): a
written rule was treated as settled guidance without checking what it actually
covered. Here it was our own rule, and it covered half the problem.

## Prevention rule

**When a working tree is meant to hold a change permanently, hide the change rather
than ask people to leave it alone.** A rule that only says "do not commit this"
still leaves "undo this" open, and someone will take it. Use the setting that makes
the tool stop reporting it.

For these two folders, [`.gitmodules`](../../.gitmodules) now sets `ignore = all`, so
`git status` no longer mentions them. Never move either folder back to the commit
this repository records in order to get a clean tree. To freeze a new version on
purpose:

```bash
git add --force .agents doqs
```

## Related

- [Hide the tooling gitlinks from `git status`](../decisions/2026-09-22_hide-the-tooling-gitlinks.md)
- [A session hook checks out the tooling submodules](../decisions/2026-09-16_cloud-session-submodule-hook.md)
