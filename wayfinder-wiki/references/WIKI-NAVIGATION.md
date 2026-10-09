# Wiki Navigation During Wayfinding

## Session entry (in order)

1. `wiki_*/00_BOOT.md`: identity, stack, agent rules
2. `wiki_*/01_MAP.md`: domain router, including the planning row to `meta/INDEX.md`
3. `wiki_*/meta/AGENT_PROTOCOL.md`: context budget and decision tree
4. `wiki_*/meta/INDEX.md`, then `meta/wayfinding/INDEX.md`: which maps exist and their state
5. The map: `MAP.md` and the generated `tickets/README.md`
6. The ticket being worked, then only its `domains` (at most 2) and the pages it links

## Context budget

| Layer | Budget | Wayfinding rule |
|---|---|---|
| L0 + L1 | ~1k tokens combined | Read once at start |
| Hub and wayfinding index | Small tables | Read once at start |
| `MAP.md` + `tickets/README.md` | The low-res view | Read once; don't load every ticket body |
| One ticket | ~100K-token session | The only ticket you resolve this session |
| L2 domains | Max 2 | From the ticket's `domains` field |
| Closed tickets, L3 decisions, research, prototypes | On demand | Zoom in only when the ticket depends on them |
| L4 reference | Lookup only | Verify claims; record new facts as table rows |

## Routing without reading everything

- Match the ticket's `read_when` and `domains` against the L1 router and domain `read_when`.
- Use L2 **Do NOT read unless** to avoid loading the wrong bounded context.
- Prefer domain `code_paths` over repo-wide search.
- Prefer the generated `tickets/README.md` over opening ticket files to learn status or blockers.

## After resolving something

| What | Update |
|---|---|
| Ticket answer | Ticket `## Resolution` + one line in map **Decisions so far** |
| Domain term | `domains/<d>.md` `## Language` (via `/domain-modeling-wiki`) |
| Cross-cutting term | `reference/glossary.md` |
| Hard decision | `topics/decisions/`, domain `children`, `topics/README.md` |
| System fact | Matching `reference/*.md` table |
| External fact | `meta/research/<slug>.md` + `meta/research/INDEX.md` |
| Prototype verdict | `meta/prototypes/<slug>.md` + `meta/prototypes/INDEX.md` |
| New bounded context | New L2 domain + router row in `01_MAP.md` |
| Any of the above | One `meta/CHANGELOG.md` entry per session, then `index` and `check` |

Never add session prose to L0 or L4 pages.
