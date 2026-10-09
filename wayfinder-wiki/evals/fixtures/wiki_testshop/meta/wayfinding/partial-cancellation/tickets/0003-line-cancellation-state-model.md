---
layer: meta
kind: wayfinder-ticket
effort: partial-cancellation
id: "0003"
type: prototype
mode: HITL
status: open
assignee:
blocked_by: ["0002"]
domains: [ordering]
read_when: [state machine, order status, line status]
parent: ../MAP.md
---

# Line cancellation state model

## Question

Once a line cancellation is defined, how do Order and line statuses move together? A logic prototype should walk the hard cases: cancel during pick, cancel the last line, cancel after a partial shipment.
