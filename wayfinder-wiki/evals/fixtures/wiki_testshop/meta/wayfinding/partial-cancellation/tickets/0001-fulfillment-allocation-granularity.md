---
layer: meta
kind: wayfinder-ticket
effort: partial-cancellation
id: "0001"
type: research
mode: AFK
status: closed
assignee: matu
blocked_by: []
domains: [fulfillment]
read_when: [allocation, reservation, stock]
parent: ../MAP.md
---

# Fulfillment allocation granularity

## Question

Does fulfillment reserve stock per Order or per line? Decision 0001 deferred partial cancellation because of order-level allocation; is that still true in the code?

## Resolution

Still true: the fulfillment worker reserves stock for the whole Order in one step and releases it only on full cancellation. Releasing a single line would need per-line reservations. This unblocks the decision of what a line cancellation is. Resolved 2026-10-08 by a research subagent.

### Wiki updates

- [Fulfillment allocation](../../../research/fulfillment-allocation.md) (research note)
