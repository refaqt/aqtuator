# 2026-09-22 — Hide the tooling gitlinks from `git status`

## Context

This repository mounts two tooling repositories as submodules:
[refaqt-agents](https://github.com/refaqt/refaqt-agents) at [`.agents/`](../../.agents/)
and [doqs](https://github.com/refaqt/doqs) at [`doqs/`](../../doqs/). Both follow the
`main` branch of their own repository. The session hook and
[`setup-tooling.sh`](../../setup-tooling.sh) both end with:

```bash
git submodule update --remote -- doqs .agents
```

That call moves each folder to the newest commit on `main`. The commit this
repository records for each folder, called the pin, stays where it was. Git reports
the difference as a modified file:

```
 M .agents
 M doqs
```

The rule so far was written for a person: leave those two uncommitted unless you
mean to set a new pin. See
[the session hook decision](2026-09-16_cloud-session-submodule-hook.md).

Agents read that rule and still got it wrong, in almost every session. An agent
finishes a task, wants a clean working tree, sees the two modified entries, and
reports something like this:

> Only aqtuator's doqs gitlink is dirty — the one thing AGENTS.md says to leave
> uncommitted. I'll clear it without setting a new pin, by returning the submodule
> to its recorded commit.

The reasoning sounds careful and the result is wrong. Returning the folder to its
recorded commit throws away the update the session just downloaded. The rules,
skills and checking scripts go back to an older version, silently, at the end of
the work.

The wording was not the problem. The word "uncommitted" tells an agent not to
commit. It does not tell an agent not to revert, and reverting is the other way to
reach a clean tree.

## Decision

Stop showing the two folders as modified. [`.gitmodules`](../../.gitmodules) now sets
`ignore = all` on `doqs` and `.agents`.

```
[submodule "doqs"]
	path = doqs
	url = https://github.com/refaqt/doqs.git
	branch = main
	ignore = all
```

`git status` and `git diff` now skip both. A session that updates the tooling ends
with a clean working tree, so there is nothing left for anyone to tidy away.

`modules/stoq` keeps the normal setting. Machine modules are pinned to an exact
commit and a change there is real news.

## What still works

`ignore = all` only changes what `git status` and `git diff` print. It does not
change what git checks out.

- The session hook and `setup-tooling.sh` still fetch the newest `main`.
- Continuous integration still checks out the recorded pin. The workflow uses
  `submodules: recursive`, which never reads this setting.
- `git submodule status` still shows the true state, with a leading `+` on a folder
  that sits ahead of its pin.

## Setting a new pin on purpose

Git now refuses a plain `git add` on either folder and says what to do instead:

```
hint: Skipping submodule due to ignore=all: doqs
hint: Use --force if you really want to add the submodule.
```

So a deliberate pin bump is one extra word:

```bash
git add --force .agents doqs
```

This is the cost of the change, and it is the right way round. Freezing a new pin
is rare and deliberate. The modified entries appeared in nearly every session.

## Consequences

- A local edit inside `doqs/` or `.agents/` is also hidden. Neither folder is a
  place to edit anything. Changes to the shared kit belong in
  [refaqt-agents](https://github.com/refaqt/refaqt-agents), and changes to the
  layout, checks and templates belong in [doqs](https://github.com/refaqt/doqs).
- The pins will drift further behind `main` over time, because nothing now nudges
  anyone to bump them. Bump them together with any file that the current template
  wrote into this repository, which is what this change does for the session hook.
- The same trap exists in every repository that uses doqs. The fix here is local.
  Moving it into the doqs template is a separate piece of work.

## Related

- [A session hook checks out the tooling submodules](2026-09-16_cloud-session-submodule-hook.md)
- [Put back the tooling update to get a clean working tree](../mistakes/2026-09-22_reverted-the-tooling-update.md)
