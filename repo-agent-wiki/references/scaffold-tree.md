# Scaffold Templates

Replace `<WIKI>`, `<PROJECT>`, `<STACK>`, `<DOMAIN>` placeholders.

## `README.md`

```markdown
# <WIKI>

Layered context wiki for coding agents.

| File | Layer | When |
|------|-------|------|
| [00_BOOT.md](00_BOOT.md) | L0 | Every session |
| [01_MAP.md](01_MAP.md) | L1 | Non-trivial tasks |
| [domains/](domains/) | L2 | 1–2 per task |
| [topics/](topics/) | L3 | Narrow deep dives |
| [reference/](reference/) | L4 | Lookups only |

**Status:** Scaffold | Fill phase N
```

## `00_BOOT.md` skeleton

```markdown
---
layer: L0
scope: agent entry point
tokens: ~200
read_when: always
children:
  - 01_MAP.md
  - meta/AGENT_PROTOCOL.md
---

# <PROJECT> — Agent Boot

**Stack:** <STACK>

## What this system does
<2–3 sentences>

## Components
| Component | Role |
|-----------|------|

## Agent rules (mandatory)
1. Read this file, then `01_MAP.md`, then only relevant domain(s).
2. Do not load monolithic PROJECT.md if wiki suffices.
3. Use `reference/` for facts; `topics/` for deep dives.
4. Follow `meta/AGENT_PROTOCOL.md`.

## Code layout
<minimal tree>

## Status
> Scaffold | Fill complete
```

## `01_MAP.md` router table

```markdown
| If your task involves… | Read |
|------------------------|------|
| … | [domains/<x>.md](domains/<x>.md) |
```

## L2 domain skeleton

```markdown
---
layer: L2
domain: <DOMAIN>
scope: <one line>
read_when: ["kw1", "kw2"]
code_paths: []
parent: 01_MAP.md
children: []
topics: []
---

# Domain: <Title>

## Service / module
| Property | Value |

## Responsibilities
- [ ] …

## Key paths
| Area | Path |

## Related
- [reference/…](../reference/…)

## Do NOT read unless
<when to use another domain>
```

## L3 topic stub

```markdown
---
layer: L3
domain: <DOMAIN>
scope: <narrow concern>
read_when: []
parent: domains/<DOMAIN>.md
status: stub
migrate_from: []
---

# Topic: <Title>

> Stub — migrate from …

## Outline (to fill)
- [ ] …

## Code entry points
- …
```

## `meta/AGENT_PROTOCOL.md` sections

1. Navigation order (numbered list L0→L4)
2. Context budget table
3. Decision tree (domain keywords → files)
4. Code exploration rules
5. Wiki maintenance rules
6. Planning in flight: "Before planning or building, read `meta/INDEX.md` (if present) for active wayfinding maps and SDLC artifacts; reuse an effort's slug rather than starting a parallel one."

## `meta/INDEX.md` hub (create lazily)

Only when the first planning folder appears. Link only the folder indexes that exist.

```markdown
---
layer: meta
scope: hub for planning and evidence artifacts
read_when: [planning, roadmap, wayfinding, research, prototype, spec, in flight]
parent: ../01_MAP.md
---

# Planning & evidence index

| Index | What it lists |
|---|---|
| [wayfinding/INDEX.md](wayfinding/INDEX.md) | Maps of decision tickets for foggy efforts |
| [sdlc-artifacts/INDEX.md](sdlc-artifacts/INDEX.md) | Stage artifacts and specs per effort |
| [research/INDEX.md](research/INDEX.md) | Cited research notes |
| [prototypes/INDEX.md](prototypes/INDEX.md) | Prototype verdicts and their branches |
```

Add to `01_MAP.md`:

```markdown
| Planning in flight, wayfinding, research, prototypes | [meta/INDEX.md](meta/INDEX.md) |
```

## `meta/CHANGELOG.md` format

```markdown
### YYYY-MM-DD — Title
- What changed
- Domains: a | b
- Paths: …
```
