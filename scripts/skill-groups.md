# Skill Groups

Source of truth for **which skills to symlink into a repo**.  
Linker: `scripts/link_skill_group.py` · CLI: `scripts/link-skills`  
Links are created in `./.cursor/skills/` (that folder is gitignored).

A group is a **closed workflow**. If you link the group, every skill that workflow **invokes or requires on disk** is included (or pulled via `needs`).

Do **not** split a pipeline across groups unless the leftover skills are unused.

---

## How to compose a repo

Put atomic group names in `.skill-groups` (often under `.cursor/skills/`). You can also list **individual skill ids** (folder names under `all_skills`):

```
dev-wiki
trello
graphify
```

```bash
link-skills --file .skill-groups --force
link-skills dev-wiki trello --force
link-skills graphify --force
```

`./.cursor/skills/` is created if it does not exist. Pass `--dir` only to link somewhere else.

The linker **auto-includes `needs`**. Example: `science-lit` also links `science-common`.

---

## Two ship pipelines (do not mix casually)

| Pipeline | When | Chain |
|----------|------|--------|
| **Matt flow** | Idea → tickets → TDD in a git repo | `grill-docs` or `grill-wiki` → `spec-ship` (`implement` calls `tdd` + `code-review`) |
| **Manifest flow** | Strict step list, no scope creep | `manifest`: blueprint-planner → restricted-coder → adversarial-reviewer → shepherd-agent → agent-journaler |

`implement` does **not** call restricted-coder. `restricted-coder` does **not** call `/tdd`. Pick one pipeline per repo (or link both if you truly use both).

---

## Needs graph (group → other groups)

| Group | Needs | Why |
|-------|--------|-----|
| `grill-docs` | — | Embeds `grilling` (primitive) |
| `grill-wiki` | — | Embeds `grilling` + `grilling-wiki` + `domain-modeling-wiki`; `repo-agent-wiki` on disk (`grill-with-wiki` **stops** if no `wiki_*/`) |
| `grill-stateless` | — | Embeds `grilling` |
| `spec-ship` | — | `implement` **requires** `tdd` + `code-review` |
| `spec-ship-wiki` | — | Same chain with `tdd-wiki` instead of `tdd` for `wiki_*/` repos |
| `wiki` | — | Every `*-wiki` skill, plus `grilling`, `prototype`, and `code-review`, which those skills read |
| `inbox` | `spec-ship` | `/triage` produces issues for `/implement` |
| `fog` | `spec-ship` | `/wayfinder` hands off to `/to-spec`, not `/implement` |
| `debug` | `design` | Post-mortem may call `/improve-codebase-architecture` |
| `design` | — | `prototype` often paired with `/handoff` (included) |
| `manifest` | — | Full chain including `agent-journaler` |
| `geo` | — | `/geo` orchestrator **delegates** to all `geo-*` children |
| `adk` | — | `/google-agents-cli-workflow` **re-reads** every phase skill |
| `science-lit` | `science-common` | Shared `uv` HTTP package must sit beside science skills |
| `science-seq` | `science-common` | same |
| `science-db` | `science-common` | same |
| `linkedin` | — | Comments skill is local; writer is **missing on disk** (see below) |
| `slides` | `brand` | `theme-factory` is the visual pack pptx often uses |

---

## Skill → skill (inside a group)

### Matt main flow (`ask-matt` map)

```
grill-with-docs  --uses-->  grilling, domain-modeling
grill-with-wiki  --uses-->  grilling-wiki, domain-modeling-wiki
grill-with-wiki  --requires on disk-->  repo-agent-wiki  --uses-->  grilling
grill-me         --uses-->  grilling
implement        --uses-->  tdd, code-review
implement        --wiki-->  tdd-wiki, code-review  (when wiki_*/ exists)
to-tickets       --feeds-->  implement
wayfinder        --feeds-->  to-spec
wayfinder-wiki   --feeds-->  to-spec-wiki
wayfinder-wiki   --uses-->   grilling-wiki, domain-modeling-wiki, research-wiki, prototype-wiki
to-spec-wiki     --feeds-->  implement-wiki
implement-wiki   --uses-->   tdd-wiki, code-review
prototype-wiki   --reads-->  prototype
research-wiki    --reads-->  research (fallback only; the wiki skill is in the group)
triage           --feeds-->  implement
diagnosing-bugs  --may feed-->  improve-codebase-architecture
prototype        --uses-->  handoff (other directory)
wait-what        --uses-->  CONTEXT.md vocabulary (from grill-docs)
```

