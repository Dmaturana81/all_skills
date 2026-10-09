# Decision Format (Wiki)

Recorded trade-offs live in `topics/decisions/` — the wiki equivalent of ADRs.

Create the directory lazily when the first decision is accepted.

## Path and numbering

```
wiki_<name>/topics/decisions/0001-event-sourced-orders.md
wiki_<name>/topics/decisions/0002-postgres-write-model.md
```

Scan existing files for the highest number and increment.

## Template

```md
---
layer: L3
domain: ordering
scope: event-sourced write model for orders
read_when: [event-sourcing, orders, write-model, cqrs]
parent: domains/ordering.md
status: accepted
---

# Event-sourced orders

We store order state as an append-only event stream and project read models asynchronously. Chose this over mutable row updates because audit requirements need a complete history and we expect frequent state transitions per order.

## Considered options

- **Mutable Postgres rows** — simpler queries, but no built-in audit trail
- **Event sourcing** — audit-friendly, harder read-side queries (accepted)

## Consequences

- Read models may lag writes by seconds
- Cancellation becomes an event, not a DELETE
```

Most decisions need only the opening paragraph. Add optional sections when they add genuine value.

### Optional frontmatter links

| Field | When | Value |
|-------|------|-------|
| `origin` | Decided while resolving a wayfinder ticket | `meta/wayfinding/<effort>/tickets/NNNN-slug.md` |
| `supersedes` | This record overrides an earlier one | `topics/decisions/NNNN-slug.md` |
| `superseded_by` | Set on the older record | `topics/decisions/NNNN-slug.md` |

Statuses: `accepted`, `amended` (part of it overridden; say which part), `superseded` (fully replaced). Paths are relative to the wiki root.

## After writing

1. Add the file path to the owning domain's frontmatter `children`
2. List it in `topics/README.md` with status `filled`
3. Append `meta/CHANGELOG.md`:

```md
### YYYY-MM-DD — Record decision: event-sourced orders
- Added topics/decisions/0001-event-sourced-orders.md
- Domains: ordering
```

## When to offer a decision record

All three must be true:

1. **Hard to reverse** — meaningful cost to change later
2. **Surprising without context** — a future reader will wonder why
3. **Real trade-off** — genuine alternatives existed

Skip easy-to-reverse, obvious, or no-alternative choices.

## What qualifies

- Architectural shape (monorepo, CQRS, service boundaries)
- Integration patterns between domains (events vs sync HTTP)
- Technology lock-in (database, message bus, auth provider)
- Boundary decisions ("Customer owned by ordering; others reference by ID only")
- Deliberate deviations from the obvious path
- Constraints not visible in code (compliance, SLA contracts)
- Rejected alternatives worth remembering

