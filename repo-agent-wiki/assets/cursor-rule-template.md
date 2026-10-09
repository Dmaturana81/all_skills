---
status: draft — NOT installed in .cursor/rules
---

# Draft Cursor Rule — <PROJECT> Wiki Context

## Suggested: `.cursor/rules/<project>-wiki.mdc`

```markdown
---
description: <PROJECT> agent context — use <WIKI_DIR> layered docs before exploring the codebase
alwaysApply: true
---

# <PROJECT> Wiki Context Protocol

Primary context: `<WIKI_DIR>/`

## Mandatory read order

1. `<WIKI_DIR>/00_BOOT.md` — every session
2. `<WIKI_DIR>/01_MAP.md` — non-trivial tasks
3. `<WIKI_DIR>/domains/<domain>.md` — max 2 domains
4. `<WIKI_DIR>/topics/<topic>.md` — one narrow deep dive
5. `<WIKI_DIR>/reference/<file>.md` — lookups only

## Rules

- Do NOT load all domain files in one session.
- Prefer `<WIKI_DIR>/reference/` over grepping for config facts.
- Do NOT load PROJECT.md if wiki layers suffice.
- After significant changes: update `<WIKI_DIR>/meta/CHANGELOG.md` and affected pages.
- Before planning or building, check `<WIKI_DIR>/meta/INDEX.md` (if present) for work already in flight.
- Follow `<WIKI_DIR>/meta/AGENT_PROTOCOL.md`.

## Domain quick map

| Task area | Domain file |
|-----------|-------------|
| <!-- fill per repo --> | `domains/....md` |
```

## Installation (only when user asks)

1. Copy block to `.cursor/rules/<project>-wiki.mdc`
2. Optional one-liner in `PROJECT.md` → `<WIKI_DIR>/00_BOOT.md`
