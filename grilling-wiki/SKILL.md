---
name: grilling-wiki
description: >-
  An SDLC-style grilling session that stress-tests the user's plan against the
  repo's layered agent wiki (wiki_*/ L0–L4), while capturing every stage's
  committed artifact (intent/spec/plan/test/deploy/maintain) per effort inside
  the wiki and keeping an index of them. Also runs in ticket mode, scoped to
  one question, for /wayfinder-wiki.
---

# Grilling (Wiki + AI-native SDLC artifacts)

This skill combines two ideas:

1. The relentless, round-based grilling interview (/grilling)
2. The Anthropic AI-native SDLC "committed artifact" chain (intent → spec → plan → test → deploy → maintain)

The key rule: every artifact you create/patch lives inside the wiki repo, and it is indexed so future sessions can pick it up as the next stage's input.

## Prerequisites

1. The repo has a wiki at `wiki_*/` (created by `repo-agent-wiki`).
2. Read-only routing must work: we load only what we need using the wiki navigation protocol.

## Before the first question (wiki bootstrap)

1. **Find the wiki** — glob `wiki_*/` at the repo root.
2. **Route through the wiki**:
   - Read `wiki_*/00_BOOT.md` and `wiki_*/01_MAP.md`
   - Read `wiki_*/meta/AGENT_PROTOCOL.md`
   - Use: [references/WIKI-NAVIGATION.md](./references/WIKI-NAVIGATION.md)

If no wiki exists, stop and tell the user to run `repo-agent-wiki` first (scaffold is enough).

3. **Check what's already in flight**: read `wiki_*/meta/INDEX.md` if it exists. If a wayfinding map or SDLC artifacts already cover this plan, build on them instead of starting over.

## Two modes

| Mode | When | Scope | Output |
|---|---|---|---|
| **SDLC mode** (default) | The user wants to grill a plan they can hold in one session | All six stages below | `meta/sdlc-artifacts/<effort>/*.md` |
| **Ticket mode** | Invoked by `/wayfinder-wiki` for a grilling ticket, to name a destination, or for a breadth-first charting pass | Only the question you were given | The ticket's `## Resolution` (written by `/wayfinder-wiki`); no stage artifacts |

### Ticket mode rules

- The design tree is rooted at the ticket's `## Question`. Grill until that question is answered, not until the whole effort is.
- A sharp question that falls outside this ticket is a **candidate ticket**. Note it and report it at the end; don't chase it. A question you can't phrase sharply yet is **candidate fog**. A question beyond the map's destination is **candidate out of scope**.
- In a **breadth-first** charting pass, fan out across the whole space one level deep: surface the open decisions and their dependencies, and settle none of them.
- Terms and hard decisions are still written inline via `/domain-modeling-wiki`.
- Stop when the ticket's question is answered and the user confirms it. Hand back the answer, the candidates, and the list of wiki pages you changed.

## Session structure (Stage artifacts, SDLC mode)

Treat the grilling conversation as a stage-by-stage SDLC artifact capture. Ask questions, wait for answers, then write/patch the next artifact. Do not silently assume values.

All stage artifacts for one effort live under:

`wiki_<name>/meta/sdlc-artifacts/<effort>/`

`<effort>` is a short kebab-case slug, agreed with the user in Stage 1. If the work came from a wayfinding map, reuse the map's effort slug, so the map, its spec, and its plan share one name. Legacy wikis with artifacts directly in `meta/sdlc-artifacts/` keep working; treat that folder as one unnamed effort and don't move files unless asked.

Create the directories and the index lazily, but always keep the index up to date.

Index path:

`wiki_<name>/meta/sdlc-artifacts/INDEX.md`

When you add or update an artifact, also update `INDEX.md` to link it and summarize what changed. One section per effort:

```markdown
## <Effort name> (`<effort>`)

Map: [<map name>](../wayfinding/<effort>/MAP.md)  <!-- only if one exists -->

| Stage | Artifact | Status | Last change |
|---|---|---|---|
| Plan | [intent.md](<effort>/intent.md) | resolved | 2026-10-09: success criteria added |
```

