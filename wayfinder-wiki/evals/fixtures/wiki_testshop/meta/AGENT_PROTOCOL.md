# Agent Protocol

## Navigation order

1. `00_BOOT.md`
2. `01_MAP.md`
3. At most 2 `domains/*.md`
4. L3 topics / L4 reference on demand

## Context budget

| Layer | Limit |
|-------|-------|
| L0 + L1 | ~1k tokens combined |
| L2 | Max 2 domains per session |

## Decision tree

- order, cancel, customer → ordering
- invoice, payment → billing
- ship, warehouse → fulfillment

## Code exploration

Prefer domain `code_paths` over repo-wide search.

## Planning in flight

Before planning or building, read `meta/INDEX.md` for active wayfinding maps and research; reuse an effort's slug rather than starting a parallel one.
