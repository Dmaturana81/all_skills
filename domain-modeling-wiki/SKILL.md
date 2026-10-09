---
name: domain-modeling-wiki
description: Actively build and sharpen a project's agent wiki language (wiki_*/ L2 `## Language`), plus glossary index and decision records, as you clarify a design during grilling.
---

# Domain Modeling (Wiki)

Actively build and sharpen the project's **ubiquitous language** inside the repo's layered agent wiki.

This is the wiki equivalent of `domain-modeling`: it updates terminology and records hard trade-offs **as they crystallize**, instead of letting session history drift.

## File targets (assumes `wiki_*/` exists)

- L2 domain language: `wiki_<name>/domains/<domain>.md` (`## Language`)
- Cross-cutting glossary index (L4): `wiki_<name>/reference/glossary.md`
- Hard decision records (L3): `wiki_<name>/topics/decisions/NNNN-slug.md`

## During the session

### Challenge against the wiki's glossary/language

When the user uses a term that conflicts with the existing language in the wiki:

1. Call out the conflict immediately.
2. Ask the user which meaning they intend.
3. Only update the wiki once you have a shared resolution.

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term anchored in the wiki language:

- If a single bounded context owns the term, use that domain's canonical meaning.
- If it spans multiple bounded contexts, route it through `reference/glossary.md`.

### Discuss concrete scenarios (boundary testing)

Stress-test bounded-context boundaries with specific scenarios. If the wiki's L2 domain file includes a "Do NOT read unless" guard, use it to validate whether the plan belongs in that bounded context.

### Cross-reference with code and L4 tables

When the user states how something works, verify against:

- The relevant domain's `code_paths` guidance
- The L4 reference tables (`reference/*.md`)

If you find contradictions, surface them as questions before recording terminology or decisions.

## Update the wiki inline

Capture resolutions as they happen — don't batch.

### Terminology

Follow this mapping:

- Domain-specific term
  - Update: `domains/<name>.md` -> append/extend the `## Language` section
- Cross-cutting term
  - Update: `reference/glossary.md` (create lazily when first needed)

Use: [references/GLOSSARY-FORMAT.md](./references/GLOSSARY-FORMAT.md)

Rules:

- Glossary content is **definitions only** — no implementation details, no specs.
- Keep changes minimal: add the smallest definition that disambiguates the term.

### Hard decisions (wiki trade-offs)

Offer a decision record only when all three are true:

1. **Hard to reverse** — meaningful cost to change later
2. **Surprising without context** — a future reader will wonder why
3. **Real trade-off** — genuine alternatives existed

When accepted:

1. Write `topics/decisions/NNNN-slug.md`
2. Link from the owning domain's frontmatter `children`
3. Update `topics/README.md` with status `filled`
4. Append `meta/CHANGELOG.md`

Use: [references/DECISION-FORMAT.md](./references/DECISION-FORMAT.md)

### When the session is a wayfinder ticket

Called from `/wayfinder-wiki`, the ticket's `## Resolution` is the answer; the wiki pages you write are where its terms and trade-offs live. Keep them linked both ways:

- A decision record born from a ticket gets `origin:` in its frontmatter: the wiki-root-relative path to the ticket (`meta/wayfinding/<effort>/tickets/NNNN-slug.md`).
- If it overrides an earlier record, set `supersedes:` on the new one and `superseded_by:` on the old one (status `superseded` if fully replaced, `amended` if only part of it), and say which part in one line.
- Report every page you changed, so the ticket's `### Wiki updates` list is complete.

### Keep the layers "pure"

- Never add session prose to L0 (boot) or L4 (reference tables).
- L4 stays lookup-only (tables/links); keep narrative in decision records, stage artifacts managed by `grilling-wiki`, or wayfinder ticket resolutions managed by `wayfinder-wiki`.

## Lazy creation rules

Create wiki files only when you have something to write:

- Missing L2 `## Language` section -> add on first resolved domain-specific term
- Missing `reference/glossary.md` -> create on first cross-cutting term
- Missing `topics/decisions/` -> create on first accepted hard decision

