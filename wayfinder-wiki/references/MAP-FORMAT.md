# Map, Ticket, and Index Formats

All files use the wiki's frontmatter subset: `key: value`, `key: [a, b]`, or `key:` followed by `- item` lines. `wayfinding.py` parses exactly this subset.

## Relative links

Links are relative to the file they appear in. `wayfinding.py check` fails on any that don't resolve.

| From | To wiki root | To `meta/research/` | To `topics/decisions/` |
|---|---|---|---|
| `meta/wayfinding/<effort>/MAP.md` | `../../../` | `../../research/` | `../../../topics/decisions/` |
| `meta/wayfinding/<effort>/tickets/*.md` | `../../../../` | `../../../research/` | `../../../../topics/decisions/` |

## `meta/wayfinding/<effort>/MAP.md`

The effort slug is the folder name: short, kebab-case, stable (`partial-cancellation`).

```markdown
---
layer: meta
kind: wayfinder-map
effort: partial-cancellation
status: charting            # charting | active | cleared | handed-off
owner: matu                 # who claims tickets on this map
domains: [ordering, fulfillment]
read_when: [partial cancel, line item, refund]
parent: ../INDEX.md
handoff:                    # set by /to-spec-wiki, e.g. ../../sdlc-artifacts/partial-cancellation/spec.md
---

# Partial line-item cancellation

## Destination

A spec for letting a customer cancel one line item before it ships, ready for /to-spec-wiki.

## Notes

- Domains: [ordering](../../../domains/ordering.md), [fulfillment](../../../domains/fulfillment.md)
- Constraint: [Full-order cancellation only](../../../topics/decisions/0001-full-order-cancellation-only.md) must be revisited, not ignored
- Every grilling ticket: /grilling-wiki ticket mode + /domain-modeling-wiki

## Decisions so far

<!-- one line per closed ticket: linked name, then the gist. Never restate the detail. -->

- [What a line-item cancellation is](tickets/0001-what-a-line-item-cancellation-is.md): voids one Order Line before it is allocated; see **Line Cancellation** in ordering Language

## Not yet specified

<!-- in-scope fog you can't phrase as a sharp question yet -->

- How refunds interact once billing has invoiced part of an order

## Out of scope

<!-- one line each: gist, why, link to the out-of-scope ticket -->

- [Storefront cancel UI](tickets/0004-storefront-cancel-ui.md): the destination is a backend spec; UI is a later effort
```

## `meta/wayfinding/<effort>/tickets/NNNN-<slug>.md`

Create with `wayfinding.py new`, which assigns the id and writes this skeleton. The H1 is the ticket's name.

```markdown
---
layer: meta
kind: wayfinder-ticket
effort: partial-cancellation
id: "0002"
type: grilling              # research | prototype | grilling | task
mode: HITL                  # research=AFK, prototype/grilling=HITL, task=either
status: open                # open | closed | out-of-scope
assignee:                   # the claim; written by `wayfinding.py claim`
blocked_by: ["0001"]
domains: [ordering]         # at most 2; what to load for this ticket
read_when: [allocation, line item]
parent: ../MAP.md
---

# Allocation granularity for partial cancellation

## Question

Fulfillment allocates inventory per order. Must partial cancellation wait for line-level allocation, or can it release order-level stock proportionally?
```

### On resolution

Append below the question, then set `status: closed` (or `out-of-scope`).

```markdown
## Resolution

Line-level allocation is a prerequisite. Partial cancellation releases exactly the cancelled line's stock, so it needs per-line reservations. Resolved 2026-10-09 with matu.

### Wiki updates

- [Line-level allocation before partial cancel](../../../../topics/decisions/0002-line-level-allocation.md) (new decision, supersedes part of 0001)
- [fulfillment Language](../../../../domains/fulfillment.md): **Line Reservation**
- [Fulfillment allocation research](../../../research/fulfillment-allocation.md)

### Invalidated

- None
```

Keep the resolution to the answer and the links. The detail lives in the pages it links.

## Generated files: do not edit by hand

`wayfinding.py index <wiki>` rewrites these from the maps and tickets:

- `meta/wayfinding/INDEX.md`: one row per map, with status, destination gist, frontier size, open and settled counts.
- `meta/wayfinding/<effort>/tickets/README.md`: the frontier, then every ticket with type, mode, status, claim, and blockers, all by name.

`check` fails when either is stale, so run `index` after any ticket or map edit.

## `meta/INDEX.md` (hub)

Hand-maintained, rarely changes. Create it lazily on the first planning artifact of any kind, and link only the sub-indexes that exist.

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
| [sdlc-artifacts/INDEX.md](sdlc-artifacts/INDEX.md) | Intent, spec, plan, test, deploy, maintain artifacts per effort |
| [research/INDEX.md](research/INDEX.md) | Cited research notes |
| [prototypes/INDEX.md](prototypes/INDEX.md) | Prototype verdicts and their branches |
```

## `meta/CHANGELOG.md` entry

One entry per session that changed the wiki:

```markdown
### 2026-10-09 — Wayfinding: resolve "Allocation granularity for partial cancellation"
- Map: [Partial line-item cancellation](wayfinding/partial-cancellation/MAP.md)
- Added topics/decisions/0002-line-level-allocation.md; fulfillment Language: Line Reservation
- New tickets: Reservation release timing
- Domains: ordering | fulfillment
```
