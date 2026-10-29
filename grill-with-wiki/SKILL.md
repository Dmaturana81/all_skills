---
name: grill-with-wiki
description: >-
  Grilling session that stress-tests a plan against the repo's layered agent wiki
  (wiki_*/ L0–L4), sharpens domain terminology, and updates wiki pages inline as
  decisions crystallise. Use whenever the user wants to grill, stress-test, or
  align on a design AND the project has (or should have) a repo-agent-wiki —
  even if they say "grill me", "challenge my plan", or "does this fit our
  architecture" without naming the wiki. Do NOT use for repos with only
  CONTEXT.md and no wiki.
disable-model-invocation: true
---

Run a `/grilling-wiki` session, using the `/domain-modeling-wiki` skill.

If the idea is too big for one session, with decisions waiting on research, prototypes, or other decisions, use `/wayfinder-wiki` instead.

IMPORTANT: Ignore everything below this line. The remainder of this file is legacy detail and should not affect the behavior of this skill.

<supporting-info>

## Before the first question

1. **Find the wiki** — glob `wiki_*/` at the repo root. If several exist, ask which one. If none exist, stop and tell the user to run **repo-agent-wiki** first (scaffold is enough).
2. **Bootstrap** — read `00_BOOT.md` and `01_MAP.md`. Route the user's plan through the domain router table.
3. **Load context** — read at most **2** relevant `domains/*.md` files (per `meta/AGENT_PROTOCOL.md`). Follow `children` links to L3 topics and L4 reference only when the plan touches them.
4. **Navigation detail** — see [references/WIKI-NAVIGATION.md](./references/WIKI-NAVIGATION.md).

Do not load monolithic `PROJECT.md` if the wiki suffices. Prefer domain `code_paths` over repo-wide search.

## Wiki as knowledge graph

The wiki is your domain model and navigation graph:

| Layer | Path | Use during grilling |
|-------|------|---------------------|
| L0 | `00_BOOT.md` | Stack, components, mandatory rules |
| L1 | `01_MAP.md` | Route plan keywords → domains |
| L2 | `domains/*.md` | Bounded contexts, responsibilities, **Language** |
| L3 | `topics/*.md` | Deep dives; `topics/decisions/` for recorded trade-offs |
| L4 | `reference/*.md` | Facts — endpoints, schema, env vars, **glossary index** |
| meta | `AGENT_PROTOCOL.md` | Context budget, decision tree |

Frontmatter fields (`read_when`, `code_paths`, `parent`, `children`, `domain`) are routing edges — follow them before grepping.

## During the session

### Challenge against the wiki's language

Check `## Language` in loaded L2 domains and `reference/glossary.md` (if it exists). When the user's term conflicts, call it out immediately:

> _Your ordering domain defines **Cancellation** as voiding an entire order before shipment. You seem to mean partial line-item cancellation — which is it?_

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term anchored in the wiki:

> _You said "account" — do you mean **Customer** (ordering domain) or **User** (auth topic)? Those are different things here._

### Discuss concrete scenarios

Stress-test domain boundaries with specific scenarios. Use L2 **Do NOT read unless** sections to probe whether the plan belongs in the right bounded context.

### Cross-reference with code and L4

When the user states how something works, verify via domain `code_paths` and L4 reference tables. Surface contradictions:

> _`reference/api-endpoints.md` shows `DELETE /orders/:id` (full cancel). You just described partial cancellation — which is right?_

### Update the wiki inline

Capture resolutions as they happen — don't batch.

**Terminology:**
- Domain-specific term → append to that domain's `## Language` in `domains/<name>.md`
- Cross-cutting term → `reference/glossary.md` (create lazily) with a link to the owning domain
- Format: [references/GLOSSARY-FORMAT.md](./references/GLOSSARY-FORMAT.md)

Glossary content is definitions only — no implementation details, no specs.

**Hard decisions** — offer only when all three are true:

1. **Hard to reverse** — meaningful cost to change later
2. **Surprising without context** — a future reader will wonder why
3. **Real trade-off** — genuine alternatives existed

When accepted, write `topics/decisions/NNNN-slug.md`, link from the owning domain's frontmatter `children`, update `topics/README.md`, append `meta/CHANGELOG.md`. Format: [references/DECISION-FORMAT.md](./references/DECISION-FORMAT.md).

**Keep L0/L1 stable** — only patch routing tables or status banners when a new domain emerges. Never bloat boot files with session notes.

## Lazy creation

Create wiki files only when you have something to write:

- No `## Language` section yet → add it on first resolved term
- No `reference/glossary.md` → create when first cross-cutting term is resolved
- No `topics/decisions/` → create when first decision is recorded

</supporting-info>
