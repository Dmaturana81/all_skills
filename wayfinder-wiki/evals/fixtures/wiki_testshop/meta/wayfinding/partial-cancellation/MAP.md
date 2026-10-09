---
layer: meta
kind: wayfinder-map
effort: partial-cancellation
status: active
owner: matu
domains: [ordering, fulfillment]
read_when: [partial cancel, line item, cancellation, allocation]
parent: ../INDEX.md
handoff:
---

# Partial line-item cancellation

## Destination

A spec for letting a Customer cancel one line of an Order before it ships, ready for /to-spec-wiki.

## Notes

- Domains: [ordering](../../../domains/ordering.md), [fulfillment](../../../domains/fulfillment.md)
- Must revisit, not ignore: [Full-order cancellation only](../../../topics/decisions/0001-full-order-cancellation-only.md)
- Grilling tickets: /grilling-wiki ticket mode + /domain-modeling-wiki

## Decisions so far

- [Fulfillment allocation granularity](tickets/0001-fulfillment-allocation-granularity.md): stock is reserved per Order today, not per line

## Not yet specified

- How refunds interact once billing has invoiced part of an Order

## Out of scope

- [Storefront cancel button](tickets/0004-storefront-cancel-button.md): the destination is a backend spec; UI is a later effort
