---
layer: meta
kind: research-note
scope: does fulfillment reserve stock per order or per line
read_when: [allocation, reservation, stock, fulfillment]
parent: INDEX.md
effort: partial-cancellation
ticket: meta/wayfinding/partial-cancellation/tickets/0001-fulfillment-allocation-granularity.md
sources_checked: 2026-10-08
---

# Fulfillment allocation

## Answer

Stock is reserved for the whole Order in one step and released only on full cancellation. Per-line release is not possible without per-line reservations.

## Findings

- Reservation happens once per Order when fulfillment accepts it ([fulfillment domain](../../domains/fulfillment.md))
- Decision 0001 names order-level allocation as the reason partial cancellation was deferred ([decision](../../topics/decisions/0001-full-order-cancellation-only.md))

## Open questions

- Whether the warehouse system supports per-line reservations at all
