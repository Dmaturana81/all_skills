# Wiki Navigation During a Grill Session

Use this when routing the user's plan through the wiki knowledge graph.

## Session entry (in order)

1. `wiki_*/00_BOOT.md` — identity, stack, component table, agent rules
2. `wiki_*/01_MAP.md` — domain router: "If task involves X → read Y"
3. `wiki_*/meta/AGENT_PROTOCOL.md` — context budget and decision tree
4. `wiki_*/meta/INDEX.md` (if present): planning in flight, meaning wayfinding maps, SDLC artifacts per effort, research, prototypes
5. **At most 2** `domains/*.md` files matched to the plan (in ticket mode, the ticket's `domains`)
6. Follow `children` / inline links to L3 topics and L4 reference as needed

## Routing without reading everything

- Match plan keywords against domain `read_when` in frontmatter and the L1 router table
- Use L2 **Do NOT read unless** to avoid loading wrong bounded contexts
- Drop to L4 (`reference/`) for facts; L3 (`topics/`) for behaviour deep dives
- Use L2 `code_paths` for targeted code reads — not repo-wide grep

## Context budget

| Layer | Budget | Grill session rule |
|-------|--------|-------------------|
| L0 + L1 | ~1k tokens combined | Read once at start; don't re-read |
| L2 domains | ~1k each, max 2 | Pick domains the plan touches |
| L3 topics | On demand | Load when plan hits a specific concern |
| L4 reference | Lookup only | Verify claims against tables |

## Where terminology lives

| Scope | Location |
|-------|----------|
| Single bounded context | `domains/<name>.md` → `## Language` |
| Cross-cutting / index | `reference/glossary.md` → links to owning domain |
| Recorded trade-offs | `topics/decisions/NNNN-slug.md` |
| Decisions still being made | `meta/wayfinding/<effort>/` tickets, via `meta/INDEX.md` |

## After resolving something

| What | Update |
|------|--------|
| Domain term | `domains/<name>.md` → `## Language` |
| Cross-cutting term | `reference/glossary.md` |
| Hard decision | `topics/decisions/`, domain `children`, `topics/README.md`, `meta/CHANGELOG.md` |
| New bounded context | New L2 domain + router row in `01_MAP.md` + `CHANGELOG.md` |
| Stage artifact | `meta/sdlc-artifacts/<effort>/*.md` + `meta/sdlc-artifacts/INDEX.md` |
| Ticket-mode answer | Hand back to `/wayfinder-wiki`, which writes the ticket's `## Resolution` |

Never add session prose to L0 or L4 pages.

