---
name: wayfinder-wiki
description: >-
  Plan a huge, foggy chunk of work (more than one agent session can hold) as a
  map of decision tickets stored inside the repo's layered agent wiki (wiki_*/),
  and resolve them one per session until the way to the destination is clear.
  Every resolution lands in its canonical wiki home (domain Language, decisions,
  reference, research, prototypes) and every map and ticket stays indexed. Use
  instead of /wayfinder when the project has a wiki_*/ agent wiki.
disable-model-invocation: true
---

# Wayfinder (Wiki)

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. This skill charts that way as a **map** of **decision tickets** inside the repo's agent wiki, then works the tickets one at a time until the route is clear and someone can go and build it.

The wiki is the tracker. A map is a folder, a ticket is a file, and [scripts/wayfinding.py](scripts/wayfinding.py) supplies what a tracker would give natively: the frontier query, claiming, ids, generated indexes, and a consistency check. Everything a ticket decides is written into the wiki layer that owns it, so the wiki stays the current source of truth while the map is being worked, not only afterwards.

## Prerequisites

1. A wiki at `wiki_*/` (created by `/repo-agent-wiki`; a scaffold is enough). If several exist, ask which one. If none exist, stop and tell the user to run `/repo-agent-wiki` first.
2. Route through the wiki before anything else: `00_BOOT.md`, `01_MAP.md`, `meta/AGENT_PROTOCOL.md`, then `meta/INDEX.md`. Navigation and budgets: [references/WIKI-NAVIGATION.md](references/WIKI-NAVIGATION.md).

`<SKILL>` below means this skill's folder. Every script call is `python3 <SKILL>/scripts/wayfinding.py <command> ...`.

## Plan, don't do

Each ticket resolves a **decision**. The map is done when nothing is left to decide before someone goes and does the thing. The pull to just build it is the signal that you've reached the edge of the map and it's time to hand off. A map's **Notes** may override this and carry execution into the map; absent that, produce decisions, not deliverables.

## Refer by name

Every map and ticket has a **name**: its H1 title. In everything the human reads (narration, Decisions so far, resolutions), refer to it by name with the link inside the name: `[Refund timing](tickets/0002-refund-timing.md)`, never a bare `0002`. The generated indexes follow the same rule.

## Where everything lives

```
wiki_<name>/
├── 01_MAP.md                    # router row: planning in flight → meta/INDEX.md
└── meta/
    ├── INDEX.md                 # hub: links every planning index below
    ├── CHANGELOG.md             # one dated entry per session that changed the wiki
    ├── wayfinding/
    │   ├── INDEX.md             # GENERATED: every map, status, frontier size
    │   └── <effort>/
    │       ├── MAP.md           # the map: an index, never a store
    │       └── tickets/
    │           ├── README.md    # GENERATED: frontier + all tickets
    │           └── NNNN-<slug>.md
    ├── research/                # /research-wiki notes + INDEX.md
    ├── prototypes/              # /prototype-wiki verdicts + INDEX.md
    └── sdlc-artifacts/<effort>/ # /to-spec-wiki writes spec.md here at handoff
```

Create folders lazily. On the first map in a wiki, also create `meta/INDEX.md` (if missing), add a `01_MAP.md` router row ("Planning in flight, wayfinding, research, prototypes → `meta/INDEX.md`"), and add the planning step to `meta/AGENT_PROTOCOL.md`. Formats for the map, tickets, resolutions, and the hub: [references/MAP-FORMAT.md](references/MAP-FORMAT.md).

### One canonical home per fact

A decision lives in exactly one place. The ticket's `## Resolution` holds the answer to its question; anything else the session produced goes to the layer that owns it, and the resolution **links** there instead of restating it.

| The session produced… | Canonical home | Written by |
|---|---|---|
| The answer to the ticket's question | ticket `## Resolution` | this skill |
| A canonical term | `domains/<d>.md` `## Language`, or `reference/glossary.md` if cross-cutting | `/domain-modeling-wiki` |
| A hard trade-off (hard to reverse, surprising, real alternatives) | `topics/decisions/NNNN-slug.md` with `origin:` → the ticket | `/domain-modeling-wiki` |
| A verified fact about this system | the matching `reference/*.md` table | this skill, L4 rules (tables only) |
| A fact from outside the repo | `meta/research/<slug>.md`, cited | `/research-wiki` |
| A prototype verdict | `meta/prototypes/<slug>.md`; code on `prototype/<slug>` branch | `/prototype-wiki` |
| A new bounded context | new `domains/<d>.md` + `01_MAP.md` router row | `/repo-agent-wiki` update rules |
| One-line gist of the route walked | map `## Decisions so far` | this skill |

