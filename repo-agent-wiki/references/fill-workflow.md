# Fill Workflow

## Order (do not skip)

### 1. L4 reference — facts from code

| File | Primary sources |
|------|-----------------|
| `env-vars.md` | `.env.example`, compose, `settings.*`, configmaps |
| `api-endpoints.md` | routers, OpenAPI, route decorators |
| `db-schema.md` | migrations, `CREATE TABLE`, ORM models |
| `queues.md` | queue client, message publish/consume sites |
| `docker-images.md` | compose image tags, Dockerfiles |
| `file-map.md` | entry points, workers, key modules |

Rules:
- Mark unverified cells as `TODO`
- Add `source:` in frontmatter
- No narrative paragraphs

### 2. L3 topics — migrate depth

Pick highest-value topics first (orchestration, data layer, main algorithm).

For each topic:
1. Read legacy doc + implementation
2. Write English concise prose + diagrams
3. Set `status: filled` in frontmatter
4. Link from parent domain `topics:` list
5. Update `topics/README.md`

### 3. L2 domains — orient without duplicating

- Check off responsibilities that exist in code
- Fill service table (versions from compose)
- Point to L3/L4 — do not paste endpoint tables

### 4. CHANGELOG

Pull from:
- `PROJECT.md` "Recent changes"
- Last 10–20 meaningful git commits
- Conversation-known deltas

### 5. L0/L1 touch-up

- Update domain router if domains renamed
- Update status banner only on L0

## Quality bar

| Good | Bad |
|------|-----|
| `completo` requires 4 pipelines CONCLUIDO | Copying entire PROJECT.md into domain |
| Link to `reference/queues.md` | Duplicating queue table in 3 files |
| `read_when: ["CompletionChecker"]` | 300-line domain file |
| Cite `code_paths` | Guessing env var names |

## Optional topics (add when needed)

- `auth-levels`, `eval-*`, `*-pipeline`, `completion-checker`, `crud-patterns`
- List uncreated topics under `topics/README.md` → Planned
