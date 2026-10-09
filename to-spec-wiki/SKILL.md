---
name: to-spec-wiki
description: >-
  Turn a cleared wayfinder-wiki map, or the current conversation, into a spec
  stored in the repo's layered agent wiki (wiki_*/meta/sdlc-artifacts/<effort>/spec.md),
  indexed and linked to every decision it rests on. No interview, just
  synthesis. Use when a wayfinding map is cleared, or when /to-spec is needed
  and the project has a wiki_*/.
disable-model-invocation: true
---

# To Spec (Wiki)

Synthesize what is already decided into a spec. Do NOT interview the user; if something essential is undecided, it belongs back on the map as a ticket, not in this session.

## Sources

**From a map** (the usual case): the user names a map whose `status` is `cleared`. If it is still `active`, stop and say which tickets are open; run `wayfinding.py frontier` to list them.

1. Read `MAP.md` and `tickets/README.md`.
2. Read every closed ticket's `## Resolution`, and follow its `Wiki updates` links to the decisions, Language entries, L4 rows, research notes, and prototype records.
3. Read the domains the map's Notes name (at most 2 at a time).

**From the conversation**: when there is no map, use what was discussed, exactly as `/to-spec` does.

## Writing the spec

1. Explore the code the spec touches via domain `code_paths`. Use the wiki's `## Language` terms throughout, and respect every `topics/decisions/` record in the area.
2. Sketch the test seams. Prefer existing seams and the highest seam possible; ideally one. **Check them with the user**: this is the only question you ask.
3. Write `wiki_<name>/meta/sdlc-artifacts/<effort>/spec.md` using the `/to-spec` template (problem, solution, user stories, implementation decisions, testing decisions, out of scope, further notes), with frontmatter:

```yaml
---
layer: meta
kind: sdlc-spec
effort: <effort slug>
status: ready-for-agent
read_when: [<keywords>]
parent: ../INDEX.md
source_map: ../../wayfinding/<effort>/MAP.md
---
```

4. Add two sections at the end:
   - `## Related wiki decisions`: links to each `topics/decisions/` record the spec relies on.
   - `## Canonical terminology`: links to the owning `domains/<d>.md` sections.

   Implementation Decisions gist each decision and link the ticket or decision record that holds it; don't copy their detail. The map's **Out of scope** becomes the spec's Out of scope.

## Closing the loop

1. Add or update the effort's entry in `meta/sdlc-artifacts/INDEX.md` (create lazily; link from `meta/INDEX.md`).
2. On the map: set `status: handed-off` and `handoff: ../../sdlc-artifacts/<effort>/spec.md`.
3. Run `wayfinding.py index` and `wayfinding.py check`, then `validate_wiki.py`.
4. Append `meta/CHANGELOG.md`.
5. Tell the user the next step: `/implement-wiki` on the spec.

If the team also tracks work in an issue tracker, offer to publish the spec there with the `ready-for-agent` label, linking back to the wiki file. The wiki copy stays canonical.
