---
layer: L3
domain: ordering
scope: full-order cancellation only
read_when: [cancellation, cancel, partial]
parent: domains/ordering.md
status: accepted
---

# Full-order cancellation only

We cancel entire orders via DELETE /orders/:id. Partial line-item cancellation was deferred because fulfillment allocates inventory at order level, not line level. Revisit if warehouse moves to line-level allocation.
