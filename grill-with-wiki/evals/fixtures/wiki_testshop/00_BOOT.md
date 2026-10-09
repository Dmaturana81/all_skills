---
layer: L0
scope: agent entry point
tokens: ~200
read_when: always
children:
  - 01_MAP.md
  - meta/AGENT_PROTOCOL.md
---

# TestShop — Agent Boot

**Stack:** FastAPI, Postgres, Redis, Celery

## What this system does

E-commerce backend: customers place orders, warehouse fulfills them, billing invoices after shipment.

## Components

| Component | Role |
|-----------|------|
| ordering-api | Order placement and cancellation |
| fulfillment-worker | Pick, pack, ship |
| billing-api | Invoice generation |

## Agent rules (mandatory)

1. Read this file, then `01_MAP.md`, then only relevant domain(s).
2. Max 2 domains per session.
3. Use `reference/` for facts; `topics/` for deep dives.
4. Follow `meta/AGENT_PROTOCOL.md`.

## Code layout

```
src/
├── ordering/
├── fulfillment/
└── billing/
```

## Status

> Fill complete (eval fixture)
