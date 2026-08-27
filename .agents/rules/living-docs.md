# Living documentation

Per-entry files — not single accumulating documents.

| Location | Purpose | Update trigger |
| --- | --- | --- |
| `docs/log/YYYY-MM-DD_topic.md` | What was done (any role), chronologically | A working session worth recording |
| `docs/decisions/YYYY-MM-DD_topic.md` | ADRs | A non-trivial technical choice |
| `docs/mistakes/YYYY-MM-DD_topic.md` | Errors and prevention rules | After a mistake or failed approach |
| `.agents-local/skills/patterns/SKILL.md` | Reusable project-specific coding patterns | A pattern proves out or changes |

Templates live in this kit under `bootstrap/docs/` and, when present, in a doqs (or similar) submodule. Each folder has a `README.md` index — **update it when adding a file**, or the entry becomes invisible.

`docs/architecture.md` is a short overview. Component detail belongs next to its code, in that module's `README.md`.