`setup-matt-pocock-skills` is the documented precondition for tracker/labels. **Not present** in `~/Xcode/all_skills` right now — install from mattpocock/skills if the Matt flow fails on tracker setup.

### Manifest flow

```
blueprint-planner → restricted-coder → adversarial-reviewer → shepherd-agent → (user) → agent-journaler
```

`restricted-coder` FAIL loops back to itself or `blueprint-planner`. Do not link only `restricted-coder`.

### GEO

`geo` is the router (`/geo audit`, `/geo report`, …). Full audit subagents need:

`geo-audit`, `geo-citability`, `geo-crawlers`, `geo-llmstxt`, `geo-brand-mentions`, `geo-platform-optimizer`, `geo-schema`, `geo-technical`, `geo-content`, `geo-report`, `geo-report-pdf`

Link **`geo` (the group)** — not a slice — unless you will never run `/geo audit`.

### ADK

`google-agents-cli-workflow` is the entrypoint. Phases: scaffold → adk-code → eval → deploy → publish → observability. Link **`adk`** as one group.

### Science

`science_skills_common` / `scienceskillscommon` are **not invoked**; other science skills import them via `uv`. They must be linked next to any science pack (`science-common`).

### LinkedIn (this vault)

| Skill | Role | Needs |
|-------|------|--------|
| `linkedin-comment-discuss` | Comments only; wiki `Drafts` + `references/` | `wiki_career/` (not a skill) |
| `linkedin-writer` | Posts + comments, multi-brand | Brand pack files **inside the skill** |

They do **not** call each other. Writer path in catalog (`~/.cursor/skills/linkedin-writer`) is **empty / missing** as of 2026-08-13. Restore the folder or the `linkedin` group will skip it.

---

## Atomic groups

### Alignment

| Group | Definition | Skills |
|-------|------------|--------|
| `grill-docs` | Grill in a git repo; write `CONTEXT.md` + ADRs | `grilling`, `grill-with-docs`, `wait-what`, `domain-modeling` |
| `grill-wiki` | Grill against `wiki_*/` (Daniel default when wiki exists) | `grilling`, `grilling-wiki`, `domain-modeling-wiki`, `repo-agent-wiki`, `grill-with-wiki`, `wait-what` |
| `grill-stateless` | Grill with **no** repo / no wiki | `grilling`, `grill-me` |
| `spec-ship` | Spec → tickets → implement (TDD + review) | `to-spec`, `to-tickets`, `implement`, `tdd`, `code-review` |
| `spec-ship-wiki` | Spec → tickets → implement (TDD-wiki + review) | `to-spec`, `to-tickets`, `implement-wiki`, `tdd-wiki`, `code-review` |
| `wiki` | Every wiki skill, from scaffold through wayfinding to implement | `repo-agent-wiki`, `grilling`, `grilling-wiki`, `domain-modeling-wiki`, `grill-with-wiki`, `wayfinder-wiki`, `research-wiki`, `prototype`, `prototype-wiki`, `to-spec-wiki`, `implement-wiki`, `tdd-wiki`, `code-review` |
| `inbox` | Incoming bugs/requests → agent-ready issues | `triage` |
| `fog` | Multi-session decision map (not a build) | `wayfinder`, `ask-matt` |
| `debug` | Hard-bug loop with a red command first | `diagnosing-bugs` |
| `design` | Architecture survey, deep modules, throwaway prototype | `improve-codebase-architecture`, `codebase-design`, `prototype`, `handoff` |
| `research` | Background primary-source memo into the grill | `research` |
| `ask-others` | Questionnaire for someone else | `to-questionnaire` |
| `productivity` | Daily non-code workflow (add `trello` and/or `to-questionnaire` individually) | `grilling`, `grill-me`, `wait-what`, `handoff` |
| `human-ops` | Only a human can click / provision | `wizard`, `teach` |

### Strict delivery

| Group | Definition | Skills |
|-------|------------|--------|
| `manifest` | Execution Manifest pipeline, no scope creep | `blueprint-planner`, `restricted-coder`, `adversarial-reviewer`, `shepherd-agent`, `agent-journaler` |

### Brand / web / agents

