# Adversarial Reviewer — Checklist

Critique the change set against security, performance, correctness, and technical debt. Produce a structured report; do not silently fix code.

## 1. Security (highest priority)

### Universal

- [ ] **Injection** — SQL, shell, LDAP, XPath, template, and command injection: user or external input must not be concatenated into queries or commands; use parameters, prepared statements, or safe APIs
- [ ] **Secrets** — No API keys, tokens, passwords, private keys, or connection strings in source, configs committed to git, logs, or client bundles
- [ ] **AuthZ / AuthN** — New endpoints, handlers, or UI routes enforce authentication and authorization consistent with the project; no IDOR (accessing others’ resources by ID tampering)
- [ ] **Input validation** — Untrusted input validated at trust boundaries; file uploads restricted by type/size; path traversal blocked
- [ ] **Output encoding** — User-controlled data escaped in HTML, SQL, shell, and logs; avoid dangerous “safe”/raw rendering without justification
- [ ] **Crypto** — No custom crypto; use vetted libraries; no weak algorithms (MD5/SHA1 for passwords, ECB, static IVs) for security-sensitive data
- [ ] **Dependencies** — New deps justified; no known-critical CVEs ignored without documented exception
- [ ] **Sensitive data** — PII/financial/health data not logged, cached, or returned beyond need; errors do not leak stack traces or internals to clients in production paths

### Stack addenda (apply when repo uses the stack)

| Stack | Also check |
|-------|------------|
| **Web / API** | CSRF for state-changing browser forms; CORS not `*` with credentials; security headers where applicable; SSRF on URL fetchers |
| **Django / Flask / Rails** | Framework auth decorators/middleware on new views; ORM/raw SQL parameterization; `mark_safe` / `\|safe` justified |
| **Node / Express** | `eval`, `child_process` with user input; prototype pollution in `merge`/`extend` |
| **Frontend** | XSS via `dangerouslySetInnerHTML`, `v-html`, `{@html}`; secrets in env exposed via `NEXT_PUBLIC_*` / Vite `VITE_*` |
| **Scrapers / jobs** | Credentials not logged; rate limits and robots/terms respected per project policy |

## 2. Performance

- [ ] **N+1 / chatty I/O** — ORM loops, repeated fetches in hot paths; batch or prefetch where the pattern exists in the codebase
- [ ] **Unbounded work** — Lists, exports, and queries have pagination or limits; no unbounded memory growth on user input size
- [ ] **Algorithmic cost** — Avoid O(n²)+ on large collections in request/job paths without justification
- [ ] **Caching** — Expensive reads not duplicated when the project already caches; cache invalidation considered for writes
- [ ] **Resources** — Connections, files, and handles closed; no obvious leaks in new long-lived processes

## 3. Correctness and reliability

- [ ] **Error handling** — Failures handled explicitly; no swallowed exceptions that hide data loss or security failures
- [ ] **Concurrency** — Races, double-submit, non-atomic read-modify-write where state matters
- [ ] **Edge cases** — Empty, null, boundary values, timezone/date handling if dates appear in the diff
- [ ] **Breaking changes** — Public API or schema changes documented or versioned per project norms
- [ ] **Tests** — Non-trivial logic has tests or a stated reason in the handoff; critical paths not left untested

## 4. Technical debt and maintainability

- [ ] **Scope** — Changes match the stated task/manifest; no unrelated drive-by refactors
- [ ] **Duplication** — New logic does not duplicate utilities already in the repo
- [ ] **Configuration** — Magic numbers and environment-specific values externalized when the project does so elsewhere
- [ ] **TODO / FIXME** — Tracked with ticket or manifest reference; not silent landmines
- [ ] **Docs** — Public behavior or ops changes reflected in README/PROJECT.md when the project keeps them current

## Output format (required)

Return a single JSON object in a fenced `json` block:

**Pass:**

```json
{
  "status": "PASS",
  "issues": [],
  "summary": "One-line verdict",
  "reviewed_paths": ["path/to/file"]
}
```

**Fail:**

```json
{
  "status": "FAIL",
  "issues": [
    {
      "severity": "High",
      "category": "security",
      "file": "relative/path",
      "line": 42,
      "description": "What is wrong",
      "suggestion": "Concrete fix or verification step"
    }
  ],
  "summary": "One-line verdict",
  "reviewed_paths": ["path/to/file"]
}
```

**Fields**

| Field | Values |
|-------|--------|
| `severity` | `Low` \| `Med` \| `High` |
| `category` | `security` \| `performance` \| `correctness` \| `tech-debt` |
| `status` | `PASS` only if zero `High` and zero `Med` with `category: security` |

Optional: `blocked_by` (string) for the single most important fix when status is `FAIL`.

## Handoff

- **PASS** → **shepherd-agent** with diff summary and this JSON (if in pipeline)
- **FAIL** → implementer (**restricted-coder** or author) with full `issues` array; do not merge, commit, or approve release
