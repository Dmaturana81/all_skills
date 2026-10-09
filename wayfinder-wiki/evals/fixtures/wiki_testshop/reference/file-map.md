---
layer: L4
scope: entry points and key modules
read_when: [files, entry point, where is]
parent: 01_MAP.md
source: src/
---

# File Map

| Path | Domain | Role |
|------|--------|------|
| `src/ordering/router.py` | ordering | HTTP routes for orders |
| `src/fulfillment/` | fulfillment | Pick, pack, ship worker |
| `src/billing/` | billing | Invoice generation |
