# Onboarding

How to set up, run, and navigate this repository.

## Prerequisites

- [List prerequisites.]

## Setup

1. Clone the repository (with submodules): `git clone --recurse-submodules …`
2. If `.agents/` is empty: `git submodule update --init --recursive`
3. [Install dependencies and configure the environment.]

## Where to read next

| Doc | Use |
| --- | --- |
| `docs/architecture.md` | Module map and data flow |
| `docs/patterns/SKILL.md` | Project-specific reusable patterns |
| `docs/decisions/` | Past technical decisions (ADRs) |
| `docs/mistakes/` | What went wrong and how to avoid it |
| `docs/log/` | Chronological activity log |
| `.agents/` | Shared agent rules and skills (refaqt-agents) |

## Cursor / Agent

Root `AGENTS.md` is the entry point. Shared rules/skills live in `.agents/`; Cursor adapters may live under `.cursor/rules/`. Prefer project guidance over duplicate User Rules in Settings.