Never put secrets in the wiki. A task ticket records *where* credentials live, not their values.

## The map

`<effort>/MAP.md`, frontmatter `kind: wayfinder-map`. Body sections, in this order:

- **Destination**: what reaching the end looks like (a spec, a locked decision, a change made in place). One or two lines. Every session orients to it before choosing a ticket.
- **Notes**: domain, the L2 domains this effort touches, skills every session should consult, standing preferences.
- **Decisions so far**: the index. One line per closed ticket: linked name and a one-line gist.
- **Not yet specified**: in-scope fog you can't ticket yet.
- **Out of scope**: work ruled beyond the destination. Closed, never graduates.

The map is an **index, not a store**: it gists and links, never restates. Open tickets are **not** listed in it; they are found by the frontier query and the generated `tickets/README.md`.

Map `status` moves `charting` → `active` → `cleared` → `handed-off`. `cleared` requires no open tickets and no fog. `handed-off` requires a `handoff:` path to the spec.

**Single writer.** Only the session driving the map edits `MAP.md` and runs `index`. Subagents write their own ticket and evidence files and report back; the driving session folds their results into the map.

## Tickets

`<effort>/tickets/NNNN-<slug>.md`, frontmatter `kind: wayfinder-ticket`. The body is the question, sized to one ~100K-token agent session. The answer is not part of the question; it is added as `## Resolution` when the ticket closes.

| Field | Meaning |
|---|---|
| `type` | `research`, `prototype`, `grilling`, or `task`. The body never states the type; read this field. |
| `mode` | `AFK` (agent alone) or `HITL` (worked live with the human). Fixed by type, except `task`. |
| `status` | `open`, `closed`, or `out-of-scope` |
| `assignee` | The claim. Open and empty means unclaimed. |
| `blocked_by` | Ids of tickets that must be settled first |
| `domains` | L2 domains to load for this ticket (at most 2) |

A ticket is **unblocked** when every blocker is `closed` or `out-of-scope`. The **frontier** is the open, unblocked, unclaimed tickets, the edge of the known: `wayfinding.py frontier <effort_dir>`.

**Claim first.** Run `wayfinding.py claim <effort_dir> <id> <name>` before any other work, using the map's `owner` (or `git config user.name`). If the wiki is committed and shared, commit the claimed ticket file immediately so other sessions and devs see it. If the wiki is gitignored, claims are visible only within this checkout, so don't run parallel sessions from separate worktrees.

## Ticket types

Every ticket is **HITL** or **AFK**. A HITL ticket only resolves through a live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): a fact a decision waits on, found outside the working directory (docs, third-party APIs, knowledge bases). Resolved by a subagent running `/research-wiki`, which writes `meta/research/<slug>.md` and the ticket's resolution.
- **Prototype** (HITL): a cheap, rough artifact to react to when "how should it look or behave" is the question. Run `/prototype-wiki`: code on a `prototype/<slug>` branch, verdict in `meta/prototypes/<slug>.md`.
- **Grilling** (HITL): conversation, the default. Run `/grilling-wiki` in **ticket mode** together with `/domain-modeling-wiki`.
- **Task** (AFK or HITL): manual work that must happen before a decision can be made (sign up for a service, provision access, move data so its shape can be seen). The one type that *does* rather than decides; it earns its place by unblocking a decision. Do it yourself where you can (AFK); otherwise hand the human a precise checklist, or use `/wizard` for credential and dashboard steps (HITL). The resolution records what was done and the facts later tickets need.

## Fog of war

The map is deliberately incomplete: don't chart what you can't yet see. **Not yet specified** holds the dim view of what's coming: the suspected question, the area to revisit. Everything there is in scope, just not sharp enough to ticket.

**Fog or ticket?** Ask whether you can state the question precisely now, not whether you can answer it now.

- **Ticket** when the question is sharp, even if it is blocked.
- **Not yet specified** when you can't phrase it that sharply yet. Don't pre-slice fog into ticket-sized pieces; one patch may become several tickets, or none.

Resolving a ticket clears the fog ahead of it: graduate whatever is now specifiable into tickets and delete that patch from **Not yet specified**, so it lives only as its ticket.

## Out of scope

Fog only gathers toward the destination. Work beyond it is **out of scope**: not fog, never graduated, back only if the destination is redrawn, and then as a fresh map.

When an existing ticket turns out to sit past the destination, set `status: out-of-scope`, write a `## Resolution` saying why, and add one line to **Out of scope** linking it. It stays out of **Decisions so far**, which records the route actually walked.

## Invocation

