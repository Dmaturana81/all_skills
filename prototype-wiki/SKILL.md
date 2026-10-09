---
name: prototype-wiki
description: >-
  Build a throwaway prototype to answer one design question, then record the
  question, verdict, and branch in the repo's layered agent wiki
  (wiki_*/meta/prototypes/) so the answer stays findable after the code is
  gone. Use when a state model, business logic, or UI must be seen to be
  decided, including wayfinder-wiki prototype tickets, and the project has a wiki_*/.
---

# Prototype (Wiki)

A prototype is **throwaway code that answers a question**. Build it exactly as `/prototype` says: pick the branch (logic or UI) from the question, keep it trivial to run, no persistence, no polish, surface the state. Read `/prototype` and its `LOGIC.md` or `UI.md` for how.

This skill adds what happens around the code, so the answer outlives it.

## Before building

1. Read `00_BOOT.md`, `01_MAP.md`, and the domain the question belongs to (at most 2). Name things with that domain's `## Language`.
2. Check `meta/prototypes/INDEX.md`: if this question was already prototyped, start from that verdict.
3. If this is a wayfinder ticket, claim it first (`wayfinding.py claim`).

## Where things go

| Thing | Home |
|---|---|
| Prototype code | A `prototype/<slug>` branch, out of main, never merged |
| Question, verdict, how to run it | `wiki_<name>/meta/prototypes/<slug>.md` |
| A validated term | `/domain-modeling-wiki` → L2 `## Language` |
| A validated hard trade-off | `/domain-modeling-wiki` → `topics/decisions/` |
| The decision itself, for a wayfinder ticket | The ticket's `## Resolution`, linking the record above |

Prototype code never goes in the wiki. The wiki holds the verdict and a pointer to the branch. If a snippet encodes the decision better than prose (a state machine, a type shape), quote just that part in the record.

## The session is HITL

The human reacts to the prototype; you don't stand in for them. Show it, let them drive it, and write down what they decided in their words. If they're unavailable, stop with the prototype running and the record marked `verdict: pending`.

## Record format

```markdown
---
layer: meta
kind: prototype-record
scope: <one line: the question>
read_when: [<keywords>]
parent: INDEX.md
branch: prototype/<slug>
verdict: accepted | rejected | pending
effort: <wayfinding effort slug, if any>
ticket: <relative path to the wayfinder ticket, if any>
---

# <Question as a name>

## Question

## How to run

`git checkout prototype/<slug> && <one command>`

## Verdict

<what the human decided and why, in their words>

## Decision-rich snippet

<optional: only the part that encodes the decision>
```

## After the verdict

1. Add a row to `meta/prototypes/INDEX.md` (create it lazily, link it from `meta/INDEX.md`): name, question, verdict, branch, used by.
2. Commit the prototype to its branch and push it. Open no pull request.
3. For a wayfinder ticket: write `## Resolution` with a `### Wiki updates` list, set `status: closed`. If you are not the session driving the map, don't edit `MAP.md`.
4. Append `meta/CHANGELOG.md`.

If no wiki exists, fall back to `/prototype`.
