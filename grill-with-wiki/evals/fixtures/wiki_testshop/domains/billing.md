---
layer: L2
domain: billing
scope: invoicing after shipment
read_when: [invoice, payment, billing]
code_paths:
  - src/billing/
parent: 01_MAP.md
children: []
---

# Domain: Billing

## Responsibilities

- [x] Generate invoice when fulfillment emits ShipmentDispatched
- [x] Track payment status

## Language

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

## Do NOT read unless

- Order placement or cancellation → ordering domain
