# Agent Journaler — Protocol

Append a **System_Audit_Log** after meaningful work so patterns (latency, guessing, tool friction, scope drift) are visible over time.

## Log location

Resolve in this order:

1. **`PROJECT.md`** — If it defines `agent_journal_path` (file or directory), use it.
   - Directory → append to `<path>/YYYY-MM-DD.md`
   - File → append to that file regardless of date
2. **Default** — `.agent/journal/YYYY-MM-DD.md` at the workspace root
3. **Fallback** — If `.agent/` is not writable, use `docs/agent-journal/YYYY-MM-DD.md` and note the fallback in the entry

Create missing parent directories. One file per calendar day (unless `agent_journal_path` points to a single file). Separate entries with a line containing only `---`.

## System_Audit_Log template

Copy, fill, and append:

```markdown
---
timestamp: 2026-05-22T14:30:00Z
task: <short title>
task_ref: <optional: manifest id, issue #, PR, or user quote>
agents: <optional: blueprint-planner, restricted-coder, … or "single">
---

## System_Audit_Log

### outcome
completed | blocked | failed_review | abandoned

### latency_bottleneck
Where did time go? (user wait, CI, Docker, large index, slow MCP, network)
- step: ...
- cause: ...

### hallucination_check
Decisions **guessed** vs **verified** (PROJECT.md, README, code, docs, user message).
- guessed: ...
- verified: ...

### tool_friction
Hardest tools or capabilities (search, tests, terminal, MCP, browser, permissions).
- friction: ...
- workaround: ...

### scope_drift
Did work exceed the stated task or manifest?
- drift: yes | no
- details: ...

### human_clarifications
Questions asked of the user and whether they were answered (omit section if none).

### lessons
One or two bullets: skill/rule/PROJECT.md improvements for next time.
```

## Field guidance

| Field | Notes |
|-------|--------|
| `outcome` | `failed_review` when adversarial-reviewer returned FAIL; `blocked` when waiting on user or external system |
| `hallucination_check` | Call out APIs, paths, or conventions assumed without reading the repo |
| `scope_drift` | Include drive-by refactors, extra files, or missing manifest steps |
| `agents` | Omit or set `single` when not using the multi-agent pipeline |

## Rules

- Factual tone; no marketing or filler.
- No secrets, tokens, credentials, or PII — redact with `<REDACTED>`.
- Keep each section to a few lines unless the incident was severe.
- Link to artifacts when useful: commit hash, PR URL, reviewer JSON status (not full payloads with sensitive paths).

## Meta improvement

When skimming the last 7 days of journal files:

- If the same `tool_friction` appears **3+ times**, propose a **one-line** addition to the relevant skill, Cursor rule, or `PROJECT.md` section.
- If `guessed` repeatedly names the same gap, propose documenting it in `PROJECT.md` or README.

Present proposals to the user; do not edit playbooks or skills unless asked.

## Example entry

```markdown
---
timestamp: 2026-05-22T16:00:00Z
task: Add adversarial-reviewer skill
task_ref: user request
agents: single
---

## System_Audit_Log

### outcome
completed

### latency_bottleneck
- step: file search
- cause: broken path in SKILL.md required glob to locate reference/

### hallucination_check
- guessed: none
- verified: reference/journaling_protocol.md exists beside SKILL.md

### tool_friction
- friction: none significant
- workaround: n/a

### scope_drift
- drift: no
- details: Updated SKILL.md and reference only

### lessons
- Prefer `reference/` paths relative to skill root, not `skills/meta/...` placeholders.
```