Two modes. Either way, **never resolve more than one ticket per session**; research tickets resolved by subagents during charting are the only exception.

### Chart the map

User invokes with a loose idea.

1. **Route through the wiki.** Bootstrap per the prerequisites. Read `meta/wayfinding/INDEX.md`: if a map for this destination already exists, switch to working it instead of charting a duplicate.
2. **Name the destination.** Run `/grilling-wiki` in ticket mode with `/domain-modeling-wiki`, scoped to one question: what is this map finding its way to? The destination fixes the scope, so it is settled first. Challenge it against existing `## Language`, `topics/decisions/`, and L4 tables.
3. **Map the frontier, breadth-first.** Grill again, fanning out across the whole space rather than deep on any thread: the open decisions, the first steps takeable now, and which L2 domains each touches. **If this surfaces no fog** (the way is already clear and the whole journey fits one session), you don't need a map: stop and suggest `/grill-with-wiki` or `/to-spec-wiki` instead.
4. **Create the map**: `meta/wayfinding/<effort>/MAP.md`, `status: charting`, Destination and Notes filled, Decisions so far empty, fog sketched into **Not yet specified**. Create the `meta/INDEX.md` hub and router row if this is the wiki's first map.
5. **Create the tickets you can specify now** with `wayfinding.py new <effort_dir> --type <t> --title "<name>"`, then fill each `## Question` and `domains`. Wire `blocked_by` in a second pass, once every id exists.
6. **Fire the research subagents.** For each research ticket, launch a subagent with `/research-wiki`, the ticket path, and the instruction to claim it, write the note, write the resolution, and close it, but not to touch `MAP.md`. When they report back, add each to **Decisions so far** and graduate any fog they cleared.
7. **Close out**: set `status: active`, run `index`, append `meta/CHANGELOG.md`, run the checks (below). Stop. Charting resolves nothing by hand.

### Work through the map

User invokes with a map (name, effort slug, or path). A ticket is optional; without one, you pick the next decision, not the user.

1. **Load the low-res view**: `MAP.md` and `tickets/README.md`, not every ticket body. Run `wayfinding.py check`; if it reports drift (a closed ticket missing from **Decisions so far**, a stale index, a broken link), repair that first.
2. **Choose and claim.** Use the ticket the user named; otherwise take the first ticket in `wayfinding.py frontier`. **Claim it** before any work.
3. **Load only what the ticket needs**: its `domains` (at most 2), and the linked tickets, decisions, research, or prototypes it depends on. Zoom into closed tickets on demand. Consult any skills the map's Notes name.
4. **Resolve it as its `type`** (see Ticket types). If unsure, use `/grilling-wiki` in ticket mode with `/domain-modeling-wiki`.
5. **Write to the wiki as things crystallize**, using the canonical-home table: terms and decisions via `/domain-modeling-wiki`, facts into L4, evidence into `meta/research/` or `meta/prototypes/`.
6. **Record the resolution**: add `## Resolution` (the answer, plus a `Wiki updates` list linking every page this session touched), set `status: closed`, and add one line to **Decisions so far**.
7. **Advance the frontier**: create newly surfaced tickets (create, then wire); graduate fog the answer made specifiable; rule beyond-the-destination tickets out of scope; update or delete tickets the decision invalidated (say so in the resolution).
8. **Close out**: run `index`, append one `meta/CHANGELOG.md` entry for the session, run the checks. If no open tickets and no fog remain, set `status: cleared` and tell the user to run `/to-spec-wiki` on this map.

The user may run unblocked tickets in parallel sessions, so expect other sessions to be editing ticket files concurrently. Re-read a ticket before editing it.

## Checks before finishing any session

```bash
python3 <SKILL>/scripts/wayfinding.py index wiki_<name>/
python3 <SKILL>/scripts/wayfinding.py check wiki_<name>/
python3 <repo-agent-wiki>/scripts/validate_wiki.py wiki_<name>/
```

Both must pass. `check` verifies the map sections, that **Decisions so far** and **Out of scope** match ticket statuses, that no open ticket is listed in the map, the ticket fields and blocking graph (no unknown blockers or cycles), that every relative link resolves, and that the generated indexes are current. `validate_wiki.py` verifies the wiki as a whole, including that every planning file is reachable from `meta/INDEX.md`.

## Handoff

When the map is `cleared`, it hands off; it doesn't build. `/to-spec-wiki` collapses the map's linked decisions into `meta/sdlc-artifacts/<effort>/spec.md`, sets the map to `handed-off`, and the main flow continues with `/implement-wiki`. Go straight to `/implement-wiki` only when the effort turned out to be genuinely small.
