# Wiki Navigation During TDD

Use this when routing a test-first implementation through the wiki knowledge graph.

## Session entry (in order)

1. `wiki_*/00_BOOT.md` — build/test/lint commands, stack, agent rules
2. `wiki_*/01_MAP.md` — domain router: route the change to bounded contexts
3. `wiki_*/meta/AGENT_PROTOCOL.md` — context budget and decision tree
4. **SDLC artifacts** (if present): find the effort in `meta/sdlc-artifacts/INDEX.md` (reached from `meta/INDEX.md`), then read from `meta/sdlc-artifacts/<effort>/` (legacy wikis keep them directly in `meta/sdlc-artifacts/`):
   - `plan.md` — seams, files, order of work, risks
   - `test.md` — proof commands, acceptance criteria
   - `spec.md` — requirements tests must satisfy
5. **At most 2** `domains/*.md` files matched to the change
6. Follow `children` links to L3 decisions and L4 reference as needed

## Routing without reading everything

- Match change keywords against domain `read_when` and the L1 router table
- Use L2 **Do NOT read unless** to avoid wrong bounded contexts
- Use L2 `code_paths` for targeted code reads — not repo-wide grep
- Drop to L4 for facts (endpoints, schema); L3 for behavior deep dives and decisions

## Context budget

| Layer | Budget | TDD session rule |
|-------|--------|----------------|
| L0 + L1 | ~1k tokens combined | Read once at start |
| L2 domains | ~1k each, max 2 | Domains the change touches |
| SDLC artifacts | As needed | `plan.md` + `test.md` before first red test |
| L3 decisions | On demand | When touching an area with recorded trade-offs |
| L4 reference | Lookup only | Verify assumptions against tables |

## Where vocabulary and constraints live

| Scope | Location |
|-------|----------|
| Canonical terms | `domains/<name>.md` → `## Language` |
| Cross-cutting terms | `reference/glossary.md` |
| Hard trade-offs | `topics/decisions/NNNN-slug.md` |
| Seams and proof | `meta/sdlc-artifacts/<effort>/plan.md`, `test.md` |

## After the loop

| What changed | Update |
|--------------|--------|
| New canonical term surfaced by tests | `/domain-modeling-wiki` → L2 or glossary |
| Testing strategy trade-off | `/domain-modeling-wiki` → L3 decision |
| Seams or proof commands changed | Patch `<effort>/plan.md` / `test.md` + `meta/sdlc-artifacts/INDEX.md` |

Never add session prose to L0 or L4 pages.
