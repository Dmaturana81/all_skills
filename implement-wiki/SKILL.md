---
name: implement-wiki
description: >-
  Implement a piece of work from a spec or tickets in a wiki_*/ repo, then
  bring the wiki up to date with what changed. Use when the user wants to
  implement a spec or tickets and the project uses a layered agent wiki.
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

## Find the spec

If the user names an effort or a map rather than a file, route through `meta/INDEX.md` → `meta/sdlc-artifacts/INDEX.md` to `meta/sdlc-artifacts/<effort>/spec.md`. Read the decisions and Language it links; don't re-decide them. If the spec came from a wayfinding map, the map's closed tickets hold the detail behind each decision. Zoom into them only when the spec's gist isn't enough.

## Build

Use `/tdd-wiki` where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use `/code-review` to review the work.

## Keep the wiki current

Before committing, update the wiki pages the change made stale. The wiki describes the code as it is now:

- `reference/*.md`: new or changed endpoints, env vars, schema, queues, files (verified from code).
- `domains/<d>.md`: tick off responsibilities that now exist; add `code_paths`.
- `topics/`: patch any deep dive whose behavior changed.
- `meta/sdlc-artifacts/<effort>/`: mark the spec `status: implemented` and update the effort's row in `INDEX.md`.
- `meta/CHANGELOG.md`: one dated entry naming the effort, the domains, and the paths.

Then run `repo-agent-wiki`'s `scripts/validate_wiki.py` on the wiki, and `wayfinder-wiki`'s `scripts/wayfinding.py check` if `meta/wayfinding/` exists.

Commit your work, including the wiki updates, to the current branch.