| Group | Definition | Skills |
|-------|------------|--------|
| `linkedin` | AINNOVA/personal LinkedIn comments + posts | `linkedin-comment-discuss`, `linkedin-writer` |
| `govtech` | AINNOVA consulta pública / CPSI pipeline | `ainnova-govtech-cpsi` (vault `.cursor/skills/`) |
| `brand` | Visual theme / Anthropic-style chrome | `brand-guidelines`, `theme-factory` |
| `geo` | Full GEO suite (orchestrator + children) | `geo` + all `geo-*` listed above |
| `adk` | Google ADK lifecycle | all 7 `google-agents-cli-*` |
| `mcp` | Author an MCP server | `mcp-builder` |
| `frontend` | UI, HTML artifacts, Playwright | `frontend-design`, `web-artifacts-builder`, `webapp-testing` |
| `github` | GitHub + issues (Matt tracker option) | `github`, `gh-issues` |
| `graph` | Codebase graph | `graphify` |
| `skills-meta` | Write new skills | `skill-creator` |
| `claude-api` | Anthropic API apps | `claude-api` |
| `image` | Gemini image gen | `nano-banana-pro` |

### Science

| Group | Definition | Skills |
|-------|------------|--------|
| `science-common` | Shared HTTP/`uv` package (not invoked) | `science_skills_common`, `scienceskillscommon`, `uv` |
| `science-lit` | Papers | arXiv, bioRxiv, EuropePMC, OpenAlex, PubMed |
| `science-seq` | Sequence / structure | UniProt, NCBI, PDB, MSA, similarity, Foldseek, PyMOL, AlphaFold, AlphaGenome |
| `science-db` | Chem / clinical / variant / ontology DBs | ChEMBL, trials, ClinVar, OpenFDA, OpenTargets, gnomAD, dbSNP, + Ensembl, ENCODE, OLS, GTEx, HPA, InterPro, JASPAR, PubChem, QuickGO, Reactome, STRING, UCSC, UniBind |

### Artifacts

| Group | Definition | Skills |
|-------|------------|--------|
| `slides` | PPTX | `pptx` |
| `sheets` | XLSX | `xlsx` |
| `docs-write` | Human docs + agent-facing prose | `doc-coauthoring`, `writing-for-agents` |

---

## Aliases (expand to atomic groups)

| Alias | Expands to | Use when |
|-------|------------|----------|
| `engineering` | `grill-docs` + ship pipeline | Same as `dev-docs` — Matt flow, `CONTEXT.md` repos |
| `engineering-docs` / `dev-docs` | `grill-docs` + ship pipeline | All developing using docs (`CONTEXT.md` + ADRs) |
| `engineering-wiki` / `dev-wiki` | `grill-wiki` + `spec-ship-wiki` + ship extras | All developing using `wiki_*/` |
| `engineering-plain` / `dev` | `grill-stateless` + ship pipeline | All developing without wiki and without docs |
| `coding` | `spec-ship` `debug` | Implement-only, plan already exists |
| `manifest-ship` | `manifest` | Strict manifest repos (ADK labs, locked scope) |
| `marketing` | `linkedin` `geo` `brand` | AINNOVA site + LinkedIn |
| `adk` | (atomic, already closed) | 5dgai / agents-cli projects |
| `docs` | `slides` `sheets` `docs-write` `brand` | Decks and docs |
| `science` | `science-common` `science-lit` `science-seq` `science-db` | NanoTemper / wet-lab |

---

## Suggested `.skill-groups` by repo type

| Repo | Groups |
|------|--------|
| **daniel-career** (this vault) | `linkedin` `grill-stateless` `docs-write` `geo` |
| **ainnova** (Wagtail + GEO) | `grill-wiki` `spec-ship` `geo` `docs-write` |
| **kaggle/5dgai** (ADK) | `adk` `manifest` `grill-wiki` |
| **generic product API** | `dev-docs` or `dev-wiki` |
| **wiki-only pack** | `wiki` |
| **productivity vault** | `productivity` + `trello` and/or `to-questionnaire` |
| **NanoTemper / science** | `science` `grill-docs` `docs-write` |

---

## On disk vs catalog (2026-08-13)

| Skill | Status |
|-------|--------|
| `linkedin-writer` | Catalogued; **folder missing** (`~/.cursor/skills` empty) |
| `setup-matt-pocock-skills` | Documented by `ask-matt`; **not in all_skills** |
| `linkedin-comment-discuss` | Present: `daniel-career/.cursor/skills/` |

---

## Left ungrouped (on purpose)

Integrations you rarely need as a pack: `apple-notes`, `apple-reminders`, `bluebubbles`, `discord`, `slack`, `slack-gif-creator`, `gog`, `goplaces`, `gifgrep`, `video-frames`, `wacli`. Link individually: `link-skills trello` or `link-skills graphify`.

Duplicate: `web-artifacts-builder` exists at `all_skills/` root and `all_skills/web/`. Linker prefers `web/` when `geo` or `frontend` is selected.

---

## Related

- [[Skills Index]]
- [[Skills - Career LinkedIn Index]]
- [[Consulting]]
