---
name: log
description: Add or edit an entry in the business activity log (docs/log/). Use whenever the user wants to record what they did, note an outreach attempt, log a research pass, write up a call or meeting, or capture a decision — for any of business-dev, marketing, sales, finance, or purchasing. Triggers on "log this", "add a log entry", "note that", "record today's work".
---

# Adding an activity log entry

The log is the chronological record of business-side work on AQTUATOR, across all roles. It is one
flat directory — there is no per-role subfolder, because work often blurs across roles (a pricing
pass touches both `finance` and `sales`; a competitor writeup feeds `marketing`). Instead, every
entry is labeled with the role(s) it belongs to right under the heading.

## File

```
docs/log/YYYY-MM-DD_topic-slug.md
```

- `YYYY-MM-DD` — the date the work happened, not necessarily today. Resolve relative dates ("yesterday",
  "on Tuesday").
- `topic-slug` — kebab-case, naming what the entry is *about*. Look at
  [`docs/log/README.md`](../../../docs/log/README.md) for the established style.
- If an entry for that date already exists and the new content belongs with it, **append to it**
  rather than creating a second file. Two entries for one date need distinct slugs.

## Content

Start with the H1, then a role label line, then the entry:

```markdown
# YYYY-MM-DD — Topic Title

**Role(s):** business-dev

## What happened

## Decisions

## Open Questions

## Next Steps
```

**Role(s)** is mandatory on every entry. List every role the work touches — a single role most of
the time, more than one when the work is genuinely blurry (e.g. `business-dev, finance` for a
partnership term sheet with pricing implications, or `purchasing, finance` for a sourced BOM
that feeds a cost model). Use the slugs from `.claude/agents/`:
`business-dev`, `marketing`, `sales`, `finance`, `purchasing`.

**Use the sections that carry content; drop the empty ones.** A short entry that's three bullets
under `## What happened` is perfectly normal — do not pad an entry to fill the template.

## Supporting files vs. deliverables

`docs/log/` is narrative only. A file belongs alongside the entry in `docs/log/` only if it's
genuinely scoped to that one entry and has no life beyond it — e.g. a quick one-off note backing
up a single claim made in the entry.

Anything meant to be read, cited, or built on again later independent of the log entry — a
dataset, a competitor landscape doc, a pricing model, a pitch draft — is a **deliverable**, not a
supporting file. Deliverables belong in `docs/<role>/YYYY-MM-DD_topic.*` instead (`docs/business-dev/`,
`docs/marketing/`, `docs/sales/`, `docs/finance/`, `docs/purchasing/` — each role's subagent already
saves its own work there). Reference the deliverable from the log entry with a relative link rather
than embedding or duplicating it in `docs/log/`, and add a row to that role folder's own `README.md`
alongside the `docs/log/README.md` row.

## Finish

1. Update the table in [`docs/log/README.md`](../../../docs/log/README.md) — add a row with the
   date, linked topic, and role(s). Keep it in date order.
2. Commit as `docs(log): <short description>`.
3. Push per the repo's normal branch/PR flow.

Confirm what you wrote and where, and give the user the path.
