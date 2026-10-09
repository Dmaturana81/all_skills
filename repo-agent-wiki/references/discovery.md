# Repository Discovery Checklist

Run before scaffolding. Record findings in scratch notes, then compress into L0/L1.

## 1. Documentation scan

- [ ] `PROJECT.md`, `README.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `AGENT.md`
- [ ] `docs/` and `**/docs/` under modules
- [ ] `DEPLOYMENT.md`, `ARCHITECTURE.md`
- [ ] OpenAPI / Swagger specs
- [ ] ADRs or `CHANGELOG.md`

## 2. Structure scan

```bash
# Adjust depth; skip node_modules, .venv, vendor
find . -maxdepth 4 -type d \( -name node_modules -o -name .git -o -name .venv \) -prune -o -type d -print
```

Identify:
- Monorepo packages vs single app
- `src/`, `app/`, `cmd/`, `services/`
- Workers vs API vs frontend
- Shared `lib/`, `common/`, `internal/`

## 3. Runtime scan

- [ ] `docker-compose*.yml`, `Dockerfile*`, `kubernetes/`, `.github/workflows/`
- [ ] `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`
- [ ] `.env.example`, configmaps, `settings.py` / `config/`

Extract for L4:
- Service names and image tags
- Env var names (not secret values)
- Ports and health endpoints

## 4. Data & integration scan

- [ ] Migration folders, `schema.sql`, ORM models
- [ ] Queue client code, event bus, webhooks
- [ ] External API clients

## 5. Domain proposal

Draft 5–8 domain slugs (lowercase, hyphenated filenames):

```
api | frontend | database | infra | <business-1> | <business-2> | ...
```

For each domain record:
- Primary code paths (3–8)
- Legacy doc paths to migrate
- 1–3 likely L3 topics

## 6. Topic candidates

Prioritize cross-cutting concerns agents struggle with:
- Orchestration / completion gates
- CRUD or data-access patterns
- Auth
- Message contracts
- Main algorithm pipeline

Mark others as "planned" in `topics/README.md` only.
