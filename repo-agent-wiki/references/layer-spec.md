# Layer Specification

## YAML frontmatter (all wiki pages)

```yaml
---
layer: L0 | L1 | L2 | L3 | L4 | meta
domain: api          # L2/L3 only
scope: one-line purpose
tokens: ~N           # estimate for L0-L3
read_when:           # string or list — agent routing keywords
  - keyword1
parent: 01_MAP.md    # navigation up
children:            # navigation down
  - domains/api.md
code_paths:          # L2/L3 — prefer over grep
  - src/api/
status: stub | filled   # L3 during scaffold
migrate_from:        # L3 — legacy doc paths
  - docs/old.md
source: file.py      # L4 — verification source
---
```

## L0 — `00_BOOT.md`

**Always loaded.** Contains only:
- Project name + one-sentence purpose
- Stack (bullets, not essays)
- Top-level components table (services/modules)
- 4 mandatory agent rules (read order, no PROJECT.md if wiki loaded, reference vs topics, protocol link)
- Minimal code tree (3 levels max)
- Status banner (scaffold / fill phase)

**Never:** endpoint lists, schema columns, routing rules, changelog history.

## L1 — `01_MAP.md`

**Loaded for non-trivial tasks.** Contains:
- Architecture diagram (mermaid or ASCII) — one only
- Domain router table: "If task involves X → read Y"
- Cross-cutting reference index
- Layer/code layout table (if different from boot tree)
- "Do NOT load unless" short list

## L2 — `domains/<name>.md`

One **bounded context** per file. Structure:

1. Service/module summary table
2. Responsibilities (checkbox list)
3. Key paths table
4. Pipeline position (if applicable)
5. Links to L3 topics + L4 reference
6. **Do NOT read unless** — negative routing

Keep under ~1500 tokens. Deep content → L3.

## L3 — `topics/<name>.md`

**One concern per file.** Examples across repos:
- `extraction-pipeline`, `auth-levels`, `completion-checker`, `crud-patterns`, `routing-rules`, `queue-contracts`

Structure: overview → flow diagram → tables → code entry points → related links.

## L4 — `reference/*.md`

**Lookup only.** Standard files (include only what applies):

| File | When |
|------|------|
| `file-map.md` | Always |
| `env-vars.md` | Env-based config |
| `api-endpoints.md` | HTTP API |
| `db-schema.md` | Database |
| `queues.md` | Message queues / events |
| `docker-images.md` | Containers |

No paragraphs. Tables + code path for verification.

## meta/

| File | Purpose |
|------|---------|
| `AGENT_PROTOCOL.md` | Navigation order, context budget, decision tree |
| `CHANGELOG.md` | Dated deltas only |
| `DRAFT_CURSOR_RULE.md` | Optional install template — not active rule |
| `INDEX.md` | Hub: links each planning folder's `INDEX.md` (lazy) |
| `wayfinding/<effort>/` | Decision-ticket maps (`/wayfinder-wiki`) |
| `sdlc-artifacts/<effort>/` | Stage artifacts and specs (`/grilling-wiki`, `/to-spec-wiki`) |
| `research/` | Cited research notes (`/research-wiki`) |
| `prototypes/` | Prototype verdicts (`/prototype-wiki`) |

Planning folders hold work in flight and its evidence. They are never the canonical home of a term (L2), trade-off (L3 decisions), or system fact (L4); they link to those.
