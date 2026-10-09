---
layer: L1
scope: system map and domain router
tokens: ~700
read_when: [map, architecture, routing]
parent: 00_BOOT.md
children:
  - domains/ordering.md
  - domains/billing.md
  - domains/fulfillment.md
---

# System Map

## Domain router

| If your task involves… | Read |
|------------------------|------|
| Orders, cancellation, customers | [domains/ordering.md](domains/ordering.md) |
| Invoices, payments | [domains/billing.md](domains/billing.md) |
| Shipping, picking, warehouse | [domains/fulfillment.md](domains/fulfillment.md) |

## Cross-cutting reference

| Need | Read |
|------|------|
| API endpoints | [reference/api-endpoints.md](reference/api-endpoints.md) |
| Glossary index | [reference/glossary.md](reference/glossary.md) |
| Planning in flight, wayfinding, research, prototypes | [meta/INDEX.md](meta/INDEX.md) |

## Do NOT load unless

- Billing questions → don't load fulfillment
- Fulfillment questions → don't load billing unless shipment triggers invoice
