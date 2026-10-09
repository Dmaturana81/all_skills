---
name: tdd-wiki
description: >-
  Test-driven development for wiki-backed repos. Use when the user wants red-green-refactor,
  test-first features or bug fixes, and the project has (or should have) a wiki_*/ agent wiki —
  even if they only say "TDD" or "write the test first". Prefer this over /tdd when wiki_*/
  exists. Reads seams and proof from wiki SDLC artifacts and domain language from L2/L3.
---

# Test-Driven Development (Wiki)

TDD is the red → green loop. This skill is the wiki-backed reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle — consult them before and during the loop, not after.

The core loop is identical to `/tdd`. What changes is **where vocabulary and constraints come from**: the layered agent wiki instead of `CONTEXT.md` and `docs/adr/`.

## Before the first test

1. **Find the wiki** — glob `wiki_*/` at the repo root. If several exist, ask which one. If none exist, stop and tell the user to run **repo-agent-wiki** first (scaffold is enough), or fall back to `/tdd` if they insist on proceeding without a wiki.
2. **Bootstrap routing** — read `00_BOOT.md`, `01_MAP.md`, and `meta/AGENT_PROTOCOL.md`. Route the change through the domain router; load at most **2** relevant `domains/*.md` files.
3. **Load the build context**: find the effort in `meta/sdlc-artifacts/INDEX.md` (ask which one if several are active), then read from `meta/sdlc-artifacts/<effort>/`, or directly from `meta/sdlc-artifacts/` in legacy wikis. If they exist:
   - `plan.md` — files that change, order of work, risks
   - `test.md` — what "green" means, commands, acceptance criteria
   - `spec.md` — requirements the tests must satisfy
4. **Navigation detail** — see [references/WIKI-NAVIGATION.md](./references/WIKI-NAVIGATION.md).

Prefer domain `code_paths` over repo-wide search. Do not load monolithic `PROJECT.md` if the wiki suffices.

## Vocabulary and constraints

When naming tests, describing behavior, or choosing seams:

- Use **`## Language`** in loaded L2 domains and `reference/glossary.md` (if present) for canonical terms.
- Respect **`topics/decisions/NNNN-slug.md`** in the area you are touching — tests must not contradict accepted trade-offs.
- When a term is ambiguous, apply `/domain-modeling-wiki` to resolve it before locking test names.

Test names should read like specifications in the project's ubiquitous language — not generic programmer jargon.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "customer can see claim status in portal" tells you exactly what capability exists — and survives refactors because it doesn't care about internal structure.

See [tests.md](./tests.md) for examples and [mocking.md](./mocking.md) for mocking guidelines.

## Seams — where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything — agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?"

Prefer seams already named in `plan.md`. If the shape of the interface is itself in question — how deep the module is, where the seam belongs — use `/codebase-design` for module, interface, depth, seam, adapter, leverage and locality vocabulary.

## Anti-patterns

- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does, so it passes by construction. Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec, or `test.md` acceptance criteria.
- **Horizontal slicing** — writing all tests first, then all implementation. Work in **vertical slices** instead — one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage (`/code-review`), not the red → green implementation cycle.
- **Proof before done.** Run the verification commands from `test.md` (or `00_BOOT.md` build/test commands if `test.md` is missing). Paste output when reporting a slice complete.

## After the session

If the loop surfaced a term worth canonizing or a hard trade-off about testing strategy, apply `/domain-modeling-wiki` — don't leave it only in chat or test comments.

If the effort's `test.md` or `plan.md` is now stale (new seams, new proof commands, changed risks), patch the artifact and update `meta/sdlc-artifacts/INDEX.md`.
