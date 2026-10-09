---
layer: L2
domain: ordering
scope: order placement and cancellation
read_when: [order, cancel, customer, placement]
code_paths:
  - src/ordering/
parent: 01_MAP.md
children:
  - reference/api-endpoints.md
  - topics/decisions/0001-full-order-cancellation-only.md
---

# Domain: Ordering

## Service / module

| Property | Value |
|----------|-------|
| Entry | `src/ordering/router.py` |
| Storage | Postgres `orders`, `order_lines` |

## Responsibilities

- [x] Accept new orders from customers
- [x] Cancel entire orders before shipment
- [ ] Partial line-item cancellation (not implemented)

## Key paths

| Area | Path |
|------|------|
| Router | `src/ordering/router.py` |
| Service | `src/ordering/service.py` |

## Language

**Order**:
A customer request to purchase one or more products, tracked from placement through fulfillment.
_Avoid_: Purchase, transaction

**Cancellation**:
Voiding an **entire order** before any line item has shipped.
_Avoid_: Refund, return, partial cancel

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account

## Related

- [reference/api-endpoints.md](../reference/api-endpoints.md)
- [0001-full-order-cancellation-only](../topics/decisions/0001-full-order-cancellation-only.md)

## Do NOT read unless

- Invoice or payment logic → use billing domain
- Warehouse or shipping → use fulfillment domain