The first time `INDEX.md` is created, link it from `meta/INDEX.md` (create the hub if it doesn't exist; see `/wayfinder-wiki` MAP-FORMAT for its shape).

### Association rules (indexing)

Each stage artifact must include:
- `## Related wiki decisions`: bullet links to any `wiki_*/topics/decisions/NNNN-slug.md` files that are relevant to the decisions in that stage
- `## Canonical terminology`: bullet links to owning `wiki_*/domains/<name>.md` sections (and `reference/glossary.md` rows for cross-cutting terms, if applicable)

This is how artifacts stay "associated" and remain findable in later sessions.

### Stage 1 — Plan: capture `intent.md`

Artifact:

`wiki_<name>/meta/sdlc-artifacts/<effort>/intent.md`

Ask the user for:
- Effort name and slug (the folder these artifacts live in)
- Problem (what hurts)
- Proposed outcome
- Affected users and systems
- Constraints (especially non-negotiables)
- Open questions
- Success criteria / leading indicator you can measure

After resolution, write or patch `intent.md`, then add a link + short summary to `INDEX.md`.

### Stage 2 — Design: capture `spec.md`

Artifact:

`wiki_<name>/meta/sdlc-artifacts/<effort>/spec.md`

Ask the user for:
- Requirements (functional + non-functional)
- Proposed design at the right level (bounded contexts, key interfaces, data flow)
- How decisions will be recorded (links to L3 decisions when relevant)
- Areas of concern and any remaining open questions from intent

While designing, whenever terminology/disambiguation or decisions are needed, follow:
- `/domain-modeling-wiki` (update wiki language, glossary, and decision records)

After resolution, write or patch `spec.md`, then update `INDEX.md`.

### Stage 3 — Build: capture `plan.md`

Artifact:

`wiki_<name>/meta/sdlc-artifacts/<effort>/plan.md`

Ask the user for:
- Files that change (or modules if unknown yet)
- Order of work
- Proof / verification plan (tests, screenshots, commands)
- Risks and why they matter

After resolution, write or patch `plan.md`, then update `INDEX.md`.

### Stage 4 — Test: capture `test.md`

Artifact:

`wiki_<name>/meta/sdlc-artifacts/<effort>/test.md`

Ask the user for:
- What "green" means (commands / checks / acceptance criteria)
- How to reproduce failures / edge cases
- What you will not change during a fix (e.g. tests)

After resolution, write or patch `test.md`, then update `INDEX.md`.

### Stage 5 — Deploy: capture `deploy.md`

Artifact:

`wiki_<name>/meta/sdlc-artifacts/<effort>/deploy.md`

Ask the user for:
- Approval gates (what human decision points exist)
- Rollback strategy
- What must be reviewed before any production action

After resolution, write or patch `deploy.md`, then update `INDEX.md`.

### Stage 6 — Maintain: capture `maintain.md`

Artifact:

`wiki_<name>/meta/sdlc-artifacts/<effort>/maintain.md`

Ask the user for:
- Monitoring/alerts to detect drift or failures
- The loop: what happens when a control band is breached
- What new evals/tests should be added after the first incident

After resolution, write or patch `maintain.md`, then update `INDEX.md`.

## Relentless grilling rules (round-based)

In both modes, use the /grilling discipline:

- Build a "design tree" of open decisions.
- Ask the whole current frontier (all questions whose prerequisites are settled) in one round.
- Number questions and provide your recommended answer.
- Wait for feedback before expanding the frontier.

## Terminology + decisions while grilling

Do NOT try to implement all wiki updates inline. Instead:

- When you need to add/adjust a canonical term or glossary entry, apply `/domain-modeling-wiki`.
- When you need a trade-off record, apply `/domain-modeling-wiki`'s "Hard decisions" rules.

## Too big for one session?

If, during SDLC mode, the design tree keeps growing faster than it closes, or decisions wait on research, prototypes, or work only the user can do, say so and suggest `/wayfinder-wiki`. Anything already captured in `intent.md` becomes the map's Destination and Notes; don't throw it away.

## Stop condition

The session is done only when:

- **SDLC mode**: every stage artifact (intent/spec/plan/test/deploy/maintain) has a resolved draft (no remaining open questions), OR
- **Ticket mode**: the ticket's question is answered and the user confirms it, OR
- The user explicitly asks to stop early.

Before finishing, append one `meta/CHANGELOG.md` entry for the session and run `repo-agent-wiki`'s `scripts/validate_wiki.py` on the wiki.

