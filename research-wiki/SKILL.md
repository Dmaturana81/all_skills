---
name: research-wiki
description: >-
  Investigate a question against high-trust primary sources and capture the
  cited findings inside the repo's layered agent wiki (wiki_*/meta/research/),
  indexed and linked to the decision or wayfinder ticket waiting on them. Use
  when the user wants something researched, docs or API facts gathered, or a
  wayfinder-wiki research ticket resolved, and the project has a wiki_*/.
---

# Research (Wiki)

Spin up a **background agent** to do the research, so you keep working while it reads. Same discipline as `/research`; the difference is where the findings land and how they stay findable.

## Its job

1. **Route first.** Read `00_BOOT.md`, `01_MAP.md`, and `meta/research/INDEX.md` if it exists. If a note already answers the question, extend it instead of writing a second one.
2. **Investigate primary sources**: official docs, source code, specs, first-party APIs, not a secondary write-up of them. Follow every claim back to the source that owns it. Record the version or date of what you read; facts about third-party systems go stale.
3. **Write one note** at `wiki_<name>/meta/research/<slug>.md` (format below), citing each claim's source.
4. **Index it**: add a row to `meta/research/INDEX.md` (create it lazily, and link it from `meta/INDEX.md`).
5. **Promote durable facts.** A fact about *this* system that later work will look up (an env var, a rate limit, an endpoint contract) also becomes a row in the matching `reference/*.md` table, with the note as its `source:`. The note stays the evidence; the L4 row is the lookup.
6. **Append `meta/CHANGELOG.md`.**

## When resolving a wayfinder ticket

The ticket path is given to you. Claim it first (`wayfinding.py claim`), then after writing the note:

- add `## Resolution` to the ticket: the answer in a few sentences, plus a `### Wiki updates` list linking the note and any promoted L4 rows;
- set the ticket's `status: closed`;
- **do not edit `MAP.md` or run `index`**; the session driving the map does that. Report the ticket name, the one-line gist, and any new questions the research exposed, so it can graduate fog.

Research is AFK: surface facts, never make the decision the ticket is waiting on. If the facts point at a choice, say so in the resolution as "the decision this unblocks".

## Note format

```markdown
---
layer: meta
kind: research-note
scope: <one line: the question answered>
read_when: [<keywords>]
parent: INDEX.md
effort: <wayfinding effort slug, if any>
ticket: <relative path to the wayfinder ticket, if any>
sources_checked: 2026-10-09
---

# <Question as a name>

## Answer

<2–5 sentences. What a decision-maker needs to know.>

## Findings

- <claim> ([source](https://...))
- <claim> ([source](https://...))

## Open questions

- <what the sources did not settle>
```

## `meta/research/INDEX.md`

```markdown
---
layer: meta
scope: index of cited research notes
read_when: [research, sources, findings, third-party, api docs]
parent: ../INDEX.md
---

# Research notes

| Note | Answers | Checked | Used by |
|---|---|---|---|
| [Fulfillment allocation](fulfillment-allocation.md) | Can stock be reserved per line? | 2026-10-09 | [Allocation granularity](../wayfinding/partial-cancellation/tickets/0002-allocation-granularity.md) |
```

If no wiki exists, fall back to `/research`.
