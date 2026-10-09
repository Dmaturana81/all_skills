---
layer: L2
domain: fulfillment
scope: warehouse pick pack ship
read_when: [ship, warehouse, fulfillment, picking]
code_paths:
  - src/fulfillment/
parent: 01_MAP.md
children: []
---

# Domain: Fulfillment

## Responsibilities

- [x] Pick and pack order lines
- [x] Emit ShipmentDispatched when shipped

## Do NOT read unless

- Cancellation before ship → ordering domain
